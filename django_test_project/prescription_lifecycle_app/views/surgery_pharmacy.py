# surgery_pharmacy.py
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from prescription_lifecycle_app.models.surgery_pharmacy import SurgeryPharmacy

class SurgeryPharmacyListView(ListView):
    model = SurgeryPharmacy
    template_name = 'prescription_lifecycle_app/surgery_pharmacy/list.html'

class SurgeryPharmacyCreateView(CreateView):
    model = SurgeryPharmacy
    fields = ['name', 'address', 'type', 'status']
    template_name = 'prescription_lifecycle_app/surgery_pharmacy/form.html'
    success_url = reverse_lazy('prescription_lifecycle_app:location-list')

class SurgeryPharmacyDetailView(DetailView):
    model = SurgeryPharmacy
    template_name = 'prescription_lifecycle_app/surgery_pharmacy/detail.html'

class SurgeryPharmacyUpdateView(UpdateView):
    model = SurgeryPharmacy
    fields = ['name', 'address', 'type', 'status']
    template_name = 'prescription_lifecycle_app/surgery_pharmacy/form.html'
    success_url = reverse_lazy('prescription_lifecycle_app:location-list')

class SurgeryPharmacyDeleteView(DeleteView):
    model = SurgeryPharmacy
    template_name = 'prescription_lifecycle_app/surgery_pharmacy/confirm_delete.html'
    success_url = reverse_lazy('prescription_lifecycle_app:location-list')