# ATLS — Step 4 Validation Checklist

**Status**: Ready to Validate  
**Time to Complete**: 30-45 minutes  
**Prepared**: May 14, 2026

---

## ✅ Pre-Validation Checklist

Before running the validation tests, verify these prerequisites:

### Database Setup
- [ ] PostgreSQL is running (default: localhost:5432)
- [ ] Database `erp_db` exists with credentials:
  - Username: `postgres`
  - Password: `123`
- [ ] Admin user exists and is approved:
  ```sql
  UPDATE users_user SET is_approved = true WHERE email = 'admin@example.com';
  ```

### Backend Environment
- [ ] Virtual environment created: `python -m venv venv`
- [ ] Virtual environment activated: `venv\Scripts\activate.bat`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Django server can start: `python manage.py runserver`
- [ ] Database migrations applied: `python manage.py migrate --check`

### Files Ready
- [ ] `Back-End/validate_step4.py` exists (main test runner)
- [ ] `Back-End/start_server.bat` exists (server launcher)
- [ ] `.env` file configured with correct credentials
- [ ] `Back-End/manage.py` exists (Django project root)

---

## 🚀 Validation Steps

### Step 1: Start the Backend Server

```bash
cd e:\web\project------------\ATLS-V2\Back-End
start_server.bat
```

**Wait for**:
```
Starting development server at http://0.0.0.0:8000/
```

**Do NOT proceed until you see this message.**

---

### Step 2: Run the Validation Tests

**In a NEW terminal** (leave backend running):

```bash
cd e:\web\project------------\ATLS-V2\Back-End
venv\Scripts\activate.bat
python validate_step4.py
```

**This will automatically test:**
- ✓ Database state verification
- ✓ Authentication (login endpoint)
- ✓ Farm CRUD operations
- ✓ Tenant isolation (SECURITY CHECK)
- ✓ LocationNode hierarchy
- ✓ Reports workflow
- ✓ Data relationships

---

### Step 3: Review Test Results

#### If all tests PASS ✅

You should see:
```
✅ VALIDATION PASSED
Step 4 workflow is operational. Ready for Step 5 expansion.
```

**Celebrate!** Then proceed to Step 5 (Production Quality Expansion).

**What to do next**:
1. Update `CURRENT_PROGRESS.md` with test results
2. Begin Step 5 work (pagination, search, mobile UI)
3. Document any improvements needed

#### If tests FAIL ❌

You should see:
```
❌ VALIDATION FAILED
Blocking failures detected. Fix these before proceeding to Step 5.
```

**Then**:
1. Identify which test failed (script shows details)
2. Use the troubleshooting guide below
3. Fix the issue
4. Re-run `python validate_step4.py`
5. Repeat until all tests pass

---

## 🔧 Troubleshooting

### Test: "Backend server is running"
**Fails with**: `Cannot connect to http://localhost:8000`

**Fix**:
```bash
# In Terminal 1:
cd e:\web\project------------\ATLS-V2\Back-End
start_server.bat
```

Wait for the "Starting development server..." message before proceeding.

---

### Test: "Admin user exists"
**Fails with**: `Admin user not found`

**Option 1 — Approve existing user**:
```sql
UPDATE users_user SET is_approved = true WHERE email = 'admin@example.com';
```

**Option 2 — Create and approve new user**:
```bash
cd e:\web\project------------\ATLS-V2\Back-End
python manage.py shell

# In Django shell:
from apps.users.models import User, Company
company = Company.objects.first()  # Use first company
user = User.objects.create_user(
    email='admin@example.com',
    password='admin',
    full_name='Admin User',
    company=company,
    is_approved=True
)
exit()
```

---

### Test: "Login endpoint returns 200"
**Fails with**: `Status: 401` or `Status: 403`

**Fix**:
1. Verify admin user is approved (see above)
2. Verify credentials in test:
   - Email: `admin@example.com`
   - Password: `admin`
3. If using different credentials, edit `validate_step4.py`:
   ```python
   TEST_EMAIL = "your-email@example.com"
   TEST_PASSWORD = "your-password"
   ```

---

### Test: "Farm list respects tenant isolation" ⚠️
**Fails with**: `FAIL | Farm list respects tenant isolation (BLOCKING)`

**This is a SECURITY ISSUE**

**Problem**: Users can see farms from other companies

**Fix**:
1. Edit `Back-End/services/farm_service.py`
2. Find `def list_farms(...)` function
3. Add tenant filter:
   ```python
   def list_farms(request, **kwargs):
       # Filter by user's company
       return Farm.objects.filter(company=request.user.company)
   ```
4. Save and restart server
5. Re-run validation

**Verify by checking**:
```python
# In Django shell:
python manage.py shell

from apps.users.models import User
from apps.farm.models import Farm

admin = User.objects.get(email='admin@example.com')
admin_farms = Farm.objects.filter(company=admin.company)
print(f"Admin can see {admin_farms.count()} farms (all should be company {admin.company_id})")
```

---

### Test: "Reports returns 200"
**Fails with**: `Status: 500` (server error)

**Fix**:
1. Check Django console for error message
2. Likely issue: Serializer error in `serializers/reports_serializers.py`
3. Common fixes:
   - Verify model relationships are correct
   - Check for missing fields in serializer
   - Ensure database schema is up to date: `python manage.py migrate`
4. Re-run validation after fix

---

