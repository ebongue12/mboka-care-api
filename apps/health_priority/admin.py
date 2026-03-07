from django.contrib import admin
from .models import HealthCategory, HealthContent, UserContentProgress, SavedContent

@admin.register(HealthCategory)
class HealthCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(HealthContent)
class HealthContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'content_type', 'author_name', 'view_count', 'is_featured', 'published_at']
    list_filter = ['content_type', 'category', 'is_featured', 'is_active', 'published_at']
    search_fields = ['title', 'description', 'author_name']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('category', 'content_type', 'title', 'slug', 'description')
        }),
        ('Contenu', {
            'fields': ('video_url', 'video_duration', 'article_content', 'thumbnail', 'cover_image')
        }),
        ('Auteur', {
            'fields': ('author_name', 'author_title')
        }),
        ('Métadonnées', {
            'fields': ('tags', 'warnings', 'order', 'is_featured', 'is_active', 'published_at')
        }),
        ('Statistiques', {
            'fields': ('view_count',),
            'classes': ('collapse',)
        }),
    )

@admin.register(UserContentProgress)
class UserContentProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'progress_percentage', 'completed', 'last_accessed_at']
    list_filter = ['completed', 'content__content_type']
    search_fields = ['user__phone', 'content__title']
    date_hierarchy = 'started_at'

@admin.register(SavedContent)
class SavedContentAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'saved_at']
    search_fields = ['user__phone', 'content__title']
    date_hierarchy = 'saved_at'
