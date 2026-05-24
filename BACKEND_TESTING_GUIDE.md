# ATLS-V2 Backend API Testing Guide

## Quick Start

### Option 1: Using Batch Script (Easiest)
```batch
cd e:\web\project------------\ATLS-V2\Back-End
start_server.bat
```

### Option 2: Using PowerShell Script
```powershell
cd e:\web\project------------\ATLS-V2\Back-End
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\test_api.ps1
```

### Option 3: Manual Testing

**Terminal 1 - Start Server:**
```batch
cd e:\web\project------------\ATLS-V2\Back-End
venv\Scripts\activate.bat
python manage.py runserver 0.0.0.0:8000
```

**Terminal 2 - Run Tests:**
```batch
cd e:\web\project------------\ATLS-V2\Back-End
venv\Scripts\activate.bat
python test_api_manually.py
```

---

## Manual Testing with curl

### 1. Test Login

```batch
curl -X POST http://localhost:8000/api/auth/login/ ^
  -H "Content-Type: application/json" ^
  -d "{\"email\": \"admin@example.com\", \"password\": \"admin\"}"
```

**Expected Response (Status 200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOjEsImlhdCI6MTcwOTk4NzY0OCwiZXhwIjoxNzA5OTkxMjQ4fQ.abcdef...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOjEsImlhdCI6MTcwOTk4NzY0OCwiZXhwIjoxNzA5OTk4ODQ4fQ.ghijkl...",
  "user": {
    "id": 1,
    "email": "admin@example.com",
    "name": "Admin User",
    "role": "SUPER_ADMIN",
    "is_approved": true,
    "is_active": true,
    "permissions": []
  }
}
```

**Error Responses:**
- **401 Unauthorized**: Invalid credentials
  ```json
  {"detail": "Invalid email or password."}
  ```
- **403 Forbidden**: Account not approved
  ```json
  {"detail": "Your account is pending approval."}
  ```
- **403 Forbidden**: Account deactivated
  ```json
  {"detail": "Your account has been deactivated."}
  ```

### 2. Test Farm List

**Copy the `access` token from login response, then:**

```batch
curl -X GET http://localhost:8000/api/farm/farms/ ^
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

**Expected Response (Status 200):**
```json
[
  {
    "id": 1,
    "name": "North Farm",
    "description": "Primary farming area",
    "location": "Northern Region",
    "area": 150.5,
    "is_active": true
  },
  {
    "id": 2,
    "name": "South Farm",
    "description": "Secondary farming area",
    "location": "Southern Region",
    "area": 120.0,
    "is_active": true
  }
]
```

**Error Responses:**
- **401 Unauthorized**: Missing or invalid token
  ```json
  {"detail": "Invalid authentication credentials."}
  ```

### 3. Test Current User Endpoint

