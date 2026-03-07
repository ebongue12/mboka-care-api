from django.contrib import admin
from .models import PatientProfile, FamilyMember

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'age', 'blood_group', 'account_type', 'created_at']
    list_filter = ['account_type', 'blood_group']
    search_fields = ['first_name', 'last_name', 'user__phone']

@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'age', 'relation', 'family_chief', 'is_active']
    list_filter = ['relation', 'is_active']
    search_fields = ['first_name', 'last_name']
