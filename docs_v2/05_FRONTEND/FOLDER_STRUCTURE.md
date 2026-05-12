# ATLS FRONTEND: FOLDER STRUCTURE & GOVERNANCE

> **Confidential & Proprietary**  
> **Target Audience:** Principal Architects, Frontend Engineering Leads, AI Implementation Agents  
> **Type:** Master Governance Document  
> **Scope:** Frontend Physical Repository Architecture, Folder Isolation, Import Direction, and AI-Safe Code Generation

---

## Purpose

Define the master frontend folder structure, physical organization, and directory governance for the ATLS platform. This document codifies the *physical* manifestation of Domain-Driven Design in the frontend codebase, ensuring that folder hierarchy directly reflects domain boundaries, import direction rules prevent cross-domain contamination, and AI agents can safely generate and refactor code within isolated, predictable boundaries.

This document is **NOT** about component architecture (see [COMPONENT_ARCHITECTURE.md](COMPONENT_ARCHITECTURE.md)), routing mechanics (see [ROUTING_SYSTEM.md](ROUTING_SYSTEM.md)), or theme/styling (see [TAILWIND_RULES.md](TAILWIND_RULES.md)). This document **ONLY** addresses: where files live, how folders relate to each other, import direction rules, and structure governance.

## Scope

*   Frontend project physical structure and folder hierarchy
*   Domain-based isolation rules
*   Shared layer governance (what can go in shared, what cannot)
*   Feature folder organization and depth constraints
*   Service organization and ownership
*   Query and mutation layer organization
*   Zustand store isolation
*   Form, Layout, Navigation, and Table component structures
*   Barrel export rules
*   Import direction constraints
*   Forbidden anti-patterns and AI safety rules
*   Real agricultural scenarios demonstrating correct structure
*   Enforcement checklist for architecture reviews

## Current Status

- [x] Not Started
- [x] In Progress
- [ ] Completed

## Dependencies

*   [COMPONENT_ARCHITECTURE.md](COMPONENT_ARCHITECTURE.md) — Component execution and composition
*   [ROUTING_SYSTEM.md](ROUTING_SYSTEM.md) — Route architecture and navigation
*   [DOMAIN_DRIVEN_ARCHITECTURE.md](../01_ARCHITECTURE/DOMAIN_DRIVEN_ARCHITECTURE.md) — Backend domain strategy applied to frontend
*   [MONOREPO_STRUCTURE.md](../MONOREPO_STRUCTURE.md) — Overall repository structure
*   [SYSTEM_PHILOSOPHY.md](../00_PROJECT_CORE/SYSTEM_PHILOSOPHY.md) — ATLS platform philosophy

## Notes

This is the master frontend folder structure governance document. It enforces **domain isolation**, **shared layer minimalism**, **controlled import direction**, and **AI-safe code generation boundaries**.

## Last Updated

2026-05-12

---

## 1. Frontend Structure Philosophy

ATLS frontend is organized as a **domain-isolated modular monolith**, not a layers-based monolith. This means:

*   **Primary Organization:** Business domains (harvest, equipment, operations, etc.), not technical layers (components, hooks, services).
*   **Folder Hierarchy:** Folders reflect organizational and domain boundaries, not framework concerns.
*   **Self-Contained Domains:** Each domain can theoretically be extracted into a separate repo or package without breaking other domains.
*   **Shared Kernel Minimalism:** Shared code is kept to truly generic, domain-agnostic utilities and UI primitives.
*   **AI-Safe Boundaries:** Clear folder boundaries allow AI agents to operate within a domain without accidentally contaminating adjacent domains.

---

## 2. Modular Frontend Strategy

The ATLS frontend employs a **Feature-First Modular Architecture**:

*   **Domains → Features → Pages → Components → UI Primitives**
*   Each domain contains complete vertical slices: pages, hooks, state, services, types.
*   Features own their data, UI, state management, and API integrations.
*   Shared code is minimal and truly cross-domain.

### Principle of Vertical Slices

```
src/
├── features/
│   ├── farm/                 ← Domain
│   │   ├── pages/
│   │   ├── hooks/            ← domain-specific hooks
│   │   ├── stores/           ← domain-specific state
│   │   ├── services/         ← domain-specific API services
│   │   ├── types/            ← domain entity types
│   │   └── components/       ← domain-specific components
│   ├── harvest/              ← Domain
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── stores/
│   │   ├── services/
│   │   ├── types/
│   │   └── components/
│   └── equipment/
└── shared/                   ← Cross-domain primitives only
```

---

## 3. Domain-Based Folder Isolation

Each domain folder is a **fortress**. Internal domain implementation is not imported by other domains.

### Domain Folder Structure

```
src/features/<domain>/
├── index.ts                     ← Barrel export (public API only)
├── pages/
│   ├── index.ts
│   ├── <entity>-list-page.tsx
│   └── <entity>-detail-page.tsx
├── hooks/
│   ├── index.ts
│   ├── use<entity>-query.ts
│   ├── use<entity>-mutation.ts
│   └── use<entity>-form.ts
├── stores/
│   ├── index.ts
│   ├── <entity>-store.ts       ← Zustand store
│   └── <entity>-ui-store.ts    ← UI state (filters, selected, etc.)
├── services/
│   ├── index.ts
│   ├── <entity>-api.ts
│   └── <entity>-sync.ts        ← Offline sync logic
├── types/
│   ├── index.ts
│   ├── <entity>.ts
│   └── api.ts                  ← Domain-specific API response types
├── components/
│   ├── index.ts
│   ├── <entity>-card.tsx
│   ├── <entity>-form.tsx
│   ├── <entity>-table.tsx
│   └── ui/                     ← Domain-specific UI components only
│       ├── <entity>-header.tsx
│       └── <entity>-filter.tsx
├── layouts/
│   ├── index.ts
│   └── <domain>-layout.tsx     ← Domain-specific layout wrapper
└── __tests__/
    ├── hooks.test.ts
    ├── stores.test.ts
    ├── services.test.ts
    └── components.test.ts
```

### Domain Folder Rules

*   **Ownership:** One domain team owns a domain folder. No shared ownership across domains.
*   **Internal Files:** Files prefixed with underscore (e.g., `_utils.ts`) are internal and not exported via barrel.
*   **Public API:** Only exported from `index.ts` barrel. Other domains import from barrels only.
*   **No Internal Imports:** Other domains must NOT import from `domain/pages`, `domain/hooks`, `domain/stores` directly.
*   **No Direct Entity Imports:** Other domains must NOT import types from `domain/types/entity.ts` directly.

### Cross-Domain Reference Pattern

```typescript
// ❌ FORBIDDEN: Direct import from internal domain module
import { useFarmQuery } from 'src/features/farm/hooks/useFarmQuery';

// ✅ ALLOWED: Import from barrel only
import { FarmPage, useFarmQuery } from 'src/features/farm';

// ✅ ALLOWED: Import shared types from shared/contracts
import { FarmDTO } from 'src/shared/contracts/farm';

// ✅ ALLOWED: Domain can import its own types
import { FarmFormData } from 'src/features/farm/types';
```

---

