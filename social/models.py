# my_entrepreneur_platform/social/models.py

from django.db import models
from django.conf import settings # To refer to the User model
from django.contrib.contenttypes.fields import GenericForeignKey # For generic relations
from django.contrib.contenttypes.models import ContentType # For generic relations

class Follow(models.Model):
    """
    Represents a user following another user or a startup.
    Uses GenericForeignKey for flexibility.
    """
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following', # Renamed from 'followers' to avoid conflict on User model
        help_text="The user who is following."
    )

    # GenericForeignKey to link to either a User or a Startup
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id') # The actual followed object

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Follows"
        # Ensure a user can only follow a specific content_object once
        unique_together = ('follower', 'content_type', 'object_id')
        ordering = ['-created_at'] # Newest follows first

    def __str__(self):
        return f"{self.follower.username} follows {self.content_object}"