# my_entrepreneur_platform/projects/admin.py

from django.contrib import admin
from .models import Technology, Project

# Register your models here
admin.site.register(Technology)
admin.site.register(Project)