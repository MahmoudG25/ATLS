# Role & Permission Matrix (RBAC)

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ATLS-REF-ROL |
| **Status** | AUTHORITATIVE |
| **Version** | 2.0.0 |
| **Owner** | Security & Product Team |
| **Applicability** | Global Identity & Access Management |

## 1. Role Philosophy
Access control in ATLS follows the **Principle of Least Privilege (PoLP)**. Users are granted the minimum level of access required to perform their specific operational duties. In a multi-tenant agricultural environment, permission leaks are considered critical security failures.
- **Tenant-Locked**: Permissions are valid ONLY within the user's specific tenant context.
- **Task-Focused**: Roles are designed around physical farm operations (e.g., Harvesting, Spraying).
- **Audit-Linked**: Every permission check is traceable in the [AUDIT_DOMAIN.md].

## 2. RBAC Architecture
ATLS uses a standard **Role-Based Access Control (RBAC)** model:
- **Permission**: A discrete capability (e.g., `create:harvest_load`).
- **Role**: A collection of permissions (e.g., `Supervisor`).
- **Assignment**: Linking a User to one or more Roles within a specific Tenant.

## 3. Tenant Isolation Rules
- **No Global Scope**: Except for the `SuperAdmin`, all permissions MUST be checked against the `tenant_id`.
- **Validation**: Every API request must pass a "Tenant-Role Validator" that ensures the role is legitimate for that specific tenant.

## 4. Role Hierarchy
Roles follow a logical hierarchy, but permissions are **additive** rather than purely inherited to maintain strict security boundaries.

## 5. Super Admin Role (System Level)
- **Scope**: Platform-wide (Cross-tenant).
- **Access**: Full system configuration, tenant creation, and global audit logs.
- **Restriction**: Forbidden from viewing operational farm data (e.g., specific harvest weights) unless explicitly granted for debugging.

## 6. Tenant Admin Role (Account Level)
- **Scope**: Single Tenant.
- **Access**: Full management of the tenant's users, roles, and global settings.
- **Key Capability**: `manage:tenant_users`, `manage:tenant_billing`.

## 7. Farm Manager Role
- **Scope**: Single Tenant.
- **Access**: All operational domains (Farm, HR, Equipment, Inventory, Harvest).
- **Key Capability**: `approve:harvest`, `view:financial_reports`, `manage:farm_hierarchy`.

## 8. Supervisor Role
- **Scope**: Specific Farm/Block (Operational).
- **Access**: Operational journals, personnel assignments, and harvest verification.
- **Key Capability**: `verify:daily_journal`, `create:personnel_assignment`.

## 9. Field Worker Role
- **Scope**: Task-specific.
- **Access**: Personal task list, "Capture Evidence" tools.
- **Key Capability**: `submit:task_log`, `upload:media_evidence`.

## 10. Inventory Staff Role
- **Access**: Inventory movements, batch tracking, and warehouse logs.
- **Key Capability**: `record:stock_movement`, `manage:inventory_batches`.

## 11. Harvest Staff Role
- **Access**: Harvest load recording and quality checks.
- **Key Capability**: `create:harvest_load`, `record:quality_check`.

## 12. HR Staff Role
- **Access**: Personnel records, contracts, and payroll data.
- **Key Capability**: `manage:personnel_profiles`, `view:worker_payroll`.

## 13. Equipment Operator Role
- **Access**: Equipment logs and maintenance requests.
- **Key Capability**: `log:equipment_usage`, `create:maintenance_request`.

## 14. Auditor Role
- **Access**: Read-only access to all domains including Audit trails.
- **Key Capability**: `view:audit_logs`, `view:historical_records`.

## 15. Read-Only Analytics Role
- **Access**: Dashboard and reporting read models.
- **Key Capability**: `view:analytics_dashboard`, `export:reports`.

## 16. Guest/Temporary Role
- **Access**: Extremely limited (e.g., only viewing a specific public-facing load document).

