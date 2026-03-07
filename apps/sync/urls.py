from django.urls import path
from .views import (
    sync_upload,
    sync_download,
    resolve_conflict,
    sync_status,
    SyncLogListView,
    SyncConflictListView
)

urlpatterns = [
    # Synchronisation
    path('upload/', sync_upload, name='sync-upload'),
    path('download/', sync_download, name='sync-download'),
    path('status/', sync_status, name='sync-status'),
    
    # Conflits
    path('conflicts/', SyncConflictListView.as_view(), name='sync-conflicts'),
    path('conflicts/resolve/', resolve_conflict, name='sync-resolve-conflict'),
    
    # Logs
    path('logs/', SyncLogListView.as_view(), name='sync-logs'),
]
