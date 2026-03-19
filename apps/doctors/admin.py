from django.contrib import admin
from django.utils import timezone
from .models import HealthcareStaff, QRScanLog, PatientFollowUp


@admin.register(HealthcareStaff)
class HealthcareStaffAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'staff_type', 'establishment', 'city',
        'verified', 'verification_status', 'total_scans',
        'total_patients_followed', 'created_at',
    ]
    list_filter = ['staff_type', 'verified', 'verification_status', 'city']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'establishment']
    readonly_fields = ['id', 'total_scans', 'total_patients_followed', 'created_at', 'updated_at', 'verified_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Informations personnelles', {
            'fields': ('id', 'user', 'staff_type', 'first_name', 'last_name', 'phone', 'email'),
        }),
        ("Lieu d'exercice", {
            'fields': ('city', 'establishment'),
        }),
        ('Expérience', {
            'fields': ('specialty', 'years_experience', 'patients_treated_range', 'medical_order_number'),
        }),
        ('Vérification', {
            'fields': ('verified', 'verification_status', 'diploma_document', 'work_contract', 'verified_by', 'verified_at'),
        }),
        ('Statistiques', {
            'fields': ('total_scans', 'total_patients_followed', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    actions = ['verify_staff', 'reject_staff']

    @admin.action(description='Vérifier les comptes sélectionnés')
    def verify_staff(self, request, queryset):
        updated = queryset.update(
            verified=True,
            verification_status='VERIFIED',
            verified_by=request.user,
            verified_at=timezone.now(),
        )
        self.message_user(request, f'{updated} compte(s) vérifié(s) avec succès.')

    @admin.action(description='Rejeter les comptes sélectionnés')
    def reject_staff(self, request, queryset):
        updated = queryset.update(
            verified=False,
            verification_status='REJECTED',
        )
        self.message_user(request, f'{updated} compte(s) rejeté(s).')


@admin.register(QRScanLog)
class QRScanLogAdmin(admin.ModelAdmin):
    list_display = ['healthcare_staff', 'patient', 'motif', 'timestamp', 'notification_sent']
    list_filter = ['motif', 'notification_sent', 'timestamp']
    search_fields = ['healthcare_staff__first_name', 'healthcare_staff__last_name']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']


@admin.register(PatientFollowUp)
class PatientFollowUpAdmin(admin.ModelAdmin):
    list_display = ['healthcare_staff', 'patient', 'is_active', 'added_at']
    list_filter = ['is_active']
    search_fields = ['healthcare_staff__first_name', 'healthcare_staff__last_name']
    readonly_fields = ['added_at']
    ordering = ['-added_at']
