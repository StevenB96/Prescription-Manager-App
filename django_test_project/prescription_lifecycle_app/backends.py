from bson.objectid import ObjectId
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password

from .db import user_col
from prescription_lifecycle_app.models.user import User

class MongoBackend(BaseBackend):
    """
    Authenticate against MongoDB “users” collection.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        user_doc = user_col.find_one({"username": username})
        if not user_doc:
            return None
        if not check_password(password, user_doc["password_hash"]):
            return None
        return User(user_doc)

    def get_user(self, user_id):
        try:
            oid = ObjectId(user_id)
        except Exception:
            return None
        doc = user_col.find_one({"_id": oid})
        return User(doc) if doc else None
