# from django.shortcuts import render, redirect
# from django.urls import reverse
# from django.contrib.auth import logout as django_logout
# from django.contrib import messages
# from django.http import JsonResponse

# from werkzeug.security import generate_password_hash, check_password_hash
# from prescription_manager_app.models.user import User

# from authlib.integrations.django_oauth2 import AuthorizationServer, ResourceProtector
# from prescription_manager_app.oauth.storage import (
#     query_client, save_token, AuthorizationCodeGrant, ClientCredentialsGrant
# )

# # Pass query_client and save_token as positional args
# authorization = AuthorizationServer(query_client, save_token)
# require_oauth  = ResourceProtector()

# # Register grants immediately
# authorization.register_grant(AuthorizationCodeGrant)
# authorization.register_grant(ClientCredentialsGrant)

# def get_current_user(request):
#     uid = request.session.get('user_id')
#     return User.get(uid) if uid else None

# # — Registration —
# def register(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         email    = request.POST['email']
#         password = request.POST['password']
#         role     = int(request.POST['role'])
#         pw_hash  = generate_password_hash(password)
#         User.create(username, email, pw_hash, role)
#         messages.success(request, 'Registration successful. Please log in.')
#         return redirect(reverse('login'))
#     return render(request, 'prescription_manager_app/admin/auth/register.html')

# # — Login —
# def login(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         user = User.get_by_username(username)
#         if user and check_password_hash(user.password_hash, password):
#             request.session['user_id'] = user.id
#             return redirect(request.GET.get('next', reverse('user-list')))
#         messages.error(request, 'Invalid username or password')
#     return render(request, 'prescription_manager_app/admin/auth/login.html')

# # — Logout —
# def logout(request):
#     django_logout(request)
#     return redirect(reverse('login'))

# # — OAuth2 Authorization Endpoint —
# def authorize(request):
#     user = get_current_user(request)
#     if not user:
#         return redirect(f"{reverse('login')}?next={request.path}")

#     if request.method == 'GET':
#         grant = authorization.get_consent_grant(request=request, end_user=user)
#         return render(request, 'oauth/authorize.html', {
#             'client': grant.client,
#             'scopes': grant.request.scope.split()
#         })

#     confirmed = request.POST.get('confirm') == 'yes'
#     return authorization.create_authorization_response(
#         request=request,
#         grant_user=user if confirmed else None
#     )

# # — OAuth2 Token Endpoint —
# def token(request):
#     return authorization.create_token_response(request)

# # — Protected Profile API —
# @require_oauth('profile')
# def api_profile(request):
#     user = User.get(request.resource_owner.user_id)
#     return JsonResponse({
#         'username': user.username,
#         'email': user.email,
#         'role': user.role
#     })
