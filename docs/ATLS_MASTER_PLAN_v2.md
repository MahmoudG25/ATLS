# 🌿 ATLS — خطة التطوير الشاملة النهائية (SaaS-Ready Master Plan v2)

> **Stack:** Django 6 + DRF | React 19 + Vite | MUI v9 + Tailwind v4 | i18next (AR/EN)
> **نوع المنتج:** Multi-Tenant Farm Management SaaS — قابل للبيع لأي مزرعة
> **Core Entity Chain:** `Company → Farm → LocationNode → Report → LaborEntry / Attachment`

---

## 🎯 الهدف النهائي

نظام يمكن تخصيصه لأي مزرعة (نخيل، زيتون، فواكه، خضروات) بدون تعديل كود — فقط من Admin Dashboard.

---

# ☁️ CLOUDINARY — إعداد المطلوب منك

## ما تفعله أنت (مرة واحدة فقط):

### الخطوة 1 — إنشاء حساب
- اذهب إلى: https://cloudinary.com
- سجّل حساب مجاني (Free plan يكفي للتطوير)

### الخطوة 2 — من الـ Dashboard احضر:
```
Cloud Name:    dcpg2t2nb
API Key:       991725825931581
API Secret:    WXebNJ7q3yjHBRuUc3JcZOZiK0A
```

