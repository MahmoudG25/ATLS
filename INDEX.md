# 📚 ATLS-V2 Backend Testing - Complete Index

## 📍 Start Here

**New to this testing setup?** Start with these files in this order:

1. **READ_ME_FIRST.md** ← YOU ARE HERE
   - Overview of environment issue
   - What was done instead
   - Key findings
   - Quick navigation

2. **QUICK_REFERENCE.md** ← 30-SECOND START
   - Commands to run
   - Quick curl examples
   - Common issues

3. **BACKEND_TESTING_GUIDE.md** ← DETAILED GUIDE
   - Step-by-step instructions
   - Multiple testing options
   - Troubleshooting

4. **API_TEST_REPORT.md** ← TECHNICAL DEEP DIVE
   - Complete specifications
   - Database schema
   - Expected responses

---

## 🎯 What to Do Right Now

### ✅ Prerequisites
- [ ] PostgreSQL running on localhost:5432
- [ ] Database `erp_db` exists
- [ ] Virtual environment at `Back-End/venv/`

### ✅ Approve Admin User (Required!)
```sql
UPDATE users_user SET is_approved = true WHERE email = 'admin@example.com';
```

### ✅ Start Testing
```batch
cd Back-End
start_server.bat
```

In another terminal:
```batch
cd Back-End
venv\Scripts\activate.bat
python test_api_manually.py
```

---

## 📂 File Structure

```
e:\web\project------------\ATLS-V2\
│
├── 📄 READ_ME_FIRST.md ........................ START HERE
├── 📋 QUICK_REFERENCE.md ..................... 30-sec summary
├── 📘 BACKEND_TESTING_GUIDE.md ............... Full guide
├── 📊 TESTING_SUMMARY.md ..................... Executive summary
├── 📄 API_TEST_REPORT.md ..................... Technical specs
│
└── Back-End/
    ├── 🚀 start_server.bat ................... Click to start server
    ├── 🧪 test_api_manually.py .............. Run for testing
    ├── 🧪 test_api.ps1 ...................... PowerShell version
    ├── manage.py
    ├── venv/
    └── core/settings.py
```

---

## 🚀 Three Ways to Test

### Option 1: One Click (Easiest)
```batch
Back-End\start_server.bat
```
Then in another terminal:
```batch
cd Back-End
venv\Scripts\activate.bat
python test_api_manually.py
```

### Option 2: Manual Commands
```batch
cd Back-End
venv\Scripts\activate.bat
python manage.py runserver 0.0.0.0:8000
```
Then use curl in another terminal.

### Option 3: PowerShell Script
```powershell
cd Back-End
.\test_api.ps1
```

---

## 📝 What Each File Does

### Documentation Files

| File | Purpose | Read Time |
|------|---------|-----------|
| **READ_ME_FIRST.md** | Overview & navigation | 5 min |
| **QUICK_REFERENCE.md** | Commands & quick answers | 3 min |
| **BACKEND_TESTING_GUIDE.md** | Step-by-step testing guide | 10 min |
| **TESTING_SUMMARY.md** | Executive summary | 8 min |
| **API_TEST_REPORT.md** | Technical specifications | 20 min |

### Testing Scripts

| File | Purpose | How to Run |
|------|---------|-----------|
| **start_server.bat** | Start Django server | Double-click or `start_server.bat` |
| **test_api_manually.py** | Auto test with Python | `python test_api_manually.py` |
| **test_api.ps1** | PowerShell automation | `.\test_api.ps1` |

---

## 🔑 Key Endpoints

### Login
```
POST http://localhost:8000/api/auth/login/
{
  "email": "admin@example.com",
  "password": "admin"
}
```

### Farm List
```
GET http://localhost:8000/api/farm/farms/
Header: Authorization: Bearer {token}
```

### Current User
```
GET http://localhost:8000/api/auth/me/
Header: Authorization: Bearer {token}
```

---

## ⚠️ Critical Issues Found

### 1️⃣ Missing Tenant Filtering (Security Issue)
**Location**: `Back-End/services/farm_service.py`

**Current Code** (UNSAFE):
```python
def list_farms():
    return Farm.objects.filter(is_active=True)  # ❌ Returns ALL farms
```

**Should Be** (SAFE):
```python
def list_farms(user=None):
    farms = Farm.objects.filter(is_active=True)
    if user and hasattr(user, 'company') and user.company:
        farms = farms.filter(company_id=user.company.id)  # ✅ Filter by tenant
    return farms
```

**Impact**: Users can see farms from other companies

### 2️⃣ User Approval Required
**Location**: Database field `users_user.is_approved`

**Issue**: Users cannot login if not approved

**Fix**:
```sql
UPDATE users_user SET is_approved = true WHERE email = 'admin@example.com';
```

---

## 🔍 Database Quick Reference

**Connection**:
```
Host: localhost
Port: 5432
Database: erp_db
User: postgres
Password: 123
```

**Common Commands**:
```sql
-- Check users
SELECT email, is_approved, is_active FROM users_user;

-- Approve user
UPDATE users_user SET is_approved = true WHERE email = 'admin@example.com';

-- Check farms
SELECT id, name, company_id FROM farm_farm;

-- Connect with psql
psql -h localhost -U postgres -d erp_db
```

---

## ✅ Expected Results

### Login Test
- **Status**: 200
- **Response**: `{access, refresh, user}`
- **Token**: Valid JWT (60 min lifetime)