## 4. App Shell Structure

The app shell is the root orchestrator, containing only routing, auth, theme, and layout composition.

```
src/
├── app/
│   ├── App.tsx                  ← Root app component
│   ├── App.css                  ← Global styles (minimal)
│   ├── root-layout.tsx          ← Main shell layout (header, nav, main area)
│   ├── error-boundary.tsx       ← Top-level error boundary
│   ├── providers.tsx            ← Context providers (Auth, Theme, etc.)
│   └── __tests__/
│       └── App.test.tsx
├── routes/
│   ├── index.ts
│   ├── public-routes.ts
│   ├── auth-routes.ts
│   └── domain-routes.ts         ← Routes imported from features/*/routes.ts
├── layouts/
│   ├── index.ts
│   ├── dashboard-layout.tsx     ← Shared dashboard wrapper
│   ├── form-layout.tsx          ← Shared form wrapper
│   └── mobile-layout.tsx        ← Mobile-first bottom nav wrapper
├── contexts/
│   ├── index.ts
│   ├── auth-context.tsx         ← Auth state provider
│   ├── theme-context.tsx        ← Theme provider
│   └── tenant-context.tsx       ← Tenant context provider
└── __tests__/
    └── routes.test.ts
```

### App Shell Rules

*   **No Business Logic:** The app shell orchestrates only. No domain-specific state or API calls.
*   **Minimal CSS:** Global styles are minimal. Domain-specific styles remain in domain folders.
*   **Provider Stack:** Providers are stacked in `providers.tsx` and mounted in `App.tsx`.
*   **Routes Import:** Routes are imported from domain `routes.ts` files and composed in `root-routes.ts`.

---

## 5. Route-Level Organization

Routes are organized at the domain level, not globally.

```
src/features/<domain>/
├── routes.ts                    ← Domain route definitions
├── pages/
│   ├── index.ts
│   ├── <entity>-list-page.tsx
│   └── <entity>-detail-page.tsx
└── layouts/
    └── <domain>-layout.tsx
```

### Route File Rules

*   **Ownership:** Each domain owns its route definitions.
*   **Route Objects:** Use React Router v7 route objects, not JSX routes.
*   **Lazy Loading:** Routes are lazy-loaded via `React.lazy()` and `<Suspense>`.
*   **Layout Nesting:** Domain routes nest within shared layouts via `<Outlet>`.
*   **No Hardcoding:** Routes are not hardcoded in the app shell. They are imported and composed.

### Route Definition Example

```typescript
// src/features/farm/routes.ts
import { lazy } from 'react';

export const farmRoutes = [
  {
    path: 'farm',
    element: <FarmLayout />,
    children: [
      {
        index: true,
        element: lazy(() => import('./pages/farm-list-page')),
      },
      {
        path: ':farmId',
        element: lazy(() => import('./pages/farm-detail-page')),
      },
    ],
  },
];
```

---

## 6. Feature Folder Structure

A feature folder is a complete vertical slice within a domain.

```
src/features/<domain>/<feature>/
├── index.ts                     ← Public API barrel
├── pages/
│   ├── index.ts
│   └── <feature>-page.tsx
├── hooks/
│   ├── index.ts
│   ├── use<feature>-query.ts
│   └── use<feature>-mutation.ts
├── components/
│   ├── index.ts
│   ├── <feature>-card.tsx
│   ├── <feature>-form.tsx
│   └── ui/
│       └── <feature>-header.tsx
├── stores/
│   ├── index.ts
│   └── <feature>-store.ts
├── services/
│   ├── index.ts
│   └── <feature>-api.ts
├── types/
│   ├── index.ts
│   └── <feature>.ts
└── __tests__/
    └── <feature>.test.ts
```

### Feature Depth Rule

*   **Shallow Nesting:** Features are one level deep (`features/<domain>/<feature>/`). No nested feature-in-feature.
*   **No Sub-Features:** If a feature becomes too large, split it into a separate domain, not a sub-feature.
*   **Max Folder Depth:** Keep folder depth to 5 levels (`src/features/domain/feature/components/subcomponent/index.ts` is the maximum).

---

## 7. Shared Layer Rules

The shared layer is **carefully controlled**. This is the primary risk zone for domain contamination.

```
src/shared/
├── ui/                          ← Shared UI primitives only
│   ├── index.ts
│   ├── button.tsx
│   ├── input.tsx
│   ├── modal.tsx
│   └── table.tsx
├── hooks/
│   ├── index.ts
│   ├── use-query-params.ts
│   └── use-offline.ts
├── utils/
│   ├── index.ts
│   ├── format-date.ts
│   ├── format-currency.ts
│   └── validators.ts
├── constants/
│   ├── index.ts
│   ├── api.ts
│   ├── ui.ts
│   └── validation.ts
├── types/
│   ├── index.ts
│   ├── api.ts
│   └── common.ts
├── contracts/
│   ├── index.ts
│   ├── farm.ts
│   ├── harvest.ts
│   └── equipment.ts
├── stores/
│   ├── index.ts
│   ├── auth-store.ts            ← Global auth state only
│   ├── theme-store.ts           ← Global theme state only
│   └── notification-store.ts    ← Global notifications only
├── services/
│   ├── index.ts
│   ├── http-client.ts           ← Shared HTTP client
│   ├── offline-cache.ts         ← Offline cache provider
│   └── error-handler.ts
├── theme/
│   ├── index.ts
│   ├── theme-provider.tsx
│   ├── tokens.ts
│   └── colors.ts
├── i18n/
│   ├── index.ts
│   ├── i18n-config.ts
│   └── translations/
├── layouts/
│   ├── index.ts
│   ├── dashboard-layout.tsx     ← Generic dashboard wrapper
│   ├── form-layout.tsx
│   └── mobile-bottom-nav.tsx
└── __tests__/
    └── shared.test.ts
```

### Shared Layer Governance

*   **No Domain Logic:** Shared utilities are never domain-specific.
*   **No Domain Imports:** Shared files must NEVER import from `features/` folders.
*   **No Business Rules:** Shared utils are purely technical (formatting, validation, HTTP).
*   **Public API Only:** All shared exports are via barrel files.
*   **Strict Review:** Any new shared file requires architecture review.

### Prohibited in Shared

*   ❌ Forms containing domain business logic
*   ❌ Entity types (move to domain contracts)
*   ❌ Domain-specific hooks (`use-farm-query`, `use-harvest-mutation`)
*   ❌ Domain services (`farm-api`, `equipment-sync`)
*   ❌ Domain state stores (`farm-store`, `harvest-ui-store`)
*   ❌ Shared folders with 50+ files ("util dumping")
*   ❌ Random helper functions not categorized by concern

---

## 8. Shared UI Structure

Shared UI components are generic, brand-agnostic, and framework-compatible.

