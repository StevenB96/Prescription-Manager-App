import json
import time
import secrets
import base64
from datetime import datetime

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.urls import reverse

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


def to_scope_list(value):
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
    auth_header = request.META.get("HTTP_AUTHORIZATION", "")
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
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
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

# --- Public Endpoints ---


# @csrf_exempt
# def register_user(request):
#     """
#     Handles user registration. Supports GET for showing the form and POST for submission.
#     """
#     if request.method == "GET":
#         return render(request, "oauth_service/register.html")
#     if request.method != "POST":
#         return JsonResponse({"error": "Method Not Allowed: POST required"}, status=405)

#     data = _parse_request_body(request)
#     email, password = data.get("email"), data.get("password")

#     if not email or not password:
#         return JsonResponse({"error": "Bad Request: Missing email or password"}, status=400)
#     if user_col.find_one({"email": email}):
#         return JsonResponse({"error": "Conflict: Email already registered"}, status=409)

#     user_col.insert_one({
#         "email": email,
#         "password_hash": hash_password_bcrypt(password),
#         "created_at": datetime.utcnow(),
#         "updated_at": datetime.utcnow()
#     })
#     return JsonResponse({"message": "User registered successfully"}, status=201)


@csrf_exempt
def authorise(request):
    """
    Handles the authorization code grant flow's authorization step.
    Displays a consent page (GET) or processes user consent (POST).
    """
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

    client_scopes = set(to_scope_list(client.get("scope")))
    requested_scopes = set(to_scope_list(scope))
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

    # Assuming user is logged in (Django's auth_login should handle this)
    if not request.user.is_authenticated:
        # Depending on app design, might redirect to login page instead
        return JsonResponse({"error": "Unauthorised: User not logged in"}, status=401)

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

    # Redirect back to client with authorization code
    sep = "&" if "?" in redirect_uri else "?"
    state_param = f"&state={state}" if state else ""
    return redirect(f"{redirect_uri}{sep}code={code}{state_param}")


@csrf_exempt
def token(request):
    """
    Handles the token endpoint for exchanging authorization codes,
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

    # Grant Type: Authorization Code
    if grant_type == "authorization_code":
        code, redirect_uri = data.get("code"), data.get("redirect_uri")
        auth_code = oauth_code_col.find_one_and_delete(
            {"code": code, "client_id": client["client_id"]}
        )
        if not auth_code or auth_code.get("redirect_uri") != redirect_uri or auth_code.get("expires_at", 0) < current_time:
            return JsonResponse({"error": "Invalid, mismatched, or expired authorization code"}, status=400)
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
