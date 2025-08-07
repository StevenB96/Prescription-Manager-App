# 1. register_user_view(request)
# Route: POST /oauth/register-user/ (or whatever you wire it to)
# Purpose: Allows a new user to sign up with email and password.
# Steps:
# Validate that both email and password are present in the request.
# Check MongoDB user_col to ensure the email isn’t already taken.
# Hash the plaintext password with bcrypt and store the resulting password_hash along with the email in user_col.
# Return a success message (201 Created–style) or an error if something’s missing/duplicate.
# Why it matters:
# You need users in your system before they can authenticate & obtain tokens.

# 2. authorize(request)
# Route: GET + POST on /oauth/authorize/
# Decorator: @login_required
# Purpose: Implements the Authorization Code step.
# GET request flow:
# Reads client_id, redirect_uri, and optional state from the query string.
# Validates that client_id exists in oauth_client_col and that its redirect_uri matches.
# Renders a consent page (authorize.html) asking the logged-in user to “Authorize” the third-party app.
# POST request flow:
# After the user clicks “Authorize,” reads the same hidden form fields.
# Generates a one-time code (the authorization code).
# Stores it in oauth_code_col along with the user_id, client_id, redirect_uri, and timestamp.
# Redirects the user’s browser back to the client’s redirect_uri, appending ?code=…&state=….
# Why it matters:
# This is the user-facing consent step, and it issues the code that the client will exchange for a token.

# 3. token(request)
# Route: POST /oauth/token/
# Decorator: @csrf_exempt
# Purpose: Exchanges credentials or codes for access tokens (and refresh tokens).
# Behavior by grant_type:
# grant_type=password (Resource Owner Password Credentials)
# Reads email, password, client_id, and client_secret.
# Validates the client against oauth_client_col.
# Fetches the user document by email from user_col.
# Checks the bcrypt password_hash.
# Issues an access_token + refresh_token, stored in oauth_token_col, with an expiry.
# Returns the token JSON (access_token, expires_in, refresh_token, etc.).
# grant_type=authorization_code (Authorization Code Grant)
# Reads code, client_id, client_secret, and redirect_uri.
# Validates the client and that the one-time code exists & matches the redirect_uri.
# Deletes the used code (one-time use).
# Issues new tokens (as above) and stores them.
# Returns the token JSON.
# Why it matters:
# It’s the secure token-issuing endpoint clients use to obtain credentials for API access.

# 4. oauth_required(view_func)
# Type: Decorator
# Purpose: Protects your resource endpoints by enforcing Bearer-token authentication.
# How it works:
# Reads the Authorization: Bearer <token> header.
# Looks up the token in oauth_token_col.
# Checks that it exists and hasn’t expired (expires_at vs. time.time()).
# Injects request.user_id from the token data into the view.
# If anything fails, returns 401 Unauthorized.
# Why it matters:
# Any view wrapped in @oauth_required requires a valid access token to proceed.

# 5. user_info(request)
# Route: e.g. GET /oauth/userinfo/
# Decorator: @oauth_required
# Purpose: A simple protected resource example.
# Behavior:
# By the time your code runs, request.user_id is set by the decorator.
# Returns a JSON payload confirming access and echoing back the user’s ID.
# Why it matters:
# Demonstrates how clients can call your APIs using the Bearer token they obtained.

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

import secrets
import time
import bcrypt

from .db import (
    oauth_client_col,
    oauth_code_col,
    oauth_token_col,
    user_col,               # make sure you import your user collection here
)

# --------------------------
# 1. User Registration
# --------------------------

@csrf_exempt
def register_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    email = request.POST.get("email")
    password = request.POST.get("password")
    if not email or not password:
        return JsonResponse({"error": "Missing email or password"}, status=400)

    if user_col.find_one({"email": email}):
        return JsonResponse({"error": "Email already registered"}, status=400)

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    user_col.insert_one({
        "email": email,
        "password_hash": password_hash.decode("utf-8")
    })

    return JsonResponse({"message": "User registered successfully"})


# --------------------------
# 2. Authorization Endpoint
# --------------------------