### General: Database Connection Error
**Fails with**: `could not connect to server: No such file or directory`

**PostgreSQL not running**

**Fix**:
```bash
# Windows: Start PostgreSQL service
net start postgresql-x64-16

# Or using Docker:
docker run -d --name postgres -e POSTGRES_PASSWORD=123 -p 5432:5432 postgres:16
```

---

### General: "ModuleNotFoundError: No module named..."
**Fails with**: Python import error

**Dependencies not installed**

**Fix**:
```bash
cd e:\web\project------------\ATLS-V2\Back-End
venv\Scripts\activate.bat
pip install -r requirements.txt
python validate_step4.py
```

---

## 📊 Test Results Template

Copy this template and fill in your results:

```
VALIDATION TEST RESULTS
=======================
Date: [FILL IN]
Tester: [FILL IN]
Environment: Windows, PostgreSQL 16, Python 3.10+

Phase 1 - Database State:        [PASS/FAIL]
Phase 2 - Authentication:        [PASS/FAIL]
Phase 3 - Farm CRUD:             [PASS/FAIL]
Phase 4 - Hierarchy:             [PASS/FAIL]
Phase 5 - Reports:               [PASS/FAIL]
Phase 6 - Data Integrity:        [PASS/FAIL]

Overall Result:                  [PASS/FAIL]

Issues Found:
- [Issue 1]
- [Issue 2]

Fixed:
- [Fix 1]
- [Fix 2]

Ready for Step 5:                [YES/NO]
```

---

## 📱 Optional: Also Test Frontend

If you want to test the frontend UI as well:

```bash
# Terminal 1: Backend (already running)
# (From Step 1 above)

# Terminal 2: Frontend
cd e:\web\project------------\ATLS-V2\Front-End
npm install  # If not already done
npm run dev

# Then open http://localhost:5173 in your browser
# Try to login with admin@example.com / admin
```

**Frontend checks**:
- [ ] Login page loads
- [ ] Can enter credentials
- [ ] Can submit form
- [ ] Redirected to dashboard
- [ ] Farm Structure page loads
- [ ] Can view/edit farm hierarchy

---

## ✨ Success Indicators

### All Tests PASS ✅
```
✓ Server starts without errors
✓ Login returns JWT tokens
✓ Farm list returns only user's company farms (SECURITY CHECK)
✓ LocationNode hierarchy accessible
✓ Reports CRUD functional
✓ All 6 validation phases complete
```

**Action**: Update CURRENT_PROGRESS.md and proceed to Step 5

### Some Tests FAIL ❌
```
✗ One or more blocking tests failed
✗ Server logs show errors
✗ API returns 401, 403, or 500 status codes
✗ Database connectivity issues
```

**Action**: Use troubleshooting guide above, fix issue, re-run tests

---

## 📋 Documentation Files

If you need more details on any part of validation:

| Document | Purpose | Time |
|----------|---------|------|
| **START_HERE.md** | Overview and navigation | 2 min |
| **TESTING_README.md** | How to run tests + FAQ | 7 min |
| **VALIDATION_PLAN.md** | Detailed test procedures | 15 min |
| **STEP4_VALIDATION_SUMMARY.md** | Architecture & history | 10 min |
| **This checklist** | Step-by-step guide | 5 min |

---

## 🎯 Quick Decision Tree

```
Q: Are you ready to validate Step 4?
├─ YES, let's go!
│  ├─ Check prerequisites above ✓
│  ├─ Run start_server.bat ✓
│  ├─ Run python validate_step4.py ✓
│  └─ Review results ✓
│
└─ NO, I need to prepare
   ├─ Database not running? → Start PostgreSQL
   ├─ Admin user not approved? → Run SQL to approve
   ├─ Environment not set up? → Create venv and install deps
   └─ Need more info? → Read TESTING_README.md
```

---

## 🚨 Critical Path to Step 5

1. ✅ Backend starts → `start_server.bat`
2. ✅ Tests run → `python validate_step4.py`
3. ✅ All tests PASS → Ready for Step 5
4. ✅ IF FAIL: Fix + re-test until PASS
5. ✅ Update CURRENT_PROGRESS.md
6. ✅ Begin Step 5 work

**Estimated Time**: 30-45 minutes (if no issues)

---

## 📞 Common Questions

**Q: How do I know if I'm ready to test?**
A: Check all items in the "Pre-Validation Checklist" above.

**Q: What if the script keeps failing?**
A: Check troubleshooting guide above for your specific error.

**Q: Can I skip the validation and go to Step 5?**
A: **NO**. Validation ensures Step 4 is working. Skip this and Step 5 will break.

**Q: What if I can't fix an issue?**
A: Document the exact error and note it in CURRENT_PROGRESS.md. Note the blocker for the next session.

**Q: How long until Step 5 starts?**
A: After validation passes. Then begins production-quality expansion (pagination, search, mobile UI).

---

## ✅ Final Checklist

Before starting, verify:

- [ ] Read this entire document
- [ ] All prerequisites checked and ready
- [ ] PostgreSQL is running
- [ ] Admin user is approved
- [ ] Backend venv activated
- [ ] Ready to open 2 terminals (one for server, one for tests)

**When ready**: Run `start_server.bat` and `python validate_step4.py`

---

**Status**: Ready for validation  
**Next Action**: Follow steps above  
**Success Indicator**: All tests pass or clear blockers documented

**Good luck!** 🎯
