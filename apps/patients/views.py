from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
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
