from rest_framework import serializers
from .models import HarvestReport, SortingReport, HarvestAttachment
from apps.reports.models import Season, Variety, Unit, QualityGrade, SortingCategory
from apps.farm.models import LocationNode


from django.db import transaction
from serializers.reports_serializers import LaborEntrySerializer


class HarvestAttachmentSerializer(serializers.ModelSerializer):
    report_title = serializers.SerializerMethodField()
    engineer_name = serializers.SerializerMethodField()
    location_name = serializers.SerializerMethodField()

    class Meta:
        model = HarvestAttachment
        fields = ["id", "report", "file_url", "file_type", "uploaded_at", "report_title", "engineer_name", "location_name"]

    def get_report_title(self, obj):
        if obj.report:
            loc_name = obj.report.location.name if obj.report.location else ""
            date_str = obj.report.harvest_date.strftime("%Y-%m-%d") if obj.report.harvest_date else ""
            return f"حصاد - {loc_name} ({date_str})".strip(" - ")
        return None

    def get_engineer_name(self, obj):
        if obj.report:
            user = obj.report.supervisor or obj.report.created_by
            if user:
                return user.name or user.email
        return None

    def get_location_name(self, obj):
        if obj.report and obj.report.location:
            return obj.report.location.name
        return None

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, "copy") else dict(data)
        if "url" in data and "file_url" not in data:
            data["file_url"] = data["url"]
        if "type" in data and "file_type" not in data:
            data["file_type"] = data["type"]
        return super().to_internal_value(data)

    def to_representation(self, instance):
        import mimetypes
        url = instance.file_url or ""
        file_type = instance.file_type or "FILE"
        
        thumbnail_url = url
        if file_type == "IMAGE" and "cloudinary.com" in url:
            thumbnail_url = url.replace("/upload/", "/upload/c_thumb,w_200/")
            
        filename = url.split('/')[-1] if url else ""
        mime, _ = mimetypes.guess_type(filename)
        if not mime:
            if file_type == "IMAGE":
                mime = "image/jpeg"
            elif file_type == "VIDEO":
                mime = "video/mp4"
            else:
                mime = "application/octet-stream"
                
        uploaded_by_name = None
        if hasattr(instance, "report") and instance.report:
            if hasattr(instance.report, "engineer") and instance.report.engineer:
                uploaded_by_name = instance.report.engineer.name or instance.report.engineer.username
            elif hasattr(instance.report, "supervisor") and instance.report.supervisor:
                uploaded_by_name = instance.report.supervisor.name or instance.report.supervisor.username
            elif hasattr(instance.report, "created_by") and instance.report.created_by:
                uploaded_by_name = instance.report.created_by.name or instance.report.created_by.username

        rep = {
            "id": instance.id,
            "type": file_type,
            "url": url,
            "thumbnail_url": thumbnail_url,
            "mime_type": mime,
            "file_name": filename or "attachment",
            "file_size": None,
            "source": "harvest",
            "uploaded_by": uploaded_by_name,
            "created_at": instance.uploaded_at.isoformat() if instance.uploaded_at else None,
            "file_url": url,
            "file_type": file_type,
            "uploaded_at": instance.uploaded_at.isoformat() if instance.uploaded_at else None,
            "report_title": self.get_report_title(instance),
            "engineer_name": self.get_engineer_name(instance),
            "location_name": self.get_location_name(instance),
            "report": instance.report_id,
        }
        return rep




