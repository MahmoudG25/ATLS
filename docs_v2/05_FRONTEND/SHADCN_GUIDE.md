# SHADCN GUIDE

## Purpose
Define authoritative shadcn/ui governance for ATLS frontend, establishing component ownership rules, wrapper strategy, shared UI primitive governance, domain extension patterns, and AI-safe customization constraints. This document ensures consistent, maintainable, accessible shadcn component usage while preventing uncontrolled duplication, inline overrides, and component inconsistency across agricultural ERP workflows.

## Scope
Covers shadcn/ui ownership rules, wrapper component strategy, shared UI primitives architecture, domain extension governance, variant system rules, design token integration, accessibility guarantees, mobile-first component behavior, RTL compatibility, dialog governance, form governance, table governance, drawer/mobile sheet governance, data display standards, loading/skeleton standards, error/empty state standards, toast/notification standards, command palette architecture, sidebar/navigation standards, controlled customization rules, AI-safe extension rules, and real agricultural ERP examples.

## Current Status
- [x] Not Started
- [ ] In Progress
- [x] Completed

## Dependencies
- `docs_v2/02_FRONTEND/TAILWIND_RULES.md`
- `docs_v2/02_FRONTEND/DESIGN_SYSTEM.md`
- `docs_v2/05_FRONTEND/COMPONENT_ARCHITECTURE.md`
- `docs_v2/07_AI_AGENT/AI_DEVELOPMENT_RULES.md`

## Notes
shadcn/ui is the primary component library for ATLS. All shadcn components are treated as immutable base primitives. Domain-specific customization flows through wrapper components and variant systems. Direct node_modules modification is forbidden. Component consistency is enforced through strict governance.

## Last Updated
2026-05-12

---

## 1. Component Ownership Rules

**RULE:** shadcn/ui components are base primitives owned by the system. Domain teams own wrappers, not core components.

**Ownership Hierarchy:**
1. **System Level (shadcn/ui):** Base unstyled/minimally styled components
2. **Wrapper Level (src/components/ui):** Branded wrappers enforcing ATLS design
3. **Domain Level (src/features/[domain]):** Domain-specific extensions
4. **Page Level (src/pages):** Page composition and orchestration

**Ownership Rules:**
- **Do Not Modify:** shadcn components in `node_modules`
- **Do Not Duplicate:** Never copy shadcn components; always wrap
- **Do Own:** Wrapper components that enforce ATLS branding
- **Do Own:** Domain-specific extensions and variants
- **Do Coordinate:** Cross-domain component needs through architecture review

**Example: Button Ownership**
```jsx
// 1. shadcn/ui Base (NEVER modify)
// node_modules/@shadcn/ui/components/button/Button.tsx
export const Button = forwardRef(({ ...props }, ref) => (
  <button ref={ref} {...props} />
))

// 2. ATLS Wrapper (wrapper level)
// src/components/ui/Button.tsx
import { Button as ShadcnButton } from '@/components/shadcn/button'
import { cn } from '@/lib/utils'

export const Button = forwardRef(({ variant = 'primary', size = 'md', ...props }, ref) => (
  <ShadcnButton
    ref={ref}
    className={cn(
      'font-medium transition-colors',
      variant === 'primary' && 'bg-primary text-white hover:bg-primary-dark',
      variant === 'secondary' && 'bg-secondary text-white hover:bg-secondary-dark',
      size === 'md' && 'px-4 py-2',
      size === 'lg' && 'px-6 py-3',
    )}
    {...props}
  />
))

// 3. Domain Extension (domain level)
// src/features/olive/components/HarvestButton.tsx
export const HarvestButton = (props) => (
  <Button variant="primary" size="lg" {...props}>
    Start Harvest
  </Button>
)

// 4. Usage (page level)
import { HarvestButton } from '@/features/olive/components'
<HarvestButton onClick={startHarvest} />
```

---

## 2. Wrapper Component Strategy

**RULE:** All shadcn components must be wrapped at the UI layer. Wrappers enforce ATLS design, accessibility, and mobile-first behavior.

**Wrapper Architecture:**
```
src/components/ui/
  ├── Button.tsx          (wrapper enforcing ATLS button rules)
  ├── Dialog.tsx          (wrapper for modal governance)
  ├── Form.tsx            (wrapper for form governance)
  ├── Table.tsx           (wrapper for table governance)
  ├── Input.tsx           (wrapper enforcing input standards)
  ├── Select.tsx          (wrapper enforcing select standards)
  ├── Card.tsx            (wrapper enforcing card standards)
  ├── Tabs.tsx            (wrapper enforcing tab standards)
  ├── Toast.tsx           (wrapper for notification governance)
  └── [component].tsx     (wrapper for all shadcn components)
```

