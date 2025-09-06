from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from oauth_service.db.connection import oauth_code_col, oauth_token_col
from oauth_service.auth.session_helpers import get_logged_in_mongo_user
from oauth_service.forms import DeauthoriseForm
from django.conf import settings


@require_http_methods(["GET", "POST"])
def manage_apps(request):
    """Displays all tokens and codes for the logged-in user."""
    mongo_user = get_logged_in_mongo_user(request)
    if not mongo_user:
        return redirect("oauth_service:login-user")

    user_id = str(mongo_user.id)

    # Fetch user tokens and codes
    user_tokens = list(oauth_token_col.find({"user_id": user_id}))
    user_codes = list(oauth_code_col.find({"user_id": user_id}))

    # Normalize into a single list with type labels
    items = []

    for t in user_tokens:
        items.append({
            "type": "token",
            "client_id": t["client_id"],
            "client_secret": settings.INTERNAL_OAUTH_CLIENT_SECRET,
            "access_token": t.get("access_token"),
            "refresh_token": t.get("refresh_token"),
            "expires_at": t.get("expires_at"),
            "scope": t.get("scope"),
            "created_at": t.get("created_at"),
        })

    for c in user_codes:
        items.append({
            "type": "code",
            "client_id": c["client_id"],
            "client_secret": settings.INTERNAL_OAUTH_CLIENT_SECRET,
            "code": c.get("code"),
            "redirect_uri": c.get("redirect_uri"),
            "expires_at": c.get("expires_at"),
            "scope": c.get("scope"),
            "created_at": c.get("created_at"),
        })

    return render(
        request,
        "oauth_service/manage_apps.html",
        {"items": items},
    )


@require_http_methods(["POST"])
def deauthorise_client(request):
    """Revokes all tokens for a specific client application."""
    mongo_user = get_logged_in_mongo_user(request)
    if not mongo_user:
        return redirect("oauth_service:login-user")

    form = DeauthoriseForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"error": form.errors}, status=400)

    client_id = form.cleaned_data["client_id"]

    oauth_token_col.delete_many({
        "user_id": str(mongo_user.id),
        "client_id": client_id
    })

    return redirect(reverse('oauth_service:manage-apps'))