### الخطوة 3 — أضفها في `.env` (Backend):
```env
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### الخطوة 4 — إنشاء Folders في Cloudinary Dashboard:
```
atls/
├── employees/avatars/      ← صور الموظفين
├── employees/attachments/  ← ملفات الموظفين (PDF + صور)
└── reports/attachments/    ← مرفقات التقارير
```

### الخطوة 5 — إعداد Upload Preset (مهم للـ Frontend direct upload):
- من Dashboard → Settings → Upload → Add Upload Preset
- اسمه: `atls_unsigned`
- Mode: **Unsigned** (للرفع المباشر من Frontend)
- Folder: `atls/`
- Allowed Formats: `jpg,jpeg,png,webp,pdf`

### الكود اللي هيتضاف في المشروع (ستراه في الملفات):
```python
# Backend/config/settings.py — يُضاف تلقائياً:
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': env('CLOUDINARY_API_KEY'),
    'API_SECRET': env('CLOUDINARY_API_SECRET'),
}
```

---

# 📋 فهرس الـ Modules الكاملة

| # | Module | الحالة الحالية | الأولوية |
|---|--------|---------------|-----------|
| 1 | FarmStructure UI | ⚠️ موجود — يحتاج تحسين | 🔴 أولاً |
| 2 | Daily Report — LaborEntry Panel | ⚠️ موجود — يحتاج ميزة | 🔴 ثانياً |
| 3 | HR Module (Backend + Frontend) | ❌ Backend فاضي | 🔴 ثالثاً |
| 4 | Admin Dashboard (شامل) | ⚠️ بسيط جداً | 🔴 رابعاً |
| 5 | Warehouse — إدارة المخازن | ⚠️ موجود — يحتاج تحسين | 🟡 خامساً |
| 6 | Accounting — المحاسبة | ⚠️ موجود — يحتاج تحسين | 🟡 سادساً |
| 7 | Fleet — الأسطول والمعدات | ⚠️ موجود — يحتاج تحسين | 🟡 سابعاً |
| 8 | Palm Records — حقول النخيل | ⚠️ موجود — يحتاج توحيد | 🟢 ثامناً |
| 9 | Olive Records — حقول الزيتون | ⚠️ موجود — يحتاج توحيد | 🟢 تاسعاً |
| 10 | Production — المحصول | ⚠️ موجود — يحتاج ربط | 🟢 عاشراً |

---

## 🧱 مبادئ ثابتة لا تُخرق أبداً

```
1. كل موديل له company = FK(Company)           [TenantAwareModel]
2. LocationNode هو المصدر الوحيد للمواقع
3. كل شيء قابل للتخصيص من Admin Dashboard
4. لا hardcoded labels — كل شيء من DB
5. كل feature محكومة بـ role permissions
6. الكود نظيف: Logic في services/ — لا في Views
7. كل queryset يمر على company scoping
```

---

## 🗺️ Role Permissions Map (الجدول الكامل)

| Feature | SUPER_ADMIN | OWNER | MANAGER | ENGINEER | HR | ACCOUNTANT | WAREHOUSE |
|---------|------------|-------|---------|----------|----|------------|-----------|
| Admin Dashboard | ✅ كامل | ✅ كامل | ✅ جزئي | ❌ | ❌ | ❌ | ❌ |
| Farm Structure | ✅ | ✅ | ✅ | 👁️ قراءة | ❌ | ❌ | ❌ |
| Daily Reports | ✅ | ✅ | ✅ | ✅ إنشاء | ❌ | 👁️ | ❌ |
| HR Module | ✅ | ✅ | ✅ جزئي | 👁️ ملفه فقط | ✅ كامل | ❌ | ❌ |
| Warehouse | ✅ | ✅ | ✅ | ❌ | ❌ | 👁️ | ✅ كامل |
| Accounting | ✅ | ✅ | 👁️ | ❌ | ❌ | ✅ كامل | ❌ |
| Fleet/Equipment | ✅ | ✅ | ✅ | 👁️ | ❌ | ❌ | ❌ |
| Palm/Olive Records | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Production | ✅ | ✅ | ✅ | ✅ | ❌ | 👁️ | ❌ |
| Custom Fields Admin | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |

---

# 🏗️ SIDEBAR STRUCTURE (Navigation)

```
SIDEBAR
├── 📊 Dashboard                (الكل)
├── 🌳 هيكل المزرعة             (SUPER_ADMIN, OWNER, MANAGER, ENGINEER[read])
├── 📋 التقارير                  (SUPER_ADMIN, OWNER, MANAGER, ENGINEER)
│   ├── التقرير اليومي
│   ├── تقرير الري
│   └── تقرير التسميد
├── 👥 الموارد البشرية (HR)      (SUPER_ADMIN, OWNER, MANAGER, HR)
│   ├── الموظفين
│   └── الإجازات والحضور
├── 🏭 المخازن                   (SUPER_ADMIN, OWNER, MANAGER, WAREHOUSE)
├── 💰 المحاسبة                  (SUPER_ADMIN, OWNER, ACCOUNTANT)
├── 🚜 الأسطول والمعدات          (SUPER_ADMIN, OWNER, MANAGER)
├── 🌴 حقول النخيل               (SUPER_ADMIN, OWNER, MANAGER, ENGINEER)
├── 🫒 حقول الزيتون              (SUPER_ADMIN, OWNER, MANAGER, ENGINEER)
├── 📦 المحصول                   (SUPER_ADMIN, OWNER, MANAGER, ENGINEER)
└── ⚙️ لوحة الإدارة              (SUPER_ADMIN, OWNER, MANAGER[جزئي])
```

---

# 🔴 PHASE 1 — FarmStructure UI (أولاً)

## المشكلة الحالية:
الشجرة ثابتة الحجم — لو في 50 عنصر يتداخلوا ويكون المظهر سيئاً.

## الحل — Adaptive Tree:

### خوارزمية الحجم:
```javascript
const getNodeConfig = (totalSiblings) => {
  if (totalSiblings <= 3)  return { size: 'lg', iconSize: 24, textSize: '14px', padding: '12px 16px' };
  if (totalSiblings <= 6)  return { size: 'md', iconSize: 20, textSize: '12px', padding: '8px 12px'  };
  if (totalSiblings <= 12) return { size: 'sm', iconSize: 16, textSize: '11px', padding: '6px 8px'   };
  return                          { size: 'xs', iconSize: 14, textSize: '10px', padding: '4px 6px'   };
};
```

### Layout Rules:
```
- الـ Sectors (level 1): عرض 100% — كل sector في row
- الـ Stages (level 2): flex-wrap داخل الـ sector — يتوزعوا أفقياً
- الـ Enclosures (level 3): grid بـ columns تتغير بناءً على العدد
  - 1-4  enclosures → 2 columns
  - 5-8  enclosures → 3 columns
  - 9+   enclosures → 4 columns
