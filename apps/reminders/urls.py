from django.urls import path
from .views import (
    ReminderListCreateView,
    ReminderDetailView,
    ReminderDeactivateView,
    ReminderLogListCreateView,
    ReminderLogDetailView,
    reminder_stats
)

urlpatterns = [
    # Rappels
    path('', ReminderListCreateView.as_view(), name='reminders'),
    path('<uuid:pk>/', ReminderDetailView.as_view(), name='reminder-detail'),
    path('<uuid:pk>/deactivate/', ReminderDeactivateView.as_view(), name='reminder-deactivate'),
    
    # Logs
    path('logs/', ReminderLogListCreateView.as_view(), name='reminder-logs'),
    path('logs/<uuid:pk>/', ReminderLogDetailView.as_view(), name='reminder-log-detail'),
    
    # Stats
    path('stats/', reminder_stats, name='reminder-stats'),
]
