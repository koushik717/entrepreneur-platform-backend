# my_entrepreneur_platform/content/models.py

from django.db import models
from django.conf import settings # To refer to the User model
from django.contrib.contenttypes.fields import GenericForeignKey # For generic relations (for Like)
from django.contrib.contenttypes.models import ContentType # For generic relations (for Like)

class Post(models.Model):
    """
    Represents a user-generated post or update on the platform.
    """
    POST_TYPE_CHOICES = [
        ('TEXT', 'Text Post'),
        ('IMAGE', 'Image Post'),
        ('VIDEO', 'Video Post'),
        ('LINK', 'Link Post'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
        help_text="The user who created this post."
    )
    content = models.TextField(blank=True, null=True, help_text="Text content of the post.")
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    video = models.FileField(upload_to='post_videos/', blank=True, null=True)
    link = models.URLField(blank=True, null=True, help_text="External link associated with the post.")
    post_type = models.CharField(max_length=10, choices=POST_TYPE_CHOICES, default='TEXT')

    # Boolean to control visibility (e.g., public vs. followers only) - for future use
    is_public = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Posts"
        ordering = ['-created_at'] # Newest posts first

    def __str__(self):
        return f"Post by {self.owner.username} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class Comment(models.Model):
    """
    Represents a comment on a Post.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="The post this comment belongs to."
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="The user who wrote the comment."
    )
    content = models.TextField(help_text="Text content of the comment.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Comments"
        ordering = ['created_at'] # Oldest comments first

    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}"

class Like(models.Model):
    """
    Represents a 'like' on a Post or Comment.
    Uses GenericForeignKey for flexibility.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes',
        help_text="The user who liked the item."
    )
    # GenericForeignKey to link to either a Post or a Comment
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id') # The actual liked object

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Likes"
        # Ensure a user can only like a specific content_object once
        unique_together = ('user', 'content_type', 'object_id')
        ordering = ['-created_at']

    def __str__(self):
        return f"Like by {self.user.username} on {self.content_object}"