# my_entrepreneur_platform/notifications/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# This view will serve the notification_test.html template
@login_required # Only logged-in users can access this page
def notification_test_view(request):
    # The template will use {{ request.user.id }} to get the current user's ID
    return render(request, 'notification_test.html', {})