from rest_framework import serializers
from .models import Notification, NotificationPreference, PushToken

class NotificationSerializer(serializers.ModelSerializer):
    """Serializer pour notification"""
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'notification_type',
            'title', 'message',
            'related_patient', 'related_reminder', 'extra_data',
            'read', 'read_at', 'delivered', 'delivered_at',
            'push_sent', 'push_sent_at',
            'created_at'
        ]
        read_only_fields = [
            'id', 'recipient', 'delivered', 'delivered_at',
            'push_sent', 'push_sent_at', 'created_at'
        ]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer pour préférences"""
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'user',
            'push_enabled', 'email_enabled', 'sms_enabled',
            'medication_reminders', 'appointment_reminders',
            'follower_alerts', 'consent_requests',
            'document_updates', 'system_updates',
            'quiet_hours_start', 'quiet_hours_end',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class PushTokenSerializer(serializers.ModelSerializer):
    """Serializer pour token push"""
    
    class Meta:
        model = PushToken
        fields = [
            'id', 'user', 'token', 'platform',
            'is_active', 'device_name', 'device_id',
            'created_at', 'updated_at', 'last_used_at'
        ]
        read_only_fields = [
            'id', 'user', 'created_at', 'updated_at', 'last_used_at'
        ]
