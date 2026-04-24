# Atlas Farm ERP — Enterprise-Level UI/UX Design Prompt

## Purpose
This prompt is designed to generate a world-class, production-grade UI/UX system using an AI design tool (Figma AI, Galileo AI, Uizard, etc.).
The output must reach enterprise SaaS quality comparable to Stripe, Notion, Linear, and Shopify.

---

## 1. Product Overview
Atlas Farm ERP is a full-scale agricultural management system for large farming operations (date palm & olive farms).

Core capabilities:
- Farm hierarchy (Farm → Sector → Plot)
- Tree management (Palm & Olive)
- Inventory & warehouse
- Equipment & maintenance tracking
- Production & yield analytics
- Daily reports
- Financial accounting
- Role-based access control
- CMS landing page
- Notifications system

Tech Stack:
- Frontend: React + Vite + MUI + Tailwind
- Backend: Django REST Framework
- Auth: JWT
- i18n: Arabic (RTL) + English (LTR)

---

## 2. Design Philosophy (CRITICAL)
- Clarity over decoration
- Function-first UI
- Instant readability (scan in <3 seconds)
- No visual noise
- Strong hierarchy
- Consistency everywhere
- Mobile-first thinking

---

## 3. Design System (MANDATORY)

### Colors
Primary: #16a34a (Agricultural Green)

Neutrals:
#f8fafc → #0f172a (full slate scale)

Semantic:
- Success: green
- Warning: amber
- Error: red
- Info: blue

### Typography
Arabic: Cairo
English: Inter / Outfit

Scale:
- Display: 5rem
- H1: 3rem
- H2: 2.25rem
- H3: 1.875rem
- Body: 1rem
- Caption: 0.75rem

### Spacing
Strict 8px grid system

### Radius
- Small: 8px
- Medium: 10px
- Large: 12px
- XL: 16px

### Shadows
- Subtle (default)
- Elevated
- Colored (for primary actions)

---

## 4. Pages & Screens (FULL COVERAGE)

Design ALL flows:

### Public
- Landing Page (hero, features, stats, CTA, footer)

### Auth
- Login
- Register
- Forgot Password
- Reset Password
- Pending Approval

### Core App
- Dashboard (KPIs + charts)
- Farm Structure
- Palm Records
- Olive Records
- Warehouse
- Equipment
- Finance
- Production
- Reports
- Profile
- Admin Panel

### System
- 403 / 404 pages

---

## 5. UX Requirements

### User Flow Optimization
- Remove friction
- Reduce steps
- Clear navigation paths
- Logical grouping

### States
- Loading (skeletons)
- Empty states
- Error states
- Success feedback

### Forms
- Inline validation
- Smart defaults
- Clear error messages
- Disabled states during submit

---

## 6. Component System

Design reusable components:

- Buttons (primary, secondary, ghost, destructive)
- Inputs (text, select, date, password)
- Cards
- Tables
- Modals
- Navigation (sidebar, topbar, mobile nav)
- Notifications
- Chips & badges

All components must:
- Be consistent
- Support RTL
- Have hover/focus/disabled states

---

## 7. Advanced UX (MUST INCLUDE)

- Analytics dashboard (charts, trends)
- Activity log timeline
- Global search (command palette)
- Map visualization (farm plots)
- Bulk actions for tables
- Export / print views
- Offline indicator (PWA behavior)
- Onboarding tour
- Dark mode

---

## 8. RTL Support (STRICT)

- RTL is default
- Full layout mirroring
- Arabic typography optimization
- Icon direction flipping
- Correct spacing alignment

---

## 9. Responsiveness

### Mobile (Priority)
- Bottom navigation
- Fullscreen modals
- Large touch targets (48px+)

### Tablet
- 2-column layouts
- Collapsible sidebar

### Desktop
- Full layout
- Multi-column grids

---

## 10. Interactions & Motion

- Smooth transitions (0.2s)
- Micro-interactions
- Hover feedback
- Focus states
- Skeleton loading
- Subtle animations only (no distraction)

---

## 11. Output Requirements

The AI must generate:

- Full design system
- All screens
- Desktop + Mobile versions
- RTL + LTR versions
- Component library
- Interaction states

---

## 12. Final Standard (NON-NEGOTIABLE)

The output MUST be:

- Pixel-perfect
- Fully consistent
- Production-ready
- No UX issues
- No spacing errors
- No weak hierarchy

If anything is missing → ADD it  
If anything is unclear → IMPROVE it  

The result must look like it was designed by a top-tier product design team.
