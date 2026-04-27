
## 🎯 SYSTEM TYPE

Multi-Tenant Farm Management SaaS

Each Company:

* owns multiple farms
* has isolated data
* fully customizable

---

## 🧠 CORE ENTITIES (THE ONLY SOURCE OF TRUTH)

### 1. Company

Root of all data

---

### 2. User

* belongs to Company
* has role (Engineer, Manager, Admin, HR, etc.)

---

### 3. Farm

* belongs to Company

---

### 4. LocationNode (🔥 CORE OF SYSTEM)

Hierarchical structure:

Farm
└── Stage / Sector
  └── Enclosure
    └── Sub-units

❗ ALL location references MUST use LocationNode
❗ NO other location tables allowed

---

### 5. Operation

* belongs to Company
* categorized (pollination, planting, maintenance…)

---

### 6. Report (MASTER ENTITY)

Types:

* DailyTaskReport
* (Future: Fertilization, Irrigation → unified)

Each report MUST include:

* company
* farm
* location (ONLY LocationNode)
* operation
* engineer

---

### 7. LaborEntry

* linked to Report
* tracks workers (company / contractor)

---

### 8. Contractor

* reusable across system
* linked to company

---

### 9. Attachment

* linked to Report
* stored externally (Cloudinary)

---

## ⚠️ REMOVED ENTITIES (DO NOT USE)

* Sector ❌
* Plot ❌
* Crop / Stage / Enclosure as tables ❌
* ReportDropdownOption ❌

---

## 🧩 MODULES (HIGH LEVEL)

* Reports
* HR
* Warehouse
* Equipment
* Accounting

All modules MUST:

* be tenant-scoped
* reuse core entities
* NOT create duplicate logic

---

## 🔗 RELATIONSHIP RULE

ALL data must connect to:

Company → Farm → LocationNode → Report → (Labor / Attachments)

---

## 🎯 FINAL GOAL

System must be:

* Scalable
* Clean
* Reusable
* Analytics-ready
* Sellable
