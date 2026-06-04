# Back-End/permissions/registry/reports.py

PERMISSIONS = {
    "reports.create": {
        "module": "reports",
        "label": "إضافة التقارير",
        "description": "صلاحية كتابة تقرير يومي أو تقرير حصاد",
    },
    "reports.delete": {
        "module": "reports",
        "label": "حذف التقارير",
        "description": "صلاحية حذف التقارير اليومية أو الحصاد",
    },
    "reports.export": {
        "module": "reports",
        "label": "تصدير التقارير",
        "description": "صلاحية تصدير التقارير والبيانات الإحصائية بصيغة Excel/PDF",
    },
}
