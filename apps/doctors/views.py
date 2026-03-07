from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import DoctorProfile
from .serializers import DoctorProfileSerializer

class DoctorProfileMeView(generics.RetrieveUpdateAPIView):
    """Profil médecin de l'utilisateur connecté"""
    permission_classes = [IsAuthenticated]
    serializer_class = DoctorProfileSerializer
    
    def get_object(self):
        return self.request.user.doctor_profile


class DoctorProfileListView(generics.ListAPIView):
    """Liste des médecins vérifiés"""
    permission_classes = [IsAuthenticated]
    serializer_class = DoctorProfileSerializer
    queryset = DoctorProfile.objects.filter(verified=True)
