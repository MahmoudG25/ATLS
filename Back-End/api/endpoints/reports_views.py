from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Count, Avg, IntegerField
from django.db.models.functions import Coalesce
from apps.reports.models import (
    Operation, DailyTaskReport, FertilizationReport, IrrigationReport,
    CustomFieldDefinition, CustomFieldValue, ReportDropdownOption, LaborEntry, Attachment
)
from serializers.reports_serializers import (
    OperationSerializer,
    DailyTaskReportSerializer,
    FertilizationReportSerializer,
    IrrigationReportSerializer,
    CustomFieldDefinitionSerializer,
    CustomFieldValueSerializer,
    ReportDropdownOptionSerializer,
    LaborEntrySerializer,
    AttachmentSerializer,
    # Analytics Serializers
    KPIDashboardSerializer,
    ProductivityAnalyticsSerializer,
    OperationsSummarySerializer,
    WorkersByLocationSerializer,
    OperationLocationMatrixSerializer,
)
from apps.reports.permissions import IsManagerOrReadOnly
from apps.reports.services import (
    comparison_analytics,
    cost_analytics,
    dashboard_bundle,
    smart_alerts,
    smart_suggestions,
)
from apps.reports.selectors import (
    kpi_metrics,
    kpi_dashboard,
    productivity_analytics,
    operations_summary,
    workers_by_location,
    operation_location_matrix,
)
from django_filters.rest_framework import DjangoFilterBackend
import django_filters

class DailyTaskFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='report_date', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='report_date', lookup_expr='lte')
    engineer_name = django_filters.CharFilter(field_name='engineer__name', lookup_expr='icontains')
    operation_name = django_filters.CharFilter(field_name='operation__name', lookup_expr='icontains')
    location = django_filters.NumberFilter(field_name='location_id')
    
    class Meta:
        model = DailyTaskReport
        fields = ['engineer', 'report_date', 'operation', 'location']


def _for_company(queryset, request):
    company = getattr(request, "company", None)
    if request.user.is_superuser:
        return queryset
    if hasattr(queryset, "for_company"):
        return queryset.for_company(company)
    if not company:
        return queryset.none()
    return queryset.filter(company=company)

class OperationListView(generics.ListAPIView):
    serializer_class = OperationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Operation.objects.filter(is_active=True).order_by("name")
        return _for_company(qs, self.request)

class DailyTaskReportListCreate(generics.ListCreateAPIView):
    serializer_class = DailyTaskReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DailyTaskFilter

    def get_queryset(self):
        qs = DailyTaskReport.objects.select_related(
            "engineer",
            "operation",
            "variety",
            "unit",
            "contractor",
            "location",
            "location__parent",
        ).prefetch_related("attachments", "labor_entries")
        return _for_company(qs, self.request)

    def perform_create(self, serializer):
        serializer.save(
            engineer=self.request.user,
            company=getattr(self.request, "company", None),
        )

class DailyTaskReportDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DailyTaskReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return _for_company(DailyTaskReport.objects.all(), self.request)

class FertilizationListCreate(generics.ListCreateAPIView):
    serializer_class = FertilizationReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return _for_company(FertilizationReport.objects.all(), self.request)

    def perform_create(self, serializer):
        serializer.save(company=getattr(self.request, "company", None))

class FertilizationDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FertilizationReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return _for_company(FertilizationReport.objects.all(), self.request)

class IrrigationListCreate(generics.ListCreateAPIView):
    serializer_class = IrrigationReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return _for_company(IrrigationReport.objects.all(), self.request)

    def perform_create(self, serializer):
        serializer.save(company=getattr(self.request, "company", None))

class IrrigationDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = IrrigationReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return _for_company(IrrigationReport.objects.all(), self.request)

class DailyTaskSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        summary = _for_company(DailyTaskReport.objects.all(), request).values(
            'operation__name', 'report_date'
        ).annotate(
            total_productivity=Sum('actual_productivity'),
            avg_work_hours=Avg('work_hours'),
            reports_count=Count('id'),
            total_workers=Coalesce(Sum('company_workers'), 0, output_field=IntegerField()) + Coalesce(Sum('contractor_workers'), 0, output_field=IntegerField()),
        ).order_by('-report_date')
        return Response(summary)

class DailyTaskExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Placeholder for export logic using openpyxl
        return Response({"message": "Export feature pending implementation"})

class CustomFieldDefinitionListCreate(generics.ListCreateAPIView):
    serializer_class = CustomFieldDefinitionSerializer
    permission_classes = [IsManagerOrReadOnly]

    def get_queryset(self):
        return _for_company(CustomFieldDefinition.objects.all(), self.request)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, company=getattr(self.request, "company", None))

class CustomFieldDefinitionDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CustomFieldDefinitionSerializer
    permission_classes = [IsManagerOrReadOnly]

    def get_queryset(self):
        return _for_company(CustomFieldDefinition.objects.all(), self.request)

class CustomFieldValueListCreate(generics.ListCreateAPIView):
    serializer_class = CustomFieldValueSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return _for_company(
            CustomFieldValue.objects.select_related("field"),
            self.request,
        )

class CustomFieldValueDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CustomFieldValueSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return _for_company(CustomFieldValue.objects.select_related("field"), self.request)

class ReportDropdownOptionListCreate(generics.ListCreateAPIView):
    serializer_class = ReportDropdownOptionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_active']

    def get_queryset(self):
        return _for_company(ReportDropdownOption.objects.all(), self.request)

    def perform_create(self, serializer):
        serializer.save(company=getattr(self.request, "company", None))

class ReportDropdownOptionDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReportDropdownOptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return _for_company(ReportDropdownOption.objects.all(), self.request)

    def perform_update(self, serializer):
        company = getattr(self.request, "company", None)
        serializer.save(company=company)


class LaborEntryListCreate(generics.ListCreateAPIView):
    serializer_class = LaborEntrySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["report", "worker_type", "contractor"]

    def get_queryset(self):
        return LaborEntry.objects.filter(report__in=_for_company(DailyTaskReport.objects.all(), self.request))

    def perform_create(self, serializer):
        serializer.save(company=getattr(self.request, "company", None))


class AttachmentListCreate(generics.ListCreateAPIView):
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["report", "file_type"]

    def get_queryset(self):
        return Attachment.objects.filter(report__in=_for_company(DailyTaskReport.objects.all(), self.request))

    def perform_create(self, serializer):
        serializer.save(company=getattr(self.request, "company", None))


class OperationAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = _for_company(DailyTaskReport.objects.all(), request)
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        if start_date:
            qs = qs.filter(report_date__gte=start_date)
        if end_date:
            qs = qs.filter(report_date__lte=end_date)

        data = qs.values("operation__id", "operation__name").annotate(
            total_reports=Count("id"),
            total_productivity=Sum("actual_productivity"),
            total_workers=Coalesce(Sum("company_workers"), 0, output_field=IntegerField()) + Coalesce(Sum("contractor_workers"), 0, output_field=IntegerField()),
            company_workers=Sum("company_workers"),
            contractor_workers=Sum("contractor_workers"),
            avg_hours=Avg("work_hours"),
        ).order_by("-total_reports")
        return Response(data)


class WorkerAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = _for_company(DailyTaskReport.objects.all(), request)
        data = {
            "totals": qs.aggregate(
                company_workers=Sum("company_workers"),
                contractor_workers=Sum("contractor_workers"),
                avg_hours=Avg("work_hours"),
                reports=Count("id"),
            ),
            "by_engineer": list(
                qs.values("engineer__id", "engineer__name").annotate(
                    reports=Count("id"),
                    total_workers=Coalesce(Sum("company_workers"), 0, output_field=IntegerField()) + Coalesce(Sum("contractor_workers"), 0, output_field=IntegerField()),
                    total_productivity=Sum("actual_productivity"),
                ).order_by("-reports")
            ),
        }
        return Response(data)


class CostAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(cost_analytics(getattr(request, "company", None)))


class KPIAnalyticsView(APIView):
    """
    GET /analytics/kpi
    
    Comprehensive KPI dashboard with:
    - Total workers (company + contractor)
    - Total operations
    - Average productivity per operation
    - Workers per location
    
    Query params:
    - start_date: YYYY-MM-DD
    - end_date: YYYY-MM-DD
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = getattr(request, "company", None)
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        
        data = kpi_dashboard(company, start_date=start_date, end_date=end_date)
        serializer = KPIDashboardSerializer(data)
        return Response(serializer.data)


class ProductivityAnalyticsView(APIView):
    """
    GET /analytics/productivity
    
    Productivity aggregation with grouping by:
    - operation
    - location (LocationNode)
    - date
    
    Includes min/max/avg/total productivity metrics.
    
    Query params:
    - start_date: YYYY-MM-DD
    - end_date: YYYY-MM-DD
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = getattr(request, "company", None)
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        
        data = productivity_analytics(company, start_date=start_date, end_date=end_date)
        serializer = ProductivityAnalyticsSerializer(data)
        return Response(serializer.data)


class ComparisonAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(comparison_analytics(getattr(request, "company", None)))


class DashboardAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(dashboard_bundle(getattr(request, "company", None)))


class SmartInsightsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = getattr(request, "company", None)
        return Response({
            "alerts": smart_alerts(company),
            "suggestions": smart_suggestions(company),
        })


# ============================================================================
# ADVANCED ANALYTICS ENDPOINTS
# ============================================================================

class OperationsSummaryView(APIView):
    """
    GET /analytics/operations-summary
    
    Operations summary with detailed breakdown:
    - Workers per operation (company + contractor split)
    - Work hours per operation
    - Reports count per operation
    - Location breakdown
    - Engineer count
    
    Query params:
    - start_date: YYYY-MM-DD
    - end_date: YYYY-MM-DD
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = getattr(request, "company", None)
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        
        data = operations_summary(company, start_date=start_date, end_date=end_date)
        serializer = OperationsSummarySerializer(data)
        return Response(serializer.data)


class WorkersByLocationView(APIView):
    """
    GET /analytics/workers-by-location
    
    Worker distribution grouped by LocationNode:
    - Total workers per location
    - Company vs contractor split
    - Reports count
    - Engineers and operations per location
    
    Query params:
    - start_date: YYYY-MM-DD
    - end_date: YYYY-MM-DD
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = getattr(request, "company", None)
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        
        data = workers_by_location(company, start_date=start_date, end_date=end_date)
        serializer = WorkersByLocationSerializer(data)
        return Response(serializer.data)


class OperationLocationMatrixView(APIView):
    """
    GET /analytics/operation-location-matrix
    
    Cross-tabulation of operations vs locations:
    - Worker counts at operation x location intersection
    - Company vs contractor breakdown
    - Reports count
    
    Query params:
    - start_date: YYYY-MM-DD
    - end_date: YYYY-MM-DD
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = getattr(request, "company", None)
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        
        data = operation_location_matrix(company, start_date=start_date, end_date=end_date)
        serializer = OperationLocationMatrixSerializer(data)
        return Response(serializer.data)
