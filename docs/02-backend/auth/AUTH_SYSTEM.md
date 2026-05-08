# Auth System — Backend Reference

> Merged from: `back-end/auth.md` + `back-end/admin.md`

---

## 1. User Model

```python
class User(AbstractUser):
    ROLE_CHOICES = [
        ('SUPER_ADMIN', 'Super Admin'),
        ('OWNER',       'Owner'),
        ('MANAGER',     'Manager'),
        ('ENGINEER',    'Engineer'),
        ('HR',          'HR Officer'),
        ('ACCOUNTANT',  'Accountant'),
        ('WAREHOUSE',   'Warehouse Officer'),
    ]
    username    = None                   # disabled — email is login identifier
    email       = models.EmailField(unique=True)
    name        = models.CharField(max_length=200)
    phones      = models.JSONField(default=list, blank=True)
    role        = models.CharField(max_length=20, choices=ROLE_CHOICES)
    company     = models.ForeignKey(Company, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
```

---

## 2. Registration & Approval Flow

```
POST /auth/register/
  → User created with is_approved=False
  → Admins notified via Notification system
  → User sees "Awaiting approval" screen

POST /auth/approve-user/{id}/   (MANAGER+)
  → is_approved=True
  → User can now login

POST /auth/login/
  → Validates is_approved=True
  → Returns { access, refresh } JWT tokens

POST /auth/token/refresh/
  → Returns new access token

POST /auth/logout/
  → Blacklists refresh token
```

---

## 3. JWT Configuration

```python
# settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(hours=12),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS':  True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

Frontend attaches token via Axios interceptor:
```javascript
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})
```

---

## 4. Employee Auto-Creation

When a User with a field role registers, an `Employee` record is auto-created:

```python
FIELD_ROLES = ['ENGINEER', 'MANAGER', 'HR', 'ACCOUNTANT', 'WAREHOUSE']

def create_user(validated_data):
    user = User.objects.create_user(**validated_data)
    if user.role in FIELD_ROLES:
        Employee.objects.get_or_create(
            user=user,
            defaults={'hire_date': date.today(), 'status': 'active'}
        )
    return user
```

---

## 5. Notification System

```python
class Notification(models.Model):
    TYPE_CHOICES = [
        ('user_pending', 'New user awaiting approval'),
        ('low_stock',    'Warehouse low stock alert'),
        ('leave_request','Leave request submitted'),
        ('system',       'System notification'),
    ]
    recipient   = models.ForeignKey(User, on_delete=models.CASCADE)
    type        = models.CharField(max_length=30, choices=TYPE_CHOICES)
    message     = models.TextField()
    is_read     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
```

Endpoints:
```
GET   /notifications/              ← list (unread first)
PATCH /notifications/{id}/read/    ← mark one as read
PATCH /notifications/read-all/     ← mark all as read
```

---

## 6. Admin Dashboard Endpoints

```
GET  /admin/users/                 ← list all users in company
PATCH /admin/users/{id}/approve/   ← approve pending user
PATCH /admin/users/{id}/deactivate/ ← deactivate user
GET  /admin/landing-content/       ← CMS content
PATCH /admin/landing-content/      ← update CMS content
```

Permission: `MANAGER+` for user management, `OWNER+` for CMS.
