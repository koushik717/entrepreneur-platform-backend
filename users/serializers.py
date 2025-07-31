# my_entrepreneur_platform/users/serializers.py

from rest_framework import serializers
from .models import UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()

# Serializer for the Django built-in User model (basic info)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['username', 'email'] # Username/email often not directly changeable via profile API

# Serializer for your custom UserProfile model
class UserProfileSerializer(serializers.ModelSerializer):
    # Include the basic user details nested within the profile
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'profile_picture', 'location', 'phone_number', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at'] # Auto-set by Django