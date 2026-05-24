# ATLS Step 4 Validation Guide

**Date**: May 14, 2026  
**Status**: Ready for Testing  
**Phase**: Step 4 — Validate Primary Workflow (Farm → LocationNode → Reports)

---

## Quick Start (3 Steps)

### 1. Start the Backend Server

```bash
cd "e:\web\project------------\ATLS-V2\Back-End"
start_server.bat
```

Expected output:
```
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

### 2. In a New Terminal, Run the Validation Script

```bash
cd "e:\web\project------------\ATLS-V2\Back-End"
venv\Scripts\activate.bat
python validate_step4.py
```

### 3. Review the Results

The script will test:
- ✅ Database state (admin user, farms, locations)
- ✅ Authentication (JWT login)
- ✅ Farm CRUD + tenant isolation (security check!)
- ✅ Hierarchy and LocationNodes
- ✅ Reports workflow
- ✅ Data relationships

---

## Prerequisites

Before running tests, ensure:

1. **PostgreSQL is running** on localhost:5432
2. **Database `erp_db` exists** with credentials from `.env`:
   ```
   DB_USER=postgres
   DB_PASSWORD=123
   DB_NAME=erp_db
   ```

3. **Admin user is set up and approved**:
   ```sql
   UPDATE users_user SET is_approved = true WHERE email = 'admin@example.com';
   ```

If the admin user doesn't exist yet:
```sql
INSERT INTO users_user (email, password, full_name, is_approved, is_active, role, created_at)
VALUES ('admin@example.com', 'admin_hashed_password', 'Admin User', true, true, 'ADMIN', NOW());
```

---

## What Gets Tested

| Phase | Tests | Status | Blocking |
|-------|-------|--------|----------|
| 1. Database | Admin user, company, farms, locations | Auto-detected | YES |
| 2. Auth | Login endpoint, JWT tokens | Automated | YES |
| 3. Farms | CRUD operations, tenant isolation | Automated | YES |
| 4. Hierarchy | LocationNode tree structure | Automated | NO |
| 5. Reports | Task reports workflow | Automated | YES |
| 6. Integrity | Data relationships | Automated | NO |

---

## Understanding Results

### ✅ PASS
If you see:
```
✅ VALIDATION PASSED
Step 4 workflow is operational. Ready for Step 5 expansion.
```

This means:
- Backend is working
- Authentication is functional
- Farm CRUD is operational
- Tenant isolation is enforced
- Reports workflow is ready
- **✅ Ready to proceed to Step 5**

### ❌ FAIL
If you see blocking failures, fix them:

#### Problem: "Backend server is running"
**Solution**: Start the server in a new terminal:
```bash
cd e:\web\project------------\ATLS-V2\Back-End
start_server.bat
```

#### Problem: "Login returns 401/403"
**Solution**: Admin user needs approval:
```sql
UPDATE users_user SET is_approved = true WHERE email = 'admin@example.com';
```

#### Problem: "Farm list respects tenant isolation" FAILS
**⚠️ SECURITY ISSUE** — User can see other companies' farms
**Solution**: Check `services/farm_service.py` → `list_farms()` must filter by tenant

#### Problem: "Reports returns 500"
**Solution**: Check Django error logs for serialization issues

---

## Manual Testing (Without Script)

If you prefer to test manually with curl:

### 1. Login
```bash
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
    "company": 1
  }
}
```

### 2. Get Current User (Verify Token)
```bash
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 3. List Farms
```bash
curl -X GET http://localhost:8000/api/farm/farms/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

**Check**: Do you only see farms from your company? ✅

### 4. Get Hierarchy
```bash
curl -X GET http://localhost:8000/api/farm/hierarchy/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 5. List Reports
```bash
curl -X GET http://localhost:8000/api/reports/tasks/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

---

## Troubleshooting

### Server won't start

**Error**: `ModuleNotFoundError: No module named 'django'`

**Fix**:
```bash
cd e:\web\project------------\ATLS-V2\Back-End
venv\Scripts\activate.bat
pip install -r requirements.txt
python manage.py runserver 0.0.0.0:8000
```

### Database connection error

**Error**: `could not connect to server: No such file or directory`

**Fix**: PostgreSQL is not running
```bash
# Windows: Start PostgreSQL service
net start postgresql-x64-16

# Or use Docker:
docker run -d --name postgres -e POSTGRES_PASSWORD=123 -p 5432:5432 postgres:16
```

### Admin user not found

**Error**: "Admin user exists: ✗ FAIL"

**Fix**: Create and approve admin user:
```bash
cd e:\web\project------------\ATLS-V2\Back-End
python manage.py shell

# In Django shell:
from apps.users.models import User, Company
company = Company.objects.first()  # or create one
user = User.objects.create_user(
    email='admin@example.com',
    password='admin',
    full_name='Admin',
    company=company,
    is_approved=True
)
exit()
```

### CORS error when testing from frontend

**Error**: "CORS policy: No 'Access-Control-Allow-Origin' header"

**Fix**: Check Django settings:
```python
# In Back-End/core/settings.py
CORS_ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
```

---

## Files Created/Used

| File | Purpose |
|------|---------|
| `validate_step4.py` | Main validation script (you're running this) |
| `start_server.bat` | One-click server startup |
| `VALIDATION_PLAN.md` | Detailed test plan |
| `.env` | Database credentials |

---

## Next Steps

### If PASS ✅

1. Update CURRENT_PROGRESS.md
2. Begin Step 5 (Production Quality Expansion):
   - Add pagination to Farm/Reports lists
   - Add search and filtering
   - Add mobile responsiveness
   - Improve error handling

### If FAIL ❌

1. Fix highest-priority blocking issues first
2. Re-run validation script
3. Iterate until all tests pass
4. Then proceed to Step 5

---

## Support

**Question**: Where are the test results recorded?
**Answer**: Run the script again to see results. Results are printed to console.

**Question**: Can I test the frontend now?
**Answer**: Yes! Start the frontend dev server:
```bash
cd e:\web\project------------\ATLS-V2\Front-End
npm run dev
```

Then open http://localhost:5173 and try logging in.

**Question**: What if I need to test just one endpoint?
**Answer**: Use curl commands above or modify `validate_step4.py` to test specific phase.

**Question**: Can I run tests against a production server?
**Answer**: Change `API_BASE` in `validate_step4.py` to your production URL. But do NOT test user credentials in production!

---

## Phase Summary

### ✅ Phases 1-3 (Complete)
- Monorepo setup
- Backend core (Django, DRF, JWT, PostgreSQL)
- Frontend core (React, Vite, routing, auth)

### 🔄 Phase 4 (This Validation)
- Backend: Farm CRUD + Reports (done)
- Frontend: Farm Structure page (70% done)
- **Current**: Validate end-to-end workflow

### ⏭️ Phase 5 (Next)
- Production quality expansion
- Pagination, search, mobile UI
- Enhanced error handling
- Performance optimization

---

**Document Version**: 1.0  
**Last Updated**: May 14, 2026  
**Maintained By**: AI Execution Protocol v1.0.0
