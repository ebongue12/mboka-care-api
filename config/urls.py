from django.contrib import admin
from django.urls import path
from config.setup_view import run_setup

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__setup__/', run_setup),
]
