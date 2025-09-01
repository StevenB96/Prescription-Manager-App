# prescription_manager_app\oauth_service\urls.py

from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

app_name = 'oauth_service'

urlpatterns = [
    # User Account Management
    path('register/', views.register_user, name='register-user'),
    path('login/', views.login_user, name='login-user'),
    path('logout/', views.logout_user, name='logout-user'),

    # OAuth2 Core Protocol Endpoints
    path('authorise/', views.authorise, name='authorise'),
    path('token/', csrf_exempt(views.token), name='token'),

    # Protected Resource Access
    path('userinfo/', csrf_exempt(views.user_info), name='user-info'),

    # User Application Management
    path('manage-apps/', views.manage_apps, name='manage-apps'),
    path('deauthorise/<int:client_id>/',
         views.deauthorise_client, name='deauthorise-client'),

    # Token Management
    path('revoke/', views.revoke_token, name='revoke-token'),
]

# OAuth flow: Client (app w/ client_id & secret) asks Auth Server for access.
# User logs in -> server returns short-lived code.
# Client exchanges code (+ credentials) for token(s).
# Token = credential to access user resources (access token, refresh token).
