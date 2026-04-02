import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('doctors', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HealthTip',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('category', models.CharField(
                    choices=[
                        ('NUTRITION', 'Nutrition'),
                        ('SPORT', 'Sport & Activité physique'),
                        ('SANTE_MENTALE', 'Santé mentale'),
                        ('PREVENTION', 'Prévention & Dépistage'),
                        ('MEDICAMENT', 'Médicaments'),
                        ('HYGIENE', 'Hygiène'),
                        ('GROSSESSE', 'Grossesse & Maternité'),
                        ('ENFANT', 'Santé enfant'),
                        ('AUTRE', 'Autre'),
                    ],
                    default='AUTRE', max_length=30,
                )),
                ('visibility', models.CharField(
                    choices=[
                        ('ALL', 'Tout le monde'),
                        ('CITY', 'Une ville'),
                        ('DISTRICT', 'Des quartiers'),
                    ],
                    default='ALL', max_length=20,
                )),
                ('target_city', models.CharField(blank=True, max_length=100)),
                ('target_districts', models.JSONField(blank=True, default=list)),
                ('views_count', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('published_by', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='health_tips',
                    to='doctors.healthcarestaff',
                )),
            ],
            options={
                'verbose_name': 'Astuce Santé',
                'verbose_name_plural': 'Astuces Santé',
                'db_table': 'health_tips',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='healthtip',
            index=models.Index(fields=['visibility', 'target_city'], name='health_tips_visibil_idx'),
        ),
        migrations.AddIndex(
            model_name='healthtip',
            index=models.Index(fields=['is_active', 'created_at'], name='health_tips_active_idx'),
        ),
    ]
