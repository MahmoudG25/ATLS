# Back-End/permissions/registry/hr.py

PERMISSIONS = {
    "hr.manage": {
        "module": "hr",
        "label": "إدارة الموارد البشرية",
        "description": "صلاحية كاملة لإدارة شؤون الموظفين والعمال والرواتب",
    },
    "hr.read": {
        "module": "hr",
        "label": "عرض شؤون الموظفين",
        "description": "صلاحية استعراض الموظفين والرواتب دون إمكانية التعديل",
    },
    "hr.edit": {
        "module": "hr",
        "label": "تعديل شؤون الموظفين",
        "description": "صلاحية إضافة وتعديل بيانات الموظفين والعمال",
    },
    "payroll.approve": {
        "module": "hr",
        "label": "اعتماد الرواتب",
        "description": "صلاحية اعتماد فترات الرواتب والمعاملات المالية للموظفين",
    },
}
