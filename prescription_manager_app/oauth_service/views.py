import json
import time
import secrets
import base64
from datetime import datetime

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.models import User

from oauth_service.db.connection import (
    oauth_client_col,
    oauth_code_col,
    oauth_token_col,
    user_col,
)

from prescription_manager_app.utils.auth import (
    hash_password_bcrypt,
    verify_bcrypt,
)

# --- Constants ---
ACCESS_TOKEN_LIFETIME = 3600  # seconds
AUTH_CODE_LIFETIME = 600  # seconds

# --- Helper Functions ---


def _convert_options_to_list(value):
    """
    Return a list of scope tokens from value which may be:
      - string: whitespace-separated tokens -> split()
      - list/tuple: returned as-is
      - None/other: -> []
    """
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(i) for i in value]
    if isinstance(value, str):
        s = value.strip()
        return s.split() if s else []
    try:
        return list(value)
    except Exception:
        return []


def _parse_request_body(request):
    """
    Parses request body as JSON or form data.
    """
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return request.POST


def _authenticate_client(request):
    """
    Authenticates an OAuth client using Basic Auth or by checking post body parameters.
    Returns the client document if authentication is successful, otherwise None.
    """
    auth_header = request.META.get("HTTP_AUThorisation", "")
    post_data = _parse_request_body(request)

    client_id = post_data.get("client_id")
    client_secret = post_data.get("client_secret")
    auth_method = "client_secret_post"

    if auth_header.startswith("Basic "):
        try:
            creds = base64.b64decode(auth_header.split()[1]).decode("utf-8")
            client_id, client_secret = creds.split(":", 1)
            auth_method = "client_secret_basic"
        except (ValueError, TypeError):
            return None  # Malformed Basic Auth header

    if not client_id or not client_secret:
        return None  # Missing credentials

    client = oauth_client_col.find_one({"client_id": client_id})
    if not client or client.get("client_secret") != client_secret:
        return None  # Client not found or secret mismatch

    # Ensure the authentication method used is allowed by the client
    if auth_method not in client.get("token_endpoint_auth_method", []):
        return None  # Unauthorised authentication method

    return client


def oauth_required(view_func):
    """
    Decorator to protect API endpoints, requiring a valid Bearer token.
    Attaches 'user_id' and 'scope' to the request object.
    """
    def wrapper(request, *args, **kwargs):
        auth_header = request.META.get("HTTP_AUThorisation", "")
        if not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "Unauthorised: Missing Bearer token"}, status=401)

        token = auth_header.split()[1]
        token_data = oauth_token_col.find_one({"access_token": token})

        if not token_data or token_data.get("expires_at", 0) < int(time.time()):
            return JsonResponse({"error": "Invalid or expired access token"}, status=401)

        request.user_id = token_data.get("user_id")
        request.scope = token_data.get("scope", "").split()
        return view_func(request, *args, **kwargs)
    return wrapper

# --- User Account Management ---


@csrf_exempt
@require_http_methods(["GET", "POST"])
def register_user(request):
    """
    Handles user registration (email + password).
    Stores hashed password in Mongo and Django's User model for session login.
    """
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            return render(request, "oauth_service/register.html", {
                "error": "Email and password are required."
            })

        # Check if user already exists (Mongo)
        existing_user = user_col.find_one({"email": email})
        if existing_user:
            return render(request, "oauth_service/register.html", {
                "error": "An account with this email already exists."
            })

        # Hash password & insert into Mongo
        password_hash = hash_password_bcrypt(password)
        user_doc = {
            "email": email,
            "password_hash": password_hash,
            "created_at": datetime.utcnow(),
            "is_active": True,
        }
        result = user_col.insert_one(user_doc)

        # Create matching Django user (for session auth)
        django_user = User.objects.create_user(
            username=email, email=email, password=password
        )
        auth_login(request, django_user)

        return redirect("oauth_service:manage-apps")

    return render(request, "oauth_service/register.html")


