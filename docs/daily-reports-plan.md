# 📋 خطة نظام التقارير اليومية — Atlas Farm ERP

> **الهدف:** بناء نظام تقارير يومية متكامل مدمج مع مشروع Atlas Farm ERP القائم على Django + React/Vite، يغطي تقرير المهام اليومي، التسميد، والري — مع تجربة عرض جميلة وسلسة تليق بمشروع زراعي احترافي.

---

## جدول المحتويات

1. [نظرة عامة على النظام](#1-نظرة-عامة-على-النظام)
2. [أنواع التقارير](#2-أنواع-التقارير)
3. [نماذج البيانات — Django Models](#3-نماذج-البيانات--django-models)
4. [API Endpoints](#4-api-endpoints)
5. [تصميم الـ Frontend — React](#5-تصميم-الـ-frontend--react)
6. [تجربة عرض التقارير](#6-تجربة-عرض-التقارير)
7. [نموذج إدخال البيانات](#7-نموذج-إدخال-البيانات)
8. [ملفات المشروع التي تتأثر](#8-ملفات-المشروع-التي-تتأثر)
9. [خطة التنفيذ](#9-خطة-التنفيذ)

---

## 1. نظرة عامة على النظام

نظام التقارير مبني على **4 تقارير رئيسية** مستخرجة من بيانات المزرعة الحالية:

```
Atlas Farm Reports System
│
├── تقرير المهام اليومي        ← الأساسي (Engineers Daily Log)
├── تقرير التسميد              ← Fertilization Report
├── تقرير الري                 ← Irrigation Report
└── ملخص العمليات (Pivot)      ← Operations Summary
```

### المبادئ التصميمية

- **RTL-first:** كل الواجهات تدعم العربية بشكل أصيل
- **Mobile-first:** المهندسون يدخلون البيانات من الحقل عبر الهاتف
- **Read at a glance:** العرض مصمم ليُقرأ في ثوانٍ، بألوان وأيقونات واضحة
- **No duplicates:** نفس نموذج التسجيل يغذي كل التقارير تلقائياً

---

## 2. أنواع التقارير

### 2.1 تقرير المهام اليومي `DailyTaskReport`

أهم تقرير في النظام. يُسجَّل يومياً من كل مهندس.

**الحقول المطلوبة (مستخرجة من البيانات الفعلية):**

| الحقل | النوع | المصدر | ملاحظة |
|-------|-------|--------|--------|
| `engineer` | FK → Engineer | اسم المهندس | أحمد خالد / مرسي سعد / إلخ |
| `report_date` | Date | التاريخ | auto-fill اليوم |
| `sector` | CharField | القطاع | A / B / C / D / الصوب |
| `variety` | CharField | الصنف | مجدول / صعيدي / ليمون / أخرى |
| `enclosure` | CharField | الحوشة | أرقام مثل 1-2-3 |
| `work_location` | CharField | مكان العمل | المرحلة الأولى / السيوي / إلخ |
| `company_workers` | IntegerField | عدد عمال الشركة | |
| `contractor_workers` | IntegerField | عدد عمال المقاول | |
| `contractor_code` | IntegerField | كود المقاول | 1 / 2 / 7 / 8 |
| `operation` | FK → Operation | اسم العملية الفنية | من قائمة ثابتة |
| `unit` | CharField | الوحدة | فسيلة / نخلة / جورة / حوشة |
| `actual_productivity` | FloatField | الانتاجية الفعلية | |
| `work_hours` | FloatField | ساعات العمل | |
| `overtime_hours` | FloatField | اجمالي ساعات الإضافي | nullable |
| `overtime_productivity` | FloatField | الانتاجية في الإضافي | nullable |
| `notes` | TextField | ملاحظة | nullable |

---

### 2.2 تقرير التسميد `FertilizationReport`

**الحقول:**

| الحقل | النوع | ملاحظة |
|-------|-------|--------|
| `report_date` | Date | |
| `variety` | CharField | الصنف |
| `material` | FK → FertMaterial | المادة الفعالة |
| `active_percentage` | FloatField | النسبة المئوية |
| `rate_per_feddan` | FloatField | معدل الفدان |
| `transfer_number` | IntegerField | رقم التحويلة |
| `valves` | CharField | المحابس |
| `area_feddan` | FloatField | المساحة بالفدان |
| `tree_count` | IntegerField | عدد الأشجار |
| `total_quantity` | FloatField | إجمالي الكمية (محسوبة) |
| `operator` | CharField | القائم بالعمل |
| `notes` | TextField | ملاحظات |

**المواد الكيماوية المعرّفة (من البيانات):**

```python
FERTILIZER_MATERIALS = [
    ("سلفات نشادر",    "20%"),
    ("سلفات مغنسيوم",  "15%"),
    ("سلفات بوتاسيوم", "50%"),
    ("حمض فوسفوريك",  "85%"),
    ("سلفات زنك",      ""),
    ("سلفات منجنيز",   ""),
    ("سلفات حديد",     ""),
    ("بوريك",          ""),
    ("هيومك",          ""),
    ("نترات كالسيوم",  ""),
    ("حمض نيتريك",    ""),
]
```

---

### 2.3 تقرير الري `IrrigationReport`

**الحقول:**

| الحقل | النوع | ملاحظة |
|-------|-------|--------|
| `sector_number` | IntegerField | رقم القطاع |
| `transfer_number` | IntegerField | رقم التحويلة |
| `area_feddan` | FloatField | المساحة بالفدان |
| `tree_count` | IntegerField | عدد النخيل |
| `well_flow_m3` | FloatField | تصرف البئر م³/ساعة |
| `water_per_tree` | FloatField | كمية المياه للنخلة |
| `irrigation_hours` | FloatField | عدد ساعات الري للتحويلة |
| `irrigation_cycles` | IntegerField | عدد مرات الري |
| `notes` | TextField | |

---

### 2.4 ملخص العمليات `OperationsSummary` (View — لا يُدخَل يدوياً)

يُحسب تلقائياً من `DailyTaskReport` عبر Django aggregation:

```python
from django.db.models import Sum, Count

DailyTaskReport.objects.values(
    'operation__name', 'variety'
).annotate(
    total_productivity=Sum('actual_productivity'),
    total_workers=Sum('contractor_workers'),
)
```

---

## 3. نماذج البيانات — Django Models

```python
# Back-End/reports/models.py

from django.db import models
from django.conf import settings


class Operation(models.Model):
    """قائمة العمليات الفنية الثابتة"""
    name = models.CharField(max_length=200, unique=True)
    category = models.CharField(max_length=50, choices=[
        ('harvest',      'حصاد'),
        ('planting',     'زراعة'),
        ('maintenance',  'صيانة'),
        ('pest_control', 'مكافحة'),
        ('transport',    'نقل وتحميل'),
        ('other',        'أخرى'),
    ])

    class Meta:
        verbose_name = "عملية فنية"
        verbose_name_plural = "العمليات الفنية"

    def __str__(self):
        return self.name


class DailyTaskReport(models.Model):
    """تقرير المهام اليومي"""

    SECTOR_CHOICES = [
        ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'),
        ('greenhouse', 'الصوب'),
        ('new_farms',  'الزراعات الجديدة'),
        ('all',        'كل المزرعة'),
    ]

    VARIETY_CHOICES = [
        ('medjool',         'مجدول'),
        ('saidi',           'صعيدي'),
        ('lemon',           'ليمون'),
        ('medjool_lemon',   'مجدول + ليمون'),
        ('farihi',          'فريحي'),
        ('greenhouse',      'الصوب'),
        ('all',             'كل الأصناف'),
        ('other',           'أخرى'),
    ]

    UNIT_CHOICES = [
        ('seedling',  'فسيلة'),
        ('palm',      'نخلة'),
        ('pit',       'جورة'),
        ('enclosure', 'حوشة'),
        ('preparation', 'تحضيرة'),
        ('cone',      'كوز'),
        ('other',     'أخرى'),
    ]

    engineer        = models.ForeignKey(
                          settings.AUTH_USER_MODEL,
                          on_delete=models.PROTECT,
                          related_name='daily_reports',
                          verbose_name="المهندس"
                      )
    report_date     = models.DateField(verbose_name="تاريخ التقرير")
    sector          = models.CharField(max_length=20, choices=SECTOR_CHOICES, verbose_name="القطاع")
    variety         = models.CharField(max_length=30, choices=VARIETY_CHOICES, verbose_name="الصنف")
    enclosure       = models.CharField(max_length=100, blank=True, verbose_name="الحوشة")
    work_location   = models.CharField(max_length=100, verbose_name="مكان العمل")
    company_workers = models.PositiveIntegerField(default=0, verbose_name="عمال الشركة")
    contractor_workers = models.PositiveIntegerField(default=0, verbose_name="عمال المقاول")
    contractor_code = models.CharField(max_length=20, blank=True, verbose_name="كود المقاول")
    operation       = models.ForeignKey(Operation, on_delete=models.PROTECT, verbose_name="العملية الفنية")
    unit            = models.CharField(max_length=20, choices=UNIT_CHOICES, verbose_name="الوحدة")
    actual_productivity  = models.FloatField(null=True, blank=True, verbose_name="الانتاجية الفعلية")
    work_hours      = models.FloatField(verbose_name="ساعات العمل")
    overtime_hours  = models.FloatField(null=True, blank=True, verbose_name="ساعات الإضافي")
    overtime_productivity = models.FloatField(null=True, blank=True, verbose_name="انتاجية الإضافي")
    notes           = models.TextField(blank=True, verbose_name="ملاحظة")
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "تقرير مهام يومي"
        verbose_name_plural = "تقارير المهام اليومية"
        ordering = ['-report_date', 'engineer']
        indexes = [
            models.Index(fields=['report_date']),
            models.Index(fields=['engineer', 'report_date']),
            models.Index(fields=['sector', 'report_date']),
        ]

    def __str__(self):
        return f"{self.engineer} | {self.report_date} | {self.operation}"


class FertilizationReport(models.Model):
    """تقرير التسميد"""

    report_date         = models.DateField(verbose_name="تاريخ")
    variety             = models.CharField(max_length=30, verbose_name="الصنف")
    material_name       = models.CharField(max_length=100, verbose_name="المادة الفعالة")
    active_percentage   = models.FloatField(null=True, blank=True, verbose_name="النسبة %")
    rate_per_feddan     = models.FloatField(null=True, blank=True, verbose_name="معدل الفدان")
    transfer_number     = models.IntegerField(null=True, blank=True, verbose_name="رقم التحويلة")
    valves              = models.CharField(max_length=50, blank=True, verbose_name="المحابس")
    area_feddan         = models.FloatField(null=True, blank=True, verbose_name="المساحة (فدان)")
    tree_count          = models.IntegerField(null=True, blank=True, verbose_name="عدد الأشجار")
    total_quantity      = models.FloatField(null=True, blank=True, verbose_name="إجمالي الكمية")
    operator            = models.CharField(max_length=100, blank=True, verbose_name="القائم بالعمل")
    notes               = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "تقرير تسميد"
        verbose_name_plural = "تقارير التسميد"
        ordering = ['-report_date']


class IrrigationReport(models.Model):
    """تقرير الري"""

    report_date       = models.DateField(verbose_name="تاريخ")
    sector_number     = models.IntegerField(verbose_name="رقم القطاع")
    transfer_number   = models.IntegerField(verbose_name="رقم التحويلة")
    area_feddan       = models.FloatField(null=True, blank=True, verbose_name="المساحة (فدان)")
    tree_count        = models.IntegerField(null=True, blank=True, verbose_name="عدد النخيل")
    well_flow_m3      = models.FloatField(null=True, blank=True, verbose_name="تصرف البئر م³/ساعة")
    water_per_tree    = models.FloatField(null=True, blank=True, verbose_name="كمية المياه للنخلة")
    irrigation_hours  = models.FloatField(null=True, blank=True, verbose_name="ساعات الري")
    irrigation_cycles = models.IntegerField(null=True, blank=True, verbose_name="مرات الري")
    notes             = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "تقرير ري"
        verbose_name_plural = "تقارير الري"
        ordering = ['-report_date']
```

---

## 4. API Endpoints

```python
# Back-End/reports/urls.py

urlpatterns = [
    # تقارير المهام اليومية
    path('reports/tasks/',           DailyTaskReportListCreate.as_view()),
    path('reports/tasks/<int:pk>/',  DailyTaskReportDetail.as_view()),
    path('reports/tasks/summary/',   DailyTaskSummaryView.as_view()),  # pivot
    path('reports/tasks/export/',    DailyTaskExportView.as_view()),   # Excel

    # تقارير التسميد
    path('reports/fertilization/',          FertilizationListCreate.as_view()),
    path('reports/fertilization/<int:pk>/', FertilizationDetail.as_view()),

    # تقارير الري
    path('reports/irrigation/',          IrrigationListCreate.as_view()),
    path('reports/irrigation/<int:pk>/', IrrigationDetail.as_view()),

    # بيانات مساعدة
    path('reports/operations/',   OperationListView.as_view()),  # قائمة العمليات
]
```

### Filters المتاحة على `/reports/tasks/`

```
GET /api/reports/tasks/?date=2025-08-19
GET /api/reports/tasks/?engineer=3
GET /api/reports/tasks/?sector=A
GET /api/reports/tasks/?date_from=2025-08-01&date_to=2025-08-31
GET /api/reports/tasks/?operation=تلقيح
```

---

## 5. تصميم الـ Frontend — React

### هيكل المكونات

```
Front-End/src/views/reports/
│
├── ReportsIndex.jsx          ← الصفحة الرئيسية للتقارير
├── DailyTaskReport/
│   ├── DailyTaskList.jsx     ← قائمة التقارير مع فلاتر
│   ├── DailyTaskCard.jsx     ← بطاقة تقرير مفردة
│   ├── DailyTaskForm.jsx     ← نموذج الإدخال
│   └── DailyTaskSummary.jsx  ← ملخص العمليات (pivot)
├── FertilizationReport/
│   ├── FertilizationList.jsx
│   └── FertilizationForm.jsx
├── IrrigationReport/
│   ├── IrrigationList.jsx
│   └── IrrigationForm.jsx
└── shared/
    ├── ReportFilters.jsx     ← شريط الفلاتر المشترك
    ├── ReportBadge.jsx       ← badge للقطاع / الصنف
    └── ExportButton.jsx      ← تصدير Excel
```

### التوجيه (Routing)

```javascript
// Front-End/src/router/routes.js

{
  path: '/reports',
  children: [
    { path: '',           element: <ReportsIndex />      },
    { path: 'tasks',      element: <DailyTaskList />     },
    { path: 'tasks/new',  element: <DailyTaskForm />     },
    { path: 'tasks/:id',  element: <DailyTaskCard />     },
    { path: 'summary',    element: <DailyTaskSummary />  },
    { path: 'fertilization', element: <FertilizationList /> },
    { path: 'irrigation',    element: <IrrigationList />    },
  ]
}
```

---

## 6. تجربة عرض التقارير

### 6.1 صفحة قائمة التقارير `DailyTaskList`

```
┌─────────────────────────────────────────────────┐
│  📋 تقارير المهام اليومية          [+ تقرير جديد] │
├─────────────────────────────────────────────────┤
│  📅 التاريخ  👷 المهندس  🗂 القطاع  🔍 بحث       │
├─────────────────────────────────────────────────┤
│                                                  │
│  ╔══════════════════════════════════════════╗   │
│  ║  أحمد خالد          19 أغسطس 2025       ║   │
│  ║  ──────────────────────────────────────  ║   │
│  ║  🌿 الصوب · أخرى · صيانة صوب ودكار     ║   │
│  ║  👷 3 شركة + 8 مقاول · كود: 3           ║   │
│  ║  📊 1 صوبة في 9 ساعات + 3 أضافي        ║   │
│  ╚══════════════════════════════════════════╝   │
│                                                  │
│  ╔══════════════════════════════════════════╗   │
│  ║  عبد الرحمن حسن      19 أغسطس 2025      ║   │
│  ║  ──────────────────────────────────────  ║   │
│  ║  🌴 A · مجدول+ليمون · إزالة حشائش      ║   │
│  ║  👷 1 شركة + 28 مقاول · كود: 1          ║   │
│  ║  📊 780 جورة في 9 ساعات + 1 أضافي      ║   │
│  ╚══════════════════════════════════════════╝   │
└─────────────────────────────────────────────────┘
```

### 6.2 بطاقة التقرير المفردة `DailyTaskCard`

```
┌──────────────────────────────────────────────────────┐
│  ← رجوع                                   ✏️ تعديل  │
├──────────────────────────────────────────────────────┤
│                                                       │
│     م. أحمد خالد                   19 أغسطس 2025    │
│     ─────────────────────────────────────────────    │
│                                                       │
│   📍 الموقع          🗂 القطاع       🌿 الصنف        │
│   الصوب              الصوب           أخرى             │
│                                                       │
│   ⚙️ العملية الفنية                                   │
│   ┌───────────────────────────────────────────────┐  │
│   │  صيانة صوب وتنشير أكواز دكار                 │  │
│   └───────────────────────────────────────────────┘  │
│                                                       │
│   👷 العمال                                          │
│   ┌───────────────┐  ┌───────────────┐               │
│   │  3 شركة       │  │  8 مقاول      │               │
│   │               │  │  كود: 3       │               │
│   └───────────────┘  └───────────────┘               │
│                                                       │
│   📊 الإنتاجية                                       │
│   ┌──────────────────────────────────────────────┐   │
│   │  الوحدة    الانتاجية    الساعات    الإضافي   │   │
│   │  كوز       1 صوبة       9 ساعات   3 ساعات   │   │
│   └──────────────────────────────────────────────┘   │
│                                                       │
│   📝 ملاحظة                                          │
│   عدد 1 ساعة لعدد 3 عمال شركة للمتابعة في الصوب    │
│   لعدم وجود أخطاء من عمال الصيانة أثناء العمل       │
│                                                       │
└──────────────────────────────────────────────────────┘
```

### 6.3 ألوان البطاقات حسب القطاع

```javascript
// colors.js
const SECTOR_COLORS = {
  A:          { bg: '#E8F5E9', border: '#4CAF50', text: '#1B5E20' }, // أخضر
  B:          { bg: '#E3F2FD', border: '#2196F3', text: '#0D47A1' }, // أزرق
  C:          { bg: '#FFF3E0', border: '#FF9800', text: '#E65100' }, // برتقالي
  D:          { bg: '#F3E5F5', border: '#9C27B0', text: '#4A148C' }, // بنفسجي
  greenhouse: { bg: '#E0F2F1', border: '#00BCD4', text: '#006064' }, // فيروزي (الصوب)
  new_farms:  { bg: '#FCE4EC', border: '#E91E63', text: '#880E4F' }, // وردي (الزراعات الجديدة)
};

const VARIETY_ICONS = {
  medjool:   '🌴',
  saidi:     '🌿',
  lemon:     '🍋',
  greenhouse:'🏗️',
  other:     '🔧',
};
```

### 6.4 ملخص العمليات `DailyTaskSummary`

```
┌──────────────────────────────────────────────┐
│  📈 ملخص العمليات          [يومي/أسبوعي/شهري] │
├──────────────────────────────────────────────┤
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ نقل وتحميل│  │إزالة حشائش│  │تلقيح     │  │
│  │  9,610 🌴 │  │  9,404 🌿 │  │  7,424 🌴 │  │
│  │  فسيلة   │  │  جورة    │  │  نخلة    │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│                                              │
│  اسم العملية           الصنف   الانتاجية     │
│  ─────────────────────────────────────────  │
│  متابعة الفصل          مجدول      2,200     │
│  ازالة العروسه         مجدول      1,480     │
│  تقليع فسائل           صعيدي      1,420     │
│  زراعة الفسائل         صعيدي      1,115     │
│  تلقيح                 صعيدي      3,419     │
│                                              │
└──────────────────────────────────────────────┘
```

---

## 7. نموذج إدخال البيانات

### 7.1 تصميم الـ Form

النموذج مقسم إلى **3 خطوات** (stepper) لتسهيل الإدخال من الجوال:

```
الخطوة 1: من أنا وأين؟
─────────────────────────────
  📅 التاريخ     [اليوم تلقائياً]
  👷 اسم المهندس  [dropdown]
  🗂 القطاع       [A / B / C / D / الصوب / ...]
  🌿 الصنف        [مجدول / صعيدي / ...]
  🏠 الحوشة       [نص حر، مثال: 1-2-3]
  📍 مكان العمل   [نص حر]

الخطوة 2: تفاصيل العمل
─────────────────────────────
  ⚙️ العملية الفنية   [searchable dropdown]
  📦 الوحدة            [فسيلة / نخلة / جورة / ...]
  👥 عمال الشركة       [رقم]
  👥 عمال المقاول      [رقم]
  🔢 كود المقاول       [رقم]

الخطوة 3: الإنتاجية والملاحظات
─────────────────────────────
  📊 الانتاجية الفعلية  [رقم]
  ⏰ ساعات العمل        [رقم]
  ⏱ ساعات الإضافي      [رقم، اختياري]
  📈 انتاجية الإضافي    [رقم، اختياري]
  📝 ملاحظة             [textarea]

  [← رجوع]            [💾 حفظ التقرير]
```

### 7.2 Validation Rules

```javascript
// Front-End/src/views/reports/DailyTaskReport/validation.js

export const taskReportSchema = yup.object({
  engineer:           yup.number().required('اختر اسم المهندس'),
  report_date:        yup.date().required('التاريخ مطلوب'),
  sector:             yup.string().required('القطاع مطلوب'),
  variety:            yup.string().required('الصنف مطلوب'),
  work_location:      yup.string().required('مكان العمل مطلوب'),
  operation:          yup.number().required('العملية الفنية مطلوبة'),
  unit:               yup.string().required('الوحدة مطلوبة'),
  work_hours:         yup.number().min(0.5).max(24).required('ساعات العمل مطلوبة'),
  contractor_workers: yup.number().min(0).required(),
  company_workers:    yup.number().min(0).required(),
  // overtime — اختياري لكن مترابط
  overtime_hours: yup.number().nullable().when('overtime_productivity', {
    is: (val) => val > 0,
    then: (s) => s.required('أدخل ساعات الإضافي'),
  }),
});
```

---

## 8. ملفات المشروع التي تتأثر

```
Atlas Farm ERP
│
├── Back-End/
│   ├── reports/                 ← [جديد] تطبيق كامل
│   │   ├── models.py            ← النماذج الـ4
│   │   ├── serializers.py       ← DRF serializers
│   │   ├── views.py             ← ListCreate + Detail + Summary
│   │   ├── urls.py              ← routes
│   │   ├── filters.py           ← django-filter
│   │   ├── admin.py             ← admin panel
│   │   └── migrations/
│   ├── config/
│   │   ├── settings.py          ← [تعديل] أضف 'reports' في INSTALLED_APPS
│   │   └── urls.py              ← [تعديل] أضف path('api/', include('reports.urls'))
│
├── Front-End/
│   ├── src/
│   │   ├── views/
│   │   │   └── reports/         ← [جديد] المكونات كاملة
│   │   ├── services/
│   │   │   └── reportsApi.js    ← [جديد] API calls
│   │   ├── router/
│   │   │   └── routes.js        ← [تعديل] أضف مسارات التقارير
│   │   └── components/
│   │       └── Sidebar.jsx      ← [تعديل] أضف رابط التقارير
│
└── docs/
    ├── back-end/
    │   └── reports.md           ← [موجود — يُحدَّث بالـ API الجديد]
    └── front-end/
        └── module-pages.md      ← [موجود — يُحدَّث بصفحات التقارير]
```

---

## 9. خطة التنفيذ

### المرحلة الأولى: Backend (3 أيام)

```
اليوم 1:
  [ ] إنشاء تطبيق reports: python manage.py startapp reports
  [ ] كتابة models.py كاملاً
  [ ] python manage.py makemigrations && migrate
  [ ] كتابة admin.py (لتسجيل بيانات تجريبية)

اليوم 2:
  [ ] كتابة serializers.py
  [ ] كتابة views.py (CRUD كامل)
  [ ] ربط urls.py
  [ ] اختبار الـ API بـ Postman أو DRF Browsable API

اليوم 3:
  [ ] إضافة django-filter
  [ ] إضافة summary view (aggregation)
  [ ] إضافة export view (openpyxl)
  [ ] كتابة permissions (المهندس يرى تقاريره فقط، المدير يرى الكل)
```

### المرحلة الثانية: Frontend (4 أيام)

```
اليوم 4:
  [ ] إنشاء مجلد views/reports/
  [ ] كتابة reportsApi.js (axios calls)
  [ ] ReportFilters.jsx (شريط الفلاتر)

اليوم 5:
  [ ] DailyTaskList.jsx (قائمة مع بطاقات)
  [ ] DailyTaskCard.jsx (عرض تقرير مفرد)

اليوم 6:
  [ ] DailyTaskForm.jsx (stepper form — 3 خطوات)
  [ ] Validation بـ react-hook-form + yup

اليوم 7:
  [ ] DailyTaskSummary.jsx (pivot table + charts بـ recharts)
  [ ] FertilizationList + Form
  [ ] IrrigationList + Form
  [ ] تحديث Sidebar وRoutes
```

### المرحلة الثالثة: Polish (يوم واحد)

```
اليوم 8:
  [ ] اختبار RTL على كل الشاشات
  [ ] اختبار على الجوال (mobile viewport)
  [ ] تحسين الألوان والأيقونات
  [ ] تحديث docs/back-end/reports.md
  [ ] تحديث docs/front-end/module-pages.md
```

---

## ملاحظات ختامية

- **الأولوية:** ابدأ بـ `DailyTaskReport` فقط — هو الأكثر استخداماً
- **الأسماء:** قائمة المهندسين والعمليات الفنية تُبنى من البيانات الموجودة في السبريدشيت
- **Export:** استخدم `openpyxl` في الـ backend لتصدير نفس تنسيق السبريدشيت الحالي للتوافق مع الفريق
- **Offline support:** فكّر مستقبلاً في PWA أو local caching للمهندسين في مناطق ضعيفة الشبكة

---

*Last updated: 2025-08-19 — Atlas Farm ERP Reporting System Plan*
