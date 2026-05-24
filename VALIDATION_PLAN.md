# Step 4 Validation Plan — Farm + Reports Workflow

**Current Date**: May 14, 2026
**Phase**: Step 4 Validation (Primary Operational Workflow)
**Objective**: Validate Farm Structure and Daily Task Reports end-to-end

---

## Executive Summary

This document outlines the validation strategy for confirming that the **primary operational workflow** (Farm → LocationNode → Reports) works end-to-end.

Steps 1-3 are complete (Monorepo, Backend Core, Frontend Core). Step 4 backend is complete. Step 4 frontend is ~70% complete. **This validation will identify any blocking issues.**

---

## Test Scope

### ✅ In Scope — Must Validate

1. **Backend Availability**
   - [ ] Django dev server starts without errors
   - [ ] All dependencies load correctly
   - [ ] Database connection established

2. **Authentication Workflow**
   - [ ] POST /api/auth/login/ — returns JWT with valid access token
   - [ ] GET /api/auth/me/ — returns authenticated user details
   - [ ] Token refresh mechanism works

3. **Farm CRUD Operations**
   - [ ] GET /api/farm/farms/ — returns tenant-scoped farms (security check!)
   - [ ] POST /api/farm/farms/ — create new farm
   - [ ] GET /api/farm/hierarchy/ — returns LocationNode hierarchy
   - [ ] POST/PATCH /api/farm/location-nodes/ — CRUD operations on hierarchy

4. **Reports Workflow**
   - [ ] GET /api/reports/tasks/ — list daily task reports
   - [ ] POST /api/reports/tasks/ — create new task report
   - [ ] GET /api/reports/tasks/{id}/ — retrieve report details
   - [ ] Relationship verification: Report → Farm → LocationNode

5. **Frontend Rendering**
   - [ ] Login page loads and accepts credentials
   - [ ] Farm Structure page renders (if frontend server running)
   - [ ] Can navigate hierarchy tree
   - [ ] Can create/edit locations

6. **Tenant Isolation**
   - [ ] User only sees their company's farms
   - [ ] Reports filtered by tenant
   - [ ] No cross-tenant data leakage

### ❌ Out of Scope — Skip For Now

- Performance testing
- Load testing
- Mobile responsiveness
- Analytics accuracy
- Advanced filtering/search
- Offline functionality

---

## Test Procedure

### Phase 1: Backend Setup

```bash
cd e:\web\project------------\ATLS-V2\Back-End

# Activate venv
venv\Scripts\activate.bat

# Verify database
python manage.py migrate --check

# Start server
python manage.py runserver 0.0.0.0:8000
```

**Expected Output**:
```
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

### Phase 2: Authentication Test

```bash
# Login (assuming admin/test account exists and is approved)
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"admin@example.com\", \"password\": \"admin\"}"
```

**Expected Response** (Status 200):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "admin@example.com",
    "full_name": "Admin User",
    "role": "ADMIN",
    "is_approved": true,
    "company": {...}
  }
}
```

### Phase 3: Farm CRUD Test

```bash
# Get farms (using ACCESS token from login)
curl -X GET http://localhost:8000/api/farm/farms/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

**Expected Response** (Status 200):
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Farm Alpha",
      "company": 1,
      "...": "...more fields..."
    }
  ]
}
```

**CRITICAL CHECK**: Verify that only farms owned by the user's company are returned.

### Phase 4: Hierarchy Test

```bash
# Get location hierarchy
curl -X GET http://localhost:8000/api/farm/hierarchy/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

**Expected Response**:
```json
{
  "farms": [...],
  "location_nodes": [...],
  "structure": {...hierarchy tree...}
}
```

### Phase 5: Reports Workflow Test

```bash
# List reports
curl -X GET http://localhost:8000/api/reports/tasks/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"

# Create a report
curl -X POST http://localhost:8000/api/reports/tasks/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-05-14",
    "location_node": 1,
    "operations": [...],
    "notes": "..."
  }'
```

**Expected**: 200 OK with created report data

### Phase 6: Frontend Test (if applicable)

```bash
cd e:\web\project------------\ATLS-V2\Front-End
npm run dev

