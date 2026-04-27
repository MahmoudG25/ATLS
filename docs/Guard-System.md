# 🧠 Farm SaaS System — AI Governance & Refactoring Protocol

## 🚨 CORE RULE (READ FIRST)

This is NOT a coding task.
This is a **system design + refactoring mission**.

The AI MUST:

* Think before coding
* Validate before modifying
* Avoid breaking existing logic

---

## 1. 🔒 GLOBAL PRINCIPLES (NON-NEGOTIABLE)

1. NO duplicate concepts
2. NO creating new tables if similar data exists
3. ALL entities must be reusable across the system
4. ALL data must be tenant-scoped (Company)
5. ANY change must NOT break existing features

---

## 2. 🧱 SYSTEM THINKING MODE

Before writing ANY code, the AI MUST:

### Step 1 — Scan System

* Read all models
* Map relationships
* Detect duplicates
* Detect weak design

---

### Step 2 — Build Mental Model

The system MUST revolve around:

* Company
* Farm
* Location (dynamic hierarchy)
* Operation
* Report
* Labor
* Contractor
* Attachment

If any feature does NOT connect to these → it's WRONG

---

## 3. 🌳 LOCATION IS THE CORE (CRITICAL)

ALL location references MUST use:

```python
LocationNode
```

❌ DO NOT:

* Create Sector table
* Create Stage table
* Create custom location fields

✅ ALWAYS:

* Use LocationNode tree

---

## 4. 🔁 REUSABILITY RULE

Before creating ANY model:

ASK:

> "Can this be reused elsewhere?"

### Examples:

| Entity     | MUST be reusable                     |
| ---------- | ------------------------------------ |
| Contractor | Used in reports, payments, analytics |
| Location   | Used everywhere                      |
| Operation  | Used in reports + analytics          |

---

## 5. 🧩 DATA CONSISTENCY RULE

When creating or updating data:

### MUST CHECK:

* Same company
* Valid relationships
* No orphan records

---

## 6. ⚠️ ANTI-CHAOS RULE

AI MUST STOP if:

* It is about to create a new model similar to existing one
* It is duplicating logic
* It is adding fields without system need

Instead:
→ Refactor existing structure

---

## 7. 🏗️ DATABASE STRUCTURE STANDARD

### MUST FOLLOW:

* TenantAwareModel base
* ForeignKeys (NOT raw IDs)
* Indexed fields
* Clean naming

---

## 8. 🔗 SHARED ENTITIES (IMPORTANT)

These MUST be globally reusable:

* LocationNode
* Contractor
* Operation
* User
* Attachment

❌ DO NOT tie them to one module only

---

## 9. 🧠 FEATURE IMPLEMENTATION RULE

Before implementing ANY feature:

AI MUST answer:

1. Where does this data belong?
2. Is there an existing model for it?
3. Will this affect analytics?
4. Is this reusable?
5. Will this break tenant isolation?

---

## 10. 📊 ANALYTICS-FIRST THINKING

Every data saved MUST support:

* aggregation
* filtering
* grouping

If NOT → design is WRONG

---

## 11. 🎯 UI/UX AWARENESS

AI MUST ensure:

* No random spacing
* No misaligned elements
* Consistent layout
* RTL support

---

## 12. 🧪 SAFE REFACTORING MODE

When modifying code:

* DO NOT delete blindly
* Mark old logic if needed
* Ensure backward compatibility

---

## 13. 🚫 FORBIDDEN ACTIONS

AI MUST NOT:

* Create duplicate tables
* Hardcode values
* Ignore tenant logic
* Break existing APIs
* Build isolated features

---

## 14. ✅ REQUIRED OUTPUT FORMAT

When AI works, it MUST:

1. Explain what is wrong
2. Show fixed structure
3. Provide updated code
4. Ensure no regression

---

## 15. 🎯 FINAL GOAL

Build a system that is:

* Scalable
* Clean
* Reusable
* Sellable

NOT:

* Quick
* Messy
* Temporary

---

## 🔥 FINAL WARNING

If AI:

* Fixes one part and breaks another → FAILURE
* Adds complexity without reason → FAILURE
* Ignores system structure → FAILURE

---

## 🧠 MINDSET

Think like:
→ Senior Architect

NOT:
→ Junior Developer
