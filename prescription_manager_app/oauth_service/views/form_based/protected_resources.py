from django.views.decorators.http import require_http_methods
from django.http import JsonResponse


@require_http_methods(["GET"])
def user_info(request):
    """
    Protected resource endpoint to retrieve basic user information (user_id and scope).
    Assumes middleware has attached `user_id` and `scope` to the request.
    """
    return JsonResponse({"user_id": request.user_id, "scope": request.scope})
