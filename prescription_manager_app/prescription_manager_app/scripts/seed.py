# prescription_manager_app\prescription_manager_app\scripts\seed.py

import os
import sys
import random
from datetime import datetime, timedelta

# Optional: ensure project root on path if running as script
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from prescription_manager_app.db.connection import (
    user_col,
    medication_col,
    appointment_col,
    prescription_col,
    facility_col,
)

# NOTE: import from utils.auth (bcrypt-only)
from prescription_manager_app.utils.auth import hash_password_bcrypt


def seed_users():
    user_col.delete_many({})
    role_map = {"DOCTOR": 0, "PHARMACIST": 1, "PATIENT": 2, "ADMIN": 3}
    usernames = [
        ("alice", "PATIENT"), ("drbob", "DOCTOR"), ("charlie", "PHARMACIST"),
        ("admin1", "ADMIN"), ("eve", "PATIENT"), ("drzoe", "DOCTOR"),
        ("inactive_pat", "PATIENT"), ("pharmacist_joe", "PHARMACIST")
    ]
    docs = []
    now = datetime.utcnow()
    for name, role_name in usernames:
        docs.append({
            "username": name,
            "email": f"{name}@example.com",
            "password_hash": hash_password_bcrypt("test1234"),
            "role": role_map[role_name],
            "status": random.randint(0, 2),
            "created_at": now,
            "updated_at": now,
        })
    user_col.insert_many(docs)
    print("Seeded users")
    return list(user_col.find({}))


def seed_medications():
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
    now = datetime.utcnow()
    for generic, brand, chemical, price in meds:
        docs.append({
            "generic_name": generic,
            "brand_name": brand,
            "chemical_name": chemical,
            "price": round(price, 2),
            "status": 0,
            "created_at": now,
            "updated_at": now
        })
    medication_col.insert_many(docs)
    print("Seeded medications")
    return list(medication_col.find({}))


def seed_facilities():
    facility_col.delete_many({})
    entries = [
        ("Greenwood Clinic", "123 Health Rd", 0),
        ("City Pharmacy", "456 Medicine Ave", 1),
        ("Westside Health", "789 Clinic Blvd", 0),
        ("Main Street Pharmacy", "101 Rx St", 1),
        ("24hr Emergency Clinic", "202 Emergency Ln", 0),
    ]
    docs = []
    now = datetime.utcnow()
    for name, addr, type_code in entries:
        docs.append({
            "name": name,
            "address": addr,
            "type": type_code,
            "status": 0 if type_code == 0 else random.randint(0, 1),
            "created_at": now,
            "updated_at": now
        })
    facility_col.insert_many(docs)
    print("Seeded facility entries")
    return list(facility_col.find({}))


def seed_appointments(users, facilities):
    appointment_col.delete_many({})
    doctors = [u for u in users if u.get("role") == 0]
    patients = [u for u in users if u.get("role") == 2]
    surgeries = [f for f in facilities if f.get("type") == 0]
    docs = []
    now = datetime.utcnow()
    for _ in range(10):
        docs.append({
            "surgery_id": random.choice(surgeries)["_id"],
            "medical_professional_id": random.choice(doctors)["_id"],
            "patient_id": random.choice(patients)["_id"],
            "time": now + timedelta(days=random.randint(1, 30)),
            "status": random.randint(0, 3),
            "created_at": now,
            "updated_at": now
        })
    appointment_col.insert_many(docs)
    print("Seeded appointments")
    return list(appointment_col.find({}))


def seed_prescriptions(users, medications, facilities):
    prescription_col.delete_many({})
    doctors = [u for u in users if u.get("role") == 0]
    patients = [u for u in users if u.get("role") == 2]
    pharmacies = [f for f in facilities if f.get("type") == 1]
    docs = []
    now = datetime.utcnow()
    for _ in range(10):
        docs.append({
            "pharmacy_id": random.choice(pharmacies)["_id"],
            "medication_id": random.choice(medications)["_id"],
            "prescriber_id": random.choice(doctors)["_id"],
            "patient_id": random.choice(patients)["_id"],
            "medical_exemption_type": random.randint(0, 3),
            "status": random.randint(0, 3),
            "created_at": now,
            "updated_at": now
        })
    prescription_col.insert_many(docs)
    print("Seeded prescriptions")
    return list(prescription_col.find({}))


def run_all_seeders():
    users = seed_users()
    medications = seed_medications()
    facilities = seed_facilities()
    seed_appointments(users, facilities)
    seed_prescriptions(users, medications, facilities)
    print("✅ All seeders executed successfully.")


if __name__ == "__main__":
    run_all_seeders()
