from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import (
    Sum,
    Count,
    Avg,
    IntegerField,
    F,
    OuterRef,
    Subquery,
    ExpressionWrapper,
    FloatField,
    Case,
    When,
    Value,
)
from django.db.models.functions import Coalesce
from apps.reports.models import (
    Operation,
    Variety,
    Unit,
    Contractor,
    DailyTaskReport,
    FertilizationReport,
    IrrigationReport,
    CustomFieldDefinition,
    CustomFieldValue,
    ReportDropdownOption,
    LaborEntry,
    Attachment,
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
    VarietySerializer,
    UnitSerializer,
    ContractorSerializer,
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
from rest_framework.pagination import PageNumberPagination
import django_filters

class TaskPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class DailyTaskFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name="report_date", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="report_date", lookup_expr="lte")
    engineer_name = django_filters.CharFilter(
        field_name="engineer__name", lookup_expr="icontains"
    )
    operation_name = django_filters.CharFilter(
        field_name="operation__name", lookup_expr="icontains"
    )
    location = django_filters.NumberFilter(field_name="location_id")

    class Meta:
        model = DailyTaskReport
        fields = ["engineer", "report_date", "operation", "location"]


def _for_company(queryset, request):
    company = getattr(request, "company", None)
    
    # --- TEMPORARY SINGLE-TENANT COMPATIBILITY FALLBACK ---
    # TODO: [Strict Tenant Assignment Enforcement]
    # Future multi-tenant expansion MUST require all users to be explicitly assigned to a company.
    # Currently, Engineer accounts without a company assignment receive empty dropdowns.
    # We fallback to the first company to stabilize operational reporting.
    if not company and request.user.is_authenticated:
        from apps.users.models import Company
        company = Company.objects.first()
        request.company = company
    # ------------------------------------------------------
    
    # Temporary debug logging for tenant/data-access integrity audit
    print(f"[TENANT DEBUG] User: {request.user} (Superuser: {request.user.is_superuser})")
    print(f"[TENANT DEBUG] Middleware Company: {getattr(request, 'company', None)}")
    print(f"[TENANT DEBUG] Resolved Company: {company}")
    
    if request.user.is_superuser:
        qs = queryset
    elif hasattr(queryset, "for_company"):
        qs = queryset.for_company(company)
    elif not company:
        qs = queryset.none()
    else:
        qs = queryset.filter(company=company)
        
    if hasattr(qs.model, 'is_deleted'):
        qs = qs.filter(is_deleted=False)
        
    print(f"[TENANT DEBUG] Queryset ({queryset.model.__name__}) Count: {qs.count()}")
    return qs


class OperationListView(generics.ListCreateAPIView):
    serializer_class = OperationSerializer
    permission_classes = [IsManagerOrReadOnly]

    def get_queryset(self):
        qs = Operation.objects.filter(is_active=True).order_by("name")
        return _for_company(qs, self.request)

    def perform_create(self, serializer):
        company = getattr(self.request, "company", None)
        if not company:
            from apps.users.models import Company
            company = Company.objects.first()
        serializer.save(company=company)

class OperationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OperationSerializer
    permission_classes = [IsManagerOrReadOnly]

    def get_queryset(self):
        return _for_company(Operation.objects.all(), self.request)

    def perform_destroy(self, instance):
        if getattr(instance, "is_system", False):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied({"detail": "System operations cannot be deactivated."})
        # Soft delete by deactivating
        instance.is_active = False
        instance.save(update_fields=["is_active"])


class DailyTaskReportListCreate(generics.ListCreateAPIView):
    serializer_class = DailyTaskReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DailyTaskFilter
    pagination_class = TaskPagination

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
        from apps.users.models import Company
        from rest_framework.exceptions import ValidationError as DRFValidationError

        # Single-Tenant: Auto-fetch the only company in the system
        main_company = Company.objects.first()
        if not main_company:
            raise DRFValidationError(
                {
                    "company": "لم يتم إعداد بيانات الشركة في النظام بعد. يرجى التواصل مع السوبر أدمن."
                }
            )

        user = self.request.user
        # Privileged roles can assign reports to any engineer via request body.
        # All other roles are forced to file under their own identity.
        PRIVILEGED = {"SUPER_ADMIN", "OWNER", "MANAGER", "ADMIN"}
        save_kwargs = {"company": main_company}

        if not (hasattr(user, "role") and user.role in PRIVILEGED):
            save_kwargs["engineer"] = user

        instance = serializer.save(**save_kwargs)


class DailyTaskReportDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DailyTaskReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return _for_company(DailyTaskReport.objects.all(), self.request)

    def perform_update(self, serializer):
        instance = self.get_object()
        user_role = getattr(self.request.user, "role", "ENGINEER")
        is_super = user_role in ["SUPER_ADMIN", "OWNER"]
        is_manager = is_super or user_role == "MANAGER"

        if instance.status == "approved":
            if not is_super:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Approved reports are immutable and cannot be edited.")
            
            # If SUPER_ADMIN is editing an approved report, an override reason is strictly required.
            override_reason = serializer.validated_data.get("override_reason")
            if not override_reason:
                from rest_framework.exceptions import ValidationError as DRFValidationError
                raise DRFValidationError({"override_reason": "سبب التعديل الاستثنائي مطلوب."})
            
            from django.utils import timezone
            serializer.save(
                override_by=self.request.user,
                override_at=timezone.now(),
                was_overridden=True
            )
            # Ensure status remains approved
            instance.status = "approved"
        elif not is_manager and instance.status not in ["draft", "submitted", "rejected"]:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Engineers can only edit draft, submitted, or rejected reports.")
        else:
            serializer.save()

    def perform_destroy(self, instance):
        user_role = getattr(self.request.user, "role", "ENGINEER")
        is_super = user_role in ["SUPER_ADMIN", "OWNER"]
        is_manager = is_super or user_role == "MANAGER"

        if instance.status == "approved" and not is_super:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Approved reports are immutable and cannot be deleted.")

        if not is_manager and instance.status not in ["draft", "submitted", "rejected"]:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Engineers can only delete draft, submitted, or rejected reports.")

        from django.utils import timezone
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save(update_fields=["is_deleted", "deleted_at", "deleted_by"])


class DailyTaskReportActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, action):
        from rest_framework import status
        try:
            report = _for_company(DailyTaskReport.objects.all(), request).get(pk=pk)
        except DailyTaskReport.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user_role = getattr(request.user, "role", "ENGINEER")
        is_manager = user_role in ["MANAGER", "SUPER_ADMIN", "OWNER"]

        if action == "submit":
            if report.status not in ["draft", "rejected"]:
                return Response({"detail": "Only draft or rejected reports can be submitted."}, status=status.HTTP_400_BAD_REQUEST)
            if report.engineer != request.user and not is_manager:
                return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
            from django.utils import timezone
            report.status = "submitted"
            report.rejection_reason = ""
            report.submitted_at = timezone.now()
            report.save(update_fields=["status", "rejection_reason", "submitted_at", "updated_at"])
            return Response({"status": report.status})

        if not is_manager:
            return Response({"detail": "Only managers can perform this action."}, status=status.HTTP_403_FORBIDDEN)

        if action == "review":
            if report.status != "submitted":
                return Response({"detail": "Only submitted reports can be reviewed."}, status=status.HTTP_400_BAD_REQUEST)
            report.status = "under_review"
            report.save(update_fields=["status", "updated_at"])
            return Response({"status": report.status})

        if action == "approve":
            if report.status not in ["submitted", "under_review"]:
                return Response({"detail": "Cannot approve this report."}, status=status.HTTP_400_BAD_REQUEST)
            from django.utils import timezone
            report.status = "approved"
            report.approved_at = timezone.now()
            report.save(update_fields=["status", "approved_at", "updated_at"])
            return Response({"status": report.status})

        if action == "reject":
            if report.status not in ["submitted", "under_review"]:
                return Response({"detail": "Cannot reject this report."}, status=status.HTTP_400_BAD_REQUEST)
            rejection_reason = request.data.get("rejection_reason", "").strip()
            if not rejection_reason:
                return Response({"detail": "Rejection reason is required."}, status=status.HTTP_400_BAD_REQUEST)
            from django.utils import timezone
            report.status = "rejected"
            report.rejection_reason = rejection_reason
            report.rejected_at = timezone.now()
            report.save(update_fields=["status", "rejection_reason", "rejected_at", "updated_at"])
            return Response({"status": report.status})

        return Response({"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)


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
        summary = (
            _for_company(DailyTaskReport.objects.all(), request)
            .values("operation__name", "report_date")
            .annotate(
                total_productivity=Sum("actual_productivity"),
                avg_work_hours=Avg("work_hours"),
                reports_count=Count("id"),
                total_workers=Coalesce(
                    Sum("company_workers"), 0, output_field=IntegerField()
                )
                + Coalesce(Sum("contractor_workers"), 0, output_field=IntegerField()),
            )
            .order_by("-report_date")
        )
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
        company = getattr(self.request, "company", None)
        if not company:
            from apps.users.models import Company
            company = Company.objects.first()
        serializer.save(created_by=self.request.user, company=company)


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
        return _for_company(
            CustomFieldValue.objects.select_related("field"), self.request
        )


from rest_framework.exceptions import MethodNotAllowed

class ReportDropdownOptionListCreate(generics.ListCreateAPIView):
    serializer_class = ReportDropdownOptionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category", "is_active"]

    def get_queryset(self):
        return _for_company(ReportDropdownOption.objects.all(), self.request)

    def perform_create(self, serializer):
        raise MethodNotAllowed(
            "POST", 
            detail="Legacy ReportDropdownOption write endpoint deprecated. Please use the dedicated Master Data endpoints."
        )


class ReportDropdownOptionDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReportDropdownOptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return _for_company(ReportDropdownOption.objects.all(), self.request)

    def perform_update(self, serializer):
        raise MethodNotAllowed(
            "PUT/PATCH", 
            detail="Legacy ReportDropdownOption write endpoint deprecated."
        )

    def perform_destroy(self, instance):
        raise MethodNotAllowed(
            "DELETE", 
            detail="Legacy ReportDropdownOption write endpoint deprecated."
        )


class VarietyListView(generics.ListCreateAPIView):
    serializer_class = VarietySerializer
    permission_classes = [IsManagerOrReadOnly]

    def get_queryset(self):
        return _for_company(Variety.objects.filter(is_active=True), self.request)

    def perform_create(self, serializer):
        company = getattr(self.request, "company", None)
        if not company:
            from apps.users.models import Company
            company = Company.objects.first()
        serializer.save(company=company)


class VarietyDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = VarietySerializer
    permission_classes = [IsManagerOrReadOnly]

    def get_queryset(self):
        return _for_company(Variety.objects.all(), self.request)

    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save(update_fields=["is_active"])


class UnitListView(generics.ListCreateAPIView):
    serializer_class = UnitSerializer
    permission_classes = [IsManagerOrReadOnly]

    def get_queryset(self):
        return _for_company(Unit.objects.filter(is_active=True), self.request)

    def perform_create(self, serializer):
        company = getattr(self.request, "company", None)
        if not company:
            from apps.users.models import Company
            company = Company.objects.first()
        serializer.save(company=company)


class UnitDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UnitSerializer
    permission_classes = [IsManagerOrReadOnly]

    def get_queryset(self):
        return _for_company(Unit.objects.all(), self.request)

    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save(update_fields=["is_active"])


class ContractorListView(generics.ListCreateAPIView):
    serializer_class = ContractorSerializer
    permission_classes = [IsManagerOrReadOnly]

    def get_queryset(self):
        return _for_company(Contractor.objects.filter(is_active=True), self.request)

    def perform_create(self, serializer):
        company = getattr(self.request, "company", None)
        if not company:
            from apps.users.models import Company
            company = Company.objects.first()
        serializer.save(company=company)


class ContractorDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContractorSerializer
    permission_classes = [IsManagerOrReadOnly]

    def get_queryset(self):
        return _for_company(Contractor.objects.all(), self.request)

    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save(update_fields=["is_active"])


class LaborEntryListCreate(generics.ListCreateAPIView):
    serializer_class = LaborEntrySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["report", "worker_type", "contractor"]

    def get_queryset(self):
        return LaborEntry.objects.filter(
            report__in=_for_company(DailyTaskReport.objects.all(), self.request)
        )

    def perform_create(self, serializer):
        instance = serializer.save(company=getattr(self.request, "company", None))
        
        # Phase 2 Dual-Write Bridge
        from services.reports_service import sync_child_operation_log
        sync_child_operation_log(instance)


class AttachmentListCreate(generics.ListCreateAPIView):
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["report", "file_type"]

    def get_queryset(self):
        return Attachment.objects.filter(
            report__in=_for_company(DailyTaskReport.objects.all(), self.request)
        )

    def perform_create(self, serializer):
        instance = serializer.save(company=getattr(self.request, "company", None))
        
        # Phase 2 Dual-Write Bridge
        from services.reports_service import sync_child_operation_log
        sync_child_operation_log(instance)


class OperationAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.reports.models import OperationLog
        qs = _for_company(OperationLog.objects.all(), request)
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        if start_date:
            qs = qs.filter(report__report_date__gte=start_date)
        if end_date:
            qs = qs.filter(report__report_date__lte=end_date)

        data = (
            qs.values("operation__id", "operation__name")
            .annotate(
                total_reports=Count("id"),
                total_productivity=Sum("actual_productivity"),
                total_workers=Coalesce(
                    Sum("company_workers"), 0, output_field=IntegerField()
                )
                + Coalesce(Sum("contractor_workers"), 0, output_field=IntegerField()),
                company_workers=Sum("company_workers"),
                contractor_workers=Sum("contractor_workers"),
                avg_hours=Avg("work_hours"),
            )
            .order_by("-total_reports")
        )
        return Response(data)


class WorkerAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.reports.models import OperationLog
        qs = _for_company(OperationLog.objects.all(), request)
        data = {
            "totals": qs.aggregate(
                company_workers=Sum("company_workers"),
                contractor_workers=Sum("contractor_workers"),
                avg_hours=Avg("work_hours"),
                reports=Count("id"),
            ),
            "by_engineer": list(
                qs.values(engineer__id=F("report__engineer__id"), engineer__name=F("report__engineer__name"))
                .annotate(
                    reports=Count("id"),
                    total_workers=Coalesce(
                        Sum("company_workers"), 0, output_field=IntegerField()
                    )
                    + Coalesce(
                        Sum("contractor_workers"), 0, output_field=IntegerField()
                    ),
                    total_productivity=Sum("actual_productivity"),
                )
                .order_by("-reports")
            ),
        }
        return Response(data)


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
        return Response(
            {
                "alerts": smart_alerts(company),
                "suggestions": smart_suggestions(company),
            }
        )


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

        data = operation_location_matrix(
            company, start_date=start_date, end_date=end_date
        )
        serializer = OperationLocationMatrixSerializer(data)
        return Response(serializer.data)


class CostAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = getattr(request, "company", None)

        labor_sum_subquery = (
            LaborEntry.objects.filter(report=OuterRef("pk"))
            .values("report")
            .annotate(
                total=Sum(
                    ExpressionWrapper(
                        F("hours") * F("worker_rate"), output_field=FloatField()
                    )
                )
            )
            .values("total")
        )

        qs = (
            _for_company(DailyTaskReport.objects.all(), request)
            .annotate(
                report_cost=Coalesce(
                    Subquery(labor_sum_subquery),
                    0.0,
                    output_field=FloatField(),
                )
            )
            .filter(location__type="ENCLOSURE")
        )

        total_cost = qs.aggregate(total=Sum("report_cost"))["total"] or 0.0

        cost_per_operation = list(
            qs.values("operation__name")
            .annotate(agg_cost=Sum("report_cost"))
            .values(operation=F("operation__name"), total_cost=F("agg_cost"))
            .order_by("-total_cost")
        )

        cost_per_location = list(
            qs.values("location__id", "location__name")
            .annotate(agg_cost=Sum("report_cost"))
            .values(location=F("location__name"), total_cost=F("agg_cost"))
            .order_by("-total_cost")
        )

        return Response(
            {
                "total_cost": float(total_cost),
                "cost_per_operation": cost_per_operation,
                "cost_per_location": cost_per_location,
            }
        )


class TrendsAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        labor_sum_subquery = (
            LaborEntry.objects.filter(report=OuterRef("pk"))
            .values("report")
            .annotate(
                total=Sum(
                    ExpressionWrapper(
                        F("hours") * F("worker_rate"), output_field=FloatField()
                    )
                )
            )
            .values("total")
        )

        qs = (
            _for_company(DailyTaskReport.objects.all(), request)
            .annotate(
                report_cost=Coalesce(
                    Subquery(labor_sum_subquery),
                    0.0,
                    output_field=FloatField(),
                )
            )
            .filter(location__type="ENCLOSURE")
        )

        trends = list(
            qs.values("report_date")
            .annotate(
                total_reports=Count("id"),
                total_workers=Sum("company_workers") + Sum("contractor_workers"),
                total_hours=Sum("work_hours"),
                total_cost=Sum("report_cost"),
            )
            .order_by("report_date")
        )

        return Response({"trends": trends})


class InsightsAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = _for_company(DailyTaskReport.objects.all(), request).filter(
            location__type="ENCLOSURE"
        )

        # Productivity: Output per worker (handling division by zero)
        productivity = (
            qs.values("operation__name")
            .annotate(
                total_workers=Coalesce(Sum("company_workers"), 0)
                + Coalesce(Sum("contractor_workers"), 0),
                total_output=Coalesce(Sum("actual_productivity"), 0.0),
            )
            .annotate(
                productivity=Case(
                    When(
                        total_workers__gt=0, then=F("total_output") / F("total_workers")
                    ),
                    default=Value(0.0),
                    output_field=FloatField(),
                )
            )
        )

        best_productivity = productivity.order_by("-productivity").first()
        worst_productivity = productivity.order_by("productivity").first()

        # Cost: Derived from LaborEntry hours * rate via subquery
        cost_data = qs.annotate(
            report_cost=Coalesce(
                Subquery(
                    LaborEntry.objects.filter(report=OuterRef("pk"))
                    .values("report")
                    .annotate(
                        total=Sum(
                            ExpressionWrapper(
                                F("hours") * F("worker_rate"), output_field=FloatField()
                            )
                        )
                    )
                    .values("total")
                ),
                0.0,
                output_field=FloatField(),
            )
        )

        cost_per_operation = cost_data.values("operation__name").annotate(
            total_cost=Sum("report_cost")
        )

        highest_cost_operation = cost_per_operation.order_by("-total_cost").first()

        return Response(
            {
                "best_productivity": best_productivity,
                "worst_productivity": worst_productivity,
                "highest_cost_operation": highest_cost_operation,
            }
        )
