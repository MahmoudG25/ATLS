import logging
from rest_framework import generics, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.shortcuts import get_object_or_404
from core.tenant import TenantAwareModel
from apps.hr.models import (
    Worker,
    PayrollPeriod,
    PayrollTransaction,
    PendingWorkerReview,
    ContractorLedger,
    Employee,
    EmployeeDocument,
    PayrollComponent,
    LeaveRequest
)
from apps.reports.models import LaborEntry, Contractor

logger = logging.getLogger(__name__)

def _get_company(request):
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

    if user.is_superuser or getattr(user, "role", None) == "SUPER_ADMIN":
        return queryset

    company = _get_company(request)
    if not company:
        return queryset.none()

    if hasattr(queryset, "for_company"):
        qs = queryset.for_company(company)
    else:
        qs = queryset.filter(company=company)
        
    return qs

# ─── SERIALIZERS ──────────────────────────────────────────────────────────────

class WorkerSerializer(serializers.ModelSerializer):
    hourly_rate = serializers.ReadOnlyField()
    total_overtime = serializers.SerializerMethodField()
    total_deductions = serializers.SerializerMethodField()
    total_overtime_hours = serializers.SerializerMethodField()
    total_deductions_hours = serializers.SerializerMethodField()
    net_salary = serializers.SerializerMethodField()

    class Meta:
        model = Worker
        fields = [
            "id",
            "name",
            "worker_type",
            "contractor",
            "badge_number",
            "national_id",
            "address",
            "hire_date",
            "monthly_salary",
            "standard_work_hours",
            "status",
            "notes",
            "hourly_rate",
            "total_overtime",
            "total_deductions",
            "total_overtime_hours",
            "total_deductions_hours",
            "net_salary",
            "created_at",
        ]

    def get_total_overtime(self, obj):
        period = PayrollPeriod.objects.filter(company=obj.company, is_closed=False).order_by("-start_date").first()
        if not period:
            period = PayrollPeriod.objects.filter(company=obj.company).order_by("-start_date").first()
        if not period:
            return 0.0
        
        txs = PayrollTransaction.objects.filter(
            worker=obj,
            period=period,
            transaction_type="OVERTIME",
            status__in=["PENDING", "APPROVED"]
        ).aggregate(total=Sum("amount"))
        return float(txs["total"] or 0.0)

    def get_total_overtime_hours(self, obj):
        period = PayrollPeriod.objects.filter(company=obj.company, is_closed=False).order_by("-start_date").first()
        if not period:
            period = PayrollPeriod.objects.filter(company=obj.company).order_by("-start_date").first()
        if not period:
            return 0.0
        
        txs = PayrollTransaction.objects.filter(
            worker=obj,
            period=period,
            transaction_type="OVERTIME",
            status__in=["PENDING", "APPROVED"]
        ).aggregate(total=Sum("hours"))
        return float(txs["total"] or 0.0)

    def get_total_deductions(self, obj):
        period = PayrollPeriod.objects.filter(company=obj.company, is_closed=False).order_by("-start_date").first()
        if not period:
            period = PayrollPeriod.objects.filter(company=obj.company).order_by("-start_date").first()
        if not period:
            return 0.0
            
        txs = PayrollTransaction.objects.filter(
            worker=obj,
            period=period,
            transaction_type="DEDUCTION",
            status__in=["PENDING", "APPROVED"]
        ).aggregate(total=Sum("amount"))
        return float(txs["total"] or 0.0)

    def get_total_deductions_hours(self, obj):
        period = PayrollPeriod.objects.filter(company=obj.company, is_closed=False).order_by("-start_date").first()
        if not period:
            period = PayrollPeriod.objects.filter(company=obj.company).order_by("-start_date").first()
        if not period:
            return 0.0
            
        txs = PayrollTransaction.objects.filter(
            worker=obj,
            period=period,
            transaction_type="DEDUCTION",
            status__in=["PENDING", "APPROVED"]
        ).aggregate(total=Sum("hours"))
        return float(txs["total"] or 0.0)

    def get_net_salary(self, obj):
        overtime = self.get_total_overtime(obj)
        deductions = self.get_total_deductions(obj)
        base = float(obj.monthly_salary) if obj.monthly_salary else 0.0
        return base + overtime - deductions

    def create(self, validated_data):
        request = self.context.get("request")
        company = _get_company(request)
        validated_data["company"] = company
        return super().create(validated_data)


class PayrollPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollPeriod
        fields = ["id", "name", "start_date", "end_date", "is_closed"]

    def create(self, validated_data):
        request = self.context.get("request")
        company = _get_company(request)
        validated_data["company"] = company
        return super().create(validated_data)


class PayrollTransactionSerializer(serializers.ModelSerializer):
    worker_name = serializers.CharField(source="worker.name", read_only=True)
    worker_type = serializers.CharField(source="worker.worker_type", read_only=True)
    period = serializers.PrimaryKeyRelatedField(
        queryset=PayrollPeriod.objects.all(),
        required=False,
        allow_null=True
    )
    period_name = serializers.CharField(source="period.name", read_only=True)
    report_id = serializers.UUIDField(source="labor_entry.report.id", read_only=True)
    engineer_name = serializers.SerializerMethodField()

    class Meta:
        model = PayrollTransaction
        fields = [
            "id",
            "worker",
            "worker_name",
            "worker_type",
            "period",
            "period_name",
            "date",
            "transaction_type",
            "hours",
            "amount",
            "status",
            "notes",
            "labor_entry",
            "report_id",
            "engineer_name",
        ]

    def get_engineer_name(self, obj):
        try:
            if obj.labor_entry:
                if obj.labor_entry.report and obj.labor_entry.report.engineer:
                    return obj.labor_entry.report.engineer.name
                if obj.labor_entry.harvest_report and (obj.labor_entry.harvest_report.supervisor or obj.labor_entry.harvest_report.created_by):
                    user = obj.labor_entry.harvest_report.supervisor or obj.labor_entry.harvest_report.created_by
                    return user.name or user.email
                if obj.labor_entry.operation_log:
                    op_log = obj.labor_entry.operation_log
                    if op_log.source_type == "IRRIGATION" and op_log.source_id:
                        from apps.reports.models import IrrigationReport
                        rep = IrrigationReport.objects.filter(id=op_log.source_id).first()
                        if rep and rep.engineer:
                            return rep.engineer.name
                    if op_log.source_type == "PEST_CONTROL" and op_log.source_id:
                        from apps.reports.models import PestControlReport
                        rep = PestControlReport.objects.filter(id=op_log.source_id).first()
                        if rep and rep.engineer:
                            return rep.engineer.name
        except Exception:
            pass
        return "النظام"

    def create(self, validated_data):
        request = self.context.get("request")
        company = _get_company(request)
        validated_data["company"] = company

        # default status to APPROVED if created via serializer
        if "status" not in validated_data:
            validated_data["status"] = "APPROVED"

        # default period to latest open period or create one on the fly
        period = validated_data.get("period")
        if not period:
            period = PayrollPeriod.objects.filter(company=company, is_closed=False).order_by("-start_date").first()
            if not period:
                import datetime
                today = datetime.date.today()
                start_of_month = today.replace(day=1)
                if today.month == 12:
                    end_of_month = today.replace(year=today.year + 1, month=1, day=1) - datetime.timedelta(days=1)
                else:
                    end_of_month = today.replace(month=today.month + 1, day=1) - datetime.timedelta(days=1)
                
                period_name = start_of_month.strftime("%B %Y")
                period = PayrollPeriod.objects.create(
                    company=company,
                    name=period_name,
                    start_date=start_of_month,
                    end_date=end_of_month,
                    is_closed=False
                )
            validated_data["period"] = period

        # calculate amount if hours provided but amount is 0/empty
        amount = validated_data.get("amount", 0)
        hours = validated_data.get("hours", 0)
        worker = validated_data.get("worker")
        
        if (not amount or amount == 0) and hours > 0 and worker:
            from decimal import Decimal
            rate = Decimal(f"{worker.hourly_rate:.4f}")
            amount = Decimal(hours) * rate

        # Always round amount to 2 decimal places to avoid Django Decimal ValidationErrors (max_digits=10)
        if amount:
            from decimal import Decimal
            validated_data["amount"] = Decimal(f"{amount:.2f}")

        return super().create(validated_data)


