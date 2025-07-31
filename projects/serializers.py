# my_entrepreneur_platform/projects/serializers.py

from rest_framework import serializers
from .models import Technology, Project
from django.contrib.auth import get_user_model
from startups.serializers import StartupSerializer as BasicStartupSerializer # For nesting Startup info
from users.serializers import UserSerializer as BasicUserSerializer # For nesting User info

User = get_user_model()

# Serializer for the Technology model
class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = ['id', 'name', 'description']

# Serializer for the Project model
class ProjectSerializer(serializers.ModelSerializer):
    # Display owner and related_startup using nested serializers
    owner = BasicUserSerializer(read_only=True) # Read-only, will be set automatically by view
    owner_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='owner', write_only=True, required=False) # For input
    
    related_startup = BasicStartupSerializer(read_only=True) # Nested display of Startup
    related_startup_id = serializers.PrimaryKeyRelatedField(
        queryset=BasicStartupSerializer.Meta.model.objects.all(), # Use model from BasicStartupSerializer
        source='related_startup', write_only=True, required=False, allow_null=True
    ) # For input (providing startup ID)

    # Display technologies_used using the TechnologySerializer
    technologies_used = TechnologySerializer(many=True, read_only=True)
    technologies_used_ids = serializers.PrimaryKeyRelatedField(
        queryset=Technology.objects.all(), source='technologies_used', many=True, write_only=True, required=False
    ) # For input (providing list of technology IDs)

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'tagline', 'description', 'project_logo', 'status',
            'technologies_used', 'technologies_used_ids',
            'looking_for', 'link_to_repo', 'link_to_demo',
            'owner', 'owner_id',
            'related_startup', 'related_startup_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']