# my_entrepreneur_platform/notifications/serializers.py

from rest_framework import serializers
from .models import Notification # Import Navya's Notification model
from django.contrib.auth import get_user_model # To get the User model
from django.contrib.contenttypes.models import ContentType # To handle generic relations

User = get_user_model() # Get your custom or default User model

# A simple serializer for basic User info. This is useful when you want to show
# who the 'actor' (e.g., who liked, who followed) is, without showing all their details.
class BasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username'] # Only expose necessary fields

# The main serializer for a single Notification object
class NotificationSerializer(serializers.ModelSerializer):
    # These fields automatically look up and serialize the related User object if it's an actor/target
    # (assuming actor/target are often User models, as in "User X followed you")
    actor_user = BasicUserSerializer(source='actor', read_only=True)
    target_user = BasicUserSerializer(source='target', read_only=True)

    class Meta:
        model = Notification
        # The fields that will be included in the JSON response for a notification
        fields = [
            'id', 'recipient', 'actor_user', 'verb', 'target_user',
            'action_url', 'timestamp', 'is_read'
        ]
        # These fields are set automatically by the system and shouldn't be set by API requests
        read_only_fields = ['recipient', 'timestamp']

# This serializer is used specifically for API requests that want to mark notifications as read.
# It doesn't map directly to a model, but helps validate incoming data.
class NotificationMarkReadSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(), # Expects a list of integer IDs
        required=False, # Not required if mark_all is true
        help_text="A list of notification IDs to mark as read. Required if 'mark_all' is false."
    )
    mark_all = serializers.BooleanField(
        default=False, # By default, don't mark all
        help_text="Set to true to mark all unread notifications for the user as read. Overrides 'notification_ids'."
    )

    def validate(self, data):
        # Custom validation: if not marking all, then notification_ids must be provided
        if not data.get('mark_all') and not data.get('notification_ids'):
            raise serializers.ValidationError("Either 'notification_ids' or 'mark_all' must be provided.")
        return data