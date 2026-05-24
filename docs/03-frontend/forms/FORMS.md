# Forms — Frontend Reference

> Form patterns, validation, and submission for ATLS.

---

## Stack

| Library | Purpose |
|---------|---------|
| `react-hook-form` | Form state management |
| `zod` | Schema validation |
| `@hookform/resolvers/zod` | Bridge between the two |
| MUI `TextField`, `Select` | Input components |

---

## Standard Form Pattern

```jsx
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

// 1. Define schema
const schema = z.object({
  name:      z.string().min(2, 'الاسم مطلوب'),
  date:      z.string().min(1, 'التاريخ مطلوب'),
  location:  z.number({ required_error: 'الموقع مطلوب' }),
  workers:   z.number().min(0).default(0),
})

// 2. Form component
const MyForm = ({ onSuccess }) => {
  const { control, handleSubmit, formState: { errors, isSubmitting } } = useForm({
    resolver: zodResolver(schema),
    defaultValues: { workers: 0 }
  })

  const onSubmit = async (data) => {
    await myService.create(data)
    onSuccess()
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Controller
        name="name"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            label={t('fields.name')}
            error={!!errors.name}
            helperText={errors.name?.message}
            fullWidth
          />
        )}
      />
      <Button type="submit" disabled={isSubmitting} variant="contained">
        {isSubmitting ? <CircularProgress size={20} /> : t('common.save')}
      </Button>
    </form>
  )
}
```

---

## Select Fields (FK Dropdowns)

```jsx
// Dropdown backed by API data
const { data: locations } = useLocations()

<Controller
  name="location"
  control={control}
  render={({ field }) => (
    <FormControl fullWidth error={!!errors.location}>
      <InputLabel>{t('fields.location')}</InputLabel>
      <Select {...field} label={t('fields.location')}>
        {locations?.map(loc => (
          <MenuItem key={loc.id} value={loc.id}>{loc.name}</MenuItem>
        ))}
      </Select>
      <FormHelperText>{errors.location?.message}</FormHelperText>
    </FormControl>
  )}
/>
```

---

## Error Handling

```jsx
// API errors — show at form level, not just field level
const [apiError, setApiError] = useState(null)

const onSubmit = async (data) => {
  try {
    setApiError(null)
    await myService.create(data)
    onSuccess()
  } catch (err) {
    setApiError(err.response?.data?.detail || 'حدث خطأ غير متوقع')
  }
}

// In JSX:
{apiError && <Alert severity="error" sx={{ mb: 2 }}>{apiError}</Alert>}
```

---

## Form Submission Flow Rules

```
onSubmit handler → calls service → service returns
  ✅ Success → call onSuccess() → close dialog / redirect
  ❌ Error   → set apiError state → show Alert above form
              → never use alert() or console.log()

isSubmitting   → disable submit button → show CircularProgress inside button
```

---

## Dialog Forms (Drawer/Modal)

```jsx
// Pattern for forms inside MUI Dialog
<Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
  <DialogTitle>{t('report.create_title')}</DialogTitle>
  <DialogContent>
    <Box sx={{ pt: 1 }}>
      {/* form fields */}
    </Box>
  </DialogContent>
  <DialogActions>
    <Button onClick={onClose} color="inherit">{t('common.cancel')}</Button>
    <Button onClick={handleSubmit(onSubmit)} variant="contained" disabled={isSubmitting}>
      {isSubmitting ? <CircularProgress size={16} /> : t('common.save')}
    </Button>
  </DialogActions>
</Dialog>
```

---

## Validation Messages (Arabic)

All error messages in Arabic. Zod patterns:

```javascript
z.string().min(2, 'يجب ألا يقل عن حرفين')
z.string().email('البريد الإلكتروني غير صحيح')
z.number({ required_error: 'هذا الحقل مطلوب' }).min(0, 'يجب أن يكون 0 أو أكثر')
z.string().min(1, 'هذا الحقل مطلوب')
```

---

## Do NOT

```
❌ useState for each form field
❌ Manual validation logic (use Zod)
❌ fetch() inside form submit handler (use services.js)
❌ Hardcoded error messages in English (use i18n or Arabic directly)
❌ alert() or confirm() for user feedback
```
