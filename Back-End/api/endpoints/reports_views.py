from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum
from apps.reports.models import (
    Operation, DailyTaskReport, FertilizationReport, IrrigationReport,
    CustomFieldDefinition, CustomFieldValue, ReportDropdownOption
)
from serializers.reports_serializers import (
    OperationSerializer,
    DailyTaskReportSerializer,
    FertilizationReportSerializer,
    IrrigationReportSerializer,
    CustomFieldDefinitionSerializer,
    CustomFieldValueSerializer,
    ReportDropdownOptionSerializer
)
from apps.reports.permissions import IsManagerOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
import django_filters

class DailyTaskFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='report_date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='report_date', lookup_expr='lte')
    
    class Meta:
        model = DailyTaskReport
        fields = ['engineer', 'report_date', 'sector', 'operation']

class OperationListView(generics.ListAPIView):
    queryset = Operation.objects.all()
    serializer_class = OperationSerializer
    permission_classes = [IsAuthenticated]

class DailyTaskReportListCreate(generics.ListCreateAPIView):
    queryset = DailyTaskReport.objects.all()
    serializer_class = DailyTaskReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DailyTaskFilter

    def perform_create(self, serializer):
        serializer.save(engineer=self.request.user)

class DailyTaskReportDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = DailyTaskReport.objects.all()
    serializer_class = DailyTaskReportSerializer
    permission_classes = [IsAuthenticated]

class FertilizationListCreate(generics.ListCreateAPIView):
    queryset = FertilizationReport.objects.all()
    serializer_class = FertilizationReportSerializer
    permission_classes = [IsAuthenticated]

class FertilizationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = FertilizationReport.objects.all()
    serializer_class = FertilizationReportSerializer
    permission_classes = [IsAuthenticated]

class IrrigationListCreate(generics.ListCreateAPIView):
    queryset = IrrigationReport.objects.all()
    serializer_class = IrrigationReportSerializer
    permission_classes = [IsAuthenticated]

class IrrigationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = IrrigationReport.objects.all()
    serializer_class = IrrigationReportSerializer
    permission_classes = [IsAuthenticated]

class DailyTaskSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        summary = DailyTaskReport.objects.values(
            'operation__name', 'variety'
        ).annotate(
            total_productivity=Sum('actual_productivity'),
            total_workers=Sum('contractor_workers'),
        )
        return Response(summary)

class DailyTaskExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Placeholder for export logic using openpyxl
        return Response({"message": "Export feature pending implementation"})

class CustomFieldDefinitionListCreate(generics.ListCreateAPIView):
    queryset = CustomFieldDefinition.objects.all()
    serializer_class = CustomFieldDefinitionSerializer
    permission_classes = [IsManagerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class CustomFieldDefinitionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomFieldDefinition.objects.all()
    serializer_class = CustomFieldDefinitionSerializer
    permission_classes = [IsManagerOrReadOnly]

class CustomFieldValueListCreate(generics.ListCreateAPIView):
    queryset = CustomFieldValue.objects.all()
    serializer_class = CustomFieldValueSerializer
    permission_classes = [IsAuthenticated]

class CustomFieldValueDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomFieldValue.objects.all()
    serializer_class = CustomFieldValueSerializer
    permission_classes = [IsAuthenticated]

class ReportDropdownOptionListCreate(generics.ListCreateAPIView):
    queryset = ReportDropdownOption.objects.all()
    serializer_class = ReportDropdownOptionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_active']

class ReportDropdownOptionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReportDropdownOption.objects.all()
    serializer_class = ReportDropdownOptionSerializer
    permission_classes = [IsAuthenticated]
