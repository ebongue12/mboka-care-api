import uuid
from django.db import models
from apps.accounts.models import User
from apps.patients.models import PatientProfile, FamilyMember

class Reminder(models.Model):
    """Rappels médicaux - Fonctionne HORS CONNEXION"""
    
    REMINDER_TYPE_CHOICES = (
        ('MEDICATION', 'Médicament'),
        ('APPOINTMENT', 'Rendez-vous'),
        ('EXAM', 'Examen médical'),
        ('VACCINATION', 'Vaccination'),
        ('OTHER', 'Autre'),
    )
    
    FREQUENCY_CHOICES = (
        ('DAILY', 'Quotidien'),
        ('WEEKLY', 'Hebdomadaire'),
        ('MONTHLY', 'Mensuel'),
        ('CUSTOM', 'Personnalisé'),
        ('ONE_TIME', 'Une fois'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Propriétaire
    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reminders'
    )
    family_member = models.ForeignKey(
        FamilyMember,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reminders'
    )
    
    # Type de rappel
    reminder_type = models.CharField(
        max_length=20,
        choices=REMINDER_TYPE_CHOICES,
        default='MEDICATION'
    )
    
    # Détails
    title = models.CharField(max_length=200)
    medication_name = models.CharField(max_length=200, blank=True)
    dosage = models.CharField(max_length=100, blank=True)
    instructions = models.TextField(blank=True)
    
    # Fréquence
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='DAILY'
    )
    
    # Horaires (JSON pour flexibilité)
    # Exemple: ["08:00", "14:00", "20:00"]
    time_slots = models.JSONField(default=list)
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    # Statut
    is_active = models.BooleanField(default=True)
    
    # Mode local (offline-first)
    local_only = models.BooleanField(default=False)
    
    # Notifications
    notify_patient = models.BooleanField(default=True)
    notify_followers = models.BooleanField(default=False)  # Premium
    notify_doctor = models.BooleanField(default=False)  # Premium
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    
    # Synchronisation
    synced = models.BooleanField(default=False)
    synced_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'reminders'
        verbose_name = 'Rappel'
        verbose_name_plural = 'Rappels'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_frequency_display()}"


class ReminderLog(models.Model):
    """Historique des prises de médicaments"""
    
    STATUS_CHOICES = (
        ('PENDING', 'En attente'),
        ('TAKEN', 'Pris'),
        ('MISSED', 'Manqué'),
        ('DELAYED', 'Retardé'),
        ('SKIPPED', 'Sauté volontairement'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Rappel concerné
    reminder = models.ForeignKey(
        Reminder,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    
    # Date et heure prévues
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    scheduled_datetime = models.DateTimeField()
    
    # Confirmation prise
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    # Confirmation
    confirmed_at = models.DateTimeField(null=True, blank=True)
    confirmed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Notifications envoyées
    notification_sent_to_patient = models.BooleanField(default=False)
    notification_sent_to_followers = models.BooleanField(default=False)
    notification_sent_to_doctor = models.BooleanField(default=False)
    
    # Synchronisation offline
    synced = models.BooleanField(default=False)
    synced_at = models.DateTimeField(null=True, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reminder_logs'
        verbose_name = 'Log de Rappel'
        verbose_name_plural = 'Logs de Rappels'
        ordering = ['-scheduled_datetime']
        indexes = [
            models.Index(fields=['reminder', 'scheduled_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.reminder.title} - {self.scheduled_datetime} - {self.get_status_display()}"
