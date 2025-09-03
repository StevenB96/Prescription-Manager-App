from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from oauth_service.db.connection import oauth_client_col, oauth_token_col
from oauth_service.auth.session_helpers import get_logged_in_mongo_user
from oauth_service.forms import DeauthoriseForm


@require_http_methods(["GET", "POST"])
def manage_apps(request):
    """Displays all applications the logged-in user has authorized."""
    mongo_user = get_logged_in_mongo_user(request)
    if not mongo_user:
        return redirect("oauth_service:login-user")

    authorised_client_ids = oauth_token_col.distinct(
        "client_id", {"user_id": str(mongo_user.id)})
    clients = list(oauth_client_col.find(
        {"client_id": {"$in": authorised_client_ids}}))

    return render(request, "oauth_service/manage_apps.html", {"clients": clients})


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
