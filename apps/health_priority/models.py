import uuid
from django.db import models
from apps.accounts.models import User

class HealthCategory(models.Model):
    """Catégories de contenu santé"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True)  # Emoji ou icon name
    
    # Ordre d'affichage
    order = models.IntegerField(default=0)
    
    # Statut
    is_active = models.BooleanField(default=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'health_categories'
        verbose_name = 'Catégorie Santé'
        verbose_name_plural = 'Catégories Santé'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class HealthContent(models.Model):
    """Contenu éducatif santé (vidéos, articles)"""
    
    CONTENT_TYPE_CHOICES = (
        ('VIDEO', 'Vidéo'),
        ('ARTICLE', 'Article'),
        ('INFOGRAPHIC', 'Infographie'),
        ('GUIDE', 'Guide'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Catégorie
    category = models.ForeignKey(
        HealthCategory,
        on_delete=models.CASCADE,
        related_name='contents'
    )
    
    # Type de contenu
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES,
        default='VIDEO'
    )
    
    # Informations
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    
    # Contenu
    video_url = models.URLField(blank=True)  # YouTube, Vimeo, etc.
    video_duration = models.IntegerField(null=True, blank=True)  # En secondes
    article_content = models.TextField(blank=True)  # Markdown ou HTML
    
    # Media
    thumbnail = models.ImageField(upload_to='health_priority/thumbnails/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='health_priority/covers/', null=True, blank=True)
    
    # Auteur/Expert
    author_name = models.CharField(max_length=200, blank=True)
    author_title = models.CharField(max_length=200, blank=True)  # Ex: "Dr. Sarah Kamga, Gynécologue"
    
    # Tags pour recherche
    tags = models.JSONField(default=list, blank=True)
    
    # Précautions/Avertissements
    warnings = models.TextField(blank=True)
    
    # Ordre et visibilité
    order = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)  # Contenu mis en avant
    is_active = models.BooleanField(default=True)
    
    # Statistiques
    view_count = models.IntegerField(default=0)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'health_contents'
        verbose_name = 'Contenu Santé'
        verbose_name_plural = 'Contenus Santé'
        ordering = ['-is_featured', 'order', '-published_at']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['content_type']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_content_type_display()})"


class UserContentProgress(models.Model):
    """Suivi de progression de l'utilisateur dans le contenu"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='health_progress'
    )
    content = models.ForeignKey(
        HealthContent,
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    
    # Progression
    completed = models.BooleanField(default=False)
    progress_percentage = models.IntegerField(default=0)  # 0-100
    
    # Pour les vidéos
    last_watched_position = models.IntegerField(default=0)  # En secondes
    
    # Dates
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_content_progress'
        verbose_name = 'Progression Utilisateur'
        verbose_name_plural = 'Progressions Utilisateurs'
        unique_together = [['user', 'content']]
        indexes = [
            models.Index(fields=['user', 'completed']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.content.title} - {self.progress_percentage}%"


class SavedContent(models.Model):
    """Contenus enregistrés/favoris par l'utilisateur"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_health_contents'
    )
    content = models.ForeignKey(
        HealthContent,
        on_delete=models.CASCADE,
        related_name='saved_by_users'
    )
    
    # Notes personnelles
    notes = models.TextField(blank=True)
    
    # Métadonnées
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'saved_health_contents'
        verbose_name = 'Contenu Enregistré'
        verbose_name_plural = 'Contenus Enregistrés'
        unique_together = [['user', 'content']]
        ordering = ['-saved_at']
    
    def __str__(self):
        return f"{self.user} - {self.content.title}"
