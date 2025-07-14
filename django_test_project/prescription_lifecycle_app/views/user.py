# user.py
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from prescription_lifecycle_app.models.user import User

class UserListView(ListView):
    model = User
    template_name = 'user_list.html'

class UserCreateView(CreateView):
    model = User
    fields = ['username', 'email', 'password_hash', 'role', 'status']
    template_name = 'user_form.html'
    success_url = reverse_lazy('prescription_lifecycle_app:user-list')

class UserDetailView(DetailView):
    model = User
    template_name = 'user_detail.html'

class UserUpdateView(UpdateView):
    model = User
    fields = ['username', 'email', 'password_hash', 'role', 'status']
    template_name = 'user_form.html'
    success_url = reverse_lazy('prescription_lifecycle_app:user-list')

class UserDeleteView(DeleteView):
    model = User
    template_name = 'user_confirm_delete.html'
    success_url = reverse_lazy('prescription_lifecycle_app:user-list')