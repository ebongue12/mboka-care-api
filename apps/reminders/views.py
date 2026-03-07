from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Reminder, ReminderLog
from .serializers import (
    ReminderSerializer,
    ReminderLogSerializer,
    ReminderStatsSerializer
)

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
        serializer.save(created_by=self.request.user)


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
