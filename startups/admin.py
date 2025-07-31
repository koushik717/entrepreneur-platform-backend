# my_entrepreneur_platform/startups/admin.py

from django.contrib import admin
from .models import Industry, Startup

# Register your models here
admin.site.register(Industry)
admin.site.register(Startup)