```
src/shared/ui/
├── index.ts
├── button/
│   ├── button.tsx
│   ├── button.types.ts
│   └── __tests__/
│       └── button.test.tsx
├── input/
│   ├── input.tsx
│   ├── input.types.ts
│   └── __tests__/
├── modal/
│   ├── modal.tsx
│   ├── modal-content.tsx
│   ├── modal.types.ts
│   └── __tests__/
├── table/
│   ├── table.tsx
│   ├── table-header.tsx
│   ├── table-body.tsx
│   ├── table-row.tsx
│   ├── table-cell.tsx
│   ├── table.types.ts
│   └── __tests__/
├── form/
│   ├── form-field.tsx
│   ├── form-label.tsx
│   ├── form-error.tsx
│   ├── form.types.ts
│   └── __tests__/
├── card/
│   ├── card.tsx
│   └── __tests__/
└── ...
```

### Shared UI Rules

*   **No State Logic:** UI components are stateless or have only local UI state (open/closed).
*   **Props-Driven:** All behavior is driven by props, not internal state.
*   **Accessibility:** All shared UI components must be WCAG 2.1 AA compliant.
*   **Theme Support:** All colors and spacing are theme-tokenized.
*   **RTL Support:** All layouts support RTL via CSS logical properties.
*   **Mobile-First:** All components are responsive and mobile-optimized by default.
*   **TypeScript:** All shared UI components have strict types.

---

## 9. Shared Hooks Structure

Shared hooks are utility hooks for cross-domain concerns.

```
src/shared/hooks/
├── index.ts
├── use-query-params.ts          ← URL query param management
├── use-offline.ts               ← Offline status detection
├── use-previous.ts              ← Previous value tracking
├── use-debounce.ts              ← Debounce utility
├── use-throttle.ts              ← Throttle utility
├── use-local-storage.ts         ← Local storage sync
├── use-responsive.ts            ← Responsive breakpoint detection
├── use-intersection.ts          ← Intersection observer
├── use-async-effect.ts          ← Async effect helper
└── __tests__/
    └── hooks.test.ts
```

### Shared Hooks Rules

*   **No Domain Dependencies:** Shared hooks never import from `features/`.
*   **Truly Reusable:** If a hook is used by only one domain, it belongs in that domain.
*   **Composition Over Logic:** Shared hooks are thin wrappers or utility functions.
*   **Clear Responsibility:** One hook per concern. No god hooks.
*   **Documented:** All shared hooks have clear JSDoc with usage examples.

### Forbidden Hook Anti-Pattern

```typescript
// ❌ FORBIDDEN: Domain-specific hook in shared
export const useFarmList = () => {
  return useQuery({
    queryKey: ['farms'],
    queryFn: () => farmApi.list(),
  });
};

// ✅ ALLOWED: Generic query wrapper in domain
// src/features/farm/hooks/use-farm-list.ts
export const useFarmList = () => {
  return useQuery({
    queryKey: ['farms'],
    queryFn: () => farmApi.list(),
  });
};
```

---

## 10. Shared Utils Rules

Shared utils are categorized by concern and kept minimal.

```
src/shared/utils/
├── index.ts
├── format.ts                    ← Date, currency, number formatting
├── validators.ts               ← Reusable validation functions
├── string.ts                   ← String manipulation (camelCase, kebab-case, etc.)
├── math.ts                     ← Math utilities (sum, average, etc.)
├── arrays.ts                   ← Array utilities (uniqBy, groupBy, etc.)
├── objects.ts                  ← Object utilities (pick, omit, etc.)
├── errors.ts                   ← Error handling utilities
└── __tests__/
    └── utils.test.ts
```

### Shared Utils Rules

*   **Max 10 Files:** Shared utils stay under 10 files. If exceeding, move domain-specific utils to domain folder.
*   **Pure Functions:** All utils are pure functions with no side effects.
*   **No State:** Utils never maintain state or access global variables.
*   **Well-Named:** Function names are clear and self-documenting.
*   **Tested:** All utils have unit tests with 100% coverage.
*   **Documented:** JSDoc on all exports.

### Utils Anti-Pattern

```typescript
// ❌ FORBIDDEN: Giant utils folder
src/shared/utils/
├── formatFarmName.ts
├── calculateHarvestYield.ts
├── validateFarmBoundary.ts
├── syncFarmWithServer.ts
├── transformFarmAPIResponse.ts
├── ...50 more files
└── (becomes impossible to navigate)

// ✅ ALLOWED: Move domain-specific utils to domain
src/features/farm/utils/
├── format.ts
├── validators.ts
├── calculations.ts
└── sync.ts
```

---

## 11. Shared Constants Rules

Constants are organized by domain and concern.

```
src/shared/constants/
├── index.ts
├── api.ts                       ← API endpoints, timeouts, retry logic
├── ui.ts                        ← UI breakpoints, animation durations
├── validation.ts               ← Validation regex, message templates
├── permissions.ts              ← Role and permission constants
└── __tests__/
    └── constants.test.ts
```

### Constants Organization

*   **Domain-Specific Constants:** Belong in the domain (e.g., `features/farm/constants/`)
*   **Cross-Domain Constants:** Belong in shared
*   **No Magic Numbers:** All numbers are constants with clear names
*   **Environment-Aware:** Constants that vary by environment use environment config

```typescript
// ❌ FORBIDDEN: Magic numbers in code
const maxRetries = 3;
const timeout = 30000;

// ✅ ALLOWED: Named constants
const MAX_API_RETRIES = 3;
const API_REQUEST_TIMEOUT_MS = 30000;
```

---

## 12. Shared Types Structure

Shared types are minimal and domain-agnostic.

```
src/shared/types/
├── index.ts
├── api.ts                       ← Generic API types (Response, Error, Pagination)
├── common.ts                    ← Primitives (UUID, Money, Coordinates, etc.)
├── store.ts                     ← Generic store types
└── __tests__/
    └── types.test.ts
```

### Shared Types Rules

*   **No Domain Entities:** Entity types belong in domain `types/` folders
*   **No Domain DTOs:** API DTOs belong in domain `types/api.ts`
*   **Primitive Types Only:** Only generic, cross-domain types in shared
*   **Well-Documented:** All types have clear comments

### Domain Types Example

```typescript
// ❌ FORBIDDEN: Domain entity type in shared
// src/shared/types/entities.ts
export interface Farm {
  id: string;
  name: string;
  sectors: Sector[];
}

// ✅ ALLOWED: Domain entity type in domain
// src/features/farm/types/farm.ts
export interface Farm {
  id: string;
  name: string;
  sectors: Sector[];
}

// ✅ ALLOWED: Generic primitive in shared
// src/shared/types/common.ts
export type UUID = string & { readonly __uuid: true };
```

---

## 13. API Layer Structure

API services are domain-owned and organized by entity and concern.

```
src/features/<domain>/services/
├── index.ts
├── <entity>-api.ts              ← API calls for an entity
├── <entity>-sync.ts             ← Offline sync logic
└── __tests__/
    └── api.test.ts
```

### API Service Rules

*   **HTTP Client:** All API calls use the shared `http-client`
*   **Request/Response Types:** Defined in domain `types/api.ts`
*   **Error Handling:** Errors are handled via shared error handler
*   **Retry Logic:** Retry logic is configured in shared HTTP client
*   **Timeout:** Timeout values are from shared constants
*   **No Fetch Calls:** Direct `fetch()` calls are forbidden. Use HTTP client.