- Collapse/Expand على كل branch بزر سهم
- Horizontal scroll على الـ container لو الشجرة عريضة
```

### الملفات المتأثرة:
```
Front-End/src/pages/farm/
├── FarmStructure.jsx   ← إعادة كتابة الـ TreeItem component
├── FarmStructure.css   ← إضافة classes للـ sizes
└── hooks/
    └── useFarmTree.js  ← logic منفصلة (جديد)
```

### الميزات المضافة:
- ✅ Collapse/Expand per branch
- ✅ حجم متكيف مع العدد
- ✅ Horizontal scroll عند الحاجة
- ✅ Hover → أزرار العمليات
- ✅ Search/Filter بالاسم
- ✅ Count badge على كل node (عدد الأبناء)

---

# 🔴 PHASE 2 — Daily Report: LaborEntry Inline Panel (ثانياً)

## المطلوب:

### في `DailyTaskForm.jsx`:
بجانب `company_workers` و`contractor_workers` → أيقونة `✏️`

```
عمال الشركة: [عداد: 3] ✏️
عمال المقاول: [عداد: 2] ✏️
```

عند الضغط على ✏️ → Drawer من الأسفل:

```
┌─────────────────────────────────────┐
│  👷 تفاصيل العمال                    │
│                                      │
│  ┌──────────────────────────────┐   │
│  │ اسم العامل  │ ساعات │ إضافي │   │ ← جدول العمال المضافين
│  │ أحمد محمد  │   8   │   2   │ 🗑️│
│  │ محمد علي   │   8   │   0   │ 🗑️│
│  └──────────────────────────────┘   │
│                                      │
│  ─── إضافة عامل جديد ─────────────  │
│  الاسم: [___________________] 🔍    │  ← search في HR
│  نوع العامل: ○ شركة  ● مقاول        │
│  المقاول: [dropdown اختياري]         │
│  ساعات العمل: [8]                   │
│  ساعات إضافية: [0]                  │
│  الأجر/ساعة: [50]                   │
│  ملاحظات: [________________]        │
│                                      │
│  [إلغاء]          [➕ إضافة للقائمة] │
│                                      │
│            [💾 حفظ التفاصيل]         │
└─────────────────────────────────────┘
```

### منطق الـ Search:
```javascript
// عند كتابة الاسم → نبحث في HR employees
// نعرض اقتراحات إذا في نتائج
// عند الاختيار → يُملأ الأجر تلقائياً من salary الموظف
// إذا لم يُوجد → يُحفظ كـ worker_name فقط (بدون ربط)
```

### Backend — `LaborEntry` model (تعديل):
```python
# إضافة إلى الموديل الموجود:
employee = models.ForeignKey(
    'hr.Employee',
    null=True, blank=True,
    on_delete=models.SET_NULL,
    related_name='labor_entries',
    help_text="ربط بموظف HR إذا كان مسجلاً"
)
```

### منطق الحفظ في Backend:
```python
# في serializer أو service:
def resolve_employee(worker_name, company):
    """البحث عن موظف بالاسم في نفس الشركة"""
    try:
        return Employee.objects.get(
            user__name__iexact=worker_name,
            user__company=company
        )
    except Employee.DoesNotExist:
        return None
```

### الملفات المتأثرة:
```
Back-End/apps/reports/models.py         ← إضافة employee FK إلى LaborEntry
Back-End/serializers/reports_serializers.py ← تحديث LaborEntrySerializer
Front-End/src/pages/reports/DailyTaskReport/
├── DailyTaskForm.jsx                   ← إضافة زر + منطق الـ Drawer
└── LaborEntryDrawer.jsx                ← جديد (Drawer component)
```

---

# 🔴 PHASE 3 — HR Module (ثالثاً)

## 3.1 — Backend Models (تعديل `apps/hr/models.py`):

### إضافات على Employee:
```python
address                  = models.TextField(blank=True, default='')
national_id              = models.CharField(max_length=20, blank=True, default='')
phone                    = models.CharField(max_length=20, blank=True, default='')
emergency_contact_name   = models.CharField(max_length=100, blank=True, default='')
emergency_contact_phone  = models.CharField(max_length=20, blank=True, default='')
avatar_url               = models.URLField(max_length=500, blank=True, default='')
# الراتب موجود → نحتفظ به
# salary = models.DecimalField(...) موجود
```

### موديل جديد `EmployeeAttachment`:
```python
class EmployeeAttachment(models.Model):
    FILE_TYPE_CHOICES = [
        ('image', 'صورة'),
        ('pdf', 'PDF'),
        ('other', 'أخرى'),
    ]
    employee    = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attachments')
    name        = models.CharField(max_length=200)
    file_url    = models.URLField(max_length=1000)      # رابط Cloudinary
    file_type   = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
