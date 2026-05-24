# ATLS Step 4 Validation — Getting Started

**Last Updated**: May 14, 2026  
**Status**: Validation Framework Ready  
**Time to Complete**: 30 minutes

---

## 📍 You Are Here

You're at the end of **Step 4 (Primary Workflow)** implementation.

- ✅ **Backend**: Complete (Farm CRUD, Reports, Auth)
- ✅ **Frontend**: ~70% complete (Farm Structure page mostly done)
- 🔄 **NOW**: Validate that everything works together end-to-end

---

## 🚀 Quick Start (3 Commands)

### Option A: Interactive Menu (Easiest)
```bash
cd e:\web\project------------\ATLS-V2\Back-End
run_validation.bat
```

This opens a menu where you can:
- Start backend server
- Prepare database (create test data)
- Run validation tests
- View documentation

### Option B: Manual Steps (3 Commands)

#### 1️⃣ Start the Backend Server
```bash
cd e:\web\project------------\ATLS-V2\Back-End
start_server.bat
```

**Wait for**: `Starting development server at http://0.0.0.0:8000/`

#### 2️⃣ In a New Terminal, Prepare Database (if needed)
```bash
cd e:\web\project------------\ATLS-V2\Back-End
venv\Scripts\activate.bat
python prepare_test_data.py
```

This creates test company, admin user, farms, and locations if missing.

#### 3️⃣ Run Tests
```bash
cd e:\web\project------------\ATLS-V2\Back-End
venv\Scripts\activate.bat
python validate_step4.py
```

### 4️⃣ Review Results
- ✅ **PASS**: Ready to proceed to Step 5
- ❌ **FAIL**: Fix issues using guide below

---

## 📚 Documentation

### Start Here 👇

1. **[TESTING_README.md](TESTING_README.md)** — Quick-start guide (7 min read)
   - How to run tests
   - What gets tested
   - Troubleshooting

2. **[STEP4_VALIDATION_SUMMARY.md](STEP4_VALIDATION_SUMMARY.md)** — Executive summary (10 min read)
   - What we built
   - How validation works
   - What comes next

3. **[VALIDATION_PLAN.md](VALIDATION_PLAN.md)** — Detailed test plan (technical reference)
   - Test procedures
   - Expected responses
   - Success criteria

---

## 🎯 What Gets Tested

```
✅ Phase 1: Database state (admin user, farms, locations)
✅ Phase 2: Authentication (JWT login works)
✅ Phase 3: Farm CRUD + tenant isolation (SECURITY CHECK)
✅ Phase 4: Hierarchy and location nodes
✅ Phase 5: Reports workflow
✅ Phase 6: Data relationships and integrity
```

---

## ⚡ Prerequisites

Before testing, verify:

- [ ] PostgreSQL running on localhost:5432
- [ ] Database `erp_db` exists
- [ ] Admin user is approved: `UPDATE users_user SET is_approved = true WHERE email = 'admin@example.com';`
- [ ] Virtual environment setup: `venv\Scripts\activate.bat`

---

## 🔧 If Something Breaks

### "Backend server is running" ❌
→ Start server: `start_server.bat`

### "Admin user exists" ❌
→ Approve user:
```sql
UPDATE users_user SET is_approved = true WHERE email = 'admin@example.com';
```

### "Farm list respects tenant isolation" ❌ ⚠️
→ **SECURITY ISSUE** — See `TESTING_README.md` section "Troubleshooting"

### Other errors
→ See **Troubleshooting** section in `TESTING_README.md`

---

## 📋 Files You'll Need

| File | What It Does |
|------|--------------|
| `Back-End/validate_step4.py` | Main test runner (run this!) |
| `Back-End/start_server.bat` | Starts Django dev server |
| `TESTING_README.md` | How to run tests + troubleshooting |
| `STEP4_VALIDATION_SUMMARY.md` | What we built + architecture |
| `VALIDATION_PLAN.md` | Detailed test procedures |

---

## 📊 Expected Outcomes

### ✅ If Tests PASS
```
✅ VALIDATION PASSED
Step 4 workflow is operational. Ready for Step 5 expansion.
```

