from django.urls import path
from .views import DoctorProfileMeView, DoctorProfileListView

urlpatterns = [
    path('me/', DoctorProfileMeView.as_view(), name='doctor-me'),
    path('', DoctorProfileListView.as_view(), name='doctor-list'),
]
