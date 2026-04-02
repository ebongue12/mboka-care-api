import os
from django.http import JsonResponse, HttpResponseForbidden
from django.core.management import call_command
import io


def run_setup(request):
    # Protéger l'endpoint avec une clé secrète
    key = request.GET.get('key', '') or request.headers.get('X-Setup-Key', '')
    expected = os.environ.get('SETUP_SECRET_KEY', '')
    if not expected or key != expected:
        return HttpResponseForbidden('Accès refusé.')
    """Exécute les migrations et collectstatic"""
    output = io.StringIO()
    
    try:
        # Migrations
        call_command('migrate', stdout=output, interactive=False)
        migrations_output = output.getvalue()
        
        # Collectstatic
        output = io.StringIO()
        call_command('collectstatic', '--noinput', stdout=output)
        static_output = output.getvalue()
        
        return JsonResponse({
            'status': 'success',
            'migrations': migrations_output,
            'static': static_output
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)
