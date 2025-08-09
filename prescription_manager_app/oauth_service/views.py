# prescription_manager_app\oauth_service\views.py

import json
import time
import secrets
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from oauth_service.db.connection import (
    oauth_client_col,
    oauth_code_col,
    oauth_token_col,
    user_col,
)

from prescription_manager_app.utils.auth import (
    hash_password_bcrypt,
    verify_bcrypt,
    is_bcrypt_hash,
)


# User registration endpoint
# Accepts POST with email and password (form or JSON)
# Creates a new user if email not registered
@csrf_exempt
def register_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    email = request.POST.get("email")
    password = request.POST.get("password")
    if not email or not password:
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
            email = email or payload.get("email")
            password = password or payload.get("password")
        except Exception:
            pass

    if not email or not password:
        return JsonResponse({"error": "Missing email or password"}, status=400)

    if user_col.find_one({"email": email}):
        return JsonResponse({"error": "Email already registered"}, status=400)

    password_hash = hash_password_bcrypt(password)
    user_col.insert_one({
        "email": email,
        "password_hash": password_hash,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })

    return JsonResponse({"message": "User registered successfully"}, status=201)


# OAuth2 authorization endpoint (requires user login)
# GET: Render consent page for client app
# POST: Handle user approval and issue auth code
@login_required
def authorize(request):
    if request.method == "GET":
        client_id = request.GET.get("client_id")
        redirect_uri = request.GET.get("redirect_uri")
        state = request.GET.get("state")

        client = oauth_client_col.find_one({"client_id": client_id})
        valid_redirect = False
        if client:
            if client.get("redirect_uri") == redirect_uri:
                valid_redirect = True
            elif isinstance(client.get("redirect_uris"), list) and redirect_uri in client.get("redirect_uris"):
                valid_redirect = True

        if not client or not valid_redirect:
            return JsonResponse({"error": "Invalid client or redirect_uri"}, status=400)

        return render(request, "authorize.html", {"client_id": client_id, "redirect_uri": redirect_uri, "state": state})

    # POST: user approved the client, generate auth code and redirect back
    user_id = str(request.user.id)
    client_id = request.POST.get("client_id")
    redirect_uri = request.POST.get("redirect_uri")
    state = request.POST.get("state")

    if not all([client_id, redirect_uri]):
        return JsonResponse({"error": "Missing client_id or redirect_uri"}, status=400)

    client = oauth_client_col.find_one({"client_id": client_id})
    valid_redirect = False
    if client:
        if client.get("redirect_uri") == redirect_uri:
            valid_redirect = True
        elif isinstance(client.get("redirect_uris"), list) and redirect_uri in client.get("redirect_uris"):
            valid_redirect = True
    if not client or not valid_redirect:
        return JsonResponse({"error": "Invalid client or redirect_uri"}, status=400)

    code = secrets.token_urlsafe(24)
    oauth_code_col.insert_one({
        "code": code,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "user_id": user_id,
        "created_at": int(time.time()),
        "expires_at": int(time.time()) + 600  # 10 minutes expiry
    })

    sep = "&" if "?" in redirect_uri else "?"
    state_param = f"&state={state}" if state else ""
    return redirect(f"{redirect_uri}{sep}code={code}{state_param}")


# OAuth2 token endpoint
# Supports grant_type=password and authorization_code
# Issues access and refresh tokens on valid requests
@csrf_exempt
def token(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    # Determine grant type (form or JSON)
    grant_type = request.POST.get("grant_type") or (json.loads(request.body.decode("utf-8") or "{}").get("grant_type") if request.body else None)

    if grant_type == "password":
        data = {}
        try:
            data = json.loads(request.body.decode("utf-8") or "{}")
        except Exception:
            pass

        email = request.POST.get("email") or data.get("email")
        password = request.POST.get("password") or data.get("password")
        client_id = request.POST.get("client_id") or data.get("client_id")
        client_secret = request.POST.get("client_secret") or data.get("client_secret")

        if not all([email, password, client_id, client_secret]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        client = oauth_client_col.find_one({"client_id": client_id})
        if not client or client.get("client_secret") != client_secret:
            return JsonResponse({"error": "Invalid client"}, status=401)

        user = user_col.find_one({"email": email})
        if not user:
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        stored_hash = user.get("password_hash", "")
        if not is_bcrypt_hash(stored_hash) or not verify_bcrypt(password, stored_hash):
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        # Issue tokens
        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)
        expires_in = 3600

        oauth_token_col.insert_one({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": int(time.time()) + expires_in,
            "client_id": client_id,
            "user_id": str(user["_id"]),
            "created_at": int(time.time()),
        })

        return JsonResponse({
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": expires_in,
            "refresh_token": refresh_token,
        })

    elif grant_type == "authorization_code":
        data = {}
        try:
            data = json.loads(request.body.decode("utf-8") or "{}")
        except Exception:
            pass

        code = request.POST.get("code") or data.get("code")
        client_id = request.POST.get("client_id") or data.get("client_id")
        client_secret = request.POST.get("client_secret") or data.get("client_secret")
        redirect_uri = request.POST.get("redirect_uri") or data.get("redirect_uri")

        if not all([code, client_id, client_secret, redirect_uri]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        client = oauth_client_col.find_one({"client_id": client_id})
        if not client or client.get("client_secret") != client_secret:
            return JsonResponse({"error": "Invalid client"}, status=401)

        auth_code = oauth_code_col.find_one({"code": code, "client_id": client_id})
        if not auth_code or auth_code.get("redirect_uri") != redirect_uri:
            return JsonResponse({"error": "Invalid or mismatched code"}, status=400)

        if auth_code.get("expires_at") and auth_code["expires_at"] < int(time.time()):
            oauth_code_col.delete_one({"code": code})
            return JsonResponse({"error": "Authorization code expired"}, status=400)

        oauth_code_col.delete_one({"code": code})

        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)
        expires_in = 3600

        oauth_token_col.insert_one({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": int(time.time()) + expires_in,
            "client_id": client_id,
            "user_id": auth_code["user_id"],
            "created_at": int(time.time()),
        })

        return JsonResponse({
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": expires_in,
            "refresh_token": refresh_token,
        })

    else:
        return JsonResponse({"error": "Unsupported grant type"}, status=400)


# Decorator to protect views with OAuth2 token authentication
# Validates bearer token and token expiration
def oauth_required(view_func):
    def wrapper(request, *args, **kwargs):
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth.startswith("Bearer "):
            return JsonResponse({"error": "Unauthorized"}, status=401)
        token = auth.split()[1]
        token_data = oauth_token_col.find_one({"access_token": token})
        if not token_data or token_data.get("expires_at", 0) < int(time.time()):
            return JsonResponse({"error": "Invalid or expired token"}, status=401)
        request.user_id = token_data.get("user_id")
        return view_func(request, *args, **kwargs)
    return wrapper


# Protected resource example returning user info
@oauth_required
def user_info(request):
    return JsonResponse({"user_id": request.user_id, "message": "Access granted to protected resource"})