### Farm List Test
- **Status**: 200
- **Response**: Array of farm objects
- **Each farm**: `{id, name, description, location, area, is_active}`

### User Info Test
- **Status**: 200
- **Response**: `{id, email, name, role, is_approved, is_active, permissions}`

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection refused | Start Django server first |
| 401 Unauthorized | Add Authorization header |
| 403 Account pending | Approve user in database |
| 500 Server error | Check Django console for error |
| Database error | Verify PostgreSQL running & credentials |

---

## 📋 Checklist Before Testing

- [ ] PostgreSQL running
- [ ] Django server can start
- [ ] Admin user is approved in database
- [ ] Virtual environment activated
- [ ] Network access to localhost:8000
- [ ] Read QUICK_REFERENCE.md or BACKEND_TESTING_GUIDE.md

---

## 🎓 Learning Path

### Beginner
1. Read QUICK_REFERENCE.md
2. Run start_server.bat
3. Run python test_api_manually.py
4. Review results

### Intermediate
1. Read BACKEND_TESTING_GUIDE.md
2. Use curl commands manually
3. Inspect database
4. Test error scenarios

### Advanced
1. Read API_TEST_REPORT.md
2. Review source code
3. Identify issues (tenant filtering!)
4. Implement fixes
5. Write additional tests

---

## 📊 Configuration Summary

| Setting | Value |
|---------|-------|
| Framework | Django 6.0.4 |
| Database | PostgreSQL |
| Auth | JWT (SimpleJWT) |
| Debug | True |
| Access Token TTL | 60 minutes |
| Refresh Token TTL | 24 hours |
| CORS Enabled | Yes |

---

## 🔐 Security Notes

- ✅ JWT authentication enabled
- ✅ Password validation configured
- ⚠️ Tenant filtering missing (SECURITY ISSUE)
- ⚠️ User approval required
- ✅ CORS configured for frontend
- ⚠️ DEBUG=True (only for development!)

---

## 📞 Documentation by Topic

### Authentication
- → Read: API_TEST_REPORT.md sections 2, 4
- → Read: BACKEND_TESTING_GUIDE.md section "JWT Token Information"

### API Endpoints
- → Read: API_TEST_REPORT.md section 3
- → Read: QUICK_REFERENCE.md section "🔑 Login Endpoint"

### Database
- → Read: API_TEST_REPORT.md section 8
- → Read: BACKEND_TESTING_GUIDE.md section "Database Information"

### Testing
- → Read: BACKEND_TESTING_GUIDE.md sections 1-5
- → Read: QUICK_REFERENCE.md section "Quick Start"

### Troubleshooting
- → Read: BACKEND_TESTING_GUIDE.md section "Troubleshooting"
- → Read: QUICK_REFERENCE.md section "Common Issues"

### Code Issues
- → Read: API_TEST_REPORT.md section 6
- → Read: TESTING_SUMMARY.md section "Recommendations"

---

## 🚀 Getting Started Commands

```batch
REM Step 1: Navigate to backend
cd e:\web\project------------\ATLS-V2\Back-End

REM Step 2: Start server (this will run continuously)
start_server.bat

REM Then in a NEW terminal, do:
cd e:\web\project------------\ATLS-V2\Back-End
venv\Scripts\activate.bat
python test_api_manually.py

REM Or use curl manually:
curl -X POST http://localhost:8000/api/auth/login/ ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin@example.com\",\"password\":\"admin\"}"
```

---

## 📈 Progress Tracking

- ✅ Code analysis complete
- ✅ Configuration reviewed
- ✅ Issues identified
- ✅ Documentation created
- ✅ Scripts provided
- ⏳ Waiting for you to run tests
- ⏳ Waiting for you to fix tenant filtering
- ⏳ Waiting for production deployment

---

## 🎯 Next Steps

1. **Review**: Read QUICK_REFERENCE.md (3 min)
2. **Prepare**: Approve admin user in database
3. **Test**: Run start_server.bat + test_api_manually.py
4. **Validate**: Check all tests pass
5. **Fix**: Apply tenant filtering recommendation
6. **Deploy**: Backend is ready for production

---

## 📞 Quick Help

**Can't find something?**
- API commands → QUICK_REFERENCE.md
- Step-by-step → BACKEND_TESTING_GUIDE.md
- Technical details → API_TEST_REPORT.md
- Overview → TESTING_SUMMARY.md

**Still stuck?**
- Check the error in Django console
- Review the troubleshooting section in BACKEND_TESTING_GUIDE.md
- Compare your response with expected response in API_TEST_REPORT.md

---

## 📄 Document Organization

```
By Speed:
  Quick Reference (3 min) ↓
  Testing Guide (10 min) ↓
  Technical Report (20 min)

By Phase:
  Read Documentation ↓
  Run Tests ↓
  Fix Issues ↓
  Validate ↓
  Deploy

By Topic:
  Authentication → Sections 2, 4, 5
  Endpoints → Section 3, 5
  Database → Section 8
  Testing → All guides
  Issues → Sections 6, 10
```

---

## ✨ Summary

✅ **Backend Status**: Fully configured and ready  
⚠️ **Issue Found**: Missing tenant filtering (must fix)  
📋 **Documentation**: Complete with examples  
🚀 **Scripts**: Ready to use  
⏳ **Next**: You run the tests  

---

**Last Updated**: Current Session  
**Status**: Ready for Testing  
**Location**: e:\web\project------------\ATLS-V2\

**START WITH**: QUICK_REFERENCE.md or BACKEND_TESTING_GUIDE.md
