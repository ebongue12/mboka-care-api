import uuid
from django.db import models
from apps.accounts.models import User


class HealthcareStaff(models.Model):
    """Personnel de santé (tous types)"""
    STAFF_TYPES = [
        ('MEDECIN', 'Médecin'),
        ('INFIRMIER', 'Infirmier/Infirmière'),
        ('SECOURISTE', 'Secouriste'),
        ('AIDE_SOIGNANT', 'Aide-soignant(e)'),
        ('SAGE_FEMME', 'Sage-femme'),
    ]

    VERIFICATION_STATUSES = [
        ('PENDING', 'En attente'),
        ('VERIFIED', 'Vérifié'),
        ('REJECTED', 'Rejeté'),
    ]

    PATIENTS_RANGE_CHOICES = [
        ('0-100', 'Moins de 100'),
        ('100-500', '100 à 500'),
        ('500-1000', '500 à 1000'),
        ('1000+', 'Plus de 1000'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='healthcare_staff'
    )
    staff_type = models.CharField(max_length=20, choices=STAFF_TYPES)

    # Identité
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    # Lieu d'exercice
    city = models.CharField(max_length=100)
    establishment = models.CharField(max_length=200)

    # Expérience
    specialty = models.CharField(max_length=100, blank=True)
    years_experience = models.IntegerField(default=0)
    patients_treated_range = models.CharField(
        max_length=20,
        choices=PATIENTS_RANGE_CHOICES,
        default='0-100'
    )

    # Vérification
    verified = models.BooleanField(default=False)
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUSES,
        default='PENDING'
    )
    diploma_document = models.FileField(upload_to='staff_diplomas/', null=True, blank=True)
    work_contract = models.FileField(upload_to='staff_contracts/', null=True, blank=True)
    medical_order_number = models.CharField(max_length=100, blank=True)

    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_staff'
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    # Stats
    total_scans = models.IntegerField(default=0)
    total_patients_followed = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'healthcare_staff'
        verbose_name = 'Personnel de Santé'
        verbose_name_plural = 'Personnels de Santé'

    def __str__(self):
        return f"{self.get_staff_type_display()} {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class QRScanLog(models.Model):
    """Historique scans QR Code"""
    MOTIF_CHOICES = [
        ('URGENCE', 'Urgence'),
        ('CONSULTATION', 'Consultation'),
        ('SUIVI', 'Suivi'),
        ('AUTRE', 'Autre'),
    ]

    healthcare_staff = models.ForeignKey(
        HealthcareStaff,
        on_delete=models.CASCADE,
        related_name='scans'
    )
    patient = models.ForeignKey(
        'patients.PatientProfile',
        on_delete=models.CASCADE,
        related_name='scans_received'
    )

    timestamp = models.DateTimeField(auto_now_add=True)
    motif = models.CharField(max_length=20, choices=MOTIF_CHOICES)
    notes = models.TextField(blank=True)
    notification_sent = models.BooleanField(default=False)

    class Meta:
        db_table = 'qr_scan_logs'
        ordering = ['-timestamp']
        verbose_name = 'Log Scan QR'
        verbose_name_plural = 'Logs Scans QR'

    def __str__(self):
        return f"{self.healthcare_staff} → {self.patient} ({self.motif}) {self.timestamp:%Y-%m-%d %H:%M}"


class PatientFollowUp(models.Model):
    """Patients suivis par le personnel de santé"""
    healthcare_staff = models.ForeignKey(
        HealthcareStaff,
        on_delete=models.CASCADE,
        related_name='followed_patients'
    )
    patient = models.ForeignKey(
        'patients.PatientProfile',
        on_delete=models.CASCADE,
        related_name='following_staff'
    )

    added_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'patient_follow_ups'
        unique_together = ['healthcare_staff', 'patient']
        verbose_name = 'Suivi Patient'
        verbose_name_plural = 'Suivis Patients'

    def __str__(self):
        return f"{self.healthcare_staff} suit {self.patient}"
