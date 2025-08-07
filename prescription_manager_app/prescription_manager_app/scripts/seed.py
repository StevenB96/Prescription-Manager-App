#!/usr/bin/env python
import os
import sys
import random
from datetime import datetime, timedelta
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.utils.crypto import get_random_string
from bson.objectid import ObjectId

# ── Project Root Setup ──
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ── DB Collections ──
from prescription_manager_app.db.connection import (
    user_col,
    medication_col,
    oauth_client_col,
    appointment_col,
    prescription_col,
    facility_col,
)

# ── Utilities ──
hasher = PBKDF2PasswordHasher()

def hash_password(raw_password: str) -> str:
    """
    Hash passwords using Django's PBKDF2 algorithm.
    """
    salt = get_random_string(12)
    return hasher.encode(raw_password, salt)

# ── Seeder Functions ──

def seed_users():
    """Seed the user collection with diverse roles and statuses."""
    user_col.delete_many({})
    role_map = {"DOCTOR": 0, "PHARMACIST": 1, "PATIENT": 2, "ADMIN": 3}
    usernames = [
        ("alice", "PATIENT"), ("drbob", "DOCTOR"), ("charlie", "PHARMACIST"),
        ("admin1", "ADMIN"), ("eve", "PATIENT"), ("drzoe", "DOCTOR"),
        ("inactive_pat", "PATIENT"), ("pharmacist_joe", "PHARMACIST")
    ]
    users = []
    for name, role_name in usernames:
        users.append({
            "username": name,
            "email": f"{name}@example.com",
            "password_hash": hash_password("test1234"),
            "role": role_map[role_name],
            "status": random.randint(0, 2),
            "created_at": datetime.utcnow() - timedelta(days=random.randint(0, 365)),
            "updated_at": datetime.utcnow(),
        })
    user_col.insert_many(users)
    print("Seeded users")
    return list(user_col.find({}))


def seed_medications():
    """Seed the medication collection with common drugs."""
    medication_col.delete_many({})
    meds = [
        ("aspirin", "Bayer", "acetylsalicylic acid", 3.99),
        ("metformin", None, "metformin hydrochloride", 0.10),
        ("lisinopril", "Zestril", "lisinopril dihydrate", 0.25),
        ("ibuprofen", "Advil", "ibuprofen", 2.99),
        ("amoxicillin", "Moxatag", "amoxicillin trihydrate", 1.20),
        ("atorvastatin", "Lipitor", "atorvastatin calcium", 0.35),
        ("omeprazole", "Prilosec", "omeprazole", 0.50),
    ]
    docs = []
    for generic, brand, chemical, price in meds:
        docs.append({
            "generic_name": generic,
            "brand_name": brand,
            "chemical_name": chemical,
            "price": round(price, 2),
            "status": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
    medication_col.insert_many(docs)
    print("Seeded medications")
    return list(medication_col.find({}))


# def seed_oauth_clients():
#     """Seed the OAuth client collection with web and mobile clients."""
#     oauth_client_col.delete_many({})
#     clients = [
#         {
#             "client_id": "web-client",
#             "client_secret": "supersecret",
#             "redirect_uris": ["http://localhost:8000/callback"],
#             "grant_types": ["authorization_code", "refresh_token"],
#             "response_types": ["code"],
#             "scope": "profile",
#             "token_endpoint_auth_method": "client_secret_basic",
#         },
#         {
#             "client_id": "mobile-client",
#             "client_secret": "mobilesecret",
#             "redirect_uris": ["myapp://oauth-callback"],
#             "grant_types": ["password", "refresh_token"],
#             "response_types": ["token"],
#             "scope": "profile email",
#             "token_endpoint_auth_method": "client_secret_post",
#         }
#     ]
#     oauth_client_col.insert_many(clients)
#     print("Seeded OAuth clients")


def seed_facilities():
    """Seed surgeries and pharmacies into a unified collection."""
    facility_col.delete_many({})
    entries = [
        ("Greenwood Clinic", "123 Health Rd", 0),
        ("City Pharmacy", "456 Medicine Ave", 1),
        ("Westside Health", "789 Clinic Blvd", 0),
        ("Main Street Pharmacy", "101 Rx St", 1),
        ("24hr Emergency Clinic", "202 Emergency Ln", 0),
    ]
    docs = []
    for name, addr, type_code in entries:
        docs.append({
            "name": name,
            "address": addr,
            "type": type_code,
            "status": 0 if type_code == 0 else random.randint(0, 1),
            "created_at": datetime.utcnow() - timedelta(days=random.randint(0, 100)),
            "updated_at": datetime.utcnow()
        })
    facility_col.insert_many(docs)
    print("Seeded facility entries")
    return list(facility_col.find({}))


def seed_appointments(users, facilities):
    """Seed appointments with valid doctor, patient, and surgery IDs."""
    appointment_col.delete_many({})
    doctors = [u for u in users if u["role"] == 0]
    patients = [u for u in users if u["role"] == 2]
    surgeries = [f for f in facilities if f["type"] == 0]
    docs = []
    for _ in range(10):
        docs.append({
            "surgery_id": random.choice(surgeries)["_id"],
            "medical_professional_id": random.choice(doctors)["_id"],
            "patient_id": random.choice(patients)["_id"],
            "time": datetime.utcnow() + timedelta(days=random.randint(1, 30)),
            "status": random.randint(0, 3),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
    appointment_col.insert_many(docs)
    print("Seeded appointments")
    return list(appointment_col.find({}))


def seed_prescriptions(users, medications, facilities):
    """Seed prescriptions with links to pharmacies, medications, doctors, and patients."""
    prescription_col.delete_many({})
    doctors = [u for u in users if u["role"] == 0]
    patients = [u for u in users if u["role"] == 2]
    pharmacies = [f for f in facilities if f["type"] == 1]
    docs = []
    for _ in range(10):
        docs.append({
            "pharmacy_id": random.choice(pharmacies)["_id"],
            "medication_id": random.choice(medications)["_id"],
            "prescriber_id": random.choice(doctors)["_id"],
            "patient_id": random.choice(patients)["_id"],
            "medical_exemption_type": random.randint(0, 3),
            "status": random.randint(0, 3),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
    prescription_col.insert_many(docs)
    print("Seeded prescriptions")
    return list(prescription_col.find({}))

if __name__ == "__main__":
    users = seed_users()
    medications = seed_medications()
    # seed_oauth_clients()
    facilities = seed_facilities()
    seed_appointments(users, facilities)
    seed_prescriptions(users, medications, facilities)
    print("✅ All seeders executed successfully.")
