from rest_framework import serializers
from .models import HealthCategory, HealthContent, UserContentProgress, SavedContent

class HealthCategorySerializer(serializers.ModelSerializer):
    """Serializer pour catégorie"""
    content_count = serializers.SerializerMethodField()
    
    class Meta:
        model = HealthCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon',
            'order', 'is_active', 'content_count',
            'created_at', 'updated_at'
        ]
    
    def get_content_count(self, obj):
        return obj.contents.filter(is_active=True).count()


class HealthContentListSerializer(serializers.ModelSerializer):
    """Serializer léger pour liste de contenus"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = HealthContent
        fields = [
            'id', 'category', 'category_name', 'content_type',
            'title', 'slug', 'description',
            'thumbnail', 'video_duration',
            'author_name', 'author_title',
            'is_featured', 'view_count',
            'published_at'
        ]


class HealthContentDetailSerializer(serializers.ModelSerializer):
    """Serializer complet pour détail de contenu"""
    category = HealthCategorySerializer(read_only=True)
    
    class Meta:
        model = HealthContent
        fields = [
            'id', 'category', 'content_type',
            'title', 'slug', 'description',
            'video_url', 'video_duration',
            'article_content',
            'thumbnail', 'cover_image',
            'author_name', 'author_title',
            'tags', 'warnings',
            'is_featured', 'view_count',
            'created_at', 'updated_at', 'published_at'
        ]


class UserContentProgressSerializer(serializers.ModelSerializer):
    """Serializer pour progression"""
    
    class Meta:
        model = UserContentProgress
        fields = [
            'id', 'user', 'content',
            'completed', 'progress_percentage',
            'last_watched_position',
            'started_at', 'completed_at', 'last_accessed_at'
        ]
        read_only_fields = ['id', 'user', 'started_at', 'last_accessed_at']


class SavedContentSerializer(serializers.ModelSerializer):
    """Serializer pour contenu enregistré"""
    content = HealthContentListSerializer(read_only=True)
    
    class Meta:
        model = SavedContent
        fields = [
            'id', 'user', 'content', 'notes', 'saved_at'
        ]
        read_only_fields = ['id', 'user', 'saved_at']
