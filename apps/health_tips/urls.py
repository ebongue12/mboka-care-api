from django.urls import path
from .views import (
    PatientHealthTipsView,
    StaffHealthTipsView,
    StaffHealthTipDetailView,
    mark_tip_viewed,
)

urlpatterns = [
    # Patient
    path('feed/', PatientHealthTipsView.as_view(), name='health-tips-feed'),
    path('<uuid:tip_id>/view/', mark_tip_viewed, name='health-tip-viewed'),

    # Personnel de santé
    path('staff/', StaffHealthTipsView.as_view(), name='staff-health-tips'),
    path('staff/<uuid:pk>/', StaffHealthTipDetailView.as_view(), name='staff-health-tip-detail'),
]
