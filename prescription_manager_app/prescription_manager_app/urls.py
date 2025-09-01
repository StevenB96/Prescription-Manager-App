# prescription_manager_app\prescription_manager_app\urls.py

from django.urls import path
from . import views
from django.shortcuts import render

app_name = 'prescription_manager_app'


def home(request):
    return render(request, 'prescription_manager_app/admin/base.html')


urlpatterns = [
    path('admin', home, name='home'),

    # Users CRUD
    path('admin/users/',
         views.user.user_list,
         name='user-list'),
    path('admin/users/new/',
         views.user.user_create,
         name='user-create'),
    path('admin/users/<str:user_id>/',
         views.user.user_detail,
         name='user-detail'),
    path('admin/users/<str:user_id>/edit/',
         views.user.user_update,
         name='user-update'),
    path('admin/users/<str:user_id>/delete/',
         views.user.user_delete,
         name='user-delete'),

    # Facility CRUD
    path('admin/facilities/', views.facility_list, name='facility-list'),
    path('admin/facilities/new/', views.facility_create, name='facility-create'),
    path('admin/facilities/<str:facility_id>/',
         views.facility_detail, name='facility-detail'),
    path('admin/facilities/<str:facility_id>/edit/',
         views.facility_update, name='facility-update'),
    path('admin/facilities/<str:facility_id>/delete/',
         views.facility_delete, name='facility-delete'),

    # Medication CRUD
    path('admin/medications/', views.medication_list, name='medication-list'),
    path('admin/medications/new/', views.medication_create,
         name='medication-create'),
    path('admin/medications/<str:medication_id>/',
         views.medication_detail, name='medication-detail'),
    path('admin/medications/<str:medication_id>/edit/',
         views.medication_update, name='medication-update'),
    path('admin/medications/<str:medication_id>/delete/',
         views.medication_delete, name='medication-delete'),

    # Prescription CRUD
    path('admin/prescriptions/', views.prescription_list, name='prescription-list'),
    path('admin/prescriptions/new/', views.prescription_create,
         name='prescription-create'),
    path('admin/prescriptions/<str:prescription_id>/',
         views.prescription_detail, name='prescription-detail'),
    path('admin/prescriptions/<str:prescription_id>/edit/',
         views.prescription_update, name='prescription-update'),
    path('admin/prescriptions/<str:prescription_id>/delete/',
         views.prescription_delete, name='prescription-delete'),

    # Appointment CRUD
    path('admin/appointments/', views.appointment_list, name='appointment-list'),
    path('admin/appointments/new/', views.appointment_create,
         name='appointment-create'),
    path('admin/appointments/<str:appointment_id>/',
         views.appointment_detail, name='appointment-detail'),
    path('admin/appointments/<str:appointment_id>/edit/',
         views.appointment_update, name='appointment-update'),
    path('admin/appointments/<str:appointment_id>/delete/',
         views.appointment_delete, name='appointment-delete'),
]
