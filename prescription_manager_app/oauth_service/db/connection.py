# prescription_manager_app\oauth_service\db\connection.py

from pymongo import MongoClient

# Connect to MongoDB (adjust URI as needed)
client = MongoClient("mongodb://localhost:27017/")
db = client["prescription_manager_app"]

# Collection handles
oauth_client_col = db["oauth_client"]
oauth_code_col = db["oauth_code"]
oauth_token_col = db["oauth_token"]
user_col = db["user"]
