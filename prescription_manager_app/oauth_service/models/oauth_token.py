import time
import secrets
from oauth_service.db.connection import oauth_token_col

ACCESS_TOKEN_LIFETIME = 3600


class OAuthToken:
    """
    PyMongo-backed wrapper for the 'oauth_token' collection.
    """

    def __init__(self, data):
        self._data = data

    @property
    def id(self):
        return str(self._data.get("_id"))

    @property
    def access_token(self):
        return self._data.get("access_token")

    @property
    def refresh_token(self):
        return self._data.get("refresh_token")

    @property
    def client_id(self):
        return self._data.get("client_id")

    @property
    def user_id(self):
        return self._data.get("user_id")

    @property
    def scope(self):
        return self._data.get("scope")

    @property
    def created_at(self):
        return self._data.get("created_at")

    @property
    def expires_at(self):
        return self._data.get("expires_at")

    @property
    def revoked(self):
        return self._data.get("revoked", False)

    @classmethod
    def create(cls, client_id, user_id, scope=None, lifetime=ACCESS_TOKEN_LIFETIME):
        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)
        now = int(time.time())
        expires_at = now + lifetime
        doc = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "client_id": client_id,
            "user_id": user_id,
            "scope": scope,
            "created_at": now,
            "expires_at": expires_at,
            "revoked": False,
        }
        result = oauth_token_col.insert_one(doc)
        doc["_id"] = result.inserted_id
        return cls(doc)

    @classmethod
    def get_by_access_token(cls, token):
        doc = oauth_token_col.find_one({"access_token": token})
        return cls(doc) if doc else None

    @classmethod
    def get_by_refresh_token(cls, token):
        doc = oauth_token_col.find_one({"refresh_token": token})
        return cls(doc) if doc else None

    @classmethod
    def list_all(cls):
        return [cls(d) for d in oauth_token_col.find().sort("created_at", 1)]

    @classmethod
    def update(cls, token, **kwargs):
        allowed = {"scope", "expires_at", "revoked"}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return None
        oauth_token_col.update_one(
            {"$or": [{"access_token": token}, {"refresh_token": token}]},
            {"$set": fields}
        )
        return cls.get_by_access_token(token) or cls.get_by_refresh_token(token)

    @classmethod
    def delete(cls, token):
        res = oauth_token_col.delete_many(
            {"$or": [{"access_token": token}, {"refresh_token": token}]}
        )
        return res.deleted_count > 0
