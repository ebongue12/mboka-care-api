from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Q
from .models import Consent, PatientFollower, EmergencyAccess
from .serializers import (
    ConsentSerializer,
    PatientFollowerSerializer,
    EmergencyAccessSerializer
)

# ===== CONSENTEMENTS =====

class ConsentGivenListView(generics.ListAPIView):
    """Liste des consentements donnés par le patient"""
    permission_classes = [IsAuthenticated]
    serializer_class = ConsentSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'patient_profile'):
            return Consent.objects.filter(
                patient=user.patient_profile,
                active=True
            )
        return Consent.objects.none()


class ConsentReceivedListView(generics.ListAPIView):
    """Liste des consentements reçus (pour médecins)"""
    permission_classes = [IsAuthenticated]
    serializer_class = ConsentSerializer
    
    def get_queryset(self):
        return Consent.objects.filter(
            granted_to=self.request.user,
            active=True
        )


class ConsentCreateView(generics.CreateAPIView):
    """Donner un consentement"""
    permission_classes = [IsAuthenticated]
    serializer_class = ConsentSerializer
    
    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'patient_profile'):
            serializer.save(patient=user.patient_profile)


class ConsentRevokeView(generics.DestroyAPIView):
    """Révoquer un consentement"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'patient_profile'):
            return Consent.objects.filter(
                patient=user.patient_profile,
                active=True
            )
        return Consent.objects.none()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.active = False
        instance.revoked_at = timezone.now()
        instance.revoked_by = request.user
        instance.save()
        
        return Response({
            'message': 'Consentement révoqué avec succès'
        }, status=status.HTTP_204_NO_CONTENT)


# ===== FOLLOWERS (PROCHES) =====

class FollowerListCreateView(generics.ListCreateAPIView):
    """Liste et ajout de followers"""
    permission_classes = [IsAuthenticated]
    serializer_class = PatientFollowerSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'patient_profile'):
            return PatientFollower.objects.filter(
                patient=user.patient_profile,
                active=True
            )
        return PatientFollower.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'patient_profile'):
   
            serializer.save(patient=user.patient_profile)


class FollowerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail, modification, suppression follower"""
    permission_classes = [IsAuthenticated]
    serializer_class = PatientFollowerSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'patient_profile'):
            return PatientFollower.objects.filter(
                patient=user.patient_profile,
                active=True
            )
        return PatientFollower.objects.none()
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.active = False
        instance.deactivated_at = timezone.now()
        instance.save()


# ===== ACCÈS D'URGENCE =====

class EmergencyAccessCreateView(generics.CreateAPIView):
    """Enregistrer un accès d'urgence (mode "Je veux aider")"""
    permission_classes = [AllowAny]  # Pas d'authentification requise
    serializer_class = EmergencyAccessSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Si l'utilisateur est connecté, l'enregistrer
        if request.user.is_authenticated:
            serializer.validated_data['helper_user'] = request.user
        
        emergency_access = serializer.save()
        
        # TODO: Envoyer notification au patient
        
        return Response({
            'message': 'Accès d\'urgence enregistré',
            'access_id': str(emergency_access.id)
        }, status=status.HTTP_201_CREATED)


class EmergencyAccessListView(generics.ListAPIView):
    """Historique des accès d'urgence"""
    permission_classes = [IsAuthenticated]
    serializer_class = EmergencyAccessSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'patient_profile'):
            return EmergencyAccess.objects.filter(
                Q(patient=user.patient_profile) |
                Q(family_member__family_chief=user.patient_profile)
            )
        return EmergencyAccess.objects.none()
