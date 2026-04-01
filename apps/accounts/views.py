from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    phone = request.data.get('phone')
    email = request.data.get('email')
    password = request.data.get('password')
    role = request.data.get('role', 'PATIENT')
    
    if User.objects.filter(phone=phone).exists():
        return Response({'error': 'Ce numéro est déjà utilisé'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(phone=phone, email=email, password=password, role=role)

    # Créer automatiquement le profil selon le rôle
    if role == 'PATIENT':
        from apps.patients.models import PatientProfile
        country = request.data.get('country', '') or request.data.get('country_residence', '')
        city = request.data.get('city', '') or request.data.get('city_residence', '')
        district = request.data.get('district', '') or request.data.get('district_residence', '')
        PatientProfile.objects.get_or_create(
            user=user,
            defaults={
                'first_name': request.data.get('first_name', ''),
                'last_name': request.data.get('last_name', ''),
                'date_of_birth': request.data.get('date_of_birth') or '2000-01-01',
                'place_of_birth': request.data.get('place_of_birth', '') or city,
                'country_of_birth': request.data.get('country_of_birth', '') or country,
                'country_residence': country,
                'city_residence': city,
                'district_residence': district,
            }
        )

    refresh = RefreshToken.for_user(user)

    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    phone = request.data.get('phone')
    password = request.data.get('password')
    
    if not phone or not password:
        return Response({'error': 'Téléphone et mot de passe requis'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(phone=phone)
    except User.DoesNotExist:
        return Response({'error': 'Téléphone ou mot de passe incorrect'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if not user.check_password(password):
        return Response({'error': 'Téléphone ou mot de passe incorrect'}, status=status.HTTP_401_UNAUTHORIZED)
    
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data
    })

@api_view(['POST'])
def logout(request):
    return Response({'message': 'Déconnecté avec succès'})
