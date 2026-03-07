from rest_framework import serializers
from .models import SyncQueue, SyncConflict, SyncLog, LastSync

class SyncQueueSerializer(serializers.ModelSerializer):
    """Serializer pour queue de sync"""
    
    class Meta:
        model = SyncQueue
        fields = [
            'id', 'user', 'entity_type', 'entity_id',
            'action', 'data', 'synced', 'synced_at',
            'error_count', 'last_error',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'synced', 'synced_at',
            'error_count', 'last_error', 'created_at', 'updated_at'
        ]


class SyncConflictSerializer(serializers.ModelSerializer):
    """Serializer pour conflit"""
    
    class Meta:
        model = SyncConflict
        fields = [
            'id', 'user', 'entity_type', 'entity_id',
            'client_version', 'server_version',
            'client_updated_at', 'server_updated_at',
            'resolution', 'resolved_version',
            'created_at', 'resolved_at'
        ]
        read_only_fields = [
            'id', 'user', 'created_at', 'resolved_at'
        ]


class SyncLogSerializer(serializers.ModelSerializer):
    """Serializer pour log de sync"""
    
    class Meta:
        model = SyncLog
        fields = [
            'id', 'user', 'items_uploaded', 'items_downloaded',
            'conflicts_detected', 'errors_count',
            'status', 'details', 'error_details',
            'started_at', 'completed_at', 'duration_seconds'
        ]
        read_only_fields = ['id', 'user', 'started_at']


class LastSyncSerializer(serializers.ModelSerializer):
    """Serializer pour dernière sync"""
    
    class Meta:
        model = LastSync
        fields = [
            'id', 'user',
            'reminders_last_sync', 'documents_last_sync',
            'medical_records_last_sync', 'consents_last_sync',
            'last_full_sync',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class SyncUploadSerializer(serializers.Serializer):
    """Serializer pour upload de queue"""
    
    queue = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False
    )


class SyncDownloadSerializer(serializers.Serializer):
    """Serializer pour download de changements"""
    
    since = serializers.DateTimeField(required=False, allow_null=True)
    entity_types = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