@csrf_exempt
@require_http_methods(["GET", "POST"])
def login_user(request):
    """
    Handles user login via email + password.
    Authenticates against Mongo and Django’s User model.
    """
    if request.method == "POST":
        email = request.POST.get("username")
        password = request.POST.get("password")

        user_doc = user_col.find_one({"email": email})
        if not user_doc or not verify_bcrypt(password, user_doc.get("password_hash", "")):
            return render(request, "oauth_service/login.html", {
                "form": {"errors": True}
            })

        # Authenticate Django session user
        django_user = authenticate(request, username=email, password=password)
        if django_user:
            auth_login(request, django_user)
            return redirect("oauth_service:manage-apps")

        return render(request, "oauth_service/login.html", {
            "form": {"errors": True}
        })

    return render(request, "oauth_service/login.html")


def logout_user(request):
    """Logs out the user from Django session."""
    auth_logout(request)
    return redirect("oauth_service:login-user")

# --- Public Endpoints ---


@csrf_exempt
def authorise(request):
    """
    Handles the authorisation code grant flow's authorisation step.
    Displays a consent page (GET) or processes user consent (POST).
    """
    # Read params: prefer POST (form) when present, otherwise fall back to GET
    if request.method == "POST":
        # returns plain dict for JSON or form data
        data = _parse_request_body(request)
        client_id = data.get("client_id") or request.GET.get("client_id")
        redirect_uri = data.get(
            "redirect_uri") or request.GET.get("redirect_uri")
        response_type = data.get("response_type") or request.GET.get(
            "response_type", "code")
        scope = data.get("scope") or request.GET.get("scope", "")
        state = data.get("state") or request.GET.get("state")
    else:
        # GET (display consent)
        client_id = request.GET.get("client_id")
        redirect_uri = request.GET.get("redirect_uri")
        response_type = request.GET.get("response_type", "code")
        scope = request.GET.get("scope", "")
        state = request.GET.get("state")

    client = oauth_client_col.find_one({"client_id": client_id})
    if not client:
        return JsonResponse({"error": "Invalid client_id"}, status=400)
    if redirect_uri not in client.get("redirect_uris", []):
        return JsonResponse({"error": "Invalid redirect_uri"}, status=400)
    if response_type not in client.get("response_types", []):
        return JsonResponse({"error": "Unsupported response_type"}, status=400)

    client_scopes = set(_convert_options_to_list(client.get("scope")))
    requested_scopes = set(_convert_options_to_list(scope))
    if not requested_scopes.issubset(client_scopes):
        return JsonResponse({"error": "Invalid scope"}, status=400)

    if request.method == "GET":
        # Show consent page
        return render(request, "oauth_service/authorise.html", {
            "client": client,
            "state": state,
            "scope": scope,
            "redirect_uri": redirect_uri
        })

    # User submits consent form (POST request)
    code = secrets.token_urlsafe(24)
    oauth_code_col.insert_one({
        "code": code,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "user_id": str(request.user.id),  # Store the logged-in user's ID
        "scope": scope,
        "created_at": int(time.time()),
        "expires_at": int(time.time()) + AUTH_CODE_LIFETIME,
    })

    # Redirect back to client with authorisation code
    sep = "&" if "?" in redirect_uri else "?"
    state_param = f"&state={state}" if state else ""
    return redirect(f"{redirect_uri}{sep}code={code}{state_param}")


