from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlencode
from django.shortcuts import render, redirect
from django.urls import reverse
import secrets
import time

from oauth_service.auth.session_helpers import get_logged_in_mongo_user
from oauth_service.db.connection import oauth_client_col, oauth_code_col, oauth_token_col
from oauth_service.forms import AuthoriseForm, TokenForm, RevokeForm

# --- Constants ---
ACCESS_TOKEN_LIFETIME = 3600  # seconds
AUTH_CODE_LIFETIME = 600  # seconds


def build_manage_apps_redirect(
        redirect_uri: str,
        state: str,
        code: str = None
):
    params = {}
    if code:
        params['code'] = code
        if state:
            params['state'] = state
    else:
        params['error'] = 'access_denied'
    url = f"{redirect_uri}?{urlencode(params)}"
    return url


def parse_client_scope(scope_value):
    if not scope_value:
        raise ValueError("Client scope must not be empty or None")
    return set(s.strip() for s in scope_value.split(',') if s.strip())


def _validate_client(client_id, redirect_uri, response_type, scope):
    client = oauth_client_col.find_one({"client_id": client_id})
    if not client:
        return None, JsonResponse({"error": "Invalid client_id"}, status=400)
    if redirect_uri not in client.get("redirect_uris", []):
        return None, JsonResponse({"error": "Invalid redirect_uri"}, status=400)
    if response_type not in client.get("response_types", []):
        return None, JsonResponse({"error": "Unsupported response_type"}, status=400)

    client_scopes = set(client.get("scopes") or [])
    if not client_scopes:
        raise ValueError("Client scopes must be a non-empty array")

    requested_scopes = set((scope or "").split())
    if not requested_scopes.issubset(client_scopes):
        return None, JsonResponse({"error": "Invalid scope"}, status=400)

    return client, None


@csrf_exempt
@require_http_methods(["GET", "POST"])
def authorise(request):
    mongo_user = get_logged_in_mongo_user(request)
    if not mongo_user:
        next_url = request.get_full_path()
        return redirect(f"{reverse('oauth_service:login-user')}?next={next_url}")

    form = AuthoriseForm(request.GET if request.method ==
                         "GET" else request.POST)
    if not form.is_valid():
        return JsonResponse({"error": form.errors}, status=400)

    client_id = form.cleaned_data["client_id"]
    redirect_uri = form.cleaned_data["redirect_uri"]
    response_type = form.cleaned_data["response_type"]
    scope = form.cleaned_data["scope"]
    state = form.cleaned_data.get("state", "")

    client, error = _validate_client(
        client_id, redirect_uri, response_type, scope)
    if error:
        return error

    if request.method == "GET":
        return render(request, "oauth_service/authorise.html", {
            "client": client,
            "state": state,
            "scope": scope,
            "redirect_uri": redirect_uri,
            "form": form,
        })

    if "allow" not in request.POST:
        url = build_manage_apps_redirect(
            redirect_uri,
            state,
        )
        return redirect(url)

    code = secrets.token_urlsafe(24)
    now = int(time.time())
    oauth_code_col.insert_one({
        "code": code,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "user_id": str(mongo_user.id),
        "scope": scope,
        "created_at": now,
        "expires_at": now + AUTH_CODE_LIFETIME,
    })

    url = build_manage_apps_redirect(
        redirect_uri,
        state,
        code
    )
    return redirect(url)


@csrf_exempt
def token(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    form = TokenForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"error": form.errors}, status=400)

    data = form.cleaned_data
    grant_type = data["grant_type"]

    client_id = data.get("client_id") or request.POST.get("client_id")
    client_secret = data.get(
        "client_secret") or request.POST.get("client_secret")
    client = oauth_client_col.find_one({"client_id": client_id})
    if not client or client.get("client_secret") != client_secret:
        return JsonResponse({"error": "Invalid client credentials"}, status=401)
    if grant_type not in client.get("grant_types", []):
        return JsonResponse({"error": "Unsupported grant type"}, status=400)

    user_id, scope = None, None
    now = int(time.time())

    if grant_type == "authorization_code":
        code = data["code"]
        redirect_uri = data["redirect_uri"]
        auth_code = oauth_code_col.find_one_and_delete(
            {"code": code, "client_id": client_id}
        )
        if not auth_code or auth_code.get("redirect_uri") != redirect_uri or auth_code.get("expires_at", 0) < now:
            return JsonResponse({"error": "Invalid or expired code"}, status=400)
        user_id, scope = auth_code["user_id"], auth_code.get("scope")

    elif grant_type == "refresh_token":
        token_data = oauth_token_col.find_one_and_delete(
            {"refresh_token": data["refresh_token"], "client_id": client_id}
        )
        if not token_data:
            return JsonResponse({"error": "Invalid or revoked refresh token"}, status=400)
        user_id, scope = token_data["user_id"], token_data.get("scope")

    access_token = secrets.token_urlsafe(32)
    refresh_token = secrets.token_urlsafe(32)
    expires_at = now + ACCESS_TOKEN_LIFETIME

    oauth_token_col.insert_one({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": expires_at,
        "client_id": client_id,
        "user_id": user_id,
        "scope": scope,
        "created_at": now,
    })

    return JsonResponse({
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": ACCESS_TOKEN_LIFETIME,
        "refresh_token": refresh_token,
        "scope": scope,
    })


@csrf_exempt
@require_http_methods(["POST"])
def revoke_token(request):
    form = RevokeForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"error": form.errors}, status=400)

    client_id = form.cleaned_data["client_id"]
    client_secret = form.cleaned_data["client_secret"]
    client = oauth_client_col.find_one({"client_id": client_id})
    if not client or client.get("client_secret") != client_secret:
        return JsonResponse({"error": "Invalid client credentials"}, status=401)

    token_to_revoke = form.cleaned_data["token"]
    oauth_token_col.delete_many({
        "$or": [{"access_token": token_to_revoke}, {"refresh_token": token_to_revoke}],
        "client_id": client_id,
    })

    return JsonResponse({}, status=200)
