# prescription_manager_app\oauth_service\urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('authorize/', 
        views.authorize, 
        name='authorize'),
    path('token/', 
        views.token, 
        name='token'),
    path('userinfo/', 
        views.user_info, 
        name='user_info'),
    path('register-client/', 
        views.register_user, 
        name='register_user'),
]