# my_entrepreneur_platform/my_entrepreneur_platform/urls.py

from django.contrib import admin
from django.urls import path, include

# Import views from your chat application
from chat.views import chat_test_view, ChatRoomListCreateAPIView, ChatRoomDetailAPIView, MessageListAPIView, MessageCreateAPIView

# Import views from your notifications application
from notifications.views import notification_test_view # <--- IMPORTANT: This line is added

urlpatterns = [
    # Django Admin site URL
    path('admin/', admin.site.urls),


    path('chat/test/', chat_test_view, name='chat_test'),


    path('api/chat/rooms/', ChatRoomListCreateAPIView.as_view(), name='chat-room-list-create'),
    path('api/chat/rooms/<int:pk>/', ChatRoomDetailAPIView.as_view(), name='chat-room-detail'),
    path('api/chat/rooms/<int:room_id>/messages/', MessageListAPIView.as_view(), name='message-list'),
    path('api/chat/rooms/<int:room_id>/messages/create/', MessageCreateAPIView.as_view(), name='message-create'),


    path('notifications/test/', notification_test_view, name='notification_test'), # <--- IMPORTANT: This line is added
]