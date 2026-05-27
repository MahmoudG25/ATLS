import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from datetime import date
from decimal import Decimal
from django.contrib.contenttypes.models import ContentType

from apps.users.models import User, Company
from apps.farm.models import Farm, LocationNode
from apps.reports.models import (
    IrrigationReport, IrrigationDetail, AppliedFertilizer,
    PestControlReport, OperationalLocationAllocation, Contractor,
    LaborEntry, OperationLog, Season
)
from apps.hr.models import Worker
from apps.warehouse.models import Item, MaterialVerificationAlert

@pytest.fixture
def setup_data():
    # Create Company
    company = Company.objects.create(name="ATLS Test Farm Company", subscription_plan="enterprise")
    
    # Create User
    user = User.objects.create(
        email="test_eng@example.com",
        name="Engineer Test",
        company=company,
        role="ENGINEER",
        is_active=True,
        is_approved=True
    )
    user.set_password("password")
    user.save()
    
    # Create Season
    season = Season.objects.create(
        name="2026 Season",
        company=company,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        status="OPEN"
    )
    
    # Create Farm and Enclosure
    farm = Farm.objects.create(name="Beta Farm", company=company)
    enclosure = LocationNode.objects.create(
        farm=farm,
        name="Field A1",
        type=LocationNode.TYPE_ENCLOSURE,
        company=company,
        is_active=True
    )
    
    # Create system items in warehouse
    system_fertilizer = Item.objects.create(
        name="NPK Fertilizer",
        category="fertilizers",
        unit="KG",
        company=company
    )
    
    system_pesticide = Item.objects.create(
        name="Delta Insecticide",
        category="pesticides",
        unit="L",
        company=company
    )
    
    # Create Contractors
    contractor_a = Contractor.objects.create(
        name="Contractor A",
        rate_per_hour=Decimal("20.00"),
        company=company,
        is_active=True
    )
    contractor_b = Contractor.objects.create(
        name="Contractor B",
        rate_per_hour=Decimal("15.50"),
        company=company,
        is_active=True
    )
    
    # Create HR Workers
    worker_1 = Worker.objects.create(
        name="Worker Company 1",
        worker_type="COMPANY",
        company=company,
        monthly_salary=Decimal("6000.00"), # 6000 / 30 / 8 = 25.00/hour
        standard_work_hours=8,
        status="active"
    )
    worker_2 = Worker.objects.create(
        name="Worker Company 2",
        worker_type="COMPANY",
        company=company,
        monthly_salary=Decimal("4800.00"), # 4800 / 30 / 8 = 20.00/hour
        standard_work_hours=8,
        status="active"
    )
    # Average rate should be (25 + 20) / 2 = 22.50
    
    return {
        "company": company,
        "user": user,
        "season": season,
        "farm": farm,
        "enclosure": enclosure,
        "system_fertilizer": system_fertilizer,
        "system_pesticide": system_pesticide,
        "contractor_a": contractor_a,
        "contractor_b": contractor_b,
        "worker_1": worker_1,
        "worker_2": worker_2,
    }

@pytest.mark.django_db
def test_location_allocation_cost_sync_on_irrigation(setup_data):
    # 1. Create IrrigationReport
    company = setup_data["company"]
    user = setup_data["user"]
    enclosure = setup_data["enclosure"]
    
    irrigation_report = IrrigationReport.objects.create(
        company=company,
        date=date(2026, 5, 25),
        engineer=user,
        is_fertilized=True,
        notes="Test irrigation report"
    )
    
    # Create detail
    detail = IrrigationDetail.objects.create(
        company=company,
        report=irrigation_report,
        phase=enclosure,
        shifts_count=2,
        hours_per_shift=Decimal("4.0")
    )
    
    # 2. Create allocation matrix
    allocation = OperationalLocationAllocation.objects.create(
        company=company,
        content_type=ContentType.objects.get_for_model(IrrigationReport),
        object_id=irrigation_report.id,
        enclosure=enclosure,
        allocated_workers_company=2,
        allocated_workers_contractor_a=3,
        allocated_workers_contractor_b=1,
        productivity_value=Decimal("85.5")
    )
    
    # 3. Verify OperationLog was created automatically
    op_log = OperationLog.objects.filter(
        company=company,
        location=enclosure,
        source_id=irrigation_report.id
    ).first()
    
    assert op_log is not None
    assert op_log.company_workers == 2
    assert op_log.contractor_workers == 4
    assert op_log.actual_productivity == 85.5
    
    # 4. Verify LaborEntry rows were created with calculated wages
    labor_entries = LaborEntry.objects.filter(operation_log=op_log)
    assert labor_entries.count() == 6 # 2 company + 3 contractor A + 1 contractor B
    
    company_entries = labor_entries.filter(worker_type=LaborEntry.WORKER_TYPE_COMPANY)
    assert company_entries.count() == 2
    for entry in company_entries:
        assert entry.worker_rate == Decimal("22.50") # average of 25.00 and 20.00
        assert entry.hours == Decimal("8.0")
        
    contractor_a_entries = labor_entries.filter(worker_type=LaborEntry.WORKER_TYPE_CONTRACTOR, contractor=setup_data["contractor_a"])
    assert contractor_a_entries.count() == 3
    for entry in contractor_a_entries:
        assert entry.worker_rate == Decimal("20.00")
        
    contractor_b_entries = labor_entries.filter(worker_type=LaborEntry.WORKER_TYPE_CONTRACTOR, contractor=setup_data["contractor_b"])
    assert contractor_b_entries.count() == 1
    for entry in contractor_b_entries:
        assert entry.worker_rate == Decimal("15.50")

