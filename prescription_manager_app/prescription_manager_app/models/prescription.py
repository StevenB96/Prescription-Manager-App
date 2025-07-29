from bson.objectid import ObjectId
from datetime import datetime
from prescription_manager_app.db import prescription_col

class Prescription:
    """
    A PyMongo-backed wrapper for the 'prescription' collection.
    """
    EXEMPTION_NONE = 0
    EXEMPTION_LOW_INCOME = 1
    EXEMPTION_PREGNANCY = 2
    EXEMPTION_CHRONIC = 3

    STATUS_NEW = 0
    STATUS_FILLED = 1
    STATUS_CANCELLED = 2
    STATUS_EXPIRED = 3

    EXEMPTION_DISPLAY = {
        EXEMPTION_NONE: "None",
        EXEMPTION_LOW_INCOME: "Low Income",
        EXEMPTION_PREGNANCY: "Pregnancy",
        EXEMPTION_CHRONIC: "Chronic Condition",
    }

    STATUS_DISPLAY = {
        STATUS_NEW: "New",
        STATUS_FILLED: "Filled",
        STATUS_CANCELLED: "Cancelled",
        STATUS_EXPIRED: "Expired",
    }

    EXEMPTION_CHOICES = list(EXEMPTION_DISPLAY.items())

    STATUS_CHOICES = list(STATUS_DISPLAY.items())

    def __init__(self, data):
        self._data = data

    @property
    def id(self):
        return str(self._data.get("_id"))

    @property
    def pharmacy_id(self):
        return str(self._data.get("pharmacy_id"))

    @property
    def medication_id(self):
        return str(self._data.get("medication_id"))

    @property
    def prescriber_id(self):
        return str(self._data.get("prescriber_id")) if self._data.get("prescriber_id") else None

    @property
    def patient_id(self):
        return str(self._data.get("patient_id"))

    @property
    def medical_exemption_type(self):
        return self._data.get("medical_exemption_type")

    @property
    def status(self):
        return self._data.get("status")

    @property
    def created_at(self):
        return self._data.get("created_at")

    @property
    def updated_at(self):
        return self._data.get("updated_at")
    
    def get_exemption_display(self):
        return self.EXEMPTION_DISPLAY.get(self.medical_exemption_type, "Unknown")

    def get_status_display(self):
        return self.STATUS_DISPLAY.get(self.status, "Unknown")

    @classmethod
    def create(cls, pharmacy_id, medication_id, prescriber_id, patient_id, medical_exemption_type=EXEMPTION_NONE, status=STATUS_NEW):
        now = datetime.utcnow()
        doc = {
            "pharmacy_id": ObjectId(pharmacy_id),
            "medication_id": ObjectId(medication_id),
            "prescriber_id": ObjectId(prescriber_id) if prescriber_id else None,
            "patient_id": ObjectId(patient_id),
            "medical_exemption_type": medical_exemption_type,
            "status": status,
            "created_at": now,
            "updated_at": now,
        }
        result = prescription_col.insert_one(doc)
        doc["_id"] = result.inserted_id
        return cls(doc)

    @classmethod
    def get(cls, id):
        try:
            oid = ObjectId(id)
        except Exception:
            return None
        doc = prescription_col.find_one({"_id": oid})
        return cls(doc) if doc else None

    @classmethod
    def list_all(cls):
        return [cls(d) for d in prescription_col.find().sort("created_at", 1)]

    @classmethod
    def update(cls, id, **kwargs):
        allowed = {"pharmacy_id", "medication_id", "prescriber_id", "patient_id", "medical_exemption_type", "status"}
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
        prescription_col.update_one({"_id": oid}, {"$set": fields})
        return cls.get(id)

    @classmethod
    def delete(cls, id):
        try:
            oid = ObjectId(id)
        except Exception:
            return False
        res = prescription_col.delete_one({"_id": oid})
        return res.deleted_count == 1
