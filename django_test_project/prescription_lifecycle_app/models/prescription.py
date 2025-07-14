# prescription.py
from django.db import models
from .surgery_pharmacy import SurgeryPharmacy
from .medication import Medication
from .user import User

class Prescription(models.Model):
    pharmacy = models.ForeignKey(SurgeryPharmacy, on_delete=models.CASCADE, related_name='prescriptions')
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='prescriptions')
    prescriber = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='prescribed_prescriptions')
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_prescriptions')
    MEDICAL_EXEMPTION_CHOICES = [
        (0, 'None'),
        (1, 'Low Income'),
        (2, 'Pregnancy'),
        (3, 'Chronic Conditions'),
    ]
    medical_exemption_type = models.IntegerField(max_length=50, choices=MEDICAL_EXEMPTION_CHOICES, default='none')
    STATUS_CHOICES = [
        (0, 'New'),
        (1, 'Filled'),
        (2, 'Cancelled'),
        (3, 'Expired'),
    ]
    status = models.IntegerField(max_length=20, choices=STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Prescription #{self.id} for {self.patient}"
