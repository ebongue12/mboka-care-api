from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.http import HttpResponse
from .models import PatientProfile, FamilyMember
from .qr_utils import generate_qr_payload, save_qr_code
import json

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_patient_qr(request):
    """
    Génère le QR Code pour le patient connecté
    """
    user = request.user
    
    if not hasattr(user, 'patient_profile'):
        return Response(
            {'error': 'Profil patient non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    patient = user.patient_profile
    
    # Générer le payload
    payload = generate_qr_payload(patient_profile=patient)
    
    # Sauvegarder le QR Code
    save_qr_code(patient, payload)
    
    # Retourner les informations
    return Response({
        'message': 'QR Code généré avec succès',
        'qr_code_url': request.build_absolute_uri(patient.qr_code_image.url) if patient.qr_code_image else None,
        'payload': payload,
        'emergency_data': {
            'name': payload['name'],
            'age': payload['age'],
            'blood_group': payload['blood_group'],
            'allergies': payload['allergies'],
            'chronic_conditions': payload['chronic_conditions'],
            'emergency_contact': payload['emergency_contact'],
            'emergency_contact_name': payload.get('emergency_contact_name', ''),
            'emergency_notes': payload['emergency_notes'],
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_family_member_qr(request, member_id):
    """
    Génère le QR Code pour un membre de famille
    """
    user = request.user
    
    if not hasattr(user, 'patient_profile'):
        return Response(
            {'error': 'Profil patient non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        member = FamilyMember.objects.get(
            id=member_id,
            family_chief=user.patient_profile,
            is_active=True
        )
    except FamilyMember.DoesNotExist:
        return Response(
            {'error': 'Membre de famille non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Générer le payload
    payload = generate_qr_payload(family_member=member)
    
    # Sauvegarder le QR Code
    save_qr_code(member, payload)
    
    # Retourner les informations
    return Response({
        'message': 'QR Code généré avec succès',
        'qr_code_url': request.build_absolute_uri(member.qr_code_image.url) if member.qr_code_image else None,
        'payload': payload,
        'emergency_data': {
            'name': payload['name'],
            'age': payload['age'],
            'relation': payload['relation'],
            'blood_group': payload['blood_group'],
            'allergies': payload['allergies'],
            'chronic_conditions': payload['chronic_conditions'],
            'emergency_notes': payload['emergency_notes'],
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def scan_qr_emergency(request):
    """
    Scanner un QR Code (mode "Je veux aider")
    Aucune authentification requise
    Fonctionne OFFLINE (le payload est dans le QR)
    """
    qr_payload = request.data.get('qr_payload')
    helper_name = request.data.get('helper_name', '')
    helper_phone = request.data.get('helper_phone', '')
    location = request.data.get('location', {})
    
    if not qr_payload:
        return Response(
            {'error': 'qr_payload requis'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Parser le payload JSON
        if isinstance(qr_payload, str):
            payload = json.loads(qr_payload)
        else:
            payload = qr_payload
        
        # Extraire les données d'urgence
        emergency_data = {
            'type': payload.get('type'),
            'name': payload.get('name'),
            'age': payload.get('age'),
            'blood_group': payload.get('blood_group'),
            'allergies': payload.get('allergies'),
            'chronic_conditions': payload.get('chronic_conditions'),
            'emergency_contact': payload.get('emergency_contact'),
            'emergency_contact_name': payload.get('emergency_contact_name', ''),
            'emergency_notes': payload.get('emergency_notes'),
            'last_updated': payload.get('last_updated'),
        }
        
        if payload.get('type') == 'FAMILY_MEMBER':
            emergency_data['relation'] = payload.get('relation')
        
        # TODO: Enregistrer l'accès d'urgence dans EmergencyAccess
        # (nécessite la connexion pour sync plus tard)
        
        return Response({
            'success': True,
            'emergency_data': emergency_data,
            'message': 'Données d\'urgence récupérées avec succès'
        })
        
    except json.JSONDecodeError:
        return Response(
            {'error': 'Payload QR Code invalide'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Erreur lors du scan: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_patient_qr(request):
    """
    Récupérer le QR Code existant du patient
    """
    user = request.user
    
    if not hasattr(user, 'patient_profile'):
        return Response(
            {'error': 'Profil patient non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    patient = user.patient_profile
    
    if not patient.qr_code_image:
        return Response(
            {'message': 'QR Code pas encore généré', 'exists': False},
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response({
        'exists': True,
        'qr_code_url': request.build_absolute_uri(patient.qr_code_image.url),
        'payload': patient.qr_public_payload,
        'last_updated': patient.updated_at.isoformat()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_family_member_qr(request, member_id):
    """
    Récupérer le QR Code existant d'un membre de famille
    """
    user = request.user
    
    if not hasattr(user, 'patient_profile'):
        return Response(
            {'error': 'Profil patient non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        member = FamilyMember.objects.get(
            id=member_id,
            family_chief=user.patient_profile,
            is_active=True
        )
    except FamilyMember.DoesNotExist:
        return Response(
            {'error': 'Membre de famille non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not member.qr_code_image:
        return Response(
            {'message': 'QR Code pas encore généré', 'exists': False},
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response({
        'exists': True,
        'qr_code_url': request.build_absolute_uri(member.qr_code_image.url),
        'payload': member.qr_public_payload,
        'last_updated': member.updated_at.isoformat()
    })
