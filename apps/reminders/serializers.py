from rest_framework import serializers
from .models import Reminder, ReminderLog

class ReminderSerializer(serializers.ModelSerializer):
    """Serializer pour rappel"""
    
    class Meta:
        model = Reminder
        fields = [
            'id', 'patient', 'family_member', 'reminder_type',
            'title', 'medication_name', 'dosage', 'instructions',
            'frequency', 'time_slots', 'start_date', 'end_date',
            'is_active', 'local_only',
            'notify_patient', 'notify_followers', 'notify_doctor',
            'created_by', 'created_at', 'updated_at',
            'synced', 'synced_at'
        ]
        read_only_fields = [
            'id', 'created_by', 'created_at', 'updated_at',
            'synced', 'synced_at'
        ]


class ReminderLogSerializer(serializers.ModelSerializer):
    """Serializer pour log de rappel"""
    
    class Meta:
        model = ReminderLog
        fields = [
            'id', 'reminder', 'scheduled_date', 'scheduled_time',
            'scheduled_datetime', 'status', 'confirmed_at',
            'confirmed_by', 'notes',
            'notification_sent_to_patient',
            'notification_sent_to_followers',
            'notification_sent_to_doctor',
            'synced', 'synced_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'confirmed_by', 'created_at', 'updated_at',
            'synced', 'synced_at'
        ]
    
    def create(self, validated_data):
        # Construire scheduled_datetime depuis date + time
        from datetime import datetime, time as dt_time
        scheduled_date = validated_data.get('scheduled_date')
        scheduled_time = validated_data.get('scheduled_time')
        
        if scheduled_date and scheduled_time:
            validated_data['scheduled_datetime'] = datetime.combine(
                scheduled_date,
                scheduled_time
            )
        
        return super().create(validated_data)


class ReminderStatsSerializer(serializers.Serializer):
    """Serializer pour statistiques d'observance"""
    
    reminder = ReminderSerializer(read_only=True)
    period = serializers.CharField()
    total_scheduled = serializers.IntegerField()
    taken = serializers.IntegerField()
    missed = serializers.IntegerField()
    delayed = serializers.IntegerField()
    skipped = serializers.IntegerField()
    adherence_rate = serializers.FloatField()
    chart_data = serializers.ListField()
