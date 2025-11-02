import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import OriginValidator
from Middleware.wsMiddleware import JWTAuthMiddleware
import chat.routing
import notifications.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": OriginValidator(
        JWTAuthMiddleware(
            URLRouter(
                chat.routing.websocket_urlpatterns +
                notifications.routing.websocket_urlpatterns
            )
        ),
        allowed_origins=[
            "https://socialnetwork-su0z.onrender.com",
            "http://localhost:3000",
        ]
    ),
})