from django.contrib import admin
from .models import SyncQueue, SyncConflict, SyncLog, LastSync

@admin.register(SyncQueue)
class SyncQueueAdmin(admin.ModelAdmin):
    list_display = ['user', 'entity_type', 'action', 'synced', 'error_count', 'created_at']
    list_filter = ['synced', 'action', 'entity_type']
    search_fields = ['user__phone', 'entity_type']
    date_hierarchy = 'created_at'

@admin.register(SyncConflict)
class SyncConflictAdmin(admin.ModelAdmin):
    list_display = ['user', 'entity_type', 'resolution', 'created_at', 'resolved_at']
    list_filter = ['resolution', 'entity_type']
    search_fields = ['user__phone']
    date_hierarchy = 'created_at'

@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'items_uploaded', 'items_downloaded', 'conflicts_detected', 'started_at', 'duration_seconds']
    list_filter = ['status', 'started_at']
    search_fields = ['user__phone']
    date_hierarchy = 'started_at'

@admin.register(LastSync)
class LastSyncAdmin(admin.ModelAdmin):
    list_display = ['user', 'last_full_sync', 'updated_at']
    search_fields = ['user__phone']
