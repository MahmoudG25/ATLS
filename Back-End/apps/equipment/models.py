from django.db import models
from django.conf import settings
from core.tenant import TenantAwareModel
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date


class Equipment(TenantAwareModel):
    EQUIPMENT_TYPES = [
        ('tractor', 'جرار / حارث زراعي'),
        ('car', 'سيارة نقل / بيك أب'),
        ('motorcycle', 'موتوسيكل ميداني'),
        ('generator', 'مولد كهربائي / مضخة ري'),
        ('sprayer', 'ماكينة رش / مكافحة'),
    ]
    
    METER_TYPES = [
        ('hours', 'ساعات عمل (Hours)'),
        ('km', 'مسافة مقطوعة (KM)'),
        ('days', 'أيام تقويمية (Days)'),
    ]

    name = models.CharField(max_length=255, verbose_name="اسم المعدة / الآلية")
    plate_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="رقم اللوحة / شاسيه")
    equipment_type = models.CharField(max_length=50, choices=EQUIPMENT_TYPES, default='tractor', verbose_name="نوع المعدة")
    meter_type = models.CharField(max_length=20, choices=METER_TYPES, default='hours', verbose_name="وحدة قياس العداد")
    
    # Live Meter Counters
    current_meter = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, verbose_name="قراءة العداد الحالية")
    last_maintenance_meter = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, verbose_name="قراءة العداد عند آخر صيانة")
    last_maintenance_date = models.DateField(null=True, blank=True, verbose_name="تاريخ آخر صيانة")
    
    # Custom Maintenance Threshold
    maintenance_interval = models.DecimalField(max_digits=10, decimal_places=2, default=50.0, verbose_name="فترة الصيانة الدورية المسموحة")
    
    image = models.CharField(max_length=500, null=True, blank=True, verbose_name="رابط صورة المعدة")
    is_active = models.BooleanField(default=True, verbose_name="نشط بالخدمة")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات المواصفات")

    # ── Compatibility fields to keep other modules / old codes from breaking ──
    type = models.CharField(max_length=100, blank=True, default="")
    model = models.CharField(max_length=100, blank=True, default="")
    serial_number = models.CharField(max_length=100, blank=True, default="")
    purchase_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, default="active")
    specifications = models.TextField(blank=True, default="")
    
    current_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    oil_change_interval_hours = models.DecimalField(max_digits=8, decimal_places=2, default=250.0)
    oil_change_interval_days = models.IntegerField(default=180)
    last_oil_change_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    last_oil_change_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'fleet_equipment'
        verbose_name = 'المعدات والآليات'

    @property
    def meter_delta(self):
        if self.meter_type == 'days':
            start_date = self.last_maintenance_date or self.purchase_date or (self.created_at.date() if self.created_at else date.today())
            return models.DecimalField().to_python((date.today() - start_date).days)
        return self.current_meter - self.last_maintenance_meter

    @property
    def requires_maintenance(self):
        return self.meter_delta >= self.maintenance_interval

    @property
    def last_operation_date(self):
        last_log = self.logs.order_by('-date', '-created_at').first()
        return last_log.date if last_log else None

    @property
    def equipment_type_display(self):
        return dict(self.EQUIPMENT_TYPES).get(self.equipment_type, self.equipment_type)

    def __str__(self):
        return f"{self.name} ({self.equipment_type_display})"

    def save(self, *args, **kwargs):
        # Enforce compatibility mapping
        if self.equipment_type and not self.type:
            self.type = self.equipment_type.upper()
        elif self.type and not self.equipment_type:
            t_lower = self.type.lower()
            if t_lower in dict(self.EQUIPMENT_TYPES):
                self.equipment_type = t_lower
            elif t_lower == 'truck':
                self.equipment_type = 'car'
            elif t_lower == 'harvester':
                self.equipment_type = 'tractor'
            elif t_lower == 'irrigation_pump':
                self.equipment_type = 'generator'
            else:
                self.equipment_type = 'tractor'

        if self.plate_number and not self.serial_number:
            self.serial_number = self.plate_number
        elif self.serial_number and not self.plate_number:
            self.plate_number = self.serial_number

        # Sync counters
        if self.meter_type == 'days':
            # Auto-calculate elapsed days since starting point (e.g. purchase date or creation date)
            start = self.purchase_date or (self.created_at.date() if self.created_at else date.today())
            self.current_meter = (date.today() - start).days
            self.current_hours = self.current_meter
        else:
            if self.current_meter != 0.0 and self.current_hours == 0.0:
                self.current_hours = self.current_meter
            elif self.current_hours != 0.0 and self.current_meter == 0.0:
                self.current_meter = self.current_hours

        super().save(*args, **kwargs)


