# my_entrepreneur_platform/users/models.py

from django.db import models
from django.conf import settings # To refer to the User model configured in settings.py
from django.db.models.signals import post_save # For automatic profile creation
from django.dispatch import receiver # For connecting the signal

class UserProfile(models.Model):
    """
    Stores additional profile information for a user beyond Django's built-in User model.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    # You might add fields here for specific roles if they are common enough
    # Example: is_entrepreneur = models.BooleanField(default=False)
    #          is_investor = models.BooleanField(default=False)
    #          is_mentor = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} Profile'

# Signal to automatically create a UserProfile when a new User is created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# Signal to automatically save the UserProfile when the User is saved
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    # This handles cases where user is updated, ensuring profile is also saved
    if hasattr(instance, 'userprofile'): # Check if userprofile exists to prevent error on first save
        instance.userprofile.save()