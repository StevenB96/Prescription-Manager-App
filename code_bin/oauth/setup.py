# from authlib.integrations.django_oauth2 import AuthorizationServer, ResourceProtector

# from .storage import (
#     query_client,
#     save_token,
#     AuthorizationCodeGrant,
#     ClientCredentialsGrant
# )

# authorization = AuthorizationServer()
# require_oauth   = ResourceProtector()

# def config_oauth():
#     """
#     Configure OAuth2 server and register grant handlers.
#     """
#     authorization.init_app(
#         query_client=query_client,
#         save_token=save_token
#     )
#     authorization.register_grant(AuthorizationCodeGrant)
#     authorization.register_grant(ClientCredentialsGrant)

# # Initialize immediately
# config_oauth()
