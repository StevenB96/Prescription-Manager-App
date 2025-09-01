# from django.shortcuts import render, redirect
# from django.contrib.auth import authenticate, login
# from django.contrib.auth.models import User
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse

# def register(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         User.objects.create_user(username=username, password=password)
#         return redirect('login')
#     return render(request, 'prescription_manager_app/admin/auth/register.html')

# def login(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(request, username=username, password=password)
#         if user:
#             login(request, user)
#             return redirect('authorise')
#         else:
#             return render(request, 'prescription_manager_app/admin/auth/login.html', {'error': 'Invalid credentials'})
#     return render(request, 'prescription_manager_app/admin/auth/login.html')
