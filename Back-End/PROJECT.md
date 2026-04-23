# BACKEND (Django + DRF + Service Layer)

## Goal

Clean, modular ERP API

## Stack

* Django
* DRF
* PostgreSQL
* JWT

## Architecture

apps/

* users/
* farm/
* palm/
* olive/
* warehouse/
* equipment/
* accounting/
* reports/

core/

* base models
* utilities

api/

* routers
* endpoints

services/

* user_service.py
* farm_service.py
* report_service.py
* accounting_service.py

serializers/
permissions/

## Rules

* Views = routing only
* Logic in services
* No duplicated logic
* Each module مستقل

## Patterns

* Service layer per module
* Role-based permissions
* Reusable serializers

## Notes

* Start simple, extend later
* Keep models normalized
* Use select_related / prefetch_related
