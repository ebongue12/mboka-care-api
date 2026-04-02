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


ALLOWED_DOCUMENT_TYPES = {
    'application/pdf',
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/webp',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
}

MAX_DOCUMENT_SIZE_MB = 20


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
        file = validated_data.get('file')
        if file:
            if file.content_type not in ALLOWED_DOCUMENT_TYPES:
                raise serializers.ValidationError({
                    'file': (
                        f"Type de fichier non autorisé ({file.content_type}). "
                        "Formats acceptés : PDF, images (JPEG, PNG, WebP), Word."
                    )
                })
            if file.size > MAX_DOCUMENT_SIZE_MB * 1024 * 1024:
                raise serializers.ValidationError({
                    'file': f"Fichier trop volumineux (max {MAX_DOCUMENT_SIZE_MB} Mo)."
                })
            validated_data['file_name'] = file.name
            validated_data['file_size'] = file.size
            validated_data['file_type'] = file.content_type
        return super().create(validated_data)
