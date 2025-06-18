# my_entrepreneur_platform/my_entrepreneur_platform/urls.py

from django.contrib import admin
from django.urls import path, include
from chat.views import chat_test_view # <--- ADD THIS IMPORT

urlpatterns = [
    path('admin/', admin.site.urls),
    # You'll add other app URLs here later, e.g., path('api/users/', include('users.urls')),

    path('chat/test/', chat_test_view, name='chat_test'), # <--- ADD THIS LINE
]