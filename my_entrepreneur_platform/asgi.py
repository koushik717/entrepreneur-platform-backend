# my_entrepreneur_platform/my_entrepreneur_platform/asgi.py

import os

# Re-add these imports
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator # Keep this for security
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_entrepreneur_platform.settings')

django_asgi_app = get_asgi_application()

import chat.routing # This should already be uncommented

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # Re-introduce AllowedHostsOriginValidator and AuthMiddlewareStack
    "websocket": AllowedHostsOriginValidator( # Re-add this
        AuthMiddlewareStack( # <--- Re-add this
            URLRouter(chat.routing.websocket_urlpatterns)
        )
    ),
})