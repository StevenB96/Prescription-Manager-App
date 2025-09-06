import time
from oauth_service.db.connection import oauth_code_col

AUTH_CODE_LIFETIME = 600


class OAuthCode:
    """
    PyMongo-backed wrapper for the 'oauth_code' collection.
    """

    def __init__(self, data):
        self._data = data

    @property
    def id(self):
        return str(self._data.get("_id"))

    @property
    def code(self):
        return self._data.get("code")

    @property
    def client_id(self):
        return self._data.get("client_id")

    @property
    def user_id(self):
        return self._data.get("user_id")

    @property
    def redirect_uri(self):
        return self._data.get("redirect_uri")

    @property
    def scope(self):
        return self._data.get("scope")

    @property
    def created_at(self):
        return self._data.get("created_at")

    @property
    def expires_at(self):
        return self._data.get("expires_at")

    @classmethod
    def create(cls, code, client_id, user_id, redirect_uri=None, scope=None, lifetime=AUTH_CODE_LIFETIME):
        now = int(time.time())
        expires_at = now + lifetime
        doc = {
            "code": code,
            "client_id": client_id,
            "user_id": user_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "created_at": now,
            "expires_at": expires_at,
        }
        result = oauth_code_col.insert_one(doc)
        doc["_id"] = result.inserted_id
        return cls(doc)

    @classmethod
    def get_by_code(cls, code):
        doc = oauth_code_col.find_one({"code": code})
        return cls(doc) if doc else None

    @classmethod
    def list_all(cls):
        return [cls(d) for d in oauth_code_col.find().sort("created_at", 1)]

    @classmethod
    def update(cls, code, **kwargs):
        allowed = {"redirect_uri", "scope", "expires_at"}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return None
        oauth_code_col.update_one({"code": code}, {"$set": fields})
        return cls.get(code)

    @classmethod
    def delete(cls, code):
        res = oauth_code_col.delete_one({"code": code})
        return res.deleted_count == 1
