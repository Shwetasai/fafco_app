from django.urls import path
from .views import PartListCreateAPIView, PartDetailAPIView, PartcsvListView

urlpatterns = [
    path('parts/', PartListCreateAPIView.as_view(), name='part-list-create'),
    path('parts/<int:part_id>/', PartDetailAPIView.as_view(), name='part-detail'),
    path('partcsv/', PartcsvListView.as_view(), name='partcsv-list'),
]
