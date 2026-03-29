# prescription_manager_app/prescription_manager_app/urls.py

from django.urls import path
from . import views
from django.shortcuts import render
from oauth_service.decorators import mongo_admin_required

app_name = 'prescription_manager_app'


@mongo_admin_required()
def home(request):
    return render(request, 'prescription_manager_app/admin/base.html')


urlpatterns = [
    path('', home, name='home'),
    path('admin', home, name='home'),

    # Users CRUD
    path(
        'admin/users/',
        mongo_admin_required()(views.user.user_list),
        name='user-list'
    ),
    path(
        'admin/users/new/',
        mongo_admin_required()(views.user.user_create),
        name='user-create'
    ),
    path(
        'admin/users/<str:user_id>/',
        mongo_admin_required()(views.user.user_detail),
        name='user-detail'
    ),
    path(
        'admin/users/<str:user_id>/edit/',
        mongo_admin_required()(views.user.user_update),
        name='user-update'
    ),
    path(
        'admin/users/<str:user_id>/delete/',
        mongo_admin_required()(views.user.user_delete),
        name='user-delete'
    ),

    # Facility CRUD
    path(
        'admin/facilities/',
        mongo_admin_required()(views.facility_list),
        name='facility-list'
    ),
    path(
        'admin/facilities/new/',
        mongo_admin_required()(views.facility_create),
        name='facility-create'
    ),
    path(
        'admin/facilities/<str:facility_id>/',
        mongo_admin_required()(views.facility_detail),
        name='facility-detail'
    ),
    path(
        'admin/facilities/<str:facility_id>/edit/',
        mongo_admin_required()(views.facility_update),
        name='facility-update'
    ),
    path(
        'admin/facilities/<str:facility_id>/delete/',
        mongo_admin_required()(views.facility_delete),
        name='facility-delete'
    ),

    # Medication CRUD
    path(
        'admin/medications/',
        mongo_admin_required()(views.medication_list),
        name='medication-list'
    ),
    path(
        'admin/medications/new/',
        mongo_admin_required()(views.medication_create),
        name='medication-create'
    ),
    path(
        'admin/medications/<str:medication_id>/',
        mongo_admin_required()(views.medication_detail),
        name='medication-detail'
    ),
    path(
        'admin/medications/<str:medication_id>/edit/',
        mongo_admin_required()(views.medication_update),
        name='medication-update'
    ),
    path(
        'admin/medications/<str:medication_id>/delete/',
        mongo_admin_required()(views.medication_delete),
        name='medication-delete'
    ),

    # Prescription CRUD
    path(
        'admin/prescriptions/',
        mongo_admin_required()(views.prescription_list),
        name='prescription-list'
    ),
    path(
        'admin/prescriptions/new/',
        mongo_admin_required()(views.prescription_create),
        name='prescription-create'
    ),
    path(
        'admin/prescriptions/<str:prescription_id>/',
        mongo_admin_required()(views.prescription_detail),
        name='prescription-detail'
    ),
    path(
        'admin/prescriptions/<str:prescription_id>/edit/',
        mongo_admin_required()(views.prescription_update),
        name='prescription-update'
    ),
    path(
        'admin/prescriptions/<str:prescription_id>/delete/',
        mongo_admin_required()(views.prescription_delete),
        name='prescription-delete'
    ),

    # Appointment CRUD
    path(
        'admin/appointments/',
        mongo_admin_required()(views.appointment_list),
        name='appointment-list'
    ),
    path(
        'admin/appointments/new/',
        mongo_admin_required()(views.appointment_create),
        name='appointment-create'
    ),
    path(
        'admin/appointments/<str:appointment_id>/',
        mongo_admin_required()(views.appointment_detail),
        name='appointment-detail'
    ),
    path(
        'admin/appointments/<str:appointment_id>/edit/',
        mongo_admin_required()(views.appointment_update),
        name='appointment-update'
    ),
    path(
        'admin/appointments/<str:appointment_id>/delete/',
        mongo_admin_required()(views.appointment_delete),
        name='appointment-delete'
    ),
]
