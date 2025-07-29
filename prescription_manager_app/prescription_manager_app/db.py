from pymongo import MongoClient

# Connect to MongoDB (adjust URI as needed)
client = MongoClient("mongodb://localhost:27017/")
db = client["prescription_manager_app"]

# Collection handles
user_col = db["user"]
medication_col = db["medication"]
oauth_client_col = db["oauth_client"]
oauth_code_col = db["oauth_code"]
oauth_token_col = db["oauth_token"]
appointment_col = db["appointment"]
prescription_col = db["prescription"]
facility_col = db["facility"]
