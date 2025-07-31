# my_entrepreneur_platform/users/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404 # New import for retrieving objects

from .models import UserProfile # Your UserProfile model
from .serializers import UserProfileSerializer, UserSerializer # Your new serializers
from django.contrib.auth import get_user_model # To get the User model

User = get_user_model()

# View for a user to retrieve and update their OWN profile
class UserProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated] # Only authenticated users can access

    def get_object(self):
        # Ensure a user can only retrieve/update their own profile
        return get_object_or_404(UserProfile, user=self.request.user)

    def perform_update(self, serializer):
        # Optionally handle profile_picture update or other custom logic here
        serializer.save()

# View for retrieving ANY user's profile (public view)
class UserProfilePublicDetailAPIView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.AllowAny] # Anyone can view public profiles
    queryset = UserProfile.objects.all()
    lookup_field = 'user_id' # Allows lookup by user ID in the URL (e.g., /api/profiles/1/)

    def get_object(self):
        # Retrieve profile by user_id from URL
        user_id = self.kwargs.get('user_id')
        return get_object_or_404(UserProfile, user__id=user_id)