# user.py
from django.db import models

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=128)
    ROLE_CHOICES = [
        (0, 'Doctor'),
        (1, 'Pharmacist'),
        (2, 'Patient'),
        (3, 'Administrator'),
    ]
    role = models.IntegerField(max_length=20, choices=ROLE_CHOICES)
    STATUS_CHOICES = [
        (0, 'Active'),
        (1, 'Inactive'),
    ]
    status = models.IntegerField(max_length=20, choices=STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username