@login_required
def authorize(request):
    if request.method == "GET":
        client_id    = request.GET.get("client_id")
        redirect_uri = request.GET.get("redirect_uri")
        state        = request.GET.get("state")

        client = oauth_client_col.find_one({"client_id": client_id})
        if not client or client["redirect_uri"] != redirect_uri:
            return JsonResponse({"error": "Invalid client or redirect_uri"}, status=400)

        return render(request, "authorize.html", {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "state": state,
        })

    # POST → user clicked “Authorize”
    user_id      = str(request.user.id)
    client_id    = request.POST["client_id"]
    redirect_uri = request.POST["redirect_uri"]
    state        = request.POST.get("state")

    code = secrets.token_urlsafe(16)
    oauth_code_col.insert_one({
        "code": code,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "user_id": user_id,
        "created_at": int(time.time()),
    })

    return redirect(f"{redirect_uri}?code={code}&state={state}")


# --------------------------
# 3. Token Exchange Endpoint
# --------------------------

@csrf_exempt
def token(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    grant_type = request.POST.get("grant_type")

    # —— Resource Owner Password Credentials Grant ——
    if grant_type == "password":
        email         = request.POST.get("email")
        password      = request.POST.get("password")
        client_id     = request.POST.get("client_id")
        client_secret = request.POST.get("client_secret")

        if not all([email, password, client_id, client_secret]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # 1. Validate client
        client = oauth_client_col.find_one({"client_id": client_id})
        if not client or client["client_secret"] != client_secret:
            return JsonResponse({"error": "Invalid client"}, status=401)

        # 2. Validate user credentials
        user = user_col.find_one({"email": email})
        if not user:
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        stored_hash = user["password_hash"].encode("utf-8")
        if not bcrypt.checkpw(password.encode("utf-8"), stored_hash):
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        # 3. Issue tokens
        access_token  = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)
        expires_in    = 3600

        oauth_token_col.insert_one({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": int(time.time()) + expires_in,
            "client_id": client_id,
            "user_id": str(user["_id"]),
        })

        return JsonResponse({
            "access_token": access_token,
            "token_type":   "Bearer",
            "expires_in":   expires_in,
            "refresh_token": refresh_token,
        })

    # —— Authorization Code Grant —— 
    elif grant_type == "authorization_code":
        code          = request.POST.get("code")
        client_id     = request.POST.get("client_id")
        client_secret = request.POST.get("client_secret")
        redirect_uri  = request.POST.get("redirect_uri")

        if not all([code, client_id, client_secret, redirect_uri]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Validate client
        client = oauth_client_col.find_one({"client_id": client_id})
        if not client or client["client_secret"] != client_secret:
            return JsonResponse({"error": "Invalid client"}, status=401)

        # Validate and consume code
        auth_code = oauth_code_col.find_one({"code": code, "client_id": client_id})
        if not auth_code or auth_code["redirect_uri"] != redirect_uri:
            return JsonResponse({"error": "Invalid or mismatched code"}, status=400)
        oauth_code_col.delete_one({"code": code})

        # Issue tokens
        access_token  = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)
        expires_in    = 3600

        oauth_token_col.insert_one({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": int(time.time()) + expires_in,
            "client_id": client_id,
            "user_id": auth_code["user_id"],
        })

        return JsonResponse({
            "access_token": access_token,
            "token_type":   "Bearer",
            "expires_in":   expires_in,
            "refresh_token": refresh_token,
        })

    else:
        return JsonResponse({"error": "Unsupported grant type"}, status=400)


# --------------------------
# 4. Protected Resource
# --------------------------

def oauth_required(view_func):
    def wrapper(request, *args, **kwargs):
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth.startswith("Bearer "):
            return JsonResponse({"error": "Unauthorized"}, status=401)

        token = auth.split()[1]
        token_data = oauth_token_col.find_one({"access_token": token})
        if not token_data or token_data["expires_at"] < time.time():
            return JsonResponse({"error": "Invalid or expired token"}, status=401)

        request.user_id = token_data["user_id"]
        return view_func(request, *args, **kwargs)
    return wrapper

@oauth_required
def user_info(request):
    return JsonResponse({
        "user_id": request.user_id,
        "message": "Access granted to protected resource"
    })