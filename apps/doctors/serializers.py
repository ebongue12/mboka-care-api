from rest_framework import serializers
from .models import DoctorProfile

class DoctorProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil médecin"""
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = DoctorProfile
        fields = [
            'id', 'user', 'first_name', 'last_name', 'full_name',
            'specialization', 'license_number', 'hospital_affiliation',
            'practice_country', 'practice_city', 'practice_district',
            'practice_address', 'verified', 'verified_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'verified', 'verified_at',
            'created_at', 'updated_at'
        ]
