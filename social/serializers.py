# my_entrepreneur_platform/social/serializers.py

from rest_framework import serializers
from .models import Follow
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

# Import serializers from other apps to nest related objects
from users.serializers import UserSerializer as BasicUserSerializer # For follower/followed_user info
from startups.serializers import StartupSerializer as BasicStartupSerializer # For followed_startup info

User = get_user_model()

# Serializer for creating/deleting a Follow relationship
class FollowCreateSerializer(serializers.ModelSerializer):
    # These fields are used for input (who is being followed)
    content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.filter(model__in=['user', 'startup']), # Can follow User or Startup
        slug_field='model',
        write_only=True
    )
    object_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Follow
        fields = ['content_type', 'object_id']
        read_only_fields = ['follower', 'created_at'] # Follower is set automatically by view, created_at by Django

    # Custom validation to ensure content_type and object_id form a valid, existing object
    def validate(self, data):
        content_type = data.get('content_type')
        object_id = data.get('object_id')
        follower = self.context['request'].user # Get follower from request context

        if not content_type or not object_id:
            raise serializers.ValidationError("Content type and object ID are required.")

        # Get the actual model class from the ContentType
        Model = content_type.model_class()
        if not Model:
            raise serializers.ValidationError("Invalid content type specified.")

        try:
            followed_object = Model.objects.get(pk=object_id)
        except Model.DoesNotExist:
            raise serializers.ValidationError("Object to follow does not exist.")

        # Prevent a user from following themselves
        if Model == User and followed_object == follower:
            raise serializers.ValidationError("You cannot follow yourself.")

        # Ensure user is not already following this object (handled by unique_together in model, but good here)
        if Follow.objects.filter(follower=follower, content_type=content_type, object_id=object_id).exists():
            raise serializers.ValidationError("You are already following this item.")
        
        # --- IMPORTANT: The line 'data['followed_object'] = followed_object' has been REMOVED.
        # This was causing the TypeError, as 'followed_object' is not a field on the Follow model.
        # The serializer now correctly only passes model fields to .save() ---

        return data

# Serializer for displaying Follow relationships (who is following whom)
class FollowSerializer(serializers.ModelSerializer):
    follower = BasicUserSerializer(read_only=True) # Show info about the follower
    
    # Use SerializerMethodField to dynamically serialize the followed object (User or Startup)
    followed_object_info = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'content_type', 'object_id', 'followed_object_info', 'created_at']
        read_only_fields = ['id', 'follower', 'content_type', 'object_id', 'followed_object_info', 'created_at']

    def get_followed_object_info(self, obj):
        # Dynamically serialize the content_object (User or Startup)
        if isinstance(obj.content_object, User):
            return BasicUserSerializer(obj.content_object).data
        elif isinstance(obj.content_object, BasicStartupSerializer.Meta.model): # Check against the Startup model
            return BasicStartupSerializer(obj.content_object).data
        return None