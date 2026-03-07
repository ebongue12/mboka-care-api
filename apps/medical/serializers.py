from rest_framework import serializers
from .models import MedicalRecord, MedicalDocument

class MedicalRecordSerializer(serializers.ModelSerializer):
    """Serializer pour dossier médical"""
    
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'patient', 'family_member', 'level',
            'title', 'description', 'record_date',
            'created_by', 'created_at', 'updated_at',
            'is_deleted'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class MedicalDocumentSerializer(serializers.ModelSerializer):
    """Serializer pour document médical"""
    
    class Meta:
        model = MedicalDocument
        fields = [
            'id', 'patient', 'family_member', 'document_type',
            'file', 'file_name', 'file_size', 'file_type',
            'title', 'description', 'document_date',
            'access_level', 'uploaded_by', 'uploaded_at',
            'synced', 'is_archived', 'is_deleted'
        ]
        read_only_fields = [
            'id', 'file_name', 'file_size', 'file_type',
            'uploaded_by', 'uploaded_at', 'synced'
        ]
    
    def create(self, validated_data):
        # Extraire les métadonnées du fichier
        file = validated_data.get('file')
        if file:
            validated_data['file_name'] = file.name
            validated_data['file_size'] = file.size
            validated_data['file_type'] = file.content_type
        
        return super().create(validated_data)
