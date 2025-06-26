# my_entrepreneur_platform/chat/admin.py

from django.contrib import admin
from .models import ChatRoom, Message

# Register your models here so they show up in the Django admin panel
admin.site.register(ChatRoom)
admin.site.register(Message)