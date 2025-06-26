# my_entrepreneur_platform/notifications/models.py

from django.db import models
from django.conf import settings # To refer to the User model
from django.contrib.contenttypes.fields import GenericForeignKey # For generic relations
from django.contrib.contenttypes.models import ContentType # For generic relations

class Notification(models.Model):
    """
    Represents a generic notification for a user.
    Examples: A user liked your post, someone followed you, new message, etc.
    """
    # Who receives the notification
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    # Who caused the notification (optional)
    actor_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='actor_notifications', null=True, blank=True)
    actor_object_id = models.PositiveIntegerField(null=True, blank=True)
    actor = GenericForeignKey('actor_content_type', 'actor_object_id')

    # What happened (e.g., 'liked', 'followed', 'commented on', 'sent a message')
    verb = models.CharField(max_length=255)

    # The object related to the notification (e.g., the Post that was liked, the User that was followed)
    target_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='target_notifications', null=True, blank=True)
    target_object_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    # Optional: A URL to directly link to the relevant content
    action_url = models.URLField(blank=True, null=True)

    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False) # Has the user seen/read this notification?

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-timestamp'] # Newest notifications first

    def __str__(self):
        if self.actor:
            return f"{self.actor.username} {self.verb} {self.target or ''}"
        return f"{self.recipient.username} - {self.verb} {self.target or ''}"

    def get_absolute_url(self):
        return self.action_url or '#'