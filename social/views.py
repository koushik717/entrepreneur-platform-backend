# my_entrepreneur_platform/social/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType # For GenericForeignKey
from django.db import IntegrityError # To handle unique_together exceptions

from .models import Follow
from .serializers import FollowCreateSerializer, FollowSerializer

from django.contrib.auth import get_user_model
User = get_user_model()

from startups.models import Startup # Import Startup model to check type

# View for creating and deleting Follow relationships
class FollowCreateDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # POST: Create a new Follow (UPDATED)
    def post(self, request, content_type_model, object_id, *args, **kwargs): # content_type_model and object_id are from URL
        # Validate content_type_model from URL
        if content_type_model not in ['user', 'startup']:
            return Response({"detail": "Invalid content_type_model in URL. Must be 'user' or 'startup'."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Create a mutable dictionary of data for the serializer
        # We put the URL kwargs into the data so the serializer can find them
        data_for_serializer = request.data.copy()
        data_for_serializer['content_type'] = content_type_model # e.g., 'user'
        data_for_serializer['object_id'] = object_id # e.g., 2

        # Pass the request context to the serializer (needed for current user)
        serializer = FollowCreateSerializer(data=data_for_serializer, context={'request': request})
        serializer.is_valid(raise_exception=True) # Validate the data

        try:
            # serializer.save() will create the Follow instance using the validated_data
            # The serializer's validate method will have already checked followed_object existence
            follow_instance = serializer.save(follower=request.user) # Set the follower automatically

            return Response(FollowSerializer(follow_instance).data, status=status.HTTP_201_CREATED)
        except IntegrityError: # Handle unique_together constraint (already following)
            return Response(
                {"detail": "You are already following this item."},
                status=status.HTTP_409_CONFLICT # 409 Conflict indicates existing resource
            )
        except Exception as e:
            return Response(
                {"detail": f"Could not follow: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    # DELETE: Unfollow an existing relationship (UPDATED for robustness)
    def delete(self, request, content_type_model, object_id, *args, **kwargs):
        if content_type_model not in ['user', 'startup']:
            return Response({"detail": "Invalid content type model for unfollow."},
                            status=status.HTTP_400_BAD_REQUEST)

        content_type = get_object_or_404(ContentType, model=content_type_model)

        # Find the specific Follow object for the current user
        follow_instance = get_object_or_404(
            Follow,
            follower=request.user, # Ensure the follower matches the current user
            content_type=content_type,
            object_id=object_id
        )
        follow_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# --- Remaining Views (FollowingListAPIView, FollowersListAPIView) as they were ---
class FollowingListAPIView(generics.ListAPIView):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        return Follow.objects.filter(follower=user).select_related('content_type').order_by('-created_at')

class FollowersListAPIView(generics.ListAPIView):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        user_content_type = ContentType.objects.get_for_model(User)
        return Follow.objects.filter(content_type=user_content_type, object_id=user.id).select_related('follower').order_by('-created_at')