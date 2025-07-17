# views/appointment.py

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from prescription_lifecycle_app.models.appointment import Appointment
from datetime import datetime

@require_http_methods(["GET"])
def appointment_list(request):
    appointments = Appointment.list_all()
    return render(
        request,
        'prescription_lifecycle_app/appointment/list.html',
        {'appointments': appointments}
    )

@require_http_methods(["GET", "POST"])
def appointment_create(request):
    if request.method == 'POST':
        Appointment.create(
            surgery_id = request.POST.get('surgery_id'),
            medical_professional_id = request.POST.get('medical_professional_id'),
            patient_id = request.POST.get('patient_id'),
            time = datetime.fromisoformat(request.POST.get('time')),
            status = int(request.POST.get('status') or Appointment.STATUS_SCHEDULED),
        )
        return redirect(reverse('prescription_lifecycle_app:appointment-list'))

    form_data = {
        'surgery_id': {'value': ''},
        'medical_professional_id': {'value': ''},
        'patient_id': {'value': ''},
        'time': {'value': ''},
        'status': {'value': ''},
    }

    return render(request, 'prescription_lifecycle_app/appointment/form.html', {
        'form': form_data,
        'status_choices': Appointment.STATUS_CHOICES,
        'form_title': 'Schedule Appointment',
        'submit_label': 'Schedule',
        'list_url': reverse('prescription_lifecycle_app:appointment-list'),
    })

@require_http_methods(["GET"])
def appointment_detail(request, appointment_id):
    appointment = Appointment.get(appointment_id)
    if not appointment:
        return redirect(reverse('prescription_lifecycle_app:appointment-list'))

    return render(request, 'prescription_lifecycle_app/appointment/detail.html', {
        'appointment': appointment
    })

@require_http_methods(["GET", "POST"])
def appointment_update(request, appointment_id):
    appointment = Appointment.get(appointment_id)
    if not appointment:
        return redirect(reverse('prescription_lifecycle_app:appointment-list'))

    if request.method == 'POST':
        Appointment.update(
            appointment_id,
            surgery_id = request.POST.get('surgery_id'),
            medical_professional_id = request.POST.get('medical_professional_id'),
            patient_id = request.POST.get('patient_id'),
            time = datetime.fromisoformat(request.POST.get('time')),
            status = int(request.POST.get('status') or appointment.status),
        )
        return redirect(reverse('prescription_lifecycle_app:appointment-list'))

    form_data = {
        'surgery_id': {'value': appointment.surgery_id},
        'medical_professional_id': {'value': appointment.medical_professional_id},
        'patient_id': {'value': appointment.patient_id},
        'time': {'value': appointment.time},
        'status': {'value': appointment.status},
    }

    return render(request, 'prescription_lifecycle_app/appointment/form.html', {
        'form': form_data,
        'status_choices': Appointment.STATUS_CHOICES,
        'form_title': 'Edit Appointment',
        'submit_label': 'Save Changes',
        'list_url': reverse('prescription_lifecycle_app:appointment-list'),
    })

@require_http_methods(["GET", "POST"])
def appointment_delete(request, appointment_id):
    appointment = Appointment.get(appointment_id)
    if not appointment:
        return redirect(reverse('prescription_lifecycle_app:appointment-list'))

    if request.method == 'POST':
        Appointment.delete(appointment_id)
        return redirect(reverse('prescription_lifecycle_app:appointment-list'))

    return render(request, 'prescription_lifecycle_app/appointment/confirm_delete.html', {
        'appointment': appointment
    })