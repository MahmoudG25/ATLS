import os
import django
from datetime import date, datetime, timedelta
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.users.models import User, Company
from apps.farm.models import Farm, LocationNode, EnclosureProfile
from apps.reports.models import (
    Operation, Season, Variety, Unit, Contractor,
    DailyTaskReport, OperationLog, LaborEntry
)
from apps.equipment.models import Equipment, Maintenance, Usage
from apps.warehouse.models import Warehouse, Item, Movement
from apps.accounting.models import Expense, Revenue, Salary

def seed_everything():
    print("Starting rich agricultural data seeding...")

    # 1. Company and Users
    company = Company.objects.first()
    if not company:
        company = Company.objects.create(name="شركة أطلس الزراعية", subscription_plan="enterprise")
        print(f"Created company: {company.name}")
    else:
        print(f"Using company: {company.name}")

    # Ensure admin user exists and is assigned to the company
    admin_user = User.objects.filter(role="SUPER_ADMIN").first()
    if not admin_user:
        admin_user, created = User.objects.get_or_create(
            email="admin@example.com",
            defaults={
                "name": "أدمن النظام",
                "company": company,
                "is_approved": True,
                "is_active": True,
                "role": "SUPER_ADMIN",
            }
        )
        if created:
            admin_user.set_password("admin")
            admin_user.save()
            print("Created admin user admin@example.com / admin")
    else:
        admin_user.company = company
        admin_user.save()
        print(f"Using admin user: {admin_user.email}")

    # Create an agricultural engineer user
    engineer_user, created = User.objects.get_or_create(
        email="engineer@example.com",
        defaults={
            "name": "المهندس أحمد محمود",
            "company": company,
            "is_approved": True,
            "is_active": True,
            "role": "ENGINEER",
        }
    )
    if created:
        engineer_user.set_password("engineer")
        engineer_user.save()
        print("Created engineer user engineer@example.com / engineer")

    # 2. Seasons
    current_year = datetime.now().year
    season, created = Season.objects.get_or_create(
        name=str(current_year),
        company=company,
        defaults={
            "start_date": date(current_year, 1, 1),
            "end_date": date(current_year, 12, 31),
            "status": "OPEN",
        }
    )
    print(f"Season: {season.name} [OK]")

    # 3. Units & Varieties
    UNITS_DATA = ["كجم", "طن", "صندوق", "لتر", "متر مكعب"]
    for u_name in UNITS_DATA:
        Unit.objects.get_or_create(name=u_name, company=company)
    unit_kg = Unit.objects.get(name="كجم", company=company)
    unit_box = Unit.objects.get(name="صندوق", company=company)
    unit_ton = Unit.objects.get(name="طن", company=company)
    unit_liter = Unit.objects.get(name="لتر", company=company)

    VARIETIES_DATA = ["مجدول", "صقعي", "خلاص", "كلاماتا", "شملالي"]
    for v_name in VARIETIES_DATA:
        Variety.objects.get_or_create(name=v_name, company=company)
    var_medjool = Variety.objects.get(name="مجدول", company=company)
    var_olive = Variety.objects.get(name="كلاماتا", company=company)

    # 4. Contractors
    contractor_elite, _ = Contractor.objects.get_or_create(
        name="مجموعة النخبة للمقاولات الزراعية",
        company=company,
        defaults={"rate_per_hour": 15.00}
    )
    contractor_aljazeera, _ = Contractor.objects.get_or_create(
        name="شركة الجزيرة للخدمات الميدانية",
        company=company,
        defaults={"rate_per_hour": 12.50}
    )

    # 5. Farm Structure
    farm, _ = Farm.objects.get_or_create(
        name="مزرعة الواحة الكبرى",
        company=company,
        defaults={"is_active": True}
    )

    # Create Location Nodes (Sectors and Enclosures)
    sector_palm, _ = LocationNode.objects.get_or_create(
        farm=farm,
        name="قطاع النخيل الشرقي",
        type=LocationNode.TYPE_SECTOR,
        company=company,
        defaults={"is_active": True, "order": 1}
    )

    sector_olive, _ = LocationNode.objects.get_or_create(
        farm=farm,
        name="قطاع الزيتون الغربي",
        type=LocationNode.TYPE_SECTOR,
        company=company,
        defaults={"is_active": True, "order": 2}
    )

    # Enclosures for Palm
    enc_p1, _ = LocationNode.objects.get_or_create(
        farm=farm,
        name="حوش النخيل 1 (مجدول)",
        type=LocationNode.TYPE_ENCLOSURE,
        parent=sector_palm,
        company=company,
        defaults={"is_active": True, "order": 1}
    )
    EnclosureProfile.objects.get_or_create(
        location_node=enc_p1,
        company=company,
        defaults={
            "crop_type": "palm",
            "planting_year": 2018,
            "tree_count": 450,
            "expected_yield": 45.00,
            "profile_data": {"spacing": "8x8", "irrigation_type": "bubbler"}
        }
    )

    enc_p2, _ = LocationNode.objects.get_or_create(
        farm=farm,
        name="حوش النخيل 2 (خلاص)",
        type=LocationNode.TYPE_ENCLOSURE,
        parent=sector_palm,
        company=company,
        defaults={"is_active": True, "order": 2}
    )
    EnclosureProfile.objects.get_or_create(
        location_node=enc_p2,
        company=company,
        defaults={
            "crop_type": "palm",
            "planting_year": 2019,
            "tree_count": 600,
            "expected_yield": 55.00,
            "profile_data": {"spacing": "8x8", "irrigation_type": "bubbler"}
        }
    )

    # Enclosures for Olive
    enc_o1, _ = LocationNode.objects.get_or_create(
        farm=farm,
        name="حوش الزيتون 1 (كلاماتا)",
        type=LocationNode.TYPE_ENCLOSURE,
        parent=sector_olive,
        company=company,
        defaults={"is_active": True, "order": 1}
    )
    EnclosureProfile.objects.get_or_create(
        location_node=enc_o1,
        company=company,
        defaults={
            "crop_type": "olive",
            "planting_year": 2015,
            "tree_count": 800,
            "expected_yield": 24.00,
            "profile_data": {"spacing": "6x6", "irrigation_type": "drip"}
        }
    )

    print("Farm Structure, Sectors & Enclosures Created! [OK]")

    # 6. Operations (Technicals)
    op_pollination, _ = Operation.objects.get_or_create(
        name="تلقيح نخيل يدوي",
        company=company,
        defaults={"category": "pollination", "profile_type": "generic"}
    )
    op_fertilization, _ = Operation.objects.get_or_create(
        name="تسميد عضوي وكيميائي",
        company=company,
        defaults={"category": "fertilization", "profile_type": "generic"}
    )
    op_irrigation, _ = Operation.objects.get_or_create(
        name="تشغيل وصيانة الري بالتنقيط",
        company=company,
        defaults={"category": "maintenance", "profile_type": "generic"}
    )
    op_harvest, _ = Operation.objects.get_or_create(
        name="حصاد وتعبئة المحصول",
        company=company,
        defaults={"category": "transport", "profile_type": "generic"}
    )
    op_protection, _ = Operation.objects.get_or_create(
        name="رش وقائي ضد سوسة النخيل",
        company=company,
        defaults={"category": "protection", "profile_type": "generic"}
    )
    op_pruning, _ = Operation.objects.get_or_create(
        name="تقليم وتكريب موسمي",
        company=company,
        defaults={"category": "maintenance", "profile_type": "generic"}
    )

    print("Operations Created! [OK]")

    # 7. Equipment Fleet
    eq_list = [
        "جرار زراعي جون دير 5075E",
        "جرار زراعي ماسي فيرغسون 385",
        "مرشة مبيدات هيدروليكية ذاتية الحركة",
        "شاحنة نقل مبردة إيسوزو",
        "آلة حصاد الزيتون الميكانيكية",
    ]
    equipments = []
    for eq_name in eq_list:
        eq, _ = Equipment.objects.get_or_create(name=eq_name)
        equipments.append(eq)

    # Seed usage & maintenance for equipment
    today = date.today()
    for i, eq in enumerate(equipments):
        # usages
        for d in range(1, 10):
            Usage.objects.get_or_create(
                equipment=eq,
                date=today - timedelta(days=d),
                defaults={
                    "hours_used": random.randint(3, 8),
                    "fuel_consumption": random.randint(15, 45)
                }
            )
        # maintenance
        Maintenance.objects.get_or_create(
            equipment=eq,
            date=today - timedelta(days=random.randint(15, 30)),
            defaults={
                "notes": "صيانة دورية، تغيير فلاتر وزيت المحرك والتأكد من ضغط السيور والفرامل."
            }
        )
    print("Equipment Fleet, Usages & Maintenance Seeded! [OK]")

    # 8. Warehouse and Stock
    warehouse, _ = Warehouse.objects.get_or_create(
        name="المستودع المركزي الشمالي",
        company=company,
        defaults={"location": "القطاع الإداري للمزرعة", "is_active": True}
    )

    items_data = [
        ("سماد NPK مركّب ذواب", "fertilizers", 3500.00, "كجم"),
        ("مبيد فطري كوبروكسيد النحاس", "pesticides", 450.00, "لتر"),
        ("صناديق حصاد بلاستيكية سعة 20 كجم", "tools", 1200.00, "صندوق"),
        ("شبكات خراطيم ري بالتنقيط 16 ملم", "tools", 80.00, "لفة"),
    ]
    for name, cat, qty, unit_str in items_data:
        item, _ = Item.objects.get_or_create(
            name=name,
            company=company,
            defaults={
                "category": cat,
                "quantity": qty,
                "warehouse": warehouse,
                "unit": unit_str,
                "updated_by": admin_user,
                "is_active": True
            }
        )
        # Create Inward Movement
        Movement.objects.get_or_create(
            item=item,
            movement_type="IN",
            company=company,
            defaults={
                "quantity": qty,
                "user": admin_user,
                "responsible_user": admin_user,
                "note": "رصيد افتتاحي للمخزن وجرد موسمي تم اعتماده."
            }
        )
    print("Warehouses, Items and Movements Seeded! [OK]")

    # 9. Accounting & Finances
    Expense.objects.all().delete()
    Revenue.objects.all().delete()
    Salary.objects.all().delete()

    # Expenses
    expenses_list = [
        ("أسمدة كيميائية ومخصبات للتربة", 7500.00, today - timedelta(days=12), "أسمدة"),
        ("شراء مبيدات لمكافحة الحشرات والآفات", 3200.00, today - timedelta(days=10), "مبيدات"),
        ("قطع غيار وزيوت للجرار الزراعي والآلات", 1850.00, today - timedelta(days=8), "صيانة"),
        ("ديزل وقود للأسطول الميداني والمضخات", 2600.00, today - timedelta(days=5), "وقود"),
        ("تكاليف عمال مقاولة لحصاد الزيتون", 12000.00, today - timedelta(days=3), "عمالة مقاولة"),
    ]
    for notes, amt, dt, cat in expenses_list:
        Expense.objects.create(
            company=company,
            date=dt,
            amount=amt,
            category=cat,
            notes=notes
        )

    # Revenues
    revenues_list = [
        (55000.00, today - timedelta(days=15), "مبيعات تمور"),
        (38000.00, today - timedelta(days=6), "مبيعات زيتون"),
        (15000.00, today - timedelta(days=2), "مبيعات فسائل"),
    ]
    for amt, dt, src in revenues_list:
        Revenue.objects.create(
            company=company,
            date=dt,
            amount=amt,
            source=src
        )

    # Salaries
    Salary.objects.create(
        company=company,
        employee=engineer_user,
        date=today - timedelta(days=1),
        amount=4800.00
    )
    print("Financial Expenses, Revenues and Salaries Seeded! [OK]")

    # 10. Daily Task Reports and Operation Logs
    # Clean old ones to avoid duplicates
    DailyTaskReport.objects.filter(company=company).delete()
    OperationLog.objects.filter(company=company).delete()

    reports_data = [
        # Report 1
        {
            "date": today - timedelta(days=4),
            "op": op_fertilization,
            "loc": enc_p1,
            "company_workers": 6,
            "contractor_workers": 10,
            "contractor": contractor_elite,
            "var": var_medjool,
            "unit": unit_kg,
            "hours": 8.0,
            "prod": 350.0,
            "notes": "تم تسميد كامل الحوش الأول بسماد NPK الذواب بنسب متساوية وفق الخطة التشغيلية.",
            "status": "approved",
            "rate": 150.0, # Rate for labor entries
        },
        # Report 2
        {
            "date": today - timedelta(days=3),
            "op": op_irrigation,
            "loc": enc_o1,
            "company_workers": 4,
            "contractor_workers": 0,
            "contractor": None,
            "var": var_olive,
            "unit": unit_liter,
            "hours": 6.5,
            "prod": 1800.0,
            "notes": "متابعة دورة الري بالتنقيط في حوش الزيتون 1، وتنظيف فلاتر خطوط المياه الرئيسية والفرعية.",
            "status": "approved",
            "rate": 0.0,
        },
        # Report 3
        {
            "date": today - timedelta(days=2),
            "op": op_protection,
            "loc": enc_p2,
            "company_workers": 5,
            "contractor_workers": 8,
            "contractor": contractor_aljazeera,
            "var": var_medjool,
            "unit": unit_liter,
            "hours": 7.0,
            "prod": 250.0,
            "notes": "رش وقائي بالمرشات لقطاع النخيل لمنع ظهور سوسة النخيل الحمراء. الوضع ممتاز تحت السيطرة.",
            "status": "approved",
            "rate": 12.0,
        },
        # Report 4
        {
            "date": today - timedelta(days=1),
            "op": op_harvest,
            "loc": enc_p1,
            "company_workers": 8,
            "contractor_workers": 15,
            "contractor": contractor_elite,
            "var": var_medjool,
            "unit": unit_box,
            "hours": 9.0,
            "prod": 450.0,
            "notes": "حصاد قطوف التمور المكتملة النضج، وتعبئتها في صناديق بلاستيكية تمهيداً لنقلها لمخازن المزرعة.",
            "status": "submitted",
            "rate": 16.0,
        }
    ]

    for idx, r in enumerate(reports_data):
        rep = DailyTaskReport.objects.create(
            company=company,
            engineer=engineer_user,
            report_date=r["date"],
            location=r["loc"],
            variety=r["var"],
            company_workers=r["company_workers"],
            contractor_workers=r["contractor_workers"],
            contractor=r["contractor"],
            operation=r["op"],
            unit=r["unit"],
            actual_productivity=r["prod"],
            work_hours=r["hours"],
            notes=r["notes"],
            status=r["status"]
        )

        # Create corresponding OperationLog (analytics source of truth)
        op_log = OperationLog.objects.create(
            company=company,
            location=r["loc"],
            operation=r["op"],
            season=season,
            source_type=OperationLog.SOURCE_DAILY_TASK,
            source_id=None,
            report=rep,
            variety=r["var"],
            unit=r["unit"],
            contractor=r["contractor"],
            company_workers=r["company_workers"],
            contractor_workers=r["contractor_workers"],
            actual_productivity=r["prod"],
            work_hours=r["hours"],
            profile_type=r["op"].profile_type,
            status="COMPLETED"
        )

        # Create Labor Entries for cost aggregation
        if r["company_workers"] > 0:
            for cw in range(r["company_workers"]):
                LaborEntry.objects.create(
                    company=company,
                    report=rep,
                    operation_log=op_log,
                    worker_name=f"عامل شركة أ-{cw+1}",
                    worker_type=LaborEntry.WORKER_TYPE_COMPANY,
                    worker_rate=12.00,
                    hours=r["hours"],
                    note="دوام كامل للشركة"
                )

        if r["contractor_workers"] > 0 and r["contractor"]:
            for cw in range(r["contractor_workers"]):
                LaborEntry.objects.create(
                    company=company,
                    report=rep,
                    operation_log=op_log,
                    worker_name=f"عامل مقاولة ب-{cw+1}",
                    worker_type=LaborEntry.WORKER_TYPE_CONTRACTOR,
                    contractor=r["contractor"],
                    worker_rate=r["rate"],
                    hours=r["hours"],
                    note="حصاد/مقاولة ميدانية"
                )

    print("Reports, Operational Logs, and Labor Entries Seeded successfully! [OK]")
    print("\n✅ Rich agricultural data seeding complete!")

if __name__ == "__main__":
    seed_everything()
