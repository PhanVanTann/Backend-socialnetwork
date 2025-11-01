import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from Middleware.wsMiddleware import JWTAuthMiddleware
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
import chat.routing
import notifications.routing
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(
            chat.routing.websocket_urlpatterns +
            notifications.routing.websocket_urlpatterns
        )
    ),
})