class HarvestReportSerializer(serializers.ModelSerializer):
    location_name = serializers.SerializerMethodField()
    crop_name = serializers.SerializerMethodField()
    season_name = serializers.SerializerMethodField()
    variety_name = serializers.SerializerMethodField()
    unit_name = serializers.SerializerMethodField()
    supervisor_name = serializers.SerializerMethodField()
    creator_name = serializers.SerializerMethodField()
    attachments = HarvestAttachmentSerializer(many=True, read_only=True)
    labor_entries = serializers.ListField(
        child=serializers.DictField(), required=False, write_only=True, default=list
    )
    labor_entries_detail = LaborEntrySerializer(
        many=True, read_only=True, source="labor_entries"
    )
    force_update = serializers.BooleanField(required=False, write_only=True, default=False)


    def get_location_name(self, obj):
        return obj.location.name if obj.location else "—"

    def get_crop_name(self, obj):
        if obj.location and hasattr(obj.location, 'profile') and obj.location.profile:
            crop_type = obj.location.profile.crop_type
            mapping = {
                "palm": "نخيل",
                "olive": "زيتون"
            }
            return mapping.get(crop_type, crop_type or "—")
        return "—"

    def get_season_name(self, obj):
        return obj.season.name if obj.season else "—"

    def get_variety_name(self, obj):
        return obj.variety.name if obj.variety else "—"

    def get_unit_name(self, obj):
        return obj.unit.name if obj.unit else "—"

    def get_creator_name(self, obj):
        user = obj.created_by
        if not user:
            return self.get_supervisor_name(obj)
        return getattr(user, 'name', '') or user.email

    def get_supervisor_name(self, obj):
        user = obj.supervisor or obj.created_by
        if not user:
            return "غير محدد"
        return getattr(user, 'name', '') or user.email

    def to_internal_value(self, data):
        if "labor_entries" in data and isinstance(data["labor_entries"], str):
            import json
            try:
                if hasattr(data, "copy"):
                    data = data.copy()
                data["labor_entries"] = json.loads(data["labor_entries"])
            except Exception:
                pass
        return super().to_internal_value(data)

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("force_update", None)   # not a model field
        labor_entries_data = validated_data.pop("labor_entries", [])
        report = super().create(validated_data)
        self.sync_labor_entries(report, labor_entries_data)
        return report


    @transaction.atomic
    def update(self, instance, validated_data):
        labor_entries_data = validated_data.pop("labor_entries", None)
        force_update = validated_data.pop("force_update", False)
        if force_update:
            instance.force_update = True
        report = super().update(instance, validated_data)
        if labor_entries_data is not None:
            self.sync_labor_entries(report, labor_entries_data)
        return report

    def sync_labor_entries(self, report, labor_entries_data):
        from apps.reports.models import LaborEntry
        existing_entries = {str(le.id): le for le in report.labor_entries.all()}
        seen_ids = set()

        for entry_data in labor_entries_data:
            entry_id = entry_data.get("id")
            contractor_id = entry_data.get("contractor")

            # Only pass fields that exist on the LaborEntry model
            # (deduction_hours, deduction_amount, worker FK were removed in migration 0006)
            clean_fields = {
                "worker_name": entry_data.get("worker_name", ""),
                "worker_type": entry_data.get("worker_type", "COMPANY"),
                "worker_rate": entry_data.get("worker_rate", 0),
                "hours": entry_data.get("hours", 0),
                "overtime": entry_data.get("overtime", 0),
                "note": entry_data.get("note", ""),
                "company_id": report.company_id,
                "harvest_report": report,
            }

            if contractor_id:
                clean_fields["contractor_id"] = contractor_id

            if entry_id and str(entry_id) in existing_entries:
                entry = existing_entries[str(entry_id)]
                for k, v in clean_fields.items():
                    setattr(entry, k, v)
                entry.save()
                seen_ids.add(str(entry_id))
            else:
                entry = LaborEntry.objects.create(**clean_fields)
                seen_ids.add(str(entry.id))

        # Delete removed entries
        for old_id, old_entry in existing_entries.items():
            if old_id not in seen_ids:
                old_entry.delete()


    class Meta:
        model = HarvestReport
        fields = [
            "id", "company", "location", "location_name", "crop_name", "season", "season_name",
            "harvest_date", "variety", "variety_name", "quantity", "unit", "unit_name",
            "company_workers", "contractor_workers", "contractor_name", "labor_hours",
            "labor_count", "supervisor", "supervisor_name", "created_by", "creator_name",
            "transport_method", "is_partial", "notes", "status", "attachments",
            "variety_name_snapshot", "unit_label_snapshot", "created_at", "updated_at",
            "labor_entries", "labor_entries_detail",
            "override_reason", "override_by", "override_at", "was_overridden", "force_update"
        ]
        read_only_fields = ("company", "status", "variety_name_snapshot", "unit_label_snapshot", "override_by", "override_at", "was_overridden")



class SortingReportSerializer(serializers.ModelSerializer):
    location_name = serializers.SerializerMethodField()

    def get_location_name(self, obj):
        if obj.harvest_report and obj.harvest_report.location:
            return obj.harvest_report.location.name
        return "—"
    
    class Meta:
        model = SortingReport
        fields = "__all__"
        read_only_fields = ("company", "status", "harvest_info_snapshot")

    def validate(self, data):
        """Quantity integrity check: Sorted + Rejected + Waste <= Incoming"""
        incoming = data.get("incoming_quantity")
        final = data.get("final_quantity")
        rejected = data.get("rejected_quantity", 0)
        waste = data.get("waste_quantity", 0)
        
        if (final + rejected + waste) > incoming:
            raise serializers.ValidationError("Total output exceeds incoming quantity.")
        return data
