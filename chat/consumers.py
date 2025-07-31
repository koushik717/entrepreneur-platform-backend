# my_entrepreneur_platform/chat/consumers.py

import json
import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from django.contrib.auth import get_user_model
from .models import ChatRoom, Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        user = self.scope["user"]

        if user.is_anonymous:
            print(f"WebSocket rejected: Anonymous user trying to connect to room {self.room_name}")
            await self.close()
            return

        try:
            self.chat_room = await database_sync_to_async(ChatRoom.objects.get)(name=self.room_name)
        except ChatRoom.DoesNotExist:
            print(f"WebSocket rejected: Chat room '{self.room_name}' not found.")
            await self.close()
            return

        is_participant = await database_sync_to_async(
            lambda: self.chat_room.participants.filter(id=user.id).exists()
        )()

        if not is_participant:
            print(f"WebSocket rejected: User {user.username} is not a participant of room {self.room_name}")
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        print(f"WebSocket connected: User {user.username} (ID: {user.id}) joined room {self.room_name}")

        recent_messages = await database_sync_to_async(lambda: list(
            Message.objects.filter(chat_room=self.chat_room)
                           .order_by('-timestamp')[:10]
                           .select_related('sender')
        ))()
        
        recent_messages = reversed(recent_messages)

        for message_obj in recent_messages:
            message_data = {
                'message': f"{message_obj.sender.username}: {message_obj.content}",
                'sender_id': message_obj.sender.id,
                'timestamp': message_obj.timestamp.isoformat()
            }
            await self.send(text_data=json.dumps(message_data))

    async def disconnect(self, close_code):
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
        user = self.scope["user"]

        if user.is_anonymous:
            print(f"Receive rejected: Anonymous user tried to send message to room {self.room_name}")
            return

        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']

        try:
            new_message_obj = await database_sync_to_async(Message.objects.create)(
                chat_room=self.chat_room,
                sender=user,
                content=message_content
            )
            print(f"Message saved: User {user.username} in room {self.chat_room.name}: {message_content}")
        except Exception as e:
            print(f"Error saving message: {e}")
            await self.send(text_data=json.dumps({"error": "Failed to save message."}))
            return

        full_message_display = f"{user.username}: {message_content}"

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': full_message_display,
                'sender_id': user.id,
                'timestamp': new_message_obj.timestamp.isoformat()
            }
        )

    async def chat_message(self, event):
        message_text = event['message']
        sender_id = event.get('sender_id')
        timestamp = event.get('timestamp')

        await self.send(text_data=json.dumps({
            'message': message_text,
            'sender_id': sender_id,
            'timestamp': timestamp
        }))