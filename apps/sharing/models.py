import uuid
from django.db import models
from apps.accounts.models import User
from apps.patients.models import PatientProfile

class Consent(models.Model):
    """Consentement d'accès aux données médicales"""
    
    ACCESS_LEVEL_CHOICES = (
        ('LEVEL_1', 'Public (QR Code)'),
        ('LEVEL_2', 'Médecin autorisé'),
        ('LEVEL_3', 'Historique complet'),
    )
    
    CONSENT_TYPE_CHOICES = (
        ('EXPLICIT', 'Consentement explicite'),
        ('EMERGENCY', 'Urgence médicale'),
        ('TEMPORARY', 'Temporaire'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Propriétaire des données
    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name='consents_given'
    )
    
    # Bénéficiaire du consentement
    granted_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='consents_received'
    )
    
    # Niveau d'accès accordé
    level = models.CharField(
        max_length=10,
        choices=ACCESS_LEVEL_CHOICES,
        default='LEVEL_2'
    )
    
    # Statut
    active = models.BooleanField(default=True)
    
    # Dates
    granted_at = models.DateTimeField(auto_now_add=True)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    
    # Révocation
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consents_revoked'
    )
    
    # Type de consentement
    consent_type = models.CharField(
        max_length=20,
        choices=CONSENT_TYPE_CHOICES,
        default='EXPLICIT'
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consents'
        verbose_name = 'Consentement'
        verbose_name_plural = 'Consentements'
        unique_together = [['patient', 'granted_to', 'active']]
        indexes = [
            models.Index(fields=['patient', 'active']),
            models.Index(fields=['granted_to', 'active']),
        ]
    
    def __str__(self):
        return f"{self.patient} → {self.granted_to} (Niveau {self.level})"


class PatientFollower(models.Model):
    """
    Proches qui suivent un patient (PREMIUM uniquement)
    LIMITE : 3 followers maximum par patient
    """
    
    RELATION_TYPE_CHOICES = (
        ('FAMILY', 'Famille'),
        ('CAREGIVER', 'Garde-malade'),
        ('FRIEND', 'Ami proche'),
        ('OTHER', 'Autre'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name='followers'
    )
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following_patients'
    )
    
    # Relation type
    relation_type = models.CharField(
        max_length=20,
        choices=RELATION_TYPE_CHOICES,
        default='FAMILY'
    )
    
    # Notifications
    receive_medication_alerts = models.BooleanField(default=True)
    receive_appointment_reminders = models.BooleanField(default=True)
    receive_emergency_alerts = models.BooleanField(default=True)
    
    # Statut
    active = models.BooleanField(default=True)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'patient_followers'
        verbose_name = 'Proche Suiveur'
        verbose_name_plural = 'Proches Suiveurs'
        unique_together = [['patient', 'follower']]
        indexes = [
            models.Index(fields=['patient', 'active']),
            models.Index(fields=['follower', 'active']),
        ]
    
    def __str__(self):
        return f"{self.follower} suit {self.patient}"
    
    def save(self, *args, **kwargs):
        # Vérifier la limite de 3 followers actifs
        if not self.pk and self.active:
            active_count = PatientFollower.objects.filter(
                patient=self.patient,
                active=True
            ).count()
            
            if active_count >= 3:
                from django.core.exceptions import ValidationError
                raise ValidationError(
                    "Limite de 3 proches suiveurs atteinte"
                )
        
        super().save(*args, **kwargs)


class EmergencyAccess(models.Model):
    """
    Enregistre les accès d'urgence via mode "Je veux aider"
    Permet traçabilité et audit
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Qui aide
    helper_name = models.CharField(max_length=200, blank=True)
    helper_phone = models.CharField(max_length=20, blank=True)
    helper_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emergency_helps_provided'
    )
    
    # Qui est aidé
    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='emergency_accesses'
    )
    family_member = models.ForeignKey(
        'patients.FamilyMember',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='emergency_accesses'
    )
    
    # Métadonnées accès
    qr_code_scanned = models.CharField(max_length=500)
    access_timestamp = models.DateTimeField(auto_now_add=True)
    access_location = models.JSONField(null=True, blank=True)
    offline_mode = models.BooleanField(default=False)
    
    # Synchronisation
    synced = models.BooleanField(default=False)
    synced_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'emergency_accesses'
        verbose_name = "Accès d'Urgence"
        verbose_name_plural = "Accès d'Urgence"
        ordering = ['-access_timestamp']
        indexes = [
            models.Index(fields=['access_timestamp']),
            models.Index(fields=['synced']),
        ]
    
    def __str__(self):
        helper = self.helper_user or self.helper_name or "Anonyme"
        return f"Urgence: {helper} → {self.patient or self.family_member}"
