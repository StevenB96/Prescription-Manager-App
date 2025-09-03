from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from oauth_service.forms import RegisterForm, LoginForm
from prescription_manager_app.models.user import User
from oauth_service.auth.session_helpers import (
    login_mongo_user,
    logout_mongo_user,
    get_logged_in_mongo_user
)


@require_http_methods(["GET", "POST"])
def register_user(request):
    """Handles user registration using Django Forms."""
    form = RegisterForm(request.POST if request.method == "POST" else None)

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]

        try:
            User.create(
                username=email,
                email=email,
                password=password,
                role=User.ROLE_ADMIN
            )
        except ValueError as e:
            return render(request, "oauth_service/register.html", {
                "form": form,
                "error": str(e)
            })

        return redirect("oauth_service:login-user")

    return render(request, "oauth_service/register.html", {
        "form": form,
        "user": get_logged_in_mongo_user(request)
    })


@csrf_exempt
@require_http_methods(["GET", "POST"])
def login_user(request):
    """Handles user login using Django Forms."""
    form = LoginForm(request.POST if request.method == "POST" else None)

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["username"]
        password = form.cleaned_data["password"]

        mongo_user = User.get_by_email(email)
        if mongo_user and mongo_user.check_password(password):
            login_mongo_user(request, mongo_user)
            return redirect("oauth_service:index")
        form.add_error(None, "Invalid credentials or inactive account")

    return render(request, "oauth_service/login.html", {
        "form": form,
        "user": get_logged_in_mongo_user(request)
    })


@require_http_methods(["GET"])
def logout_user(request):
    """Logs out the user from Django session."""
    logout_mongo_user(request)
    return redirect("oauth_service:login-user")