**Wrapper Template:**
```jsx
// src/components/ui/[Component].tsx
import { [Component] as Shadcn[Component] } from '@/components/shadcn/[component]'
import { cn } from '@/lib/utils'

/**
 * ATLS [Component] - Wrapper enforcing ATLS design standards
 * 
 * - Mobile-first responsive behavior
 * - RTL-aware rendering
 * - Dark mode support
 * - Accessibility compliance
 * - ATLS design tokens
 */
export const [Component] = forwardRef((
  { className, variant = 'default', size = 'md', ...props },
  ref
) => {
  return (
    <Shadcn[Component]
      ref={ref}
      className={cn(
        // ATLS base styles
        'transition-colors duration-200',
        // Variant styles
        variant === 'primary' && 'bg-primary text-white hover:bg-primary-dark',
        // Size styles
        size === 'md' && 'px-4 py-2 text-base',
        // Mobile-first responsive
        'md:px-6 md:py-3',
        // Dark mode
        'dark:hover:bg-primary-dark',
        // Custom overrides
        className
      )}
      {...props}
    />
  )
})

[Component].displayName = '[Component]'
```

**Wrapper Rules:**
- Always accept `className` prop for composition
- Always apply `dark:` utilities
- Always include responsive variants
- Always ensure accessibility attributes
- Always use `forwardRef` for native elements
- Always set `displayName` for debugging

---

## 3. Shared UI Primitives

**RULE:** Shared UI primitives are generic, reusable, brand-enforcing components in `src/components/ui`.

**Primitive Categories:**

### Layout Primitives
- **Card:** Content container with shadow and padding
- **Container:** Max-width wrapper with mobile padding
- **Stack:** Flex column with consistent gap
- **Grid:** Grid layout with responsive columns
- **Divider:** Semantic separator

### Input Primitives
- **Input:** Text input with validation states
- **Select:** Dropdown with search (shadcn)
- **Checkbox:** Toggle option
- **Radio:** Single selection from group
- **Switch:** Boolean toggle
- **Textarea:** Multi-line text input

### Display Primitives
- **Badge:** Status/tag display
- **Chip:** Removable tag or category
- **Avatar:** User/entity image display
- **Skeleton:** Loading placeholder
- **Spinner:** Loading indicator
- **Progress:** Progress bar or ring

### Overlay Primitives
- **Dialog:** Modal dialog
- **Drawer:** Slide-out panel (mobile bottom sheet)
- **Popover:** Floating content container
- **Tooltip:** Hover information
- **Toast:** Notification message

### Navigation Primitives
- **Button:** CTA button
- **Link:** Semantic link
- **Breadcrumb:** Navigation path
- **Tabs:** Tab navigation
- **Menu:** Dropdown menu

**Primitive Usage:**
```jsx
// GOOD: Using primitives for composition
<Card className="p-4">
  <Stack gap={4}>
    <h2 className="text-xl font-bold">Field Data</h2>
    <Input
      label="Field Name"
      type="text"
      required
    />
    <Select
      label="Field Type"
      options={fieldTypes}
      required
    />
    <Stack gap={2} direction="row" justifyContent="end">
      <Button variant="secondary">Cancel</Button>
      <Button variant="primary">Save</Button>
    </Stack>
  </Stack>
</Card>

// BAD: Creating custom containers
<div style={{border: '1px solid #e5e7eb', padding: '16px', borderRadius: '8px'}}>
  <div style={{display: 'flex', flexDirection: 'column', gap: '16px'}}>
    {/* Content */}
  </div>
</div>
```

---

## 4. Domain Extension Rules

**RULE:** Domains extend shared primitives for domain-specific needs. Extensions own variants, composition, and orchestration.

**Extension Architecture:**
```
src/features/[domain]/components/
  ├── ui/
  │   ├── [DomainButton].tsx     (domain-specific button)
  │   ├── [DomainCard].tsx       (domain-specific card)
  │   └── [DomainForm].tsx       (domain-specific form)
  ├── dialogs/
  │   ├── [ActionDialog].tsx
  │   └── [ConfirmDialog].tsx
  └── widgets/
      ├── [DataWidget].tsx
      └── [KPIWidget].tsx
```

**Extension Pattern:**
```jsx
// GOOD: Domain extension wrapping primitive
// src/features/olive/components/ui/OliveFieldCard.tsx
import { Card } from '@/components/ui/Card'
import { Stack } from '@/components/ui/Stack'
import { Badge } from '@/components/ui/Badge'

export const OliveFieldCard = ({ field, onSelect }) => (
  <Card
    className="cursor-pointer hover:shadow-lg transition-shadow"
    onClick={onSelect}
  >
    <Stack gap={3}>
      <div className="flex justify-between items-start">
        <h3 className="text-lg font-semibold">{field.name}</h3>
        <Badge variant={getHealthStatus(field)}>
          {getHealthLabel(field)}
        </Badge>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <MetricDisplay label="Area" value={field.area} unit="ha" />
        <MetricDisplay label="Moisture" value={field.moisture} unit="%" />
      </div>
    </Stack>
  </Card>
)

// Forbidden: Duplicating shadcn component
// DO NOT DO THIS
export const OliveFieldCard = ({ field }) => (
  <div className="border rounded-lg p-4 shadow">
    {/* Reinventing Card */}
  </div>
)
```