class PendingWorkerReviewSerializer(serializers.ModelSerializer):
    labor_entry_worker_type = serializers.CharField(source="labor_entry.worker_type", read_only=True)
    labor_entry_report_date = serializers.SerializerMethodField()
    labor_entry_report_id = serializers.SerializerMethodField()
    labor_entry_hours = serializers.DecimalField(source="labor_entry.hours", max_digits=8, decimal_places=2, read_only=True)
    labor_entry_overtime = serializers.DecimalField(source="labor_entry.overtime", max_digits=8, decimal_places=2, read_only=True)
    labor_entry_note = serializers.CharField(source="labor_entry.note", read_only=True, default="")
    location_name = serializers.SerializerMethodField()
    operation_name = serializers.SerializerMethodField()
    engineer_name = serializers.SerializerMethodField()

    class Meta:
        model = PendingWorkerReview
        fields = [
            "id",
            "labor_entry",
            "labor_entry_worker_type",
            "labor_entry_report_date",
            "labor_entry_report_id",
            "labor_entry_hours",
            "labor_entry_overtime",
            "labor_entry_note",
            "worker_name_fallback",
            "location_name",
            "operation_name",
            "engineer_name",
            "created_at",
            "resolved",
            "resolved_worker",
        ]

    def get_labor_entry_report_date(self, obj):
        try:
            le = obj.labor_entry
            if not le:
                return None
            if le.report:
                return le.report.report_date
            if le.harvest_report:
                return le.harvest_report.harvest_date
            if le.operation_log:
                op_log = le.operation_log
                if op_log.report:
                    return op_log.report.report_date
                if op_log.source_type == "IRRIGATION" and op_log.source_id:
                    from apps.reports.models import IrrigationReport
                    rep = IrrigationReport.objects.filter(id=op_log.source_id).first()
                    if rep:
                        return rep.date
                if op_log.source_type == "PEST_CONTROL" and op_log.source_id:
                    from apps.reports.models import PestControlReport
                    rep = PestControlReport.objects.filter(id=op_log.source_id).first()
                    if rep:
                        return rep.date
        except Exception:
            pass
        return None

    def get_labor_entry_report_id(self, obj):
        try:
            le = obj.labor_entry
            if not le:
                return None
            if le.report:
                return le.report.id
            if le.harvest_report:
                return le.harvest_report.id
            if le.operation_log:
                op_log = le.operation_log
                if op_log.report:
                    return op_log.report.id
                if op_log.source_id:
                    return op_log.source_id
        except Exception:
            pass
        return None

    def get_location_name(self, obj):
        try:
            if obj.labor_entry and obj.labor_entry.operation_log and obj.labor_entry.operation_log.location:
                return obj.labor_entry.operation_log.location.name
        except Exception:
            pass
        return "حوشة غير محددة"

    def get_operation_name(self, obj):
        try:
            if obj.labor_entry and obj.labor_entry.operation_log and obj.labor_entry.operation_log.operation:
                return obj.labor_entry.operation_log.operation.name
        except Exception:
            pass
        return "عملية غير محددة"

    def get_engineer_name(self, obj):
        try:
            if obj.labor_entry and obj.labor_entry.report and obj.labor_entry.report.engineer:
                return obj.labor_entry.report.engineer.name
            if obj.labor_entry and obj.labor_entry.harvest_report and (obj.labor_entry.harvest_report.supervisor or obj.labor_entry.harvest_report.created_by):
                user = obj.labor_entry.harvest_report.supervisor or obj.labor_entry.harvest_report.created_by
                return user.name or user.email
            if obj.labor_entry and obj.labor_entry.operation_log:
                # Resolve from operation log source report
                op_log = obj.labor_entry.operation_log
                if op_log.source_type == "IRRIGATION" and op_log.source_id:
                    from apps.reports.models import IrrigationReport
                    rep = IrrigationReport.objects.filter(id=op_log.source_id).first()
                    if rep and rep.engineer:
                        return rep.engineer.name
                if op_log.source_type == "PEST_CONTROL" and op_log.source_id:
                    from apps.reports.models import PestControlReport
                    rep = PestControlReport.objects.filter(id=op_log.source_id).first()
                    if rep and rep.engineer:
                        return rep.engineer.name
        except Exception:
            pass
        return "مهندس غير محدد"