### API Service Example

```typescript
// src/features/farm/services/farm-api.ts
import { httpClient } from 'src/shared/services';
import type { FarmDTO, FarmListQuery } from '../types/api';

export const farmApi = {
  async list(query: FarmListQuery) {
    return httpClient.get<FarmDTO[]>('/api/farms', { params: query });
  },

  async getById(id: string) {
    return httpClient.get<FarmDTO>(`/api/farms/${id}`);
  },

  async create(data: FarmDTO) {
    return httpClient.post<FarmDTO>('/api/farms', data);
  },
};
```

---

## 14. Query Layer Structure

Query hooks wrap React Query and expose typed, cached results.

```
src/features/<domain>/hooks/
├── index.ts
├── queries/
│   ├── use-<entity>-list.ts
│   ├── use-<entity>-detail.ts
│   └── use-<entity>-search.ts
└── __tests__/
    └── queries.test.ts
```

### Query Hook Rules

*   **Query Keys:** Defined in domain constant (e.g., `FARM_QUERIES`)
*   **Stale Times:** Configured based on data sensitivity
*   **Retry Logic:** Inherited from HTTP client
*   **Error Handling:** Errors are typed and handled by component or error boundary
*   **No Side Effects:** Query hooks are pure, no mutations on fetch
*   **Suspense Optional:** May enable suspense for non-critical queries

### Query Hook Example

```typescript
// src/features/farm/hooks/queries/use-farm-list.ts
import { useQuery } from '@tanstack/react-query';
import { farmApi } from '../../services';
import { FARM_QUERY_KEYS } from '../../constants';

export const useFarmList = (filters?: FarmListQuery) => {
  return useQuery({
    queryKey: FARM_QUERY_KEYS.list(filters),
    queryFn: () => farmApi.list(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 30 * 60 * 1000,    // 30 minutes
  });
};
```

---

## 15. Mutation Layer Structure

Mutation hooks wrap React Query mutations and handle side effects.

```
src/features/<domain>/hooks/
├── index.ts
├── mutations/
│   ├── use-create-<entity>.ts
│   ├── use-update-<entity>.ts
│   └── use-delete-<entity>.ts
└── __tests__/
    └── mutations.test.ts
```

### Mutation Hook Rules

*   **Optimistic Updates:** Mutations should apply optimistic updates to affected queries
*   **Query Invalidation:** Invalidate only affected query keys after success
*   **Error Rollback:** Rollback optimistic updates on error
*   **Loading State:** Mutations expose loading and error states for UI
*   **Typed Errors:** Error responses are typed
*   **No Component Logic:** Mutations are thin wrappers, not orchestrators

### Mutation Hook Example

```typescript
// src/features/farm/hooks/mutations/use-create-farm.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { farmApi } from '../../services';
import { FARM_QUERY_KEYS } from '../../constants';

export const useCreateFarm = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: FarmDTO) => farmApi.create(data),
    onSuccess: (newFarm) => {
      queryClient.invalidateQueries({
        queryKey: FARM_QUERY_KEYS.lists(),
      });
      queryClient.setQueryData(
        FARM_QUERY_KEYS.detail(newFarm.id),
        newFarm
      );
    },
    onError: () => {
      // Error handling is delegated to the component
    },
  });
};
```

---

## 16. Zustand Store Organization

Global state (auth, theme, notifications) is Zustand-based and minimal.

```
src/shared/stores/
├── index.ts
├── auth-store.ts                ← User, token, permissions
├── theme-store.ts               ← Theme, RTL, language
├── notification-store.ts        ← Toast notifications
└── __tests__/
    └── stores.test.ts
```

### Domain Zustand Stores

Feature-specific UI state (filters, selected items) lives in domain stores:

```
src/features/<domain>/stores/
├── index.ts
├── <entity>-store.ts            ← Entity business state
├── <entity>-ui-store.ts         ← Entity UI state (filters, selected, sort)
└── __tests__/
    └── stores.test.ts
```

### Zustand Store Rules

*   **Shared Stores:** Auth, theme, notifications only
*   **Domain Stores:** Each domain has UI state stores if needed
*   **No Server Data:** Server data belongs in React Query, not Zustand
*   **Minimal Selectors:** Selectors are co-located with store definitions
*   **No Cross-Domain Stores:** Stores don't coordinate across domains
*   **Typed:** All store state is strongly typed
*   **Immer Middleware:** Use Immer for immutable updates

### Zustand Store Example

```typescript
// src/features/farm/stores/farm-ui-store.ts
import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';

interface FarmUIStore {
  selectedFarmId: string | null;
  filters: FarmListFilters;
  sortBy: SortField;
  setSelectedFarm: (id: string) => void;
  setFilters: (filters: Partial<FarmListFilters>) => void;
  setSortBy: (field: SortField) => void;
}

export const useFarmUIStore = create<FarmUIStore>()(
  immer((set) => ({
    selectedFarmId: null,
    filters: {},
    sortBy: 'name',
    setSelectedFarm: (id) => set({ selectedFarmId: id }),
    setFilters: (filters) =>
      set((state) => {
        state.filters = { ...state.filters, ...filters };
      }),
    setSortBy: (field) => set({ sortBy: field }),
  }))
);
```

---

## 17. Form Structure Rules

Forms are organized by concern and domain.

```
src/features/<domain>/components/forms/
├── index.ts
├── <entity>-form.tsx            ← Main form component
├── <entity>-form.schema.ts      ← Zod/schema definitions
├── <entity>-form.types.ts       ← Form-specific types
└── __tests__/
    └── <entity>-form.test.tsx
```

### Form Organization

*   **Schema Ownership:** Each domain owns form schemas for its entities
*   **Validation Centralized:** Zod schemas define validation rules
*   **Type Safety:** Schema-derived types prevent runtime errors
*   **Reusable Fields:** Custom field components are in `src/shared/ui/form/`
*   **No Global Form State:** Form state is local (React Hook Form) unless shared across multiple pages

### Form Example

```typescript
// src/features/farm/components/forms/farm-form.schema.ts
import { z } from 'zod';

export const farmFormSchema = z.object({
  name: z.string().min(1, 'Farm name is required'),
  location: z.object({
    latitude: z.number(),
    longitude: z.number(),
  }),
  area: z.number().positive('Area must be positive'),
});

export type FarmFormData = z.infer<typeof farmFormSchema>;
```

---

## 18. Layout Folder Strategy

Layouts are shared shells and domain-specific wrappers.

```
src/shared/layouts/
├── index.ts
├── dashboard-layout.tsx         ← Generic dashboard with sidebar
├── form-layout.tsx              ← Generic form wrapper
├── mobile-layout.tsx            ← Mobile-first bottom nav
└── error-layout.tsx             ← Error page layout

src/features/<domain>/layouts/
├── index.ts
└── <domain>-layout.tsx          ← Domain-specific layout wrapper
```

### Layout Rules

*   **Shared Layouts:** Generic shells reused across domains
*   **Domain Layouts:** Wrap shared layouts with domain-specific navigation or context
*   **No Business Logic:** Layouts only handle structure, not state or data fetching
*   **Responsive:** Layouts adapt to mobile-first and desktop modes
*   **Lazy-Loadable:** Layouts are imported via React Router and lazy-loaded

