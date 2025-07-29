from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from prescription_manager_app.models.medication import Medication

# List
def medication_list(request):
    medications = Medication.list_all()
    return render(
        request,
        'prescription_manager_app/medication/list.html',
        {'medications': medications}
    )

# Create
@require_http_methods(["GET", "POST"])
def medication_create(request):
    if request.method == 'POST':
        Medication.create(
            generic_name=request.POST.get('generic_name'),
            brand_name=request.POST.get('brand_name'),
            chemical_name=request.POST.get('chemical_name'),
            price=float(request.POST.get('price') or 0),
            status=int(request.POST.get('status') or Medication.STATUS_ACTIVE),
        )
        return redirect(reverse('prescription_manager_app:medication-list'))

    form_data = {
        'generic_name': {'value': ''},
        'brand_name': {'value': ''},
        'chemical_name': {'value': ''},
        'price': {'value': ''},
        'status': {'value': Medication.STATUS_ACTIVE},
    }

    return render(request, 'prescription_manager_app/medication/form.html', {
        'form': form_data,
        'status_choices': Medication.STATUS_CHOICES,
        'form_title': 'Create Medication',
        'submit_label': 'Create',
    })

# Detail
def medication_detail(request, medication_id):
    medication = Medication.get(medication_id)
    if not medication:
        return redirect(reverse('prescription_manager_app:medication-list'))

    return render(
        request,
        'prescription_manager_app/medication/detail.html',
        {'medication': medication}
    )

# Update
@require_http_methods(["GET", "POST"])
def medication_update(request, medication_id):
    medication = Medication.get(medication_id)
    if not medication:
        return redirect(reverse('prescription_manager_app:medication-list'))

    if request.method == 'POST':
        Medication.update(
            medication_id,
            generic_name=request.POST.get('generic_name'),
            brand_name=request.POST.get('brand_name'),
            chemical_name=request.POST.get('chemical_name'),
            price=float(request.POST.get('price') or 0),
            status=int(request.POST.get('status') or medication.status),
        )
        return redirect(reverse('prescription_manager_app:medication-list'))

    form_data = {
        'generic_name': {'value': medication.generic_name},
        'brand_name': {'value': medication.brand_name},
        'chemical_name': {'value': medication.chemical_name},
        'price': {'value': medication.price},
        'status': {'value': medication.status},
    }

    return render(request, 'prescription_manager_app/medication/form.html', {
        'form': form_data,
        'status_choices': Medication.STATUS_CHOICES,
        'form_title': 'Edit Medication',
        'submit_label': 'Save Changes',
    })

# Delete
@require_http_methods(["GET", "POST"])
def medication_delete(request, medication_id):
    medication = Medication.get(medication_id)
    if not medication:
        return redirect(reverse('prescription_manager_app:medication-list'))

    if request.method == 'POST':
        Medication.delete(medication_id)
        return redirect(reverse('prescription_manager_app:medication-list'))

    return render(
        request,
        'prescription_manager_app/medication/confirm_delete.html',
        {'medication': medication}
    )
