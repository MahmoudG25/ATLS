import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from datetime import date
from django.utils import timezone

from apps.users.models import User, Company
from apps.farm.models import Farm, LocationNode
from apps.reports.models import (
    DailyTaskReport, Operation, Season, Variety, Unit, Attachment, GalleryMedia
)
from apps.production.models import HarvestReport, HarvestAttachment
from serializers.reports_serializers import AttachmentSerializer
from apps.production.serializers import HarvestAttachmentSerializer

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def setup_data():
    # Create Company
    company = Company.objects.create(name="Test Company", subscription_plan="enterprise")
    
    # Create User without 'username' parameter
    user = User.objects.create(
        email="test@example.com",
        name="Test User",
        company=company,
        role="ENGINEER",
        is_active=True,
        is_approved=True
    )
    user.set_password("password")
    user.save()
    
    # Create Season
    season = Season.objects.create(
        name="2026",
        company=company,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        status="OPEN"
    )
    
    # Create Unit
    unit = Unit.objects.create(name="كجم", company=company)
    
    # Create Variety
    variety = Variety.objects.create(name="مجدول", company=company)
    
    # Create Farm & Location Node
    farm = Farm.objects.create(name="Test Farm", company=company)
    location = LocationNode.objects.create(
        farm=farm,
        name="Enclosure 1",
        type=LocationNode.TYPE_ENCLOSURE,
        company=company,
        is_active=True
    )
    
    # Create Operation
    operation = Operation.objects.create(
        name="Test Operation",
        company=company,
        category="maintenance",
        profile_type="generic"
    )
    
    # Create DailyTaskReport
    task_report = DailyTaskReport.objects.create(
        company=company,
        engineer=user,
        report_date=date(2026, 5, 22),
        location=location,
        variety=variety,
        company_workers=5,
        contractor_workers=0,
        operation=operation,
        unit=unit,
        actual_productivity=100.0,
        work_hours=8.0,
        notes="Daily report notes",
        status="draft"
    )
    
    # Create HarvestReport
    harvest_report = HarvestReport.objects.create(
        company=company,
        location=location,
        season=season,
        harvest_date=date(2026, 5, 22),
        variety=variety,
        quantity=500.00,
        unit=unit,
        status=HarvestReport.STATE_DRAFT,
        supervisor=user,
        created_by=user
    )
    
    return {
        "company": company,
        "user": user,
        "season": season,
        "unit": unit,
        "variety": variety,
        "location": location,
        "operation": operation,
        "task_report": task_report,
        "harvest_report": harvest_report
    }

@pytest.mark.django_db
def test_attachment_serializer_representation_and_internal_value(setup_data):
    task_report = setup_data["task_report"]
    company = setup_data["company"]
    
    # Create standard attachment
    attachment = Attachment.objects.create(
        company=company,
        report=task_report,
        file_url="https://res.cloudinary.com/demo/image/upload/sample.jpg",
        file_type="IMAGE"
    )
    
    serializer = AttachmentSerializer(instance=attachment)
    data = serializer.data
    
    # Check unified field mapping in serialization output
    assert data["url"] == "https://res.cloudinary.com/demo/image/upload/sample.jpg"
    assert data["type"] == "IMAGE"
    assert data["file_url"] == "https://res.cloudinary.com/demo/image/upload/sample.jpg"
    assert data["file_type"] == "IMAGE"
    assert data["thumbnail_url"] == "https://res.cloudinary.com/demo/image/upload/c_thumb,w_200/sample.jpg"
    assert data["source"] == "daily_task"
    assert data["uploaded_by"] == "Test User"
    assert data["report_title"] == f"Test Operation - Enclosure 1 (2026-05-22)"
    
    # Check deserialization supports both write formats
    write_data_legacy = {
        "company": company.id,
        "report": task_report.id,
        "file_url": "https://res.cloudinary.com/demo/image/upload/sample2.jpg",
        "file_type": "IMAGE"
    }
    
    deserializer_legacy = AttachmentSerializer(data=write_data_legacy)
    assert deserializer_legacy.is_valid(), deserializer_legacy.errors
    validated_legacy = deserializer_legacy.validated_data
    assert validated_legacy["file_url"] == "https://res.cloudinary.com/demo/image/upload/sample2.jpg"
    assert validated_legacy["file_type"] == "IMAGE"
    
    write_data_unified = {
        "company": company.id,
        "report": task_report.id,
        "url": "https://res.cloudinary.com/demo/image/upload/sample3.jpg",
        "type": "IMAGE"
    }
    deserializer_unified = AttachmentSerializer(data=write_data_unified)
    assert deserializer_unified.is_valid(), deserializer_unified.errors
    validated_unified = deserializer_unified.validated_data
    assert validated_unified["file_url"] == "https://res.cloudinary.com/demo/image/upload/sample3.jpg"
    assert validated_unified["file_type"] == "IMAGE"

