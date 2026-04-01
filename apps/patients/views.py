from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import PatientProfile, FamilyMember
from .serializers import PatientProfileSerializer, FamilyMemberSerializer

class PatientProfileMeView(generics.RetrieveUpdateAPIView):
    """Profil patient de l'utilisateur connecté"""
    permission_classes = [IsAuthenticated]
    serializer_class = PatientProfileSerializer
    
    def get_object(self):
        profile, _ = PatientProfile.objects.get_or_create(user=self.request.user)
        return profile


class FamilyMemberListCreateView(generics.ListCreateAPIView):
    """Liste et création de membres de famille"""
    permission_classes = [IsAuthenticated]
    serializer_class = FamilyMemberSerializer
    
    def get_queryset(self):
        return self.request.user.patient_profile.family_members.filter(is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(family_chief=self.request.user.patient_profile)


class FamilyMemberDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail, modification, suppression membre famille"""
    permission_classes = [IsAuthenticated]
    serializer_class = FamilyMemberSerializer

    def get_queryset(self):
        return self.request.user.patient_profile.family_members.filter(is_active=True)

    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def consultation_history(request):
    """Historique des consultations reçues par le patient (via QR scans)"""
    try:
        from apps.doctors.models import QRScanLog
        profile, _ = PatientProfile.objects.get_or_create(user=request.user)
        logs = QRScanLog.objects.filter(
            patient=profile
        ).select_related('healthcare_staff').order_by('-timestamp')[:50]
        data = []
        for log in logs:
            s = log.healthcare_staff
            data.append({
                'id': str(log.id),
                'doctor': {
                    'first_name': s.first_name,
                    'last_name': s.last_name,
                    'staff_type': s.staff_type,
                },
                'motif': log.motif,
                'timestamp': log.timestamp.isoformat(),
                'notes': log.notes,
            })
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_abuse(request):
    """Signalement d'un accès abusif au QR code"""
    # On enregistre le signalement dans les notes du scan si possible
    try:
        from apps.doctors.models import QRScanLog
        scan_id = request.data.get('scan_id')
        reason = request.data.get('reason', 'Accès non autorisé signalé')
        if scan_id:
            try:
                log = QRScanLog.objects.get(id=scan_id)
                log.notes = f"[SIGNALEMENT] {reason}\n{log.notes}"
                log.save()
            except QRScanLog.DoesNotExist:
                pass
        return Response({'message': 'Signalement enregistré avec succès'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def health_status_update(request):
    """Mise à jour des informations de santé critiques"""
    try:
        profile, _ = PatientProfile.objects.get_or_create(user=request.user)
        allowed_fields = [
            'blood_group', 'chronic_conditions', 'allergies',
            'emergency_notes', 'emergency_contact_name', 'emergency_contact_phone'
        ]
        for field in allowed_fields:
            if field in request.data:
                setattr(profile, field, request.data[field])
        profile.save()
        return Response(PatientProfileSerializer(profile).data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
