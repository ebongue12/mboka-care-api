import uuid
from django.db import models
from apps.accounts.models import User

class DoctorProfile(models.Model):
    """Profil médecin"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Lien vers User
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    
    # Identité
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    # Informations professionnelles
    specialization = models.CharField(max_length=200)
    license_number = models.CharField(max_length=100, unique=True)
    hospital_affiliation = models.CharField(max_length=200, blank=True)
    
    # Localisation cabinet
    practice_country = models.CharField(max_length=100)
    practice_city = models.CharField(max_length=100)
    practice_district = models.CharField(max_length=100)
    practice_address = models.TextField(blank=True)
    
    # Vérification
    verified = models.BooleanField(default=False)
    verification_document = models.FileField(
        upload_to='doctor_verification/',
        null=True,
        blank=True
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_doctors'
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctor_profiles'
        verbose_name = 'Profil Médecin'
        verbose_name_plural = 'Profils Médecins'
    
    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"Dr. {self.first_name} {self.last_name}"
