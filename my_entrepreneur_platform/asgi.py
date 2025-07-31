# my_entrepreneur_platform/my_entrepreneur_platform/asgi.py

import os

from django.urls import path # Import 'path' from django.urls.
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_entrepreneur_platform.settings')

django_asgi_app = get_asgi_application()

# Import the WebSocket routing maps from your apps
import chat.routing
import notifications.routing

# This is the main "traffic cop" for your application, directing different types of requests
application = ProtocolTypeRouter({
    "http": django_asgi_app, # Handle regular web page requests (HTTP)

    # Handle "instant message pipe" (WebSocket) connections
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                # Route WebSocket connections for chat
                path("ws/chat/", URLRouter(chat.routing.websocket_urlpatterns)),

                # Route WebSocket connections for notifications
                path("ws/notifications/", URLRouter(notifications.routing.websocket_urlpatterns)),
            ])
        )
    ),
})