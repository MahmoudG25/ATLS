# Django Backend API Test Report
## ATLS-V2 Project

**Test Date**: Current Session  
**Backend Path**: `e:\web\project------------\ATLS-V2\Back-End`  
**Environment**: Development (DEBUG=True)

---

## Executive Summary

This report documents the Django backend infrastructure, configuration analysis, and testing approach for the ATLS-V2 agriculture management system. Due to environment constraints preventing direct command execution, a comprehensive analysis has been performed based on codebase inspection.

### Key Findings:

✅ **Configuration Status**: Properly configured  
✅ **Database**: PostgreSQL configured (localhost:5432)  
✅ **Authentication**: JWT-based via `rest_framework_simplejwt`  
✅ **API Structure**: RESTful endpoints with role-based access control  
⚠️ **Potential Issue**: Tenant filtering not applied in farm list endpoint  

---

## 1. Environment Configuration

### Django Settings (`core/settings.py`)

| Setting | Value |
|---------|-------|
| **Framework** | Django 6.0.4 |
| **Debug Mode** | True ✓ |
| **Database Engine** | PostgreSQL |
| **Database Name** | `erp_db` |
| **Database User** | `postgres` |
| **Database Password** | `123` |
| **Database Host** | `localhost` |
| **Database Port** | `5432` |
| **Authentication** | JWT (SimpleJWT) |
| **Secret Key** | Configured ✓ |
| **Allowed Hosts** | `localhost, 127.0.0.1` |
| **CORS Origins** | `http://localhost:5173, http://127.0.0.1:5173` |

### .env Configuration (`.env`)

```
SECRET_KEY=django-insecure-k+vm=^3g(7hh!%yy_k(n)-psz+albolqaalg=(*^md@r$^)447
DEBUG=True
DB_NAME=erp_db
DB_USER=postgres
DB_PASSWORD=123
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGIN=http://localhost:5173,http://127.0.0.1:5173
```

### Installed Applications

- `rest_framework` - RESTful API framework
- `rest_framework_simplejwt` - JWT authentication
- `corsheaders` - CORS support
- `mppt` - Materialized Path Tree library
- Custom apps: `users`, `farm`, `palm`, `olive`, `warehouse`, `equipment`, `accounting`, `production`, `reports`, `hr`

---

## 2. Authentication System Analysis

### User Model (`apps/users/models.py`)

```python
class User(AbstractUser):
    email: EmailField (unique)           # Primary authentication field
    name: CharField                      # User's full name
    role: CharField                      # Role: SUPER_ADMIN, OWNER, MANAGER, ENGINEER, etc.
    is_approved: BooleanField            # Must be True to login
    is_active: BooleanField              # Account status
    company: ForeignKey(Company)         # Multi-tenant support
    app_permissions: ManyToManyField     # Fine-grained permissions
```

### User Approval Workflow

**CRITICAL**: Users must have `is_approved=True` to login. Unapproved users will receive:
```json
{
    "detail": "Your account is pending approval."
}
```

### Authentication Service (`services/user_service.py`)

```python
def authenticate_user(email, password):
    # 1. Authenticate credentials
    user = authenticate(email=email, password=password)
    
    # 2. Check is_approved flag
    if not user.is_approved:
        raise PermissionDenied("Your account is pending approval.")
    
    # 3. Check is_active flag
    if not user.is_active:
        raise PermissionDenied("Your account has been deactivated.")
    
    # 4. Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": user
    }
```

### JWT Configuration (`core/settings.py`)

```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),    # 1 hour
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),       # 24 hours
}
```

---

## 3. API Endpoints

### Authentication Endpoints

| Method | Endpoint | Auth Required | Purpose |
|--------|----------|---------------|---------|
| POST | `/api/auth/login` | ❌ | Login with email/password |
| POST | `/api/auth/register` | ❌ | Register new account (pending approval) |
| GET | `/api/auth/me` | ✅ | Get current user details |
| PATCH | `/api/auth/me` | ✅ | Update current user profile |
| POST | `/api/auth/me/security` | ✅ | Change password |

### Farm Management Endpoints

