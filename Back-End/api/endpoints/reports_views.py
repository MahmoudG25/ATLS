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
    Q,
)
from django.db.models.functions import Coalesce
from apps.reports.models import (
    Operation,
    Variety,
    Unit,
    Contractor,
    ApplicationMethod,
    DailyTaskReport,
    FertilizationReport,
    IrrigationReport,
    CustomFieldDefinition,
    CustomFieldValue,
    LaborEntry,
    Attachment,
    Season,
    GalleryMedia,
    PestControlReport,
    OperationalLocationAllocation,
)
from serializers.reports_serializers import (
    OperationSerializer,
    DailyTaskReportSerializer,
    DailyTaskReportListSerializer,
    FertilizationReportSerializer,
    IrrigationReportSerializer,
    CustomFieldDefinitionSerializer,
    CustomFieldValueSerializer,
    ReportDropdownOptionSerializer,
    LaborEntrySerializer,
    AttachmentSerializer,
    GalleryMediaSerializer,
    VarietySerializer,
    UnitSerializer,
    ContractorSerializer,
    ApplicationMethodSerializer,
    # Analytics Serializers
    KPIDashboardSerializer,
    ProductivityAnalyticsSerializer,
    OperationsSummarySerializer,
    WorkersByLocationSerializer,
    OperationLocationMatrixSerializer,
    SeasonSerializer,
    PestControlReportSerializer,
    OperationalLocationAllocationSerializer,
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
from services.activity_service import log_activity

class TaskPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10000


class DailyTaskFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name="report_date", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="report_date", lookup_expr="lte")
    engineer_name = django_filters.CharFilter(
        field_name="engineer__name", lookup_expr="icontains"
    )
    operation_name = django_filters.CharFilter(
        field_name="operation__name", lookup_expr="icontains"
    )
    
    # Hierarchical location filter (supports UUIDs)
    location = django_filters.UUIDFilter(method="filter_location")
    
    # Generic operational search
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = DailyTaskReport
        fields = ["engineer", "operation", "report_date"]

    def filter_location(self, queryset, name, value):
        if not value:
            return queryset
        try:
            from apps.farm.models import LocationNode
            # Get node and all its children in the hierarchy
            node = LocationNode.objects.get(id=value)
            descendant_ids = node.get_descendants(include_self=True).values_list('id', flat=True)
            return queryset.filter(location_id__in=descendant_ids)
        except Exception as e:
            logger.error(f"Error in location filter: {e}")
            return queryset

    def filter_search(self, queryset, name, value):
        from django.db.models import Q
        if not value:
            return queryset
        
        # Check if value is a numeric ID
        id_query = Q()
        if value.startswith("#"):
            val = value[1:]
            if val.isdigit():
                id_query = Q(id=val)
        elif value.isdigit():
            id_query = Q(id=value)

        return queryset.filter(
            id_query |
            Q(engineer__name__icontains=value) |
            Q(operation__name__icontains=value) |
            Q(enclosure_name__icontains=value) |
            Q(location__name__icontains=value)
        )


import logging
logger = logging.getLogger(__name__)

def _get_company(request):
    """
    Safely resolves the company for the current request.
    Handles JWT authentication where middleware might not have request.company yet.
    """
    company = getattr(request, "company", None)
    if not company and request.user.is_authenticated:
        company = getattr(request.user, "company", None)
    
    if not company:
        try:
            from apps.users.models import Company
            company = Company.objects.first()
        except:
            pass
    return company

