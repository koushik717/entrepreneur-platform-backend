# my_entrepreneur_platform/chat/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # --- ADD THIS AUTHENTICATION CHECK ---
        user = self.scope["user"] # Get the user object from the WebSocket scope

        if user.is_anonymous: # Check if the user is not logged in
            print(f"WebSocket rejected: Anonymous user trying to connect to room {self.room_name}")
            await self.close() # Close the connection immediately if not authenticated
            return # Stop the connect method here

        print(f"WebSocket connected: User {user.username} (ID: {user.id}) joined room {self.room_name}")
        # --- END AUTHENTICATION CHECK ---


        # Join room group (only if authenticated)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept() # Accept the connection (only if authenticated)

    async def disconnect(self, close_code):
        # Check if user was added to group before trying to remove
        user = self.scope.get("user")
        if user and not user.is_anonymous:
            print(f"WebSocket disconnected: User {user.username} left room {self.room_name}")
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        else:
            print(f"WebSocket disconnected: Anonymous user left room {self.room_name}")


    async def receive(self, text_data):
        # Get the user object from the WebSocket scope
        user = self.scope["user"]

        # Double-check authentication for safety (though connect() should handle it)
        if user.is_anonymous:
            print(f"Receive rejected: Anonymous user tried to send message to room {self.room_name}")
            return # Don't process message if not authenticated

        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Add sender's username to the message for display (optional, but good for testing)
        full_message = f"{user.username}: {message}"

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': full_message # Send the message with username
            }
        )

    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))