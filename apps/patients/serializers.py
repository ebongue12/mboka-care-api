from rest_framework import serializers
from .models import PatientProfile, FamilyMember

class PatientProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil patient"""
    age = serializers.ReadOnlyField()
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = PatientProfile
        fields = [
            'id', 'user', 'first_name', 'last_name', 
            'date_of_birth', 'age', 'full_name',
            'place_of_birth', 'country_of_birth',
            'country_residence', 'city_residence', 'district_residence',
            'blood_group', 'chronic_conditions', 'allergies',
            'emergency_notes', 'emergency_contact_name', 'emergency_contact_phone',
            'account_type', 'qr_code_image',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class FamilyMemberSerializer(serializers.ModelSerializer):
    """Serializer pour membre de famille"""
    age = serializers.ReadOnlyField()
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = FamilyMember
        fields = [
            'id', 'family_chief', 'first_name', 'last_name',
            'date_of_birth', 'age', 'full_name',
            'place_of_birth', 'country_of_birth',
            'country_residence', 'city_residence', 'district_residence',
            'relation', 'blood_group', 'chronic_conditions', 'allergies',
            'emergency_notes', 'qr_code_image', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'family_chief', 'created_at', 'updated_at']