def _for_company(queryset, request):
    user = request.user
    if not user or not user.is_authenticated:
        return queryset.none()

    # 1. Super Admin bypass: sees all records across all tenants
    if user.is_superuser or getattr(user, "role", None) == "SUPER_ADMIN":
        return queryset

    # 2. Extract company with multiple fallbacks
    company = _get_company(request)

    if not company:
        logger.warning(f"User {user} accessed {queryset.model.__name__} without a company assignment.")
        return queryset.none()
    
    # 3. Apply tenant isolation logic
    if hasattr(queryset, "for_company"):
        # Uses the logic in core.tenant.TenantQuerySet
        qs = queryset.for_company(company)
    else:
        # Fallback for QuerySets that don't have the for_company manager method
        filter_q = Q(company=company)
        if hasattr(queryset.model, "is_system"):
            filter_q |= Q(is_system=True)
        qs = queryset.filter(filter_q)
        
    if hasattr(qs.model, "is_deleted"):
        qs = qs.filter(is_deleted=False)
        
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
            # Super Admin: no company from middleware, fall back to first available
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
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DailyTaskFilter
    pagination_class = TaskPagination

    def get_serializer_class(self):
        if self.request.method == "GET":
            return DailyTaskReportListSerializer
        return DailyTaskReportSerializer

    def get_queryset(self):
        qs = DailyTaskReport.objects.select_related(
            "engineer",
            "operation",
            "variety",
            "unit",
            "contractor",
            "location",
            "location__parent",
        ).prefetch_related(
            "attachments",
            "labor_entries",
            "operation_logs",
            "operation_logs__operation",
        )
        return _for_company(qs, self.request)

    def perform_create(self, serializer):
        from rest_framework.exceptions import ValidationError as DRFValidationError

        # Resolve company: prefer middleware-injected, fall back for Super Admin
        main_company = getattr(self.request, "company", None)
        if not main_company:
            from apps.users.models import Company
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
        log_activity(user, f"Created Daily Task Report: {instance.pk}", "Reports")


class DailyTaskReportDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DailyTaskReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return _for_company(
            DailyTaskReport.objects.select_related(
                "engineer",
                "operation",
                "variety",
                "unit",
                "contractor",
                "location",
                "location__parent",
            ).prefetch_related(
                "attachments",
                "attachments__report",
                "attachments__report__operation",
                "attachments__report__location",
                "attachments__report__engineer",
                "labor_entries",
                "operation_logs",
                "operation_logs__operation",
                "operation_logs__location",
                "operation_logs__variety",
                "operation_logs__unit",
            ),
            self.request,
        )


    def perform_update(self, serializer):
        instance = self.get_object()
        user_role = getattr(self.request.user, "role", "ENGINEER")
        is_super = user_role in ["SUPER_ADMIN", "OWNER"]
        is_manager = is_super or user_role == "MANAGER"

        if instance.status == "approved":
            if not is_manager:
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
            log_activity(self.request.user, f"Super Admin Override: Daily Task Report {instance.pk}", "Reports")
        elif not is_manager and instance.status not in ["draft", "submitted", "rejected"]:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Engineers can only edit draft, submitted, or rejected reports.")
        else:
            serializer.save()
            log_activity(self.request.user, f"Updated Daily Task Report: {instance.pk}", "Reports")

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
        log_activity(self.request.user, f"Deleted Daily Task Report: {instance.pk}", "Reports")


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


class FertilizationFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name="report_date", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="report_date", lookup_expr="lte")
    enclosure = django_filters.UUIDFilter(field_name="enclosure_id")

    class Meta:
        model = FertilizationReport
        fields = ["enclosure"]


class FertilizationListCreate(generics.ListCreateAPIView):
    serializer_class = FertilizationReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = FertilizationFilter

    def get_queryset(self):
        return _for_company(FertilizationReport.objects.all(), self.request)

    def perform_create(self, serializer):
        serializer.save(company=getattr(self.request, "company", None))


class FertilizationDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FertilizationReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return _for_company(FertilizationReport.objects.all(), self.request)


class IrrigationFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="date", lookup_expr="lte")
    engineer = django_filters.UUIDFilter(field_name="engineer_id")
    search = django_filters.CharFilter(method="filter_search")
    phase = django_filters.UUIDFilter(method="filter_phase")
    enclosure = django_filters.UUIDFilter(method="filter_enclosure")

    class Meta:
        model = IrrigationReport
        fields = ["engineer", "date", "enclosure"]

    def filter_search(self, queryset, name, value):
        from django.db.models import Q
        if not value:
            return queryset
        
        id_query = Q()
        if value.startswith("#"):
            val = value[1:]
            if val.isdigit():
                id_query = Q(id=val)
        elif value.isdigit():
            id_query = Q(id=value)
            
        return queryset.filter(
            Q(engineer__username__icontains=value) |
            Q(engineer__name__icontains=value) |
            Q(notes__icontains=value) |
            id_query
        ).distinct()

    def filter_phase(self, queryset, name, value):
        if not value:
            return queryset
        from apps.farm.models import LocationNode
        try:
            node = LocationNode.objects.get(id=value)
            descendant_ids = list(node.get_descendants(include_self=True).values_list('id', flat=True))
            return queryset.filter(details__phase_id__in=descendant_ids).distinct()
        except Exception:
            return queryset

    def filter_enclosure(self, queryset, name, value):
        if not value:
            return queryset
        from apps.farm.models import LocationNode
        try:
            node = LocationNode.objects.get(id=value)
            ancestor_ids = list(node.get_ancestors(include_self=True).values_list('id', flat=True))
            return queryset.filter(details__phase_id__in=ancestor_ids).distinct()
        except Exception:
            return queryset


class IrrigationListCreate(generics.ListCreateAPIView):
    serializer_class = IrrigationReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IrrigationFilter
    pagination_class = TaskPagination

    def get_queryset(self):
        return _for_company(
            IrrigationReport.objects.select_related("engineer", "contractor")
            .prefetch_related(
                "details",
                "details__phase",
                "details__fertilizers",
                "details__fertilizers__fertilizer_item",
            )
            .all(),
            self.request,
        )

    def perform_create(self, serializer):
        serializer.save(company=getattr(self.request, "company", None))


class IrrigationDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = IrrigationReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return _for_company(IrrigationReport.objects.all(), self.request)


class PestControlFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="date", lookup_expr="lte")
    enclosure = django_filters.UUIDFilter(method="filter_enclosure")

    class Meta:
        model = PestControlReport
        fields = ["enclosure"]

    def filter_enclosure(self, queryset, name, value):
        if not value:
            return queryset
        from apps.reports.models import OperationalLocationAllocation
        from django.contrib.contenttypes.models import ContentType
        try:
            content_type = ContentType.objects.get_for_model(PestControlReport)
            allocs = OperationalLocationAllocation.objects.filter(
                content_type=content_type,
                enclosure_id=value
            )
            report_ids = allocs.values_list('object_id', flat=True)
            return queryset.filter(id__in=report_ids)
        except Exception:
            return queryset


class PestControlListCreate(generics.ListCreateAPIView):
    serializer_class = PestControlReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = PestControlFilter

    def get_queryset(self):
        return _for_company(PestControlReport.objects.all(), self.request)

    def perform_create(self, serializer):
        serializer.save(company=getattr(self.request, "company", None))


class PestControlDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PestControlReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return _for_company(PestControlReport.objects.all(), self.request)


class OperationalLocationAllocationListCreate(generics.ListCreateAPIView):
    serializer_class = OperationalLocationAllocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return _for_company(OperationalLocationAllocation.objects.all(), self.request)

    def perform_create(self, serializer):
        serializer.save(company=getattr(self.request, "company", None))


class OperationalLocationAllocationDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OperationalLocationAllocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return _for_company(OperationalLocationAllocation.objects.all(), self.request)



class DailyTaskSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.reports.models import OperationLog
        # Use OperationLog as source of truth for Phase 3 analytics
        summary = (
            _for_company(OperationLog.objects.all(), request)
            .values(sector=F("location__parent__name"))
            .annotate(
                total_tasks=Count("id"),
                total_productivity=Sum("actual_productivity"),
                total_workers=Sum(F("company_workers") + F("contractor_workers")),
            )
            .order_by("sector")
        )
        return Response(summary)


class DailyTaskExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        import csv
        from django.http import HttpResponse
        
        # Reuse the same queryset logic
        qs = DailyTaskReport.objects.select_related(
            "engineer", "operation", "location"
        ).order_by("-report_date")
        qs = _for_company(qs, request)
        
        # Apply filters
        fs = DailyTaskFilter(request.GET, queryset=qs)
        reports = fs.qs

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reports_export.csv"'
        response.write(u'\ufeff'.encode('utf8')) # BOM for Excel UTF-8 support
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Date', 'Status', 'Operation', 'Location', 'Engineer', 'Productivity', 'Unit'])
        
        for r in reports:
            writer.writerow([
                r.id,
                r.report_date,
                r.status,
                r.operation.name if r.operation else "",
                r.location.name if r.location else (r.enclosure_name or ""),
                r.engineer.name if r.engineer else "",
                r.actual_productivity,
                r.unit.name if r.unit else ""
            ])
            
        return response


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


class ApplicationMethodListView(generics.ListCreateAPIView):
    serializer_class = ApplicationMethodSerializer
    permission_classes = [IsManagerOrReadOnly]

    def get_queryset(self):
        return _for_company(ApplicationMethod.objects.filter(is_active=True), self.request)

    def perform_create(self, serializer):
        company = getattr(self.request, "company", None)
        if not company:
            from apps.users.models import Company
            company = Company.objects.first()
        serializer.save(company=company)


class ApplicationMethodDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ApplicationMethodSerializer
    permission_classes = [IsManagerOrReadOnly]

    def get_queryset(self):
        return _for_company(ApplicationMethod.objects.all(), self.request)

    def perform_destroy(self, instance):
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


class SeasonListView(generics.ListCreateAPIView):
    serializer_class = SeasonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Season.objects.all().order_by("-start_date")
        return _for_company(qs, self.request)

    def perform_create(self, serializer):
        company = getattr(self.request, "company", None)
        if not company:
            from apps.users.models import Company
            company = Company.objects.first()
        serializer.save(company=company)


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
        company = getattr(self.request, "company", None)
        if not company:
            from apps.users.models import Company
            company = Company.objects.first()
        instance = serializer.save(company=company)
        
        # Phase 2 Dual-Write Bridge
        from services.reports_service import sync_child_operation_log
        sync_child_operation_log(instance)


class AttachmentDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Attachment.objects.filter(
            report__in=_for_company(DailyTaskReport.objects.all(), self.request)
        )


class GalleryMediaListCreate(generics.ListCreateAPIView):
    serializer_class = GalleryMediaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["file_type"]

    def get_queryset(self):
        return _for_company(GalleryMedia.objects.all(), self.request)


class GalleryMediaDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GalleryMediaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return _for_company(GalleryMedia.objects.all(), self.request)


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
        company = _get_company(request)
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
        company = _get_company(request)
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        data = productivity_analytics(company, start_date=start_date, end_date=end_date)
        serializer = ProductivityAnalyticsSerializer(data)
        return Response(serializer.data)


class ComparisonAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(comparison_analytics(_get_company(request)))


class DashboardAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(dashboard_bundle(_get_company(request)))


class SmartInsightsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = _get_company(request)
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
        company = _get_company(request)
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
        from apps.reports.models import OperationLog
        # In Phase 3, we aggregate metrics from OperationLog
        qs = _for_company(OperationLog.objects.all(), request)
        
        # Filter for enclosure-level logs to maintain consistency with old logic
        qs = qs.filter(location__type="ENCLOSURE")

        trends = list(
            qs.values(report_date=F("report__report_date"))
            .annotate(
                total_reports=Count("report", distinct=True),
                total_workers=Sum(F("company_workers") + F("contractor_workers")),
                total_hours=Sum("work_hours"),
                # cost aggregation from labor entries related to the log
                total_cost=Sum(
                    ExpressionWrapper(
                        F("labor_entries__hours") * F("labor_entries__worker_rate"),
                        output_field=FloatField()
                    )
                ),
            )
            .order_by("report_date")
        )

        return Response({"trends": trends})


class InsightsAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.reports.models import OperationLog
        qs = _for_company(OperationLog.objects.all(), request).filter(
            location__type="ENCLOSURE"
        )

        # Productivity: Output per worker
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

        # Cost: Derived from LaborEntry hours * rate
        cost_per_operation = qs.values("operation__name").annotate(
            total_cost=Sum(
                ExpressionWrapper(
                    F("labor_entries__hours") * F("labor_entries__worker_rate"),
                    output_field=FloatField()
                )
            )
        )

        highest_cost_operation = cost_per_operation.order_by("-total_cost").first()

        company = _get_company(request)
        return Response(
            {
                "best_productivity": best_productivity,
                "worst_productivity": worst_productivity,
                "highest_cost_operation": highest_cost_operation,
                "alerts": smart_alerts(company),
                "suggestions": smart_suggestions(company),
            }
        )


class MediaFeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        from apps.production.models import HarvestAttachment
        from apps.production.serializers import HarvestAttachmentSerializer

        attachments_qs = _for_company(Attachment.objects.all(), request)
        harvest_qs = _for_company(HarvestAttachment.objects.all(), request)
        gallery_qs = _for_company(GalleryMedia.objects.all(), request)

        engineer = request.query_params.get("engineer")
        enclosure = request.query_params.get("enclosure")
        operation_type = request.query_params.get("operation_type")
        date = request.query_params.get("date")
        report = request.query_params.get("report")
        file_type = request.query_params.get("file_type") or request.query_params.get("type")

        if engineer:
            attachments_qs = attachments_qs.filter(report__engineer_id=engineer)
            harvest_qs = harvest_qs.filter(
                Q(report__supervisor_id=engineer) | Q(report__created_by_id=engineer)
            )
            gallery_qs = gallery_qs.filter(uploaded_by_id=engineer)

        if enclosure:
            attachments_qs = attachments_qs.filter(
                Q(report__location_id=enclosure) | Q(operation_log__location_id=enclosure)
            )
            harvest_qs = harvest_qs.filter(report__location_id=enclosure)
            gallery_qs = gallery_qs.none()

        if operation_type:
            attachments_qs = attachments_qs.filter(
                Q(report__operation_id=operation_type) | Q(operation_log__operation_id=operation_type)
            )
            harvest_qs = harvest_qs.none()
            gallery_qs = gallery_qs.none()

        if date:
            attachments_qs = attachments_qs.filter(report__report_date=date)
            harvest_qs = harvest_qs.filter(report__harvest_date=date)
            gallery_qs = gallery_qs.none()

        if report:
            attachments_qs = attachments_qs.filter(report_id=report)
            harvest_qs = harvest_qs.filter(report_id=report)
            gallery_qs = gallery_qs.none()

        if file_type:
            attachments_qs = attachments_qs.filter(file_type=file_type)
            harvest_qs = harvest_qs.filter(file_type=file_type)
            gallery_qs = gallery_qs.filter(file_type=file_type)

        attachments_qs = attachments_qs.select_related(
            "report", "report__engineer", "report__location", "operation_log"
        )
        harvest_qs = harvest_qs.select_related(
            "report", "report__supervisor", "report__created_by", "report__location"
        )
        gallery_qs = gallery_qs.select_related("uploaded_by")

        attachments_data = AttachmentSerializer(attachments_qs, many=True).data
        harvest_data = HarvestAttachmentSerializer(harvest_qs, many=True).data
        gallery_data = GalleryMediaSerializer(gallery_qs, many=True).data

        media_items = []
        media_items.extend(attachments_data)
        media_items.extend(harvest_data)
        media_items.extend(gallery_data)

        def get_created_at(item):
            return item.get("created_at") or "1970-01-01T00:00:00Z"
        media_items.sort(key=get_created_at, reverse=True)

        page = request.query_params.get("page")
        page_size = request.query_params.get("page_size") or 20

        if page:
            try:
                page = int(page)
                page_size = int(page_size)
                start = (page - 1) * page_size
                end = start + page_size
                paginated_items = media_items[start:end]
                
                has_next = end < len(media_items)
                has_prev = start > 0
                total_count = len(media_items)
                total_pages = (total_count + page_size - 1) // page_size
                
                return Response({
                    "results": paginated_items,
                    "count": total_count,
                    "total_pages": total_pages,
                    "current_page": page,
                    "has_next": has_next,
                    "has_prev": has_prev
                })
            except ValueError:
                pass

        return Response(media_items)


class OperationCoverageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = _get_company(request)
        season_id = request.query_params.get("season")
        location_id = request.query_params.get("location")
        operation_id = request.query_params.get("operation")
        time_frame = request.query_params.get("time_frame", "season")

        if not season_id:
            return Response({"error": "season parameter is required"}, status=400)

        data = get_operation_coverage(
            company=company,
            season_id=season_id,
            location_id=location_id,
            operation_id=operation_id,
            time_frame=time_frame
        )
        return Response(data)


class IrrigationIntelligenceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = _get_company(request)
        season_id = request.query_params.get("season")
        location_id = request.query_params.get("location")
        time_frame = request.query_params.get("time_frame", "season")

        if not season_id:
            return Response({"error": "season parameter is required"}, status=400)

        data = irrigation_analytics_by_season(
            company=company,
            season_id=season_id,
            location_id=location_id,
            time_frame=time_frame
        )
        return Response(data)


class HarvestIntelligenceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = _get_company(request)
        season_id = request.query_params.get("season")
        location_id = request.query_params.get("location")
        time_frame = request.query_params.get("time_frame", "season")

        if not season_id:
            return Response({"error": "season parameter is required"}, status=400)

        data = harvest_analytics_by_season(
            company=company,
            season_id=season_id,
            location_id=location_id,
            time_frame=time_frame
        )
        return Response(data)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_node_tree_count(request, pk):
    from apps.farm.models import LocationNode, EnclosureProfile, StageProfile
    company = _get_company(request)
    try:
        node = LocationNode.objects.get(id=pk, company=company)
    except LocationNode.DoesNotExist:
        return Response({"error": "Location node not found"}, status=404)

    tree_count = request.data.get("tree_count")
    if tree_count is None:
        return Response({"error": "tree_count is required"}, status=400)

    try:
        tree_count = int(tree_count)
        if tree_count < 0:
            raise ValueError()
    except ValueError:
        return Response({"error": "tree_count must be a positive integer"}, status=400)

    if node.type == LocationNode.TYPE_STAGE:
        profile, created = StageProfile.objects.update_or_create(
            location_node=node,
            company=company,
            defaults={"tree_count": tree_count}
        )
        try:
            profile.clean()
            profile.save()
        except ValidationError as e:
            return Response({"error": e.message_dict if hasattr(e, 'message_dict') else str(e)}, status=400)
    elif node.type == LocationNode.TYPE_ENCLOSURE:
        profile, created = EnclosureProfile.objects.update_or_create(
            location_node=node,
            company=company,
            defaults={"tree_count": tree_count}
        )
        try:
            profile.clean()
            profile.save()
        except ValidationError as e:
            return Response({"error": e.message_dict if hasattr(e, 'message_dict') else str(e)}, status=400)
    else:
        return Response({"error": "Tree count can only be updated for Stage or Enclosure nodes"}, status=400)

    return Response({"success": True, "tree_count": tree_count})


# Centralized authorization injection for reports views
import inspect

from rest_framework.views import APIView
from permissions.role_permissions import HasModuleAccess

for name, obj in list(globals().items()):
    if inspect.isclass(obj) and issubclass(obj, APIView) and obj.__module__ == __name__:
        perms = list(getattr(obj, "permission_classes", []))
        if HasModuleAccess not in perms:
            perms.insert(0, HasModuleAccess)
        obj.permission_classes = perms
        obj.required_module = "reports"

