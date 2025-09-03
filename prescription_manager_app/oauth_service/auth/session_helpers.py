from datetime import datetime
from prescription_manager_app.models.user import User

# Constants
MONGO_SESSION_USER_ID = "_auth_user_id"
MONGO_SESSION_HASH = "_auth_user_hash"


def login_mongo_user(request, user: User):
    request.session.cycle_key()
    request.session[MONGO_SESSION_USER_ID] = str(user.id)
    request.session[MONGO_SESSION_HASH] = user.get_session_auth_hash()
    request.session.set_expiry(60 * 60 * 24)
    User.update(user.id, last_logged_in=datetime.utcnow())


def logout_mongo_user(request):
    """
    Clear MongoDB session keys to log out a user.
    """
    for key in [MONGO_SESSION_USER_ID, MONGO_SESSION_HASH]:
        request.session.pop(key, None)


def get_logged_in_mongo_user(request):
    """
    Retrieve the currently logged-in MongoDB user from session.
    Returns None if not logged in.
    """
    user_id = request.session.get(MONGO_SESSION_USER_ID)
    if not user_id:
        return None
    user = User.get(user_id)
    # Optional: validate session hash to prevent tampering
    if not user:
        return None
    session_hash = request.session.get(MONGO_SESSION_HASH)
    if session_hash != user.get_session_auth_hash():
        # Session hash mismatch, treat as logged out
        logout_mongo_user(request)
        return None
    return user