# Then open http://localhost:5173
# Verify:
# - Login page loads
# - Can submit login form
# - Redirects to dashboard
# - Farm Structure page renders
# - Can view/edit hierarchy
```

---

## Validation Matrix

| Test | Endpoint | Expected Status | Blocking |
|------|----------|-----------------|----------|
| Server starts | (Django) | 200 OK | YES |
| Login works | POST /auth/login | 200 OK | YES |
| Get user | GET /auth/me | 200 OK | YES |
| List farms | GET /farm/farms | 200 OK | YES |
| Get hierarchy | GET /farm/hierarchy | 200 OK | YES |
| List reports | GET /reports/tasks | 200 OK | YES |
| Create report | POST /reports/tasks | 201 CREATED | YES |
| Tenant isolation | (in farm list) | Correct data | YES |

---

## Possible Issues & Resolutions

### Issue 1: Server fails to start
**Symptoms**: `ModuleNotFoundError`, `ImproperlyConfigured`, database connection errors
**Resolution**: Run `pip install -r requirements.txt` in venv

### Issue 2: Login returns 401/403
**Symptoms**: "Invalid credentials" or "User not approved"
**Resolution**: Approve admin user in database:
```sql
UPDATE users_user SET is_approved = true WHERE email = 'admin@example.com';
```

### Issue 3: Farm list returns all farms (tenant isolation broken)
**Symptoms**: User sees farms from other companies
**Resolution**: Check `farm_service.py` `list_farms()` — must filter by `company=request.user.company`

### Issue 4: Reports endpoint returns 500
**Symptoms**: Server logs show serialization error
**Resolution**: Check `reports_serializers.py` — may have broken relationships

### Issue 5: Frontend doesn't connect to backend
**Symptoms**: CORS error in browser console
**Resolution**: Verify `.env.development` has correct API endpoint, check Django CORS settings

---

## Success Criteria

✅ **PASS** if ALL of the following are true:

1. Django server starts and responds to requests
2. Authentication workflow returns valid JWT tokens
3. Farm list endpoint returns tenant-scoped data (user's company only)
4. LocationNode CRUD operations work
5. Reports workflow allows create/read/list
6. No 500 errors in backend
7. No security violations (no cross-tenant data)
8. Frontend server starts (if testing UI)
9. Login page renders and accepts input
10. Farm Structure page loads

❌ **FAIL** if ANY of the following occur:

1. Backend server crashes on startup
2. Login endpoint returns error
3. Farm list returns cross-tenant data
4. Reports endpoints return 500 errors
5. Frontend cannot reach backend API
6. Authentication tokens are invalid/expired

---

## Next Steps After Validation

If PASS:
→ Begin Step 5 (Production Quality Expansion)
→ Add pagination, search, sorting to Farm/Reports UI
→ Add mobile responsiveness
→ Improve error handling and UX

If FAIL:
→ Document all failures as blockers
→ Fix highest-priority issues first
→ Re-run validation after each fix
→ Do NOT proceed to Step 5 until Step 4 is fully validated

---

## Testing Execution Log

**Start Time**: [Will be filled during testing]

### Test Results

```
Backend Server:        [ ] PASS [ ] FAIL
Authentication:        [ ] PASS [ ] FAIL
Farm CRUD:             [ ] PASS [ ] FAIL
Hierarchy:             [ ] PASS [ ] FAIL
Reports Workflow:      [ ] PASS [ ] FAIL
Tenant Isolation:      [ ] PASS [ ] FAIL
Frontend (if testing): [ ] PASS [ ] FAIL

Overall: [ ] PASS [ ] FAIL
```

**End Time**: [Will be filled after testing]

---

## Appendix — Database State Verification

Before testing, verify database state:

```sql
-- Check if admin user exists and is approved
SELECT id, email, is_approved, role FROM users_user WHERE email LIKE 'admin%';

-- Check if any farms exist
SELECT id, name, company_id FROM apps_farm_farm LIMIT 5;

-- Check if any location nodes exist
SELECT id, name, farm_id FROM apps_farm_locationnode LIMIT 5;

-- Check tenant isolation: list all companies
SELECT id, name FROM users_company;
```

---

## Appendix — Endpoint Reference

| Module | Endpoint | Method | Purpose |
|--------|----------|--------|---------|
| Auth | /api/auth/login | POST | Authenticate user |
| Auth | /api/auth/me | GET | Get current user |
| Farm | /api/farm/farms | GET | List farms |
| Farm | /api/farm/farms | POST | Create farm |
| Farm | /api/farm/hierarchy | GET | Get hierarchy tree |
| Farm | /api/farm/location-nodes | GET | List nodes |
| Farm | /api/farm/location-nodes | POST | Create node |
| Reports | /api/reports/tasks | GET | List reports |
| Reports | /api/reports/tasks | POST | Create report |
| Reports | /api/reports/tasks/{id} | GET | Get report |

---

**Document Version**: 1.0
**Status**: Ready for Execution
**Maintained By**: AI Execution Protocol v1.0.0
