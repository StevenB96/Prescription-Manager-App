from bson.objectid import ObjectId
from datetime import datetime
from prescription_lifecycle_app.db import appointment_col

class Appointment:
    """
    A PyMongo-backed wrapper for the 'appointment' collection.
    """
    STATUS_SCHEDULED = 0
    STATUS_COMPLETED = 1
    STATUS_CANCELLED = 2
    STATUS_NO_SHOW = 3

    STATUS_DISPLAY = {
        STATUS_SCHEDULED: "Scheduled",
        STATUS_COMPLETED: "Completed",
        STATUS_CANCELLED: "Cancelled",
        STATUS_NO_SHOW: "No Show",
    }

    STATUS_CHOICES = list(STATUS_DISPLAY.items())

    def __init__(self, data):
        self._data = data

    @property
    def id(self):
        return str(self._data.get("_id"))

    @property
    def surgery_id(self):
        return str(self._data.get("surgery_id"))

    @property
    def medical_professional_id(self):
        return str(self._data.get("medical_professional_id"))

    @property
    def patient_id(self):
        return str(self._data.get("patient_id"))

    @property
    def time(self):
        return self._data.get("time")

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
    def create(cls, surgery_id, medical_professional_id, patient_id, time, status=STATUS_SCHEDULED):
        now = datetime.utcnow()
        doc = {
            "surgery_id": ObjectId(surgery_id),
            "medical_professional_id": ObjectId(medical_professional_id) if medical_professional_id else None,
            "patient_id": ObjectId(patient_id),
            "time": time,
            "status": status,
            "created_at": now,
            "updated_at": now,
        }
        result = appointment_col.insert_one(doc)
        doc["_id"] = result.inserted_id
        return cls(doc)

    @classmethod
    def get(cls, id):
        try:
            oid = ObjectId(id)
        except Exception:
            return None
        doc = appointment_col.find_one({"_id": oid})
        return cls(doc) if doc else None

    @classmethod
    def list_all(cls):
        return [cls(d) for d in appointment_col.find().sort("time", 1)]

    @classmethod
    def update(cls, id, **kwargs):
        allowed = {"surgery_id", "medical_professional_id", "patient_id", "time", "status"}
        fields = {}
        for k, v in kwargs.items():
            if k in allowed:
                if k.endswith("_id") and v:
                    fields[k] = ObjectId(v)
                else:
                    fields[k] = v
        if not fields:
            return None
        fields["updated_at"] = datetime.utcnow()
        oid = ObjectId(id)
        appointment_col.update_one({"_id": oid}, {"$set": fields})
        return cls.get(id)

    @classmethod
    def delete(cls, id):
        try:
            oid = ObjectId(id)
        except Exception:
            return False
        res = appointment_col.delete_one({"_id": oid})
        return res.deleted_count == 1