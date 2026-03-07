from django.http import JsonResponse
from apps.accounts.models import User

def create_superuser(request):
    """Crée un superuser"""
    phone = request.GET.get('phone', '+237612345678')
    email = request.GET.get('email', 'admin@mboka.com')
    password = request.GET.get('password', 'Admin@2026')
    
    try:
        if User.objects.filter(phone=phone).exists():
            return JsonResponse({
                'status': 'exists',
                'message': f'Utilisateur {phone} existe déjà'
            })
        
        user = User.objects.create_superuser(
            phone=phone,
            email=email,
            password=password
        )
        
        return JsonResponse({
            'status': 'success',
            'message': f'Superuser créé avec succès',
            'phone': phone,
            'email': email
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)
