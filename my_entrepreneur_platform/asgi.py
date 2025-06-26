# my_entrepreneur_platform/my_entrepreneur_platform/asgi.py

import os

# Import 'path' from django.urls. Note: 'include' is NOT used here.
from django.urls import path 

# These imports are from the 'channels' library for real-time functionality
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

# This is for Django's regular web application handling
from django.core.asgi import get_asgi_application

# Set up Django's settings for this application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_entrepreneur_platform.settings')

# Get Django's regular web application handler (for normal HTTP requests like loading pages)
django_asgi_app = get_asgi_application()

# Import the WebSocket routing maps from your apps
import chat.routing
import notifications.routing

# This is the main "traffic cop" for your application, directing different types of requests
application = ProtocolTypeRouter({
    # Handle regular web page requests (HTTP)
    "http": django_asgi_app,

    # Handle "instant message pipe" (WebSocket) connections
    "websocket": AllowedHostsOriginValidator( # Layer for basic security (allowed origins)
        AuthMiddlewareStack( # Layer to identify the logged-in user for WebSockets
            URLRouter([
                # Route WebSocket connections starting with 'ws/chat/' to the chat app's routing.
                # IMPORTANT: Use URLRouter() here for nested WebSocket patterns, NOT include().
                path("ws/chat/", URLRouter(chat.routing.websocket_urlpatterns)), 

                # Route WebSocket connections starting with 'ws/notifications/' to the notifications app's routing.
                # IMPORTANT: Use URLRouter() here for nested WebSocket patterns, NOT include().
                path("ws/notifications/", URLRouter(notifications.routing.websocket_urlpatterns)),
            ])
        )
    ),
})