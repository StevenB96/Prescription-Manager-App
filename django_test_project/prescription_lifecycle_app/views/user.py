# views/user.py
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from prescription_lifecycle_app.models.user import User

# List
def user_list(request):
    users = User.list_all()
    return render(
        request, 
        'prescription_lifecycle_app/user/list.html', 
        {
            'users': users
        }
    )

# Create
@require_http_methods(["GET", "POST"])
def user_create(request):
    if request.method == 'POST':
        User.create(
            username=request.POST.get('username'),
            email=request.POST.get('email'),
            password_hash=request.POST.get('password_hash'),
            role=int(request.POST.get('role')),
            status=int(request.POST.get('status', User.STATUS_ACTIVE)),
        )
        return redirect(reverse('prescription_lifecycle_app:user-list'))

    form_data = {
        'username': {'value': ''},
        'email': {'value': ''},
        'password_hash': {'value': ''},
        'role': {'value': ''},
        'status': {'value': ''},
    }

    return render(request, 'prescription_lifecycle_app/user/form.html', {
        'form': form_data,
        'role_choices': User.ROLE_CHOICES,
        'status_choices': User.STATUS_CHOICES,
        'form_title': 'Create User',
        'submit_label': 'Create',
    })

# Detail
def user_detail(request, user_id):
    user = User.get(user_id)

    if not user:
        return redirect(reverse('user-list'))
    
    return render(
        request, 
        'prescription_lifecycle_app/user/detail.html', 
        {'user': user}
    )

# Update
@require_http_methods(["GET", "POST"])
def user_update(request, user_id):
    user = User.get(user_id)
    if not user:
        return redirect(reverse('prescription_lifecycle_app:user-list'))
    
    if request.method == 'POST':
        User.update(
            user_id,
            username=request.POST.get('username'),
            email=request.POST.get('email'),
            password_hash=request.POST.get('password_hash'),
            role=int(request.POST.get('role')),
            status=int(request.POST.get('status')),
        )
        return redirect(reverse('prescription_lifecycle_app:user-list'))

    form_data = {
        'username': {'value': user.username},
        'email': {'value': user.email},
        'password_hash': {'value': ''},
        'role': {'value': user.role},
        'status': {'value': user.status},
    }

    return render(request, 'prescription_lifecycle_app/user/form.html', {
        'form': form_data,
        'role_choices': User.ROLE_CHOICES,
        'status_choices': User.STATUS_CHOICES,
        'form_title': 'Edit User',
        'submit_label': 'Save Changes',
    })

# Delete
@require_http_methods(["GET", "POST"])
def user_delete(request, user_id):
    user = User.get(user_id)
    if not user:
        return redirect(reverse('prescription_lifecycle_app:user-list'))

    if request.method == "POST":
        User.delete(user_id)
        return redirect(reverse('prescription_lifecycle_app:user-list'))

    return render(request, 
        'prescription_lifecycle_app/user/confirm_delete.html', 
        {'user': user}
    )
