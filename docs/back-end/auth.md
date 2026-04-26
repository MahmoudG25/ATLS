# AUTH SYSTEM

## Model

Custom User (AbstractUser)

## Fields

* name
* email (unique)
* phones (JSONField)
* role
* is_approved
* is_active

## Roles (Enum)

* SUPER_ADMIN
* OWNER
* MANAGER
* ENGINEER
* ACCOUNTANT
* HR
* WAREHOUSE

## Flow

* Register → is_approved = False
* Admin approves
* Only approved users login

## JWT

* Login returns access + refresh

## Notes

* Use email as username
