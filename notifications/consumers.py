# my_entrepreneur_platform/notifications/consumers.py

import json
import datetime # Used for getting current timestamp
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async # For running synchronous DB operations in async context
from channels.layers import get_channel_layer # <--- IMPORTANT: This is the new import to get the channel layer

from django.contrib.auth import get_user_model # To get the User model configured in settings
from .models import Notification # Import Navya's Notification model

User = get_user_model() # Dynamically get your custom or default User model

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # We expect the user's ID in the URL for personalized notifications
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        # This is the group name for this specific user's notifications (e.g., 'user_1_notifications')
        self.user_group_name = f'user_{self.user_id}_notifications' 

        user = self.scope["user"] # Get the authenticated user from the WebSocket scope

        # 1. Authentication and Authorization Check
        if user.is_anonymous:
            print(f"Notification WS rejected: Anonymous user attempting to connect to user_id {self.user_id}")
            await self.close() # Close the connection
            return

        # Ensure the connecting user's ID matches the user_id in the URL
        # This prevents a user from trying to listen to another user's notifications
        if str(user.id) != self.user_id:
            print(f"Notification WS rejected: User {user.username} (ID: {user.id}) attempting to connect to other user's notifications ({self.user_id})")
            await self.close()
            return

        # 2. Join the user's specific notification group in the Channel Layer (Redis)
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        await self.accept() # Accept the WebSocket connection
        print(f"Notification WS connected: User {user.username} (ID: {user.id}) listening for notifications.")

        # Optional: You could fetch and send any unread notifications from the database here on connect.
        # This is more complex and can be done later if time permits.
        # For now, we'll focus on receiving only new notifications as they are pushed.

    async def disconnect(self, close_code):
        # Get the user from the scope (using .get for safety, as user might not exist if connect failed)
        user = self.scope.get("user")
        
        # Only attempt to remove from group if the user was authenticated and connected to their own channel
        if user and not user.is_anonymous and str(user.id) == self.user_id:
            print(f"Notification WS disconnected: User {user.username} stopped listening.")
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
        else:
            print(f"Notification WS disconnected: Unauthenticated/mismatched user left.")

    # This consumer primarily receives messages *from the Channel Layer* (i.e., from backend code).
    # It does not typically receive messages *from* the frontend client directly, unless designed for it.
    async def receive(self, text_data):
        print(f"Notification Consumer received message from client (not typically expected for notifications): {text_data}")
        # If you wanted clients to send something (e.g., mark as read), you'd add logic here.

    # This method is called by the Channel Layer (Redis) when a message is sent to this user's group.
    # The 'type': 'send_notification' in group_send calls this method.
    async def send_notification(self, event):
        # The 'event' dictionary contains the 'notification_data' sent from the backend
        notification_data = event['notification_data']
        # Send this notification data back down the WebSocket to the client's browser
        await self.send(text_data=json.dumps(notification_data))

    # Helper function (classmethod) to create a notification in the database and push it in real-time.
    # This method will be called from other parts of your Django app (e.g., from a view, a signal, or a shell).
    @classmethod
    async def create_and_send_notification(cls, recipient, actor=None, verb=None, target=None, action_url=None, message_data=None):
        # Ensure recipient is a User instance, or fetch it from DB
        if isinstance(recipient, int):
            recipient = await database_sync_to_async(User.objects.get)(id=recipient)
        elif not isinstance(recipient, User):
            raise ValueError("Recipient must be a User instance or user ID.")

        # Create the Notification object in the database (synchronous operation)
        notification_obj = await database_sync_to_async(Notification.objects.create)(
            recipient=recipient,
            actor=actor, # GenericForeignKey needs actor as a Django object if provided
            verb=verb or "has an update", # Default verb if not provided
            target=target, # GenericForeignKey needs target as a Django object if provided
            action_url=action_url,
        )
        print(f"Notification created in DB for {recipient.username}: {notification_obj.verb}")

        # Prepare the data to be sent over WebSocket. This is the JSON payload the frontend will receive.
        payload = {
            "id": notification_obj.id,
            "recipient_id": recipient.id,
            "actor_id": actor.id if actor else None,
            "actor_username": actor.username if actor else None,
            "verb": notification_obj.verb,
            "target_info": str(target) if target else None, # Convert target object to string for display
            "action_url": notification_obj.action_url,
            "timestamp": notification_obj.timestamp.isoformat(),
            "is_read": notification_obj.is_read,
            "message": message_data or f"{actor.username if actor else 'Someone'} {verb or 'has an update'}!"
        }

        # --- IMPORTANT: Get the Channel Layer instance to send messages globally ---
        channel_layer = get_channel_layer() 

        # Send the notification via the Channel Layer (Redis) to the recipient's specific group
        user_group_name = f'user_{recipient.id}_notifications'
        await channel_layer.group_send( # Use the obtained channel_layer instance here
            user_group_name,
            {
                'type': 'send_notification', # This tells the recipient's NotificationConsumer to call its send_notification method
                'notification_data': payload # The actual data to send to the frontend
            }
        )
        print(f"Notification sent to Channel Layer for user {recipient.username}.")