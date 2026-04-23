# AUTH (Frontend)

## Flow

* Register → pending approval
* Login → receive JWT
* Store token (localStorage or memory)
* Add token to all requests

## UI

* Login page
* Register page
* Protected routes

## Logic

* If no token → redirect login
* If not approved → show message

## Components

* AuthLayout
* LoginForm
* RegisterForm

## Notes

* Handle token expiration
* Logout clears token
