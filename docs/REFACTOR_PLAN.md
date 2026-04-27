## 🚨 STRATEGY

Gradual refactor WITHOUT breaking system

---

## 🔥 STEP 1 — CLEAN LOCATION SYSTEM

### REMOVE:

* crop
* stage
* enclosure fields from reports

### KEEP:

```python
location = FK(LocationNode)
```

---

## 🔥 STEP 2 — REMOVE LEGACY TABLES

Mark as deprecated:

* Sector
* Plot
* CropType

---

## 🔥 STEP 3 — FIX REPORTS

### DailyTaskReport:

KEEP:

* engineer
* operation
* location
* workers
* hours

REMOVE:

* duplicate location fields

---

## 🔥 STEP 4 — REMOVE DROPDOWN SYSTEM

DELETE:

* ReportDropdownOption

REPLACE WITH:

* proper models (Contractor, Operation, etc.)

---

## 🔥 STEP 5 — MERGE DUPLICATES

CREATE:

```python
CropRecord (type = palm / olive)
```

DELETE:

* PalmRecord
* OliveRecord

---

## 🔥 STEP 6 — TENANT FIX

ADD company to:

* Equipment
* Warehouse
* Accounting

---

## 🔥 STEP 7 — FIX WEAK REPORTS

UPDATE:

* FertilizationReport
* IrrigationReport

ADD:

* farm
* location
* operation

---

## 🔥 STEP 8 — REMOVE UNUSED

DELETE:

* CustomFieldDefinition
* CustomFieldValue (temporarily)

---

## 🔥 STEP 9 — VERIFY SYSTEM

CHECK:

* no duplicate data
* all queries working
* no broken APIs

---

## 🧠 AI EXECUTION RULE

When AI works:

1. Read SYSTEM_ARCHITECTURE.md
2. Read DATABASE_RULES.md
3. Apply REFACTOR_PLAN.md
4. DO NOT improvise
5. DO NOT add new structures

---

## 🎯 FINAL RESULT

System becomes:

* clean
* stable
* production-ready
