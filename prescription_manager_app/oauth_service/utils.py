import secrets

def register_client(name, redirect_uri):
    client_id = secrets.token_urlsafe(16)
    client_secret = secrets.token_urlsafe(32)
    oauth_client_col.insert_one({
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "name": name
    })
    return client_id, client_secrets