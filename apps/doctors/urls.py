from django.urls import path
from . import views

urlpatterns = [
    # Inscription
    path('register/', views.register_healthcare_staff, name='healthcare-register'),

    # Profil
    path('me/', views.my_profile, name='healthcare-me'),

    # Scan QR
    path('scan-qr/', views.scan_patient_qr, name='healthcare-scan-qr'),

    # Patients suivis
    path('followed-patients/', views.my_followed_patients, name='healthcare-followed-patients'),
    path('follow-patient/', views.add_patient_to_follow, name='healthcare-follow-patient'),

    # Statistiques
    path('statistics/', views.my_statistics, name='healthcare-statistics'),
]