class Maintenance(TenantAwareModel):
    equipment = models.ForeignKey(
        Equipment, on_delete=models.CASCADE, related_name="maintenances"
    )
    date = models.DateField()
    maintenance_type = models.CharField(max_length=100, default="scheduled")
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    notes = models.TextField(blank=True, default="")

    def __str__(self):
        return f"Maintenance: {self.equipment.name} on {self.date}"


class Usage(TenantAwareModel):
    equipment = models.ForeignKey(
        Equipment, on_delete=models.CASCADE, related_name="usages"
    )
    date = models.DateField()
    hours_used = models.DecimalField(max_digits=8, decimal_places=2)
    fuel_consumption = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    operator = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return f"Usage: {self.equipment.name} on {self.date}"


class OilChangeLog(TenantAwareModel):
    equipment = models.ForeignKey(
        Equipment, on_delete=models.CASCADE, related_name="oil_changes"
    )
    date = models.DateField()
    hours_at_change = models.DecimalField(max_digits=10, decimal_places=2)
    oil_type = models.CharField(max_length=100, blank=True, default="")
    filter_changed = models.BooleanField(default=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    notes = models.TextField(blank=True, default="")

    def __str__(self):
        return f"Oil Change: {self.equipment.name} on {self.date} at {self.hours_at_change} hrs"


class EquipmentLog(TenantAwareModel):
    LOG_TYPES = [
        ('maintenance', 'إصلاح وصيانة عامة'),
        ('oil_change', 'تغيير زيت وفلاتر'),
        ('fueling', 'تزويد وقود ومحروقات'),
    ]

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='logs', verbose_name="المعدة")
    log_type = models.CharField(max_length=30, choices=LOG_TYPES, verbose_name="نوع الحركة")
    date = models.DateField(verbose_name="التاريخ")
    
    meter_reading = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="قراءة العداد أثناء العملية")
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="التكلفة المباشرة (توثيق)")
    amount_liters = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="كمية اللترات (وقود / زيت)")
    details = models.TextField(verbose_name="تفاصيل الحركة والبيانات المدخلة")
    
    assigned_operator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='equipment_operations',
        verbose_name="السائق / المستخدم المسؤول"
    )

    class Meta:
        db_table = 'fleet_equipment_logs'
        ordering = ['-date', '-created_at']

    @property
    def log_type_display(self):
        return dict(self.LOG_TYPES).get(self.log_type, self.log_type)

    @property
    def operator_name(self):
        return self.assigned_operator.name if self.assigned_operator else ""


class FleetMaintenanceAlert(TenantAwareModel):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenance_alerts')
    alert_message = models.CharField(max_length=500)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        db_table = 'fleet_maintenance_alerts'
        ordering = ['-created_at']


@receiver(post_save, sender=Equipment)
def check_equipment_thresholds(sender, instance, **kwargs):
    if instance.requires_maintenance:
        unit_label = "ساعة عمل" if instance.meter_type == 'hours' else "كم"
        msg = f"المعدة ({instance.name}) تخطت {instance.meter_delta} {unit_label} منذ آخر صيانة وتتطلب إجراء صيانة أو فحص فوري."
        
        # Avoid duplication of active pending alerts
        FleetMaintenanceAlert.objects.get_or_create(
            equipment=instance,
            is_resolved=False,
            defaults={'alert_message': msg, 'company': instance.company}
        )

