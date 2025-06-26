# my_entrepreneur_platform/chat/serializers.py

from rest_framework import serializers
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model # To get the User model dynamically

User = get_user_model() # Get your custom or default User model

class UserSerializer(serializers.ModelSerializer):
    # A simple serializer for user details needed in chat context
    class Meta:
        model = User
        fields = ['id', 'username', 'email'] # Only expose necessary fields

class ChatRoomSerializer(serializers.ModelSerializer):
    # To show who the participants are, use the UserSerializer we just made
    participants = UserSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'is_group_chat', 'participants', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at'] # These are set automatically

class MessageSerializer(serializers.ModelSerializer):
    # To show who sent the message, use the UserSerializer
    sender = UserSerializer(read_only=True)
    # Display the sender's ID when creating/updating messages, but allow read_only for sender object
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='sender', write_only=True
    )

    class Meta:
        model = Message
        fields = ['id', 'chat_room', 'sender', 'sender_id', 'content', 'timestamp', 'is_read']
        read_only_fields = ['timestamp'] # This is set automatically

# A separate serializer for creating messages, mainly used by the WebSocket
class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['chat_room', 'content'] # We will get sender from the authenticated user