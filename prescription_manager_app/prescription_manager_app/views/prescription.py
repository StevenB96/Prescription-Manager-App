# views/prescription.py

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from prescription_manager_app.models.prescription import Prescription
from datetime import datetime

@require_http_methods(["GET"])
def prescription_list(request):
    prescriptions = Prescription.list_all()
    return render(
        request,
        'prescription_manager_app/admin/prescription/list.html',
        {'prescriptions': prescriptions}
    )

@require_http_methods(["GET", "POST"])
def prescription_create(request):
    if request.method == 'POST':
        Prescription.create(
            pharmacy_id = request.POST.get('pharmacy_id'),
            medication_id = request.POST.get('medication_id'),
            prescriber_id = request.POST.get('prescriber_id'),
            patient_id = request.POST.get('patient_id'),
            medical_exemption_type = int(request.POST.get('medical_exemption_type')),
            status = int(request.POST.get('status')),
        )
        return redirect(reverse('prescription_manager_app:prescription-list'))

    form_data = {
        'pharmacy_id': {'value': ''},
        'medication_id': {'value': ''},
        'prescriber_id': {'value': ''},
        'patient_id': {'value': ''},
        'medical_exemption_type': {'value': ''},
        'status': {'value': ''},
    }
    return render(request, 'prescription_manager_app/admin/prescription/form.html', {
        'form': form_data,
        'exemption_choices': Prescription.EXEMPTION_CHOICES,
        'status_choices': Prescription.STATUS_CHOICES,
        'form_title': 'Create Prescription',
        'submit_label': 'Create',
        'list_url': reverse('prescription_manager_app:prescription-list'),
    })

@require_http_methods(["GET"])
def prescription_detail(request, prescription_id):
    prescription = Prescription.get(prescription_id)
    if not prescription:
        return redirect(reverse('prescription_manager_app:prescription-list'))

    return render(request, 'prescription_manager_app/admin/prescription/detail.html', {
        'prescription': prescription
    })

@require_http_methods(["GET", "POST"])
def prescription_update(request, prescription_id):
    prescription = Prescription.get(prescription_id)
    if not prescription:
        return redirect(reverse('prescription_manager_app:prescription-list'))

    if request.method == 'POST':
        Prescription.update(
            prescription_id,
            pharmacy_id = request.POST.get('pharmacy_id'),
            medication_id = request.POST.get('medication_id'),
            prescriber_id = request.POST.get('prescriber_id'),
            patient_id = request.POST.get('patient_id'),
            medical_exemption_type = int(request.POST.get('medical_exemption_type')),
            status = int(request.POST.get('status')),
        )
        return redirect(reverse('prescription_manager_app:prescription-list'))

    form_data = {
        'pharmacy_id': {'value': prescription.pharmacy_id},
        'medication_id': {'value': prescription.medication_id},
        'prescriber_id': {'value': prescription.prescriber_id},
        'patient_id': {'value': prescription.patient_id},
        'medical_exemption_type': {'value': prescription.medical_exemption_type},
        'status': {'value': prescription.status},
    }

    return render(request, 'prescription_manager_app/admin/prescription/form.html', {
        'form': form_data,
        'exemption_choices': Prescription.EXEMPTION_CHOICES,
        'status_choices': Prescription.STATUS_CHOICES,
        'form_title': 'Edit Prescription',
        'submit_label': 'Save Changes',
        'list_url': reverse('prescription_manager_app:prescription-list'),
    })

@require_http_methods(["GET", "POST"])
def prescription_delete(request, prescription_id):
    prescription = Prescription.get(prescription_id)
    if not prescription:
        return redirect(reverse('prescription_manager_app:prescription-list'))

    if request.method == 'POST':
        Prescription.delete(prescription_id)
        return redirect(reverse('prescription_manager_app:prescription-list'))

    return render(request, 'prescription_manager_app/admin/prescription/confirm_delete.html', {
        'prescription': prescription
    })