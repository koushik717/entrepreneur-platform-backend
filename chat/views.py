# my_entrepreneur_platform/chat/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required # New import!

@login_required # <--- This decorator ensures only logged-in users can access this page
def chat_test_view(request):
    # This renders the chat_test.html template
    return render(request, 'chat_test.html', {})