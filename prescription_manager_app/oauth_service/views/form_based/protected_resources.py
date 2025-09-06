from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from oauth_service.auth.session_helpers import get_logged_in_mongo_user


@require_http_methods(["GET"])
def user_info(request):
    """
    Protected resource endpoint to retrieve basic user information (user_id and scope).
    Assumes middleware has attached `user_id` and `scope` to the request.
    """
    mongo_user = get_logged_in_mongo_user(request)

    return JsonResponse({"user_id": mongo_user.id})