**Extension Rules:**
- Extensions compose primitives, never duplicate them
- Extensions own domain-specific styling and variants
- Extensions include domain-specific props and behaviors
- Extensions maintain accessibility and mobile-first design
- Extensions are exported from `index.ts` for clarity

---

## 5. Variant System Architecture

**RULE:** Variants are the primary mechanism for customization. Variant logic is centralized and typed.

**Variant Pattern:**
```jsx
// src/components/ui/Button.tsx
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const buttonVariants = cva(
  // Base styles
  'inline-flex items-center justify-center rounded-lg font-medium transition-colors cursor-pointer',
  {
    variants: {
      // Variant type
      variant: {
        primary: 'bg-primary text-white hover:bg-primary-dark',
        secondary: 'bg-secondary text-white hover:bg-secondary-dark',
        outline: 'border border-gray-300 text-gray-900 hover:bg-gray-50',
        ghost: 'text-gray-900 hover:bg-gray-100',
        danger: 'bg-error text-white hover:bg-error-dark',
      },
      // Size variant
      size: {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2 text-base',
        lg: 'px-6 py-3 text-lg',
      },
      // Disabled state
      disabled: {
        true: 'opacity-50 cursor-not-allowed',
        false: '',
      },
    },
    compoundVariants: [
      {
        variant: 'outline',
        disabled: true,
        className: 'border-gray-200',
      },
    ],
    defaultVariants: {
      variant: 'primary',
      size: 'md',
      disabled: false,
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
  VariantProps<typeof buttonVariants> {}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant, size, disabled, className, ...props }, ref) => (
    <button
      ref={ref}
      disabled={disabled}
      className={cn(buttonVariants({ variant, size, disabled }), className)}
      {...props}
    />
  )
)

Button.displayName = 'Button'
```

**Variant Usage:**
```jsx
// Primary button
<Button variant="primary" size="md">Save</Button>

// Secondary button with custom class
<Button variant="secondary" className="w-full">Submit</Button>

// Ghost button
<Button variant="ghost">Cancel</Button>

// Disabled state
<Button disabled>Loading...</Button>
```

**Variant Rules:**
- Variants are typed using CVA or similar library
- Variants prevent arbitrary className usage
- Variants are documented and exported
- Compound variants combine base + size + state
- Domain extensions add variants, never override base

---

## 6. Design Token Integration

**RULE:** All shadcn components must use ATLS design tokens. Hardcoded colors are forbidden.

**Token Integration:**
```jsx
// tailwind.config.js
export default {
  theme: {
    colors: {
      primary: 'var(--color-primary)',
      'primary-light': 'var(--color-primary-light)',
      'primary-dark': 'var(--color-primary-dark)',
      secondary: 'var(--color-secondary)',
      neutral: {
        bg: 'var(--color-neutral-bg)',
        text: 'var(--color-neutral-text)',
      },
      status: {
        success: 'var(--color-status-success)',
        error: 'var(--color-status-error)',
        warning: 'var(--color-status-warning)',
      },
    },
  },
}
```

**Token Application in Components:**
```jsx
// GOOD: Using tokens
<button className="bg-primary hover:bg-primary-dark text-white">
  Submit
</button>

// BAD: Hardcoded colors
<button className="bg-[#2563eb] hover:bg-[#1d4ed8]">
  Submit
</button>
```

**Theme Override for White-Label:**
```jsx
// Apply custom branding tokens
export const applyBrandingTokens = (branding) => {
  const root = document.documentElement
  root.style.setProperty('--color-primary', branding.primaryColor)
  root.style.setProperty('--color-primary-dark', branding.primaryDarkColor)
  root.style.setProperty('--color-secondary', branding.secondaryColor)
}
```

---

## 7. Accessibility Guarantees

**RULE:** All shadcn components must include accessibility features. Components without WCAG AA compliance fail review.

**Accessibility Features:**

### Dialog Accessibility
```jsx
<Dialog>
  <DialogTrigger asChild>
    <Button>Open</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Confirm Action</DialogTitle>
      <DialogDescription>
        This action cannot be undone.
      </DialogDescription>
    </DialogHeader>
    {/* Content */}
  </DialogContent>
</Dialog>
```

### Form Accessibility
```jsx
<form>
  <label htmlFor="field-input" className="text-sm font-medium">
    Field Name <span aria-label="required" className="text-error">*</span>
  </label>
  <Input
    id="field-input"
    aria-required="true"
    aria-invalid={hasError}
    aria-describedby={hasError ? 'error-msg' : undefined}
  />
  {hasError && (
    <p id="error-msg" className="text-error text-sm" role="alert">
      This field is required
    </p>
  )}
</form>
```

### Keyboard Navigation
- All interactive elements are keyboard accessible
- Focus indicators are visible
- Tab order is logical
- Escape key closes modals/popovers

### Screen Reader Support
- Semantic HTML structure
- ARIA labels and descriptions
- Role attributes where needed
- Status messages announced

