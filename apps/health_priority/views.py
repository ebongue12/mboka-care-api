from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from django.db.models import Q, Prefetch
from .models import HealthCategory, HealthContent, UserContentProgress, SavedContent
from .serializers import (
    HealthCategorySerializer,
    HealthContentListSerializer,
    HealthContentDetailSerializer,
    UserContentProgressSerializer,
    SavedContentSerializer
)

# ===== CATÉGORIES =====

class HealthCategoryListView(generics.ListAPIView):
    """Liste des catégories santé"""
    permission_classes = [IsAuthenticated]
    serializer_class = HealthCategorySerializer
    queryset = HealthCategory.objects.filter(is_active=True)


# ===== CONTENUS =====

class HealthContentListView(generics.ListAPIView):
    """Liste des contenus santé"""
    permission_classes = [IsAuthenticated]
    serializer_class = HealthContentListSerializer
    
    def get_queryset(self):
        queryset = HealthContent.objects.filter(
            is_active=True,
            published_at__isnull=False
        )
        
        # Filtres
        category_id = self.request.query_params.get('category')
        content_type = self.request.query_params.get('type')
        search = self.request.query_params.get('search')
        featured = self.request.query_params.get('featured')
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        if content_type:
            queryset = queryset.filter(content_type=content_type)
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__icontains=search)
            )
        
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        return queryset


class HealthContentDetailView(generics.RetrieveAPIView):
    """Détail d'un contenu"""
    permission_classes = [IsAuthenticated]
    serializer_class = HealthContentDetailSerializer
    lookup_field = 'slug'
    
    def get_queryset(self):
        return HealthContent.objects.filter(
            is_active=True,
            published_at__isnull=False
        )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Incrémenter le compteur de vues
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        
        # Créer ou récupérer la progression
        progress, created = UserContentProgress.objects.get_or_create(
            user=request.user,
            content=instance
        )
        
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        # Ajouter la progression
        data['user_progress'] = UserContentProgressSerializer(progress).data
        
        return Response(data)


# ===== PROGRESSION =====

class UserProgressUpdateView(generics.UpdateAPIView):
    """Mettre à jour la progression"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserContentProgressSerializer
    
    def get_queryset(self):
        return UserContentProgress.objects.filter(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        content_id = request.data.get('content_id')
        
        if not content_id:
            return Response(
                {'error': 'content_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            content = HealthContent.objects.get(id=content_id, is_active=True)
        except HealthContent.DoesNotExist:
            return Response(
                {'error': 'Contenu non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        progress, created = UserContentProgress.objects.get_or_create(
            user=request.user,
            content=content
        )
        
        # Mettre à jour
        progress_percentage = request.data.get('progress_percentage', progress.progress_percentage)
        last_watched_position = request.data.get('last_watched_position', progress.last_watched_position)
        
        progress.progress_percentage = progress_percentage
        progress.last_watched_position = last_watched_position
        
        # Marquer comme complété si >= 90%
        if progress_percentage >= 90 and not progress.completed:
            progress.completed = True
            progress.completed_at = timezone.now()
        
        progress.save()
        
        serializer = self.get_serializer(progress)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_stats(request):
    """Statistiques de l'utilisateur"""
    user = request.user
    
    total_contents = HealthContent.objects.filter(is_active=True).count()
    
    progress = UserContentProgress.objects.filter(user=user)
    started_count = progress.count()
    completed_count = progress.filter(completed=True).count()
    
    saved_count = SavedContent.objects.filter(user=user).count()
    
    return Response({
        'total_contents': total_contents,
        'started_count': started_count,
        'completed_count': completed_count,
        'saved_count': saved_count,
        'completion_rate': round((completed_count / started_count * 100) if started_count > 0 else 0, 1)
    })


# ===== CONTENUS ENREGISTRÉS =====

class SavedContentListView(generics.ListAPIView):
    """Liste des contenus enregistrés"""
    permission_classes = [IsAuthenticated]
    serializer_class = SavedContentSerializer
    
    def get_queryset(self):
        return SavedContent.objects.filter(user=self.request.user)


class SavedContentCreateView(generics.CreateAPIView):
    """Enregistrer un contenu"""
    permission_classes = [IsAuthenticated]
    serializer_class = SavedContentSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SavedContentDeleteView(generics.DestroyAPIView):
    """Supprimer un contenu enregistré"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SavedContent.objects.filter(user=self.request.user)