@pytest.mark.django_db
def test_unregistered_material_alerts(setup_data):
    company = setup_data["company"]
    user = setup_data["user"]
    enclosure = setup_data["enclosure"]
    
    # Test 1: IrrigationReport with custom (unregistered) fertilizer name
    irrigation_report = IrrigationReport.objects.create(
        company=company,
        date=date(2026, 5, 25),
        engineer=user,
        is_fertilized=True
    )
    
    detail = IrrigationDetail.objects.create(
        company=company,
        report=irrigation_report,
        phase=enclosure,
        shifts_count=1,
        hours_per_shift=Decimal("3.0")
    )
    
    applied = AppliedFertilizer.objects.create(
        company=company,
        irrigation_detail=detail,
        custom_material_name="Magical Growth Juice",
        quantity=Decimal("12.50")
    )
    
    alert = MaterialVerificationAlert.objects.filter(company=company, suggested_name="Magical Growth Juice").first()
    assert alert is not None
    assert alert.source_report_type == 'irrigation'
    assert alert.source_report_id == irrigation_report.id
    assert alert.is_resolved is False
    
    # Test 2: PestControlReport with custom pesticide name
    pest_report = PestControlReport.objects.create(
        company=company,
        date=date(2026, 5, 25),
        engineer=user,
        custom_pesticide_name="Hyper Poison 9000",
        quantity=Decimal("5.0")
    )
    
    alert2 = MaterialVerificationAlert.objects.filter(company=company, suggested_name="Hyper Poison 9000").first()
    assert alert2 is not None
    assert alert2.source_report_type == 'pest_control'
    assert alert2.source_report_id == pest_report.id
    assert alert2.is_resolved is False


@pytest.mark.django_db
def test_irrigation_report_post_via_api(setup_data):
    user = setup_data["user"]
    enclosure = setup_data["enclosure"]
    system_fertilizer = setup_data["system_fertilizer"]
    
    client = APIClient()
    client.force_authenticate(user=user)
    
    payload = {
        "date": "2026-05-25",
        "engineer": user.id,
        "notes": "Testing irrigation API post",
        "is_fertilized": True,
        "total_shifts": 1,
        "total_hours": 3.0,
        "company_workers": 4,
        "contractor_workers": 3,
        "details": [
            {
                "phase": enclosure.id,
                "shifts_count": 1,
                "hours_per_shift": 3.0,
                "fertilizers": [
                    {
                        "fertilizer_item": system_fertilizer.id,
                        "custom_material_name": None,
                        "quantity": 10.5,
                        "unit": "كجم"
                    }
                ]
            }
        ]
    }
    
    url = reverse("reports_irrigation")
    response = client.post(url, payload, format="json")
    
    assert response.status_code == status.HTTP_201_CREATED, response.data
    report_id = response.data["id"]
    
    # Verify records exist and have company populated
    report = IrrigationReport.objects.get(id=report_id)
    assert report.company == setup_data["company"]
    assert report.company_workers == 4
    assert report.contractor_workers == 3
    
    detail = report.details.first()
    assert detail is not None
    assert detail.company == setup_data["company"]
    assert detail.phase == enclosure
    
    fert = detail.fertilizers.first()
    assert fert is not None
    assert fert.company == setup_data["company"]
    assert fert.fertilizer_item == system_fertilizer
    assert fert.quantity == Decimal("10.50")

    # Verify that the OperationalLocationAllocation was automatically created
    from django.contrib.contenttypes.models import ContentType
    from apps.reports.models import OperationalLocationAllocation, OperationLog
    
    content_type = ContentType.objects.get_for_model(report)
    alloc = OperationalLocationAllocation.objects.filter(
        content_type=content_type,
        object_id=report.id,
        enclosure=enclosure
    ).first()
    
    assert alloc is not None
    assert alloc.allocated_workers_company == 4
    assert alloc.allocated_workers_contractor_a == 3
    assert alloc.allocated_workers_contractor_b == 0

    # Verify that OperationLog was created with the correct worker counts
    op_log = OperationLog.objects.filter(
        company=setup_data["company"],
        location=enclosure,
        source_id=str(report.id)
    ).first()
    
    assert op_log is not None
    assert op_log.company_workers == 4
    assert op_log.contractor_workers == 3

    from serializers.reports_serializers import OperationLogTimelineSerializer
    serializer = OperationLogTimelineSerializer(op_log)
    assert serializer.data["is_shared_labor"] is False


