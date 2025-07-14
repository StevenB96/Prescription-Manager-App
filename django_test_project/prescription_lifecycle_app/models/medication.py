# medication.py
from django.db import models

class Medication(models.Model):
    generic_name = models.CharField(max_length=255)
    brand_name = models.CharField(max_length=255, blank=True, null=True)
    chemical_name = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    STATUS_CHOICES = [
        (0, 'Active'),
        (1, 'Inactive'),
    ]
    status = models.IntegerField(max_length=20, choices=STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.generic_name