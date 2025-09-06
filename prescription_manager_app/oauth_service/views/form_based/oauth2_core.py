from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlencode
from django.shortcuts import render, redirect
from django.urls import reverse
import secrets
import time

from oauth_service.auth.session_helpers import get_logged_in_mongo_user
from oauth_service.forms import AuthoriseForm, RevokeTokenForm, AccessGrantForm
from oauth_service.models import OAuthToken, OAuthCode, OAuthClient


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


def create_tokens(user_id, client_id, scope):
    """
    Generate access and refresh tokens and save them in the DB using the OAuthToken model.
    Returns a dictionary containing token info.
    """
    # Use the model to generate and persist the tokens
    token = OAuthToken.create(
        user_id=user_id,
        client_id=client_id,
        scope=scope
    )

    # Return token data in the same format as before
    return {
        "access_token": token.access_token,
        "refresh_token": token.refresh_token,
        "expires_at": token.expires_at,
        "scope": token.scope,
        "user_id": token.user_id,
    }


def validate_client(
    client_id,
    client_secret=None,
    redirect_uri=None,
    response_type=None,
    scope=None,
    require_secret=False,
    require_redirect=False,
    require_response_type=False,
    require_scope=False,
):
    """
    Validate OAuth client for various endpoints.

    Parameters:
    - client_id: str (required)
    - client_secret: str (optional)
    - redirect_uri: str (optional)
    - response_type: str (optional)
    - scope: str (optional, space-separated)
    - require_secret: bool, if True, client_secret must match
    - require_redirect: bool, if True, redirect_uri must be valid
    - require_response_type: bool, if True, response_type must be valid
    - require_scope: bool, if True, scope must be valid

    Returns:
    - client object if valid
    - JsonResponse with error if invalid
    """

    client = OAuthClient.get_by_client_id(client_id)

    if not client:
        return None, JsonResponse({"error": "Invalid client_id"}, status=400)

    if require_secret and (not client_secret or client.client_secret != client_secret):
        return None, JsonResponse({"error": "Invalid client_secret"}, status=400)

    if require_redirect and redirect_uri not in client.redirect_uris:
        return None, JsonResponse({"error": "Invalid redirect_uri"}, status=400)

    if require_response_type and response_type not in client.response_types:
        return None, JsonResponse({"error": "Unsupported response_type"}, status=400)

    client_scopes = client.scopes or []
    if require_scope:
        if not client_scopes:
            return None, JsonResponse({"error": "Client scopes must be a non-empty array"}, status=400)
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

    client, error = validate_client(
        client_id,
        redirect_uri=redirect_uri,
        response_type=response_type,
        scope=scope,
        require_redirect=True,
        require_response_type=True,
        require_scope=True
    )
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
    oauth_code = OAuthCode.create(
        code=code,
        client_id=client_id,
        user_id=str(mongo_user.id),
        redirect_uri=redirect_uri,
        scope=scope
    )

    url = build_manage_apps_redirect(
        redirect_uri,
        state,
        oauth_code.code
    )
    return redirect(url)


@csrf_exempt
@require_http_methods(["POST"])
def token(request):
    form = AccessGrantForm(request.POST)
    if not form.is_valid():
        request.session["messages"] = [{"errors": form.errors}]
        return redirect("oauth_service:manage-apps")

    data = form.cleaned_data
    client_id = data["client_id"]
    grant_type = data["grant_type"]
    client_secret = data.get("client_secret")

    client, error = validate_client(
        client_id,
        client_secret=client_secret,
        require_secret=True
    )
    if error:
        form.add_error("client_id", error)
        request.session["messages"] = [{"errors": form.errors}]
        return redirect("oauth_service:manage-apps")

    if grant_type not in client.grant_types:
        form.add_error("grant_type", "Unsupported grant type")
        request.session["messages"] = [{"errors": form.errors}]
        return redirect("oauth_service:manage-apps")

    now = int(time.time())
    user_id, scope = None, None

    if grant_type == "authorization_code":
        code = data["code"]
        redirect_uri = data["redirect_uri"]
        auth_code = OAuthCode.get_by_code(code)
        print(auth_code.code, auth_code.redirect_uri !=
              redirect_uri, auth_code.expires_at < now, auth_code.expires_at, now)

        if not auth_code or auth_code.redirect_uri != redirect_uri or auth_code.expires_at < now:
            form.add_error("code", "Invalid or expired code")
        else:
            OAuthCode.delete(code)
            user_id, scope = auth_code.user_id, auth_code.scope

    elif grant_type == "refresh_token":
        token = OAuthToken.get_by_refresh_token(data["refresh_token"])
        if not token or token.client_id != client_id:
            form.add_error("refresh_token", "Invalid or revoked refresh token")
        else:
            OAuthToken.delete(token.refresh_token)
            user_id, scope = token.user_id, token.scope

    if form.errors:
        print(form.errors)
        request.session["messages"] = [{"errors": form.errors}]
        return redirect("oauth_service:manage-apps")

    token_data = create_tokens(user_id, client_id, scope)
    request.session["messages"] = [{"success": "Access token granted"}]
    request.session["token_data"] = token_data

    return redirect("oauth_service:manage-apps")


@csrf_exempt
@require_http_methods(["POST"])
def revoke_token(request):
    form = RevokeTokenForm(request.POST)
    if not form.is_valid():
        request.session["messages"] = [{"errors": form.errors}]
        return redirect("oauth_service:manage-apps")

    client_id = form.cleaned_data["client_id"]
    client_secret = form.cleaned_data["client_secret"]
    token_to_revoke = form.cleaned_data["token"]

    client, error = validate_client(
        client_id,
        client_secret=client_secret,
        require_secret=True
    )
    if error:
        request.session["messages"] = [{"errors": {"client_id": [error]}}]
        return redirect("oauth_service:manage-apps")

    OAuthToken.delete(token_to_revoke)

    request.session["messages"] = [{"success": "Token revoked"}]
    request.session.pop("token_data", None)
    return redirect("oauth_service:manage-apps")
