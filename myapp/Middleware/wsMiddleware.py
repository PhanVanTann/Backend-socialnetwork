# myapp/ws_jwt.py
import jwt
from types import SimpleNamespace
from urllib.parse import parse_qs
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from channels.middleware import BaseMiddleware

def _get_cookie(headers: dict, name: str) -> str | None:
    raw = headers.get(b"cookie")
    if not raw:
        return None
    try:
        cookie_str = raw.decode()
    except Exception:
        return None
    for part in cookie_str.split(";"):
        k, _, v = part.strip().partition("=")
        if k == name:
            return v
    return None

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        headers = dict(scope.get("headers", []))


        token = _get_cookie(headers, "access_token")

        if not token:
            scope["ws_auth_error"] = "token_missing"
            return await super().__call__(scope, receive, send)

        scope["user"] = AnonymousUser()
        scope["ws_auth_error"] = None

        if token:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                uid  = payload.get("user_id") or payload.get("sub")
                role = payload.get("role") or "user"
                if uid:
                    scope["user"] = SimpleNamespace(id=uid, role=role, is_anonymous=False)
            except jwt.ExpiredSignatureError:
                scope["ws_auth_error"] = "token_expired"
            except Exception:
                scope["ws_auth_error"] = "token_invalid"

        return await super().__call__(scope, receive, send)