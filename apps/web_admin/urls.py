from django.urls import path
from . import views

app_name = 'web_admin'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    path('staff/<uuid:staff_id>/', views.staff_detail, name='staff_detail'),
    path('staff/<uuid:staff_id>/verify/', views.verify_staff, name='verify_staff'),
    path('staff/<uuid:staff_id>/reject/', views.reject_staff, name='reject_staff'),
]
