from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Inscription d'un nouvel utilisateur"""
    phone = request.data.get('phone')
    email = request.data.get('email')
    password = request.data.get('password')
    role = request.data.get('role', 'PATIENT')
    
    # Vérifier si l'utilisateur existe
    if User.objects.filter(phone=phone).exists():
        return Response(
            {'error': 'Ce numéro est déjà utilisé'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Créer l'utilisateur
    user = User.objects.create_user(
        phone=phone,
        email=email,
        password=password,
        role=role
    )
    
    # Générer les tokens JWT
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Connexion d'un utilisateur"""
    phone = request.data.get('phone')
    password = request.data.get('password')
    
    # Authentifier l'utilisateur
    user = authenticate(username=phone, password=password)
    
    if user is None:
        return Response(
            {'error': 'Téléphone ou mot de passe incorrect'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Générer les tokens JWT
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data
    })


@api_view(['POST'])
def logout(request):
    """Déconnexion (blacklist du token si configuré)"""
    return Response({'message': 'Déconnecté avec succès'})
