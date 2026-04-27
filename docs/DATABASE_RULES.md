## 🔒 GLOBAL RULES

1. Every model MUST have:

```python
company = ForeignKey(Company)
```

---

2. NO duplicate tables
   If model exists → reuse it

---

3. NO hardcoded values
   Use DB tables instead

---

4. ALL relationships MUST use ForeignKey
   NO raw IDs

---

5. ALL data MUST be queryable:

* filterable
* aggregatable
* groupable

---

## 🌳 LOCATION RULE

❗ ONLY ONE LOCATION SYSTEM:

```python
LocationNode
```

DO NOT create:

* Sector
* Stage
* Plot

---

## 🔁 REUSABILITY RULE

Before creating model:

ASK:

* Can this be used in another module?

If YES → global model
If NO → rethink design

---

## ⚠️ ANTI-PATTERNS (FORBIDDEN)

* Dropdown tables for business entities ❌
* Duplicate models (Palm / Olive) ❌
* GenericForeignKey (unless absolutely required) ❌

---

## 📊 ANALYTICS RULE

Every important model MUST support:

* date field
* relation to location
* relation to operation

---

## ⚡ PERFORMANCE RULE

Use:

* select_related
* prefetch_related
* indexes

---

## 🧪 VALIDATION RULE

Prevent:

* cross-company data
* orphan records

---

## 🎯 RESULT

Database must be:

* normalized
* clean
* scalable