class ContractorLedgerSerializer(serializers.ModelSerializer):
    contractor_name = serializers.CharField(source="contractor.name", read_only=True)
    engineer_name = serializers.CharField(source="labor_entry.report.engineer.name", read_only=True, default="النظام")
    location_name = serializers.CharField(source="labor_entry.operation_log.location.name", read_only=True, default="الموقع")

    class Meta:
        model = ContractorLedger
        fields = [
            "id",
            "contractor",
            "contractor_name",
            "date",
            "transaction_type",
            "hours",
            "rate",
            "amount",
            "labor_entry",
            "engineer_name",
            "location_name",
            "notes",
            "created_at",
        ]


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.user.name", read_only=True)
    document_type_display = serializers.CharField(source="get_document_type_display", read_only=True)

    class Meta:
        model = EmployeeDocument
        fields = [
            "id",
            "employee",
            "employee_name",
            "document_type",
            "document_type_display",
            "document_file",
            "issue_date",
            "expiry_date",
            "is_verified",
            "notes",
            "created_at",
        ]
        read_only_fields = ["is_verified"]

    def create(self, validated_data):
        request = self.context.get("request")
        company = _get_company(request)
        validated_data["company"] = company
        return super().create(validated_data)


class PayrollComponentSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.user.name", read_only=True)

    class Meta:
        model = PayrollComponent
        fields = [
            "id",
            "employee",
            "employee_name",
            "type",
            "name",
            "amount",
            "is_recurring",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        company = _get_company(request)
        validated_data["company"] = company
        return super().create(validated_data)


class EmployeeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.name", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    role = serializers.CharField(source="user.role", read_only=True)
    documents = EmployeeDocumentSerializer(many=True, read_only=True)
    payroll_components = PayrollComponentSerializer(many=True, read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id",
            "user",
            "name",
            "email",
            "role",
            "hire_date",
            "department",
            "position",
            "salary",
            "monthly_salary",
            "standard_work_hours",
            "status",
            "notes",
            "documents",
            "payroll_components",
            "created_at",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        company = _get_company(request)
        validated_data["company"] = company
        return super().create(validated_data)


# ─── API VIEWS ────────────────────────────────────────────────────────────────

class WorkerListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WorkerSerializer

    def get_queryset(self):
        qs = Worker.objects.all().order_by("-created_at")
        qs = _for_company(qs, self.request)
        
        # تصفية البحث بالاسم أو الكود
        search_query = self.request.query_params.get("search", None)
        if search_query:
            qs = qs.filter(
                Q(name__icontains=search_query) | 
                Q(badge_number__icontains=search_query) |
                Q(national_id__icontains=search_query)
            )
            
        # تصفية بنوع العامل
        worker_type = self.request.query_params.get("worker_type", None)
        if worker_type:
            qs = qs.filter(worker_type=worker_type)

        # تصفية بالمقاول
        contractor_id = self.request.query_params.get("contractor_id", None)
        if contractor_id:
            qs = qs.filter(contractor_id=contractor_id)
            
        return qs


class WorkerDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WorkerSerializer

    def get_queryset(self):
        return _for_company(Worker.objects.all(), self.request)


class PayrollPeriodListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PayrollPeriodSerializer

    def get_queryset(self):
        return _for_company(PayrollPeriod.objects.all(), self.request)


class PayrollTransactionListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PayrollTransactionSerializer

    def get_queryset(self):
        qs = PayrollTransaction.objects.all()
        qs = _for_company(qs, self.request)
        
        status_filter = self.request.query_params.get("status", None)
        if status_filter:
            qs = qs.filter(status=status_filter)
            
        period_filter = self.request.query_params.get("period", None)
        if period_filter:
            qs = qs.filter(period_id=period_filter)
            
        return qs


class PayrollTransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PayrollTransactionSerializer

    def get_queryset(self):
        return _for_company(PayrollTransaction.objects.all(), self.request)


class BulkApproveTransactionsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        company = _get_company(request)
        if not company:
            return Response({"error": "No company associated with user"}, status=status.HTTP_400_BAD_REQUEST)
            
        # يمكن تمرير قائمة محددة من الـ IDs أو اعتماد الكل
        transaction_ids = request.data.get("transaction_ids", None)
        
        qs = PayrollTransaction.objects.filter(company=company, status="PENDING")
        if transaction_ids:
            qs = qs.filter(id__in=transaction_ids)
            
        count = qs.count()
        qs.update(status="APPROVED")
        
        return Response({
            "message": f"تم اعتماد {count} من الحركات المعلقة بنجاح.",
            "approved_count": count
        }, status=status.HTTP_200_OK)


def _backfill_pending_reviews(company):
    """
    تقوم هذه الدالة بمسح كافة بنود العمالة للشركة (LaborEntry) المسجلة يدوياً
    وتوليد طلبات مراجعة (PendingWorkerReview) معلقة لها إن لم تكن مسجلة مسبقاً بالـ HR.
    """
    company_labor = LaborEntry.objects.filter(
        company=company,
        worker_type=LaborEntry.WORKER_TYPE_COMPANY
    )
    
    for entry in company_labor:
        name_clean = (entry.worker_name or "").strip()
        note_clean = (entry.note or "").strip()
        
        # تجاهل الأسماء الفارغة والعمالة التلقائية التي يولدها النظام
        if not name_clean or "تلقائي" in name_clean or "تلقائي" in note_clean:
            continue
            
        # التحقق مما إذا كان الاسم مسجلاً في عمال الموارد البشرية
        worker_exists = Worker.objects.filter(
            company=company,
            name=name_clean,
            worker_type="COMPANY"
        ).exists()
        
        if not worker_exists:
            # التحقق من وجود مراجعة مسبقة (نشطة أو تمت تسويتها) لمنع التكرار
            review_exists = PendingWorkerReview.objects.filter(labor_entry=entry).exists()
            if not review_exists:
                PendingWorkerReview.objects.create(
                    company=company,
                    labor_entry=entry,
                    worker_name_fallback=name_clean,
                    resolved=False
                )


class PendingWorkerReviewListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PendingWorkerReviewSerializer

    def get_queryset(self):
        company = _get_company(self.request)
        if company:
            _backfill_pending_reviews(company)

        qs = PendingWorkerReview.objects.all()
        qs = _for_company(qs, self.request)
        
        resolved_filter = self.request.query_params.get("resolved", None)
        if resolved_filter is not None:
            resolved_bool = resolved_filter.lower() == "true"
            qs = qs.filter(resolved=resolved_bool)
            
        return qs


class ResolvePendingWorkerReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        company = _get_company(request)
        pending_review = get_object_or_404(
            PendingWorkerReview.objects.filter(company=company), 
            pk=pk
        )
        
        worker_id = request.data.get("worker_id", None)
        create_new = request.data.get("create_new", False)
        
        if create_new:
            # إنشاء عامل جديد مباشرة من البيانات المدخلة
            name = request.data.get("name", pending_review.worker_name_fallback)
            worker_type = request.data.get("worker_type", "COMPANY")
            contractor_id = request.data.get("contractor_id", None)
            monthly_salary = request.data.get("monthly_salary", 0)
            national_id = request.data.get("national_id", "")
            address = request.data.get("address", "")
            hire_date = request.data.get("hire_date", None) or None
            standard_work_hours = request.data.get("standard_work_hours", 8)
            notes = request.data.get("notes", "")
            
            worker = Worker.objects.create(
                company=company,
                name=name,
                worker_type=worker_type,
                contractor_id=contractor_id,
                monthly_salary=monthly_salary,
                national_id=national_id,
                address=address,
                hire_date=hire_date,
                standard_work_hours=standard_work_hours,
                notes=notes
            )
        elif worker_id:
            # ربطه بعامل موجود مسبقاً
            worker = get_object_or_404(Worker.objects.filter(company=company), pk=worker_id)
        else:
            return Response({
                "error": "يجب تزويد worker_id لربط العامل أو تفعيل create_new لإنشاء عامل جديد."
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # تحديث المراجعة المعلقة
        pending_review.resolved = True
        pending_review.resolved_worker = worker
        pending_review.save()
        
        # ربط بند العمل الأصلي (LaborEntry) بالمقاول المعتمد وتحديث الإشارة للحسابات
        labor_entry = pending_review.labor_entry
        # NOTE: worker FK was removed in migration 0006 - only update worker_type/contractor
        labor_entry.worker_type = worker.worker_type
        labor_entry.contractor = worker.contractor
        # إعادة حفظ السطر لتفعيل حسابات المقاولين عبر الإشارات
        labor_entry.save()
        
        return Response({
            "message": "تم ربط واعتماد العامل بنجاح.",
            "worker": WorkerSerializer(worker).data
        }, status=status.HTTP_200_OK)


class ContractorLedgerListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ContractorLedgerSerializer

    def get_queryset(self):
        qs = ContractorLedger.objects.all()
        qs = _for_company(qs, self.request)
        
        contractor_id = self.request.query_params.get("contractor_id", None)
        if contractor_id:
            qs = qs.filter(contractor_id=contractor_id)
            
        return qs


class ContractorLedgerCreateView(APIView):
    """
    إنشاء حركة مالية يدوية (دفعة مسددة أو خصم) لمقاول معين.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        company = _get_company(request)
        contractor_id = request.data.get("contractor_id")
        transaction_type = request.data.get("transaction_type")
        amount = request.data.get("amount")
        date = request.data.get("date")
        notes = request.data.get("notes", "")

        # التحقق من البيانات المطلوبة
        if not contractor_id or not transaction_type or not amount or not date:
            return Response(
                {"error": "يجب تزويد contractor_id و transaction_type و amount و date."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # التحقق من أن نوع الحركة صحيح (يدوي فقط)
        allowed_types = ["PAYMENT", "DEDUCTION"]
        if transaction_type not in allowed_types:
            return Response(
                {"error": f"نوع الحركة يجب أن يكون أحد: {', '.join(allowed_types)}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            amount_decimal = float(amount)
            if amount_decimal <= 0:
                return Response({"error": "المبلغ يجب أن يكون أكبر من الصفر."}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({"error": "المبلغ غير صحيح."}, status=status.HTTP_400_BAD_REQUEST)

        contractor = get_object_or_404(Contractor.objects.filter(company=company), pk=contractor_id)

        entry = ContractorLedger.objects.create(
            company=company,
            contractor=contractor,
            date=date,
            transaction_type=transaction_type,
            hours=0,
            rate=0,
            amount=amount_decimal,
            notes=notes.strip() if notes else ""
        )

        return Response(
            ContractorLedgerSerializer(entry).data,
            status=status.HTTP_201_CREATED
        )


class ContractorDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, contractor_id):
        company = _get_company(request)
        contractor = get_object_or_404(Contractor.objects.filter(company=company), pk=contractor_id)
        
        # 1. إجمالي العمال المميزين للمقاول
        workers_qs = Worker.objects.filter(company=company, contractor=contractor).order_by("-created_at")
        total_workers = workers_qs.count()

        # 2. احتساب الأستاذ العام للمستحقات والخصومات
        ledger = ContractorLedger.objects.filter(company=company, contractor=contractor)
        
        # فلترة بالتاريخ
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")
        tx_type_filter = request.query_params.get("transaction_type")

        if date_from:
            ledger = ledger.filter(date__gte=date_from)
        if date_to:
            ledger = ledger.filter(date__lte=date_to)

        # الإيرادات/المستحقات (EARNING, OVERTIME)
        total_earnings = ContractorLedger.objects.filter(
            company=company, contractor=contractor,
            transaction_type__in=["EARNING", "OVERTIME"]
        ).aggregate(sum=Sum("amount"))["sum"] or 0
        
        # الخصومات (DEDUCTION)
        total_deductions = ContractorLedger.objects.filter(
            company=company, contractor=contractor,
            transaction_type="DEDUCTION"
        ).aggregate(sum=Sum("amount"))["sum"] or 0
        
        # المدفوعات المسددة مسبقاً (PAYMENT)
        total_paid = ContractorLedger.objects.filter(
            company=company, contractor=contractor,
            transaction_type="PAYMENT"
        ).aggregate(sum=Sum("amount"))["sum"] or 0
        
        # صافي المستحقات الحالية المتبقية للمقاول
        total_dues = (ContractorLedger.objects.filter(
            company=company, contractor=contractor,
            transaction_type__in=["EARNING", "OVERTIME"]
        ).aggregate(sum=Sum("amount"))["sum"] or 0) - total_deductions - total_paid

        # 3. قائمة المعاملات مع الفلتر
        transactions_qs = ledger.order_by("-date", "-created_at")
        if tx_type_filter and tx_type_filter != "ALL":
            transactions_qs = transactions_qs.filter(transaction_type=tx_type_filter)
        transactions = transactions_qs[:200]

        # 4. قائمة العمال التابعين
        workers_data = [
            {
                "id": str(w.id),
                "name": w.name,
                "badge_number": w.badge_number,
                "national_id": w.national_id,
                "hire_date": str(w.hire_date) if w.hire_date else None,
                "monthly_salary": float(w.monthly_salary),
                "hourly_rate": float(w.hourly_rate),
                "status": w.status,
                "notes": w.notes,
            }
            for w in workers_qs
        ]
        
        # 5. نوع النشاط
        activity_type_display = contractor.get_activity_type_display() if hasattr(contractor, 'get_activity_type_display') else ""
        
        return Response({
            "contractor": {
                "id": contractor.id,
                "name": contractor.name,
                "rate_per_hour": float(contractor.rate_per_hour),
                "is_active": contractor.is_active,
                "phone_number": contractor.phone_number,
                "email": contractor.email,
                "address": contractor.address,
                "commercial_registry": contractor.commercial_registry,
                "tax_card": contractor.tax_card,
                "contract_date": str(contractor.contract_date) if contractor.contract_date else None,
                "activity_type": contractor.activity_type,
                "activity_type_display": activity_type_display,
                "notes": contractor.notes
            },
            "summary": {
                "total_workers": total_workers,
                "total_earnings": float(total_earnings),
                "total_deductions": float(total_deductions),
                "total_paid": float(total_paid),
                "total_dues": float(total_dues)
            },
            "transactions": ContractorLedgerSerializer(transactions, many=True).data,
            "workers": workers_data
        }, status=status.HTTP_200_OK)



class EmployeeListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        qs = Employee.objects.select_related("user").prefetch_related("documents", "payroll_components").order_by("-created_at")
        return _for_company(qs, self.request)


class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        qs = Employee.objects.select_related("user")
        return _for_company(qs, self.request)


class EmployeeMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            employee = Employee.objects.select_related("user").prefetch_related("documents", "payroll_components").get(user=request.user)
            serializer = EmployeeSerializer(employee, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response({"detail": "No employee profile found for this user."}, status=status.HTTP_404_NOT_FOUND)



class EmployeeDocumentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeDocumentSerializer

    def get_queryset(self):
        qs = EmployeeDocument.objects.select_related("employee__user")
        qs = _for_company(qs, self.request)
        
        employee_id = self.request.query_params.get("employee_id", None)
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
            
        return qs


class EmployeeDocumentVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        company = _get_company(request)
        document = get_object_or_404(
            EmployeeDocument.objects.filter(company=company), 
            pk=pk
        )
        is_verified = request.data.get("is_verified", True)
        document.is_verified = is_verified
        document.save()
        return Response({
            "message": "تم تحديث حالة اعتماد المستند بنجاح.",
            "document": EmployeeDocumentSerializer(document).data
        }, status=status.HTTP_200_OK)


class PayrollComponentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PayrollComponentSerializer

    def get_queryset(self):
        qs = PayrollComponent.objects.select_related("employee__user")
        qs = _for_company(qs, self.request)
        
        employee_id = self.request.query_params.get("employee_id", None)
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
            
        return qs


class PayrollComponentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PayrollComponentSerializer

    def get_queryset(self):
        qs = PayrollComponent.objects.all()
        return _for_company(qs, self.request)


class AvailableUsersListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        company = _get_company(request)
        if not company:
            return Response([])
        
        # Filter users that belong to the same company, are active, and don't have an employee profile
        users = User.objects.filter(
            company=company,
            is_active=True,
            employee_profile__isnull=True
        ).order_by("name")
        
        data = [{"id": str(u.id), "name": u.name, "email": u.email, "role": u.role} for u in users]
        return Response(data, status=status.HTTP_200_OK)


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.user.name", read_only=True)
    leave_type_display = serializers.CharField(source="get_leave_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "employee",
            "employee_name",
            "leave_type",
            "leave_type_display",
            "start_date",
            "end_date",
            "reason",
            "status",
            "status_display",
            "created_at",
        ]
        read_only_fields = ["employee", "status", "reviewed_by"]

    def create(self, validated_data):
        request = self.context.get("request")
        company = _get_company(request)
        employee = Employee.objects.filter(user=request.user, company=company).first()
        if not employee:
            raise serializers.ValidationError("لا يوجد ملف موظف مرتبط بحسابك الحالي لتقديم طلب إجازة.")
        validated_data["employee"] = employee
        validated_data["company"] = company
        validated_data["status"] = "pending"
        return super().create(validated_data)


class LeaveRequestListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LeaveRequestSerializer

    def get_queryset(self):
        user = self.request.user
        company = _get_company(self.request)
        
        # If admin or HR, list all leave requests for the company.
        # Otherwise, only list requests for the current user's employee profile.
        if user.is_superuser or getattr(user, "role", None) in ["SUPER_ADMIN", "HR", "OWNER"]:
            qs = LeaveRequest.objects.select_related("employee__user")
            return _for_company(qs, self.request)
        
        employee = Employee.objects.filter(user=user, company=company).first()
        if not employee:
            return LeaveRequest.objects.none()
            
        return LeaveRequest.objects.filter(employee=employee, company=company).select_related("employee__user")


class LeaveRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LeaveRequestSerializer

    def get_queryset(self):
        user = self.request.user
        company = _get_company(self.request)
        if user.is_superuser or getattr(user, "role", None) in ["SUPER_ADMIN", "HR", "OWNER"]:
            qs = LeaveRequest.objects.select_related("employee__user")
            return _for_company(qs, self.request)
            
        employee = Employee.objects.filter(user=user, company=company).first()
        if not employee:
            return LeaveRequest.objects.none()
            
        return LeaveRequest.objects.filter(employee=employee, company=company)


class LeaveRequestReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        # Only admins or HR can approve/reject leave requests
        if not (user.is_superuser or getattr(user, "role", None) in ["SUPER_ADMIN", "HR", "OWNER"]):
            return Response({"detail": "غير مصرح لك باتخاذ هذا الإجراء."}, status=status.HTTP_403_FORBIDDEN)
            
        company = _get_company(request)
        leave_req = get_object_or_404(LeaveRequest.objects.filter(company=company), pk=pk)
        
        action = request.data.get("status") # approved or rejected
        if action not in ["approved", "rejected"]:
            return Response({"detail": "حالة غير صالحة. يجب أن تكون approved أو rejected."}, status=status.HTTP_400_BAD_REQUEST)
            
        leave_req.status = action
        leave_req.reviewed_by = user
        leave_req.save()
        
        # update employee status if approved
        if action == "approved":
            employee = leave_req.employee
            employee.status = "on_leave"
            employee.save()
            
        return Response({
            "message": "تم تحديث حالة طلب الإجازة بنجاح.",
            "leave_request": LeaveRequestSerializer(leave_req).data
        }, status=status.HTTP_200_OK)

