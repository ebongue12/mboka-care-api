from django.urls import path
from .views import (
    PatientProfileMeView,
    FamilyMemberListCreateView,
    FamilyMemberDetailView,
    consultation_history,
    report_abuse,
    health_status_update,
)
from .qr_views import (
    generate_patient_qr,
    generate_family_member_qr,
    scan_qr_emergency,
    get_patient_qr,
    get_family_member_qr
)

urlpatterns = [
    # Profil patient
    path('me/', PatientProfileMeView.as_view(), name='patient-me'),

    # Famille
    path('family-members/', FamilyMemberListCreateView.as_view(), name='family-members'),
    path('family-members/<uuid:pk>/', FamilyMemberDetailView.as_view(), name='family-member-detail'),

    # QR Codes
    path('qr/generate/', generate_patient_qr, name='generate-patient-qr'),
    path('qr/', get_patient_qr, name='get-patient-qr'),
    path('qr/family/<uuid:member_id>/generate/', generate_family_member_qr, name='generate-family-qr'),
    path('qr/family/<uuid:member_id>/', get_family_member_qr, name='get-family-qr'),
    path('qr/scan/', scan_qr_emergency, name='scan-qr-emergency'),

    # Nouvelles routes
    path('consultation-history/', consultation_history, name='consultation-history'),
    path('report-abuse/', report_abuse, name='report-abuse'),
    path('health-status-update/', health_status_update, name='health-status-update'),
]
