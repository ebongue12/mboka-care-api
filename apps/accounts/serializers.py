from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'email', 'first_name', 'last_name',
                  'date_of_birth', 'country', 'city', 'neighborhood',
                  'user_type', 'is_phone_verified', 'created_at']
        read_only_fields = ['id', 'is_phone_verified', 'created_at']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['phone_number', 'email', 'password', 'password2',
                  'first_name', 'last_name', 'date_of_birth',
                  'country', 'city', 'neighborhood', 'user_type']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)
