# prescription_lifecycle_app/urls.py

from django.urls import path
from . import views
from django.shortcuts import render

app_name = 'prescription_lifecycle_app'

def home(request):
    return render(request, 'prescription_lifecycle_app/base.html')

urlpatterns = [
    path('', home, name='home'),

    # Auth
    path('register/', 
         views.auth.register, 
         name='register'),
    path('login/', 
         views.auth.login, 
         name='login'),
    path('logout/', 
         views.auth.logout, 
         name='logout'),

    # OAuth2
    path('authorize/', 
         views.auth.authorize, 
         name='authorize'),
    path('token/', 
         views.auth.token, 
         name='token'),
    path('api/profile/', 
         views.auth.api_profile, 
         name='api-profile'),

    # Users CRUD
    path('users/', 
         views.user.user_list, 
         name='user-list'),
    path('users/new/', 
         views.user.user_create, 
         name='user-create'),
    path('users/<str:user_id>/', 
         views.user.user_detail, 
         name='user-detail'),
    path('users/<str:user_id>/edit/', 
         views.user.user_update, 
         name='user-update'),
    path('users/<str:user_id>/delete/',
         views.user.user_delete, 
         name='user-delete'),

     # Facility CRUD
    path('facilities/', views.facility_list, name='facility-list'),
    path('facilities/new/', views.facility_create, name='facility-create'),
    path('facilities/<str:facility_id>/', views.facility_detail, name='facility-detail'),
    path('facilities/<str:facility_id>/edit/', views.facility_update, name='facility-update'),
    path('facilities/<str:facility_id>/delete/', views.facility_delete, name='facility-delete'),

    # Medication CRUD
    path('medications/', views.medication_list, name='medication-list'),
    path('medications/new/', views.medication_create, name='medication-create'),
    path('medications/<str:medication_id>/', views.medication_detail, name='medication-detail'),
    path('medications/<str:medication_id>/edit/', views.medication_update, name='medication-update'),
    path('medications/<str:medication_id>/delete/', views.medication_delete, name='medication-delete'),

    # Prescription CRUD
    path('prescriptions/', views.prescription_list, name='prescription-list'),
    path('prescriptions/new/', views.prescription_create, name='prescription-create'),
    path('prescriptions/<str:prescription_id>/', views.prescription_detail, name='prescription-detail'),
    path('prescriptions/<str:prescription_id>/edit/', views.prescription_update, name='prescription-update'),
    path('prescriptions/<str:prescription_id>/delete/', views.prescription_delete, name='prescription-delete'),

    # Appointment CRUD
    path('appointments/', views.appointment_list, name='appointment-list'),
    path('appointments/new/', views.appointment_create, name='appointment-create'),
    path('appointments/<str:appointment_id>/', views.appointment_detail, name='appointment-detail'),
    path('appointments/<str:appointment_id>/edit/', views.appointment_update, name='appointment-update'),
    path('appointments/<str:appointment_id>/delete/', views.appointment_delete, name='appointment-delete'),
]