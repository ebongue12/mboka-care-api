import os
from django.http import JsonResponse, HttpResponseForbidden
from apps.accounts.models import User


def create_superuser(request):
    """Crée un superuser — protégé par clé secrète."""
    key = request.GET.get('key', '') or request.headers.get('X-Setup-Key', '')
    expected = os.environ.get('SETUP_SECRET_KEY', '')
    if not expected or key != expected:
        return HttpResponseForbidden('Accès refusé.')

    phone = request.GET.get('phone', '+237612345678')
    email = request.GET.get('email', 'admin@mboka.com')
    password = request.GET.get('password', 'Admin@2026')

    try:
        if User.objects.filter(phone=phone).exists():
            return JsonResponse({
                'status': 'exists',
                'message': f'Utilisateur {phone} existe déjà',
            })

        User.objects.create_superuser(phone=phone, email=email, password=password)

        return JsonResponse({
            'status': 'success',
            'message': 'Superuser créé avec succès',
            'phone': phone,
            'email': email,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)}, status=500)
