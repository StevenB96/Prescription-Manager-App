from bson.objectid import ObjectId
import time
from oauth_service.db.connection import oauth_client_col


class OAuthClient:
    """
    PyMongo-backed wrapper for the 'oauth_client' collection.
    """

    def __init__(self, data):
        self._data = data

    @property
    def id(self):
        return str(self._data.get("_id"))

    @property
    def client_id(self):
        return self._data.get("client_id")

    @property
    def client_secret(self):
        return self._data.get("client_secret")

    @property
    def name(self):
        return self._data.get("name")

    @property
    def redirect_uris(self):
        return self._data.get("redirect_uris", [])

    @property
    def grant_types(self):
        return self._data.get("grant_types", [])

    @property
    def response_types(self):
        return self._data.get("response_types", [])

    @property
    def scopes(self):
        return self._data.get("scopes", [])

    @property
    def created_at(self):
        return self._data.get("created_at")

    @property
    def revoked(self):
        return self._data.get("revoked", False)

    @classmethod
    def create(cls, client_id, client_secret, name, redirect_uris=None,
               grant_types=None, response_types=None, scopes=None):
        now = int(time.time())
        doc = {
            "client_id": client_id,
            "client_secret": client_secret,
            "name": name,
            "redirect_uris": redirect_uris or [],
            "grant_types": grant_types or [],
            "response_types": response_types or [],
            "scopes": scopes or [],
            "created_at": now,
            "revoked": False,
        }
        result = oauth_client_col.insert_one(doc)
        doc["_id"] = result.inserted_id
        return cls(doc)

    @classmethod
    def get_by_client_id(cls, client_id):
        doc = oauth_client_col.find_one({"client_id": client_id})
        return cls(doc) if doc else None

    @classmethod
    def list_all(cls):
        return [cls(d) for d in oauth_client_col.find().sort("created_at", 1)]

    @classmethod
    def update(cls, id, **kwargs):
        allowed = {"name", "redirect_uris", "grant_types",
                   "response_types", "scopes", "revoked"}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return None
        oid = ObjectId(id)
        oauth_client_col.update_one({"_id": oid}, {"$set": fields})
        return cls.get(id)

    @classmethod
    def delete(cls, id):
        try:
            oid = ObjectId(id)
        except Exception:
            return False
        res = oauth_client_col.delete_one({"_id": oid})
        return res.deleted_count == 1
