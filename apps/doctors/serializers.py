from rest_framework import serializers
from .models import HealthcareStaff, QRScanLog, PatientFollowUp


class HealthcareStaffSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    staff_type_display = serializers.CharField(source='get_staff_type_display', read_only=True)

    class Meta:
        model = HealthcareStaff
        fields = [
            'id', 'staff_type', 'staff_type_display', 'first_name', 'last_name',
            'full_name', 'phone', 'email', 'city', 'establishment',
            'specialty', 'years_experience', 'patients_treated_range',
            'verified', 'verification_status', 'medical_order_number',
            'total_scans', 'total_patients_followed', 'created_at',
        ]
        read_only_fields = [
            'id', 'verified', 'verification_status',
            'total_scans', 'total_patients_followed', 'created_at',
        ]


class HealthcareStaffRegistrationSerializer(serializers.Serializer):
    # Champs User
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    # Champs HealthcareStaff
    staff_type = serializers.ChoiceField(choices=HealthcareStaff.STAFF_TYPES)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20)
    email = serializers.EmailField()
    city = serializers.CharField(max_length=100)
    establishment = serializers.CharField(max_length=200)
    specialty = serializers.CharField(max_length=100, required=False, allow_blank=True)
    years_experience = serializers.IntegerField(default=0, min_value=0)
    patients_treated_range = serializers.ChoiceField(
        choices=HealthcareStaff.PATIENTS_RANGE_CHOICES,
        default='0-100'
    )
    medical_order_number = serializers.CharField(max_length=100, required=False, allow_blank=True)
    diploma_document = serializers.FileField(required=False)
    work_contract = serializers.FileField(required=False)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password': 'Les mots de passe ne correspondent pas.'})
        return attrs

    def validate_phone(self, value):
        from apps.accounts.models import User
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError('Un compte avec ce numéro existe déjà.')
        return value

    def create(self, validated_data):
        from apps.accounts.models import User

        password = validated_data.pop('password')
        validated_data.pop('password_confirm')

        user = User.objects.create_user(
            phone=validated_data['phone'],
            email=validated_data['email'],
            password=password,
            role='MEDECIN',
        )

        staff = HealthcareStaff.objects.create(user=user, **validated_data)
        return staff


class QRScanLogSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='healthcare_staff.full_name', read_only=True)
    staff_type = serializers.CharField(source='healthcare_staff.get_staff_type_display', read_only=True)
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = QRScanLog
        fields = ['id', 'staff_name', 'staff_type', 'patient_name', 'timestamp', 'motif', 'notes']

    def get_patient_name(self, obj):
        return f"{obj.patient.user.first_name} {obj.patient.user.last_name}"


class PatientFollowUpSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    patient_id = serializers.UUIDField(source='patient.id', read_only=True)

    class Meta:
        model = PatientFollowUp
        fields = ['id', 'patient_id', 'patient_name', 'added_at', 'notes', 'is_active']

    def get_patient_name(self, obj):
        return f"{obj.patient.user.first_name} {obj.patient.user.last_name}"
