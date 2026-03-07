from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from django.db.models import Q
from datetime import datetime
from .models import SyncQueue, SyncConflict, SyncLog, LastSync
from .serializers import (
    SyncQueueSerializer,
    SyncConflictSerializer,
    SyncLogSerializer,
    LastSyncSerializer,
    SyncUploadSerializer,
    SyncDownloadSerializer
)

# ===== UPLOAD (Client → Serveur) =====

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_upload(request):
    """
    Recevoir et traiter les modifications du client
    """
    serializer = SyncUploadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    queue_items = serializer.validated_data['queue']
    user = request.user
    
    results = []
    synced_count = 0
    failed_count = 0
    
    # Créer un log de sync
    sync_log = SyncLog.objects.create(
        user=user,
        status='SUCCESS'
    )
    
    for item in queue_items:
        try:
            # Créer l'item dans la queue
            sync_item = SyncQueue.objects.create(
                user=user,
                entity_type=item.get('entity_type'),
                entity_id=item.get('entity_id'),
                action=item.get('action'),
                data=item.get('data')
            )
            
            # TODO: Traiter l'action (CREATE, UPDATE, DELETE)
            # Pour l'instant, on marque comme synced
            sync_item.synced = True
            sync_item.synced_at = timezone.now()
            sync_item.save()
            
            results.append({
                'local_id': item.get('entity_id'),
                'server_id': str(sync_item.entity_id),
                'entity_type': sync_item.entity_type,
                'status': 'SUCCESS'
            })
            
            synced_count += 1
            
        except Exception as e:
            results.append({
                'local_id': item.get('entity_id'),
                'status': 'ERROR',
                'error': str(e)
            })
            failed_count += 1
    
    # Mettre à jour le log
    sync_log.items_uploaded = synced_count
    sync_log.errors_count = failed_count
    sync_log.completed_at = timezone.now()
    
    if failed_count > 0:
        sync_log.status = 'PARTIAL' if synced_count > 0 else 'FAILED'
    
    duration = (sync_log.completed_at - sync_log.started_at).total_seconds()
    sync_log.duration_seconds = duration
    sync_log.save()
    
    return Response({
        'synced_count': synced_count,
        'failed_count': failed_count,
        'results': results,
        'sync_log_id': str(sync_log.id)
    })


# ===== DOWNLOAD (Serveur → Client) =====

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sync_download(request):
    """
    Envoyer les changements au client
    """
    user = request.user
    
    # Récupérer le timestamp "since"
    since_param = request.query_params.get('since')
    entity_types = request.query_params.get('entity_types', '').split(',')
    
    if since_param:
        try:
            since = datetime.fromisoformat(since_param.replace('Z', '+00:00'))
        except:
            since = None
    else:
        since = None
    
    changes = {
        'timestamp': timezone.now().isoformat(),
        'changes': {}
    }
    
    # TODO: Récupérer les changements pour chaque type d'entité
    # Pour l'instant, retourner une structure vide
    
    if not entity_types or 'reminders' in entity_types:
        changes['changes']['reminders'] = []
    
    if not entity_types or 'documents' in entity_types:
        changes['changes']['documents'] = []
    
    if not entity_types or 'medical_records' in entity_types:
        changes['changes']['medical_records'] = []
    
    if not entity_types or 'consents' in entity_types:
        changes['changes']['consents'] = []
    
    return Response(changes)


# ===== CONFLITS =====

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resolve_conflict(request):
    """
    Résoudre un conflit de synchronisation
    """
    conflict_id = request.data.get('conflict_id')
    resolution = request.data.get('resolution')
    
    if not conflict_id or not resolution:
        return Response(
            {'error': 'conflict_id et resolution requis'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        conflict = SyncConflict.objects.get(
            id=conflict_id,
            user=request.user,
            resolution='PENDING'
        )
    except SyncConflict.DoesNotExist:
        return Response(
            {'error': 'Conflit non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Appliquer la résolution
    if resolution == 'USE_SERVER':
        conflict.resolved_version = conflict.server_version
    elif resolution == 'USE_CLIENT':
        conflict.resolved_version = conflict.client_version
    elif resolution == 'MERGE':
        # TODO: Implémenter logique de merge
        conflict.resolved_version = conflict.client_version
    
    conflict.resolution = resolution
    conflict.resolved_at = timezone.now()
    conflict.save()
    
    return Response({
        'resolved': True,
        'final_version': conflict.resolved_version,
        'resolution_used': resolution
    })


# ===== STATUT =====

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sync_status(request):
    """
    Statut de synchronisation de l'utilisateur
    """
    user = request.user
    
    # Dernière sync
    try:
        last_sync = LastSync.objects.get(user=user)
        last_sync_data = LastSyncSerializer(last_sync).data
    except LastSync.DoesNotExist:
        last_sync_data = None
    
    # Items en attente
    pending_uploads = SyncQueue.objects.filter(
        user=user,
        synced=False
    ).count()
    
    # Conflits en attente
    pending_conflicts = SyncConflict.objects.filter(
        user=user,
        resolution='PENDING'
    ).count()
    
    # Dernier log
    try:
        last_log = SyncLog.objects.filter(user=user).first()
        last_log_data = SyncLogSerializer(last_log).data if last_log else None
    except:
        last_log_data = None
    
    return Response({
        'last_sync': last_sync_data,
        'pending_uploads': pending_uploads,
        'pending_conflicts': pending_conflicts,
        'fully_synced': pending_uploads == 0 and pending_conflicts == 0,
        'last_log': last_log_data
    })


# ===== LOGS =====

class SyncLogListView(generics.ListAPIView):
    """Historique des synchronisations"""
    permission_classes = [IsAuthenticated]
    serializer_class = SyncLogSerializer
    
    def get_queryset(self):
        return SyncLog.objects.filter(user=self.request.user)


# ===== CONFLITS =====

class SyncConflictListView(generics.ListAPIView):
    """Liste des conflits en attente"""
    permission_classes = [IsAuthenticated]
    serializer_class = SyncConflictSerializer
    
    def get_queryset(self):
        return SyncConflict.objects.filter(
            user=self.request.user,
            resolution='PENDING'
        )
