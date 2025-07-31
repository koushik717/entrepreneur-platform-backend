# my_entrepreneur_platform/projects/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Technology, Project # Your models
from .serializers import TechnologySerializer, ProjectSerializer # Your serializers
from startups.models import Startup # Import Startup model for permission checking


# Custom Permission: Only the owner of the object can modify/delete it
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request, so we'll always allow GET, HEAD, or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the owner of the object.
        return obj.owner == request.user

# View for listing and creating Technologies (might be admin-only later, or authenticated only)
class TechnologyListCreateAPIView(generics.ListCreateAPIView):
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
    permission_classes = [permissions.AllowAny] # Allow anyone to list technologies

# View for retrieving a single Technology
class TechnologyDetailAPIView(generics.RetrieveAPIView):
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
    permission_classes = [permissions.AllowAny] # Anyone can view a specific technology

# View for listing all projects and creating new ones
class ProjectListCreateAPIView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Authenticated can create, anyone can list

    def perform_create(self, serializer):
        # Automatically set the owner of the project to the currently authenticated user
        serializer.save(owner=self.request.user)

# View for retrieving, updating, and deleting a specific project
class ProjectRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Allow read for all, but need custom permission for update/delete

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        return super().get_permissions()