---

## 19. Theme Structure Rules

Theme and styling are centralized and token-based.

```
src/shared/theme/
├── index.ts
├── theme-provider.tsx           ← Theme context provider
├── tokens.ts                    ← Design tokens (colors, spacing, etc.)
├── colors.ts                    ← Color palette
├── typography.ts               ← Font sizes, weights, line heights
├── breakpoints.ts              ← Responsive breakpoints
├── shadows.ts                  ← Shadow definitions
└── animations.ts               ← Animation durations and curves
```

### Theme Rules

*   **Token-Based:** All colors and spacing use design tokens
*   **No Hardcoding:** Color values are never hardcoded in components
*   **RTL Support:** Theme tokens support RTL via CSS logical properties
*   **Runtime Theming:** Themes can be swapped at runtime
*   **White-Label:** Multiple theme variants can coexist
*   **Dark Mode:** Theme supports light and dark modes
*   **Accessibility:** Colors have sufficient contrast for WCAG AA

---

## 20. Navigation Structure

Navigation is organized by routing and page-level navigation.

```
src/shared/layouts/
├── navigation/
│   ├── index.ts
│   ├── top-nav.tsx              ← Header navigation
│   ├── sidebar-nav.tsx          ← Desktop sidebar
│   └── mobile-bottom-nav.tsx    ← Mobile bottom navigation

src/features/<domain>/layouts/
└── navigation/
    ├── index.ts
    └── domain-nav.tsx           ← Domain-specific nav items
```

### Navigation Rules

*   **Mobile-First:** Navigation adapts to mobile screens (bottom nav) and desktop (sidebar)
*   **Runtime Config:** Navigation items are configured at runtime based on roles and permissions
*   **No Hardcoding:** Navigation menus are not hardcoded in components
*   **Active State:** Active routes are highlighted via route matching
*   **Breadcrumbs:** Breadcrumbs reflect route hierarchy

---

## 21. Table Component Organization

Tables are organized by use case and domain.

```
src/shared/ui/table/
├── table.tsx
├── table-header.tsx
├── table-body.tsx
├── table-row.tsx
├── table-cell.tsx
└── table.types.ts

src/features/<domain>/components/
├── <entity>-table.tsx           ← Domain-specific table wrapper
└── table-columns/
    ├── index.ts
    └── <entity>-columns.tsx     ← Column definitions
```

### Table Rules

*   **Shared Base:** Shared table components are generic and framework-agnostic
*   **Virtualization:** Tables with 100+ rows use virtualization
*   **Column Definitions:** Column configs are domain-owned and type-safe
*   **Sorting/Filtering:** Sorting and filtering are managed via React Query query keys
*   **Pagination:** Pagination uses query params and React Query
*   **Mobile Responsiveness:** Tables stack or scroll on mobile
*   **Accessibility:** Tables have proper headers, ARIA roles, and keyboard navigation

---

## 22. Modal & Drawer Structure

Modals and drawers are organized as domain components.

```
src/features/<domain>/components/modals/
├── index.ts
├── <entity>-create-modal.tsx    ← Domain-specific modal
└── <entity>-edit-modal.tsx

src/features/<domain>/components/drawers/
├── index.ts
└── <entity>-detail-drawer.tsx   ← Domain-specific drawer
```

### Modal & Drawer Rules

*   **Domain Ownership:** Modals are owned by the domain they serve
*   **Shared Modal Primitive:** Base modal component is in `src/shared/ui/`
*   **State Management:** Modal open/close state is managed via Zustand or URL params
*   **Trap Focus:** Modals trap focus and manage focus restoration
*   **Animations:** Modals animate in and out smoothly
*   **RTL Support:** Modals support RTL layout
*   **Mobile Optimization:** Modals are drawers on mobile

---

## 23. Mobile Component Structure

Mobile-specific components are organized separately.

```
src/features/<domain>/components/mobile/
├── index.ts
├── <entity>-mobile-card.tsx     ← Mobile-optimized card
└── <entity>-mobile-list.tsx     ← Mobile-optimized list

src/shared/ui/mobile/
├── index.ts
├── mobile-header.tsx
├── mobile-bottom-nav.tsx
└── mobile-sheet.tsx
```

### Mobile Component Rules

*   **Mobile-First:** All components are mobile-first, not mobile-added
*   **Touch Targets:** Touch targets are at least 44x44px
*   **One-Handed:** Layout allows one-handed operation on mobile
*   **Performance:** Mobile components are optimized for low-end hardware
*   **Offline:** Mobile components gracefully handle offline state
*   **Responsive Variants:** Shared components have mobile and desktop variants

---

## 24. Offline Layer Structure

Offline support is organized at the service and hook level.

```
src/shared/services/
├── index.ts
├── http-client.ts               ← HTTP client with offline fallback
└── offline-cache.ts             ← Offline data cache provider

src/features/<domain>/services/
├── <entity>-sync.ts             ← Domain-specific offline sync
└── __tests__/
    └── sync.test.ts
```

### Offline Rules

*   **Service Workers:** Handle offline sync and cache strategies
*   **Local Cache:** Offline-first reads from local cache
*   **Sync Queue:** Failed mutations are queued for later
*   **Stale Data Indicators:** UI shows staleness warnings when offline
*   **Graceful Degradation:** UI remains functional without network

---

## 25. Asset Organization Rules

Static assets are organized by type and domain.

```
public/
├── images/
│   ├── shared/
│   │   ├── logo.svg
│   │   └── icons/
│   └── domain-specific/
│       ├── farm/
│       └── harvest/
├── fonts/
├── locales/
├── config.json
└── manifest.json

src/assets/
├── illustrations/
├── icons/
└── animations/
```

### Asset Rules

*   **SVG Icons:** Icons are SVG files, not font icons
*   **Responsive Images:** Images are responsive and optimized
*   **No Large Assets:** Large assets are lazy-loaded or CDN-hosted
*   **Naming Convention:** Assets follow kebab-case naming
*   **Optimization:** All images are optimized before commit

---

## 26. Localization Structure

Localization (i18n) is centralized and domain-agnostic.

```
src/i18n/
├── index.ts
├── config.ts                    ← i18next configuration
├── locales/
│   ├── en/
│   │   ├── common.json
│   │   ├── forms.json
│   │   ├── errors.json
│   │   ├── farm.json
│   │   ├── harvest.json
│   │   └── equipment.json
│   ├── ar/
│   │   ├── common.json
│   │   ├── forms.json
│   │   └── (mirror structure)
│   └── fr/
└── __tests__/
    └── i18n.test.ts
```

### Localization Rules

*   **Namespace Strategy:** Each domain has its translation namespace
*   **Common Namespace:** Shared strings (buttons, labels) are in `common.json`
*   **RTL Support:** RTL languages (AR, HE) are fully supported
*   **Lazy Loading:** Translations are lazy-loaded per language
*   **Type Safety:** Translation keys are typed and validated
*   **No Inline Strings:** No hardcoded user-facing strings in code

