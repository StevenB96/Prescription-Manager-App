# appointment.py
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from prescription_lifecycle_app.models.appointment import Appointment

class AppointmentListView(ListView):
    model = Appointment
    template_name = 'prescription_lifecycle_app/appointment/list.html'

class AppointmentCreateView(CreateView):
    model = Appointment
    fields = ['surgery', 'medical_professional', 'patient', 'time', 'status']
    template_name = 'prescription_lifecycle_app/appointment/form.html'
    success_url = reverse_lazy('prescription_lifecycle_app:appointment-list')

class AppointmentDetailView(DetailView):
    model = Appointment
    template_name = 'prescription_lifecycle_app/appointment/detail.html'

class AppointmentUpdateView(UpdateView):
    model = Appointment
    fields = ['surgery', 'medical_professional', 'patient', 'time', 'status']
    template_name = 'prescription_lifecycle_app/appointment/form.html'
    success_url = reverse_lazy('prescription_lifecycle_app:appointment-list')

class AppointmentDeleteView(DeleteView):
    model = Appointment
    template_name = 'prescription_lifecycle_app/appointment/confirm_delete.html'
    success_url = reverse_lazy('prescription_lifecycle_app:appointment-list')
