from functools import wraps
from django.shortcuts import redirect
from django.http import JsonResponse
from oauth_service.auth.session_helpers import get_logged_in_mongo_user


def mongo_login_required(view_func=None, *, redirect_url="oauth_service:login-user", json=False):
    """
    Decorator to protect endpoints by requiring a logged-in MongoDB user.

    Args:
        redirect_url (str): Named URL or path to redirect if not logged in.
        json (bool): If True, return JSON error instead of redirect.
    """

    def decorator(view):
        @wraps(view)
        def _wrapped_view(request, *args, **kwargs):
            user = get_logged_in_mongo_user(request)
            if not user:
                if json:
                    return JsonResponse(
                        {"error": "Authentication required"},
                        status=401
                    )
                return redirect(redirect_url)
            # attach user for convenience
            request.mongo_user = user
            return view(request, *args, **kwargs)
        return _wrapped_view

    return decorator(view_func) if view_func else decorator
