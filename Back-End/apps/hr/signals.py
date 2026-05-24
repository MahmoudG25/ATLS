import datetime
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.reports.models import LaborEntry
from apps.hr.models import PayrollPeriod, ContractorLedger


def get_or_create_active_period(company):
    """
    جلب فترة الرواتب المفتوحة حالياً أو إنشاء واحدة افتراضية للشهر الحالي
    """
    today = datetime.date.today()
    start_of_month = today.replace(day=1)
    if today.month == 12:
        end_of_month = today.replace(year=today.year + 1, month=1, day=1) - datetime.timedelta(days=1)
    else:
        end_of_month = today.replace(month=today.month + 1, day=1) - datetime.timedelta(days=1)

    period_name = start_of_month.strftime("%B %Y")
    period = PayrollPeriod.objects.filter(company=company, is_closed=False).first()
    if not period:
        period = PayrollPeriod.objects.create(
            company=company,
            name=period_name,
            start_date=start_of_month,
            end_date=end_of_month,
            is_closed=False,
        )
    return period


@receiver(post_save, sender=LaborEntry)
def handle_labor_entry_post_save(sender, instance, created, **kwargs):
    """
    الإشارة المسؤولة عن معالجة بند العمل بعد الحفظ.

    IMPORTANT: The following LaborEntry fields were REMOVED in migration 0006:
      - worker (ForeignKey to Worker)
      - deduction_hours (DecimalField)
      - deduction_amount (DecimalField)

    This signal now only handles contractor ledger entries for CONTRACTOR-type
    labor entries. Company payroll auto-transactions are disabled until the
    worker FK is re-introduced.
    """
    if getattr(instance, "_saving_via_signal", False):
        return

    company = instance.company
    if not company:
        return

    # ── عمال المقاولين (CONTRACTOR) ─────────────────────────────────────────
    if instance.worker_type == LaborEntry.WORKER_TYPE_CONTRACTOR and instance.contractor:
        contractor = instance.contractor
        rate = Decimal(
            f"{float(instance.worker_rate) if instance.worker_rate and instance.worker_rate > 0 else float(contractor.rate_per_hour):.2f}"
        )

        hours = float(instance.hours or 0)
        ot_hours = float(instance.overtime or 0)
        earning_amount = Decimal(f"{hours * float(rate):.2f}")
        ot_amount = Decimal(f"{ot_hours * float(rate):.2f}")

        # تحديث معدل الأجر إذا كان صفراً
        if not instance.worker_rate or instance.worker_rate == 0:
            instance._saving_via_signal = True
            instance.worker_rate = rate
            instance.save(update_fields=["worker_rate"])
            del instance._saving_via_signal

        # جلب تاريخ التقرير
        report_date = None
        if instance.report_id:
            try:
                report_date = instance.report.report_date
            except Exception:
                pass
        elif instance.harvest_report_id:
            try:
                report_date = instance.harvest_report.harvest_date
            except Exception:
                pass
        if not report_date:
            report_date = datetime.date.today()

        # مستحقات ساعات العمل العادية للمقاول
        if hours > 0:
            ContractorLedger.objects.update_or_create(
                company=company,
                labor_entry=instance,
                transaction_type="EARNING",
                defaults={
                    "contractor": contractor,
                    "date": report_date,
                    "hours": hours,
                    "rate": rate,
                    "amount": earning_amount,
                    "notes": f"مستحقات عمل عادية - تقرير {report_date}. بند: {instance.worker_name}",
                },
            )
        else:
            ContractorLedger.objects.filter(
                labor_entry=instance, transaction_type="EARNING"
            ).delete()

        # إضافي عمال المقاول
        if ot_hours > 0:
            ContractorLedger.objects.update_or_create(
                company=company,
                labor_entry=instance,
                transaction_type="OVERTIME",
                defaults={
                    "contractor": contractor,
                    "date": report_date,
                    "hours": ot_hours,
                    "rate": rate,
                    "amount": ot_amount,
                    "notes": f"إضافي ساعات لعمال المقاول - تقرير {report_date}. بند: {instance.worker_name}",
                },
            )
        else:
            ContractorLedger.objects.filter(
                labor_entry=instance, transaction_type="OVERTIME"
            ).delete()
