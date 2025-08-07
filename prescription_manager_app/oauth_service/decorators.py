from django.http import JsonResponse
import time
from .db import oauth_token_col

def oauth_required(view_func):
    def wrapper(request, *args, **kwargs):
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth.startswith("Bearer "):
            return JsonResponse({"error": "Unauthorized"}, status=401)

        token = auth.split()[1]
        token_data = oauth_token_col.find_one({"access_token": token})
        if not token_data or token_data["expires_at"] < time.time():
            return JsonResponse({"error": "Invalid or expired token"}, status=401)

        request.user_id = token_data["user_id"]
        return view_func(request, *args, **kwargs)
    return wrapper
