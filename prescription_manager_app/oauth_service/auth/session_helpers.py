from datetime import datetime
import time
from prescription_manager_app.models.user import User
from oauth_service.models import OAuthToken

# Constants
MONGO_SESSION_USER_ID = "_auth_user_id"
MONGO_SESSION_HASH = "_auth_user_hash"
ACCESS_TOKEN_EXPIRY_HOURS = 24


# -------------------- MongoDB Session Auth --------------------

def login_mongo_user(request, user: User) -> None:
    """Log in a user via session."""
    request.session.cycle_key()
    request.session[MONGO_SESSION_USER_ID] = str(user.id)
    request.session[MONGO_SESSION_HASH] = user.get_session_auth_hash()
    request.session.set_expiry(60 * 60 * 24)
    User.update(user.id, last_logged_in=datetime.utcnow())


def logout_mongo_user(request) -> None:
    """Clear session keys to log out a user."""
    for key in [MONGO_SESSION_USER_ID, MONGO_SESSION_HASH]:
        request.session.pop(key, None)


def get_logged_in_mongo_user(request) -> User | None:
    """Retrieve the currently logged-in MongoDB user from session."""
    user_id = request.session.get(MONGO_SESSION_USER_ID)
    if not user_id:
        return None

    user = User.get(user_id)
    if not user:
        return None

    session_hash = request.session.get(MONGO_SESSION_HASH)
    if session_hash != user.get_session_auth_hash():
        logout_mongo_user(request)
        return None

    return user


# -------------------- Access Token Auth --------------------

def store_token_data(request, token_data: dict):
    """
    Store access token data in the session.
    """
    request.session["token_data"] = token_data


def remove_token_data(request):
    """
    Remove access token data from the session.
    """
    request.session.pop("token_data", None)


def get_user_by_access_token(request):
    """
    Retrieve the user from the request's Authorization header (Bearer token).
    Returns None if token is invalid or expired.
    """
    token_data = request.session.get("token_data")

    if not token_data or "access_token" not in token_data:
        user = None
    else:
        token_obj = OAuthToken.get_by_access_token(token_data["access_token"])
        user = User.get(token_obj.user_id) if token_obj else None

    return user
