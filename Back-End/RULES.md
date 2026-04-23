# BACKEND RULES

## GOAL

Clean, modular, scalable API with minimal AI confusion.

---

## CORE PRINCIPLES

* Thin views
* Fat services
* Clear module separation

---

## ARCHITECTURE

apps/

* users
* farm
* palm
* olive
* warehouse
* equipment
* accounting
* reports

---

## LAYER RULE

View → Service → Model

* Views: handle request/response only
* Services: business logic
* Models: data only

---

## NAMING

* Models: PascalCase
* Fields: snake_case
* Services: action_based (create_user, update_report)

---

## DATABASE RULES

* Use ForeignKey for relations
* Avoid duplicate data
* Use indexes where needed

---

## QUERY RULES

* Use select_related / prefetch_related
* Avoid N+1 queries

---

## AUTH RULES

* JWT only
* Block unapproved users
* Always check permissions in backend

---

## PERMISSIONS

* Role-based
* Centralized permission logic
* No scattered checks

---

## SERIALIZERS

* One serializer per use-case
* Avoid huge serializers

---

## SERVICES

Each module must have:

* create
* update
* delete
* get/list

---

## DO NOT

* Put logic in views
* Access DB directly in views
* Duplicate logic across modules

---

## ERROR HANDLING

* Use consistent response format
* Validate inputs in serializers

---

## PERFORMANCE

* Paginate lists
* Limit heavy queries

---

## AI USAGE NOTE

When modifying:

* Do not change structure
* Modify only target module
* Reuse existing services
* Do not create duplicate models
