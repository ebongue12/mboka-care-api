import uuid
from django.db import models
from apps.accounts.models import User
from apps.patients.models import PatientProfile, FamilyMember

class MedicalRecord(models.Model):
    """Dossier médical - Enregistrement médical"""
    
    ACCESS_LEVEL_CHOICES = (
        ('LEVEL_1', 'Public (QR Code)'),
        ('LEVEL_2', 'Médecin autorisé'),
        ('LEVEL_3', 'Historique complet'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Propriétaire (patient OU membre famille)
    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='medical_records'
    )
    family_member = models.ForeignKey(
        FamilyMember,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='medical_records'
    )
    
    # Niveau d'accès
    level = models.CharField(
        max_length=10,
        choices=ACCESS_LEVEL_CHOICES,
        default='LEVEL_3'
    )
    
    # Contenu
    title = models.CharField(max_length=200)
    description = models.TextField()
    record_date = models.DateField()
    
    # Traçabilité
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_records'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Soft delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'medical_records'
        verbose_name = 'Dossier Médical'
        verbose_name_plural = 'Dossiers Médicaux'
        ordering = ['-record_date']
    
    def __str__(self):
        owner = self.patient or self.family_member
        return f"{self.title} - {owner}"


class MedicalDocument(models.Model):
    """Documents médicaux (analyses, ordonnances, etc.) - ILLIMITÉ"""
    
    DOCUMENT_TYPE_CHOICES = (
        ('ANALYSIS', 'Analyse médicale'),
        ('PRESCRIPTION', 'Ordonnance'),
        ('XRAY', 'Radiographie'),
        ('SCAN', 'Scanner'),
        ('MRI', 'IRM'),
        ('REPORT', 'Compte-rendu'),
        ('VACCINATION', 'Carnet de vaccination'),
        ('OTHER', 'Autre'),
    )
    
    ACCESS_LEVEL_CHOICES = MedicalRecord.ACCESS_LEVEL_CHOICES
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Propriétaire
    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents'
    )
    family_member = models.ForeignKey(
        FamilyMember,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents'
    )
    
    # Type de document
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        default='OTHER'
    )
    
    # Fichier
    file = models.FileField(upload_to='medical_documents/%Y/%m/')
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    file_type = models.CharField(max_length=50)
    
    # Métadonnées
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    document_date = models.DateField()
    
    # Niveau d'accès
    access_level = models.CharField(
        max_length=10,
        choices=ACCESS_LEVEL_CHOICES,
        default='LEVEL_3'
    )
    
    # Upload
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Synchronisation offline
    synced = models.BooleanField(default=False)
    synced_at = models.DateTimeField(null=True, blank=True)
    
    # Archivage
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    
    # Soft delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'medical_documents'
        verbose_name = 'Document Médical'
        verbose_name_plural = 'Documents Médicaux'
        ordering = ['-document_date']
    
    def __str__(self):
        return f"{self.title} ({self.get_document_type_display()})"
