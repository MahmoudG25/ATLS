# FRONTEND (React + Vite)

## Goal

Scalable ERP UI connected to Django API.

## Stack

* React (Vite)
* Material UI
* Tailwind
* Axios
* React Router

## Folder Structure

src/

* app/ (store, config, auth state)
* pages/

  * auth/
  * dashboard/
  * farm/
  * palm/
  * olive/
  * warehouse/
  * equipment/
  * accounting/
  * reports/
  * profile/
* components/
* features/

  * auth/
  * farm/
  * palm/
  * olive/
  * warehouse/
  * equipment/
  * accounting/
  * reports/
* services/ (API layer)
* hooks/
* layouts/
* routes/
* i18n/

## Rules

* No API calls inside UI components
* Each module isolated (palm, olive, etc.)
* Use role-based rendering
* Reusable components only

## Auth Flow

* Login → JWT
* Store token
* Attach in headers
* Redirect based on role
* Block unapproved users

## UI Logic

* Sidebar items depend on role
* Dashboard dynamic per role

## Notes

* Lazy load pages
* Separate business logic in features/
* Avoid global state abuse
