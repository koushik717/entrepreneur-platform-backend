# my_entrepreneur_platform/content/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.contrib.contenttypes.models import ContentType

from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer, LikeSerializer


# Custom Permission: Only the owner/author of the object can modify/delete it
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user if hasattr(obj, 'owner') else obj.author == request.user


# --- Post Views ---
class PostListCreateAPIView(generics.ListCreateAPIView): # <--- THIS IS THE MISSING CLASS
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_content_type = ContentType.objects.get_for_model(Post)

        return Post.objects.all().annotate(
            likes_count=Count(
                'likes',
                filter=Q(likes__content_type=post_content_type)
            )
        ).select_related('owner').order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class PostRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        post_content_type = ContentType.objects.get_for_model(Post)

        return Post.objects.all().annotate(
            likes_count=Count(
                'likes',
                filter=Q(likes__content_type=post_content_type)
            )
        ).select_related('owner')


# --- Comment Views ---
class CommentListCreateAPIView(generics.ListCreateAPIView): # <--- THIS IS ANOTHER MISSING CLASS
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        post = get_object_or_404(Post, id=post_id)
        return Comment.objects.filter(post=post).select_related('author').order_by('created_at')

    def perform_create(self, serializer):
        post_id = self.kwargs['post_id']
        post = get_object_or_404(Post, id=post_id)
        serializer.save(author=self.request.user, post=post)

class CommentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all().select_related('author')
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]


# --- Like Views ---
class LikeCreateDeleteAPIView(generics.CreateAPIView, generics.DestroyAPIView): # This one was in your screenshot
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request.user
        content_type_model = self.kwargs.get('content_type_model')
        object_id = self.kwargs.get('object_id')

        if content_type_model not in ['post', 'comment']:
            raise generics.ValidationError("Invalid content type for liking.")

        content_type = get_object_or_404(ContentType, model=content_type_model)

        obj = get_object_or_404(
            Like,
            user=user,
            content_type=content_type,
            object_id=object_id
        )
        return obj

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)