## 17. Permission Naming Standards
- Format: `[action]:[entity]` (e.g., `view:personnel`, `delete:inventory_batch`).
- Actions: `view`, `create`, `update`, `delete`, `approve`, `export`, `verify`.

## 18. CRUD Permission Matrix
| Role | View | Create | Update | Delete |
| :--- | :---: | :---: | :---: | :---: |
| **Farm Manager** | ALL | ALL | ALL | ALL (Soft) |
| **Supervisor** | OWN | OWN | OWN | NONE |
| **Worker** | OWN | OWN | NONE | NONE |
| **Auditor** | ALL | NONE | NONE | NONE |

## 19. Approval Permission Matrix
- Only roles with `approve:[entity]` can transition a record to the `APPROVED` or `CLOSED` state.
- **Constraint**: A user cannot approve their own submitted report (Two-man rule for high-value items).

## 20. Media Permission Matrix
- `upload:media`: All operational roles.
- `delete:media`: Only `Farm Manager` or `Tenant Admin`.
- `view:private_media`: Requires `view:[parent_entity]` permission.

## 21. Notification Permission Matrix
- `receive:alerts`: Based on role-subscription.
- `broadcast:alert`: Only `Supervisor` or higher.

## 22. Audit Access Rules
- Access to the `AuditLog` is restricted to `SuperAdmin`, `TenantAdmin`, and `Auditor` roles.
- Standard users can only view the audit trail for entities they personally created.

## 23. Offline Permission Constraints
- Permissions are cached on the device during the last sync.
- **Rule**: If a permission expires or is revoked while offline, the next sync will reject the offline actions.

## 24. Dynamic Permission Expansion
- ATLS supports "Temporary Permissions" via the `RoleOverride` system (e.g., "Field Worker A acts as Supervisor for 8 hours").

## 25. Permission Inheritance Rules
- `Farm Manager` inherits all permissions from `Supervisor` and `Worker`.
- **FORBIDDEN**: Circular inheritance.

## 26. Role Override Rules
- Overrides must be approved by a `Farm Manager`.
- Overrides must have an `expiry_timestamp`.

## 27. Emergency Override Rules
- In critical scenarios (e.g., Safety breach), a `SuperAdmin` can grant immediate "All Access" to a local user. This action triggers a `SEV-1` security alert.

## 28. Forbidden Permission Escalations
- A user cannot grant themselves a role higher than their own current role.
- Forbid "Permission Stacking" where a user combines two roles to bypass the "Two-man rule."

## 29. AI Safety Rules
- **Global Access**: AI agents MUST NOT create roles or users with "Global Unrestricted Access."
- **Admin Bypass**: FORBID any hardcoded "Admin Bypass" or "Master Key" in the codebase.
- **Cross-Tenant**: FORBID any permission check that does not explicitly include the `tenant_id`.
- **Hidden Shortcuts**: FORBID creating `is_superuser` shortcuts in the UI or API.
- **Mutations**: FORBID any database mutation logic that does not check for a valid permission first.
- **Frontend-Only**: FORBID "Security through Obscurity" where the UI hides a button but the API endpoint remains unprotected.

## 30. Real Agricultural Permission Scenarios
- **Pesticide Management**: Only a user with `ChemicalHandler` certification (stored as a permission) can log a pesticide application.
- **Financial Closure**: Only the `Farm Manager` can "Close" a season, preventing any further data modification by supervisors.

## 31. Future Role Expansion
- **Vendor Role**: External suppliers viewing inventory needs.
- **Customer Role**: Large buyers viewing harvest quality reports for their specific loads.

## 32. Final Role Enforcement Checklist
- [ ] Every API endpoint has a `PermissionRequired` decorator.
- [ ] Tenant ID is verified for every role lookup.
- [ ] Role hierarchy is documented and non-circular.
- [ ] Approval permissions are restricted to supervisors/managers.
- [ ] Audit logs capture all permission changes.
- [ ] No frontend-only authorization.
- [ ] AI Safety rules are enforced in the codebase.
