# prescription_manager_app\oauth_service\urls.py

from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

app_name = 'oauth_service'

urlpatterns = [
    # User Account Management
    # path('register/', views.register_user, name='register'),
    # path('login/', views.login_user, name='login'),  # <--- Add this line

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
