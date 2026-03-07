import uuid
from django.db import models
from apps.accounts.models import User
from apps.patients.models import PatientProfile
from apps.reminders.models import Reminder

class Notification(models.Model):
    """Notifications système"""
    
    NOTIFICATION_TYPE_CHOICES = (
        ('MEDICATION_TAKEN', 'Médicament pris'),
        ('MEDICATION_MISSED', 'Médicament manqué'),
        ('APPOINTMENT_REMINDER', 'Rappel rendez-vous'),
        ('CONSENT_REQUEST', "Demande d'accès"),
        ('CONSENT_GRANTED', 'Accès accordé'),
        ('CONSENT_REVOKED', 'Accès révoqué'),
        ('DOCUMENT_ADDED', 'Document ajouté'),
        ('EMERGENCY_ACCESS', "Accès d'urgence"),
        ('INFO', 'Information'),
        ('SYSTEM', 'Système'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Destinataire
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    # Type de notification
    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPE_CHOICES
    )
    
    # Contenu
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Liens vers ressources (optionnel)
    related_patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    related_reminder = models.ForeignKey(
        Reminder,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    # Données supplémentaires (JSON)
    extra_data = models.JSONField(default=dict, blank=True)
    
    # Statut
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    delivered = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Push notification
    push_sent = models.BooleanField(default=False)
    push_sent_at = models.DateTimeField(null=True, blank=True)
    push_token = models.CharField(max_length=500, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.recipient} - {self.title}"


class NotificationPreference(models.Model):
    """Préférences de notifications par utilisateur"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Canaux de notification
    push_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=False)
    sms_enabled = models.BooleanField(default=False)
    
    # Types de notifications activées
    medication_reminders = models.BooleanField(default=True)
    appointment_reminders = models.BooleanField(default=True)
    follower_alerts = models.BooleanField(default=True)
    consent_requests = models.BooleanField(default=True)
    document_updates = models.BooleanField(default=True)
    system_updates = models.BooleanField(default=False)
    
    # Plages horaires (optionnel)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
        verbose_name = 'Préférence de Notification'
        verbose_name_plural = 'Préférences de Notifications'
    
    def __str__(self):
        return f"Préférences de {self.user}"


class PushToken(models.Model):
    """Tokens FCM pour push notifications"""
    
    PLATFORM_CHOICES = (
        ('ANDROID', 'Android'),
        ('IOS', 'iOS'),
        ('WEB', 'Web'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='push_tokens'
    )
    
    token = models.CharField(max_length=500, unique=True)
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES)
    
    # Statut
    is_active = models.BooleanField(default=True)
    
    # Device info
    device_name = models.CharField(max_length=200, blank=True)
    device_id = models.CharField(max_length=200, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'push_tokens'
        verbose_name = 'Token Push'
        verbose_name_plural = 'Tokens Push'
    
    def __str__(self):
        return f"{self.user} - {self.platform}"
