# my_entrepreneur_platform/startups/serializers.py

from rest_framework import serializers
from .models import Industry, Startup
from django.contrib.auth import get_user_model

User = get_user_model()

# Simple serializer for the Industry model
class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ['id', 'name', 'description']

# Serializer for the Startup model
class StartupSerializer(serializers.ModelSerializer):
    # Display owner and followers using a simple user representation
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all()) # For input/output
    owner_username = serializers.CharField(source='owner.username', read_only=True) # For display only
    
    industry = IndustrySerializer(read_only=True) # Nested display of Industry
    industry_id = serializers.PrimaryKeyRelatedField(
        queryset=Industry.objects.all(), source='industry', write_only=True, required=False, allow_null=True
    ) # For input (providing industry ID)

    # followers = UserSerializer(many=True, read_only=True) # If you had a UserSerializer defined in startups

    class Meta:
        model = Startup
        fields = [
            'id', 'name', 'tagline', 'description', 'industry', 'industry_id',
            'stage', 'funding_needs', 'website_url', 'pitch_deck_url', 'logo',
            'owner', 'owner_username', 'followers', 'created_at', 'updated_at'
        ]
        read_only_fields = ['followers', 'created_at', 'updated_at'] # Followers handled via separate actions