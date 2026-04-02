from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse
from django.db import models
from .models import MedicalRecord, MedicalDocument
from .serializers import MedicalRecordSerializer, MedicalDocumentSerializer

class MedicalRecordListCreateView(generics.ListCreateAPIView):
    """Liste et création de dossiers médicaux"""
    permission_classes = [IsAuthenticated]
    serializer_class = MedicalRecordSerializer

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'patient_profile'):
            # Patient voit ses propres dossiers + ceux de sa famille
            return MedicalRecord.objects.filter(
                models.Q(patient=user.patient_profile) |
                models.Q(family_member__family_chief=user.patient_profile),
                is_deleted=False
            )
        return MedicalRecord.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        patient = getattr(user, 'patient_profile', None)
        serializer.save(created_by=user, patient=patient)


class MedicalRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail, modification, suppression dossier médical"""
    permission_classes = [IsAuthenticated]
    serializer_class = MedicalRecordSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'patient_profile'):
            return MedicalRecord.objects.filter(
                models.Q(patient=user.patient_profile) |
                models.Q(family_member__family_chief=user.patient_profile),
                is_deleted=False
            )
        return MedicalRecord.objects.none()
    
    def perform_destroy(self, instance):
        # Soft delete
        from django.utils import timezone
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()


class MedicalDocumentListCreateView(generics.ListCreateAPIView):
    """Liste et upload de documents médicaux"""
    permission_classes = [IsAuthenticated]
    serializer_class = MedicalDocumentSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'patient_profile'):
            return MedicalDocument.objects.filter(
                models.Q(patient=user.patient_profile) |
                models.Q(family_member__family_chief=user.patient_profile),
                is_deleted=False
            )
        return MedicalDocument.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        patient = getattr(user, 'patient_profile', None)
        serializer.save(uploaded_by=user, patient=patient)


class MedicalDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail, modification, suppression document"""
    permission_classes = [IsAuthenticated]
    serializer_class = MedicalDocumentSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'patient_profile'):
            return MedicalDocument.objects.filter(
                models.Q(patient=user.patient_profile) |
                models.Q(family_member__family_chief=user.patient_profile),
                is_deleted=False
            )
        return MedicalDocument.objects.none()
    
    def perform_destroy(self, instance):
        # Soft delete
        from django.utils import timezone
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()


class MedicalDocumentDownloadView(generics.RetrieveAPIView):
    """Téléchargement de document"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'patient_profile'):
            return MedicalDocument.objects.filter(
                models.Q(patient=user.patient_profile) |
                models.Q(family_member__family_chief=user.patient_profile),
                is_deleted=False
            )
        return MedicalDocument.objects.none()
    
    def retrieve(self, request, *args, **kwargs):
        document = self.get_object()
        return FileResponse(
            document.file.open('rb'),
            as_attachment=True,
            filename=document.file_name
        )
