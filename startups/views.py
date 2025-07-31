# my_entrepreneur_platform/startups/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Industry, Startup # Your models
from .serializers import IndustrySerializer, StartupSerializer 

# Custom Permission: Only the owner of the object can modify/delete it
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request, so we'll always allow GET, HEAD, or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user

# View for listing and creating Industries (might be admin-only later)
class IndustryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer
    permission_classes = [permissions.IsAdminUser] # Only admin users can create/list industries

# View for retrieving a single Industry
class IndustryDetailAPIView(generics.RetrieveAPIView):
    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer
    permission_classes = [permissions.AllowAny] # Anyone can view industries

# View for listing all startups and creating new ones
class StartupListCreateAPIView(generics.ListCreateAPIView):
    queryset = Startup.objects.all()
    serializer_class = StartupSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Authenticated can create, anyone can list

    def perform_create(self, serializer):
        # Automatically set the owner of the startup to the currently authenticated user
        serializer.save(owner=self.request.user)

# View for retrieving, updating, and deleting a specific startup
class StartupRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Startup.objects.all()
    serializer_class = StartupSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        return super().get_permissions()