**Accessibility Checklist:**
- [ ] Component passes axe-core audit
- [ ] Keyboard navigation works
- [ ] Focus indicators visible
- [ ] Color contrast ≥ 4.5:1 (text), ≥ 3:1 (UI)
- [ ] ARIA attributes correct
- [ ] Screen reader tested

---

## 8. Mobile-First Component Behavior

**RULE:** All shadcn components must behave correctly on mobile. Mobile UX is primary.

**Mobile Behavior Rules:**

### Button Sizing
```jsx
// GOOD: Touch-friendly sizes
<Button className="py-3 px-4">  {/* 48px height minimum */}
  Submit
</Button>

// BAD: Small touch targets
<button className="py-1 px-2">  {/* 24px height - too small */}
  Submit
</button>
```

### Dialog on Mobile
```jsx
// GOOD: Full-screen on mobile, centered on desktop
<DialogContent className="
  flex flex-col max-h-screen overflow-y-auto
  md:max-h-[90vh] md:rounded-lg
  rounded-none md:rounded-lg
">
  {/* Content */}
</DialogContent>

// BAD: Desktop dialog on mobile
<DialogContent className="rounded-lg">
  {/* Too small on mobile */}
</DialogContent>
```

### Input Sizing
```jsx
// GOOD: Large tap targets
<Input className="h-12 px-4 py-3 text-base" />

// BAD: Small on mobile
<Input className="h-8 px-2 py-1 text-sm" />
```

### Responsive Variants
```jsx
// GOOD: Mobile-first responsive
<button className="text-sm md:text-base py-2 md:py-3">
  Action
</button>

// BAD: Static sizes
<button style={{padding: '8px 16px', fontSize: '12px'}}>
  Action
</button>
```

---

## 9. RTL Compatibility

**RULE:** All shadcn components must be RTL-aware. Components in Arabic must mirror correctly.

**RTL Utilities:**
- `start`/`end` instead of `left`/`right`
- `ps-` (padding-start) instead of `pl-`
- `pe-` (padding-end) instead of `pr-`
- `ms-` (margin-start) instead of `ml-`
- `me-` (margin-end) instead of `mr-`

**RTL Component Wrapper:**
```jsx
// src/components/ui/Button.tsx
export const Button = forwardRef(({ ...props }, ref) => (
  <button
    ref={ref}
    className={cn(
      'px-4 py-2 bg-primary text-white rounded-lg',
      'rtl:flex-row-reverse',  // Reverse flex for RTL
      props.className
    )}
    {...props}
  />
))
```

**Icon Mirroring in RTL:**
```jsx
// Component with icon
<Button>
  <ChevronIcon className="me-2 rtl:scale-x-[-1]" />
  <span>Next</span>
</Button>

// RTL automatically mirrors icon
```

**Dialog RTL:**
```jsx
<DialogContent className="
  rtl:flex-row-reverse
  rtl:text-right
">
  <DialogHeader>
    <DialogTitle>Title</DialogTitle>
  </DialogHeader>
</DialogContent>
```

---

## 10. Dialog Governance

**RULE:** Dialogs are modals for confirmed actions and user decisions. Dialog usage follows strict rules.

**Dialog Rules:**
- Dialogs require explicit user action (click button to confirm/cancel)
- Dialogs are not used for errors (use toast instead)
- Dialogs must have clear title and description
- Dialogs must have action buttons
- Dialogs are full-screen on mobile, centered on desktop
- Dialogs include keyboard support (Escape to close)

**Dialog Template:**
```jsx
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { useState } from 'react'

export const ConfirmDialog = ({ title, description, onConfirm, onCancel }) => {
  const [open, setOpen] = useState(false)
  
  const handleConfirm = async () => {
    await onConfirm()
    setOpen(false)
  }
  
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          {description && (
            <DialogDescription>{description}</DialogDescription>
          )}
        </DialogHeader>
        <DialogFooter className="flex gap-2 md:flex-row-reverse">
          <Button variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleConfirm}>
            Confirm
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
```

**Dialog Usage Examples:**
```jsx
// Harvest confirmation
<ConfirmDialog
  title="Start Harvest"
  description="Are you sure you want to start harvesting this field?"
  onConfirm={startHarvest}
/>

// Field deletion
<ConfirmDialog
  title="Delete Field"
  description="This action cannot be undone. All related data will be deleted."
  onConfirm={deleteField}
/>
```

---

## 11. Form Governance

**RULE:** Forms use shadcn form with React Hook Form for state management. Forms are strongly typed and accessible.

**Form Architecture:**
```jsx
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

const fieldSchema = z.object({
  name: z.string().min(1, 'Field name is required'),
  area: z.string().regex(/^\d+(\.\d{1,2})?$/, 'Valid area required'),
  fieldType: z.string().min(1, 'Field type is required'),
})

type FieldFormValues = z.infer<typeof fieldSchema>

export const FieldForm = ({ onSubmit }) => {
  const form = useForm<FieldFormValues>({
    resolver: zodResolver(fieldSchema),
    defaultValues: {
      name: '',
      area: '',
      fieldType: '',
    },
  })
  
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="flex flex-col gap-4">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Field Name</FormLabel>
              <FormControl>
                <Input placeholder="e.g., Olive Field North" {...field} />
              </FormControl>
              <FormDescription>Unique identifier for the field</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        
        <Button type="submit" disabled={form.formState.isSubmitting}>
          {form.formState.isSubmitting ? 'Saving...' : 'Save Field'}
        </Button>
      </form>
    </Form>
  )
}
```

