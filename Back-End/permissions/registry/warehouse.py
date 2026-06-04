# Back-End/permissions/registry/warehouse.py

PERMISSIONS = {
    "warehouse.manage": {
        "module": "warehouse",
        "label": "إدارة المخازن والمخزون",
        "description": "صلاحية كاملة لإضافة وتعديل المخازن وحركات المخزون",
    },
    "warehouse.transfer": {
        "module": "warehouse",
        "label": "تحويل المخزون",
        "description": "صلاحية تحويل الأصناف بين المستودعات والموافقة على التحويلات",
    },
}
