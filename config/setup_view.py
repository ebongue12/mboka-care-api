from django.http import JsonResponse
from django.core.management import call_command
import io

def run_setup(request):
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
