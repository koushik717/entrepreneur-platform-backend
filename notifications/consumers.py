# my_entrepreneur_platform/notifications/consumers.py

import json
import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer

from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.user_group_name = f'user_{self.user_id}_notifications' 

        user = self.scope["user"]

        if user.is_anonymous:
            print(f"Notification WS rejected: Anonymous user attempting to connect to user_id {self.user_id}")
            await self.close()
            return

        if str(user.id) != self.user_id:
            print(f"Notification WS rejected: User {user.username} (ID: {user.id}) attempting to connect to other user's notifications ({self.user_id})")
            await self.close()
            return

        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"Notification WS connected: User {user.username} (ID: {user.id}) listening for notifications.")

    async def disconnect(self, close_code):
        user = self.scope.get("user")
        if user and not user.is_anonymous and str(user.id) == self.user_id:
            print(f"Notification WS disconnected: User {user.username} stopped listening.")
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
        else:
            print(f"Notification WS disconnected: Unauthenticated/mismatched user left.")

    async def receive(self, text_data):
        print(f"Notification Consumer received message from client (not typically expected for notifications): {text_data}")

    async def send_notification(self, event):
        notification_data = event['notification_data']
        await self.send(text_data=json.dumps(notification_data))

    @classmethod
    async def create_and_send_notification(cls, recipient, actor=None, verb=None, target=None, action_url=None, message_data=None):
        if isinstance(recipient, int):
            recipient = await database_sync_to_async(User.objects.get)(id=recipient)
        elif not isinstance(recipient, User):
            raise ValueError("Recipient must be a User instance or user ID.")

        notification_obj = await database_sync_to_async(Notification.objects.create)(
            recipient=recipient,
            actor=actor,
            verb=verb or "has an update",
            target=target,
            action_url=action_url,
        )
        print(f"Notification created in DB for {recipient.username}: {notification_obj.verb}")

        payload = {
            "id": notification_obj.id,
            "recipient_id": recipient.id,
            "actor_id": actor.id if actor else None,
            "actor_username": actor.username if actor else None,
            "verb": notification_obj.verb,
            "target_info": str(target) if target else None,
            "action_url": notification_obj.action_url,
            "timestamp": notification_obj.timestamp.isoformat(),
            "is_read": notification_obj.is_read,
            "message": message_data or f"{actor.username if actor else 'Someone'} {verb or 'has an update'}!"
        }

        channel_layer = get_channel_layer() 

        user_group_name = f'user_{recipient.id}_notifications'
        await channel_layer.group_send(
            user_group_name,
            {
                'type': 'send_notification',
                'notification_data': payload
            }
        )
        print(f"Notification sent to Channel Layer for user {recipient.username}")