@csrf_exempt
def token(request):
    """
    Handles the token endpoint for exchanging authorisation codes,
    refresh tokens, and password credentials for access tokens.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method Not Allowed: POST required"}, status=405)

    client = _authenticate_client(request)
    if not client:
        return JsonResponse({"error": "Unauthorised: Invalid client credentials"}, status=401)

    data = _parse_request_body(request)
    grant_type = data.get("grant_type")

    if grant_type not in client.get("grant_types", []):
        return JsonResponse({"error": "Unsupported grant type for this client"}, status=400)

    user_id, scope = None, None
    current_time = int(time.time())

    # Grant Type: Authorisation Code
    if grant_type == "authorisation_code":
        code, redirect_uri = data.get("code"), data.get("redirect_uri")
        auth_code = oauth_code_col.find_one_and_delete(
            {"code": code, "client_id": client["client_id"]}
        )
        if not auth_code or auth_code.get("redirect_uri") != redirect_uri or auth_code.get("expires_at", 0) < current_time:
            return JsonResponse({"error": "Invalid, mismatched, or expired authorisation code"}, status=400)
        user_id, scope = auth_code["user_id"], auth_code.get("scope")

    # Grant Type: Refresh Token
    elif grant_type == "refresh_token":
        refresh_token = data.get("refresh_token")
        # For security, refresh tokens can be rotated (one-time use)
        token_data = oauth_token_col.find_one_and_delete(
            {"refresh_token": refresh_token, "client_id": client["client_id"]}
        )
        if not token_data:
            return JsonResponse({"error": "Invalid or revoked refresh token"}, status=400)
        user_id, scope = token_data["user_id"], token_data.get("scope")

    # Grant Type: Resource Owner Password Credentials
    elif grant_type == "password":
        email, password = data.get("email"), data.get("password")
        user = user_col.find_one({"email": email})
        if not user or not verify_bcrypt(password, user.get("password_hash", "")):
            return JsonResponse({"error": "Unauthorised: Invalid user credentials"}, status=401)
        user_id, scope = str(user["_id"]), " ".join(client.get("scope", []))

    else:
        return JsonResponse({"error": "Bad Request: Unsupported grant type"}, status=400)

    # Generate new tokens
    access_token = secrets.token_urlsafe(32)
    refresh_token = secrets.token_urlsafe(32)
    expires_at = current_time + ACCESS_TOKEN_LIFETIME

    oauth_token_col.insert_one({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": expires_at,
        "client_id": client["client_id"],
        "user_id": user_id,
        "scope": scope,
        "created_at": current_time,
    })

    return JsonResponse({
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": ACCESS_TOKEN_LIFETIME,
        "refresh_token": refresh_token,
        "scope": scope,
    })


@csrf_exempt
def revoke_token(request):
    """
    Implements RFC 7009: Token Revocation.
    Allows clients to revoke their access or refresh tokens.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method Not Allowed: POST required"}, status=405)

    client = _authenticate_client(request)
    if not client:
        return JsonResponse({"error": "Unauthorised: Invalid client credentials"}, status=401)

    data = _parse_request_body(request)
    token_to_revoke = data.get("token")

    if not token_to_revoke:
        return JsonResponse({"error": "Bad Request: Missing token to revoke"}, status=400)

    # Find and delete the token if it belongs to the authenticated client
    # Revoke both access and refresh tokens if either is provided
    oauth_token_col.delete_many({
        "$or": [
            {"access_token": token_to_revoke},
            {"refresh_token": token_to_revoke}
        ],
        "client_id": client["client_id"]
    })

    # RFC 7009 specifies returning 200 OK even if the token is invalid or already revoked
    return JsonResponse({}, status=200)


@oauth_required
def user_info(request):
    """
    Protected resource endpoint to retrieve basic user information (user_id and scope).
    Requires a valid access token.
    """
    return JsonResponse({"user_id": request.user_id, "scope": request.scope})


@oauth_required
def manage_apps(request):
    """
    Allows a logged-in user to see which applications they have authorised.
    Requires the user to be authenticated via Django's session or an OAuth token.
    """
    # Assuming request.user is available from Django's authentication middleware
    # and oauth_required decorator ensures request.user_id is set
    user_id = str(request.user.id) if hasattr(
        request.user, 'id') else request.user_id

    # Find all unique client_ids for which the user has tokens
    authorised_client_ids = oauth_token_col.distinct(
        "client_id",
        {"user_id": user_id}
    )
    clients = list(oauth_client_col.find(
        {"client_id": {"$in": authorised_client_ids}}
    ))
    return render(request, "oauth_service/manage_apps.html", {"clients": clients})


@oauth_required
def deauthorise_client(request):
    """
    Allows a user to revoke all tokens for a specific client application.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method Not Allowed: POST required"}, status=405)

    user_id = str(request.user.id) if hasattr(
        request.user, 'id') else request.user_id
    client_id = _parse_request_body(request).get("client_id")

    if not client_id:
        return JsonResponse({"error": "Bad Request: Missing client_id"}, status=400)

    # Delete ALL tokens for this user and client combination
    oauth_token_col.delete_many(
        {"user_id": user_id, "client_id": client_id}
    )

    return redirect(reverse('oauth_service:manage_apps'))