---

## 27. Permission Layer Structure

Permission checks are centralized and role-aware.

```
src/shared/permissions/
├── index.ts
├── permission.types.ts          ← Permission and role types
├── use-permission.ts            ← Permission checking hook
└── permission-guard.tsx         ← Permission-aware render wrapper

src/features/<domain>/permissions/
├── index.ts
└── <domain>-permissions.ts      ← Domain-specific permission rules
```

### Permission Rules

*   **Centralized Checks:** Permission checks are not scattered in components
*   **Hook-Based:** Permissions are checked via `usePermission()` hook
*   **Guard Components:** Permission-aware rendering uses guard components
*   **No Hardcoding:** Roles are never hardcoded in components
*   **Runtime Config:** Permissions are fetched from backend at login

---

## 28. Error Handling Structure

Error handling is organized by scope and concern.

```
src/app/
├── error-boundary.tsx           ← Top-level error boundary

src/shared/errors/
├── index.ts
├── error-boundary.tsx           ← Reusable error boundary
├── error-handler.ts             ← Centralized error handling
├── error.types.ts               ← Error type definitions
└── __tests__/
    └── errors.test.ts

src/features/<domain>/errors/
├── index.ts
└── <domain>-error-handler.tsx   ← Domain-specific error rendering
```

### Error Handling Rules

*   **Error Boundaries:** Wrap pages and feature groups with error boundaries
*   **Typed Errors:** All errors are typed and categorized
*   **User-Facing Messages:** Errors show helpful, user-facing messages
*   **Recovery Options:** Error states provide recovery actions
*   **Logging:** Errors are logged for monitoring and debugging
*   **Offline Fallback:** Network errors show offline indicators

---

## 29. Testing Folder Strategy

Tests are co-located with source files.

```
src/features/<domain>/
├── components/
│   ├── <component>.tsx
│   ├── <component>.test.tsx
│   ├── __tests__/
│   │   ├── <component>.integration.test.tsx
│   │   └── snapshots/
│   └── index.ts
├── hooks/
│   ├── <hook>.ts
│   ├── <hook>.test.ts
│   └── index.ts
├── services/
│   ├── <service>.ts
│   ├── <service>.test.ts
│   └── index.ts
└── __tests__/
    ├── integration.test.ts
    ├── fixtures/
    │   ├── mock-data.ts
    │   └── mock-api.ts
    └── setup.ts
```

### Testing Rules

*   **Co-Location:** Test files live next to source files
*   **File Naming:** Test files use `.test.ts` or `.test.tsx`
*   **Test Fixtures:** Shared mock data is in `__tests__/fixtures/`
*   **Test Setup:** Test configuration is in `__tests__/setup.ts`
*   **Coverage:** Aim for 80%+ coverage on critical paths
*   **Isolation:** Tests are isolated and don't depend on external state

---

## 30. Storybook/Component Sandbox Strategy

Component stories are co-located with components.

```
src/shared/ui/button/
├── button.tsx
├── button.stories.tsx           ← Storybook stories
├── button.types.ts
└── __tests__/
    └── button.test.tsx

src/features/<domain>/components/
├── <component>.tsx
├── <component>.stories.tsx      ← Domain component stories
└── __tests__/
```

### Storybook Rules

*   **Co-Location:** Stories live next to components
*   **Responsive Stories:** Stories show mobile, tablet, desktop variants
*   **Accessibility Stories:** Stories test keyboard navigation and ARIA
*   **Theme Stories:** Stories show light and dark themes
*   **RTL Stories:** Stories show RTL layouts
*   **Live Updating:** Stories update live during development

---

## 31. Environment File Organization

Environment configuration is centralized and validated.

```
root/
├── .env.example                 ← Template for required vars
├── .env                         ← Local development (gitignored)
├── .env.test                    ← Test environment
├── .env.staging                 ← Staging environment
└── .env.production              ← Production environment

src/config/
├── index.ts
├── env.ts                       ← Environment variable validation
├── api.config.ts               ← API configuration
├── theme.config.ts             ← Theme configuration
└── feature-flags.config.ts      ← Feature flag configuration
```

### Environment Rules

*   **Validation:** Environment variables are validated at startup
*   **Type Safety:** Env vars are typed and accessed via config module
*   **No Hardcoding:** No API URLs or secrets in code
*   **Feature Flags:** Feature flags are environment-dependent
*   **Build-Time Config:** Build-time vars are baked into the bundle

---

## 32. Build & Config Structure

Build configuration is organized and maintainable.

```
root/
├── vite.config.ts              ← Vite build configuration
├── tailwind.config.ts          ← Tailwind CSS configuration
├── postcss.config.ts           ← PostCSS configuration
├── eslint.config.js            ← ESLint configuration
├── prettier.config.js          ← Prettier configuration
├── tsconfig.json               ← TypeScript configuration
├── vitest.config.ts            ← Vitest configuration
└── .husky/
    └── pre-commit              ← Git hooks for linting
```

### Build Rules

*   **Minimal Config:** Build config is kept minimal and documented
*   **Path Aliases:** Use `@/` for absolute imports instead of relative paths
*   **Source Maps:** Source maps are generated for debugging
*   **Tree Shaking:** Unused code is tree-shaken from bundles
*   **Code Splitting:** Code is split by route and lazy-loaded

---

## 33. Barrel Export Rules

Barrel exports control the public API of each folder.

### Barrel File Pattern

Every folder with multiple exports has an `index.ts` barrel:

```typescript
// src/features/farm/index.ts
export { FarmListPage } from './pages';
export { useFarmList, useFarmDetail } from './hooks';
export { useFarmUIStore } from './stores';
export { farmApi } from './services';
export type { Farm, FarmDTO } from './types';
```

### Barrel Rules

*   **Folder API:** Each folder's public API is defined in `index.ts`
*   **No Internal Exports:** Internal files (prefixed with `_`) are not exported
*   **Explicit Exports:** Only explicitly exported items are public
*   **No Re-Export Chains:** Avoid exporting from `../index` in nested files
*   **Organized Exports:** Group imports by concern (pages, hooks, stores, etc.)

### Forbidden Barrel Pattern

```typescript
// ❌ FORBIDDEN: Exporting everything indiscriminately
export * from './utils/internal-helpers';
export * from './hooks/_private-hooks';

// ✅ ALLOWED: Explicit, curated exports
export { publicHelper } from './utils/helpers';
export { usePublicHook } from './hooks/use-public-hook';
```

---

## 34. Import Direction Rules

Imports flow unidirectionally from outer to inner layers.

### Import Direction Hierarchy

```
App Shell
    ↓
Routes / Layouts (depends on)
    ↓
Pages (depends on)
    ↓
Features / Domains (depends on)
    ↓
Shared (depends on nothing)
```

### Import Rules

✅ **ALLOWED:**
```typescript
// Pages can import from features
import { FarmListPage } from 'src/features/farm/pages';

// Features can import from shared
import { useQueryParams } from 'src/shared/hooks';

// Features can import from their own domain
import { useFarmStore } from 'src/features/farm/stores';

// Features can import from sibling domain via public API
import { HarvestPageType } from 'src/features/harvest';
```

