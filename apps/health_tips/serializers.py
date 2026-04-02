from rest_framework import serializers
from .models import HealthTip


class HealthTipSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='published_by.full_name', read_only=True)
    staff_type = serializers.CharField(source='published_by.get_staff_type_display', read_only=True)
    staff_establishment = serializers.CharField(source='published_by.establishment', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    visibility_display = serializers.CharField(source='get_visibility_display', read_only=True)

    class Meta:
        model = HealthTip
        fields = [
            'id', 'title', 'content', 'category', 'category_display',
            'visibility', 'visibility_display',
            'target_city', 'target_districts',
            'staff_name', 'staff_type', 'staff_establishment',
            'views_count', 'is_active', 'created_at',
        ]
        read_only_fields = ['id', 'views_count', 'created_at']


class HealthTipCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthTip
        fields = [
            'title', 'content', 'category',
            'visibility', 'target_city', 'target_districts',
        ]

    def validate(self, attrs):
        visibility = attrs.get('visibility', 'ALL')
        if visibility in ('CITY', 'DISTRICT') and not attrs.get('target_city'):
            raise serializers.ValidationError({'target_city': 'La ville est requise.'})
        if visibility == 'DISTRICT' and not attrs.get('target_districts'):
            raise serializers.ValidationError({'target_districts': 'Sélectionnez au moins un quartier.'})
        return attrs