```batch
curl -X GET http://localhost:8000/api/auth/me ^
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

## Database Information

### Connection Details
- **Host**: localhost
- **Port**: 5432
- **Database**: erp_db
- **User**: postgres
- **Password**: 123

### To Connect with psql:
```bash
psql -h localhost -U postgres -d erp_db
```

### Check User Approval Status:
```sql
SELECT id, email, name, role, is_approved, is_active FROM users_user;
```

### To Approve a User Manually:
```sql
UPDATE users_user SET is_approved = true WHERE email = 'admin@example.com';
```

---

## Troubleshooting

### Issue: "Failed to connect to localhost:8000"
**Solution**: Make sure Django server is running in another terminal

### Issue: "Authentication credentials were not provided"
**Solution**: Add Authorization header with token:
```bash
-H "Authorization: Bearer {access_token}"
```

### Issue: "Your account is pending approval"
**Solution**: Admin user needs to be approved in database:
```sql
UPDATE users_user SET is_approved = true WHERE email = 'admin@example.com';
```

### Issue: "Invalid email or password"
**Solution**: Verify credentials:
- Email: admin@example.com
- Password: admin
- Check database for user existence

### Issue: "Database connection refused"
**Solution**: Verify PostgreSQL is running:
- Windows: Check Services for PostgreSQL
- Verify connection parameters in `.env`:
  - DB_HOST=localhost
  - DB_PORT=5432
  - DB_NAME=erp_db
  - DB_USER=postgres
  - DB_PASSWORD=123

---

## Key Files Generated

1. **API_TEST_REPORT.md** - Comprehensive technical analysis
2. **test_api_manually.py** - Python script for automated testing
3. **start_server.bat** - Batch script to start server
4. **test_api.ps1** - PowerShell script with integrated testing
5. **BACKEND_TESTING_GUIDE.md** - This file

---

## Expected Test Results

### Login Test
- ✅ Status Code: 200
- ✅ Response contains: access, refresh, user
- ✅ User object contains: id, email, name, role, is_approved, is_active
- ✅ Access token is a valid JWT

### Farm List Test
- ✅ Status Code: 200
- ✅ Response is a JSON array
- ✅ Each farm contains: id, name, description, location, area, is_active
- ✅ Farms are filtered for active only (is_active=true)

---

## API Endpoints Reference

### Authentication
- `POST /api/auth/login/` - Login
- `POST /api/auth/register/` - Register
- `GET /api/auth/me/` - Current user
- `PATCH /api/auth/me/` - Update profile
- `POST /api/auth/me/security/` - Change password

### Farm Management
- `GET /api/farm/farms/` - List farms
- `GET /api/farm/croptypes/` - List crop types
- `GET /api/farm/structure/` - Get farm structure
- `GET /api/farm/hierarchy/` - Get hierarchy
- `GET /api/farm/location-tree/` - Get location tree

### Palm Records
- `GET /api/palm/records/` - List palm records
- `POST /api/palm/records/` - Create palm record
- `GET /api/palm/records/<id>/` - Get palm detail

### Olive Records
- `GET /api/olive/records/` - List olive records
- `POST /api/olive/records/` - Create olive record
- `GET /api/olive/records/<id>/` - Get olive detail

### Warehouse
- `GET /api/warehouse/items/` - List items
- `GET /api/warehouse/movements/` - List movements

### Reports
- `GET /api/reports/tasks/` - List task reports
- `GET /api/reports/operations/` - List operations

---

## JWT Token Information

**Token Lifetime:**
- Access Token: 60 minutes
- Refresh Token: 24 hours

**To Decode Token (for debugging):**
Use online JWT decoder at https://jwt.io (decode only, don't use for sensitive data)

**Token Structure:**
```
{
  "token_type": "access",
  "exp": 1709991248,  // Expiration timestamp
  "iat": 1709987648,  // Issued at
  "jti": "abc123...",
  "user_id": 1        // User ID
}
```

---

## Security Notes

- 🔒 Never commit `.env` file to version control
- 🔒 Change SECRET_KEY in production
- 🔒 Use strong passwords for database
- 🔒 Require HTTPS in production (set DEBUG=False)
- 🔒 Implement rate limiting for login endpoint
- 🔒 Use environment variables for sensitive data

---

## Next Steps

1. **Verify Database**: Ensure PostgreSQL is running and accessible
2. **Start Server**: Run one of the provided scripts
3. **Test Endpoints**: Use curl or Python script to test
4. **Review Logs**: Check Django console output for any errors
5. **Check Response**: Verify status codes match expected values
6. **Extract Token**: Copy JWT from login response
7. **Validate Tenant Filtering**: Verify farm list respects company boundaries

---

## Support

For issues or questions:
1. Check the API_TEST_REPORT.md for detailed technical information
2. Review logs in Django console
3. Check database connection with: `psql -h localhost -U postgres -d erp_db`
4. Verify `.env` configuration matches database setup

---

**Last Updated**: Current Session
**Backend Location**: e:\web\project------------\ATLS-V2\Back-End
**Django Version**: 6.0.4
**Database**: PostgreSQL 12+
