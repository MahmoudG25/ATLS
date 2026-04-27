# 🌴 Farm Management System — AI Execution Blueprint

## 1. SYSTEM TYPE

Multi-Tenant SaaS Platform

* Each Company has:

  * Multiple Farms
  * Custom Structure (Flexible hierarchy)
* System must support dynamic structure:

  * (Stage → Enclosure) OR (Sector → Enclosure)

---

## 2. CORE ARCHITECTURE

### Backend

* Framework: Django + Django REST Framework
* Architecture: Modular Apps

### Frontend

* React JS (with Vite)
* State Management: Zustand or Redux Toolkit
* UI Framework: Material UI (Customized Theme)

### Storage

* PostgreSQL
* Cloudinary (media storage)

---

## 3. DATABASE DESIGN (CRITICAL)

### Multi-Tenant Structure

```python
class Company:
    name
    subscription_plan

class Farm:
    name
    company (FK)

class LocationNode:
    name
    type (STAGE / SECTOR / ENCLOSURE)
    parent (self FK, nullable)
    farm (FK)
```

> This allows ANY structure (dynamic hierarchy)

---

### Operations

```python
class OperationType:
    name
    company (FK)
    is_active
```

---

### Users & Roles

```python
class User:
    name
    role (ENGINEER, MANAGER, OWNER, ADMIN, HR, ACCOUNTING, STORE)
    company (FK)
```

---

### Daily Report

```python
class DailyReport:
    date
    engineer (FK User)
    operation_type (FK)
    location (FK LocationNode)

    working_hours
    overtime_hours

    notes
```

---

### Labor تفاصيل العمال

```python
class LaborEntry:
    report (FK)
    worker_name
    worker_type (COMPANY / CONTRACTOR)
    contractor (FK nullable)
    hours
    overtime
    note
```

---

### Contractors

```python
class Contractor:
    name
    company (FK)
```

---

### Attachments

```python
class Attachment:
    report (FK)
    file_url
    file_type (IMAGE / VIDEO / FILE)
```

---

## 4. BACKEND REQUIREMENTS

### MUST IMPLEMENT

* Role-based access control (RBAC)
* Company data isolation
* Dynamic filtering APIs

---

### API STRUCTURE

```http
POST   /reports/
GET    /reports/
GET    /reports?operation=&date=&engineer=
GET    /analytics/operations
GET    /analytics/workers
```

---

### REQUIRED FEATURES

* Pagination
* Advanced filtering
* Aggregations (SUM / COUNT / AVG)

---

## 5. FRONTEND (UI/UX) — NOT OPTIONAL

## A) Report Entry UX

* Smart Form:

  * Auto-fill last values
  * Dynamic dropdowns
  * Add Labor inline (expandable rows)
  * Add attachments (drag & drop)

---

## B) Report Feed UI

### Design Style:

* Card-based layout
* Clean spacing
* Arabic RTL optimized

### Each Card:

* Engineer Name
* Operation
* Location Path (Stage > Enclosure)
* Workers count
* Notes preview
* Attachment icon

---

## C) Filters Bar

* Date range picker
* Operation filter
* Engineer filter
* Location filter

---

## D) Analytics Dashboard (HIGH PRIORITY)

### 1. Operation Analytics

* Total per operation (daily / monthly)
* Workers used
* Contractor vs Company

---

### 2. KPI Metrics

* Worker Productivity
* Cost per operation
* Avg hours per task

---

### 3. Table View (Excel Style)

* Group by:

  * Operation
  * Location
  * Date

---

## 6. FILE HANDLING

* Upload to Cloudinary
* Store URL only
* Frontend:

  * Popup modal
  * Slider for images/videos
  * File opens in new tab

---

## 7. EXPORT FEATURES

* Export to Excel
* Export to PDF

---

## 8. PERFORMANCE REQUIREMENTS

* Lazy loading
* API response < 500ms
* Optimized queries (use select_related / prefetch_related)

---

## 9. CODE QUALITY RULES

* Clean architecture
* No duplicated logic
* Use services layer
* Reusable components
* Clear naming

---

## 10. AI AGENT TASK

The AI Agent MUST:

1. Scan all existing files
2. Detect:

   * Missing models
   * Weak structure
   * Bad naming
   * Missing relationships
3. Refactor code
4. Add missing features
5. Improve UI/UX (spacing, alignment, responsiveness)
6. Ensure RTL compatibility
7. Optimize performance

---

## 11. WHAT IS NOT ACCEPTED

* Basic forms without UX thinking
* Static design
* Hardcoded values
* No analytics
* Poor spacing or alignment

---

## 12. FUTURE MODULES (DO NOT IMPLEMENT NOW)

* Accounting System
* Inventory Management
* Crop Yield Tracking
* Financial Reports

---

## FINAL GOAL

Build a **scalable, sellable SaaS product**
NOT a simple farm tool.

The system must:

* Look premium
* Feel fast
* Provide insights
* Be customizable per company