@pytest.mark.django_db
def test_pending_worker_review_signals(setup_data):
    from apps.hr.models import Worker, PendingWorkerReview
    from apps.reports.models import LaborEntry, Contractor
    
    company = setup_data["company"]
    
    # 1. Create a registered COMPANY worker
    registered_worker = Worker.objects.create(
        company=company,
        name="أحمد حسن",
        worker_type="COMPANY"
    )
    
    # 2. Create a LaborEntry with the registered worker's name
    entry_registered = LaborEntry.objects.create(
        company=company,
        worker_name="أحمد حسن",
        worker_type=LaborEntry.WORKER_TYPE_COMPANY,
        hours=Decimal("8.0")
    )
    
    # Assert that NO PendingWorkerReview is created because the worker is registered
    assert not PendingWorkerReview.objects.filter(labor_entry=entry_registered).exists()
    
    # 3. Create a LaborEntry with an unregistered worker's name
    entry_unregistered = LaborEntry.objects.create(
        company=company,
        worker_name="عامل غير مسجل",
        worker_type=LaborEntry.WORKER_TYPE_COMPANY,
        hours=Decimal("8.0")
    )
    
    # Assert that a PendingWorkerReview IS created
    review = PendingWorkerReview.objects.filter(labor_entry=entry_unregistered).first()
    assert review is not None
    assert review.worker_name_fallback == "عامل غير مسجل"
    assert review.resolved is False
    assert review.company == company
    
    # 4. Create a LaborEntry with an auto-generated worker name (containing "تلقائي")
    entry_auto = LaborEntry.objects.create(
        company=company,
        worker_name="عامل شركة تلقائي 1",
        worker_type=LaborEntry.WORKER_TYPE_COMPANY,
        note="توزيع عمالة شركة تلقائي",
        hours=Decimal("8.0")
    )
    
    # Assert that NO PendingWorkerReview is created for auto-generated workers
    assert not PendingWorkerReview.objects.filter(labor_entry=entry_auto).exists()
    
    # 5. Update the unregistered LaborEntry to a registered worker's name
    entry_unregistered.worker_name = "أحمد حسن"
    entry_unregistered.save()
    
    # Assert that the PendingWorkerReview is automatically deleted/removed
    assert not PendingWorkerReview.objects.filter(labor_entry=entry_unregistered).exists()
    
    # 6. Change entry_registered's worker type to CONTRACTOR
    contractor = Contractor.objects.create(
        company=company,
        name="مقاول اختبار",
        rate_per_hour=Decimal("15.00")
    )
    
    entry_registered.worker_type = LaborEntry.WORKER_TYPE_CONTRACTOR
    entry_registered.contractor = contractor
    entry_registered.save()
    
    # Assert that NO PendingWorkerReview is created and any old review is deleted
    assert not PendingWorkerReview.objects.filter(labor_entry=entry_registered).exists()
    
    # 7. Test backfill function and serializer
    from api.endpoints.hr_views import _backfill_pending_reviews, PendingWorkerReviewSerializer
    
    # Create another unregistered labor entry, simulating a pre-existing record created before the signal was active
    entry_retro = LaborEntry.objects.create(
        company=company,
        worker_name="عامل قديم غير مسجل",
        worker_type=LaborEntry.WORKER_TYPE_COMPANY,
        hours=Decimal("8.0")
    )
    # Delete the review that was automatically created by the signal
    PendingWorkerReview.objects.filter(labor_entry=entry_retro).delete()
    assert not PendingWorkerReview.objects.filter(labor_entry=entry_retro).exists()
    
    # Run the backfill
    _backfill_pending_reviews(company)
    
    # Assert that the review was successfully recreated via backfill
    review_retro = PendingWorkerReview.objects.filter(labor_entry=entry_retro).first()
    assert review_retro is not None
    assert review_retro.worker_name_fallback == "عامل قديم غير مسجل"
    assert review_retro.resolved is False
    
    # Assert that the serializer runs without error and returns correct custom fields
    serializer = PendingWorkerReviewSerializer(review_retro)
    data = serializer.data
    assert data["labor_entry_worker_type"] == "COMPANY"
    assert data["worker_name_fallback"] == "عامل قديم غير مسجل"
