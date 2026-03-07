from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import register_user, login_user, logout_user, user_profile

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', user_profile, name='user_profile'),
]