**Form Rules:**
- All form fields are strongly typed with Zod
- All forms use React Hook Form
- All forms include validation messages
- All forms support loading states
- All forms are accessible (labels, descriptions, error messages)
- Mobile forms stack vertically

---

## 12. Table Governance

**RULE:** Tables display data with sorting, filtering, and responsive mobile cards. Tables are the data display standard.

**Table Architecture:**
```jsx
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { useMemo, useState } from 'react'

export const FieldsTable = ({ fields }) => {
  const [sortBy, setSortBy] = useState('name')
  const [sortDir, setSortDir] = useState('asc')
  
  const sortedFields = useMemo(() => {
    return [...fields].sort((a, b) => {
      const aVal = a[sortBy]
      const bVal = b[sortBy]
      return sortDir === 'asc' 
        ? aVal > bVal ? 1 : -1
        : aVal < bVal ? 1 : -1
    })
  }, [fields, sortBy, sortDir])
  
  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader className="bg-gray-100 dark:bg-gray-800">
          <TableRow>
            <TableHead
              onClick={() => {
                setSortBy('name')
                setSortDir(sortDir === 'asc' ? 'desc' : 'asc')
              }}
              className="cursor-pointer hover:bg-gray-200"
            >
              Field Name
            </TableHead>
            <TableHead>Area (ha)</TableHead>
            <TableHead>Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sortedFields.map(field => (
            <TableRow key={field.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
              <TableCell className="font-medium">{field.name}</TableCell>
              <TableCell>{field.area}</TableCell>
              <TableCell>
                <Badge variant={field.status}>{field.status}</Badge>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
```

**Mobile Card Fallback:**
```jsx
// Desktop: Table
// Mobile: Card stack
<div className="hidden md:block">
  <FieldsTable fields={fields} />
</div>

<div className="flex flex-col gap-4 md:hidden">
  {fields.map(field => (
    <Card key={field.id} className="p-4">
      <h3 className="font-semibold">{field.name}</h3>
      <p className="text-sm text-gray-600">Area: {field.area} ha</p>
      <Badge className="mt-2">{field.status}</Badge>
    </Card>
  ))}
</div>
```

---

## 13. Drawer & Mobile Sheet Governance

**RULE:** Drawers are slide-in panels for mobile navigation and actions. Bottom sheets are mobile-first.

**Drawer Pattern:**
```jsx
import { Drawer, DrawerClose, DrawerContent, DrawerDescription, DrawerHeader, DrawerTitle, DrawerTrigger } from '@/components/ui/drawer'
import { Button } from '@/components/ui/button'

export const MobileMenu = () => {
  return (
    <Drawer>
      <DrawerTrigger asChild>
        <Button variant="ghost" size="sm">Menu</Button>
      </DrawerTrigger>
      <DrawerContent className="
        bottom-0 left-0 right-0 
        rounded-t-lg
        max-h-[80vh] overflow-y-auto
      ">
        <DrawerHeader>
          <DrawerTitle>Navigation</DrawerTitle>
        </DrawerHeader>
        <nav className="flex flex-col gap-2 p-4">
          <a href="/fields" className="py-2 px-4 hover:bg-gray-100">Fields</a>
          <a href="/reports" className="py-2 px-4 hover:bg-gray-100">Reports</a>
          <a href="/settings" className="py-2 px-4 hover:bg-gray-100">Settings</a>
        </nav>
        <DrawerClose asChild>
          <Button variant="outline" className="m-4">Close</Button>
        </DrawerClose>
      </DrawerContent>
    </Drawer>
  )
}
```

**Mobile Sheet Rules:**
- Drawers slide from bottom on mobile
- Drawers are dismissible by swipe or button
- Content is scrollable if exceeding 80vh
- Dark mode is fully supported

---

## 14. Data Display Standards

**RULE:** Data display uses consistent patterns: cards, KPI cards, metrics, badges, and status indicators.

**Card Pattern:**
```jsx
<Card className="p-4 md:p-6">
  <h3 className="text-lg font-semibold mb-4">Title</h3>
  <div className="space-y-3">
    {/* Content */}
  </div>
</Card>
```

**KPI Card Pattern:**
```jsx
<Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900 dark:to-blue-800 p-6">
  <div className="flex justify-between items-start">
    <div>
      <p className="text-sm text-gray-600 dark:text-gray-300">Production</p>
      <p className="text-3xl font-bold text-gray-900 dark:text-white">2,450 kg</p>
      <p className="text-xs text-green-600 dark:text-green-400 mt-1">+15% vs last week</p>
    </div>
    <TrendIcon className="text-green-600 w-8 h-8" />
  </div>
</Card>
```

