import jwt
from jwt.exceptions import (
    InvalidSignatureError,
    ExpiredSignatureError,
    DecodeError,
    InvalidTokenError
)
from datetime import datetime, timedelta
from django.conf import settings
from django.http import HttpResponse

def create_email_token(email):
    try:
        payload = {
            "email": email,
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "purpose": "email_verification"
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    except Exception as e:
        print(f"Error creating JWT token: {e}")
        return None
    
def decode_token(token: str):
    try:
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return decoded

    except ExpiredSignatureError:
        return {"error": "expired_token"}

    except InvalidSignatureError:
        return {"error": "invalid_signature"}

    except DecodeError:
        return {"error": "decode_error"}

    except InvalidTokenError:
        return {"error": "invalid_token"}

    except Exception as e:
        return {"error": "unknown_error"}
    
def decode_token_notime(token: str):
    try:
        decoded = jwt.decode(token,settings.SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False})
        return decoded
    except ExpiredSignatureError:
        return {"error": "expired"}
    except Exception as e:
        return {"error": "unknown_error"}
    
def create_access_token(user_id,role):
    payload = {
        "user_id": user_id,  
        "role":role,
        "exp": datetime.utcnow() + timedelta(hours=2), 
        "purpose": "user_authentication" 
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

def create_refresh_token(user_id,role):
    payload = {
        "user_id": user_id,  
        "role":role,
        "exp": datetime.utcnow() + timedelta(days=7), 
        "purpose": "refresh_token",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

def create_cookie(access_token,refresh_token):
    response = HttpResponse()
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=False, 
        samesite=None,
        #domain=None,
        max_age=2*24*3600
            )
    response.set_cookie(
        key='access_token',
        value=access_token,
        secure=False,  # tạm để False nếu đang test local
        samesite="Lax",
        httponly=True,      
        #secure=True,       
        #samesite=None,  
        #domain=None,
        max_age=60*60     
        ) 
    return response