```

## 3.2 — Auto-create Employee عند تسجيل مهندس:

### في `services/user_service.py`:
```python
FIELD_ROLES = ['ENGINEER', 'MANAGER', 'HR', 'ACCOUNTANT', 'WAREHOUSE']

def create_user(validated_data):
    user = User.objects.create_user(**validated_data)
    
    if user.role in FIELD_ROLES:
        from apps.hr.models import Employee
        # تحقق أنه مش موجود (للأمان)
        Employee.objects.get_or_create(
            user=user,
            defaults={
                'hire_date': timezone.now().date(),
                'status': 'active',
            }
        )
    return user
```

## 3.3 — Backend Endpoints:

```
GET    /hr/employees/                  ← قائمة (فلتر: status, department, search)
POST   /hr/employees/                  ← إنشاء موظف يدوي (non-user employee)
GET    /hr/employees/<id>/             ← تفاصيل كاملة
PATCH  /hr/employees/<id>/             ← تعديل
DELETE /hr/employees/<id>/             ← soft delete (status=terminated)

GET    /hr/employees/<id>/attachments/ ← ملفات الموظف
POST   /hr/employees/<id>/attachments/ ← رفع ملف (file_url + file_type + name)
DELETE /hr/attachments/<id>/           ← حذف ملف

GET    /hr/employees/search/?q=اسم     ← للـ autocomplete في LaborEntry

GET    /hr/leaves/                     ← الإجازات (فلتر: status, employee, date)
POST   /hr/leaves/                     ← طلب إجازة
PATCH  /hr/leaves/<id>/approve/        ← موافقة
PATCH  /hr/leaves/<id>/reject/         ← رفض

