from django.urls import path
from .views import (
    ConsentGivenListView,
    ConsentReceivedListView,
    ConsentCreateView,
    ConsentRevokeView,
    FollowerListCreateView,
    FollowerDetailView,
    EmergencyAccessCreateView,
    EmergencyAccessListView
)

urlpatterns = [
    # Consentements
    path('consents/given/', ConsentGivenListView.as_view(), name='consents-given'),
    path('consents/received/', ConsentReceivedListView.as_view(), name='consents-received'),
    path('consents/', ConsentCreateView.as_view(), name='consent-create'),
    path('consents/<uuid:pk>/revoke/', ConsentRevokeView.as_view(), name='consent-revoke'),
    
    # Followers
    path('followers/', FollowerListCreateView.as_view(), name='followers'),
    path('followers/<uuid:pk>/', FollowerDetailView.as_view(), name='follower-detail'),
    
    # Accès d'urgence
    path('emergency/', EmergencyAccessCreateView.as_view(), name='emergency-access'),
    path('emergency/history/', EmergencyAccessListView.as_view(), name='emergency-history'),
]
