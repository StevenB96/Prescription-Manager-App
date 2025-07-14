# prescription_lifecycle_app/urls.py
from django.urls import path
from . import views

app_name = 'prescription_lifecycle_app'

urlpatterns = [
    # User CRUD
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/create/', views.UserCreateView.as_view(), name='user-create'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/update/', views.UserUpdateView.as_view(), name='user-update'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user-delete'),

    # Surgery/Pharmacy CRUD
    path('locations/', views.SurgeryPharmacyListView.as_view(), name='location-list'),
    path('locations/create/', views.SurgeryPharmacyCreateView.as_view(), name='location-create'),
    path('locations/<int:pk>/', views.SurgeryPharmacyDetailView.as_view(), name='location-detail'),
    path('locations/<int:pk>/update/', views.SurgeryPharmacyUpdateView.as_view(), name='location-update'),
    path('locations/<int:pk>/delete/', views.SurgeryPharmacyDeleteView.as_view(), name='location-delete'),

    # Medication CRUD
    path('medications/', views.MedicationListView.as_view(), name='medication-list'),
    path('medications/create/', views.MedicationCreateView.as_view(), name='medication-create'),
    path('medications/<int:pk>/', views.MedicationDetailView.as_view(), name='medication-detail'),
    path('medications/<int:pk>/update/', views.MedicationUpdateView.as_view(), name='medication-update'),
    path('medications/<int:pk>/delete/', views.MedicationDeleteView.as_view(), name='medication-delete'),

    # Prescription CRUD
    path('prescriptions/', views.PrescriptionListView.as_view(), name='prescription-list'),
    path('prescriptions/create/', views.PrescriptionCreateView.as_view(), name='prescription-create'),
    path('prescriptions/<int:pk>/', views.PrescriptionDetailView.as_view(), name='prescription-detail'),
    path('prescriptions/<int:pk>/update/', views.PrescriptionUpdateView.as_view(), name='prescription-update'),
    path('prescriptions/<int:pk>/delete/', views.PrescriptionDeleteView.as_view(), name='prescription-delete'),

    # Appointment CRUD
    path('appointments/', views.AppointmentListView.as_view(), name='appointment-list'),
    path('appointments/create/', views.AppointmentCreateView.as_view(), name='appointment-create'),
    path('appointments/<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment-detail'),
    path('appointments/<int:pk>/update/', views.AppointmentUpdateView.as_view(), name='appointment-update'),
    path('appointments/<int:pk>/delete/', views.AppointmentDeleteView.as_view(), name='appointment-delete'),
]