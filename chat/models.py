# my_entrepreneur_platform/chat/models.py

from django.db import models
from django.conf import settings # To refer to the User model configured in settings.py

class ChatRoom(models.Model):
    """
    Represents a chat room or conversation. Can be private (2 users) or group.
    """
    # Name for group chats (optional for private chats)
    name = models.CharField(max_length=255, unique=True, blank=True, null=True)
    # Boolean to distinguish between group chats and direct messages
    is_group_chat = models.BooleanField(default=False)
    # Users participating in this chat room (Many-to-Many relationship)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='chat_rooms'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # Useful for sorting recent chats

    class Meta:
        verbose_name = "Chat Room"
        verbose_name_plural = "Chat Rooms"
        # Order by most recently updated chat room
        ordering = ['-updated_at']

    def __str__(self):
        if self.name:
            return self.name
        # For private chats, display participants' usernames
        usernames = ", ".join([user.username for user in self.participants.all()])
        return f"Private Chat: {usernames}"

class Message(models.Model):
    """
    Represents a single message within a chat room.
    """
    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE, # If a room is deleted, delete its messages
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, # If a user is deleted, delete their messages
        related_name='sent_messages'
    )
    content = models.TextField() # The actual message text
    timestamp = models.DateTimeField(auto_now_add=True) # When the message was sent
    is_read = models.BooleanField(default=False) # Simple read status (can be expanded)

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        # Order messages by time sent (oldest first)
        ordering = ['timestamp']

    def __str__(self):
        return f"Message by {self.sender.username} in {self.chat_room.name or self.chat_room.pk} at {self.timestamp.strftime('%H:%M')}"