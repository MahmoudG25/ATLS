# Auth Pages — Frontend Reference

> Merged from: `front-end/auth.md`

---

## Pages

### Login (`/login`)

**Design:** Dark gradient bg (`slate-950 → slate-900 → indigo-950`), glassmorphism card.

```
Fields:
  - Email (type=email, required)
  - Password (type=password, required)
  - Language toggle (AR/EN) → top-right

On success → redirect to /dashboard
On error → inline error below form
Unapproved user → "Awaiting admin approval" notice
```

**Service:**
```javascript
// features/auth/services.js
export const login = (email, password) =>
  api.post('/auth/login/', { email, password })
```

---

### Register (`/register`)

**Design:** Same dark theme as Login.

```
Fields:
  - Full Name (required)
  - Email (required, unique)
  - Password (required, min 8 chars)
  - Confirm Password (must match)
  - Role (select: ENGINEER / HR / ACCOUNTANT / WAREHOUSE)
  - Company Name (required)

On success → "Awaiting approval" screen (not dashboard)
```

**Note:** `is_approved=False` until an OWNER/MANAGER approves the user.

---

### Awaiting Approval Screen

Shown after registration and on login attempt if `is_approved=False`:
- Informational message only
- "Contact your admin" guidance
- Logout button

---

## Auth Flow

```
POST /auth/register/
  → 201 Created → Awaiting Approval screen

POST /auth/login/
  → 200 OK → { access, refresh }
  → Store tokens in localStorage
  → Redirect to /dashboard

POST /auth/token/refresh/  (automatic via interceptor)
  → Returns new access token on 401 response

POST /auth/logout/
  → Blacklist refresh token
  → Clear localStorage
  → Redirect to /login
```

---

## i18n

All form validation messages in Arabic by default:
```
هذا الحقل مطلوب
البريد الإلكتروني غير صحيح
كلمة المرور يجب أن تكون 8 أحرف على الأقل
كلمات المرور غير متطابقة
```