GET    /hr/attendance/                 ← الحضور (فلتر: date, employee)
POST   /hr/attendance/                 ← تسجيل حضور
PATCH  /hr/attendance/<id>/            ← تعديل
```

## 3.4 — Frontend Pages:

```
src/pages/hr/
├── HRDashboard.jsx          ← بطاقات إحصائية (موظفين، إجازات معلقة، حضور اليوم)
├── EmployeeList.jsx         ← جدول + فلاتر + بحث
├── EmployeeForm.jsx         ← نموذج إضافة/تعديل (Dialog أو Page)
├── EmployeeDetail.jsx       ← تفاصيل بـ 4 Tabs:
│   ├── Tab 1: البيانات الأساسية
│   ├── Tab 2: الملفات والمرفقات (Cloudinary upload)
│   ├── Tab 3: سجل الحضور
│   └── Tab 4: الإجازات
└── LeaveManagement.jsx      ← إدارة طلبات الإجازات
```

---

# 🔴 PHASE 4 — Admin Dashboard (رابعاً)

## هيكل الصفحة:

```
/admin                                 (SUPER_ADMIN + OWNER + MANAGER)
├── 👥 المستخدمين          ← موجود، يبقى
├── 🎨 محتوى الموقع (CMS) ← موجود، يبقى
├── ⚙️ الحقول المخصصة     ← منقول من Reports (SUPER_ADMIN + OWNER + MANAGER)
├── 🔧 العمليات الفنية     ← جديد (SUPER_ADMIN + OWNER + MANAGER)
├── 👷 المقاولون           ← جديد (SUPER_ADMIN + OWNER + MANAGER)
├── 📋 قوائم التقارير      ← جديد — Varieties + Units (SUPER_ADMIN + OWNER + MANAGER)
├── 🌿 إعدادات المحاصيل    ← جديد — أنواع المحاصيل لكل مزرعة (SUPER_ADMIN + OWNER)
└── 🏢 إعدادات الشركة      ← جديد (SUPER_ADMIN + OWNER فقط)
```

## Permission Matrix للـ Admin:

| Section | SUPER_ADMIN | OWNER | MANAGER |
|---------|------------|-------|---------|
| المستخدمين | ✅ كامل | ✅ كامل | ✅ جزئي (لا حذف) |
| CMS | ✅ | ✅ | ❌ |
| الحقول المخصصة | ✅ | ✅ | ✅ |
| العمليات الفنية | ✅ | ✅ | ✅ |
| المقاولون | ✅ | ✅ | ✅ |
| قوائم التقارير | ✅ | ✅ | ✅ |
| إعدادات المحاصيل | ✅ | ✅ | ❌ |
| إعدادات الشركة | ✅ | ✅ | ❌ |

## الميزة الأساسية — Dynamic Report Fields:
```
Admin يقدر:
✅ يضيف حقل مخصص لأي تقرير
✅ يغير نوع الحقل (text/number/date/dropdown/boolean)
✅ يضيف خيارات dropdown مباشرة
✅ يرتب الحقول بـ Drag & Drop
✅ يخفي/يظهر الحقول الثابتة
✅ يجعل الحقل إجباري أو اختياري
✅ يربط الحقل بـ محصول معين (فقط يظهر للنخيل مثلاً)
```

---

# 🟡 PHASE 5 — Warehouse — إدارة المخازن

## الحالة الحالية:
موجود backend أساسي (Items + Movements) — يحتاج تحسين UI وإضافات.

## الإضافات المطلوبة:

### Backend:
```python
# إضافة لـ WarehouseItem:
category = models.CharField(max_length=100)          # فئة المنتج
unit = models.CharField(max_length=50)               # الوحدة (كيلو/لتر/قطعة)
min_stock = models.FloatField(default=0)             # الحد الأدنى للتنبيه
location = models.CharField(max_length=200, blank=True)  # موقع المخزن

# Endpoint جديد:
GET /warehouse/alerts/    ← عناصر قاربت على النفاد (quantity <= min_stock)
GET /warehouse/summary/   ← إجماليات (قيمة المخزن، عدد الأصناف، التنبيهات)
```

### Frontend:
```
src/pages/warehouse/
├── InventoryLedger.jsx    ← موجود — تحسين UI
├── LowStockAlerts.jsx     ← جديد — تنبيهات نقص المخزون
└── WarehouseSummary.jsx   ← جديد — بطاقات إحصائية
```

### ربط مع النظام:
- تقرير التسميد → يخصم من مخزون المواد
- Alert تلقائي لـ Manager/OWNER عند نقص المخزون

---

# 🟡 PHASE 6 — Accounting — المحاسبة

## الحالة الحالية:
FinanceDashboard موجود — يحتاج ربط بالبيانات الحقيقية.

## الإضافات المطلوبة:

### Backend:
```python
# ربط الرواتب بـ HR:
GET /accounting/payroll/         ← رواتب الموظفين من HR + LaborEntry costs
GET /accounting/labor-costs/     ← تكلفة العمالة من التقارير اليومية
GET /accounting/monthly-summary/ ← ملخص شهري (إيرادات - مصروفات)

# تقرير التكلفة لكل حقل:
GET /accounting/location-costs/?location_id=X ← تكلفة موقع معين
```

### Frontend:
```
src/pages/accounting/
├── FinanceDashboard.jsx    ← موجود — إضافة charts حقيقية
├── PayrollPage.jsx         ← جديد — كشف رواتب مربوط بـ HR
├── CostAnalysis.jsx        ← جديد — تحليل تكلفة لكل موقع/عملية
└── ExpenseTracker.jsx      ← جديد — تتبع المصروفات
```

### ربط مع النظام:
```
HR.salary → Accounting.payroll
LaborEntry (hours × rate) → Accounting.labor_cost
Warehouse.movements → Accounting.material_cost
```

---

# 🟡 PHASE 7 — Fleet & Equipment — الأسطول والمعدات

## الحالة الحالية:
FleetManager موجود — يحتاج ربط بالتقارير.

## الإضافات المطلوبة:

### Backend:
```python
# إضافة لـ Equipment:
assigned_location = models.ForeignKey('farm.LocationNode', null=True, blank=True, ...)
# ربط استخدام المعدات بالتقارير اليومية:
class EquipmentUsageLog(TenantAwareModel):
    equipment = models.ForeignKey(Equipment, ...)
    report    = models.ForeignKey('reports.DailyTaskReport', null=True, blank=True, ...)
    date      = models.DateField()
    hours     = models.FloatField()
    operator  = models.ForeignKey(settings.AUTH_USER_MODEL, ...)
    notes     = models.TextField(blank=True)
