# surgery_pharmacy.py
from django.db import models

class SurgeryPharmacy(models.Model):
    TYPE_CHOICES = [
        (0, 'Surgery'),
        (1, 'Pharmacy'),
    ]
    name = models.CharField(max_length=255)
    address = models.TextField()
    type = models.IntegerField(max_length=20, choices=TYPE_CHOICES)
    STATUS_CHOICES = [
        (0, 'Active'),
        (1, 'Inactive'),
    ]
    status = models.IntegerField(max_length=20, choices=STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
