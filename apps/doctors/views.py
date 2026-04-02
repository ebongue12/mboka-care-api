from datetime import timedelta

from django.utils import timezone
from django.shortcuts import get_object_or_404

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import HealthcareStaff, QRScanLog, PatientFollowUp
from .serializers import (
    HealthcareStaffSerializer,
    HealthcareStaffRegistrationSerializer,
    QRScanLogSerializer,
    PatientFollowUpSerializer,
)
from apps.patients.models import PatientProfile


class IsVerifiedHealthcareStaff(permissions.BasePermission):
    """Seul le personnel de santé vérifié peut accéder."""
    message = 'Compte personnel de santé vérifié requis.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, 'healthcare_staff')
            and request.user.healthcare_staff.verified
        )


# ─── INSCRIPTION ──────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def register_healthcare_staff(request):
    """Inscription personnel de santé"""
    serializer = HealthcareStaffRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        staff = serializer.save()
        return Response({
            'message': 'Inscription réussie. Votre compte sera vérifié sous 48h.',
            'staff': HealthcareStaffSerializer(staff).data,
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── PROFIL ───────────────────────────────────────────────

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def my_profile(request):
    """Profil du personnel de santé connecté"""
    if not hasattr(request.user, 'healthcare_staff'):
        return Response(
            {'error': 'Aucun profil personnel de santé associé à ce compte.'},
            status=status.HTTP_404_NOT_FOUND
        )

    staff = request.user.healthcare_staff

    if request.method == 'GET':
        return Response(HealthcareStaffSerializer(staff).data)

    serializer = HealthcareStaffSerializer(staff, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── SCAN QR CODE ─────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsVerifiedHealthcareStaff])
def scan_patient_qr(request):
    """Scanner QR Code patient — accès complet au dossier"""
    patient_id = request.data.get('patient_id')
    motif = request.data.get('motif')
    notes = request.data.get('notes', '')

    if not patient_id or not motif:
        return Response(
            {'error': 'patient_id et motif sont requis.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if motif not in dict(QRScanLog.MOTIF_CHOICES):
        return Response(
            {'error': f'Motif invalide. Valeurs acceptées : {list(dict(QRScanLog.MOTIF_CHOICES).keys())}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    patient = get_object_or_404(PatientProfile, id=patient_id)
    staff = request.user.healthcare_staff

    # Enregistrer le scan
    scan_log = QRScanLog.objects.create(
        healthcare_staff=staff,
        patient=patient,
        motif=motif,
        notes=notes,
    )

    # Mettre à jour stats (atomic pour éviter les race conditions)
    from django.db.models import F as DbF
    HealthcareStaff.objects.filter(pk=staff.pk).update(total_scans=DbF('total_scans') + 1)

    # Construire le dossier complet
    from apps.patients.serializers import PatientProfileSerializer
    patient_data = PatientProfileSerializer(patient).data

    # Documents
    documents_data = []
    if hasattr(patient, 'documents'):
        from apps.medical.serializers import MedicalDocumentSerializer
        documents_data = MedicalDocumentSerializer(patient.documents.all(), many=True).data

    # Rappels
    reminders_data = []
    if hasattr(patient, 'reminders'):
        from apps.reminders.serializers import ReminderSerializer
        reminders_data = ReminderSerializer(patient.reminders.all(), many=True).data

    # Historique scans de ce patient (pour le médecin)
    recent_scans = QRScanLog.objects.filter(patient=patient).order_by('-timestamp')[:10]

    return Response({
        'scan_log_id': str(scan_log.id) if hasattr(scan_log, 'id') else scan_log.pk,
        'patient': patient_data,
        'documents': documents_data,
        'reminders': reminders_data,
        'recent_scans': QRScanLogSerializer(recent_scans, many=True).data,
    })


# ─── PATIENTS SUIVIS ──────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsVerifiedHealthcareStaff])
def my_followed_patients(request):
    """Liste des patients que je suis"""
    staff = request.user.healthcare_staff
    follow_ups = PatientFollowUp.objects.filter(
        healthcare_staff=staff,
        is_active=True
    ).select_related('patient__user')
    return Response(PatientFollowUpSerializer(follow_ups, many=True).data)


@api_view(['POST'])
@permission_classes([IsVerifiedHealthcareStaff])
def add_patient_to_follow(request):
    """Ajouter un patient à ma liste de suivi"""
    patient_id = request.data.get('patient_id')
    notes = request.data.get('notes', '')

    if not patient_id:
        return Response({'error': 'patient_id est requis.'}, status=status.HTTP_400_BAD_REQUEST)

    patient = get_object_or_404(PatientProfile, id=patient_id)
    staff = request.user.healthcare_staff

    follow_up, created = PatientFollowUp.objects.get_or_create(
        healthcare_staff=staff,
        patient=patient,
        defaults={'notes': notes},
    )

    if created:
        HealthcareStaff.objects.filter(pk=staff.pk).update(
            total_patients_followed=staff.total_patients_followed + 1
        )
        return Response(PatientFollowUpSerializer(follow_up).data, status=status.HTTP_201_CREATED)

    # Réactiver si désactivé
    if not follow_up.is_active:
        follow_up.is_active = True
        follow_up.notes = notes or follow_up.notes
        follow_up.save()

    return Response(PatientFollowUpSerializer(follow_up).data)


# ─── STATISTIQUES ─────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsVerifiedHealthcareStaff])
def my_statistics(request):
    """Statistiques de garde du personnel de santé"""
    staff = request.user.healthcare_staff
    now = timezone.now()

    stats = {
        'today': {
            'scans': QRScanLog.objects.filter(
                healthcare_staff=staff,
                timestamp__date=now.date()
            ).count(),
            'urgences': QRScanLog.objects.filter(
                healthcare_staff=staff,
                timestamp__date=now.date(),
                motif='URGENCE'
            ).count(),
        },
        'week': {
            'scans': QRScanLog.objects.filter(
                healthcare_staff=staff,
                timestamp__gte=now - timedelta(days=7)
            ).count(),
        },
        'month': {
            'scans': QRScanLog.objects.filter(
                healthcare_staff=staff,
                timestamp__gte=now - timedelta(days=30)
            ).count(),
        },
        'total': {
            'scans': staff.total_scans,
            'patients_followed': staff.total_patients_followed,
        },
        'by_motif': {
            motif: QRScanLog.objects.filter(
                healthcare_staff=staff,
                motif=motif
            ).count()
            for motif, _ in QRScanLog.MOTIF_CHOICES
        },
    }

    return Response(stats)
