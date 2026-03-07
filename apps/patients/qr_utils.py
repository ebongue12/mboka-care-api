import qrcode
import json
import hashlib
from io import BytesIO
from django.core.files import File
from django.conf import settings

def generate_qr_payload(patient_profile=None, family_member=None):
    """
    Génère le payload JSON pour le QR Code (Niveau 1 uniquement)
    Données d'urgence accessibles OFFLINE
    """
    if patient_profile:
        payload = {
            'type': 'PATIENT',
            'patient_id': str(patient_profile.id),
            'name': patient_profile.full_name,
            'age': patient_profile.age,
            'blood_group': patient_profile.blood_group or '',
            'allergies': patient_profile.allergies or '',
            'chronic_conditions': patient_profile.chronic_conditions or '',
            'emergency_contact': patient_profile.emergency_contact_phone or '',
            'emergency_contact_name': patient_profile.emergency_contact_name or '',
            'emergency_notes': patient_profile.emergency_notes or '',
            'last_updated': patient_profile.updated_at.isoformat(),
        }
    elif family_member:
        payload = {
            'type': 'FAMILY_MEMBER',
            'member_id': str(family_member.id),
            'family_chief_id': str(family_member.family_chief.id),
            'name': family_member.full_name,
            'age': family_member.age,
            'relation': family_member.get_relation_display(),
            'blood_group': family_member.blood_group or '',
            'allergies': family_member.allergies or '',
            'chronic_conditions': family_member.chronic_conditions or '',
            'emergency_notes': family_member.emergency_notes or '',
            'last_updated': family_member.updated_at.isoformat(),
        }
    else:
        raise ValueError("Patient ou membre de famille requis")
    
    # Ajouter une signature pour vérifier l'intégrité
    payload_str = json.dumps(payload, sort_keys=True)
    signature = hashlib.sha256(payload_str.encode()).hexdigest()[:16]
    payload['signature'] = signature
    
    return payload


def generate_qr_code_image(payload):
    """
    Génère l'image QR Code à partir du payload
    """
    # Convertir le payload en JSON
    qr_data = json.dumps(payload)
    
    # Créer le QR Code
    qr = qrcode.QRCode(
        version=None,  # Auto-déterminer la taille
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Haute correction d'erreur
        box_size=10,
        border=4,
    )
    
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Générer l'image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Sauvegarder dans un buffer
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer


def save_qr_code(instance, payload):
    """
    Génère et sauvegarde le QR Code pour un patient ou membre
    """
    # Générer l'image
    buffer = generate_qr_code_image(payload)
    
    # Nom du fichier
    if hasattr(instance, 'family_chief'):
        # C'est un FamilyMember
        filename = f'qr_family_{instance.id}.png'
    else:
        # C'est un PatientProfile
        filename = f'qr_patient_{instance.id}.png'
    
    # Sauvegarder dans le modèle
    instance.qr_code_image.save(filename, File(buffer), save=False)
    instance.qr_public_payload = payload
    instance.save()
    
    return instancex
