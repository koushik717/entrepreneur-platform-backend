# my_entrepreneur_platform/notifications/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer, NotificationMarkReadSerializer


# --- Your existing notification_test_view ---
@login_required
def notification_test_view(request):
    return render(request, 'notification_test.html', {})
# --- End existing notification_test_view ---


# --- New API Views for Notifications ---

class NotificationListAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = self.request.user.notifications.all()
        is_read_param = self.request.query_params.get('is_read', None)
        if is_read_param is not None:
            is_read = is_read_param.lower() == 'true'
            queryset = queryset.filter(is_read=is_read)
        return queryset.order_by('-timestamp')

class NotificationMarkReadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = NotificationMarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        notification_ids = serializer.validated_data.get('notification_ids', [])
        mark_all = serializer.validated_data.get('mark_all', False)

        user_notifications = request.user.notifications.all()
        count = 0

        if mark_all:
            updated_count = user_notifications.filter(is_read=False).update(is_read=True)
            count += updated_count
        elif notification_ids:
            updated_count = user_notifications.filter(id__in=notification_ids, is_read=False).update(is_read=True)
            count += updated_count
        else:
            return Response(
                {"detail": "Please provide 'notification_ids' or set 'mark_all' to true."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": f"{count} notifications marked as read."},
            status=status.HTTP_200_OK
        )