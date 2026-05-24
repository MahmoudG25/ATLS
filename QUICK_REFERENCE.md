# ATLS-V2 Backend API - Quick Reference Card

## 🚀 Quick Start (30 seconds)

### Terminal 1: Start Server
```batch
cd e:\web\project------------\ATLS-V2\Back-End
start_server.bat
```

### Terminal 2: Test API
```batch
cd e:\web\project------------\ATLS-V2\Back-End
venv\Scripts\activate.bat
python test_api_manually.py
```

---

## 🔑 Login Endpoint

**URL**: `POST http://localhost:8000/api/auth/login/`

**Request**:
```json
{
  "email": "admin@example.com",
  "password": "admin"
}
```

**Success Response (200)**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "admin@example.com",
    "name": "Admin",
    "role": "SUPER_ADMIN",
    "is_approved": true,
    "is_active": true
  }
}
```

**Common Errors**:
- **401**: `{"detail": "Invalid email or password."}`
- **403**: `{"detail": "Your account is pending approval."}`
- **403**: `{"detail": "Your account has been deactivated."}`

---

## 🌾 Farm List Endpoint

**URL**: `GET http://localhost:8000/api/farm/farms/`

**Headers**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Success Response (200)**:
```json
[
  {
    "id": 1,
    "name": "North Farm",
    "description": "...",
    "location": "...",
    "area": 150.5,
    "is_active": true
  }
]
```

**Common Errors**:
- **401**: `{"detail": "Invalid authentication credentials."}`

---

## 👤 Current User Endpoint

**URL**: `GET http://localhost:8000/api/auth/me/`

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response (200)**:
```json
{
  "id": 1,
  "email": "admin@example.com",
  "name": "Admin",
  "role": "SUPER_ADMIN",
  "is_approved": true,
  "is_active": true,
  "permissions": [],
  "last_login": "2024-...",
  "date_joined": "2024-..."
}
```

---

## 💾 Database Quick Reference

**Connection**:
```
Host: localhost
Port: 5432
Database: erp_db
User: postgres
Password: 123
```

**Approve Admin User**:
```sql
UPDATE users_user SET is_approved = true WHERE email = 'admin@example.com';
```

**Check User Status**:
```sql
SELECT email, is_approved, is_active, role FROM users_user;
```

**Connect with psql**:
```bash
psql -h localhost -U postgres -d erp_db
```

---

## 🔧 Manual Testing with curl

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin@example.com\",\"password\":\"admin\"}"
```

### Get Farms (replace TOKEN)
```bash
curl -X GET http://localhost:8000/api/farm/farms/ ^
  -H "Authorization: Bearer TOKEN"
```

### Get User Info
```bash
curl -X GET http://localhost:8000/api/auth/me/ ^
  -H "Authorization: Bearer TOKEN"
```

---

## 📋 Files Created

| File | Purpose |
|------|---------|
| `start_server.bat` | One-click Django server startup |
| `test_api_manually.py` | Automated API testing script |
| `test_api.ps1` | PowerShell testing script |
| `API_TEST_REPORT.md` | Technical documentation |
| `BACKEND_TESTING_GUIDE.md` | Step-by-step guide |
| `TESTING_SUMMARY.md` | Executive summary |

---

## ⚠️ Common Issues & Solutions

### Issue: Connection Refused on localhost:8000
**Solution**: Ensure Django server is running in another terminal

### Issue: 401 Authentication Error
**Solution**: Add Authorization header:
```bash
-H "Authorization: Bearer {token}"
```

### Issue: 403 Account Pending Approval
**Solution**: Approve user in database:
```sql
UPDATE users_user SET is_approved = true WHERE email = 'admin@example.com';
```

### Issue: Database Connection Failed
**Solution**: Verify PostgreSQL is running:
- Check Windows Services
- Verify `.env` credentials:
  - DB_HOST=localhost
  - DB_PORT=5432
  - DB_NAME=erp_db
  - DB_USER=postgres
  - DB_PASSWORD=123

### Issue: 500 Server Error
**Solution**: Check Django console for error stack trace

---

## 🔐 JWT Token Info

**Format**: `Bearer {token}`

**Token Lifetime**:
- Access: 60 minutes
- Refresh: 24 hours

**To Decode** (for debugging):
- Use https://jwt.io (view only)
- Never share tokens

---

## 📊 Expected Results

### ✅ Successful Login
- Status: 200
- Contains: access, refresh, user
- User: is_approved=true, is_active=true

### ✅ Successful Farm List
- Status: 200
- Response: Array of farm objects
- Each farm: id, name, description, location, area

### ✅ Successful User Info
- Status: 200
- Contains: id, email, name, role, permissions

---

## 🛠️ Configuration

**Backend Location**: `e:\web\project------------\ATLS-V2\Back-End`

**Django Settings**: `core/settings.py`

**Database**: PostgreSQL 12+

**Environment**: Development (DEBUG=True)

**Authentication**: JWT via SimpleJWT

---

## 📝 Testing Workflow

1. **Start Server**
   ```bash
   start_server.bat
   ```

2. **Run Tests**
   ```bash
   python test_api_manually.py
   ```

3. **Review Results**
   - Check status codes
   - Verify responses
   - Extract token

4. **Manual Testing** (optional)
   ```bash
   curl commands for specific endpoints
   ```

5. **Fix Issues**
   - Check database
   - Review error messages
   - Update credentials

---

## 🚨 Critical Checks

- [ ] PostgreSQL is running
- [ ] Django server starts without errors
- [ ] Admin user is approved in database
- [ ] Login returns 200 status with tokens
- [ ] Farm list returns 200 status with data
- [ ] JWT token is valid and not expired

---

## 📞 Resources

- **API_TEST_REPORT.md** - Detailed technical specs
- **BACKEND_TESTING_GUIDE.md** - Complete testing guide
- Django Docs: https://docs.djangoproject.com/
- DRF Docs: https://www.django-rest-framework.org/
- JWT Docs: https://django-rest-framework-simplejwt.readthedocs.io/

---

**Last Updated**: Current Session  
**Version**: 1.0  
**Status**: Ready for Testing