```

### في التقرير اليومي — إضافة:
```
المعدات المستخدمة: [dropdown من المعدات] + ساعات الاستخدام
```

### Frontend:
```
src/pages/equipment/
├── FleetManager.jsx      ← موجود — إضافة ربط بالتقارير
├── MaintenanceLog.jsx    ← جديد — سجل الصيانة
└── UsageAnalytics.jsx    ← جديد — تحليل استخدام المعدات
```

---

# 🟢 PHASE 8 & 9 — Palm + Olive Records (توحيد)

## المشكلة الحالية:
موديلان منفصلان (PalmRecord + OliveRecord) — وهذا خلاف مبدأ الـ SaaS.

## الحل (من REFACTOR_PLAN):
```python
# موديل موحد CropRecord:
class CropRecord(TenantAwareModel):
    CROP_TYPES = [
        ('palm',  'نخيل'),
        ('olive', 'زيتون'),
        ('grape', 'عنب'),     # قابل للتوسعة لأي محصول
        ('other', 'أخرى'),
    ]
    crop_type  = models.CharField(max_length=20, choices=CROP_TYPES)
    location   = models.ForeignKey('farm.LocationNode', ...)
    # الحقول المشتركة
    tree_count = models.IntegerField(default=0)
    area       = models.FloatField(null=True, blank=True, help_text="بالفدان")
    variety    = models.ForeignKey('reports.Variety', null=True, blank=True, ...)
    notes      = models.TextField(blank=True)
    # الحقول الإضافية المخصصة → CustomField system
