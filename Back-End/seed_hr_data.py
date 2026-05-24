import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.users.models import Company
from apps.reports.models import Contractor
from apps.hr.models import Worker, PayrollPeriod

def seed():
    company = Company.objects.first()
    if not company:
        print("No company found to seed.")
        return

    print(f"Seeding for company: {company.name}")

    # 1. Create default Active Payroll Period if not exists
    from apps.hr.signals import get_or_create_active_period
    period = get_or_create_active_period(company)
    print(f"Active Payroll Period: {period.name} ({period.start_date} -> {period.end_date})")

    # 2. Create direct company workers
    company_workers = [
        {"name": "أحمد محمود علي", "monthly_salary": 6000, "badge_number": "C-0101", "national_id": "29101011234567"},
        {"name": "محمد حسن إبراهيم", "monthly_salary": 7500, "badge_number": "C-0102", "national_id": "29302021234568"},
        {"name": "مصطفى عبد العزيز", "monthly_salary": 5000, "badge_number": "C-0103", "national_id": "29503031234569"},
    ]

    for wk_data in company_workers:
        worker, created = Worker.objects.get_or_create(
            company=company,
            badge_number=wk_data["badge_number"],
            defaults={
                "name": wk_data["name"],
                "worker_type": "COMPANY",
                "monthly_salary": wk_data["monthly_salary"],
                "national_id": wk_data["national_id"],
                "standard_work_hours": 8,
                "status": "active"
            }
        )
        if created:
            print(f"Created company worker id: {worker.id}")
        else:
            print(f"Company worker already exists id: {worker.id}")

    # 3. Create contractor workers linked to first contractor if exists
    contractor = Contractor.objects.first()
    if contractor:
        print(f"Linking contractor workers to contractor id: {contractor.id}")
        contractor_workers = [
            {"name": "كمال عبد الرحمن", "badge_number": "K-0201", "national_id": "29205051234511"},
            {"name": "جمال عبد الله", "badge_number": "K-0202", "national_id": "29406061234522"},
        ]
        for wk_data in contractor_workers:
            worker, created = Worker.objects.get_or_create(
                company=company,
                badge_number=wk_data["badge_number"],
                defaults={
                    "name": wk_data["name"],
                    "worker_type": "CONTRACTOR",
                    "contractor": contractor,
                    "national_id": wk_data["national_id"],
                    "status": "active"
                }
            )
            if created:
                print(f"Created contractor worker id: {worker.id}")
            else:
                print(f"Contractor worker already exists id: {worker.id}")

    # 4. Create official employees for existing system users
    from apps.users.models import User
    from apps.hr.models import Employee

    users_to_employee = User.objects.filter(company=company)
    for u in users_to_employee:
        if u.role in ["SUPER_ADMIN", "HR", "OWNER", "ENGINEER"]:
            position_mapping = {
                "SUPER_ADMIN": "مدير عام العمليات",
                "HR": "أخصائي موارد بشرية (HR)",
                "OWNER": "مدير قطاع",
                "ENGINEER": "مهندس زراعي"
            }
            dept_mapping = {
                "SUPER_ADMIN": "الإدارة العليا",
                "HR": "الموارد البشرية (HR)",
                "OWNER": "إدارة العمليات والمزارع",
                "ENGINEER": "الإدارة الهندسية"
            }
            emp, created = Employee.objects.get_or_create(
                company=company,
                user=u,
                defaults={
                    "hire_date": "2026-01-01",
                    "department": dept_mapping.get(u.role, "الإدارة الهندسية"),
                    "position": position_mapping.get(u.role, "مهندس زراعي"),
                    "monthly_salary": 9500 if u.role == "ENGINEER" else 15000,
                    "standard_work_hours": 8,
                    "status": "active",
                    "notes": "تم إنشاؤه تلقائياً كمهندس/موظف بالنظام"
                }
            )
            if created:
                print(f"Created official employee profile for user: {u.email}")
            else:
                print(f"Official employee profile already exists for user: {u.email}")

if __name__ == "__main__":
    seed()
