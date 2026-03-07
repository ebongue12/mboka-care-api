from django.contrib import admin
from .models import DoctorProfile

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'specialization', 'practice_city', 'verified', 'created_at']
    list_filter = ['verified', 'specialization', 'practice_city']
    search_fields = ['first_name', 'last_name', 'license_number']
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('user', 'first_name', 'last_name')
        }),
        ('Informations professionnelles', {
            'fields': ('specialization', 'license_number', 'hospital_affiliation')
        }),
        ('Localisation', {
            'fields': ('practice_country', 'practice_city', 'practice_district', 'practice_address')
        }),
        ('Vérification', {
            'fields': ('verified', 'verification_document', 'verified_at', 'verified_by')
        }),
    )
    
    readonly_fields = ['verified_at']
