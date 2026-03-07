from django.contrib import admin
from .models import MedicalRecord, MedicalDocument

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['title', 'patient', 'family_member', 'level', 'record_date', 'created_at']
    list_filter = ['level', 'record_date', 'is_deleted']
    search_fields = ['title', 'description']
    date_hierarchy = 'record_date'

@admin.register(MedicalDocument)
class MedicalDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'document_type', 'patient', 'document_date', 'file_size', 'uploaded_at']
    list_filter = ['document_type', 'access_level', 'is_archived', 'is_deleted']
    search_fields = ['title', 'description', 'file_name']
    date_hierarchy = 'document_date'
