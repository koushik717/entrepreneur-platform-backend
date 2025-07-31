# my_entrepreneur_platform/notifications/routing.py

from django.urls import re_path

from . import consumers # This will be our NotificationConsumer

websocket_urlpatterns = [
    # This pattern only matches the part *after* "ws/notifications/" from asgi.py
    re_path(r'(?P<user_id>\d+)/$', consumers.NotificationConsumer.as_asgi()),
]