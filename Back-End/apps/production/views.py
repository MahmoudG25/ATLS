from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import HarvestReport, SortingReport
from .serializers import HarvestReportSerializer, SortingReportSerializer
from services.production_workflows import HarvestWorkflowService, SortingWorkflowService


class HarvestReportViewSet(viewsets.ModelViewSet):
    serializer_class = HarvestReportSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["location", "season", "status", "is_partial"]
    search_fields = ["location__name", "notes"]
    ordering_fields = ["harvest_date", "created_at"]

    def get_queryset(self):
        return HarvestReport.objects.filter(company=self.request.user.company)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        try:
            report = HarvestWorkflowService.submit_report(pk)
            return Response(HarvestReportSerializer(report).data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def finalize(self, request, pk=None):
        try:
            report = HarvestWorkflowService.finalize_report(pk, request.user)
            return Response(HarvestReportSerializer(report).data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SortingReportViewSet(viewsets.ModelViewSet):
    serializer_class = SortingReportSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["harvest_report", "status"]
    ordering_fields = ["processing_date"]

    def get_queryset(self):
        return SortingReport.objects.filter(company=self.request.user.company)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)

    @action(detail=True, methods=["post"])
    def finalize(self, request, pk=None):
        try:
            report = SortingWorkflowService.finalize_report(pk, request.user)
            return Response(SortingReportSerializer(report).data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
