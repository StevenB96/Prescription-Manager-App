# views/facility.py
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from prescription_manager_app.models.facility import Facility

@require_http_methods(["GET"])
def facility_list(request):
    facilities = Facility.list_all()
    return render(
        request, 
        'prescription_manager_app/admin/facility/list.html', 
        {'facilities': facilities}
        )

@require_http_methods(["GET", "POST"])
def facility_create(request):
    if request.method == 'POST':
        Facility.create(
            name=request.POST.get('name'),
            address=request.POST.get('address'),
            type=int(request.POST.get('type')),
            status=int(request.POST.get('status')),
        )
        return redirect(reverse('prescription_manager_app:facility-list'))

    form_data = {
        'name': {'value': ''},
        'address': {'value': ''},
        'type': {'value': ''},
        'status': {'value': ''},
    }

    return render(request, 'prescription_manager_app/admin/facility/form.html', {
        'form': form_data,
        'type_choices': Facility.TYPE_CHOICES,
        'status_choices': Facility.STATUS_CHOICES,
        'form_title': 'Create Facility',
        'submit_label': 'Create',
    })

@require_http_methods(["GET"])
def facility_detail(request, facility_id):
    facility = Facility.get(facility_id)
    if not facility:
        return redirect(reverse('prescription_manager_app:facility-list'))
    return render(request, 'prescription_manager_app/admin/facility/detail.html', {'facility':facility})

@require_http_methods(["GET", "POST"])
def facility_update(request, facility_id):
    facility = Facility.get(facility_id)
    if not facility:
        return redirect(reverse('prescription_manager_app:facility-list'))

    if request.method == 'POST':
        Facility.update(
            facility_id,
            name=request.POST.get('name'),
            address=request.POST.get('address'),
            type=int(request.POST.get('type')),
            status=int(request.POST.get('status')),
        )
        return redirect(reverse('prescription_manager_app:facility-list'))

    form_data = {
        'name': {'value': facility.name},
        'address': {'value': facility.address},
        'type': {'value': facility.type},
        'status': {'value': facility.status},
    }

    return render(request, 'prescription_manager_app/admin/facility/form.html', {
        'form': form_data,
        'type_choices': Facility.TYPE_CHOICES,
        'status_choices': Facility.STATUS_CHOICES,
        'form_title': 'Edit Facility',
        'submit_label': 'Save Changes',
    })

@require_http_methods(["GET","POST"])
def facility_delete(request, facility_id):
    facility = Facility.get(facility_id)
    if not facility:
        return redirect(reverse('prescription_manager_app:facility-list'))
    if request.method=='POST':
        Facility.delete(facility_id)
        return redirect(reverse('prescription_manager_app:facility-list'))
    return render(request, 'prescription_manager_app/admin/facility/confirm_delete.html', {'facility':facility})
