from django.urls import path
from .views import (
    HealthCategoryListView,
    HealthContentListView,
    HealthContentDetailView,
    UserProgressUpdateView,
    user_stats,
    SavedContentListView,
    SavedContentCreateView,
    SavedContentDeleteView
)

urlpatterns = [
    # Catégories
    path('categories/', HealthCategoryListView.as_view(), name='health-categories'),
    
    # Contenus
    path('contents/', HealthContentListView.as_view(), name='health-contents'),
    path('contents/<slug:slug>/', HealthContentDetailView.as_view(), name='health-content-detail'),
    
    # Progression
    path('progress/', UserProgressUpdateView.as_view(), name='user-progress'),
    path('stats/', user_stats, name='user-stats'),
    
    # Contenus enregistrés
    path('saved/', SavedContentListView.as_view(), name='saved-contents'),
    path('saved/create/', SavedContentCreateView.as_view(), name='saved-content-create'),
    path('saved/<uuid:pk>/', SavedContentDeleteView.as_view(), name='saved-content-delete'),
]
