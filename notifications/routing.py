# my_entrepreneur_platform/notifications/routing.py

from django.urls import re_path

from . import consumers # This will be our NotificationConsumer

websocket_urlpatterns = [
    # IMPORTANT: This pattern now only matches the part *after*
    # "ws/notifications/" from the asgi.py URLRouter.
    # It expects the user's ID to know who to send notifications to.
    # Example: If asgi.py passes "1/", this matches it.
    re_path(r'(?P<user_id>\d+)/$', consumers.NotificationConsumer.as_asgi()),
]