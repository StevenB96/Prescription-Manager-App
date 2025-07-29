from bson.objectid import ObjectId
from datetime import datetime

from prescription_manager_app.db import user_col

class User:
    """
    A PyMongo‑backed wrapper for the 'users' collection.
    """
    ROLE_DOCTOR = 0
    ROLE_PHARMACIST = 1
    ROLE_PATIENT = 2
    ROLE_ADMIN = 3

    STATUS_ACTIVE   = 0
    STATUS_INACTIVE = 1

    # Display mappings
    ROLE_DISPLAY = {
        ROLE_DOCTOR: 'Doctor',
        ROLE_PHARMACIST: 'Pharmacist',
        ROLE_PATIENT: 'Patient',
        ROLE_ADMIN: 'Admin',
    }

    STATUS_DISPLAY = {
        STATUS_ACTIVE: 'Active',
        STATUS_INACTIVE: 'Inactive',
    }

    ROLE_CHOICES = list(ROLE_DISPLAY.items())

    STATUS_CHOICES = list(STATUS_DISPLAY.items())

    def __init__(self, data):
        self._data = data

    @property
    def id(self):
        return str(self._data["_id"])

    @property
    def username(self):
        return self._data.get("username")

    @property
    def email(self):
        return self._data.get("email")

    @property
    def password_hash(self):
        return self._data.get("password_hash")

    @property
    def role(self):
        return self._data.get("role")

    @property
    def status(self):
        return self._data.get("status")

    @property
    def created_at(self):
        return self._data.get("created_at")

    @property
    def updated_at(self):
        return self._data.get("updated_at")

    def get_role_display(self):
        return self.ROLE_DISPLAY.get(self.role, 'Unknown')

    def get_status_display(self):
        return self.STATUS_DISPLAY.get(self.status, 'Unknown')

    @classmethod
    def create(cls, username, email, password_hash, role, status=STATUS_ACTIVE):
        now = datetime.utcnow()
        doc = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "role": role,
            "status": status,
            "created_at": now,
            "updated_at": now,
        }
        result = user_col.insert_one(doc)
        doc["_id"] = result.inserted_id
        return cls(doc)

    @classmethod
    def get(cls, id):
        try:
            oid = ObjectId(id)
        except Exception:
            return None
        doc = user_col.find_one({"_id": oid})
        return cls(doc) if doc else None

    @classmethod
    def get_by_username(cls, username):
        doc = user_col.find_one({"username": username})
        return cls(doc) if doc else None

    @classmethod
    def list_all(cls):
        return [cls(d) for d in user_col.find().sort("created_at", 1)]

    @classmethod
    def update(cls, id, **kwargs):
        allowed = {"username", "email", "password_hash", "role", "status"}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return None
        fields["updated_at"] = datetime.utcnow()
        oid = ObjectId(id)
        user_col.update_one({"_id": oid}, {"$set": fields})
        return cls.get(id)

    @classmethod
    def delete(cls, id):
        try:
            oid = ObjectId(id)
        except Exception:
            return False
        res = user_col.delete_one({"_id": oid})
        return res.deleted_count == 1
