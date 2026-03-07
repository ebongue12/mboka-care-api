from django.contrib import admin
from django.urls import path
from config.setup_view import run_setup
from config.create_admin import create_superuser

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__setup__/', run_setup),
    path('__create_admin__/', create_superuser),
]
