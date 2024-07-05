from django.urls import path
from .views import ClaimListCreateAPIView, ClaimRetrieveUpdateAPIView,ClaimDocumentUploadAPIView

urlpatterns = [
    path('list/', ClaimListCreateAPIView.as_view(), name='claim-list-create'),
    path('claims/<int:pk>/', ClaimRetrieveUpdateAPIView.as_view(), name='claim-detail'),
    path('claims/<int:pk>/upload/', ClaimDocumentUploadAPIView.as_view(), name='claim-document-upload'),
    path('claims/<int:pk>/documents/<int:doc_pk>/', ClaimDocumentUploadAPIView.as_view(), name='claim-document-detail'),

]
