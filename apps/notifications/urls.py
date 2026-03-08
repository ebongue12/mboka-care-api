from django.urls import path
from .views import (
    NotificationListView,
    NotificationDetailView,
    NotificationMarkReadView,
    mark_all_read,
    notification_count,
    NotificationPreferenceView,
    PushTokenCreateView,
    PushTokenListView,
    PushTokenDeleteView
)

urlpatterns = [
    # Notifications
    path('', NotificationListView.as_view(), name='notifications'),
    path('<uuid:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('<uuid:pk>/read/', NotificationMarkReadView.as_view(), name='notification-read'),
    path('mark-all-read/', mark_all_read, name='mark-all-read'),
    path('count/', notification_count, name='notification-count'),
    
    # Préférences
    path('preferences/', NotificationPreferenceView.as_view(), name='notification-preferences'),
    
    # Push tokens
    path('tokens/', PushTokenCreateView.as_view(), name='push-token-create'),
    path('tokens/list/', PushTokenListView.as_view(), name='push-token-list'),
    path('tokens/<uuid:pk>/', PushTokenDeleteView.as_view(), name='push-token-delete'),
]