| Method | Endpoint | Auth Required | Purpose |
|--------|----------|---------------|---------|
| GET | `/api/farm/farms` | ✅ | List all farms |
| GET | `/api/farm/croptypes` | ✅ | List crop types |
| GET | `/api/farm/structure` | ✅ | Get farm hierarchy |
| GET | `/api/farm/hierarchy` | ✅ | Get crop structure |
| GET | `/api/farm/location-tree/` | ✅ | Get location tree |

### Serializers

#### LoginSerializer (`serializers/user_serializers.py`)

```python
class LoginSerializer(serializers.Serializer):
    email: EmailField        # Required
    password: CharField      # Required, write-only
```

#### UserSerializer

```python
class UserSerializer(serializers.ModelSerializer):
    fields = [
        "id",
        "email",
        "name",
        "role",
        "phones",
        "is_approved",
        "is_active",
        "last_login",
        "date_joined",
        "permissions"
    ]
```

---

## 4. Login Endpoint Analysis

### URL

```
POST http://localhost:8000/api/auth/login/
```

### Request

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "email": "admin@example.com",
  "password": "admin"
}
```

### Expected Response - Success (Status 200)

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "admin@example.com",
    "name": "Admin User",
    "role": "SUPER_ADMIN",
    "phones": [],
    "is_approved": true,
    "is_active": true,
    "last_login": "2024-...",
    "date_joined": "2024-...",
    "permissions": []
  }
}
```

### Possible Error Responses

**Invalid Credentials (Status 401):**
```json
{
  "detail": "Invalid email or password."
}
```

**Account Not Approved (Status 403):**
```json
{
  "detail": "Your account is pending approval."
}
```

**Account Deactivated (Status 403):**
```json
{
  "detail": "Your account has been deactivated."
}
```

**Validation Error (Status 400):**
```json
{
  "email": ["Invalid email address."],
  "password": ["This field may not be blank."]
}
```

---

## 5. Farm List Endpoint Analysis

### URL

```
GET http://localhost:8000/api/farm/farms/
```

### Request

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

### Implementation (`api/endpoints/farm_views.py`)

```python
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def farms_list_view(request):
    farms = list_farms()  # No tenant filtering!
    return Response(FarmSerializer(farms, many=True).data)
```

### Service Function (`services/farm_service.py`)

```python
def list_farms():
    return Farm.objects.filter(is_active=True)
    # ⚠️ NOTE: Does NOT filter by user's company/tenant
```

### Expected Response - Success (Status 200)

```json
[
  {
    "id": 1,
    "name": "North Farm - Palm",
    "description": "Primary palm cultivation area",
    "location": "Northern Region",
    "area": 150.5,
    "is_active": true,
    ...additional fields...
  },
  {
    "id": 2,
    "name": "South Farm - Olive",
    "description": "Olive cultivation facility",
    "location": "Southern Region",
    "area": 120.0,
    "is_active": true,
    ...
  }
]
```

### Possible Error Responses

**Unauthorized (Status 401):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Invalid Token (Status 401):**
```json
{
  "detail": "Invalid authentication credentials."
}
```

**Token Expired (Status 401):**
```json
{
  "detail": "Token is blacklisted or invalid."
}
```

---

## 6. Tenant Filtering Analysis

### Middleware Setup (`core/middleware.py`)

The `CompanyMiddleware` attaches company info to requests:

```python
class CompanyMiddleware:
    def __call__(self, request):
        user = getattr(request, "user", None)
        request.company = (
            getattr(user, "company", None)
            if user and getattr(user, "is_authenticated", False)
            else None
        )
        return self.get_response(request)
```

### Current Implementation Issue

The farm list endpoint does **NOT** apply tenant filtering:

```python
# ❌ CURRENT (No tenant filtering)
def list_farms():
    return Farm.objects.filter(is_active=True)
```

### Recommended Fix

```python
# ✅ RECOMMENDED (With tenant filtering)
def list_farms(user=None):
    farms = Farm.objects.filter(is_active=True)
    
    # Apply tenant filtering if user has a company
    if user and hasattr(user, 'company') and user.company:
        farms = farms.filter(company_id=user.company.id)
    
    return farms
```

---

## 7. Testing Instructions

### Prerequisites

