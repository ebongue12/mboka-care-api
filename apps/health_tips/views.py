import os
import requests as http_requests
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q, F
from .models import HealthTip
from .serializers import HealthTipSerializer, HealthTipCreateSerializer


# ─── Utilitaire FCM ───────────────────────────────────────────────────────────

def _send_fcm(tokens, title, body, data=None):
    """Envoie une notification FCM aux tokens fournis (Legacy API)."""
    server_key = os.environ.get('FCM_SERVER_KEY', '')
    if not server_key or not tokens:
        return
    chunks = [tokens[i:i + 500] for i in range(0, len(tokens), 500)]
    for chunk in chunks:
        try:
            http_requests.post(
                'https://fcm.googleapis.com/fcm/send',
                json={
                    'registration_ids': chunk,
                    'notification': {'title': title, 'body': body, 'sound': 'default'},
                    'data': data or {},
                    'priority': 'high',
                },
                headers={
                    'Authorization': f'key={server_key}',
                    'Content-Type': 'application/json',
                },
                timeout=10,
            )
        except Exception:
            pass


def _notify_patients_for_tip(tip):
    """Crée des notifications DB + pousse FCM aux patients ciblés."""
    from apps.notifications.models import Notification, PushToken

    patients = tip.get_target_patients().select_related('user')

    # Tokens FCM actifs
    user_ids = [p.user_id for p in patients]
    tokens = list(
        PushToken.objects.filter(user_id__in=user_ids, is_active=True)
        .values_list('token', flat=True)
    )

    title = f"💡 {tip.title}"
    body = tip.content[:120] + ('…' if len(tip.content) > 120 else '')

    # Notifications en base
    notifs = [
        Notification(
            recipient=p.user,
            notification_type='INFO',
            title=title,
            message=body,
            extra_data={'health_tip_id': str(tip.id)},
        )
        for p in patients
    ]
    Notification.objects.bulk_create(notifs, ignore_conflicts=True)

    # Push FCM
    _send_fcm(tokens, title, body, data={'type': 'HEALTH_TIP', 'tip_id': str(tip.id)})


# ─── Vues Patient ─────────────────────────────────────────────────────────────

class PatientHealthTipsView(generics.ListAPIView):
    """
    Liste des astuces santé visibles pour le patient connecté,
    filtrées selon sa ville/quartier de résidence.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = HealthTipSerializer

    def get_queryset(self):
        user = self.request.user
        patient = getattr(user, 'patient_profile', None)

        city = getattr(patient, 'city_residence', '') or ''
        district = getattr(patient, 'district_residence', '') or ''

        return HealthTip.objects.filter(is_active=True).filter(
            Q(visibility='ALL') |
            Q(visibility='CITY', target_city__iexact=city) |
            Q(visibility='DISTRICT', target_city__iexact=city,
              target_districts__contains=[district])
        ).select_related('published_by')

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_tip_viewed(request, tip_id):
    """Incrémenter le compteur de vues d'une astuce (atomic)."""
    HealthTip.objects.filter(id=tip_id, is_active=True).update(
        views_count=F('views_count') + 1
    )
    return Response({'ok': True})


# ─── Vues Personnel de Santé ──────────────────────────────────────────────────

class StaffHealthTipsView(generics.ListCreateAPIView):
    """
    GET  → liste les astuces publiées par le professionnel connecté
    POST → publie une nouvelle astuce + envoie notifications aux patients ciblés
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return HealthTipCreateSerializer if self.request.method == 'POST' else HealthTipSerializer

    def get_queryset(self):
        staff = getattr(self.request.user, 'healthcare_staff', None)
        if staff is None:
            return HealthTip.objects.none()
        return HealthTip.objects.filter(published_by=staff).select_related('published_by')

    def perform_create(self, serializer):
        staff = getattr(self.request.user, 'healthcare_staff', None)
        if staff is None:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Profil professionnel introuvable.')
        self._created_tip = serializer.save(published_by=staff)
        try:
            _notify_patients_for_tip(self._created_tip)
        except Exception:
            pass

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        tip = HealthTip.objects.select_related('published_by').get(pk=self._created_tip.pk)
        return Response(HealthTipSerializer(tip).data, status=status.HTTP_201_CREATED)


class StaffHealthTipDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail / modification / suppression d'une astuce (staff propriétaire)."""
    permission_classes = [IsAuthenticated]
    serializer_class = HealthTipSerializer

    def get_queryset(self):
        staff = getattr(self.request.user, 'healthcare_staff', None)
        if staff is None:
            return HealthTip.objects.none()
        return HealthTip.objects.filter(published_by=staff)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
