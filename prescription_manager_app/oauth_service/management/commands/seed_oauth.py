# oauth_service/management/commands/seed_oauth.py
from django.core.management.base import BaseCommand
from django.conf import settings
from oauth_service.models import OAuthClient


class Command(BaseCommand):
    help = "Seed OAuth clients into MongoDB using the OAuthClient model"

    def handle(self, *args, **options):
        # --- Clear existing OAuth clients ---
        # Use the model's list_all and delete methods to remove any existing clients.
        # This ensures that we start with a clean slate.
        for client in OAuthClient.list_all():
            OAuthClient.delete(client.id)

        # --- Create internal OAuth client ---
        # We use the OAuthClient model to create a client in a consistent way.
        # All timestamps and data structure are handled by the model.
        client = OAuthClient.create(
            client_id=settings.INTERNAL_OAUTH_CLIENT_ID,  # Unique identifier for the client
            # Secret key for authentication
            client_secret=settings.INTERNAL_OAUTH_CLIENT_SECRET,
            name="Internal App",  # Human-readable name for the client
            redirect_uris=[  # List of allowed redirect URIs
                "http://localhost:8000/admin",
                "http://localhost:8000/oauth",
                "http://localhost:8000/oauth/manage-apps"
            ],
            grant_types=[  # Grant types this client is allowed to use
                "authorization_code",  # Standard web app flow
                "refresh_token",       # Allows obtaining new access tokens without user interaction
            ],
            response_types=[  # Expected response types from the authorization server
                "code",  # Authorization code flow
            ],
            scopes=[  # Scopes the client can request
                "facility",
                "medication",
                "prescription",
                "appointment",
            ],
        )

        # --- Success message ---
        # Print a message to the console with client info
        self.stdout.write(self.style.SUCCESS(
            f"✅ OAuth client '{client.name}' seeded successfully with client_id '{client.client_id}'"
        ))
