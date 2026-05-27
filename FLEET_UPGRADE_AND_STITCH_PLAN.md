# 📋 FLEET & EQUIPMENT SYSTEM UPGRADE SPECIFICATION
# Project: Atlas Farm ERP - Fleet Management
# Platform: Django (PostgreSQL) + React (Tailwind CSS & shadcn/ui)
# Target IDE: Antigravity IDE via MCP
# Language/Direction: Arabic (RTL) / 100% Responsive (Mobile & Desktop)

---

## 🏗️ 1. ARCHITECTURAL OVERVIEW & DATABASE UPDATES (PostgreSQL)

We will refactor the existing equipment structures to natively support dual meter tracking (Hours vs. Kilometers), dynamic custom logs for maintenance/fuel/oil changes with optional operator tracking, automated alert tracking thresholds, and real-time verification handlers.

### 📊 1.1 Model Refactoring & Additions (`apps/equipment/models.py`)

#### A. Fleet Registry & Dual Meter Tracking
```python
import uuid
from django.db import models
from django.conf import settings
from core.models import TenantAwareModel

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
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name="اسم المعدة / الآلية")
    plate_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="رقم اللوحة / شاسيه")
    equipment_type = models.CharField(max_length=50, choices=EQUIPMENT_TYPES, verbose_name="نوع المعدة")
    meter_type = models.CharField(max_length=20, choices=METER_TYPES, default='hours', verbose_name="وحدة قياس العداد")
    
    # Live Meter Counters (Manual Update Mechanism - Option A)
    current_meter = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, verbose_name="قراءة العداد الحالية")
    last_maintenance_meter = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, verbose_name="قراءة العداد عند آخر صيانة")
    
    # Custom Maintenance Threshold (e.g., 50 Hours for tractor, 5000 KM for car)
    maintenance_interval = models.DecimalField(max_digits=10, decimal_places=2, default=50.0, verbose_name="فترة الصيانة الدورية المسموحة")
    
    is_active = models.BooleanField(default=True, verbose_name="نشط بالخدمة")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات المواصفات")

    class Meta:
        db_table = 'fleet_equipment'
        verbose_name = 'المعدات والآليات'

    @property
    def meter_delta(self):
        return self.current_meter - self.last_maintenance_meter

    @property
    def requires_maintenance(self):
        return self.meter_delta >= self.maintenance_interval
B. Fleet Activity Ledger (Maintenance, Fuel, and Oil Logs)
Python
class EquipmentLog(TenantAwareModel):
    LOG_TYPES = [
        ('maintenance', 'إصلاح وصيانة عامة'),
        ('oil_change', 'تغيير زيت وفلاتر'),
        ('fueling', 'تزويد وقود ومحروقات'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='logs', verbose_name="المعدة")
    log_type = models.CharField(max_length=30, choices=LOG_TYPES, verbose_name="نوع الحركة")
    date = models.DateField(verbose_name="التاريخ")
    
    # Captured context fields
    meter_reading = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="قراءة العداد أثناء العملية")
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="التكلفة المباشرة (توثيق)")
    details = models.TextField(verbose_name="تفاصيل الحركة والبيانات المدخلة")
    
    # Optional Assigned Operator / Driver Reference
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
🔔 1.2 Automated Core Signals & Centralized Alert System
We trigger an internal alert row if the current manual meter update breaches the delta limit threshold.

Python
from django.db.models.signals import post_save
from django.dispatch import receiver

class FleetMaintenanceAlert(TenantAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenance_alerts')
    alert_message = models.CharField(max_length=500)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fleet_maintenance_alerts'
        ordering = ['-created_at']

@receiver(post_save, sender=Equipment)
def check_equipment_thresholds(sender, instance, **kwargs):
    if instance.requires_maintenance:
        unit_label = "ساعة عمل" if instance.meter_type == 'hours' else "كم"
        msg = f"المعدة ({instance.name}) تخطت {instance.meter_delta} {unit_label} منذ آخر صيانة وتطلب إجراء تغيير زيت أو فحص فوري."
        
        # Avoid duplication of active pending alerts
        FleetMaintenanceAlert.objects.get_or_create(
            equipment=instance,
            is_resolved=False,
            defaults={'alert_message': msg, 'company_id': instance.company_id}
        )
🎨 2. STITCH LAYOUTS & USER CONSOLE SEGREGATION (RTL Style Sheet)
To provide an intuitive administrative console while enabling dual integration (Fleet-wide banner view + System Global Dashboard Alerts Feed), we partition UI rendering as follows:

Fleet Hub Banner Panel: Mounted directly inside the primary view container of FleetManager.jsx.

System Notification Broadcast Router: Hooked into central routing logic to intercept active dashboard nodes.

Equipment Profile View: Custom view container layout featuring tabbed historical record tracking cards.

💻 3. FRONT-END COMPONENTS SPECIFICATION (shadcn/ui + Tailwind CSS)
🔔 3.1 Integrated Alerts Board Feed Component
File destination: src/components/fleet/FleetAlertsFeed.jsx

JavaScript
import React from 'react';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Wrench, ShieldAlert } from "lucide-react";

export default function FleetAlertsFeed({ alerts, onResolve }) {
  if (!alerts || alerts.length === 0) return null;

  return (
    <div className="space-y-2 mb-4 animate-in fade-in slide-in-from-top-3 duration-300" dir="rtl">
      <div className="flex items-center space-x-reverse space-x-2 text-amber-800 font-bold text-sm mb-1 px-1">
        <ShieldAlert className="h-4 w-4 text-amber-600" />
        <span>تنبيهات الصيانة الوقائية العاجلة والأسطول</span>
      </div>
      {alerts.map(alert => (
        <Alert key={alert.id} variant="destructive" className="bg-amber-50/90 border-amber-200 text-amber-900 flex justify-between items-center p-3.5 rounded-xl shadow-sm">
          <div className="flex items-start space-x-reverse space-x-3">
            <div className="bg-amber-100 text-amber-700 p-1.5 rounded-lg mt-0.5"><Wrench className="h-4 w-4" /></div>
            <div>
              <AlertTitle className="text-xs font-bold text-amber-950">تجاوز حد التشغيل المسموح</AlertTitle>
              <AlertDescription className="text-[11px] text-amber-800 mt-0.5 font-medium">{alert.alert_message}</AlertDescription>
            </div>
          </div>
          <Button size="sm" className="bg-amber-600 hover:bg-amber-700 text-white text-xs font-medium h-8 rounded-lg" onClick={() => onResolve(alert.id)}>
            تأكيد إجراء الصيانة 🛠️
          </Button>
        </Alert>
      ))}
    </div>
  );
}
🏎️ 3.2 Main Fleet Operations Manager View Dashboard
File destination: src/pages/equipment/FleetManager.jsx

JavaScript
import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import FleetAlertsFeed from "@/components/fleet/FleetAlertsFeed";
import FleetRegistryTable from "./components/FleetRegistryTable";
import LogTransactionForm from "./components/LogTransactionForm";
import EquipmentProfileView from "./components/EquipmentProfileView";

export default function FleetManager() {
  const [activeTab, setActiveTab] = useState("registry");
  const [selectedEquipmentId, setSelectedEquipmentId] = useState(null);
  const [alerts, setAlerts] = useState([]); // Filled via API: /api/equipment/alerts/

  const viewEquipmentProfile = (id) => {
    setSelectedEquipmentId(id);
    setActiveTab("profile");
  };

  return (
    <div className="container mx-auto p-4 max-w-6xl space-y-4 text-right" dir="rtl">
      <div className="flex flex-col space-y-1">
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">منظومة الحركة، الأسطول والمعدات الآلية</h1>
        <p className="text-sm text-slate-500">إدارة الجرارات، المركبات والمولدات وتتبع عدادات الساعات والمسافات وجداول الصيانة الدورية.</p>
      </div>

      {/* Synchronized Twin Notification Display Area */}
      <FleetAlertsFeed alerts={alerts} onResolve={(id) => setAlerts(alerts.filter(a => a.id !== id))} />

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3 max-w-md h-10 bg-slate-100 p-1 rounded-xl mb-4">
          <TabsTrigger value="registry" className="rounded-lg text-xs font-semibold">سجل ومراقبة الأسطول</TabsTrigger>
          <TabsTrigger value="add-log" className="rounded-lg text-xs font-semibold">تسجيل حركة (وقود / صيانة)</TabsTrigger>
          <TabsTrigger value="profile" className="rounded-lg text-xs font-semibold" disabled={!selectedEquipmentId}>الملف التاريخي للمعدة</TabsTrigger>
        </TabsList>

        <TabsContent value="registry">
          <FleetRegistryTable onSelectProfile={viewEquipmentProfile} />
        </TabsContent>

        <TabsContent value="add-log">
          <LogTransactionForm onSuccess={() => setActiveTab("registry")} />
        </TabsContent>

        <TabsContent value="profile">
          {selectedEquipmentId && <EquipmentProfileView equipmentId={selectedEquipmentId} />}
        </TabsContent>
      </Tabs>
    </div>
  );
}
📊 3.3 Transaction Log Submissions Form View Component
File destination: src/pages/equipment/components/LogTransactionForm.jsx

JavaScript
import React, { useState } from 'react';
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export default function LogTransactionForm({ onSuccess }) {
  const [formData, setFormData] = useState({ equipment_id: '', log_type: 'maintenance', date: '', meter_reading: '', cost: '', assigned_operator: '', details: '' });
  const [fleetList] = useState([]); // System populated dropdown arrays
  const [usersList] = useState([]);  // Active Engineers/Drivers listing

  const handleSubmit = (e) => {
    e.preventDefault();
    // API pipeline ingestion placeholder -> POST /api/equipment/logs/
    onSuccess();
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white border rounded-xl p-5 shadow-sm space-y-4 max-w-xl mx-auto">
      <h3 className="text-sm font-bold text-slate-800 border-b pb-2">نموذج قيد عمليات المستند والبيانات الحركية</h3>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1">
          <Label className="text-xs">اختر الآلية / المعدة</Label>
          <Select onValueChange={(val) => setFormData({...formData, equipment_id: val})}>
            <SelectTrigger className="h-9 text-xs"><SelectValue placeholder="المعدة المعنية..." /></SelectTrigger>
            <SelectContent>{fleetList.map(f => <SelectItem key={f.id} value={f.id}>{f.name}</SelectItem>)}</SelectContent>
          </Select>
        </div>
        <div className="space-y-1">
          <Label className="text-xs">نوع المعاملة</Label>
          <Select defaultValue="maintenance" onValueChange={(val) => setFormData({...formData, log_type: val})}>
            <SelectTrigger className="h-9 text-xs"><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="maintenance">🛠️ إصلاح وصيانة عامة</SelectItem>
              <SelectItem value="oil_change">🛢️ تغيير زيت وفلاتر</SelectItem>
              <SelectItem value="fueling">⛽ تزويد وقود ومحروقات</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="space-y-1">
          <Label className="text-xs">التاريخ</Label>
          <Input type="date" className="h-9 text-xs" onChange={e => setFormData({...formData, date: e.target.value})} required />
        </div>
        <div className="space-y-1">
          <Label className="text-xs">قراءة العداد الحالية</Label>
          <Input type="number" step="0.01" placeholder="0.0" className="h-9 text-xs" onChange={e => setFormData({...formData, meter_reading: e.target.value})} required />
        </div>
        <div className="space-y-1">
          <Label className="text-xs">التكلفة المباشرة (جنية)</Label>
          <Input type="number" step="0.1" placeholder="0.0" className="h-9 text-xs" onChange={e => setFormData({...formData, cost: e.target.value})} />
        </div>
      </div>

      <div className="space-y-1">
        <Label className="text-xs">السائق / المستخدم المسؤول (اختياري)</Label>
        <Select onValueChange={(val) => setFormData({...formData, assigned_operator: val})}>
          <SelectTrigger className="h-9 text-xs"><SelectValue placeholder="تحديد الشخص المستلم للمعدة حالياً..." /></SelectTrigger>
          <SelectContent>{usersList.map(u => <SelectItem key={u.id} value={u.id}>{u.name} ({u.role})</SelectItem>)}</SelectContent>
        </Select>
      </div>

      <div className="space-y-1">
        <Label className="text-xs">شرح العمل والبيانات التوثيقية</Label>
        <Textarea className="text-xs border-slate-200" placeholder="اكتب تفاصيل الصيانة، نوع الزيت المستخدم، أو فواتير المحروقات هنا..." rows={3} onChange={e => setFormData({...formData, details: e.target.value})} required />
      </div>

      <Button type="submit" className="w-full bg-emerald-600 hover:bg-emerald-700 text-white text-xs h-9 font-bold rounded-lg shadow-sm">
        حفظ وتوثيق الحركة في سجل المعدة ✔️
      </Button>
    </form>
  );
}
📊 3.4 Comprehensive Single Equipment History Portfolio Drawer Page
File destination: src/pages/equipment/components/EquipmentProfileView.jsx

JavaScript
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Gauge, Calendar, User, DollarSign, Activity } from "lucide-react";

export default function EquipmentProfileView({ equipmentId }) {
  const [profile, setProfile] = useState(null); // Fetch -> /api/equipment/profile/<id>/
  const [historyLogs, setHistoryLogs] = useState([]);

  if (!profile) return <div className="text-center py-6 text-xs text-slate-400">جاري تحميل الملف التاريخي للآلية...</div>;

  return (
    <div className="space-y-4 border rounded-xl p-4 bg-slate-50/40">
      {/* Upper Specs Ribbon Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b pb-3 bg-white p-4 rounded-xl shadow-sm border-slate-100 gap-2">
        <div>
          <div className="flex items-center space-x-reverse space-x-2">
            <h2 className="text-lg font-bold text-slate-900">{profile.name}</h2>
            <Badge variant={profile.is_active ? "default" : "secondary"}>{profile.is_active ? 'نشطة بالخدمة' : 'خارج الخدمة'}</Badge>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">رقم اللوحة/المعرف: {profile.plate_number || 'غير متوفر'} | الفئة: {profile.equipment_type_display}</p>
        </div>
        <div className="flex items-center space-x-reverse space-x-4 bg-slate-50 p-2.5 rounded-lg border">
          <div className="text-center px-1">
            <span className="block text-[10px] text-slate-400 font-medium">العداد الحالي</span>
            <span className="font-bold text-sm text-slate-800 flex items-center justify-center gap-1 mt-0.5">
              <Gauge className="h-3.5 w-3.5 text-slate-500" /> {profile.current_meter}
            </span>
          </div>
          <div className="border-r h-6 my-auto"></div>
          <div className="text-center px-1">
            <span className="block text-[10px] text-slate-400 font-medium">الاستهلاك منذ آخر صيانة</span>
            <span className={`font-bold text-sm flex items-center justify-center gap-1 mt-0.5 ${profile.requires_maintenance ? 'text-amber-600' : 'text-emerald-600'}`}>
              {profile.meter_delta} / {profile.maintenance_interval}
            </span>
          </div>
        </div>
      </div>

      {/* Main Historical Activity Journal Grid Feed */}
      <Card className="border-slate-200 shadow-sm bg-white">
        <CardHeader className="p-4 border-b border-slate-100 bg-slate-50/50">
          <CardTitle className="text-xs font-bold text-slate-800 flex items-center gap-2">
            <Activity className="h-4 w-4 text-emerald-600" /> السجل الشامل للآلية (الصيانة والوقود والمحروقات)
          </CardTitle>
        </CardHeader>
        <CardContent className="p-4 space-y-3">
          {historyLogs.length === 0 ? (
            <div className="text-center py-8 text-xs text-slate-400">لا توجد حركات أو فواتير مسجلة تاريخياً لهذه المعدة.</div>
          ) : (
            historyLogs.map(log => (
              <div key={log.id} className="border p-3 rounded-xl flex flex-col sm:flex-row sm:items-start justify-between bg-white hover:bg-slate-50/50 gap-2 transition-colors">
                <div className="space-y-1 max-w-xl">
                  <div className="flex items-center space-x-reverse space-x-2">
                    <Badge variant={log.log_type === 'maintenance' ? 'destructive' : log.log_type === 'oil_change' ? 'warning' : 'success'} className="text-[10px] px-2 py-0.5 font-bold">
                      {log.log_type_display}
                    </Badge>
                    <span className="text-xs font-bold text-slate-800">{log.details}</span>
                  </div>
                  <div className="flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-slate-500 font-medium pt-1">
                    <span className="flex items-center gap-1"><Calendar className="h-3 w-3" /> {log.date}</span>
                    <span className="flex items-center gap-1"><Gauge className="h-3 w-3" /> قراءة العداد: {log.meter_reading}</span>
                    {log.operator_name && <span className="flex items-center gap-1"><User className="h-3 w-3" /> السائق: {log.operator_name}</span>}
                  </div>
                </div>
                <div className="bg-slate-100/60 font-bold text-xs text-slate-700 px-3 py-1.5 rounded-lg flex items-center shrink-0 self-center sm:self-start">
                  <DollarSign className="h-3.5 w-3.5 text-slate-500" /> {log.cost} جنية
                </div>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
🚀 4. REST FRAMEWORK VIEWS & SERIALIZATION INTERRUPTS
Ensure role filtering models conform strictly with DRF generic structures before linking active URL router pathways.

Python
# Associated API route maps inside Back-End generic layouts:
# Path mapping destinations within api/urls.py:
# - /api/equipment/ (GET list / POST registry)
# - /api/equipment/logs/ (POST dynamic maintenance/oil/fuel activity entries)
# - /api/equipment/alerts/ (GET pending maintenance alert rows)
# - /api/equipment/profile/<uuid:pk>/ (GET comprehensive spec & history payloads)