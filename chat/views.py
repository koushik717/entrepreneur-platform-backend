# my_entrepreneur_platform/chat/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import generics, permissions, status # New imports
from rest_framework.response import Response # New import
from django.db.models import Q # New import for complex lookups

from .models import ChatRoom, Message # Your chat models
from .serializers import ChatRoomSerializer, MessageSerializer, MessageCreateSerializer # Your new serializers
from django.contrib.auth import get_user_model # To get the User model

User = get_user_model() # Get your custom or default User model


# --- Your existing chat_test_view ---
@login_required
def chat_test_view(request):
    return render(request, 'chat_test.html', {})
# --- End existing chat_test_view ---


# --- New API Views for Chat Rooms ---
class ChatRoomListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated] # Only logged-in users can access

    def get_queryset(self):
        # Return chat rooms where the current authenticated user is a participant
        return self.request.user.chat_rooms.all()

    def perform_create(self, serializer):
        # When creating a new chat room (e.g., a private chat)
        # Frontend might send { "participants": [other_user_id] }
        # Or just { "name": "Group Chat Name", "is_group_chat": true, "participants": [ids] }

        # Example for creating a direct message chat (between current user and one other)
        # Expects 'other_user_id' in the request data
        other_user_id = self.request.data.get('other_user_id')
        if not other_user_id:
            raise serializers.ValidationError({"detail": "For direct chat, 'other_user_id' is required."})

        try:
            other_user = User.objects.get(id=other_user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "Other user not found."})

        # Check if a direct chat between these two users already exists
        # Q objects allow for complex OR/AND queries
        existing_chat = ChatRoom.objects.filter(
            is_group_chat=False
        ).filter(
            Q(participants=self.request.user) & Q(participants=other_user)
        ).distinct().first()

        if existing_chat:
            # If it exists, return the existing chat
            serializer = self.get_serializer(existing_chat)
            return Response(serializer.data, status=status.HTTP_200_OK) # Return 200 OK for existing resource

        # Create the new chat room
        instance = serializer.save(is_group_chat=False)
        instance.participants.add(self.request.user, other_user)
        instance.save() # Save again to update ManyToMany
        return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED)

class ChatRoomDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ChatRoom.objects.all() # Or more restrictive queryset

    def get_queryset(self):
        # Only allow users to retrieve chat rooms they are a participant of
        return self.request.user.chat_rooms.filter(id=self.kwargs['pk'])


# --- New API Views for Messages ---
class MessageListAPIView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        try:
            chat_room = ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            raise generics.NotFound("Chat room not found.")

        # Ensure the requesting user is a participant of this chat room
        if self.request.user not in chat_room.participants.all():
            raise permissions.PermissionDenied("You are not a participant of this chat room.")

        # Return messages for this chat room, ordered by timestamp
        return chat_room.messages.all().select_related('sender') # 'select_related' improves performance

class MessageCreateAPIView(generics.CreateAPIView):
    serializer_class = MessageCreateSerializer # Use the simpler serializer for creation
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        room_id = self.kwargs['room_id']
        try:
            chat_room = ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            raise generics.NotFound("Chat room not found.")

        # Ensure the requesting user is a participant of this chat room before creating a message
        if self.request.user not in chat_room.participants.all():
            raise permissions.PermissionDenied("You are not a participant of this chat room.")

        # Save the message, linking the sender to the current authenticated user
        serializer.save(sender=self.request.user, chat_room=chat_room)