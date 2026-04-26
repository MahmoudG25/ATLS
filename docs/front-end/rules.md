# FRONTEND RULES

## GOAL

Build clean, scalable UI with minimal AI instructions.

---

## CORE PRINCIPLES

* No business logic in components
* No API calls in UI
* Keep components dumb
* Use features/ for logic

---

## STRUCTURE RULE

Each module must follow:

feature-name/

* components/
* pages/
* services.js
* hooks.js
* types.js (optional)

---

## NAMING

* Components: PascalCase
* Files: kebab-case
* Hooks: useSomething

---

## API USAGE

* All API calls inside /services
* Use Axios instance with JWT
* No direct fetch in components

---

## AUTH RULES

* Store JWT once
* Attach token automatically
* Redirect if not authenticated
* Block unapproved users

---

## ROLE-BASED UI

* Sidebar items controlled by role
* Pages protected per role
* Never trust frontend only

---

## STATE MANAGEMENT

* Local state first
* Use global state ONLY for:

  * auth
  * user data

---

## UI RULES

* Use Material UI for components
* Use Tailwind for spacing/layout
* No inline styles

---

## PERFORMANCE

* Lazy load pages
* Avoid re-renders
* Use memo when needed

---

## DO NOT

* Mix modules together
* Duplicate logic
* Call API inside useEffect randomly

---

## AI USAGE NOTE

When modifying:

* Touch only relevant module
* Do not refactor unrelated code
* Keep structure unchanged
