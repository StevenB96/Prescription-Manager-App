# oauth_service/management/commands/seed_oauth.py
from django.core.management.base import BaseCommand
from oauth_service.db.connection import oauth_client_col
from django.conf import settings
from datetime import datetime


class Command(BaseCommand):
    help = "Seed OAuth clients into MongoDB"

    def handle(self, *args, **options):
        # Clear existing data
        oauth_client_col.delete_many({})

        clients = [
            {
                # The unique identifier for the OAuth client.
                # Used by the OAuth server to recognize which client is making requests.
                "client_id": settings.INTERNAL_OAUTH_CLIENT_ID,

                # The secret key for the OAuth client.
                # Used together with the client_id to authenticate the client when exchanging authorization codes for tokens.
                "client_secret": settings.INTERNAL_OAUTH_CLIENT_SECRET,

                # List of allowed redirect URIs.
                # After successful authorization, the user is redirected to one of these URLs.
                # Ensures that tokens are only sent to trusted locations.
                "redirect_uris": ["http://localhost:8000/callback"],

                # The grant types this client is allowed to use.
                # "authorization_code" is used for standard web app flows.
                # "refresh_token" allows the client to obtain new access tokens without user interaction.
                "grant_types": ["authorization_code", "refresh_token"],

                # The types of responses the client expects from the authorization server.
                # "code" corresponds to the authorization code flow.
                "response_types": ["code"],

                # The scopes that the client can request access to.
                # "profile" typically includes basic user information like name and email.
                "scope": "profile",

                # Authentication method the client uses at the token endpoint.
                # "client_secret_basic" means the client sends client_id and client_secret in the Authorization header.
                "token_endpoint_auth_method": "client_secret_basic",

                # Timestamp for when the client was created.
                # Useful for auditing and record keeping.
                "created_at": datetime.utcnow(),

                # Timestamp for when the client was last updated.
                # Useful to track configuration changes.
                "updated_at": datetime.utcnow(),
            },
        ]

        oauth_client_col.insert_many(clients)
        self.stdout.write(self.style.SUCCESS(
            "✅ OAuth clients seeded successfully"))
