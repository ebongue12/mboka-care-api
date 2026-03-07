from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from .models import Notification, NotificationPreference, PushToken
from .serializers import (
    NotificationSerializer,
    NotificationPreferenceSerializer,
    PushTokenSerializer
)

# ===== NOTIFICATIONS =====

class NotificationListView(generics.ListAPIView):
    """Liste des notifications de l'utilisateur"""
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        queryset = Notification.objects.filter(recipient=self.request.user)
        
        # Filtres optionnels
        unread_only = self.request.query_params.get('unread', None)
        notification_type = self.request.query_params.get('type', None)
        
        if unread_only == 'true':
            queryset = queryset.filter(read=False)
        
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        return queryset


class NotificationDetailView(generics.RetrieveAPIView):
    """Détail d'une notification"""
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


class NotificationMarkReadView(generics.UpdateAPIView):
    """Marquer une notification comme lue"""
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if not instance.read:
            instance.read = True
            instance.read_at = timezone.now()
            instance.save()
        
        serializer = self.get_serializer(instance)
        return Response({
            'message': 'Notification marquée comme lue',
            'notification': serializer.data
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    """Marquer toutes les notifications comme lues"""
    count = Notification.objects.filter(
        recipient=request.user,
        read=False
    ).update(
        read=True,
        read_at=timezone.now()
    )
    
    return Response({
        'message': f'{count} notifications marquées comme lues',
        'count': count
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_count(request):
    """Compter les notifications non lues"""
    unread_count = Notification.objects.filter(
        recipient=request.user,
        read=False
    ).count()
    
    total_count = Notification.objects.filter(
        recipient=request.user
    ).count()
    
    return Response({
        'unread_count': unread_count,
        'total_count': total_count
    })


# ===== PRÉFÉRENCES =====

class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    """Récupérer/Modifier les préférences de notifications"""
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationPreferenceSerializer
    
    def get_object(self):
        # Créer les préférences si elles n'existent pas
        preferences, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return preferences


# ===== PUSH TOKENS =====

class PushTokenCreateView(generics.CreateAPIView):
    """Enregistrer un token push"""
    permission_classes = [IsAuthenticated]
    serializer_class = PushTokenSerializer
    
    def perform_create(self, serializer):
        # Désactiver les anciens tokens du même appareil
        token_value = serializer.validated_data.get('token')
        device_id = serializer.validated_data.get('device_id')
        
        if device_id:
            PushToken.objects.filter(
                user=self.request.user,
                device_id=device_id
            ).update(is_active=False)
        
        serializer.save(user=self.request.user)


class PushTokenListView(generics.ListAPIView):
    """Liste des tokens push de l'utilisateur"""
    permission_classes = [IsAuthenticated]
    serializer_class = PushTokenSerializer
    
    def get_queryset(self):
        return PushToken.objects.filter(
            user=self.request.user,
            is_active=True
        )


class PushTokenDeleteView(generics.DestroyAPIView):
    """Supprimer un token push"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PushToken.objects.filter(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        
        return Response({
            'message': 'Token désactivé'
        }, status=status.HTTP_204_NO_CONTENT)
