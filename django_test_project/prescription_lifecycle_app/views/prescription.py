# prescription.py
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from prescription_lifecycle_app.models.prescription import Prescription

class PrescriptionListView(ListView):
    model = Prescription
    template_name = 'prescription_lifecycle_app/prescription/list.html'

class PrescriptionCreateView(CreateView):
    model = Prescription
    fields = ['pharmacy', 'medication', 'prescriber', 'patient', 'medical_exemption_type', 'status']
    template_name = 'prescription_lifecycle_app/prescription/form.html'
    success_url = reverse_lazy('prescription_lifecycle_app:prescription-list')

class PrescriptionDetailView(DetailView):
    model = Prescription
    template_name = 'prescription_lifecycle_app/prescription/detail.html'

class PrescriptionUpdateView(UpdateView):
    model = Prescription
    fields = ['pharmacy', 'medication', 'prescriber', 'patient', 'medical_exemption_type', 'status']
    template_name = 'prescription_lifecycle_app/prescription/form.html'
    success_url = reverse_lazy('prescription_lifecycle_app:prescription-list')

class PrescriptionDeleteView(DeleteView):
    model = Prescription
    template_name = 'prescription_lifecycle_app/prescription/confirm_delete.html'
    success_url = reverse_lazy('prescription_lifecycle_app:prescription-list')