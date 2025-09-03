from django.urls import path
from django.shortcuts import render
from . import views

from oauth_service.auth.session_helpers import (
    get_logged_in_mongo_user
)

app_name = 'oauth_service'


def index(request):
    user = get_logged_in_mongo_user(request)

    return render(request, 'oauth_service/base.html', {
        "user": user
    })

# Typical Screen Order Summary
# Client Login/Sign-in Page → User clicks “Login with Provider”
# OAuth Provider Login Page → User logs in
# Consent/Authorization Page → User allows or denies permissions
# Redirect Back to Client App → User sees a “Logged in successfully” screen
# Client App Fetches Tokens (backend, invisible to user)
# Protected Resource Access → User sees app content


urlpatterns = [
    path('', index, name='index'),

    # --- 🧑‍💻 User Account Management ---
    path('register/',
         views.form_based.user_management.register_user,
         name='register-user'
         ),
    path('login/',
         views.form_based.user_management.login_user,
         name='login-user'
         ),
    path('logout/',
         views.form_based.user_management.logout_user,
         name='logout-user'
         ),

    # --- 🔑 OAuth 2.0 Core Protocol Endpoints ---
    path('authorise/',
         views.form_based.oauth2_core.authorise,
         name='authorise'
         ),
    path('token/',
         views.form_based.oauth2_core.token,
         name='token'
         ),
    path('revoke/',
         views.form_based.oauth2_core.revoke_token,
         name='revoke-token'
         ),

    # --- 🔐 Protected Resource Endpoints ---
    path('userinfo/',
         views.form_based.protected_resources.user_info,
         name='user-info'
         ),

    # --- 🛠️ User Application Management ---
    path('manage-apps/',
         views.form_based.application_management.manage_apps,
         name='manage-apps'
         ),
    path('deauthorise/',
         views.form_based.application_management.deauthorise_client,
         name='deauthorise-client'
         ),
]
