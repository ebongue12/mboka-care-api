from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import Consent, PatientFollower, EmergencyAccess

class ConsentSerializer(serializers.ModelSerializer):
    """Serializer pour consentement"""
    
    class Meta:
        model = Consent
        fields = [
            'id', 'patient', 'granted_to', 'level',
            'active', 'granted_at', 'valid_from', 'valid_until',
            'revoked_at', 'revoked_by', 'consent_type',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'granted_at', 'revoked_at', 'revoked_by',
            'created_at', 'updated_at'
        ]


class PatientFollowerSerializer(serializers.ModelSerializer):
    """Serializer pour follower"""
    
    class Meta:
        model = PatientFollower
        fields = [
            'id', 'patient', 'follower', 'relation_type',
            'receive_medication_alerts',
            'receive_appointment_reminders',
            'receive_emergency_alerts',
            'active', 'created_at', 'deactivated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'deactivated_at'
        ]
    
    def validate(self, attrs):
        """Valider limite 3 followers"""
        if self.instance is None:  # Création
            patient = attrs.get('patient')
            active_count = PatientFollower.objects.filter(
                patient=patient,
                active=True
            ).count()
            
            if active_count >= 3:
                raise serializers.ValidationError(
                    "Limite de 3 proches suiveurs atteinte"
                )
        
        return attrs


class EmergencyAccessSerializer(serializers.ModelSerializer):
    """Serializer pour accès d'urgence"""
    
    class Meta:
        model = EmergencyAccess
        fields = [
            'id', 'helper_name', 'helper_phone', 'helper_user',
            'patient', 'family_member',
            'qr_code_scanned', 'access_timestamp',
            'access_location', 'offline_mode',
            'synced', 'synced_at'
        ]
        read_only_fields = [
            'id', 'access_timestamp', 'synced', 'synced_at'
        ]
