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
                "redirect_uris": [
                    "http://localhost:8000/admin",
                    "http://localhost:8000/oauth",
                    "http://localhost:8000/oauth/manage-apps"
                ],

                # The grant types this client is allowed to use.
                # Common options include:
                # - "authorization_code": Standard web app flow where the client exchanges a code for a token.
                # - "refresh_token": Allows obtaining new access tokens without user interaction.
                # - "client_credentials": For server-to-server authentication without user involvement.
                # - "password" (Resource Owner Password Credentials): Directly uses user credentials (less secure, not recommended).
                "grant_types": [
                    "authorization_code",
                    "refresh_token",
                ],

                # The types of responses the client expects from the authorization server.
                # Common options include:
                # - "code": Authorization code flow (most secure for web apps).
                # - "token": Implicit flow, where the access token is returned directly (used in SPA / front-end apps; less secure).
                # - "id_token": For OpenID Connect, returns an ID token containing user identity information.
                # - "code id_token": Hybrid flow combining code and id_token for immediate identity and token.
                "response_types": [
                    "code",
                ],

                # The scopes that the client can request access to.
                # Scopes define what resources or permissions the client is allowed to access.
                # Common scopes include:
                # - "profile": Basic user information such as name, username, and email.
                # - "email": Access to the user's email address.
                # - "openid": Required for OpenID Connect to request identity tokens.
                # - "offline_access": Allows requesting refresh tokens.
                # - "read", "write", "admin", "user": Custom scopes for API-specific permissions.
                "scopes": [
                    "facility",
                    "user",
                    "medication",
                    "prescription",
                    "appointment",
                ],

                # Authentication method the client uses at the token endpoint.
                # This determines how the client proves its identity when requesting tokens.
                # Common options include:
                # - "client_secret_basic": Client sends client_id and client_secret in the HTTP Authorization header (most common).
                # - "client_secret_post": Client sends client_id and client_secret in the POST body.
                # - "client_secret_jwt": Client signs a JWT with its secret and sends it for authentication.
                # - "private_key_jwt": Client signs a JWT using a private key (more secure, used in confidential clients).
                # - "none": Public clients that cannot keep a secret (used for SPAs or mobile apps with PKCE).
                # alternatives: client_secret_post, client_secret_jwt, private_key_jwt, none
                "token_endpoint_auth_methods": [
                    "client_secret_basic",
                ],

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
