# my_entrepreneur_platform/search/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.models import UserProfile
from startups.models import Startup, Industry
from projects.models import Project, Technology
from content.models import Post

# Re-using/simplifying basic serializers for search results
User = get_user_model()

class UserSearchSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField() # Nest profile info

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'profile']

    def get_profile(self, obj):
        try:
            return UserProfileSearchSerializer(obj.userprofile).data
        except UserProfile.DoesNotExist:
            return None

class UserProfileSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['bio', 'location', 'profile_picture'] # Just a few fields for search

class StartupSearchSerializer(serializers.ModelSerializer):
    industry_name = serializers.CharField(source='industry.name', read_only=True) # Display industry name

    class Meta:
        model = Startup
        fields = ['id', 'name', 'tagline', 'description', 'industry_name', 'stage', 'logo']

class ProjectSearchSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    class Meta:
        model = Project
        fields = ['id', 'title', 'tagline', 'description', 'status', 'owner_username', 'project_logo']

class PostSearchSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'content', 'post_type', 'owner_username', 'image', 'link']