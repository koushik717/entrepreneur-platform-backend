# my_entrepreneur_platform/search/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q # For OR queries
from django.contrib.auth import get_user_model

from users.models import UserProfile
from startups.models import Startup
from projects.models import Project
from content.models import Post

from .serializers import (
    UserSearchSerializer, StartupSearchSerializer,
    ProjectSearchSerializer, PostSearchSerializer
)

User = get_user_model()

class GlobalSearchAPIView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny] # Anyone can search

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', None) # Get the search query from ?q=

        if not query:
            return Response(
                {"detail": "Please provide a search query using the 'q' parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )

        search_results = {
            'users': [],
            'startups': [],
            'projects': [],
            'posts': [],
        }

        # --- Search Users ---
        users_queryset = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        ).distinct()
        search_results['users'] = UserSearchSerializer(users_queryset, many=True).data

        # --- Search Startups ---
        startups_queryset = Startup.objects.filter(
            Q(name__icontains=query) |
            Q(tagline__icontains=query) |
            Q(description__icontains=query) |
            Q(industry__name__icontains=query) # Search by industry name
        ).distinct()
        search_results['startups'] = StartupSearchSerializer(startups_queryset, many=True).data

        # --- Search Projects ---
        projects_queryset = Project.objects.filter(
            Q(title__icontains=query) |
            Q(tagline__icontains=query) |
            Q(description__icains=query) |
            Q(technologies_used__name__icontains=query) # Search by technology name
        ).distinct()
        search_results['projects'] = ProjectSearchSerializer(projects_queryset, many=True).data

        # --- Search Posts ---
        posts_queryset = Post.objects.filter(
            Q(content__icontains=query) |
            Q(owner__username__icontains=query) # Search by post content or owner username
        ).distinct()
        search_results['posts'] = PostSearchSerializer(posts_queryset, many=True).data

        return Response(search_results, status=status.HTTP_200_OK)