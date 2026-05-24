from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HarvestReportViewSet, SortingReportViewSet, HarvestAttachmentListCreate, HarvestAttachmentDetail

router = DefaultRouter()
router.register(r'harvest-reports', HarvestReportViewSet, basename='harvest-report')
router.register(r'sorting-reports', SortingReportViewSet, basename='sorting-report')

urlpatterns = [
    path('harvest-attachments/', HarvestAttachmentListCreate.as_view(), name='harvest-attachment-list'),
    path('harvest-attachments/<str:pk>/', HarvestAttachmentDetail.as_view(), name='harvest-attachment-detail'),
    path('', include(router.urls)),
]


