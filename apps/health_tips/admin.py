from django.contrib import admin
from .models import HealthTip

@admin.register(HealthTip)
class HealthTipAdmin(admin.ModelAdmin):
    list_display = ['title', 'published_by', 'category', 'visibility', 'views_count', 'is_active', 'created_at']
    list_filter = ['category', 'visibility', 'is_active']
    search_fields = ['title', 'content', 'published_by__first_name', 'published_by__last_name']
    readonly_fields = ['views_count', 'created_at', 'updated_at']
