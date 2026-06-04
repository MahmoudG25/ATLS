# Back-End/permissions/registry/__init__.py

from .hr import PERMISSIONS as hr_perms
from .warehouse import PERMISSIONS as wh_perms
from .reports import PERMISSIONS as rep_perms
from .accounting import PERMISSIONS as acc_perms
from .governance import PERMISSIONS as gov_perms

# Combine all registries
PERMISSIONS = {}
for registry in [hr_perms, wh_perms, rep_perms, acc_perms, gov_perms]:
    PERMISSIONS.update(registry)

def get_permission_codes():
    return list(PERMISSIONS.keys())

def get_permission_details():
    return [
        {"code": code, "name": info["label"], "description": info["description"]}
        for code, info in PERMISSIONS.items()
    ]

# Registry validation check
def validate_registry():
    seen_codes = set()
    VALID_MODULES = {"reports", "farm", "palm", "olive", "production", "accounting", "hr", "equipment", "bulletin", "warehouse"}
    
    # 1. Check HR
    for code, info in hr_perms.items():
        if code in seen_codes:
            raise ValueError(f"Duplicate permission code detected: {code}")
        seen_codes.add(code)
        if not info.get("module") or not info.get("label") or not info.get("description"):
            raise ValueError(f"Malformed definition for permission: {code}")
        if info["module"] not in VALID_MODULES:
            raise ValueError(f"Invalid module mapping for permission: {code}")

    # 2. Check Warehouse
    for code, info in wh_perms.items():
        if code in seen_codes:
            raise ValueError(f"Duplicate permission code detected: {code}")
        seen_codes.add(code)
        if not info.get("module") or not info.get("label") or not info.get("description"):
            raise ValueError(f"Malformed definition for permission: {code}")
        if info["module"] not in VALID_MODULES:
            raise ValueError(f"Invalid module mapping for permission: {code}")

    # 3. Check Reports
    for code, info in rep_perms.items():
        if code in seen_codes:
            raise ValueError(f"Duplicate permission code detected: {code}")
        seen_codes.add(code)
        if not info.get("module") or not info.get("label") or not info.get("description"):
            raise ValueError(f"Malformed definition for permission: {code}")
        if info["module"] not in VALID_MODULES:
            raise ValueError(f"Invalid module mapping for permission: {code}")

    # 4. Check Accounting
    for code, info in acc_perms.items():
        if code in seen_codes:
            raise ValueError(f"Duplicate permission code detected: {code}")
        seen_codes.add(code)
        if not info.get("module") or not info.get("label") or not info.get("description"):
            raise ValueError(f"Malformed definition for permission: {code}")
        if info["module"] not in VALID_MODULES:
            raise ValueError(f"Invalid module mapping for permission: {code}")

    # 5. Check Governance
    for code, info in gov_perms.items():
        if code in seen_codes:
            raise ValueError(f"Duplicate permission code detected: {code}")
        seen_codes.add(code)
        if not info.get("module") or not info.get("label") or not info.get("description"):
            raise ValueError(f"Malformed definition for permission: {code}")
        if info["module"] not in VALID_MODULES:
            raise ValueError(f"Invalid module mapping for permission: {code}")

# Run validation on startup
validate_registry()
