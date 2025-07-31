# my_entrepreneur_platform/notifications/serializers.py

from rest_framework import serializers
from .models import Notification
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType # To serialize generic relations

User = get_user_model()

# A simple serializer for basic User info (if not already defined elsewhere)
class BasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class NotificationSerializer(serializers.ModelSerializer):
    # Serialize the actor and target if they are User objects for simpler display
    actor_user = BasicUserSerializer(source='actor', read_only=True)
    target_user = BasicUserSerializer(source='target', read_only=True) # Assuming target might also be a User

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'actor_user', 'verb', 'target_user',
            'action_url', 'timestamp', 'is_read'
        ]
        read_only_fields = ['recipient', 'timestamp'] # These are set by the system, not frontend

# You might also want a serializer for marking as read
class NotificationMarkReadSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="A list of notification IDs to mark as read."
    )
    mark_all = serializers.BooleanField(
        default=False,
        help_text="Set to true to mark all unread notifications for the user as read. Overrides 'notification_ids'."
    )

    def validate(self, data):
        if not data.get('mark_all') and not data.get('notification_ids'):
            raise serializers.ValidationError("Either 'notification_ids' or 'mark_all' must be provided.")
        return data