**Metric Display:**
```jsx
<div className="flex justify-between items-center">
  <span className="text-sm font-medium text-gray-600">Metric</span>
  <span className="text-2xl font-bold text-gray-900">Value</span>
</div>
```

**Badge Pattern:**
```jsx
<Badge variant="success">Healthy</Badge>
<Badge variant="warning">Low Moisture</Badge>
<Badge variant="error">Action Required</Badge>
```

**Status Indicator:**
```jsx
<div className="flex items-center gap-2">
  <div className="w-2 h-2 rounded-full bg-success" />
  <span className="text-sm">Synced</span>
</div>
```

---

## 15. Loading & Skeleton Standards

**RULE:** Loading states use skeletons for perceived performance. Spinners indicate action progress.

**Skeleton Usage:**
```jsx
import { Skeleton } from '@/components/ui/skeleton'

export const CardSkeleton = () => (
  <Card className="p-4">
    <Skeleton className="h-6 w-32 mb-4" />
    <Skeleton className="h-4 w-full mb-2" />
    <Skeleton className="h-4 w-3/4" />
  </Card>
)

// Usage in component
{isLoading ? (
  <CardSkeleton />
) : (
  <Card>{content}</Card>
)}
```

**Spinner Usage:**
```jsx
import { Spinner } from '@/components/ui/spinner'

<Button disabled={isLoading}>
  {isLoading && <Spinner className="me-2 w-4 h-4" />}
  {isLoading ? 'Loading...' : 'Submit'}
</Button>
```

---

## 16. Error & Empty State Standards

**RULE:** Error and empty states guide users. States are clear, actionable, and visually distinct.

**Error State:**
```jsx
export const ErrorState = ({ message, onRetry }) => (
  <Card className="border-error/20 bg-error/5 p-6 text-center">
    <ErrorIcon className="w-8 h-8 text-error mx-auto mb-3" />
    <h3 className="text-lg font-semibold text-gray-900 mb-2">Something went wrong</h3>
    <p className="text-gray-600 mb-4">{message}</p>
    <Button onClick={onRetry}>Try Again</Button>
  </Card>
)
```

**Empty State:**
```jsx
export const EmptyState = ({ onAction }) => (
  <Card className="p-8 text-center border-2 border-dashed">
    <EmptyIcon className="w-12 h-12 text-gray-400 mx-auto mb-3" />
    <h3 className="text-lg font-semibold text-gray-900 mb-2">No data yet</h3>
    <p className="text-gray-600 mb-4">Create your first entry to get started</p>
    <Button onClick={onAction}>Create New</Button>
  </Card>
)
```

---

## 17. Toast & Notification Standards

**RULE:** Toasts provide non-blocking feedback. Toast usage follows strict rules.

**Toast Types:**
- **Success:** Action completed
- **Error:** Action failed
- **Warning:** Important notice
- **Info:** Informational message

**Toast Implementation:**
```jsx
import { useToast } from '@/components/ui/use-toast'

export const useFieldMutations = () => {
  const { toast } = useToast()
  
  const saveField = useMutation({
    mutationFn: async (field) => {
      const response = await api.fields.create(field)
      return response.data
    },
    onSuccess: () => {
      toast({
        title: 'Field Created',
        description: 'Your field has been created successfully',
        duration: 3000,
      })
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'error',
        duration: 5000,
      })
    },
  })
  
  return { saveField }
}
```

**Toast Rules:**
- Success toasts: 3 seconds duration
- Error toasts: 5 seconds duration
- Dismissible by swipe (mobile) or button
- Maximum 3 toasts on screen

---

## 18. Command Palette Architecture

**RULE:** Command palette enables rapid navigation and actions. Command palette is keyboard-first.

**Command Palette Implementation:**
```jsx
import { Command, CommandDialog, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '@/components/ui/command'
import { useEffect, useState } from 'react'

export const CommandPaletteDialog = () => {
  const [open, setOpen] = useState(false)
  
  useEffect(() => {
    const down = (e) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen(!open)
      }
    }
    document.addEventListener('keydown', down)
    return () => document.removeEventListener('keydown', down)
  }, [open])
  
  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="Search actions..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        <CommandGroup heading="Navigation">
          <CommandItem onSelect={() => navigateTo('/fields')}>
            <MapIcon className="me-2 w-4 h-4" />
            <span>Fields</span>
          </CommandItem>
          <CommandItem onSelect={() => navigateTo('/reports')}>
            <BarChartIcon className="me-2 w-4 h-4" />
            <span>Reports</span>
          </CommandItem>
        </CommandGroup>
        <CommandGroup heading="Actions">
          <CommandItem onSelect={() => openCreateField()}>
            <PlusIcon className="me-2 w-4 h-4" />
            <span>New Field</span>
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  )
}
```

---

## 19. Sidebar & Navigation Standards

**RULE:** Navigation uses shadcn sidebar on desktop, drawer on mobile. Navigation is responsive and accessible.

