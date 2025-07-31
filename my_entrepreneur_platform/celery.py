# my_entrepreneur_platform/my_entrepreneur_platform/celery.py

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_entrepreneur_platform.settings')

# Create a Celery app instance
# 'my_entrepreneur_platform' is the name of the Celery app
app = Celery('my_entrepreneur_platform')

# Load task modules from all registered Django app configs.
# This means Celery will automatically discover tasks defined in your app's tasks.py files.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps.
# Looks for a tasks.py file in each app and imports it.
app.autodiscover_tasks()

# You can add a debug task for testing purposes
@app.task(bind=True, name="debug_task")
def debug_task(self):
    print(f'Request: {self.request!r}')