```

### Frontend:
```
src/pages/crops/
├── CropRecords.jsx        ← موحد بـ type filter (يعوض Palm + Olive)
└── CropDetail.jsx         ← تفاصيل + إحصاءات + صور
```

### ملاحظة للـ SaaS:
الـ Admin يضيف أنواع المحاصيل من Admin Dashboard — لا تعديل كود.

---

# 🟢 PHASE 10 — Production — المحصول

## الإضافات المطلوبة:

### Backend:
```python
# إضافة لـ YieldRecord:
location   = models.ForeignKey('farm.LocationNode', ...)   # ربط بالموقع
crop_type  = models.CharField(max_length=20)               # نوع المحصول
variety    = models.ForeignKey('reports.Variety', null=True, ...)
# season tracking:
season     = models.CharField(max_length=50, blank=True)   # موسم الحصاد
```

### Frontend:
```
src/pages/production/
├── YieldTracking.jsx     ← موجود — إضافة location filter
├── HarvestCalendar.jsx   ← جديد — تقويم المحصول
└── YieldAnalytics.jsx    ← جديد — مقارنة سنة بسنة
```

---

# 📁 الهيكل الكامل للملفات النهائي

## Backend:
```
Back-End/
├── apps/
│   ├── hr/
│   │   ├── models.py          ← تعديل (+ address, phone, EmployeeAttachment)
│   │   ├── views.py           ← جديد كامل
│   │   └── migrations/        ← migration جديدة
│   ├── reports/
│   │   └── models.py          ← إضافة employee FK إلى LaborEntry
│   ├── farm/
│   │   └── models.py          ← تنظيف (الموديلات القديمة deprecated)
│   └── crops/                 ← جديد (يوحد Palm + Olive)
│       ├── models.py          ← CropRecord
│       └── migrations/
├── serializers/
│   ├── hr_serializers.py      ← جديد
│   └── reports_serializers.py ← تحديث LaborEntry
├── api/endpoints/
│   ├── hr_views.py            ← جديد
│   └── admin_views.py         ← جديد
├── services/
│   └── user_service.py        ← تعديل (auto-create Employee)
└── api/urls.py                ← إضافة جميع الـ routes
```

## Frontend:
```
Front-End/src/
├── layouts/
│   ├── DashboardLayout.jsx    ← تعديل (إضافة Sidebar)
│   └── Sidebar.jsx            ← جديد (role-based navigation)
├── features/
│   └── hr/
│       └── services.js        ← جديد
├── pages/
│   ├── farm/
│   │   ├── FarmStructure.jsx  ← تعديل (Adaptive Tree)
│   │   └── FarmStructure.css  ← تعديل
│   ├── reports/DailyTaskReport/
│   │   ├── DailyTaskForm.jsx  ← تعديل (+ LaborEntry button)
│   │   └── LaborEntryDrawer.jsx ← جديد
│   ├── hr/
│   │   ├── HRDashboard.jsx    ← جديد
│   │   ├── EmployeeList.jsx   ← جديد
│   │   ├── EmployeeForm.jsx   ← جديد
│   │   ├── EmployeeDetail.jsx ← جديد
│   │   └── LeaveManagement.jsx ← جديد
│   ├── admin/
│   │   ├── AdminDashboard.jsx ← تعديل كبير
│   │   └── sections/
│   │       ├── CustomFieldsAdmin.jsx  ← نقل + تحسين
│   │       ├── OperationsAdmin.jsx    ← جديد
│   │       ├── ContractorsAdmin.jsx   ← جديد
│   │       ├── DropdownsAdmin.jsx     ← جديد
│   │       ├── CropTypesAdmin.jsx     ← جديد (للـ SaaS)
│   │       └── CompanySettings.jsx    ← جديد
│   ├── crops/
│   │   ├── CropRecords.jsx    ← جديد (يوحد Palm + Olive)
│   │   └── CropDetail.jsx     ← جديد
│   ├── warehouse/
│   │   └── InventoryLedger.jsx ← تحسين + إضافات
│   ├── accounting/
│   │   ├── FinanceDashboard.jsx ← تحسين
│   │   └── PayrollPage.jsx    ← جديد
│   ├── equipment/
│   │   └── FleetManager.jsx   ← تحسين + ربط
│   └── production/
│       └── YieldTracking.jsx  ← تحسين + ربط
└── routes/
    └── AppRoutes.jsx          ← إضافة جميع الـ routes الجديدة
```

---

# 🚀 ترتيب التنفيذ الكامل

```
═══════════════════════════════════════
PHASE 1 — FarmStructure Adaptive Tree
═══════════════════════════════════════
الخطوة 1.1: تعديل FarmStructure.jsx (getNodeConfig function)
الخطوة 1.2: تعديل FarmStructure.css (size classes)
الخطوة 1.3: إضافة Collapse/Expand
الخطوة 1.4: إضافة Search/Filter
الخطوة 1.5: إضافة Count badges

═══════════════════════════════════════
PHASE 2 — LaborEntry Panel
═══════════════════════════════════════
الخطوة 2.1: migration إضافة employee FK إلى LaborEntry
الخطوة 2.2: تحديث LaborEntrySerializer
الخطوة 2.3: إنشاء LaborEntryDrawer.jsx
الخطوة 2.4: تعديل DailyTaskForm.jsx (إضافة الزر والربط)
الخطوة 2.5: إضافة employee search endpoint

═══════════════════════════════════════
PHASE 3 — HR Backend
═══════════════════════════════════════
الخطوة 3.1: تعديل Employee model + إضافة EmployeeAttachment
الخطوة 3.2: migration
الخطوة 3.3: إنشاء hr_serializers.py
الخطوة 3.4: إنشاء hr_views.py (كل الـ endpoints)
الخطوة 3.5: تحديث user_service.py (auto-create Employee)
الخطوة 3.6: إضافة routes في urls.py

