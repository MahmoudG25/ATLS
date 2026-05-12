# Security Governance & Infrastructure Protection

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ATLS-BACK-07 |
| **Status** | AUTHORITATIVE |
| **Version** | 2.0.0 |
| **Owner** | Security & Backend Team |
| **Applicability** | All ATLS Services & Infrastructure |

## 1. Security Philosophy
Security in ATLS is **Pervasive and Non-Negotiable**. We assume the perimeter is already breached and implement multiple layers of defense.
- **Defense in Depth**: Multiple overlapping security controls.
- **Least Privilege**: Users and services only have the minimum access necessary.
- **Visibility**: Everything must be logged and auditable.

## 2. Zero Trust Rules
- **Never Trust, Always Verify**: Every request, even internal service-to-service, must be authenticated and authorized.
- **Context-Aware**: Validation depends on user identity, tenant state, and resource sensitivity.
- **Encrypted Traffic**: All internal and external traffic must use TLS 1.3.

## 3. JWT Architecture
- **Stateless**: Use JWTs for identity propagation to avoid DB lookups on every request.
- **Signing**: Use `RS256` (Asymmetric) with periodic key rotation.
- **Claims**: Include `user_id`, `tenant_id`, and `roles`. **FORBID** sensitive data in JWT payloads.
- **Duration**: 15 minutes for access tokens.

## 4. Refresh Token Strategy
- **Rotation**: Issue a new refresh token on every refresh call.
- **Storage**: Store refresh tokens in a high-speed Redis store with an explicit "Revocation List".
- **Timeout**: 7 days (or until manual logout).

## 5. RBAC Rules
- **Roles**: Standard roles: `SystemAdmin`, `FarmManager`, `Supervisor`, `Worker`.
- **Permissions**: Fine-grained permissions (e.g., `can_verify_harvest`, `can_approve_payroll`).
- **Mapping**: Roles are collections of permissions. Do not hardcode role checks; check permissions.

## 6. Permission Enforcement
- **Dual Check**: Enforcement happens at the API (DRF `permissions.py`) AND the Service layer.
- **Fail Closed**: If a permission check is missing, the request must fail with a `403 Forbidden`.

## 7. Tenant Isolation
- **Physical Boundary**: Use a separate DB schema or a mandatory `tenant_id` column on all tables.
- **Logic**: Every SQL query must include `WHERE tenant_id = current_tenant_id`.
- **Middleware**: Injects the active `tenant_id` into the thread local context.

## 8. API Security
- **Endpoints**: Hide internal admin endpoints behind a VPN or IP allow-list.
- **Headers**: Mandatory use of `HSTS`, `X-Content-Type-Options`, `X-Frame-Options`.
- **Versioning**: Only support the current and previous API versions.

## 9. Rate Limiting
- **Public**: Strict limits for Login, Register, and Password Reset (e.g., 5 requests/min per IP).
- **Authenticated**: Standard limits per user (e.g., 1000 requests/min).
- **Webhooks**: Validated via secret signatures to prevent DoS.

## 10. Upload Security
- **Scanning**: Every file must be scanned for malware before being moved to permanent storage.
- **MIME**: Enforce a strict allow-list. **FORBID** execution-capable types (`.exe`, `.php`, etc.).
- **Storage**: Files are stored in a private bucket accessible only via signed URLs.

## 11. Secret Management
- **Vault**: Use a dedicated secret manager (AWS Secrets Manager, HashiCorp Vault).
- **Environment**: Never commit secrets to Git. Use encrypted `.env` or CI/CD secrets.

## 12. Encryption Rules
- **At Rest**: Transparent Data Encryption (TDE) for all DB volumes and S3 buckets.
- **Application Level**: Sensitive PII (Social Security Numbers, Bank Accounts) must be encrypted using `AES-256-GCM` before saving to DB.

## 13. Audit Security
- **Immutability**: Audit logs must be append-only and sent to a separate, read-only logging cluster.
- **Retention**: 7 years of audit logs required for financial compliance.

## 14. Session Rules
- **Single Session**: (Optional) Allow only one active session per user to prevent account sharing.
- **Timeout**: Absolute session timeout after 24 hours of activity.

## 15. CSRF/CORS Governance
- **CORS**: Explicit allow-list of domains. No wildcards (`*`) in production.
- **CSRF**: Enforced for all non-safe HTTP methods (POST, PUT, DELETE) for browser clients.

## 16. Logging & Monitoring
- **Alerting**: Immediate alerts for multiple failed logins, unauthorized tenant access attempts, and abnormal API usage patterns.
- **PII**: Automatically mask PII (Emails, Phone numbers) in logs.

## 17. Incident Response
- **Lockdown**: Ability to globally revoke all JWTs or disable a specific tenant with one command.
- **Rotation**: Standard procedure for rotating all service secrets within 60 minutes of a breach.

## 18. Performance Constraints
- **Auth Overhead**: Authentication/Permission checks must add < 5ms to the request cycle.
- **JWT Parsing**: Use optimized libraries to minimize CPU overhead.

## 19. AI Safety Rules
- **Hardcoded**: AI agents MUST NOT hardcode any secrets, API keys, or private IPs in source code.
- **Public Admin**: FORBID exposing the Django `/admin/` or Swagger docs to the public internet.
- **Unsafe Uploads**: FORBID implementing file uploads without type validation and size limits.
- **Permissions**: FORBID creating new API endpoints without an explicit permission check.
- **Leaks**: FORBID cross-tenant data joins or leaks in ORM queries.

## 20. Forbidden Security Anti-Patterns
- **The Global Admin**: Using a single "Master DB User" for the application.
- **Plaintext Passwords**: Storing any password without Argon2/BCrypt hashing.
- **In-House Crypto**: Never implement custom encryption algorithms.
- **Verbose Errors**: Returning internal stack traces or DB errors to the API client.

## 21. Agricultural Scenarios
- **Worker Data**: Access to worker wage data is restricted to HR managers. Even the worker's supervisor can only see hours worked, not the rate.
- **Harvest Evidence**: Photos taken as quality evidence cannot be modified once uploaded.

## 22. Enforcement Checklist
- [ ] TLS 1.3 enforced.
- [ ] JWT keys rotated.
- [ ] Tenant manager active and tested for leaks.
- [ ] Rate limiting active for login/auth endpoints.
- [ ] No secrets in `settings.py` or `.env` in Git.
- [ ] File scan pipeline is active.
- [ ] Audit logs are flowing to the logging cluster.
- [ ] CORS is restricted to production domains.
- [ ] 2FA is mandatory for Admin roles.
- [ ] Pentest completed for this release cycle.
