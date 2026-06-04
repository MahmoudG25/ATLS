# 📋 SYSTEM UPGRADE & STITCH LAYOUT SPECIFICATION
# Project: Atlas Farm ERP / Namaa Academy
# Platform: Django (PostgreSQL) + React (Tailwind CSS & shadcn/ui)
# Target IDE: Antigravity IDE via MCP
# Language/Direction: Arabic (RTL) / 100% Responsive (Mobile & Desktop)

---

## 🏗️ 1. ARCHITECTURAL OVERVIEW & DATABASE UPDATES (PostgreSQL)

To prevent breaking existing analytics data and historical single-location reports, we implement an explicit relational structure for multi-location operations, productivity breakdowns, and cross-module tracking for Irrigation and Pest Control.

### 📊 1.1 Model Enhancements (`apps/reports/models.py`)

#### A. Multi-Location & Custom Productivity Allocation
```python
import uuid
from django.db import models
from core.models import TenantModel  # Assuming multi-tenant base exists

class OperationalLocationAllocation(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Linked to parent task row or specialized report object
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = models.GenericForeignKey('contenttypes.ContentType', 'object_id')
    
    # Farm hierarchy linkage
    enclosure = models.ForeignKey('farm.Enclosure', on_delete=models.CASCADE, verbose_name="الحوشة")
    
    # Custom Allocated Resources (Option B)
    allocated_workers_company = models.IntegerField(default=0, verbose_name="عمال شركة")

    
    # Productivity Fields
    productivity_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="الإنتاجية للموقع")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات الموقع")

    class Meta:
        db_table = 'operational_location_allocations'
        verbose_name = 'توزيع العمليات على المواقع'
B. Specialized Irrigation and Pest Control Reports
Python
class IrrigationReport(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(verbose_name="التاريخ")
    engineer = models.ForeignKey('users.User', on_delete=models.PROTECT, verbose_name="المهندس المسؤول")
    notes = models.TextField(blank=True, null=True)
    attachments = models.JSONField(default=list, blank=True) # Cloudinary asset links
    is_fertilized = models.BooleanField(default=False, verbose_name="مع تسميد")
    
    # Totals aggregated via signals/properties
    total_shifts = models.IntegerField(default=0)
    total_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)

class IrrigationDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(IrrigationReport, on_delete=models.CASCADE, related_name='details')
    phase = models.ForeignKey('farm.Phase', on_delete=models.CASCADE, verbose_name="المرحلة")
    shifts_count = models.IntegerField(verbose_name="عدد التحويلات")
    hours_per_shift = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="عدد الساعات للتحويلة")

class AppliedFertilizer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    irrigation_detail = models.ForeignKey(IrrigationDetail, on_delete=models.CASCADE, related_name='fertilizers')
    fertilizer_material = models.ForeignKey('warehouse.Material', on_delete=models.SET_NULL, null=True, blank=True)
    custom_material_name = models.CharField(max_digits=255, blank=True, null=True, verbose_name="اسم السماد الخارجي")
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_digits=50, default="كجم")

class PestControlReport(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(verbose_name="التاريخ")
    engineer = models.ForeignKey('users.User', on_delete=models.PROTECT)
    pesticide_material = models.ForeignKey('warehouse.Material', on_delete=models.SET_NULL, null=True, blank=True)
    custom_pesticide_name = models.CharField(max_digits=255, blank=True, null=True, verbose_name="اسم المبيد الخارجي")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="الكمية المستخدمة")
    notes = models.TextField(blank=True, null=True)
    attachments = models.JSONField(default=list, blank=True)
🔔 1.2 Unregistered Material Alerts (apps/warehouse/models.py)
When an engineer writes a custom fertilizer or pesticide name, a warehouse verification request is stored.

Python
class MaterialVerificationAlert(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_report_type = models.CharField(max_length=50, choices=[('irrigation', 'ري'), ('pest_control', 'مكافحة')])
    source_report_id = models.UUIDField()
    requested_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    suggested_name = models.CharField(max_length=255, verbose_name="الاسم المكتوب ميدانياً")
    is_resolved = models.BooleanField(default=False)
    mapped_material = models.ForeignKey('warehouse.Material', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="المادة المربوطة بالمستودع")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'warehouse_material_alerts'
        ordering = ['-created_at']
🛠️ 2. DATA INJECTOR & SEED SCRIPTS FIX (seed_rich_data.py)
Ensure integrity constraints by populating base Tenant and core User instances before linking hierarchical entity rows.

Python
# Modified segment within seed scripts to ensure tenant/company configuration:
def seed_system_safely():
    # 1. Establish absolute Root Tenant
    tenant, _ = Company.objects.get_or_create(
        id="00000000-0000-0000-0000-000000000001",
        defaults={"name": "مزرعة أطلس النموذجية", "slug": "atlas-farm"}
    )
    
    # 2. Check and Map User Profiles safely
    # Inject standard options, hierarchy nodes, and master data mapped precisely with active PostgreSQL database UUID types.
🎨 3. STITCH UI/UX LAYOUT DESIGN SPECIFICATION (shadcn/ui + Tailwind CSS)
To render a seamless Arabic (RTL) layout with absolute responsive optimization for both Mobile viewports and Desktop workstations, use the following rules across all layouts.

🌐 3.1 Global Theme Configuration (src/index.css & src/theme/theme.js)
Ensure all layout roots implement strict RTL rendering utilities:

CSS
@layer base {
  body {
    @apply font-sans antialiased text-slate-900 bg-slate-50/50;
    direction: rtl;
    text-align: right;
  }
}
🔒 3.2 Role Partitioning & Interface Segregation
Super Admin Dashboard: Encapsulated into a unified single view pane (/admin-dashboard). Controls tenant switches, dynamic user permission grants, and macro audit tracking.

User Profile & Self Service: Consolidated user module located at /profile. Combines active engineer identification credentials, task submissions, and connected operational history.

💻 4. FRONT-END COMPONENTS CONVERSION & SPECIFICATIONS
🌾 4.1 Dynamic Location & Custom Resource Distributor Component
File destination: src/components/LocationAllocationMatrix.jsx

JavaScript
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function LocationAllocationMatrix({ enclosures, onChange }) {
  const [selectedLocations, setSelectedLocations] = useState([]);

  const toggleLocation = (loc) => {
    const exists = selectedLocations.find(item => item.id === loc.id);
    if (exists) {
      setSelectedLocations(selectedLocations.filter(item => item.id !== loc.id));
    } else {
      setSelectedLocations([...selectedLocations, {
        id: loc.id, name: loc.name, phase: loc.phase,
        workers_company: 0, workers_contractor_a: 0, workers_contractor_b: 0,
        productivity: 0
      }]);
    }
  };

  const updateAllocation = (id, field, value) => {
    const updated = selectedLocations.map(loc => {
      if (loc.id === id) {
        const newLoc = { ...loc, [field]: parseFloat(value) || 0 };
        return newLoc;
      }
      return loc;
    });
    setSelectedLocations(updated);
  };

  // Compute absolute dynamic productivity accumulation
  const totalProductivity = selectedLocations.reduce((sum, loc) => sum + loc.productivity, 0);

  useEffect(() => {
    onChange(selectedLocations, totalProductivity);
  }, [selectedLocations]);

  return (
    <Card className="w-full border-slate-200/80 shadow-sm">
      <CardHeader className="bg-slate-50/50 border-b border-slate-100">
        <CardTitle className="text-base font-semibold text-slate-800 flex justify-between items-center">
          <span>توزيع الموارد والإنتاجية على الأحواش</span>
          <span className="text-xs bg-emerald-50 text-emerald-700 px-2.5 py-1 rounded-full border border-emerald-100 font-bold">
            إجمالي الإنتاجية: {totalProductivity}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4 space-y-4">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {enclosures.map(enc => (
            <div key={enc.id} className="flex items-center space-x-reverse space-x-2 border p-2 rounded-md hover:bg-slate-50">
              <Checkbox id={enc.id} onCheckedChange={() => toggleLocation(enc)} />
              <Label htmlFor={enc.id} className="text-xs cursor-pointer">{enc.name} (مرحلة {enc.phase})</Label>
            </div>
          ))}
        </div>

        {selectedLocations.length > 0 && (
          <div className="overflow-x-auto border rounded-lg">
            <table className="w-full text-sm text-right text-slate-500">
              <thead className="text-xs text-slate-700 bg-slate-100/70 border-b">
                <tr>
                  <th className="p-2">الموقع</th>
                  <th className="p-2">عمال شركة</th>

                  <th className="p-2">الإنتاجية للموقع</th>
                </tr>
              </thead>
              <tbody>
                {selectedLocations.map(loc => (
                  <tr key={loc.id} className="border-b hover:bg-slate-50/80">
                    <td className="p-2 font-medium text-slate-900 text-xs">{loc.name}</td>
                    <td className="p-2"><Input type="number" className="w-16 h-8 text-xs" onChange={(e) => updateAllocation(loc.id, 'workers_company', e.target.value)} /></td>
                    <td className="p-2"><Input type="number" className="w-16 h-8 text-xs" onChange={(e) => updateAllocation(loc.id, 'workers_contractor_a', e.target.value)} /></td>
                    <td className="p-2"><Input type="number" className="w-16 h-8 text-xs" onChange={(e) => updateAllocation(loc.id, 'workers_contractor_b', e.target.value)} /></td>
                    <td className="p-2"><Input type="number" className="w-24 h-8 text-xs border-emerald-200 focus-visible:ring-emerald-400" placeholder="0.0" onChange={(e) => updateAllocation(loc.id, 'productivity', e.target.value)} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
💧 4.2 Tabbed Irrigation and Pest Control System (src/pages/reports/ReportsIndex.jsx)
Upgrade the reports home screen into structured dashboard tabs featuring responsive sub-forms.

JavaScript
import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import DailyTaskForm from "./DailyTaskReport/DailyTaskForm";
import IrrigationForm from "./IrrigationReport/IrrigationForm";
import PestControlForm from "./PestControlReport/PestControlForm";

export default function ReportsIndex() {
  return (
    <div className="container mx-auto p-4 max-w-5xl space-y-4" dir="rtl">
      <div className="flex flex-col space-y-1">
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">منظومة التقارير والعمليات الميدانية</h1>
        <p className="text-sm text-slate-500">سجل وتابع تقارير المهام اليومية والري والمكافحة للمزرعة.</p>
      </div>

      <Tabs defaultValue="daily-tasks" className="w-full">
        <TabsList className="grid w-full grid-cols-3 h-11 bg-slate-100 p-1 rounded-xl">
          <TabsTrigger value="daily-tasks" className="rounded-lg text-xs sm:text-sm font-medium transition-all">المهام الميدانية اليومية</TabsTrigger>
          <TabsTrigger value="irrigation" className="rounded-lg text-xs sm:text-sm font-medium transition-all">تقارير شبكة الري والتسميد</TabsTrigger>
          <TabsTrigger value="pest-control" className="rounded-lg text-xs sm:text-sm font-medium transition-all">تقارير وقاية النبات والمكافحة</TabsTrigger>
        </TabsList>
        
        <TabsContent value="daily-tasks" className="mt-4"><DailyTaskForm /></TabsContent>
        <TabsContent value="irrigation" className="mt-4"><IrrigationForm /></TabsContent>
        <TabsContent value="pest-control" className="mt-4"><PestControlForm /></TabsContent>
      </Tabs>
    </div>
  );
}
🧪 4.3 Material Selector Input with Custom Alternative Fallback
File destination: src/components/MaterialSelector.jsx

JavaScript
import React, { useState } from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function MaterialSelector({ materials, label, onMaterialChange }) {
  const [showCustomInput, setShowCustomInput] = useState(false);

  const handleSelectChange = (value) => {
    if (value === "custom_alternative") {
      setShowCustomInput(true);
      onMaterialChange({ material_id: null, is_custom: true, name: "" });
    } else {
      setShowCustomInput(false);
      const selected = materials.find(m => m.id === value);
      onMaterialChange({ material_id: value, is_custom: false, name: selected?.name });
    }
  };

  return (
    <div className="space-y-2 text-right">
      <Label className="text-xs font-semibold text-slate-700">{label}</Label>
      <Select onValueChange={handleSelectChange}>
        <SelectTrigger className="w-full h-10 border-slate-200">
          <SelectValue placeholder="اختر المادة من القائمة..." />
        </SelectTrigger>
        <SelectContent>
          {materials.map(mat => (
            <SelectItem key={mat.id} value={mat.id} className="text-right">{mat.name}</SelectItem>
          ))}
          <SelectItem value="custom_alternative" className="text-amber-600 font-medium text-right">⚠️ مادة أخرى (غير مسجلة بالمخزن)...</SelectItem>
        </SelectContent>
      </Select>

      {showCustomInput && (
        <div className="mt-2 space-y-1 animate-in fade-in slide-in-from-top-1 duration-200">
          <Input 
            type="text" 
            placeholder="اكتب اسم السماد أو المبيد الجديد بدقة..." 
            className="border-amber-300 focus-visible:ring-amber-400 text-xs"
            onChange={(e) => onMaterialChange({ material_id: null, is_custom: true, name: e.target.value })}
          />
          <p className="text-[10px] text-amber-600 font-medium">سيتم إرسال إشعار فوري لمدير المخازن لربط هذه المادة وتأكيدها.</p>
        </div>
      )}
    </div>
  );
}
🔔 4.4 Warehouse Notification Alert Feed Drawer (src/pages/warehouse/MaterialAlertFeed.jsx)
Where the Warehouse Manager can view field inputs, confirm registrations, and link custom inputs to system items.

JavaScript
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { BellRing, Check } from "lucide-react";

export default function MaterialAlertFeed() {
  const [alerts, setAlerts] = useState([]);
  const [warehouseMaterials, setWarehouseMaterials] = useState([]); // System catalog

  const resolveAlert = (alertId, mappedId) => {
    // Send payload to API -> /api/warehouse/alerts/<id>/resolve/ with mapped_material
    setAlerts(alerts.filter(a => a.id !== alertId));
  };

  return (
    <Card className="w-full max-w-3xl mx-auto border-slate-200">
      <CardHeader className="border-b border-slate-100 bg-slate-50/50 p-4">
        <div className="flex items-center space-x-reverse space-x-3">
          <div className="bg-amber-100 text-amber-700 p-2 rounded-lg"><BellRing className="h-5 w-5" /></div>
          <div>
            <CardTitle className="text-base font-bold text-slate-900">إشارات وتنبيهات المواد الميدانية</CardTitle>
            <CardDescription className="text-xs">المواد المدخلة بواسطة المهندسين وتحتاج لربط بمواد المخزن الرسمية.</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-4 space-y-3">
        {alerts.length === 0 ? (
          <div className="text-center py-8 text-sm text-slate-400">لا توجد طلبات ربط معلقة حالياً.</div>
        ) : (
          alerts.map(alert => (
            <div key={alert.id} className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-3 border rounded-xl bg-amber-50/30 border-amber-100 gap-3">
              <div className="space-y-1">
                <div className="flex items-center space-x-reverse space-x-2">
                  <span className="font-bold text-slate-900 text-sm">{alert.suggested_name}</span>
                  <Badge variant="outline" className="text-[10px] bg-white">{alert.source_report_type === 'irrigation' ? 'تقرير ري' : 'تقرير مكافحة'}</Badge>
                </div>
                <p className="text-xs text-slate-500">بواسطة: {alert.engineer_name} | التاريخ: {alert.date}</p>
              </div>
              <div className="flex items-center space-x-reverse space-x-2">
                <Select onValueChange={(val) => resolveAlert(alert.id, val)}>
                  <SelectTrigger className="w-48 h-9 bg-white text-xs border-slate-200">
                    <SelectValue placeholder="ربط مع مادة معتمدة..." />
                  </SelectTrigger>
                  <SelectContent>
                    {warehouseMaterials.map(m => (
                      <SelectItem key={m.id} value={m.id} className="text-right text-xs">{m.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
🚀 5. FINAL DEPLOYMENT CHECKLIST & PERMISSIONS VERIFICATION
Before updating deployment servers, verify role access settings across front-end local states and back-end authorization layers.

Verify Token Validity: Check role access parameters on private routes inside /src/routes/ProtectedRoute.jsx to prevent client-side bypassing.

Back-end Validation Rules: Audit request intercepts inside permissions/role_permissions.py to confirm that non-administrative user tokens cannot make POST requests to /api/tenants/ endpoints.

Database Migrations: Apply database schema transformations to the production server by executing standard database command wrappers sequentially:

Bash
python manage.py makemigrations reports warehouse
python manage.py migrate