═══════════════════════════════════════
PHASE 4 — HR Frontend
═══════════════════════════════════════
الخطوة 4.1: hr/services.js
الخطوة 4.2: HRDashboard.jsx
الخطوة 4.3: EmployeeList.jsx
الخطوة 4.4: EmployeeForm.jsx
الخطوة 4.5: EmployeeDetail.jsx (مع upload ملفات Cloudinary)
الخطوة 4.6: LeaveManagement.jsx

═══════════════════════════════════════
PHASE 5 — Sidebar + Navigation
═══════════════════════════════════════
الخطوة 5.1: Sidebar.jsx (role-based)
الخطوة 5.2: تعديل DashboardLayout.jsx
الخطوة 5.3: تحديث AppRoutes.jsx
الخطوة 5.4: BottomNav تحديث (للموبايل)

═══════════════════════════════════════
PHASE 6 — Admin Dashboard
═══════════════════════════════════════
الخطوة 6.1: Admin backend endpoints (operations, contractors, dropdowns)
الخطوة 6.2: تعديل AdminDashboard.jsx (هيكل جديد)
الخطوة 6.3: نقل CustomFields + تحسينها
الخطوة 6.4: OperationsAdmin + ContractorsAdmin
الخطوة 6.5: DropdownsAdmin + CropTypesAdmin

═══════════════════════════════════════
PHASE 7-10 — باقي الـ Modules
═══════════════════════════════════════
الخطوة 7: Warehouse تحسين
الخطوة 8: Accounting ربط + PayrollPage
الخطوة 9: Fleet ربط بالتقارير
الخطوة 10: CropRecord توحيد
الخطوة 11: Production ربط بالمواقع
```

---

# ⚠️ قواعد للـ AI Coder

```
❌ لا تكسر أي API موجودة (الـ response shape ثابتة)
❌ لا تحذف migrations — أضف جديدة فقط
❌ لا تُنشئ موديل جديد إذا كان مشابه موجود
❌ لا GenericForeignKey إلا في الـ CustomField system
❌ لا hardcoded roles في الـ Frontend — استخدم ROLE_PERMISSIONS object

✅ كل queryset يمر على _for_company() أو .for_company()
✅ كل endpoint له permission_classes صريحة
✅ Services layer للـ business logic
✅ Serializers تتحقق من الـ tenant scoping
✅ كل migration تأتي بعد إنشاء الـ model مباشرة
✅ الـ Frontend يستخدم الـ role من AuthContext لـ conditional rendering

# CLOUDINARY في Frontend:
✅ استخدم unsigned upload مع upload_preset='atls_unsigned'
✅ احفظ الـ secure_url في DB — مش الـ public_id
✅ اعرض preview قبل الرفع
✅ اقبل: jpg, jpeg, png, webp, pdf فقط
```

---

# 📊 خريطة الربط الكاملة (Entity Map)

```
Company
├── User
│   └── Employee (OneToOne — auto على ENGINEER/MANAGER/HR/ACCOUNTANT/WAREHOUSE)
│       ├── EmployeeAttachment[]  (Cloudinary URLs)
│       ├── LeaveRequest[]
│       └── Attendance[]
│
├── Farm
│   └── LocationNode (MPTT tree)
│       ├── DailyTaskReport[]
│       │   ├── LaborEntry[] → Employee? (ربط اختياري بالاسم)
│       │   └── Attachment[] (Cloudinary)
│       ├── FertilizationReport[]
│       ├── IrrigationReport[]
│       └── CropRecord[] (يوحد Palm + Olive)
│
├── Operation[]           (عمليات فنية)
├── Contractor[]          (مقاولون — يظهروا في LaborEntry)
├── Variety[]             (أصناف)
├── Unit[]                (وحدات)
├── CustomFieldDefinition[] (حقول مخصصة لأي تقرير)
│
├── WarehouseItem[]
│   └── WarehouseMovement[]
│
├── Equipment[]
│   └── EquipmentUsageLog[]
│
├── Expense[]
├── Revenue[]
└── YieldRecord[]
```

---

*هذا الملف هو المرجع الرئيسي للمشروع — كل تعديل يجب أن يتوافق مع هذه الخطة*
*آخر تحديث: بعد مراجعة الكود الكاملة*
