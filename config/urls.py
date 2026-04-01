from django.contrib import admin
from django.urls import path, include
from config.setup_view import run_setup
from config.create_admin import create_superuser

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__setup__/', run_setup),
    path('__create_admin__/', create_superuser),
    
    # API endpoints
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/patients/', include('apps.patients.urls')),
    path('api/doctors/', include('apps.doctors.urls')),
    path('api/healthcare/', include('apps.doctors.urls')),
    path('api/medical/', include('apps.medical.urls')),
    path('api/reminders/', include('apps.reminders.urls')),
    path('api/notifications/', include('apps.notifications.urls')),

    # Portail Admin Personnel de Santé
    path('portail-admin/', include('apps.web_admin.urls')),
]