❌ **FORBIDDEN:**
```typescript
// Shared cannot import from features
import { useFarmQuery } from 'src/features/farm/hooks';  // ❌

// Features cannot import from sibling feature internals
import { _internalHelper } from 'src/features/harvest/utils/_helpers'; // ❌

// Features cannot cross-import private modules
import { FarmStore } from 'src/features/farm/stores/farm-store'; // ❌
// Instead: import { FarmStore } from 'src/features/farm'; ✅

// Pages cannot import from other pages
import { HarvestListPage } from 'src/pages/harvest-list-page'; // ❌
```

### Import Path Rules

*   **Absolute Imports:** Use `src/` prefix for all imports (via Vite path alias)
*   **No Relative Imports:** Avoid `../` relative paths (harder to refactor)
*   **Barrel Imports:** Import from barrel files, not internal modules
*   **Path Aliases:** Use `@/` for imports from `src/`

---

## 35. Performance Constraints

Frontend performance is optimized at the structure level.

### Performance Rules

*   **Lazy Loading:** Routes and heavy components are lazy-loaded
*   **Code Splitting:** Code is split by domain and route
*   **Bundle Size:** Target < 500KB gzipped for initial load
*   **Virtualization:** Long lists (100+ items) use virtualization
*   **Image Optimization:** Images are optimized and responsive
*   **Memoization:** Expensive computations are memoized
*   **Query Caching:** React Query caches results aggressively
*   **Offline-First:** App remains functional without network

### Lighthouse Targets

*   Performance: ≥ 90
*   Accessibility: ≥ 95
*   Best Practices: ≥ 90
*   SEO: ≥ 90

---

## 36. AI Safety Rules

These rules prevent AI agents from corrupting the frontend architecture.

### AI Safety Constraints

AI must NOT:
*   ❌ Create giant `utils/` or `hooks/` folders
*   ❌ Put domain-specific hooks in `shared/hooks/`
*   ❌ Import from private domain modules (use barrel only)
*   ❌ Create cross-domain dependencies
*   ❌ Duplicate code across features
*   ❌ Embed business logic in UI components
*   ❌ Create circular dependencies
*   ❌ Use deep prop drilling instead of state management
*   ❌ Mix infrastructure and UI concerns
*   ❌ Hardcode role or permission checks
*   ❌ Create shared state for domain-specific data
*   ❌ Mutate domain entity types in shared types
*   ❌ Bypass barrel exports with internal imports
*   ❌ Create routes outside the domain route system
*   ❌ Put fetching logic directly in components

AI MUST:
*   ✅ Respect folder boundaries and isolation
*   ✅ Use barrel exports exclusively
*   ✅ Keep shared code truly generic
*   ✅ Put domain-specific code in domain folders
*   ✅ Use hooks for reusable behavior
*   ✅ Use Zustand for state management
*   ✅ Use React Query for server state
*   ✅ Extract side effects into services
*   ✅ Maintain unidirectional imports
*   ✅ Test new code before generating

---

## 37. Forbidden Frontend Anti-Patterns

These patterns are strictly prohibited and will be flagged in code reviews.

### Anti-Pattern: Giant Utils Folder

```typescript
// ❌ FORBIDDEN
src/shared/utils/
├── formatFarmName.ts
├── calculateHarvestYield.ts
├── validateFarmBoundary.ts
├── transformFarmAPIResponse.ts
├── syncFarmWithServer.ts
├── ...50 more domain-specific files

// ✅ ALLOWED
src/features/farm/utils/
├── format.ts
├── validators.ts
├── calculations.ts
└── sync.ts
```

### Anti-Pattern: Cross-Domain Imports

```typescript
// ❌ FORBIDDEN
// src/features/harvest/hooks/useHarvest.ts
import { useFarmQuery } from 'src/features/farm/hooks/useFarmQuery';

// ✅ ALLOWED
// Import from shared contracts instead
import { Farm } from 'src/shared/contracts/farm';
```

### Anti-Pattern: Shared Hooks for Domain Logic

```typescript
// ❌ FORBIDDEN
// src/shared/hooks/useFarmList.ts
export const useFarmList = () => {
  return useQuery({
    queryKey: ['farms'],
    queryFn: () => farmApi.list(),
  });
};

// ✅ ALLOWED
// src/features/farm/hooks/useFarmList.ts
export const useFarmList = () => {
  return useQuery({
    queryKey: FARM_QUERY_KEYS.list(),
    queryFn: () => farmApi.list(),
  });
};
```

### Anti-Pattern: Business Logic in Components

```typescript
// ❌ FORBIDDEN
function FarmCard({ farm }) {
  const calculateArea = () => {
    // Complex business logic in component
    const area = farm.sectors.reduce((sum, s) => sum + s.area, 0);
    return area > 1000 ? 'Large' : 'Small';
  };
  return <div>{calculateArea()}</div>;
}

// ✅ ALLOWED
// Extract to service/hook
const useFarmSize = (farm) => {
  return useMemo(() => {
    const area = farm.sectors.reduce((sum, s) => sum + s.area, 0);
    return area > 1000 ? 'Large' : 'Small';
  }, [farm]);
};

function FarmCard({ farm }) {
  const size = useFarmSize(farm);
  return <div>{size}</div>;
}
```

### Anti-Pattern: Circular Dependencies

```typescript
// ❌ FORBIDDEN
// src/features/farm/hooks/useFarm.ts
import { useHarvest } from 'src/features/harvest/hooks';

// src/features/harvest/hooks/useHarvest.ts
import { useFarm } from 'src/features/farm/hooks';

// ✅ ALLOWED: Communicate via shared types/events
// src/shared/contracts/farm.ts
export interface Farm { id: string; /* ... */ }

// Each domain imports types, not implementations
```

### Anti-Pattern: Deeply Nested Relative Imports

```typescript
// ❌ FORBIDDEN
import { Component } from '../../../components/deep/nested/path/Component';

// ✅ ALLOWED: Use absolute imports with path aliases
import { Component } from 'src/features/farm/components';
```

---

## 38. Real Agricultural Frontend Scenarios

These scenarios demonstrate correct folder structure and import patterns.

### Scenario 1: Harvest Reporting Workflow

A user navigates from a farm summary to a harvest report, selects multiple workers, and submits yield data.

**Structure:**
```
src/features/harvest/
├── pages/
│   ├── harvest-list-page.tsx
│   └── harvest-detail-page.tsx
├── components/
│   ├── harvest-table.tsx
│   ├── harvest-form.tsx
│   ├── worker-selector.tsx
│   └── yield-input.tsx
├── hooks/
│   ├── use-harvest-list.ts
│   ├── use-harvest-detail.ts
│   └── use-harvest-mutation.ts
├── stores/
│   ├── harvest-ui-store.ts  (selected workers, filters)
│   └── harvest-form-store.ts (form state across pages)
├── services/
│   ├── harvest-api.ts
│   └── harvest-sync.ts
├── types/
│   ├── harvest.ts
│   └── api.ts
└── layouts/
    └── harvest-layout.tsx
```

