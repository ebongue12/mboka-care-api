from django.contrib import admin
from .models import Consent, PatientFollower, EmergencyAccess

@admin.register(Consent)
class ConsentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'granted_to', 'level', 'consent_type', 'active', 'granted_at']
    list_filter = ['level', 'consent_type', 'active']
    search_fields = ['patient__first_name', 'patient__last_name', 'granted_to__phone']
    date_hierarchy = 'granted_at'

@admin.register(PatientFollower)
class PatientFollowerAdmin(admin.ModelAdmin):
    list_display = ['patient', 'follower', 'relation_type', 'active', 'created_at']
    list_filter = ['relation_type', 'active']
    search_fields = ['patient__first_name', 'follower__phone']

@admin.register(EmergencyAccess)
class EmergencyAccessAdmin(admin.ModelAdmin):
    list_display = ['patient', 'family_member', 'helper_name', 'access_timestamp', 'offline_mode', 'synced']
    list_filter = ['offline_mode', 'synced', 'access_timestamp']
    search_fields = ['helper_name', 'helper_phone', 'patient__first_name']
    date_hierarchy = 'access_timestamp'
