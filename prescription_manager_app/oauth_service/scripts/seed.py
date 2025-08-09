# prescription_manager_app\oauth_service\scripts\seed.py

import os
import sys

# ── Project Root Setup ──
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from prescription_manager_app.oauth_service.db.connection import oauth_client_col


def seed_oauth_clients():
    """
    Seed the OAuth client collection with predefined web and mobile clients.
    Clears existing data before inserting.
    """
    oauth_client_col.delete_many({})

    clients = [
        {
            "client_id": "web-client",
            "client_secret": "supersecret",
            "redirect_uris": ["http://localhost:8000/callback"],
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
            "scope": "profile",
            "token_endpoint_auth_method": "client_secret_basic",
            "created_at": None,
            "updated_at": None,
        },
        {
            "client_id": "mobile-client",
            "client_secret": "mobilesecret",
            "redirect_uris": ["myapp://oauth-callback"],
            "grant_types": ["password", "refresh_token"],
            "response_types": ["token"],
            "scope": "profile email",
            "token_endpoint_auth_method": "client_secret_post",
            "created_at": None,
            "updated_at": None,
        },
    ]

    oauth_client_col.insert_many(clients)
    print("✅ Seeded OAuth clients successfully.")


if __name__ == "__main__":
    seed_oauth_clients()
    print("✅ All seeders executed successfully.")
