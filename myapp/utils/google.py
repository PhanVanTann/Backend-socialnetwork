from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from google.auth.exceptions import GoogleAuthError

def decode_token_gg(token: str):
    try:
        print(settings.GOOGLE_CLIENT_ID)
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        return idinfo
    except ValueError as ve:
        return {"error": f"Invalid token: {ve}"}
    except GoogleAuthError as ge:
        return {"error": f"Google auth error: {ge}"} 