1. **PostgreSQL Running**: Ensure PostgreSQL is running on `localhost:5432`
2. **Virtual Environment**: Activate the venv
3. **Dependencies**: All packages from `requirements*.txt` must be installed

### Step 1: Start Django Server

```batch
cd e:\web\project------------\ATLS-V2\Back-End
venv\Scripts\activate.bat
python manage.py runserver 0.0.0.0:8000
```

**Expected Output:**
```
Watching for file changes with StatReloader
Starting development server at http://0.0.0.0:8000/
Quit the server with CTRL-BREAK.
```

### Step 2: Run Manual API Tests

Open another terminal:

```batch
cd e:\web\project------------\ATLS-V2\Back-End
venv\Scripts\activate.bat
python test_api_manually.py
```

### Step 3: Using curl to Test Manually

**Login Test:**
```batch
curl -X POST http://localhost:8000/api/auth/login/ ^
  -H "Content-Type: application/json" ^
  -d "{\"email\": \"admin@example.com\", \"password\": \"admin\"}"
```

**Extract Token and Test Farm Endpoint:**
```batch
REM After copying token from login response:
curl -X GET http://localhost:8000/api/farm/farms/ ^
  -H "Authorization: Bearer {YOUR_TOKEN_HERE}"
```

---

## 8. Database Information

### Database Connection Details

```
Host: localhost
Port: 5432
Database: erp_db
User: postgres
Password: 123
```

### Key Tables

- `users_user` - User accounts
- `users_company` - Company/tenant records
- `farm_farm` - Farm data
- `farm_locationnode` - Hierarchical farm structure
- `farm_sector` - Sectors within farms
- `farm_plot` - Plots within sectors

### Multi-Tenant Architecture

- Each user has a `company_id` foreign key
- Farms should be filtered by `company_id`
- Current implementation **does not enforce this**

---

## 9. Configuration Checklist

- ✅ Django project properly configured
- ✅ PostgreSQL database connection configured
- ✅ JWT authentication enabled
- ✅ CORS configured for frontend
- ✅ REST Framework configured
- ✅ User model with email-based auth
- ⚠️ **Tenant filtering not implemented in farm endpoint**
- ✅ Approval workflow in place
- ✅ Virtual environment configured

---

## 10. Recommendations

### High Priority

1. **Implement Tenant Filtering**: Add company filtering to `list_farms()` service
   ```python
   def list_farms(user=None):
       farms = Farm.objects.filter(is_active=True)
       if user and hasattr(user, 'company') and user.company:
           farms = farms.filter(company_id=user.company.id)
       return farms
   ```

2. **Update Farm View**: Pass user context
   ```python
   def farms_list_view(request):
       farms = list_farms(user=request.user)
       return Response(FarmSerializer(farms, many=True).data)
   ```

### Medium Priority

3. **Add Comprehensive Error Handling**: Standardize error responses
4. **Implement Request Logging**: Log API requests for debugging
5. **Add Rate Limiting**: Protect against brute force attacks

### Low Priority

6. **Documentation**: Generate API documentation (Swagger/OpenAPI)
7. **Caching**: Implement caching for frequently accessed data
8. **Pagination**: Ensure farm list supports pagination

---

## 11. Files Generated for Testing

- `test_api_manually.py` - Automated API testing script using requests library

### Usage
```bash
python test_api_manually.py
```

---

## Appendix A: User Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| `SUPER_ADMIN` | System administrator | All permissions |
| `OWNER` | Farm/company owner | Company-wide permissions |
| `MANAGER` | Farm manager | Farm operations |
| `ENGINEER` | Technical staff | Report creation and analysis |
| `ACCOUNTANT` | Financial staff | Accounting operations |
| `HR` | Human resources | HR operations |
| `WAREHOUSE` | Warehouse staff | Inventory management |

---

## Appendix B: Common cURL Commands

### Test Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin"}'
```

### Test Farms (with token)
```bash
curl -X GET http://localhost:8000/api/farm/farms/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test Current User
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test Crop Types
```bash
curl -X GET http://localhost:8000/api/farm/croptypes \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Document Information

- **Report Type**: Technical Analysis & Testing Guide
- **Status**: Ready for Testing
- **Generated**: Current Session
- **Environment**: Development
- **Next Steps**: Execute testing procedures outlined in Section 7