@pytest.mark.django_db
def test_harvest_attachment_serializer_representation_and_internal_value(setup_data):
    harvest_report = setup_data["harvest_report"]
    company = setup_data["company"]
    
    attachment = HarvestAttachment.objects.create(
        company=company,
        report=harvest_report,
        file_url="https://res.cloudinary.com/demo/image/upload/harvest.jpg",
        file_type="IMAGE"
    )
    
    serializer = HarvestAttachmentSerializer(instance=attachment)
    data = serializer.data
    
    assert data["url"] == "https://res.cloudinary.com/demo/image/upload/harvest.jpg"
    assert data["type"] == "IMAGE"
    assert data["file_url"] == "https://res.cloudinary.com/demo/image/upload/harvest.jpg"
    assert data["file_type"] == "IMAGE"
    assert data["source"] == "harvest"
    assert data["uploaded_by"] == "Test User"
    assert data["report_title"] == "حصاد - Enclosure 1 (2026-05-22)"
    
    # Check deserialization supports both write formats
    write_data_unified = {
        "report": harvest_report.id,
        "url": "https://res.cloudinary.com/demo/image/upload/harvest2.jpg",
        "type": "IMAGE"
    }
    deserializer = HarvestAttachmentSerializer(data=write_data_unified)
    assert deserializer.is_valid(), deserializer.errors
    validated = deserializer.validated_data
    assert validated["file_url"] == "https://res.cloudinary.com/demo/image/upload/harvest2.jpg"
    assert validated["file_type"] == "IMAGE"

@pytest.mark.django_db
def test_media_feed_view_aggregation_and_filters(api_client, setup_data):
    user = setup_data["user"]
    company = setup_data["company"]
    task_report = setup_data["task_report"]
    harvest_report = setup_data["harvest_report"]
    location = setup_data["location"]
    
    # Authenticate client
    api_client.force_authenticate(user=user)
    
    # Create attachments across types
    task_att = Attachment.objects.create(
        company=company,
        report=task_report,
        file_url="https://res.cloudinary.com/demo/image/upload/task_pic.jpg",
        file_type="IMAGE"
    )
    
    harvest_att = HarvestAttachment.objects.create(
        company=company,
        report=harvest_report,
        file_url="https://res.cloudinary.com/demo/image/upload/harvest_pic.jpg",
        file_type="IMAGE"
    )
    
    gallery_media = GalleryMedia.objects.create(
        company=company,
        uploaded_by=user,
        file_url="https://res.cloudinary.com/demo/image/upload/gallery_pic.jpg",
        file_type="IMAGE"
    )
    
    url = reverse("reports_media_feed")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    
    results = response.data
    # Aggregate feeds should return all 3 media files
    assert len(results) == 3
    
    urls = [item["url"] for item in results]
    assert "https://res.cloudinary.com/demo/image/upload/task_pic.jpg" in urls
    assert "https://res.cloudinary.com/demo/image/upload/harvest_pic.jpg" in urls
    assert "https://res.cloudinary.com/demo/image/upload/gallery_pic.jpg" in urls
    
    # Filter by enclosure (only report-associated ones, gallery media doesn't have enclosure)
    response_filter_enc = api_client.get(url, {"enclosure": str(location.id)})
    assert response_filter_enc.status_code == status.HTTP_200_OK
    results_enc = response_filter_enc.data
    assert len(results_enc) == 2
    enc_urls = [item["url"] for item in results_enc]
    assert "https://res.cloudinary.com/demo/image/upload/task_pic.jpg" in enc_urls
    assert "https://res.cloudinary.com/demo/image/upload/harvest_pic.jpg" in enc_urls
    assert "https://res.cloudinary.com/demo/image/upload/gallery_pic.jpg" not in enc_urls
