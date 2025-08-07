from pymongo import MongoClient

# Connect to MongoDB (adjust URI as needed)
client = MongoClient("mongodb://localhost:27017/")
db = client["prescription_manager_app"]

# Collection handles
user_col = db["user"]
medication_col = db["medication"]
appointment_col = db["appointment"]
prescription_col = db["prescription"]
facility_col = db["facility"]
