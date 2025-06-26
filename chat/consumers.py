# my_entrepreneur_platform/chat/consumers.py

import json
import datetime # For timestamping messages
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async # Essential for database operations in async context

from django.contrib.auth import get_user_model # To get the User model
from .models import ChatRoom, Message # Your chat models

User = get_user_model() # Dynamically get your custom or default User model

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract room name from the URL path (e.g., 'general' from ws/chat/general/)
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        # Create a group name for the chat room (used by Redis Channel Layer)
        self.room_group_name = f'chat_{self.room_name}'

        # Get the authenticated user from the WebSocket scope
        user = self.scope["user"]

        # 1. Authentication Check: Reject anonymous users
        if user.is_anonymous:
            print(f"WebSocket rejected: Anonymous user trying to connect to room {self.room_name}")
            await self.close() # Close the connection
            return # Stop further execution

        # 2. Chat Room Existence Check and Participant Check
        try:
            # Fetch the ChatRoom object from the database synchronously
            self.chat_room = await database_sync_to_async(ChatRoom.objects.get)(name=self.room_name)
        except ChatRoom.DoesNotExist:
            print(f"WebSocket rejected: Chat room '{self.room_name}' not found.")
            await self.close()
            return

        # Check if the connecting user is a participant of this chat room synchronously
        # Use lambda to wrap the entire synchronous QuerySet evaluation
        is_participant = await database_sync_to_async(
            lambda: self.chat_room.participants.filter(id=user.id).exists()
        )()

        if not is_participant:
            print(f"WebSocket rejected: User {user.username} is not a participant of room {self.room_name}")
            await self.close()
            return

        # If all checks pass, proceed:
        # Join the specific chat room group in the Channel Layer (Redis)
        await self.channel_layer.group_add(
            self.room_group_name, # The group to join (e.g., 'chat_general')
            self.channel_name     # This specific WebSocket connection's unique ID
        )

        # Accept the WebSocket connection. This completes the handshake.
        await self.accept()

        print(f"WebSocket connected: User {user.username} (ID: {user.id}) joined room {self.room_name}")

        # 3. Load and Send Recent Chat History
        # Fetch the last 10 messages for this chat room from the database synchronously
        # Use lambda to wrap the entire synchronous QuerySet evaluation
        recent_messages = await database_sync_to_async(lambda: list(
            Message.objects.filter(chat_room=self.chat_room)
                           .order_by('-timestamp')[:10]
                           .select_related('sender') # Optimize by fetching sender data in one query
        ))()

        # Reverse the order to send oldest messages first (chronological order)
        recent_messages = reversed(recent_messages)

        # Send each historical message to the newly connected client
        for message_obj in recent_messages:
            message_data = {
                'message': f"{message_obj.sender.username}: {message_obj.content}",
                'sender_id': message_obj.sender.id,
                'timestamp': message_obj.timestamp.isoformat() # Convert datetime object to ISO string
            }
            await self.send(text_data=json.dumps(message_data))

    async def disconnect(self, close_code):
        # Get the user from the scope (using .get for safety, as user might not exist if connect failed)
        user = self.scope.get("user")

        # Only attempt to remove from group if the user was authenticated and connected
        if user and not user.is_anonymous:
            print(f"WebSocket disconnected: User {user.username} left room {self.room_name}")
            # Remove this connection from the chat room group in the Channel Layer
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        else:
            print(f"WebSocket disconnected: Anonymous user left room {self.room_name}")

    async def receive(self, text_data):
        # Get the authenticated user
        user = self.scope["user"]

        # Double-check authentication (though connect() should prevent this for new connections)
        if user.is_anonymous:
            print(f"Receive rejected: Anonymous user tried to send message to room {self.room_name}")
            return

        # Parse the incoming message from the WebSocket (frontend sends JSON)
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']

        # 1. Save the message to the database (using Surya's models)
        try:
            # Create a new Message object synchronously
            new_message_obj = await database_sync_to_async(Message.objects.create)(
                chat_room=self.chat_room, # Use the chat_room object fetched in connect
                sender=user,              # The authenticated user
                content=message_content
            )
            print(f"Message saved: User {user.username} in room {self.chat_room.name}: {message_content}")
        except Exception as e:
            print(f"Error saving message: {e}")
            # Optionally send an error message back to the client if saving fails
            await self.send(text_data=json.dumps({"error": "Failed to save message. Please try again."}))
            return

        # 2. Prepare message for real-time broadcast to all clients in the group
        # This will be displayed in the chat logs of all connected users
        full_message_display = f"{user.username}: {message_content}"

        # Send the message to the specific chat room group via the Channel Layer (Redis)
        # The 'type': 'chat_message' tells other consumers in the group to call their chat_message method
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',          # Method to call in other consumers
                'message': full_message_display, # The text to display
                'sender_id': user.id,            # Sender's ID
                'timestamp': new_message_obj.timestamp.isoformat() # Use the timestamp from the saved object
            }
        )

    # This method is called when a message is received from the Channel Layer (Redis)
    # (i.e., when another consumer in the group sent a message)
    async def chat_message(self, event):
        message_text = event['message']
        sender_id = event.get('sender_id')
        timestamp = event.get('timestamp')

        # Send the received message back down this WebSocket to the client's browser
        await self.send(text_data=json.dumps({
            'message': message_text,
            'sender_id': sender_id,
            'timestamp': timestamp
        }))