**Next Steps**:
1. Update CURRENT_PROGRESS.md
2. Begin Step 5 (pagination, search, mobile UI)
3. Continue implementation

### ❌ If Tests FAIL
```
❌ VALIDATION FAILED
Blocking failures detected. Fix these before proceeding to Step 5.
```

**Next Steps**:
1. Fix failures (detailed guide in TESTING_README.md)
2. Re-run `python validate_step4.py`
3. Continue iterating until all pass

---

## 📱 Testing Both Backend & Frontend

### Backend Only (3 min)
```bash
# Terminal 1
cd Back-End && start_server.bat

# Terminal 2
cd Back-End && venv\Scripts\activate.bat && python validate_step4.py
```

### Backend + Frontend (10 min)
```bash
# Terminal 1: Backend
cd Back-End && start_server.bat

# Terminal 2: Frontend
cd Front-End && npm run dev

# Terminal 3: Tests
cd Back-End && venv\Scripts\activate.bat && python validate_step4.py

# Then open http://localhost:5173 and test login
```

---

## ⏱️ Timeline

- **2026-05-14 22:30**: Session started, codebase audited
- **2026-05-14 23:00**: Validation framework created (NOW)
- **TBD**: You run tests and review results
- **TBD**: Fix any failures (if needed)
- **TBD**: Step 4 complete, proceed to Step 5

---

## 🔐 Security Note

⚠️ **CRITICAL**: One test checks **tenant isolation** (can users see other companies' data?).

If this test FAILS: **DO NOT PROCEED TO PRODUCTION**

This is a security vulnerability and must be fixed immediately.

---

## 📖 What is ATLS?

ATLS is an enterprise ERP platform for agricultural operations, featuring:
- Farm structure management (Palm & Olive crops)
- Daily task reporting
- Employee management
- Accounting & invoicing
- Multi-tenant support (multiple companies)
- Mobile-responsive design
- Arabic/RTL support

This validation confirms the core workflow is operational.

---

## 🎓 Architecture at a Glance

```
┌─────────────────────────────────────┐
│         React Frontend (5173)        │
│  - Login, Dashboard, Farm Structure  │
└────────────┬────────────────────────┘
             │
             │ REST API calls
             ↓
┌─────────────────────────────────────┐
│      Django Backend (8000)           │
│  - Authentication (JWT)              │
│  - Farm CRUD Operations              │
│  - Reports & Analytics               │
│  - Multi-tenant isolation            │
└────────────┬────────────────────────┘
             │
             │ SQL queries
             ↓
┌─────────────────────────────────────┐
│     PostgreSQL Database (5432)       │
│  - Companies & Users                 │
│  - Farms & Locations                 │
│  - Reports & Tasks                   │
│  - HR & Accounting                   │
└─────────────────────────────────────┘
```

---

## ❓ FAQ

**Q: How long do tests take?**
A: 30-60 seconds

**Q: Can I run tests without starting the backend?**
A: No. Backend server must be running first.

**Q: What if I see a 500 error?**
A: Check Django console output. See troubleshooting guide in TESTING_README.md

**Q: Can I test just one endpoint?**
A: Yes, edit `validate_step4.py` to comment out unwanted phases.

**Q: What comes after Step 4?**
A: Step 5 — Production Quality Expansion (pagination, search, mobile responsiveness)

**Q: How do I know if I found a real bug?**
A: If a test FAILS, it's a real issue that needs fixing.

---

## 🚦 Ready to Start?

1. **Read**: `TESTING_README.md` (5 min)
2. **Run**: `start_server.bat` + `python validate_step4.py` (1 min)
3. **Review**: Test results (5 min)
4. **Next**: Fix issues or proceed to Step 5

---

## 📞 Need Help?

All common issues and solutions are documented in:
- **TESTING_README.md** — Troubleshooting section
- **VALIDATION_PLAN.md** — Detailed test procedures
- **STEP4_VALIDATION_SUMMARY.md** — Architecture overview

---

**Status**: 🟢 Ready to validate  
**Next Action**: Run validation tests  
**Estimated Time**: 30 minutes total

[👉 Continue with TESTING_README.md](TESTING_README.md)
