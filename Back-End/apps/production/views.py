from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import HarvestReport, SortingReport, HarvestAttachment
from .serializers import HarvestReportSerializer, SortingReportSerializer
from services.production_workflows import HarvestWorkflowService, SortingWorkflowService


from .filters import HarvestFilter

class HarvestReportViewSet(viewsets.ModelViewSet):
    serializer_class = HarvestReportSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = HarvestFilter
    search_fields = ["location__name", "notes", "supervisor__name"]
    ordering_fields = ["harvest_date", "created_at", "quantity", "labor_hours"]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def _get_company(self):
        """Robust company resolution with fallback for JWT/Anonymous profiles"""
        user = self.request.user
        company = getattr(user, 'company', None)
        if not company:
            from apps.users.models import Company
            company = Company.objects.first()
        return company

    def get_queryset(self):
        company = self._get_company()
        return HarvestReport.objects.filter(company=company).select_related(
            'location', 'location__profile', 'season', 'variety', 'unit', 'supervisor', 'created_by'
        ).prefetch_related('attachments')

    def perform_create(self, serializer):
        company = self._get_company()
        extra_data = {
            "company": company,
            "created_by": self.request.user
        }
        if not self.request.data.get('supervisor'):
            extra_data["supervisor"] = self.request.user
            
        report = serializer.save(**extra_data)
        self._handle_attachments(report, company)

    def perform_update(self, serializer):
        company = self._get_company()
        user = self.request.user
        instance = self.get_object()
        
        # Check if user is manager+ to allow editing finalized reports
        is_manager_plus = False
        if user and user.is_authenticated:
            is_manager_plus = user.role in ['SUPER_ADMIN', 'OWNER', 'MANAGER', 'ADMIN']
        
        extra_data = {"company": company}
        
        if instance.status == HarvestReport.STATE_FINALIZED:
            if not is_manager_plus:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Finalized reports are immutable and cannot be edited.")
            
            # Require override_reason
            override_reason = serializer.validated_data.get("override_reason") or self.request.data.get("override_reason")
            if not override_reason:
                from rest_framework.exceptions import ValidationError as DRFValidationError
                raise DRFValidationError({"override_reason": "سبب التعديل الاستثنائي مطلوب للتقارير النهائية."})
            
            from django.utils import timezone
            extra_data.update({
                "override_by": user,
                "override_at": timezone.now(),
                "was_overridden": True,
                "override_reason": override_reason,
            })
            extra_data["force_update"] = True
            
        elif not is_manager_plus and instance.status not in [HarvestReport.STATE_DRAFT, HarvestReport.STATE_SUBMITTED]:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Engineers can only edit draft or submitted reports.")

        if not self.request.data.get('supervisor'):
             if not instance.supervisor:
                 extra_data["supervisor"] = self.request.user
                 
        report = serializer.save(**extra_data)
        self._handle_attachments(report, company)

    def _handle_attachments(self, report, company):
        attachments = self.request.FILES.getlist('attachments')
        for attachment in attachments:
            from services.upload_service import upload_file
            try:
                url = upload_file(attachment, folder="production/harvest")
                content_type = attachment.content_type or ""
                if content_type.startswith("image/"):
                    ft = "IMAGE"
                elif content_type.startswith("video/"):
                    ft = "VIDEO"
                else:
                    ft = "FILE"
                
                HarvestAttachment.objects.create(
                    company=company,
                    report=report,
                    file_url=url,
                    file_type=ft
                )
            except Exception as e:
                print(f"Failed to upload production attachment: {e}")


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

    def perform_update(self, serializer):
        user = self.request.user
        is_manager_plus = False
        if user and user.is_authenticated:
            is_manager_plus = user.role in ['SUPER_ADMIN', 'OWNER', 'MANAGER', 'ADMIN']
            
        extra_data = {"company": user.company}
        if is_manager_plus:
            extra_data["force_update"] = True
            
        serializer.save(**extra_data)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)

    @action(detail=True, methods=["post"])
    def finalize(self, request, pk=None):
        try:
            report = SortingWorkflowService.finalize_report(pk, request.user)
            return Response(SortingReportSerializer(report).data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import HarvestAttachmentSerializer

class HarvestAttachmentListCreate(generics.ListCreateAPIView):
    serializer_class = HarvestAttachmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["file_type"]

    def get_queryset(self):
        user = self.request.user
        company = getattr(user, 'company', None)
        if not company:
            from apps.users.models import Company
            company = Company.objects.first()
        return HarvestAttachment.objects.filter(company=company)

    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None)
        if not company:
            from apps.users.models import Company
            company = Company.objects.first()
        serializer.save(company=company)


class HarvestAttachmentDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HarvestAttachmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        company = getattr(user, 'company', None)
        if not company:
            from apps.users.models import Company
            company = Company.objects.first()
        return HarvestAttachment.objects.filter(company=company)


