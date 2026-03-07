from django.contrib import admin
from .models import Notification, NotificationPreference, PushToken

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'title', 'read', 'created_at']
    list_filter = ['notification_type', 'read', 'push_sent', 'created_at']
    search_fields = ['recipient__phone', 'title', 'message']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Destinataire', {
            'fields': ('recipient', 'notification_type')
        }),
        ('Contenu', {
            'fields': ('title', 'message', 'extra_data')
        }),
        ('Relations', {
            'fields': ('related_patient', 'related_reminder')
        }),
        ('Statut', {
            'fields': ('read', 'read_at', 'delivered', 'delivered_at')
        }),
        ('Push', {
            'fields': ('push_sent', 'push_sent_at', 'push_token')
        }),
    )
    
    readonly_fields = ['created_at', 'read_at', 'delivered_at', 'push_sent_at']


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'push_enabled', 'email_enabled', 'sms_enabled']
    list_filter = ['push_enabled', 'email_enabled', 'sms_enabled']
    search_fields = ['user__phone']


@admin.register(PushToken)
class PushTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'platform', 'device_name', 'is_active', 'created_at']
    list_filter = ['platform', 'is_active']
    search_fields = ['user__phone', 'token', 'device_name']
