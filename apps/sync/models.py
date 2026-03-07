import uuid
from django.db import models
from apps.accounts.models import User

class SyncQueue(models.Model):
    """
    File d'attente des modifications à synchroniser
    Gère les créations/modifications offline
    """
    
    ACTION_CHOICES = (
        ('CREATE', 'Création'),
        ('UPDATE', 'Mise à jour'),
        ('DELETE', 'Suppression'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Utilisateur
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sync_queue'
    )
    
    # Entité modifiée
    entity_type = models.CharField(max_length=50)  # 'Reminder', 'Document', etc.
    entity_id = models.UUIDField()  # ID de l'entité
    
    # Action
    action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES
    )
    
    # Données (JSON du changement)
    data = models.JSONField()
    
    # Statut sync
    synced = models.BooleanField(default=False)
    synced_at = models.DateTimeField(null=True, blank=True)
    
    # Erreurs
    error_count = models.IntegerField(default=0)
    last_error = models.TextField(blank=True)
    max_retries = models.IntegerField(default=3)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sync_queue'
        verbose_name = 'File de Synchronisation'
        verbose_name_plural = 'Files de Synchronisation'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['user', 'synced']),
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.entity_type} {self.action} - {self.user}"


class SyncConflict(models.Model):
    """
    Conflits de synchronisation à résoudre
    """
    
    RESOLUTION_CHOICES = (
        ('PENDING', 'En attente'),
        ('USE_SERVER', 'Version serveur'),
        ('USE_CLIENT', 'Version client'),
        ('MERGED', 'Fusionné'),
        ('CANCELLED', 'Annulé'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Utilisateur concerné
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sync_conflicts'
    )
    
    # Entité en conflit
    entity_type = models.CharField(max_length=50)
    entity_id = models.UUIDField()
    
    # Versions en conflit
    client_version = models.JSONField()  # Données client
    server_version = models.JSONField()  # Données serveur
    
    # Timestamps
    client_updated_at = models.DateTimeField()
    server_updated_at = models.DateTimeField()
    
    # Résolution
    resolution = models.CharField(
        max_length=20,
        choices=RESOLUTION_CHOICES,
        default='PENDING'
    )
    resolved_version = models.JSONField(null=True, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'sync_conflicts'
        verbose_name = 'Conflit de Synchronisation'
        verbose_name_plural = 'Conflits de Synchronisation'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'resolution']),
            models.Index(fields=['entity_type', 'entity_id']),
        ]
    
    def __str__(self):
        return f"Conflit {self.entity_type} - {self.user}"


class SyncLog(models.Model):
    """
    Historique des synchronisations
    """
    
    STATUS_CHOICES = (
        ('SUCCESS', 'Réussi'),
        ('PARTIAL', 'Partiel'),
        ('FAILED', 'Échoué'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Utilisateur
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sync_logs'
    )
    
    # Statistiques
    items_uploaded = models.IntegerField(default=0)
    items_downloaded = models.IntegerField(default=0)
    conflicts_detected = models.IntegerField(default=0)
    errors_count = models.IntegerField(default=0)
    
    # Statut global
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SUCCESS'
    )
    
    # Détails
    details = models.JSONField(default=dict, blank=True)
    error_details = models.TextField(blank=True)
    
    # Durée
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    
    class Meta:
        db_table = 'sync_logs'
        verbose_name = 'Log de Synchronisation'
        verbose_name_plural = 'Logs de Synchronisation'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'started_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Sync {self.user} - {self.status} - {self.started_at}"


class LastSync(models.Model):
    """
    Dernière synchronisation par utilisateur
    Permet le delta sync (sync incrémental)
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='last_sync'
    )
    
    # Timestamps par entité
    reminders_last_sync = models.DateTimeField(null=True, blank=True)
    documents_last_sync = models.DateTimeField(null=True, blank=True)
    medical_records_last_sync = models.DateTimeField(null=True, blank=True)
    consents_last_sync = models.DateTimeField(null=True, blank=True)
    
    # Global
    last_full_sync = models.DateTimeField(null=True, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'last_sync'
        verbose_name = 'Dernière Synchronisation'
        verbose_name_plural = 'Dernières Synchronisations'
    
    def __str__(self):
        return f"Last sync: {self.user}"
