# my_entrepreneur_platform/content/serializers.py

from rest_framework import serializers
from .models import Post, Comment, Like
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType # For GenericForeignKey

User = get_user_model()

# A basic user serializer for nesting in Post/Comment
class BasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

# Serializer for Post model (UPDATED FOR LIKES_COUNT)
class PostSerializer(serializers.ModelSerializer):
    owner = BasicUserSerializer(read_only=True) # Display owner's info
    owner_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='owner', write_only=True) # For input
    likes_count = serializers.IntegerField(read_only=True) # <--- IMPORTANT: ADD THIS LINE

    class Meta:
        model = Post
        fields = [
            'id', 'owner', 'owner_id', 'content', 'image', 'video', 'link',
            'post_type', 'is_public', 'created_at', 'updated_at',
            'likes_count' # <--- IMPORTANT: ADD THIS LINE
        ]
        read_only_fields = ['created_at', 'updated_at', 'likes_count']

# Serializer for Comment model
class CommentSerializer(serializers.ModelSerializer):
    author = BasicUserSerializer(read_only=True) # Display author's info
    author_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='author', write_only=True) # For input
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'author_id', 'content', 'created_at']
        read_only_fields = ['created_at']

# Serializer for Like model (for creating/deleting likes)
class LikeSerializer(serializers.ModelSerializer):
    user = BasicUserSerializer(read_only=True) # Display user's info
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True) # For input
    
    # Generic fields for the liked object
    content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.filter(model__in=['post', 'comment']),
        slug_field='model',
        write_only=True
    )
    object_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'user_id', 'content_type', 'object_id', 'created_at']
        read_only_fields = ['created_at']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Like.objects.all(),
                fields=['user', 'content_type', 'object_id'],
                message="User has already liked this item."
            )
        ]

    # Custom validation to ensure object_id refers to a valid object of content_type
    def validate(self, data):
        content_type = data.get('content_type')
        object_id = data.get('object_id')

        if not content_type or not object_id:
            raise serializers.ValidationError("content_type and object_id are required.")
        
        try:
            # Get the actual model class from the ContentType
            Model = content_type.model_class()
            if not Model:
                raise serializers.ValidationError("Invalid content_type.")
            
            # Check if the object with object_id exists for that model
            Model.objects.get(pk=object_id)
        except (ContentType.DoesNotExist, Model.DoesNotExist):
            raise serializers.ValidationError("Related object does not exist.")
        except Exception as e:
            raise serializers.ValidationError(f"Error validating object: {e}")

        return data