# views/appointment.py
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from prescription_lifecycle_app.models.appointment import Appointment
from datetime import datetime

# List

def appointment_list(request):
    appointments = Appointment.list_all()
    return render(
        request, 
        'appointment/list.html', 
        {'appointments': appointments}
        )

# Create
@require_http_methods(["GET", "POST"])
def appointment_create(request):
    if request.method == 'POST':
        Appointment.create(
            surgery_id=request.POST.get('surgery_id'),
            medical_professional_id=request.POST.get('medical_professional_id'),
            patient_id=request.POST.get('patient_id'),
            time=datetime.fromisoformat(request.POST.get('time')),
            status=int(request.POST.get('status') or Appointment.STATUS_SCHEDULED)
        )
        return redirect(reverse('appointment_list'))
    return render(request, 'appointment/form.html', {'status_choices': Appointment.STATUS_CHOICES})

# Detail

def appointment_detail(request, appointment_id):
    appt = Appointment.get(appointment_id)
    if not appt:
        return redirect(reverse('appointment_list'))
    return render(request, 'appointment/detail.html', {'appointment': appt})

# Update
@require_http_methods(["GET", "POST"])
def appointment_update(request, appointment_id):
    appt = Appointment.get(appointment_id)
    if not appt:
        return redirect(reverse('appointment_list'))
    if request.method == 'POST':
        Appointment.update(
            appointment_id,
            surgery_id=request.POST.get('surgery_id'),
            medical_professional_id=request.POST.get('medical_professional_id'),
            patient_id=request.POST.get('patient_id'),
            time=datetime.fromisoformat(request.POST.get('time')),
            status=int(request.POST.get('status') or appt.status)
        )
        return redirect(reverse('appointment_list'))
    return render(request, 'appointment/form.html', {'appointment': appt, 'status_choices': Appointment.STATUS_CHOICES})

# Delete
@require_http_methods(["POST"])
def appointment_delete(request, appointment_id):
    Appointment.delete(appointment_id)
    return redirect(reverse('appointment_list'))