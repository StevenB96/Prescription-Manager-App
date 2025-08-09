# prescription_manager_app\prescription_manager_app\models\medication.py

from bson.objectid import ObjectId
from datetime import datetime
from prescription_manager_app.db.connection import medication_col

class Medication:
    """
    A PyMongo‑backed wrapper for the 'medications' collection.
    """
    STATUS_ACTIVE   = 0
    STATUS_INACTIVE = 1

    STATUS_DISPLAY = {
        STATUS_ACTIVE: "Active",
        STATUS_INACTIVE: "Inactive",
    }

    STATUS_CHOICES = list(STATUS_DISPLAY.items())

    def __init__(self, data):
        self._data = data

    @property
    def id(self):
        return str(self._data["_id"])

    @property
    def generic_name(self):
        return self._data["generic_name"]

    @property
    def brand_name(self):
        return self._data.get("brand_name")

    @property
    def chemical_name(self):
        return self._data.get("chemical_name")

    @property
    def price(self):
        return self._data.get("price", 0)

    @property
    def status(self):
        return self._data.get("status")

    @property
    def created_at(self):
        return self._data.get("created_at")

    @property
    def updated_at(self):
        return self._data.get("updated_at")
    
    def get_status_display(self):
        return self.STATUS_DISPLAY.get(self.status, "Unknown")

    @classmethod
    def create(cls, generic_name, brand_name=None, chemical_name=None,
               price=0, status=STATUS_ACTIVE):
        now = datetime.utcnow()
        doc = {
            "generic_name": generic_name,
            "brand_name": brand_name,
            "chemical_name": chemical_name,
            "price": price,
            "status": status,
            "created_at": now,
            "updated_at": now,
        }
        res = medication_col.insert_one(doc)
        doc["_id"] = res.inserted_id
        return cls(doc)

    @classmethod
    def get(cls, id):
        try:
            oid = ObjectId(id)
        except Exception:
            return None
        doc = medication_col.find_one({"_id": oid})
        return cls(doc) if doc else None

    @classmethod
    def list_all(cls):
        return [cls(d) for d in medication_col.find().sort("created_at", 1)]

    @classmethod
    def update(cls, id, **kwargs):
        allowed = {"generic_name", "brand_name", "chemical_name", "price", "status"}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return None
        fields["updated_at"] = datetime.utcnow()
        oid = ObjectId(id)
        medication_col.update_one({"_id": oid}, {"$set": fields})
        return cls.get(id)

    @classmethod
    def delete(cls, id):
        try:
            oid = ObjectId(id)
        except Exception:
            return False
        res = medication_col.delete_one({"_id": oid})
        return res.deleted_count == 1
