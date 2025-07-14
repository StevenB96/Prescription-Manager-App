# medication.py
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from prescription_lifecycle_app.models.medication import Medication

class MedicationListView(ListView):
    model = Medication
    template_name = 'prescription_lifecycle_app/medication/list.html'

class MedicationCreateView(CreateView):
    model = Medication
    fields = ['generic_name', 'brand_name', 'chemical_name', 'price', 'status']
    template_name = 'prescription_lifecycle_app/medication/form.html'
    success_url = reverse_lazy('prescription_lifecycle_app:medication-list')

class MedicationDetailView(DetailView):
    model = Medication
    template_name = 'prescription_lifecycle_app/medication/detail.html'

class MedicationUpdateView(UpdateView):
    model = Medication
    fields = ['generic_name', 'brand_name', 'chemical_name', 'price', 'status']
    template_name = 'prescription_lifecycle_app/medication/form.html'
    success_url = reverse_lazy('prescription_lifecycle_app:medication-list')

class MedicationDeleteView(DeleteView):
    model = Medication
    template_name = 'prescription_lifecycle_app/medication/confirm_delete.html'
    success_url = reverse_lazy('prescription_lifecycle_app:medication-list')