# import os
# from django.core.asgi import get_asgi_application
# import django
# from channels.routing import ProtocolTypeRouter, URLRouter

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
# django.setup()
# from Middleware.wsMiddleware import JWTAuthMiddleware
# import chat.routing
# import notifications.routing

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": JWTAuthMiddleware(
#         URLRouter(
#             chat.routing.websocket_urlpatterns +
#             notifications.routing.websocket_urlpatterns
#         )
#     ),
# })
import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
django.setup()
from channels.security.websocket import OriginValidator
from Middleware.wsMiddleware import JWTAuthMiddleware
import chat.routing
import notifications.routing



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