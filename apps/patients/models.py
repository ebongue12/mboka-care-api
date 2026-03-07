import uuid
from django.db import models
from apps.accounts.models import User

class PatientProfile(models.Model):
    """
    Profil patient MBOKA-CARE
    """
    ACCOUNT_TYPE_CHOICES = (
        ('INDIVIDUAL', 'Individuel'),
        ('FAMILY_CHIEF', 'Chef de famille'),
    )
    
    BLOOD_GROUP_CHOICES = (
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    )
    
    # Identifiant unique
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Lien vers User
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='patient_profile'
    )
    
    # Identité complète
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=100)
    country_of_birth = models.CharField(max_length=100)
    
    # Localisation résidence
    country_residence = models.CharField(max_length=100)
    city_residence = models.CharField(max_length=100)
    district_residence = models.CharField(max_length=100)
    
    # Informations médicales de base
    blood_group = models.CharField(
        max_length=5, 
        choices=BLOOD_GROUP_CHOICES, 
        null=True, 
        blank=True
    )
    
    # Données critiques (Niveau 1 - QR Code)
    chronic_conditions = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    emergency_notes = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    
    # Type de compte
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
        default='INDIVIDUAL'
    )
    
    # QR Code
    qr_public_payload = models.JSONField(default=dict, blank=True)
    qr_code_image = models.ImageField(
        upload_to='qr_codes/', 
        null=True, 
        blank=True
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'patient_profiles'
        verbose_name = 'Profil Patient'
        verbose_name_plural = 'Profils Patients'
        indexes = [
            models.Index(fields=['account_type']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """Calcule l'âge"""
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def generate_qr_payload(self):
        """Génère le payload pour QR Code (Niveau 1)"""
        return {
            'patient_id': str(self.id),
            'name': self.full_name,
            'age': self.age,
            'blood_group': self.blood_group,
            'allergies': self.allergies,
            'chronic_conditions': self.chronic_conditions,
            'emergency_contact': self.emergency_contact_phone,
            'emergency_notes': self.emergency_notes,
            'last_updated': self.updated_at.isoformat(),
        }


class FamilyMember(models.Model):
    """
    Membre de famille (max 10 par chef de famille)
    """
    RELATION_CHOICES = (
        ('CHILD', 'Enfant'),
        ('SPOUSE', 'Conjoint(e)'),
        ('PARENT', 'Parent'),
        ('SIBLING', 'Frère/Sœur'),
        ('OTHER', 'Autre'),
    )
    
    BLOOD_GROUP_CHOICES = PatientProfile.BLOOD_GROUP_CHOICES
    
    # Identifiant
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Chef de famille
    family_chief = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name='family_members'
    )
    
    # Identité complète
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=100)
    country_of_birth = models.CharField(max_length=100)
    
    # Localisation
    country_residence = models.CharField(max_length=100)
    city_residence = models.CharField(max_length=100)
    district_residence = models.CharField(max_length=100)
    
    # Relation
    relation = models.CharField(
        max_length=20,
        choices=RELATION_CHOICES,
        default='OTHER'
    )
    
    # Informations médicales
    blood_group = models.CharField(
        max_length=5, 
        choices=BLOOD_GROUP_CHOICES, 
        blank=True
    )
    chronic_conditions = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    emergency_notes = models.TextField(blank=True)
    
    # QR Code
    qr_public_payload = models.JSONField(default=dict, blank=True)
    qr_code_image = models.ImageField(
        upload_to='qr_codes/family/', 
        null=True, 
        blank=True
    )
    
    # Statut
    is_active = models.BooleanField(default=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'family_members'
        verbose_name = 'Membre de Famille'
        verbose_name_plural = 'Membres de Famille'
        indexes = [
            models.Index(fields=['family_chief', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_relation_display()})"
    
    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def generate_qr_payload(self):
        """Génère QR Code Niveau 1"""
        return {
            'member_id': str(self.id),
            'family_chief_id': str(self.family_chief.id),
            'name': self.full_name,
            'age': self.age,
            'blood_group': self.blood_group,
            'allergies': self.allergies,
            'chronic_conditions': self.chronic_conditions,
            'emergency_notes': self.emergency_notes,
            'relation': self.get_relation_display(),
            'last_updated': self.updated_at.isoformat(),
        }
