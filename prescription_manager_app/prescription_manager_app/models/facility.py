# prescription_manager_app\prescription_manager_app\models\facility.py

from bson.objectid import ObjectId
from datetime import datetime

from prescription_manager_app.db.connection import facility_col

class Facility:
    """
    A PyMongo-backed wrapper for the 'facility' collection.
    """
    TYPE_SURGERY = 0
    TYPE_PHARMACY = 1

    STATUS_ACTIVE = 0
    STATUS_INACTIVE = 1

    TYPE_DISPLAY = {
        TYPE_SURGERY: "Surgery",
        TYPE_PHARMACY: "Pharmacy",
    }

    STATUS_DISPLAY = {
        STATUS_ACTIVE: "Active",
        STATUS_INACTIVE: "Inactive",
    }

    TYPE_CHOICES = list(TYPE_DISPLAY.items())

    STATUS_CHOICES = list(STATUS_DISPLAY.items())

    def __init__(self, data):
        self._data = data

    @property
    def id(self):
        return str(self._data.get("_id"))

    @property
    def name(self):
        return self._data.get("name")

    @property
    def address(self):
        return self._data.get("address")

    @property
    def type(self):
        return self._data.get("type")

    @property
    def status(self):
        return self._data.get("status")

    @property
    def created_at(self):
        return self._data.get("created_at")

    @property
    def updated_at(self):
        return self._data.get("updated_at")
    
    def get_type_display(self):
        return self.TYPE_DISPLAY.get(self.type, "Unknown")

    def get_status_display(self):
        return self.STATUS_DISPLAY.get(self.status, "Unknown")

    @classmethod
    def create(cls, name, address, type, status=STATUS_ACTIVE):
        now = datetime.utcnow()
        doc = {
            "name": name,
            "address": address,
            "type": type,
            "status": status,
            "created_at": now,
            "updated_at": now,
        }
        result = facility_col.insert_one(doc)
        doc["_id"] = result.inserted_id
        return cls(doc)

    @classmethod
    def get(cls, id):
        try:
            oid = ObjectId(id)
        except Exception:
            return None
        doc = facility_col.find_one({"_id": oid})
        return cls(doc) if doc else None

    @classmethod
    def list_all(cls):
        return [cls(d) for d in facility_col.find().sort("created_at", 1)]

    @classmethod
    def update(cls, id, **kwargs):
        allowed = {"name", "address", "type", "status"}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return None
        fields["updated_at"] = datetime.utcnow()
        oid = ObjectId(id)
        facility_col.update_one({"_id": oid}, {"$set": fields})
        return cls.get(id)

    @classmethod
    def delete(cls, id):
        try:
            oid = ObjectId(id)
        except Exception:
            return False
        res = facility_col.delete_one({"_id": oid})
        return res.deleted_count == 1