**Sidebar Implementation:**
```jsx
import { Sidebar, SidebarContent, SidebarItem, SidebarLabel, SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarRail } from '@/components/ui/sidebar'
import { useRouter } from 'next/router'

export const AppSidebar = () => {
  const router = useRouter()
  
  return (
    <Sidebar>
      <SidebarContent>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarLabel>Main</SidebarLabel>
          </SidebarMenuItem>
          <SidebarMenuItem>
            <SidebarMenuButton
              isActive={router.pathname.startsWith('/fields')}
              onClick={() => router.push('/fields')}
            >
              <MapIcon className="w-4 h-4" />
              <span>Fields</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
          <SidebarMenuItem>
            <SidebarMenuButton
              isActive={router.pathname.startsWith('/reports')}
              onClick={() => router.push('/reports')}
            >
              <BarChartIcon className="w-4 h-4" />
              <span>Reports</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarContent>
      <SidebarRail />
    </Sidebar>
  )
}
```

**Navigation Rules:**
- Desktop: Fixed sidebar or responsive drawer
- Mobile: Bottom navigation or slide drawer
- Active states clearly indicated
- Keyboard navigation supported

---

## 20. Controlled Customization Rules

**RULE:** Component customization is controlled. Wrappers can extend; developers cannot break constraints.

**Allowed Customization:**
- Adding Tailwind utilities via `className` prop
- Using variant system for styling variations
- Composing components together
- Extending with domain-specific wrappers

**Forbidden Customization:**
- Modifying `node_modules` directly
- Passing arbitrary HTML attributes that break component behavior
- Overriding core component logic
- Creating new CSS files alongside components
- Duplicating component internals

**Example: Controlled Customization**
```jsx
// GOOD: Using className for composition
<Card className="bg-gradient-to-br from-blue-50 to-blue-100">
  {/* Content */}
</Card>

// GOOD: Using variant system
<Button variant="primary" size="lg">
  Submit
</Button>

// GOOD: Composing components
<Card>
  <Stack gap={4}>
    <h2>Title</h2>
    <Input />
    <Button>Action</Button>
  </Stack>
</Card>

// BAD: Breaking encapsulation
<Button.prototype.customRender = () => {}  // No!

// BAD: Inline style overrides
<Card style={{backgroundColor: '#custom'}}>  // Use className instead

// BAD: Duplicating component
const MyCard = () => (
  <div className="border rounded p-4">
    {/* Reinventing Card */}
  </div>
)
```

---

## 21. AI-Safe Extension Rules

**RULE:** AI agents must follow strict constraints when extending or using shadcn components.

**Required:**
- Always wrap shadcn components; never edit node_modules
- Use existing variants before creating custom variants
- Apply Tailwind utilities for styling, never custom CSS
- Include accessibility attributes (aria-*, labels, descriptions)
- Support dark mode with `dark:` utilities
- Support mobile-first responsive design
- Use TypeScript for strong typing
- Test on mobile, tablet, desktop

**Forbidden:**
- Modifying shadcn component internals
- Creating arbitrary inline styles
- Using hardcoded colors (use design tokens)
- Breaking component accessibility
- Desktop-first responsive patterns
- Creating duplicate components
- Inline style overrides

**Example: AI-Safe Extension**
```jsx
// GOOD: AI-safe domain extension
import { Button } from '@/components/ui/Button'
import { cn } from '@/lib/utils'

export const HarvestButton = ({ disabled, onClick, ...props }) => (
  <Button
    variant="primary"
    size="lg"
    disabled={disabled}
    onClick={onClick}
    className={cn(
      'uppercase font-semibold',
      'dark:bg-primary-dark dark:hover:bg-primary'
    )}
    {...props}
  />
)

// BAD: AI-unsafe pattern
export const HarvestButton = (props) => (
  <button
    style={{
      padding: '12px 16px',
      backgroundColor: '#2563eb',
      color: 'white',
      borderRadius: '8px',
    }}
    {...props}
  />
)
```

---

## 22. Forbidden Direct Component Hacking

**RULE:** Direct modification of shadcn components is strictly forbidden. All customization flows through wrappers.

**Forbidden Actions:**

### Modifying node_modules
```jsx
// FORBIDDEN: Editing component source
// node_modules/@shadcn/ui/dist/button.tsx
// export const Button = (...) => { /* custom logic */ }

// Do NOT do this!
```

### Duplicating Components
```jsx
// FORBIDDEN: Copying entire component
export const MyButton = () => (
  <button className="px-4 py-2 bg-blue-600 rounded">
    My Button
  </button>
)

// Use wrapper pattern instead
```

### Inline Overrides
```jsx
// FORBIDDEN: Passing arbitrary props that break encapsulation
<Button danger={true} customColor="purple">

// Use variant system instead
<Button variant="danger">
```

### CSS Modifications
```jsx
// FORBIDDEN: Adding custom CSS next to component
// Button.module.css
.button {
  background: custom-color;
}

// Use Tailwind utilities instead
```

---

## 23. Real Agricultural ERP Examples

