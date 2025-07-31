# my_entrepreneur_platform/my_entrepreneur_platform/urls.py

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

# Import views from your chat application
from chat.views import (
    chat_test_view,
    ChatRoomListCreateAPIView,
    ChatRoomDetailAPIView,
    MessageListAPIView,
    MessageCreateAPIView
)

# Import views from your notifications application
from notifications.views import (
    notification_test_view,
    NotificationListAPIView,
    NotificationMarkReadAPIView
)

# Import views from your users application
from users.views import (
    UserProfileRetrieveUpdateAPIView,
    UserProfilePublicDetailAPIView
)

# Import views from your startups application
from startups.views import (
    IndustryListCreateAPIView, IndustryDetailAPIView,
    StartupListCreateAPIView, StartupRetrieveUpdateDestroyAPIView
)

# Import views from your projects application
from projects.views import (
    TechnologyListCreateAPIView, TechnologyDetailAPIView,
    ProjectListCreateAPIView, ProjectRetrieveUpdateDestroyAPIView
)

# Import views from your social application
from social.views import (
    FollowCreateDeleteAPIView,
    FollowingListAPIView,
    FollowersListAPIView
)

# Import views from your search application
from search.views import GlobalSearchAPIView

# Import views from your content application # <--- UNCOMMENTED THIS IMPORT BLOCK
from content.views import (
    PostListCreateAPIView, PostRetrieveUpdateDestroyAPIView,
    CommentListCreateAPIView, CommentRetrieveUpdateDestroyAPIView,
    LikeCreateDeleteAPIView
)


# Define a very simple view function for the root path
def dummy_root_view(request):
    return HttpResponse("OK", status=200)


urlpatterns = [
    path('', dummy_root_view, name='root_dummy_view'),

    path('admin/', admin.site.urls),

    # --- 2FA URLs (TEMPORARILY COMMENTED OUT DUE TO COMPATIBILITY ISSUES) ---
    # path('2fa/', include(('two_factor.urls', 'two_factor'), namespace='two_factor')),
    # --- End 2FA ---

    # --- Existing Django Auth URLs (keep this) ---
    path('accounts/', include('django.contrib.auth.urls')),
    # --- End Existing ---

    # URL for your chat test page
    path('chat/test/', chat_test_view, name='chat_test'),

    # API URLs for Chat
    path('api/chat/rooms/', ChatRoomListCreateAPIView.as_view(), name='chat-room-list-create'),
    path('api/chat/rooms/<int:pk>/', ChatRoomDetailAPIView.as_view(), name='chat-room-detail'),
    path('api/chat/rooms/<int:room_id>/messages/', MessageListAPIView.as_view(), name='message-list'),
    path('api/chat/rooms/<int:room_id>/messages/create/', MessageListAPIView.as_view(), name='message-create'),

    # URL for notification test page
    path('notifications/test/', notification_test_view, name='notification_test'),

    # API URLs for Notifications
    path('api/notifications/', NotificationListAPIView.as_view(), name='notification-list'),
    path('api/notifications/mark_read/', NotificationMarkReadAPIView.as_view(), name='notification-mark-read'),

    # API URLs for User Profiles
    path('api/me/profile/', UserProfileRetrieveUpdateAPIView.as_view(), name='my-profile-retrieve-update'),
    path('api/profiles/<int:user_id>/', UserProfilePublicDetailAPIView.as_view(), name='public-profile-detail'),

    # API URLs for Startup Profiles
    # Industries
    path('api/industries/', IndustryListCreateAPIView.as_view(), name='industry-list-create'),
    path('api/industries/<int:pk>/', IndustryDetailAPIView.as_view(), name='industry-detail'),
    # Startups
    path('api/startups/', StartupListCreateAPIView.as_view(), name='startup-list-create'),
    path('api/startups/<int:pk>/', StartupRetrieveUpdateDestroyAPIView.as_view(), name='startup-retrieve-update-destroy'),

    # API URLs for Project Pages
    # Technologies
    path('api/technologies/', TechnologyListCreateAPIView.as_view(), name='technology-list-create'),
    path('api/technologies/<int:pk>/', TechnologyDetailAPIView.as_view(), name='technology-detail'),
    # Projects
    path('api/projects/', ProjectListCreateAPIView.as_view(), name='project-list-create'),
    path('api/projects/<int:pk>/', ProjectRetrieveUpdateDestroyAPIView.as_view(), name='project-retrieve-update-destroy'),

    # --- API URLs for Content/Posts System (UNCOMMENTED) ---
    # Posts
    path('api/posts/', PostListCreateAPIView.as_view(), name='post-list-create'),
    path('api/posts/<int:pk>/', PostRetrieveUpdateDestroyAPIView.as_view(), name='post-retrieve-update-destroy'),
    # Comments
    path('api/posts/<int:post_id>/comments/', CommentListCreateAPIView.as_view(), name='comment-list-create'),
    path('api/posts/<int:post_id>/comments/<int:pk>/', CommentRetrieveUpdateDestroyAPIView.as_view(), name='comment-retrieve-update-destroy'),
    # Likes
    path('api/likes/<str:content_type_model>/<int:object_id>/', LikeCreateDeleteAPIView.as_view(), name='like-create-delete'),
    # --- End API URLs ---

    # API URLs for Follow/Unfollow System
    # Create/Delete Follow
    path('api/follows/<str:content_type_model>/<int:object_id>/', FollowCreateDeleteAPIView.as_view(), name='follow-create-delete'),
    # List Following (who a user follows)
    path('api/users/<int:user_id>/following/', FollowingListAPIView.as_view(), name='user-following-list'),
    # List Followers (who follows a user)
    path('api/users/<int:user_id>/followers/', FollowersListAPIView.as_view(), name='user-followers-list'),
    
    # NEW API URL for Global Search
    path('api/search/', GlobalSearchAPIView.as_view(), name='global-search'),
]