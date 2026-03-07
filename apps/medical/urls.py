from django.urls import path
from .views import (
    MedicalRecordListCreateView,
    MedicalRecordDetailView,
    MedicalDocumentListCreateView,
    MedicalDocumentDetailView,
    MedicalDocumentDownloadView
)

urlpatterns = [
    # Dossiers médicaux
    path('records/', MedicalRecordListCreateView.as_view(), name='medical-records'),
    path('records/<uuid:pk>/', MedicalRecordDetailView.as_view(), name='medical-record-detail'),
    
    # Documents
    path('documents/', MedicalDocumentListCreateView.as_view(), name='medical-documents'),
    path('documents/<uuid:pk>/', MedicalDocumentDetailView.as_view(), name='medical-document-detail'),
    path('documents/<uuid:pk>/download/', MedicalDocumentDownloadView.as_view(), name='medical-document-download'),
]
