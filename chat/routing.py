# my_entrepreneur_platform/chat/routing.py

from django.urls import re_path

from . import consumers # This imports your chat bot

websocket_urlpatterns = [
    # This matches the WebSocket URL from your test_chat_client.html
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]