**Import Flow:**
```typescript
// Harvest page imports from domain
import { HarvestListPage } from 'src/features/harvest/pages';

// Page imports domain components and hooks
import { HarvestTable } from 'src/features/harvest/components';
import { useHarvestList } from 'src/features/harvest/hooks';
import { useFarmContext } from 'src/shared/hooks';

// Component imports shared UI primitives
import { Button, Table } from 'src/shared/ui';

// Hook imports from services
import { harvestApi } from 'src/features/harvest/services';

// Service imports shared HTTP client
import { httpClient } from 'src/shared/services';
```

### Scenario 2: White-Label Equipment Dashboard

A white-label tenant customizes their equipment dashboard with brand colors and custom columns.

**Structure:**
```
src/
├── shared/
│   ├── theme/
│   │   ├── tokens.ts  (customizable color tokens)
│   │   └── theme-provider.tsx
│   └── ui/
│       └── dashboard-layout.tsx  (generic dashboard wrapper)
├── features/equipment/
│   ├── pages/
│   │   └── equipment-dashboard-page.tsx
│   ├── components/
│   │   ├── equipment-table.tsx
│   │   └── equipment-chart.tsx
│   ├── layouts/
│   │   └── equipment-dashboard-layout.tsx  (domain wrapper)
│   ├── hooks/
│   │   ├── use-equipment-list.ts
│   │   └── use-equipment-analytics.ts
│   └── stores/
│       └── equipment-ui-store.ts  (column preferences, filters)
└── config/
    └── theme.config.ts  (tenant-specific theme)
```

**White-Label Implementation:**
```typescript
// App.tsx
import { themeConfig } from 'src/config/theme.config';

export function App() {
  return (
    <ThemeProvider tokens={themeConfig.tokens}>
      {/* Routes */}
    </ThemeProvider>
  );
}

// Component uses theme tokens dynamically
function EquipmentChart() {
  const { colors } = useTheme();
  return (
    <Chart
      colors={{
        primary: colors.primary,  // Tenant-specific color
        secondary: colors.secondary,
      }}
    />
  );
}
```

### Scenario 3: Offline-First Mobile Operations

A worker disconnects from the network, still views and creates operations, then syncs when reconnected.

**Structure:**
```
src/features/operations/
├── services/
│   ├── operations-api.ts  (API calls)
│   └── operations-sync.ts (offline queue and sync)
├── hooks/
│   ├── use-operations-list.ts  (cached queries)
│   ├── use-operations-mutation.ts  (optimistic updates)
│   └── use-offline-status.ts  (offline indicator)
├── stores/
│   ├── operations-ui-store.ts  (UI state)
│   └── operations-sync-store.ts  (sync queue state)
└── components/
    ├── operations-list.tsx
    ├── operation-form.tsx
    └── offline-indicator.tsx
```

**Offline Flow:**
```typescript
// Service handles offline queuing
export const operationsSync = {
  async createOperation(data) {
    if (navigator.onLine) {
      return operationsApi.create(data);
    } else {
      // Queue for later
      await offlineCache.queue('operations:create', data);
    }
  },
};

// Component shows offline UI
function OperationForm() {
  const { isOnline } = useOfflineStatus();
  const { mutate, isPending } = useCreateOperation();

  return (
    <>
      {!isOnline && <OfflineIndicator />}
      <Button disabled={isPending}>{isOnline ? 'Save' : 'Queue'}</Button>
    </>
  );
}
```

---

## 39. Future Scalability Strategy

As ATLS grows, the frontend architecture must scale gracefully.

### Scalability Patterns

*   **Monorepo → Monolith:** Individual domains can be extracted into separate packages or repos
*   **Lazy Domains:** Domains can be lazy-loaded and code-split by route
*   **Tenant-Specific Domains:** Tenant-specific features can be isolated and white-labeled
*   **Feature Flags:** Entire domains can be hidden behind feature flags
*   **Micro-Frontends:** Domains can be deployed as separate micro-frontends if needed

### Growth Phases

**Phase 1 (Current):** Monolithic React app with domain-isolated features
```
src/features/
├── farm/
├── harvest/
├── equipment/
└── ...
```

**Phase 2:** Lazy-loaded feature packages
```
src/
├── features/
├── packages/
│   ├── farm-package/
│   ├── harvest-package/
│   └── equipment-package/
└── ...
```

**Phase 3:** Independently deployable features (micro-frontends)
```
apps/
├── shell/
├── farm-module/
├── harvest-module/
└── equipment-module/
```

---

## 40. Final Frontend Structure Enforcement Checklist

Use this checklist during architecture reviews and code generation.

### Folder Organization ✓

- [ ] Each domain has an `index.ts` barrel exporting its public API
- [ ] Internal files are prefixed with `_` and not exported
- [ ] No giant folders (max 20 files per folder, max 5 levels deep)
- [ ] Shared code is truly domain-agnostic
- [ ] No shared folders containing domain-specific logic

### Import Direction ✓

- [ ] All imports use absolute paths (`src/...`), not relative paths
- [ ] Features import from shared, shared imports from nothing
- [ ] Cross-domain imports go through barrels and shared contracts only
- [ ] No direct imports from internal domain modules
- [ ] No circular dependencies between domains or features

### Domain Isolation ✓

- [ ] Each domain owns its pages, hooks, state, services, and types
- [ ] Domain types are not duplicated in shared types
- [ ] Domain services are not used by other domains
- [ ] Cross-domain communication goes through shared contracts and APIs
- [ ] No shared state for domain-specific data

### Shared Layer ✓

- [ ] Shared UI components are stateless and brand-agnostic
- [ ] Shared hooks are utility-only, not domain-specific
- [ ] Shared utils are pure functions, no side effects
- [ ] Shared types are primitives and generics, not entities
- [ ] Shared stores contain only auth, theme, notifications

### Code Quality ✓

- [ ] All files have clear, documented purposes
- [ ] Business logic is extracted from components into hooks and services
- [ ] All components are tested with unit and integration tests
- [ ] TypeScript is strict (no `any` types without justification)
- [ ] Components follow accessibility guidelines (WCAG 2.1 AA)

### Performance ✓

- [ ] Routes are lazy-loaded via React Router
- [ ] Code is split by domain and route
- [ ] Large lists are virtualized
- [ ] Images are optimized and responsive
- [ ] Unused dependencies are not imported

### AI Safety ✓

- [ ] No code generation violates domain boundaries
- [ ] No utility function dumping in shared folders
- [ ] No circular dependencies introduced
- [ ] No hardcoded role or permission checks
- [ ] No direct fetch calls without HTTP client

### Documentation ✓

- [ ] Folder purposes are clear from structure
- [ ] Public APIs are documented via barrel files
- [ ] Complex logic has JSDoc comments
- [ ] README files explain domain purposes
- [ ] This FOLDER_STRUCTURE.md is up to date

---

## Summary

The ATLS frontend is a **domain-isolated modular monolith** organized by business capabilities, not technical layers. Shared code is minimized, imports flow unidirectionally, and each domain is a self-contained vertical slice. This structure enables AI agents to safely generate code, teams to work independently, and the platform to scale gracefully.
