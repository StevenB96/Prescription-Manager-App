from datetime import datetime, timedelta
from bson.objectid import ObjectId

from prescription_lifecycle_app.db import oauth_client_col, oauth_code_col, oauth_token_col
from authlib.oauth2.rfc6749 import grants

# — Client lookup —
def query_client(client_id):
    doc = oauth_client_col.find_one({"client_id": client_id})
    if not doc:
        return None
    return type("Client", (), {
        "client_id": doc["client_id"],
        "client_secret": doc["client_secret"],
        "redirect_uris": doc["redirect_uris"],
        "grant_types": doc["grant_types"],
        "response_types": doc["response_types"],
        "scope": doc["scope"],
        "token_endpoint_auth_method": doc["token_endpoint_auth_method"],
    })()

# — Auth code — 
def save_authorization_code(client, code_data, request):
    expires = datetime.utcnow() + timedelta(minutes=10)
    oauth_code_col.insert_one({
        "code": code_data["code"],
        "client_id": client.client_id,
        "redirect_uri": request.redirect_uri,
        "scope": request.scope,
        "user_id": request.user.id,
        "expires_at": expires,
    })

def query_authorization_code(code, client):
    doc = oauth_code_col.find_one({
        "code":      code,
        "client_id": client.client_id
    })
    if not doc or doc["expires_at"] < datetime.utcnow():
        return None
    return type("AuthCode", (), doc)

def delete_authorization_code(code_obj):
    oauth_code_col.delete_one({"code": code_obj.code})

# — Token saving —
def save_token(token_data, request):
    expires = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
    oauth_token_col.insert_one({
        "access_token": token_data["access_token"],
        "refresh_token": token_data.get("refresh_token"),
        "client_id": request.client.client_id,
        "user_id": getattr(request.user, "id", None),
        "scope": token_data["scope"],
        "expires_at": expires,
    })

# — Grant classes —
class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    def save_authorization_code(self, code, request):
        save_authorization_code(request.client, code, request)
    def query_authorization_code(self, code, client):
        return query_authorization_code(code, client)
    def delete_authorization_code(self, code):
        delete_authorization_code(code)

class ClientCredentialsGrant(grants.ClientCredentialsGrant):
    def save_token(self, token_data, request):
        save_token(token_data, request)
