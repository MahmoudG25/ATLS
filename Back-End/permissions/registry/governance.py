# Back-End/permissions/registry/governance.py

PERMISSIONS = {
    "farm.manage": {
        "module": "farm",
        "label": "إدارة هيكل المزرعة",
        "description": "صلاحية إدارة الأقسام والقطاعات والأحواش الزراعية",
    },
    "equipment.manage": {
        "module": "equipment",
        "label": "إدارة الأسطول والمعدات",
        "description": "صلاحية إضافة المعدات وتحديثها وتسجيل عمليات الصيانة وتغيير الزيت",
    },
    "production.manage": {
        "module": "production",
        "label": "إدارة الإنتاج والحصاد",
        "description": "صلاحية كاملة لإدارة خطط الإنتاج وتقارير الحصاد اليومية",
    },
    "can_post_announcement": {
        "module": "bulletin",
        "label": "نشر الإعلانات",
        "description": "صلاحية نشر وإدارة الإعلانات على لوحة الإعلانات العامة للمزرعة",
    },
}
