import os
import requests as http_requests
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta, time as dt_time
from .models import Reminder, ReminderLog
from .serializers import (
    ReminderSerializer,
    ReminderLogSerializer,
    ReminderStatsSerializer
)

# ─── Labels par type de rappel ────────────────────────────────────────────────

_TYPE_LABEL = {
    'MEDICATION': 'médicament',
    'APPOINTMENT': 'rendez-vous',
    'EXAM': 'examen médical',
    'VACCINATION': 'vaccination',
    'OTHER': 'rappel',
}


def _send_follower_confirmation_fcm(reminder, log, new_status):
    """
    Crée les notifications en base + envoie FCM aux followers actifs
    suite à la confirmation (OUI / NON / TIMEOUT) d'un rappel.
    """
    from apps.sharing.models import PatientFollower
    from apps.notifications.models import Notification, PushToken

    patient = reminder.patient
    type_label = _TYPE_LABEL.get(reminder.reminder_type, 'rappel')
    patient_name = getattr(patient, 'first_name', None) or 'Votre proche'
    med_label = reminder.medication_name or reminder.title
    time_str = log.scheduled_time.strftime('%H:%M')

    if new_status == 'TAKEN':
        notif_type = 'MEDICATION_TAKEN'
        title = f"✅ {patient_name} a pris son {type_label}"
        body = f"{med_label} pris à {time_str}."
    elif new_status == 'SKIPPED':
        notif_type = 'MEDICATION_MISSED'
        title = f"❌ {patient_name} n'a PAS pris son {type_label}"
        body = f"{med_label} prévu à {time_str} — signalé comme non pris."
    else:  # MISSED
        notif_type = 'MEDICATION_MISSED'
        title = f"⚠️ Pas de réponse de {patient_name}"
        body = f"{med_label} prévu à {time_str} — aucune confirmation reçue."

    # Followers actifs qui acceptent les alertes médicaments
    followers = PatientFollower.objects.filter(
        patient=patient,
        active=True,
        receive_medication_alerts=True,
    ).select_related('follower')

    if not followers.exists():
        return

    follower_users = [f.follower for f in followers]

    # Notifications en base
    Notification.objects.bulk_create([
        Notification(
            recipient=fu,
            notification_type=notif_type,
            title=title,
            message=body,
            related_patient=patient,
            related_reminder=reminder,
            extra_data={'log_id': str(log.id), 'status': new_status},
        )
        for fu in follower_users
    ], ignore_conflicts=True)

    # Tokens FCM
    user_ids = [fu.id for fu in follower_users]
    tokens = list(
        PushToken.objects.filter(user_id__in=user_ids, is_active=True)
        .values_list('token', flat=True)
    )
    if not tokens:
        return

    server_key = os.environ.get('FCM_SERVER_KEY', '')
    if not server_key:
        return

    for chunk in [tokens[i:i + 500] for i in range(0, len(tokens), 500)]:
        try:
            http_requests.post(
                'https://fcm.googleapis.com/fcm/send',
                json={
                    'registration_ids': chunk,
                    'notification': {'title': title, 'body': body, 'sound': 'default'},
                    'data': {
                        'type': 'REMINDER_CONFIRMATION',
                        'status': new_status,
                        'log_id': str(log.id),
                    },
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

class ReminderListCreateView(generics.ListCreateAPIView):
    """Liste et création de rappels"""
    permission_classes = [IsAuthenticated]
    serializer_class = ReminderSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'patient_profile'):
            return Reminder.objects.filter(
                Q(patient=user.patient_profile) |
                Q(family_member__family_chief=user.patient_profile)
            )
        return Reminder.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        patient = getattr(user, 'patient_profile', None)
        serializer.save(created_by=user, patient=patient)


class ReminderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail, modification, suppression rappel"""
    permission_classes = [IsAuthenticated]
    serializer_class = ReminderSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'patient_profile'):
            return Reminder.objects.filter(
                Q(patient=user.patient_profile) |
                Q(family_member__family_chief=user.patient_profile)
            )
        return Reminder.objects.none()


class ReminderDeactivateView(generics.UpdateAPIView):
    """Désactiver un rappel"""
    permission_classes = [IsAuthenticated]
    serializer_class = ReminderSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'patient_profile'):
            return Reminder.objects.filter(
                Q(patient=user.patient_profile) |
                Q(family_member__family_chief=user.patient_profile)
            )
        return Reminder.objects.none()
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        
        serializer = self.get_serializer(instance)
        return Response({
            'message': 'Rappel désactivé',
            'reminder': serializer.data
        })


class ReminderLogListCreateView(generics.ListCreateAPIView):
    """Liste et création de logs de rappels"""
    permission_classes = [IsAuthenticated]
    serializer_class = ReminderLogSerializer
    
    def get_queryset(self):
        user = self.request.user
        reminder_id = self.request.query_params.get('reminder_id')
        status_filter = self.request.query_params.get('status')
        
        queryset = ReminderLog.objects.none()
        
        if hasattr(user, 'patient_profile'):
            queryset = ReminderLog.objects.filter(
                Q(reminder__patient=user.patient_profile) |
                Q(reminder__family_member__family_chief=user.patient_profile)
            )
            
            if reminder_id:
                queryset = queryset.filter(reminder_id=reminder_id)
            
            if status_filter:
                queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(confirmed_by=self.request.user)


class ReminderLogDetailView(generics.RetrieveUpdateAPIView):
    """Détail et modification log rappel"""
    permission_classes = [IsAuthenticated]
    serializer_class = ReminderLogSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'patient_profile'):
            return ReminderLog.objects.filter(
                Q(reminder__patient=user.patient_profile) |
                Q(reminder__family_member__family_chief=user.patient_profile)
            )
        return ReminderLog.objects.none()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reminder_stats(request):
    """Statistiques d'observance"""
    reminder_id = request.query_params.get('reminder_id')
    period = request.query_params.get('period', 'month')
    
    if not reminder_id:
        return Response(
            {'error': 'reminder_id requis'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        reminder = Reminder.objects.get(id=reminder_id)
    except Reminder.DoesNotExist:
        return Response(
            {'error': 'Rappel non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Calculer la période
    today = timezone.now().date()
    if period == 'week':
        start_date = today - timedelta(days=7)
    elif period == 'month':
        start_date = today - timedelta(days=30)
    elif period == 'year':
        start_date = today - timedelta(days=365)
    else:
        start_date = reminder.start_date
    
    # Récupérer les logs
    logs = ReminderLog.objects.filter(
        reminder=reminder,
        scheduled_date__gte=start_date,
        scheduled_date__lte=today
    )
    
    # Calculer les stats
    total_scheduled = logs.count()
    taken = logs.filter(status='TAKEN').count()
    missed = logs.filter(status='MISSED').count()
    delayed = logs.filter(status='DELAYED').count()
    skipped = logs.filter(status='SKIPPED').count()
    
    adherence_rate = (taken / total_scheduled * 100) if total_scheduled > 0 else 0
    
    # Données pour graphique
    chart_data = []
    current_date = start_date
    while current_date <= today:
        day_logs = logs.filter(scheduled_date=current_date)
        chart_data.append({
            'date': current_date.isoformat(),
            'taken': day_logs.filter(status='TAKEN').count(),
            'missed': day_logs.filter(status='MISSED').count()
        })
        current_date += timedelta(days=1)
    
    stats = {
        'reminder': ReminderSerializer(reminder).data,
        'period': period,
        'total_scheduled': total_scheduled,
        'taken': taken,
        'missed': missed,
        'delayed': delayed,
        'skipped': skipped,
        'adherence_rate': round(adherence_rate, 1),
        'chart_data': chart_data
    }
    
    return Response(stats)


# ─── Confirmation de prise (OUI / NON / TIMEOUT) ──────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_reminder(request):
    """
    Confirme ou infirme la prise d'un médicament / rendez-vous.

    Body JSON :
        reminder_id    (UUID)
        scheduled_time (HH:MM)
        status         TAKEN | SKIPPED | MISSED

    Crée ou met à jour le ReminderLog du jour, puis envoie FCM aux
    followers si notify_followers=True sur le rappel.
    """
    reminder_id = request.data.get('reminder_id')
    scheduled_time_str = request.data.get('scheduled_time')
    new_status = request.data.get('status')

    # Validation
    if new_status not in ('TAKEN', 'SKIPPED', 'MISSED'):
        return Response(
            {'error': "Statut invalide. Valeurs acceptées : TAKEN, SKIPPED, MISSED"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not reminder_id or not scheduled_time_str:
        return Response(
            {'error': 'reminder_id et scheduled_time sont requis'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Vérifier ownership
    user = request.user
    patient = getattr(user, 'patient_profile', None)
    if patient is None:
        return Response({'error': 'Profil patient requis'}, status=status.HTTP_403_FORBIDDEN)

    try:
        reminder = Reminder.objects.get(pk=reminder_id, patient=patient)
    except Reminder.DoesNotExist:
        return Response({'error': 'Rappel introuvable'}, status=status.HTTP_404_NOT_FOUND)

    # Parser l'heure
    try:
        h, m = map(int, scheduled_time_str.strip().split(':'))
        s_time = dt_time(h, m)
    except (ValueError, TypeError):
        return Response({'error': "Format d'heure invalide. Utilisez HH:MM"}, status=status.HTTP_400_BAD_REQUEST)

    # Date = aujourd'hui (la confirmation arrive toujours peu après l'alarme)
    now_local = timezone.localtime(timezone.now())
    s_date = now_local.date()

    # Si l'heure programmée est dans le futur (ex: alarme 23:59 → confirm 00:01),
    # utiliser la veille
    if s_time > now_local.time() and now_local.hour < 1:
        from datetime import timedelta as td
        s_date = s_date - td(days=1)

    s_dt = timezone.make_aware(datetime.combine(s_date, s_time))

    # Créer ou récupérer le log
    log, _ = ReminderLog.objects.get_or_create(
        reminder=reminder,
        scheduled_date=s_date,
        scheduled_time=s_time,
        defaults={'scheduled_datetime': s_dt, 'status': new_status},
    )
    # Mettre à jour si déjà existant
    log.status = new_status
    log.confirmed_at = timezone.now()
    log.confirmed_by = user
    log.notification_sent_to_patient = True
    log.save(update_fields=[
        'status', 'confirmed_at', 'confirmed_by',
        'notification_sent_to_patient', 'updated_at',
    ])

    # Notifier les followers
    if reminder.notify_followers:
        try:
            _send_follower_confirmation_fcm(reminder, log, new_status)
        except Exception:
            pass

    return Response({'ok': True, 'status': new_status, 'log_id': str(log.id)})
