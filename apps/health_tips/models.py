import uuid
from django.db import models


class HealthTip(models.Model):
    """
    Astuce ou conseil santé publié par un professionnel de santé.
    Visible selon la portée choisie : tout le monde, une ville ou des quartiers.
    """

    CATEGORY_CHOICES = [
        ('NUTRITION', 'Nutrition'),
        ('SPORT', 'Sport & Activité physique'),
        ('SANTE_MENTALE', 'Santé mentale'),
        ('PREVENTION', 'Prévention & Dépistage'),
        ('MEDICAMENT', 'Médicaments'),
        ('HYGIENE', 'Hygiène'),
        ('GROSSESSE', 'Grossesse & Maternité'),
        ('ENFANT', 'Santé enfant'),
        ('AUTRE', 'Autre'),
    ]

    VISIBILITY_ALL = 'ALL'
    VISIBILITY_CITY = 'CITY'
    VISIBILITY_DISTRICT = 'DISTRICT'
    VISIBILITY_CHOICES = [
        ('ALL', 'Tout le monde'),
        ('CITY', 'Une ville'),
        ('DISTRICT', 'Des quartiers'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    published_by = models.ForeignKey(
        'doctors.HealthcareStaff',
        on_delete=models.CASCADE,
        related_name='health_tips',
    )

    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='AUTRE')

    # Ciblage géographique
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='ALL')
    target_city = models.CharField(max_length=100, blank=True)
    target_districts = models.JSONField(default=list, blank=True)

    # Métriques (rétention)
    views_count = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'health_tips'
        ordering = ['-created_at']
        verbose_name = 'Astuce Santé'
        verbose_name_plural = 'Astuces Santé'
        indexes = [
            models.Index(fields=['visibility', 'target_city']),
            models.Index(fields=['is_active', 'created_at']),
        ]

    def __str__(self):
        return self.title

    def get_target_patients(self):
        """Retourne les patients correspondant au ciblage géographique."""
        from apps.patients.models import PatientProfile
        if self.visibility == self.VISIBILITY_ALL:
            return PatientProfile.objects.all()
        elif self.visibility == self.VISIBILITY_CITY:
            return PatientProfile.objects.filter(
                city_residence__iexact=self.target_city
            )
        elif self.visibility == self.VISIBILITY_DISTRICT:
            from django.db.models import Q
            q = Q()
            for district in self.target_districts:
                q |= Q(district_residence__iexact=district)
            if self.target_city:
                return PatientProfile.objects.filter(
                    city_residence__iexact=self.target_city
                ).filter(q)
            return PatientProfile.objects.filter(q)
        return PatientProfile.objects.none()
