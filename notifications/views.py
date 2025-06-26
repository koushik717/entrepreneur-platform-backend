# my_entrepreneur_platform/notifications/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required # Keep this for your test view

from rest_framework import generics, permissions, status # NEW: For API views
from rest_framework.response import Response # NEW: For sending API responses
from rest_framework.views import APIView # NEW: For custom API logic (like mark as read)

from .models import Notification # Your Notification model
from .serializers import NotificationSerializer, NotificationMarkReadSerializer # Your new serializers


# --- Your existing notification_test_view (keep this as is) ---
@login_required
def notification_test_view(request):
    return render(request, 'notification_test.html', {})
# --- End existing notification_test_view ---


# --- New API Views for Notifications (Navya's Part) ---

# This view handles listing a user's notifications
class NotificationListAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer # Use the serializer you just made
    permission_classes = [permissions.IsAuthenticated] # Only logged-in users can see their notifications

    def get_queryset(self):
        # IMPORTANT: Only return notifications that belong to the currently logged-in user
        queryset = self.request.user.notifications.all()

        # Allow filtering by 'is_read' status via a query parameter (e.g., /api/notifications/?is_read=true)
        is_read_param = self.request.query_params.get('is_read', None)
        if is_read_param is not None:
            # Convert 'true'/'false' string from URL to actual boolean
            is_read = is_read_param.lower() == 'true'
            queryset = queryset.filter(is_read=is_read)

        # Order notifications by newest first (most recent at the top)
        return queryset.order_by('-timestamp')

# This view handles marking notifications as read
class NotificationMarkReadAPIView(APIView): # Using APIView for custom POST logic
    permission_classes = [permissions.IsAuthenticated] # Only logged-in users can mark their notifications

    def post(self, request, *args, **kwargs):
        # Use the NotificationMarkReadSerializer to validate the incoming data
        serializer = NotificationMarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True) # If data is bad, it will raise an error

        # Get data from the validated request (either list of IDs or 'mark_all' flag)
        notification_ids = serializer.validated_data.get('notification_ids', [])
        mark_all = serializer.validated_data.get('mark_all', False)

        # Get all notifications for the current user
        user_notifications = request.user.notifications.all()
        count = 0 # To count how many notifications were marked

        if mark_all:
            # If 'mark_all' is true, update all unread notifications for this user
            updated_count = user_notifications.filter(is_read=False).update(is_read=True)
            count += updated_count
        elif notification_ids:
            # If specific IDs are provided, mark those unread notifications as read
            # Ensure they belong to the user and are currently unread
            updated_count = user_notifications.filter(id__in=notification_ids, is_read=False).update(is_read=True)
            count += updated_count
        else:
            # If neither IDs nor mark_all is provided, it's a bad request
            return Response(
                {"detail": "Please provide 'notification_ids' or set 'mark_all' to true."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Send a success response back to the frontend
        return Response(
            {"message": f"{count} notifications marked as read."},
            status=status.HTTP_200_OK
        )