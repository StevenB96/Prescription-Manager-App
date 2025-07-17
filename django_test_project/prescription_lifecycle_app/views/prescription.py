# views/prescription.py
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from prescription_lifecycle_app.models.prescription import Prescription
from datetime import datetime

# List
def prescription_list(request):
    prescriptions = Prescription.list_all()
    return render(
        request, 
        'prescription_lifecycle_app/prescription/list.html', 
        {'prescriptions': prescriptions}
        )

# Create
@require_http_methods(["GET", "POST"])
def prescription_create(request):
    if request.method == 'POST':
        Prescription.create(
            pharmacy_id=request.POST.get('pharmacy_id'),
            medication_id=request.POST.get('medication_id'),
            prescriber_id=request.POST.get('prescriber_id'),
            patient_id=request.POST.get('patient_id'),
            medical_exemption_type=int(request.POST.get('medical_exemption_type') or Prescription.EXEMPTION_NONE),
            status=int(request.POST.get('status') or Prescription.STATUS_NEW)
        )
        return redirect(reverse('prescription_list'))
    return render(request, 'prescription_lifecycle_app/prescription/form.html', {
        'exemption_choices': Prescription.MEDICAL_EXEMPTION_CHOICES,
        'status_choices': Prescription.STATUS_CHOICES
    })

# Detail
def prescription_detail(request, prescription_id):
    pres = Prescription.get(prescription_id)
    if not pres:
        return redirect(reverse('prescription_list'))
    return render(request, 'prescription_lifecycle_app/prescription/detail.html', {'prescription': pres})

# Update
@require_http_methods(["GET", "POST"])
def prescription_update(request, prescription_id):
    pres = Prescription.get(prescription_id)
    if not pres:
        return redirect(reverse('prescription_list'))
    if request.method == 'POST':
        Prescription.update(
            prescription_id,
            pharmacy_id=request.POST.get('pharmacy_id'),
            medication_id=request.POST.get('medication_id'),
            prescriber_id=request.POST.get('prescriber_id'),
            patient_id=request.POST.get('patient_id'),
            medical_exemption_type=int(request.POST.get('medical_exemption_type') or pres.medical_exemption_type),
            status=int(request.POST.get('status') or pres.status)
        )
        return redirect(reverse('prescription_list'))
    return render(request, 'prescription_lifecycle_app/prescription/form.html', {
        'prescription': pres,
        'exemption_choices': Prescription.MEDICAL_EXEMPTION_CHOICES,
        'status_choices': Prescription.STATUS_CHOICES
    })

# Delete
@require_http_methods(["POST"])
def prescription_delete(request, prescription_id):
    Prescription.delete(prescription_id)
    return redirect(reverse('prescription_list'))