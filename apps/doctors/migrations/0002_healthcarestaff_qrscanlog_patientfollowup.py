import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctors', '0001_initial'),
        ('patients', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HealthcareStaff',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('staff_type', models.CharField(choices=[('MEDECIN', 'Médecin'), ('INFIRMIER', 'Infirmier/Infirmière'), ('SECOURISTE', 'Secouriste'), ('AIDE_SOIGNANT', 'Aide-soignant(e)'), ('SAGE_FEMME', 'Sage-femme')], max_length=20)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('city', models.CharField(max_length=100)),
                ('establishment', models.CharField(max_length=200)),
                ('specialty', models.CharField(blank=True, max_length=100)),
                ('years_experience', models.IntegerField(default=0)),
                ('patients_treated_range', models.CharField(choices=[('0-100', 'Moins de 100'), ('100-500', '100 à 500'), ('500-1000', '500 à 1000'), ('1000+', 'Plus de 1000')], default='0-100', max_length=20)),
                ('verified', models.BooleanField(default=False)),
                ('verification_status', models.CharField(choices=[('PENDING', 'En attente'), ('VERIFIED', 'Vérifié'), ('REJECTED', 'Rejeté')], default='PENDING', max_length=20)),
                ('diploma_document', models.FileField(blank=True, null=True, upload_to='staff_diplomas/')),
                ('work_contract', models.FileField(blank=True, null=True, upload_to='staff_contracts/')),
                ('medical_order_number', models.CharField(blank=True, max_length=100)),
                ('total_scans', models.IntegerField(default=0)),
                ('total_patients_followed', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='healthcare_staff', to=settings.AUTH_USER_MODEL)),
                ('verified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='verified_staff', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Personnel de Santé',
                'verbose_name_plural': 'Personnels de Santé',
                'db_table': 'healthcare_staff',
            },
        ),
        migrations.CreateModel(
            name='QRScanLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('motif', models.CharField(choices=[('URGENCE', 'Urgence'), ('CONSULTATION', 'Consultation'), ('SUIVI', 'Suivi'), ('AUTRE', 'Autre')], max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('notification_sent', models.BooleanField(default=False)),
                ('healthcare_staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scans', to='doctors.healthcarestaff')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scans_received', to='patients.patientprofile')),
            ],
            options={
                'verbose_name': 'Log Scan QR',
                'verbose_name_plural': 'Logs Scans QR',
                'db_table': 'qr_scan_logs',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='PatientFollowUp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('healthcare_staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followed_patients', to='doctors.healthcarestaff')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following_staff', to='patients.patientprofile')),
            ],
            options={
                'verbose_name': 'Suivi Patient',
                'verbose_name_plural': 'Suivis Patients',
                'db_table': 'patient_follow_ups',
                'unique_together': {('healthcare_staff', 'patient')},
            },
        ),
    ]