### Example 1: Field Form Dialog
```jsx
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

const createFieldSchema = z.object({
  name: z.string().min(1, 'Field name required'),
  area: z.string().regex(/^\d+(\.\d{1,2})?$/, 'Valid area required'),
  type: z.string().min(1, 'Field type required'),
})

export const CreateFieldDialog = ({ open, onOpenChange, onSuccess }) => {
  const form = useForm({
    resolver: zodResolver(createFieldSchema),
  })
  
  const onSubmit = async (data) => {
    await api.fields.create(data)
    onSuccess()
    onOpenChange(false)
  }
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-screen overflow-y-auto md:max-h-[90vh] rounded-none md:rounded-lg">
        <DialogHeader>
          <DialogTitle>Create New Field</DialogTitle>
          <DialogDescription>Enter field details to create a new field record</DialogDescription>
        </DialogHeader>
        
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="flex flex-col gap-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Field Name</FormLabel>
                  <FormControl>
                    <Input placeholder="e.g., Olive North" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="area"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Area (hectares)</FormLabel>
                  <FormControl>
                    <Input type="number" placeholder="45.2" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="type"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Field Type</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="olive">Olive</SelectItem>
                      <SelectItem value="palm">Palm</SelectItem>
                      <SelectItem value="grain">Grain</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <div className="flex gap-2 md:flex-row-reverse mt-4">
              <Button type="submit" disabled={form.formState.isSubmitting} className="flex-1">
                {form.formState.isSubmitting ? 'Creating...' : 'Create Field'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                className="flex-1"
              >
                Cancel
              </Button>
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
```

### Example 2: Responsive Fields Table
```jsx
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { MoreVertical } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

export const FieldsDataTable = ({ fields, onEdit, onDelete }) => {
  return (
    <>
      {/* Desktop Table */}
      <div className="hidden md:block overflow-x-auto rounded-lg border">
        <Table>
          <TableHeader className="bg-gray-100 dark:bg-gray-800">
            <TableRow>
              <TableHead className="font-semibold">Field Name</TableHead>
              <TableHead className="font-semibold">Area (ha)</TableHead>
              <TableHead className="font-semibold">Type</TableHead>
              <TableHead className="font-semibold">Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {fields.map(field => (
              <TableRow key={field.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                <TableCell className="font-medium">{field.name}</TableCell>
                <TableCell>{field.area}</TableCell>
                <TableCell>{field.type}</TableCell>
                <TableCell>
                  <Badge variant={field.status === 'healthy' ? 'success' : 'warning'}>
                    {field.status}
                  </Badge>
                </TableCell>
                <TableCell className="text-right">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm">
                        <MoreVertical className="w-4 h-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => onEdit(field.id)}>
                        Edit
                      </DropdownMenuItem>
                      <DropdownMenuItem className="text-error" onClick={() => onDelete(field.id)}>
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      
      {/* Mobile Cards */}
      <div className="flex flex-col gap-4 md:hidden">
        {fields.map(field => (
          <Card key={field.id} className="p-4">
            <div className="flex justify-between items-start mb-3">
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">{field.name}</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">{field.type}</p>
              </div>
              <Badge variant={field.status === 'healthy' ? 'success' : 'warning'}>
                {field.status}
              </Badge>
            </div>
            
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
              Area: <span className="font-semibold text-gray-900 dark:text-white">{field.area} ha</span>
            </p>
            
            <div className="flex gap-2">
              <Button variant="outline" className="flex-1" onClick={() => onEdit(field.id)}>
                Edit
              </Button>
              <Button variant="outline" className="flex-1 text-error" onClick={() => onDelete(field.id)}>
                Delete
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </>
  )
}
```

---

## 24. Enforcement Checklist

**Before Merging PR:**
- [ ] No shadcn components edited in node_modules
- [ ] All components wrapped, not duplicated
- [ ] No inline style overrides
- [ ] Tailwind utilities applied correctly
- [ ] Dark mode variants included
- [ ] Mobile responsiveness tested
- [ ] RTL rendering verified
- [ ] Accessibility compliance checked (axe-core)
- [ ] Form validation included where needed
- [ ] Error and empty states handled
- [ ] Loading states implemented
- [ ] Focus indicators visible
- [ ] Component tested on mobile device

**Code Review Checks:**
```bash
# Check for node_modules modifications
git diff node_modules/ # Should be empty

# Check for inline styles
grep -r "style={{" src/features src/components

# Check for component duplication
grep -r "export const.*Button" src/

# Run accessibility audit
npx axe-core src/components
```

---

## Summary

ATLS shadcn governance establishes strict ownership rules, wrapper patterns, and controlled customization. shadcn components are immutable base primitives. All ATLS-specific styling flows through wrapper components. Domain extensions compose primitives without duplication. Variants enable maintainable customization. Accessibility and mobile-first design are guaranteed. Dark mode and RTL support are comprehensive. Form and table governance ensures consistency. AI agents must follow strict extension constraints. Component consistency is enforced through linting and code review.

## Last Updated
2026-05-12
