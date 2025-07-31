# my_entrepreneur_platform/users/admin.py

from django.contrib import admin
from .models import UserProfile

# Register your UserProfile model here
admin.site.register(UserProfile)