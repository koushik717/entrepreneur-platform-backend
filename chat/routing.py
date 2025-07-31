# my_entrepreneur_platform/chat/routing.py

from django.urls import re_path

from . import consumers # This imports your chat bot

websocket_urlpatterns = [
    # This pattern only matches the part *after* "ws/chat/" from asgi.py
    re_path(r'(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]