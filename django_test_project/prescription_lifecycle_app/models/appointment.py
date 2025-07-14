# appointment.py
from django.db import models
from .surgery_pharmacy import SurgeryPharmacy
from .user import User

class Appointment(models.Model):
    surgery = models.ForeignKey(SurgeryPharmacy, on_delete=models.CASCADE, related_name='appointments')
    medical_professional = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='appointments_as_professional')
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_patient')
    time = models.DateTimeField()
    STATUS_CHOICES = [
        (0, 'Scheduled'),
        (1, 'Completed'),
        (2, 'Cancelled'),
        (3, 'No Show'),
    ]
    status = models.IntegerField(max_length=20, choices=STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Appointment #{self.id} on {self.time.strftime('%Y-%m-%d %H:%M')}"
