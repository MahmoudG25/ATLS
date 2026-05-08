<!-- SECURITY NOTICE: This file has been sanitized. Real credentials have been removed. See .env files for configuration. -->

# ðŸŒ¿ ATLS â€” Ø®Ø·Ø© Ø§Ù„ØªØ·ÙˆÙŠØ± Ø§Ù„Ø´Ø§Ù…Ù„Ø© Ø§Ù„Ù†Ù‡Ø§Ø¦ÙŠØ© (SaaS-Ready Master Plan v2)

> **Stack:** Django 6 + DRF | React 19 + Vite | MUI v9 + Tailwind v4 | i18next (AR/EN)
> **Ù†ÙˆØ¹ Ø§Ù„Ù…Ù†ØªØ¬:** Multi-Tenant Farm Management SaaS â€” Ù‚Ø§Ø¨Ù„ Ù„Ù„Ø¨ÙŠØ¹ Ù„Ø£ÙŠ Ù…Ø²Ø±Ø¹Ø©
> **Core Entity Chain:** `Company â†’ Farm â†’ LocationNode â†’ Report â†’ LaborEntry / Attachment`

---

## ðŸŽ¯ Ø§Ù„Ù‡Ø¯Ù Ø§Ù„Ù†Ù‡Ø§Ø¦ÙŠ

Ù†Ø¸Ø§Ù… ÙŠÙ…ÙƒÙ† ØªØ®ØµÙŠØµÙ‡ Ù„Ø£ÙŠ Ù…Ø²Ø±Ø¹Ø© (Ù†Ø®ÙŠÙ„ØŒ Ø²ÙŠØªÙˆÙ†ØŒ ÙÙˆØ§ÙƒÙ‡ØŒ Ø®Ø¶Ø±ÙˆØ§Øª) Ø¨Ø¯ÙˆÙ† ØªØ¹Ø¯ÙŠÙ„ ÙƒÙˆØ¯ â€” ÙÙ‚Ø· Ù…Ù† Admin Dashboard.

---

# â˜ï¸ CLOUDINARY â€” Ø¥Ø¹Ø¯Ø§Ø¯ Ø§Ù„Ù…Ø·Ù„ÙˆØ¨ Ù…Ù†Ùƒ

## Ù…Ø§ ØªÙØ¹Ù„Ù‡ Ø£Ù†Øª (Ù…Ø±Ø© ÙˆØ§Ø­Ø¯Ø© ÙÙ‚Ø·):

### Ø§Ù„Ø®Ø·ÙˆØ© 1 â€” Ø¥Ù†Ø´Ø§Ø¡ Ø­Ø³Ø§Ø¨
- Ø§Ø°Ù‡Ø¨ Ø¥Ù„Ù‰: https://cloudinary.com
- Ø³Ø¬Ù‘Ù„ Ø­Ø³Ø§Ø¨ Ù…Ø¬Ø§Ù†ÙŠ (Free plan ÙŠÙƒÙÙŠ Ù„Ù„ØªØ·ÙˆÙŠØ±)

### Ø§Ù„Ø®Ø·ÙˆØ© 2 â€” Ù…Ù† Ø§Ù„Ù€ Dashboard Ø§Ø­Ø¶Ø±:
```
Cloud Name:    [REDACTED_CLOUD_NAME]
API Key:       [REDACTED_API_KEY]
API Secret:    [REDACTED_API_SECRET]
```

### Ø§Ù„Ø®Ø·ÙˆØ© 3 â€” Ø£Ø¶ÙÙ‡Ø§ ÙÙŠ `.env` (Backend):
```env
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### Ø§Ù„Ø®Ø·ÙˆØ© 4 â€” Ø¥Ù†Ø´Ø§Ø¡ Folders ÙÙŠ Cloudinary Dashboard:
```
atls/
â”œâ”€â”€ employees/avatars/      â† ØµÙˆØ± Ø§Ù„Ù…ÙˆØ¸ÙÙŠÙ†
â”œâ”€â”€ employees/attachments/  â† Ù…Ù„ÙØ§Øª Ø§Ù„Ù…ÙˆØ¸ÙÙŠÙ† (PDF + ØµÙˆØ±)
â””â”€â”€ reports/attachments/    â† Ù…Ø±ÙÙ‚Ø§Øª Ø§Ù„ØªÙ‚Ø§Ø±ÙŠØ±
```

### Ø§Ù„Ø®Ø·ÙˆØ© 5 â€” Ø¥Ø¹Ø¯Ø§Ø¯ Upload Preset (Ù…Ù‡Ù… Ù„Ù„Ù€ Frontend direct upload):
- Ù…Ù† Dashboard â†’ Settings â†’ Upload â†’ Add Upload Preset
- Ø§Ø³Ù…Ù‡: `atls_unsigned`
- Mode: **Unsigned** (Ù„Ù„Ø±ÙØ¹ Ø§Ù„Ù…Ø¨Ø§Ø´Ø± Ù…Ù† Frontend)
- Folder: `atls/`
- Allowed Formats: `jpg,jpeg,png,webp,pdf`

### Ø§Ù„ÙƒÙˆØ¯ Ø§Ù„Ù„ÙŠ Ù‡ÙŠØªØ¶Ø§Ù ÙÙŠ Ø§Ù„Ù…Ø´Ø±ÙˆØ¹ (Ø³ØªØ±Ø§Ù‡ ÙÙŠ Ø§Ù„Ù…Ù„ÙØ§Øª):
```python
# Backend/config/settings.py â€” ÙŠÙØ¶Ø§Ù ØªÙ„Ù‚Ø§Ø¦ÙŠØ§Ù‹:
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': env('CLOUDINARY_API_KEY'),
    'API_SECRET': env('CLOUDINARY_API_SECRET'),
}
```

---

# ðŸ“‹ ÙÙ‡Ø±Ø³ Ø§Ù„Ù€ Modules Ø§Ù„ÙƒØ§Ù…Ù„Ø©

| # | Module | Ø§Ù„Ø­Ø§Ù„Ø© Ø§Ù„Ø­Ø§Ù„ÙŠØ© | Ø§Ù„Ø£ÙˆÙ„ÙˆÙŠØ© |
|---|--------|---------------|-----------|
| 1 | FarmStructure UI | âš ï¸ Ù…ÙˆØ¬ÙˆØ¯ â€” ÙŠØ­ØªØ§Ø¬ ØªØ­Ø³ÙŠÙ† | ðŸ”´ Ø£ÙˆÙ„Ø§Ù‹ |
| 2 | Daily Report â€” LaborEntry Panel | âš ï¸ Ù…ÙˆØ¬ÙˆØ¯ â€” ÙŠØ­ØªØ§Ø¬ Ù…ÙŠØ²Ø© | ðŸ”´ Ø«Ø§Ù†ÙŠØ§Ù‹ |
| 3 | HR Module (Backend + Frontend) | âŒ Backend ÙØ§Ø¶ÙŠ | ðŸ”´ Ø«Ø§Ù„Ø«Ø§Ù‹ |
| 4 | Admin Dashboard (Ø´Ø§Ù…Ù„) | âš ï¸ Ø¨Ø³ÙŠØ· Ø¬Ø¯Ø§Ù‹ | ðŸ”´ Ø±Ø§Ø¨Ø¹Ø§Ù‹ |
| 5 | Warehouse â€” Ø¥Ø¯Ø§Ø±Ø© Ø§Ù„Ù…Ø®Ø§Ø²Ù† | âš ï¸ Ù…ÙˆØ¬ÙˆØ¯ â€” ÙŠØ­ØªØ§Ø¬ ØªØ­Ø³ÙŠÙ† | ðŸŸ¡ Ø®Ø§Ù…Ø³Ø§Ù‹ |
| 6 | Accounting â€” Ø§Ù„Ù…Ø­Ø§Ø³Ø¨Ø© | âš ï¸ Ù…ÙˆØ¬ÙˆØ¯ â€” ÙŠØ­ØªØ§Ø¬ ØªØ­Ø³ÙŠÙ† | ðŸŸ¡ Ø³Ø§Ø¯Ø³Ø§Ù‹ |
| 7 | Fleet â€” Ø§Ù„Ø£Ø³Ø·ÙˆÙ„ ÙˆØ§Ù„Ù…Ø¹Ø¯Ø§Øª | âš ï¸ Ù…ÙˆØ¬ÙˆØ¯ â€” ÙŠØ­ØªØ§Ø¬ ØªØ­Ø³ÙŠÙ† | ðŸŸ¡ Ø³Ø§Ø¨Ø¹Ø§Ù‹ |
| 8 | Palm Records â€” Ø­Ù‚ÙˆÙ„ Ø§Ù„Ù†Ø®ÙŠÙ„ | âš ï¸ Ù…ÙˆØ¬ÙˆØ¯ â€” ÙŠØ­ØªØ§Ø¬ ØªÙˆØ­ÙŠØ¯ | ðŸŸ¢ Ø«Ø§Ù…Ù†Ø§Ù‹ |
| 9 | Olive Records â€” Ø­Ù‚ÙˆÙ„ Ø§Ù„Ø²ÙŠØªÙˆÙ† | âš ï¸ Ù…ÙˆØ¬ÙˆØ¯ â€” ÙŠØ­ØªØ§Ø¬ ØªÙˆØ­ÙŠØ¯ | ðŸŸ¢ ØªØ§Ø³Ø¹Ø§Ù‹ |
| 10 | Production â€” Ø§Ù„Ù…Ø­ØµÙˆÙ„ | âš ï¸ Ù…ÙˆØ¬ÙˆØ¯ â€” ÙŠØ­ØªØ§Ø¬ Ø±Ø¨Ø· | ðŸŸ¢ Ø¹Ø§Ø´Ø±Ø§Ù‹ |

---

## ðŸ§± Ù…Ø¨Ø§Ø¯Ø¦ Ø«Ø§Ø¨ØªØ© Ù„Ø§ ØªÙØ®Ø±Ù‚ Ø£Ø¨Ø¯Ø§Ù‹

```
1. ÙƒÙ„ Ù…ÙˆØ¯ÙŠÙ„ Ù„Ù‡ company = FK(Company)           [TenantAwareModel]
2. LocationNode Ù‡Ùˆ Ø§Ù„Ù…ØµØ¯Ø± Ø§Ù„ÙˆØ­ÙŠØ¯ Ù„Ù„Ù…ÙˆØ§Ù‚Ø¹
3. ÙƒÙ„ Ø´ÙŠØ¡ Ù‚Ø§Ø¨Ù„ Ù„Ù„ØªØ®ØµÙŠØµ Ù…Ù† Admin Dashboard
4. Ù„Ø§ hardcoded labels â€” ÙƒÙ„ Ø´ÙŠØ¡ Ù…Ù† DB
5. ÙƒÙ„ feature Ù…Ø­ÙƒÙˆÙ…Ø© Ø¨Ù€ role permissions
6. Ø§Ù„ÙƒÙˆØ¯ Ù†Ø¸ÙŠÙ: Logic ÙÙŠ services/ â€” Ù„Ø§ ÙÙŠ Views
7. ÙƒÙ„ queryset ÙŠÙ…Ø± Ø¹Ù„Ù‰ company scoping
```

---

## ðŸ—ºï¸ Role Permissions Map (Ø§Ù„Ø¬Ø¯ÙˆÙ„ Ø§Ù„ÙƒØ§Ù…Ù„)

| Feature | SUPER_ADMIN | OWNER | MANAGER | ENGINEER | HR | ACCOUNTANT | WAREHOUSE |
|---------|------------|-------|---------|----------|----|------------|-----------|
| Admin Dashboard | âœ… ÙƒØ§Ù…Ù„ | âœ… ÙƒØ§Ù…Ù„ | âœ… Ø¬Ø²Ø¦ÙŠ | âŒ | âŒ | âŒ | âŒ |
| Farm Structure | âœ… | âœ… | âœ… | ðŸ‘ï¸ Ù‚Ø±Ø§Ø¡Ø© | âŒ | âŒ | âŒ |
| Daily Reports | âœ… | âœ… | âœ… | âœ… Ø¥Ù†Ø´Ø§Ø¡ | âŒ | ðŸ‘ï¸ | âŒ |
| HR Module | âœ… | âœ… | âœ… Ø¬Ø²Ø¦ÙŠ | ðŸ‘ï¸ Ù…Ù„ÙÙ‡ ÙÙ‚Ø· | âœ… ÙƒØ§Ù…Ù„ | âŒ | âŒ |
| Warehouse | âœ… | âœ… | âœ… | âŒ | âŒ | ðŸ‘ï¸ | âœ… ÙƒØ§Ù…Ù„ |
| Accounting | âœ… | âœ… | ðŸ‘ï¸ | âŒ | âŒ | âœ… ÙƒØ§Ù…Ù„ | âŒ |
| Fleet/Equipment | âœ… | âœ… | âœ… | ðŸ‘ï¸ | âŒ | âŒ | âŒ |
| Palm/Olive Records | âœ… | âœ… | âœ… | âœ… | âŒ | âŒ | âŒ |
| Production | âœ… | âœ… | âœ… | âœ… | âŒ | ðŸ‘ï¸ | âŒ |
| Custom Fields Admin | âœ… | âœ… | âœ… | âŒ | âŒ | âŒ | âŒ |

---

# ðŸ—ï¸ SIDEBAR STRUCTURE (Navigation)

```
SIDEBAR
â”œâ”€â”€ ðŸ“Š Dashboard                (Ø§Ù„ÙƒÙ„)
â”œâ”€â”€ ðŸŒ³ Ù‡ÙŠÙƒÙ„ Ø§Ù„Ù…Ø²Ø±Ø¹Ø©             (SUPER_ADMIN, OWNER, MANAGER, ENGINEER[read])
â”œâ”€â”€ ðŸ“‹ Ø§Ù„ØªÙ‚Ø§Ø±ÙŠØ±                  (SUPER_ADMIN, OWNER, MANAGER, ENGINEER)
â”‚   â”œâ”€â”€ Ø§Ù„ØªÙ‚Ø±ÙŠØ± Ø§Ù„ÙŠÙˆÙ…ÙŠ
â”‚   â”œâ”€â”€ ØªÙ‚Ø±ÙŠØ± Ø§Ù„Ø±ÙŠ
â”‚   â””â”€â”€ ØªÙ‚Ø±ÙŠØ± Ø§Ù„ØªØ³Ù…ÙŠØ¯
â”œâ”€â”€ ðŸ‘¥ Ø§Ù„Ù…ÙˆØ§Ø±Ø¯ Ø§Ù„Ø¨Ø´Ø±ÙŠØ© (HR)      (SUPER_ADMIN, OWNER, MANAGER, HR)
â”‚   â”œâ”€â”€ Ø§Ù„Ù…ÙˆØ¸ÙÙŠÙ†
â”‚   â””â”€â”€ Ø§Ù„Ø¥Ø¬Ø§Ø²Ø§Øª ÙˆØ§Ù„Ø­Ø¶ÙˆØ±
â”œâ”€â”€ ðŸ­ Ø§Ù„Ù…Ø®Ø§Ø²Ù†                   (SUPER_ADMIN, OWNER, MANAGER, WAREHOUSE)
â”œâ”€â”€ ðŸ’° Ø§Ù„Ù…Ø­Ø§Ø³Ø¨Ø©                  (SUPER_ADMIN, OWNER, ACCOUNTANT)
â”œâ”€â”€ ðŸšœ Ø§Ù„Ø£Ø³Ø·ÙˆÙ„ ÙˆØ§Ù„Ù…Ø¹Ø¯Ø§Øª          (SUPER_ADMIN, OWNER, MANAGER)
â”œâ”€â”€ ðŸŒ´ Ø­Ù‚ÙˆÙ„ Ø§Ù„Ù†Ø®ÙŠÙ„               (SUPER_ADMIN, OWNER, MANAGER, ENGINEER)
â”œâ”€â”€ ðŸ«’ Ø­Ù‚ÙˆÙ„ Ø§Ù„Ø²ÙŠØªÙˆÙ†              (SUPER_ADMIN, OWNER, MANAGER, ENGINEER)
â”œâ”€â”€ ðŸ“¦ Ø§Ù„Ù…Ø­ØµÙˆÙ„                   (SUPER_ADMIN, OWNER, MANAGER, ENGINEER)
â””â”€â”€ âš™ï¸ Ù„ÙˆØ­Ø© Ø§Ù„Ø¥Ø¯Ø§Ø±Ø©              (SUPER_ADMIN, OWNER, MANAGER[Ø¬Ø²Ø¦ÙŠ])
```

---

# ðŸ”´ PHASE 1 â€” FarmStructure UI (Ø£ÙˆÙ„Ø§Ù‹)

## Ø§Ù„Ù…Ø´ÙƒÙ„Ø© Ø§Ù„Ø­Ø§Ù„ÙŠØ©:
Ø§Ù„Ø´Ø¬Ø±Ø© Ø«Ø§Ø¨ØªØ© Ø§Ù„Ø­Ø¬Ù… â€” Ù„Ùˆ ÙÙŠ 50 Ø¹Ù†ØµØ± ÙŠØªØ¯Ø§Ø®Ù„ÙˆØ§ ÙˆÙŠÙƒÙˆÙ† Ø§Ù„Ù…Ø¸Ù‡Ø± Ø³ÙŠØ¦Ø§Ù‹.

## Ø§Ù„Ø­Ù„ â€” Adaptive Tree:

### Ø®ÙˆØ§Ø±Ø²Ù…ÙŠØ© Ø§Ù„Ø­Ø¬Ù…:
```javascript
const getNodeConfig = (totalSiblings) => {
  if (totalSiblings <= 3)  return { size: 'lg', iconSize: 24, textSize: '14px', padding: '12px 16px' };
  if (totalSiblings <= 6)  return { size: 'md', iconSize: 20, textSize: '12px', padding: '8px 12px'  };
  if (totalSiblings <= 12) return { size: 'sm', iconSize: 16, textSize: '11px', padding: '6px 8px'   };
  return                          { size: 'xs', iconSize: 14, textSize: '10px', padding: '4px 6px'   };
};
```

### Layout Rules:
```
- Ø§Ù„Ù€ Sectors (level 1): Ø¹Ø±Ø¶ 100% â€” ÙƒÙ„ sector ÙÙŠ row
- Ø§Ù„Ù€ Stages (level 2): flex-wrap Ø¯Ø§Ø®Ù„ Ø§Ù„Ù€ sector â€” ÙŠØªÙˆØ²Ø¹ÙˆØ§ Ø£ÙÙ‚ÙŠØ§Ù‹
- Ø§Ù„Ù€ Enclosures (level 3): grid Ø¨Ù€ columns ØªØªØºÙŠØ± Ø¨Ù†Ø§Ø¡Ù‹ Ø¹Ù„Ù‰ Ø§Ù„Ø¹Ø¯Ø¯
  - 1-4  enclosures â†’ 2 columns
  - 5-8  enclosures â†’ 3 columns
  - 9+   enclosures â†’ 4 columns
- Collapse/Expand Ø¹Ù„Ù‰ ÙƒÙ„ branch Ø¨Ø²Ø± Ø³Ù‡Ù…
- Horizontal scroll Ø¹Ù„Ù‰ Ø§Ù„Ù€ container Ù„Ùˆ Ø§Ù„Ø´Ø¬Ø±Ø© Ø¹Ø±ÙŠØ¶Ø©
```

### Ø§Ù„Ù…Ù„ÙØ§Øª Ø§Ù„Ù…ØªØ£Ø«Ø±Ø©:
```
Front-End/src/pages/farm/
â”œâ”€â”€ FarmStructure.jsx   â† Ø¥Ø¹Ø§Ø¯Ø© ÙƒØªØ§Ø¨Ø© Ø§Ù„Ù€ TreeItem component
â”œâ”€â”€ FarmStructure.css   â† Ø¥Ø¶Ø§ÙØ© classes Ù„Ù„Ù€ sizes
â””â”€â”€ hooks/
    â””â”€â”€ useFarmTree.js  â† logic Ù…Ù†ÙØµÙ„Ø© (Ø¬Ø¯ÙŠØ¯)
```

### Ø§Ù„Ù…ÙŠØ²Ø§Øª Ø§Ù„Ù…Ø¶Ø§ÙØ©:
- âœ… Collapse/Expand per branch
- âœ… Ø­Ø¬Ù… Ù…ØªÙƒÙŠÙ Ù…Ø¹ Ø§Ù„Ø¹Ø¯Ø¯
- âœ… Horizontal scroll Ø¹Ù†Ø¯ Ø§Ù„Ø­Ø§Ø¬Ø©
- âœ… Hover â†’ Ø£Ø²Ø±Ø§Ø± Ø§Ù„Ø¹Ù…Ù„ÙŠØ§Øª
- âœ… Search/Filter Ø¨Ø§Ù„Ø§Ø³Ù…
- âœ… Count badge Ø¹Ù„Ù‰ ÙƒÙ„ node (Ø¹Ø¯Ø¯ Ø§Ù„Ø£Ø¨Ù†Ø§Ø¡)

---

# ðŸ”´ PHASE 2 â€” Daily Report: LaborEntry Inline Panel (Ø«Ø§Ù†ÙŠØ§Ù‹)

## Ø§Ù„Ù…Ø·Ù„ÙˆØ¨:

### ÙÙŠ `DailyTaskForm.jsx`:
Ø¨Ø¬Ø§Ù†Ø¨ `company_workers` Ùˆ`contractor_workers` â†’ Ø£ÙŠÙ‚ÙˆÙ†Ø© `âœï¸`

```
Ø¹Ù…Ø§Ù„ Ø§Ù„Ø´Ø±ÙƒØ©: [Ø¹Ø¯Ø§Ø¯: 3] âœï¸
Ø¹Ù…Ø§Ù„ Ø§Ù„Ù…Ù‚Ø§ÙˆÙ„: [Ø¹Ø¯Ø§Ø¯: 2] âœï¸
```

Ø¹Ù†Ø¯ Ø§Ù„Ø¶ØºØ· Ø¹Ù„Ù‰ âœï¸ â†’ Drawer Ù…Ù† Ø§Ù„Ø£Ø³ÙÙ„:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  ðŸ‘· ØªÙØ§ØµÙŠÙ„ Ø§Ù„Ø¹Ù…Ø§Ù„                    â”‚
â”‚                                      â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚  â”‚ Ø§Ø³Ù… Ø§Ù„Ø¹Ø§Ù…Ù„  â”‚ Ø³Ø§Ø¹Ø§Øª â”‚ Ø¥Ø¶Ø§ÙÙŠ â”‚   â”‚ â† Ø¬Ø¯ÙˆÙ„ Ø§Ù„Ø¹Ù…Ø§Ù„ Ø§Ù„Ù…Ø¶Ø§ÙÙŠÙ†
â”‚  â”‚ Ø£Ø­Ù…Ø¯ Ù…Ø­Ù…Ø¯  â”‚   8   â”‚   2   â”‚ ðŸ—‘ï¸â”‚
â”‚  â”‚ Ù…Ø­Ù…Ø¯ Ø¹Ù„ÙŠ   â”‚   8   â”‚   0   â”‚ ðŸ—‘ï¸â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â”‚                                      â”‚
â”‚  â”€â”€â”€ Ø¥Ø¶Ø§ÙØ© Ø¹Ø§Ù…Ù„ Ø¬Ø¯ÙŠØ¯ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€  â”‚
â”‚  Ø§Ù„Ø§Ø³Ù…: [___________________] ðŸ”    â”‚  â† search ÙÙŠ HR
â”‚  Ù†ÙˆØ¹ Ø§Ù„Ø¹Ø§Ù…Ù„: â—‹ Ø´Ø±ÙƒØ©  â— Ù…Ù‚Ø§ÙˆÙ„        â”‚
â”‚  Ø§Ù„Ù…Ù‚Ø§ÙˆÙ„: [dropdown Ø§Ø®ØªÙŠØ§Ø±ÙŠ]         â”‚
â”‚  Ø³Ø§Ø¹Ø§Øª Ø§Ù„Ø¹Ù…Ù„: [8]                   â”‚
â”‚  Ø³Ø§Ø¹Ø§Øª Ø¥Ø¶Ø§ÙÙŠØ©: [0]                  â”‚
â”‚  Ø§Ù„Ø£Ø¬Ø±/Ø³Ø§Ø¹Ø©: [50]                   â”‚
â”‚  Ù…Ù„Ø§Ø­Ø¸Ø§Øª: [________________]        â”‚
â”‚                                      â”‚
â”‚  [Ø¥Ù„ØºØ§Ø¡]          [âž• Ø¥Ø¶Ø§ÙØ© Ù„Ù„Ù‚Ø§Ø¦Ù…Ø©] â”‚
â”‚                                      â”‚
â”‚            [ðŸ’¾ Ø­ÙØ¸ Ø§Ù„ØªÙØ§ØµÙŠÙ„]         â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Ù…Ù†Ø·Ù‚ Ø§Ù„Ù€ Search:
```javascript
// Ø¹Ù†Ø¯ ÙƒØªØ§Ø¨Ø© Ø§Ù„Ø§Ø³Ù… â†’ Ù†Ø¨Ø­Ø« ÙÙŠ HR employees
// Ù†Ø¹Ø±Ø¶ Ø§Ù‚ØªØ±Ø§Ø­Ø§Øª Ø¥Ø°Ø§ ÙÙŠ Ù†ØªØ§Ø¦Ø¬
// Ø¹Ù†Ø¯ Ø§Ù„Ø§Ø®ØªÙŠØ§Ø± â†’ ÙŠÙÙ…Ù„Ø£ Ø§Ù„Ø£Ø¬Ø± ØªÙ„Ù‚Ø§Ø¦ÙŠØ§Ù‹ Ù…Ù† salary Ø§Ù„Ù…ÙˆØ¸Ù
// Ø¥Ø°Ø§ Ù„Ù… ÙŠÙÙˆØ¬Ø¯ â†’ ÙŠÙØ­ÙØ¸ ÙƒÙ€ worker_name ÙÙ‚Ø· (Ø¨Ø¯ÙˆÙ† Ø±Ø¨Ø·)
```

### Backend â€” `LaborEntry` model (ØªØ¹Ø¯ÙŠÙ„):
```python
# Ø¥Ø¶Ø§ÙØ© Ø¥Ù„Ù‰ Ø§Ù„Ù…ÙˆØ¯ÙŠÙ„ Ø§Ù„Ù…ÙˆØ¬ÙˆØ¯:
employee = models.ForeignKey(
    'hr.Employee',
    null=True, blank=True,
    on_delete=models.SET_NULL,
    related_name='labor_entries',
    help_text="Ø±Ø¨Ø· Ø¨Ù…ÙˆØ¸Ù HR Ø¥Ø°Ø§ ÙƒØ§Ù† Ù…Ø³Ø¬Ù„Ø§Ù‹"
)
```

### Ù…Ù†Ø·Ù‚ Ø§Ù„Ø­ÙØ¸ ÙÙŠ Backend:
```python
# ÙÙŠ serializer Ø£Ùˆ service:
def resolve_employee(worker_name, company):
    """Ø§Ù„Ø¨Ø­Ø« Ø¹Ù† Ù…ÙˆØ¸Ù Ø¨Ø§Ù„Ø§Ø³Ù… ÙÙŠ Ù†ÙØ³ Ø§Ù„Ø´Ø±ÙƒØ©"""
    try:
        return Employee.objects.get(
            user__name__iexact=worker_name,
            user__company=company
        )
    except Employee.DoesNotExist:
        return None
```

### Ø§Ù„Ù…Ù„ÙØ§Øª Ø§Ù„Ù…ØªØ£Ø«Ø±Ø©:
```
Back-End/apps/reports/models.py         â† Ø¥Ø¶Ø§ÙØ© employee FK Ø¥Ù„Ù‰ LaborEntry
Back-End/serializers/reports_serializers.py â† ØªØ­Ø¯ÙŠØ« LaborEntrySerializer
Front-End/src/pages/reports/DailyTaskReport/
â”œâ”€â”€ DailyTaskForm.jsx                   â† Ø¥Ø¶Ø§ÙØ© Ø²Ø± + Ù…Ù†Ø·Ù‚ Ø§Ù„Ù€ Drawer
â””â”€â”€ LaborEntryDrawer.jsx                â† Ø¬Ø¯ÙŠØ¯ (Drawer component)
```

---

# ðŸ”´ PHASE 3 â€” HR Module (Ø«Ø§Ù„Ø«Ø§Ù‹)

## 3.1 â€” Backend Models (ØªØ¹Ø¯ÙŠÙ„ `apps/hr/models.py`):

### Ø¥Ø¶Ø§ÙØ§Øª Ø¹Ù„Ù‰ Employee:
```python
address                  = models.TextField(blank=True, default='')
national_id              = models.CharField(max_length=20, blank=True, default='')
phone                    = models.CharField(max_length=20, blank=True, default='')
emergency_contact_name   = models.CharField(max_length=100, blank=True, default='')
emergency_contact_phone  = models.CharField(max_length=20, blank=True, default='')
avatar_url               = models.URLField(max_length=500, blank=True, default='')
# Ø§Ù„Ø±Ø§ØªØ¨ Ù…ÙˆØ¬ÙˆØ¯ â†’ Ù†Ø­ØªÙØ¸ Ø¨Ù‡
# salary = models.DecimalField(...) Ù…ÙˆØ¬ÙˆØ¯
```

### Ù…ÙˆØ¯ÙŠÙ„ Ø¬Ø¯ÙŠØ¯ `EmployeeAttachment`:
```python
class EmployeeAttachment(models.Model):
    FILE_TYPE_CHOICES = [
        ('image', 'ØµÙˆØ±Ø©'),
        ('pdf', 'PDF'),
        ('other', 'Ø£Ø®Ø±Ù‰'),
    ]
    employee    = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attachments')
    name        = models.CharField(max_length=200)
    file_url    = models.URLField(max_length=1000)      # Ø±Ø§Ø¨Ø· Cloudinary
    file_type   = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
```

## 3.2 â€” Auto-create Employee Ø¹Ù†Ø¯ ØªØ³Ø¬ÙŠÙ„ Ù…Ù‡Ù†Ø¯Ø³:

### ÙÙŠ `services/user_service.py`:
```python
FIELD_ROLES = ['ENGINEER', 'MANAGER', 'HR', 'ACCOUNTANT', 'WAREHOUSE']

def create_user(validated_data):
    user = User.objects.create_user(**validated_data)
    
    if user.role in FIELD_ROLES:
        from apps.hr.models import Employee
        # ØªØ­Ù‚Ù‚ Ø£Ù†Ù‡ Ù…Ø´ Ù…ÙˆØ¬ÙˆØ¯ (Ù„Ù„Ø£Ù…Ø§Ù†)
        Employee.objects.get_or_create(
            user=user,
            defaults={
                'hire_date': timezone.now().date(),
                'status': 'active',
            }
        )
    return user
```

## 3.3 â€” Backend Endpoints:

```
GET    /hr/employees/                  â† Ù‚Ø§Ø¦Ù…Ø© (ÙÙ„ØªØ±: status, department, search)
POST   /hr/employees/                  â† Ø¥Ù†Ø´Ø§Ø¡ Ù…ÙˆØ¸Ù ÙŠØ¯ÙˆÙŠ (non-user employee)
GET    /hr/employees/<id>/             â† ØªÙØ§ØµÙŠÙ„ ÙƒØ§Ù…Ù„Ø©
PATCH  /hr/employees/<id>/             â† ØªØ¹Ø¯ÙŠÙ„
DELETE /hr/employees/<id>/             â† soft delete (status=terminated)

GET    /hr/employees/<id>/attachments/ â† Ù…Ù„ÙØ§Øª Ø§Ù„Ù…ÙˆØ¸Ù
POST   /hr/employees/<id>/attachments/ â† Ø±ÙØ¹ Ù…Ù„Ù (file_url + file_type + name)
DELETE /hr/attachments/<id>/           â† Ø­Ø°Ù Ù…Ù„Ù

GET    /hr/employees/search/?q=Ø§Ø³Ù…     â† Ù„Ù„Ù€ autocomplete ÙÙŠ LaborEntry

GET    /hr/leaves/                     â† Ø§Ù„Ø¥Ø¬Ø§Ø²Ø§Øª (ÙÙ„ØªØ±: status, employee, date)
POST   /hr/leaves/                     â† Ø·Ù„Ø¨ Ø¥Ø¬Ø§Ø²Ø©
PATCH  /hr/leaves/<id>/approve/        â† Ù…ÙˆØ§ÙÙ‚Ø©
PATCH  /hr/leaves/<id>/reject/         â† Ø±ÙØ¶

GET    /hr/attendance/                 â† Ø§Ù„Ø­Ø¶ÙˆØ± (ÙÙ„ØªØ±: date, employee)
POST   /hr/attendance/                 â† ØªØ³Ø¬ÙŠÙ„ Ø­Ø¶ÙˆØ±
PATCH  /hr/attendance/<id>/            â† ØªØ¹Ø¯ÙŠÙ„
```

## 3.4 â€” Frontend Pages:

```
src/pages/hr/
â”œâ”€â”€ HRDashboard.jsx          â† Ø¨Ø·Ø§Ù‚Ø§Øª Ø¥Ø­ØµØ§Ø¦ÙŠØ© (Ù…ÙˆØ¸ÙÙŠÙ†ØŒ Ø¥Ø¬Ø§Ø²Ø§Øª Ù…Ø¹Ù„Ù‚Ø©ØŒ Ø­Ø¶ÙˆØ± Ø§Ù„ÙŠÙˆÙ…)
â”œâ”€â”€ EmployeeList.jsx         â† Ø¬Ø¯ÙˆÙ„ + ÙÙ„Ø§ØªØ± + Ø¨Ø­Ø«
â”œâ”€â”€ EmployeeForm.jsx         â† Ù†Ù…ÙˆØ°Ø¬ Ø¥Ø¶Ø§ÙØ©/ØªØ¹Ø¯ÙŠÙ„ (Dialog Ø£Ùˆ Page)
â”œâ”€â”€ EmployeeDetail.jsx       â† ØªÙØ§ØµÙŠÙ„ Ø¨Ù€ 4 Tabs:
â”‚   â”œâ”€â”€ Tab 1: Ø§Ù„Ø¨ÙŠØ§Ù†Ø§Øª Ø§Ù„Ø£Ø³Ø§Ø³ÙŠØ©
â”‚   â”œâ”€â”€ Tab 2: Ø§Ù„Ù…Ù„ÙØ§Øª ÙˆØ§Ù„Ù…Ø±ÙÙ‚Ø§Øª (Cloudinary upload)
â”‚   â”œâ”€â”€ Tab 3: Ø³Ø¬Ù„ Ø§Ù„Ø­Ø¶ÙˆØ±
â”‚   â””â”€â”€ Tab 4: Ø§Ù„Ø¥Ø¬Ø§Ø²Ø§Øª
â””â”€â”€ LeaveManagement.jsx      â† Ø¥Ø¯Ø§Ø±Ø© Ø·Ù„Ø¨Ø§Øª Ø§Ù„Ø¥Ø¬Ø§Ø²Ø§Øª
```

---

# ðŸ”´ PHASE 4 â€” Admin Dashboard (Ø±Ø§Ø¨Ø¹Ø§Ù‹)

## Ù‡ÙŠÙƒÙ„ Ø§Ù„ØµÙØ­Ø©:

```
/admin                                 (SUPER_ADMIN + OWNER + MANAGER)
â”œâ”€â”€ ðŸ‘¥ Ø§Ù„Ù…Ø³ØªØ®Ø¯Ù…ÙŠÙ†          â† Ù…ÙˆØ¬ÙˆØ¯ØŒ ÙŠØ¨Ù‚Ù‰
â”œâ”€â”€ ðŸŽ¨ Ù…Ø­ØªÙˆÙ‰ Ø§Ù„Ù…ÙˆÙ‚Ø¹ (CMS) â† Ù…ÙˆØ¬ÙˆØ¯ØŒ ÙŠØ¨Ù‚Ù‰
â”œâ”€â”€ âš™ï¸ Ø§Ù„Ø­Ù‚ÙˆÙ„ Ø§Ù„Ù…Ø®ØµØµØ©     â† Ù…Ù†Ù‚ÙˆÙ„ Ù…Ù† Reports (SUPER_ADMIN + OWNER + MANAGER)
â”œâ”€â”€ ðŸ”§ Ø§Ù„Ø¹Ù…Ù„ÙŠØ§Øª Ø§Ù„ÙÙ†ÙŠØ©     â† Ø¬Ø¯ÙŠØ¯ (SUPER_ADMIN + OWNER + MANAGER)
â”œâ”€â”€ ðŸ‘· Ø§Ù„Ù…Ù‚Ø§ÙˆÙ„ÙˆÙ†           â† Ø¬Ø¯ÙŠØ¯ (SUPER_ADMIN + OWNER + MANAGER)
â”œâ”€â”€ ðŸ“‹ Ù‚ÙˆØ§Ø¦Ù… Ø§Ù„ØªÙ‚Ø§Ø±ÙŠØ±      â† Ø¬Ø¯ÙŠØ¯ â€” Varieties + Units (SUPER_ADMIN + OWNER + MANAGER)
â”œâ”€â”€ ðŸŒ¿ Ø¥Ø¹Ø¯Ø§Ø¯Ø§Øª Ø§Ù„Ù…Ø­Ø§ØµÙŠÙ„    â† Ø¬Ø¯ÙŠØ¯ â€” Ø£Ù†ÙˆØ§Ø¹ Ø§Ù„Ù…Ø­Ø§ØµÙŠÙ„ Ù„ÙƒÙ„ Ù…Ø²Ø±Ø¹Ø© (SUPER_ADMIN + OWNER)
â””â”€â”€ ðŸ¢ Ø¥Ø¹Ø¯Ø§Ø¯Ø§Øª Ø§Ù„Ø´Ø±ÙƒØ©      â† Ø¬Ø¯ÙŠØ¯ (SUPER_ADMIN + OWNER ÙÙ‚Ø·)
```

## Permission Matrix Ù„Ù„Ù€ Admin:

| Section | SUPER_ADMIN | OWNER | MANAGER |
|---------|------------|-------|---------|
| Ø§Ù„Ù…Ø³ØªØ®Ø¯Ù…ÙŠÙ† | âœ… ÙƒØ§Ù…Ù„ | âœ… ÙƒØ§Ù…Ù„ | âœ… Ø¬Ø²Ø¦ÙŠ (Ù„Ø§ Ø­Ø°Ù) |
| CMS | âœ… | âœ… | âŒ |
| Ø§Ù„Ø­Ù‚ÙˆÙ„ Ø§Ù„Ù…Ø®ØµØµØ© | âœ… | âœ… | âœ… |
| Ø§Ù„Ø¹Ù…Ù„ÙŠØ§Øª Ø§Ù„ÙÙ†ÙŠØ© | âœ… | âœ… | âœ… |
| Ø§Ù„Ù…Ù‚Ø§ÙˆÙ„ÙˆÙ† | âœ… | âœ… | âœ… |
| Ù‚ÙˆØ§Ø¦Ù… Ø§Ù„ØªÙ‚Ø§Ø±ÙŠØ± | âœ… | âœ… | âœ… |
| Ø¥Ø¹Ø¯Ø§Ø¯Ø§Øª Ø§Ù„Ù…Ø­Ø§ØµÙŠÙ„ | âœ… | âœ… | âŒ |
| Ø¥Ø¹Ø¯Ø§Ø¯Ø§Øª Ø§Ù„Ø´Ø±ÙƒØ© | âœ… | âœ… | âŒ |

## Ø§Ù„Ù…ÙŠØ²Ø© Ø§Ù„Ø£Ø³Ø§Ø³ÙŠØ© â€” Dynamic Report Fields:
```
Admin ÙŠÙ‚Ø¯Ø±:
âœ… ÙŠØ¶ÙŠÙ Ø­Ù‚Ù„ Ù…Ø®ØµØµ Ù„Ø£ÙŠ ØªÙ‚Ø±ÙŠØ±
âœ… ÙŠØºÙŠØ± Ù†ÙˆØ¹ Ø§Ù„Ø­Ù‚Ù„ (text/number/date/dropdown/boolean)
âœ… ÙŠØ¶ÙŠÙ Ø®ÙŠØ§Ø±Ø§Øª dropdown Ù…Ø¨Ø§Ø´Ø±Ø©
âœ… ÙŠØ±ØªØ¨ Ø§Ù„Ø­Ù‚ÙˆÙ„ Ø¨Ù€ Drag & Drop
âœ… ÙŠØ®ÙÙŠ/ÙŠØ¸Ù‡Ø± Ø§Ù„Ø­Ù‚ÙˆÙ„ Ø§Ù„Ø«Ø§Ø¨ØªØ©
âœ… ÙŠØ¬Ø¹Ù„ Ø§Ù„Ø­Ù‚Ù„ Ø¥Ø¬Ø¨Ø§Ø±ÙŠ Ø£Ùˆ Ø§Ø®ØªÙŠØ§Ø±ÙŠ
âœ… ÙŠØ±Ø¨Ø· Ø§Ù„Ø­Ù‚Ù„ Ø¨Ù€ Ù…Ø­ØµÙˆÙ„ Ù…Ø¹ÙŠÙ† (ÙÙ‚Ø· ÙŠØ¸Ù‡Ø± Ù„Ù„Ù†Ø®ÙŠÙ„ Ù…Ø«Ù„Ø§Ù‹)
```

---

# ðŸŸ¡ PHASE 5 â€” Warehouse â€” Ø¥Ø¯Ø§Ø±Ø© Ø§Ù„Ù…Ø®Ø§Ø²Ù†

## Ø§Ù„Ø­Ø§Ù„Ø© Ø§Ù„Ø­Ø§Ù„ÙŠØ©:
Ù…ÙˆØ¬ÙˆØ¯ backend Ø£Ø³Ø§Ø³ÙŠ (Items + Movements) â€” ÙŠØ­ØªØ§Ø¬ ØªØ­Ø³ÙŠÙ† UI ÙˆØ¥Ø¶Ø§ÙØ§Øª.

## Ø§Ù„Ø¥Ø¶Ø§ÙØ§Øª Ø§Ù„Ù…Ø·Ù„ÙˆØ¨Ø©:

### Backend:
```python
# Ø¥Ø¶Ø§ÙØ© Ù„Ù€ WarehouseItem:
category = models.CharField(max_length=100)          # ÙØ¦Ø© Ø§Ù„Ù…Ù†ØªØ¬
unit = models.CharField(max_length=50)               # Ø§Ù„ÙˆØ­Ø¯Ø© (ÙƒÙŠÙ„Ùˆ/Ù„ØªØ±/Ù‚Ø·Ø¹Ø©)
min_stock = models.FloatField(default=0)             # Ø§Ù„Ø­Ø¯ Ø§Ù„Ø£Ø¯Ù†Ù‰ Ù„Ù„ØªÙ†Ø¨ÙŠÙ‡
location = models.CharField(max_length=200, blank=True)  # Ù…ÙˆÙ‚Ø¹ Ø§Ù„Ù…Ø®Ø²Ù†

# Endpoint Ø¬Ø¯ÙŠØ¯:
GET /warehouse/alerts/    â† Ø¹Ù†Ø§ØµØ± Ù‚Ø§Ø±Ø¨Øª Ø¹Ù„Ù‰ Ø§Ù„Ù†ÙØ§Ø¯ (quantity <= min_stock)
GET /warehouse/summary/   â† Ø¥Ø¬Ù…Ø§Ù„ÙŠØ§Øª (Ù‚ÙŠÙ…Ø© Ø§Ù„Ù…Ø®Ø²Ù†ØŒ Ø¹Ø¯Ø¯ Ø§Ù„Ø£ØµÙ†Ø§ÙØŒ Ø§Ù„ØªÙ†Ø¨ÙŠÙ‡Ø§Øª)
```

### Frontend:
```
src/pages/warehouse/
â”œâ”€â”€ InventoryLedger.jsx    â† Ù…ÙˆØ¬ÙˆØ¯ â€” ØªØ­Ø³ÙŠÙ† UI
â”œâ”€â”€ LowStockAlerts.jsx     â† Ø¬Ø¯ÙŠØ¯ â€” ØªÙ†Ø¨ÙŠÙ‡Ø§Øª Ù†Ù‚Øµ Ø§Ù„Ù…Ø®Ø²ÙˆÙ†
â””â”€â”€ WarehouseSummary.jsx   â† Ø¬Ø¯ÙŠØ¯ â€” Ø¨Ø·Ø§Ù‚Ø§Øª Ø¥Ø­ØµØ§Ø¦ÙŠØ©
```

### Ø±Ø¨Ø· Ù…Ø¹ Ø§Ù„Ù†Ø¸Ø§Ù…:
- ØªÙ‚Ø±ÙŠØ± Ø§Ù„ØªØ³Ù…ÙŠØ¯ â†’ ÙŠØ®ØµÙ… Ù…Ù† Ù…Ø®Ø²ÙˆÙ† Ø§Ù„Ù…ÙˆØ§Ø¯
- Alert ØªÙ„Ù‚Ø§Ø¦ÙŠ Ù„Ù€ Manager/OWNER Ø¹Ù†Ø¯ Ù†Ù‚Øµ Ø§Ù„Ù…Ø®Ø²ÙˆÙ†

---

# ðŸŸ¡ PHASE 6 â€” Accounting â€” Ø§Ù„Ù…Ø­Ø§Ø³Ø¨Ø©

## Ø§Ù„Ø­Ø§Ù„Ø© Ø§Ù„Ø­Ø§Ù„ÙŠØ©:
FinanceDashboard Ù…ÙˆØ¬ÙˆØ¯ â€” ÙŠØ­ØªØ§Ø¬ Ø±Ø¨Ø· Ø¨Ø§Ù„Ø¨ÙŠØ§Ù†Ø§Øª Ø§Ù„Ø­Ù‚ÙŠÙ‚ÙŠØ©.

## Ø§Ù„Ø¥Ø¶Ø§ÙØ§Øª Ø§Ù„Ù…Ø·Ù„ÙˆØ¨Ø©:

### Backend:
```python
# Ø±Ø¨Ø· Ø§Ù„Ø±ÙˆØ§ØªØ¨ Ø¨Ù€ HR:
GET /accounting/payroll/         â† Ø±ÙˆØ§ØªØ¨ Ø§Ù„Ù…ÙˆØ¸ÙÙŠÙ† Ù…Ù† HR + LaborEntry costs
GET /accounting/labor-costs/     â† ØªÙƒÙ„ÙØ© Ø§Ù„Ø¹Ù…Ø§Ù„Ø© Ù…Ù† Ø§Ù„ØªÙ‚Ø§Ø±ÙŠØ± Ø§Ù„ÙŠÙˆÙ…ÙŠØ©
GET /accounting/monthly-summary/ â† Ù…Ù„Ø®Øµ Ø´Ù‡Ø±ÙŠ (Ø¥ÙŠØ±Ø§Ø¯Ø§Øª - Ù…ØµØ±ÙˆÙØ§Øª)

# ØªÙ‚Ø±ÙŠØ± Ø§Ù„ØªÙƒÙ„ÙØ© Ù„ÙƒÙ„ Ø­Ù‚Ù„:
GET /accounting/location-costs/?location_id=X â† ØªÙƒÙ„ÙØ© Ù…ÙˆÙ‚Ø¹ Ù…Ø¹ÙŠÙ†
```

### Frontend:
```
src/pages/accounting/
â”œâ”€â”€ FinanceDashboard.jsx    â† Ù…ÙˆØ¬ÙˆØ¯ â€” Ø¥Ø¶Ø§ÙØ© charts Ø­Ù‚ÙŠÙ‚ÙŠØ©
â”œâ”€â”€ PayrollPage.jsx         â† Ø¬Ø¯ÙŠØ¯ â€” ÙƒØ´Ù Ø±ÙˆØ§ØªØ¨ Ù…Ø±Ø¨ÙˆØ· Ø¨Ù€ HR
â”œâ”€â”€ CostAnalysis.jsx        â† Ø¬Ø¯ÙŠØ¯ â€” ØªØ­Ù„ÙŠÙ„ ØªÙƒÙ„ÙØ© Ù„ÙƒÙ„ Ù…ÙˆÙ‚Ø¹/Ø¹Ù…Ù„ÙŠØ©
â””â”€â”€ ExpenseTracker.jsx      â† Ø¬Ø¯ÙŠØ¯ â€” ØªØªØ¨Ø¹ Ø§Ù„Ù…ØµØ±ÙˆÙØ§Øª
```

### Ø±Ø¨Ø· Ù…Ø¹ Ø§Ù„Ù†Ø¸Ø§Ù…:
```
HR.salary â†’ Accounting.payroll
LaborEntry (hours Ã— rate) â†’ Accounting.labor_cost
Warehouse.movements â†’ Accounting.material_cost
```

---

# ðŸŸ¡ PHASE 7 â€” Fleet & Equipment â€” Ø§Ù„Ø£Ø³Ø·ÙˆÙ„ ÙˆØ§Ù„Ù…Ø¹Ø¯Ø§Øª

## Ø§Ù„Ø­Ø§Ù„Ø© Ø§Ù„Ø­Ø§Ù„ÙŠØ©:
FleetManager Ù…ÙˆØ¬ÙˆØ¯ â€” ÙŠØ­ØªØ§Ø¬ Ø±Ø¨Ø· Ø¨Ø§Ù„ØªÙ‚Ø§Ø±ÙŠØ±.

## Ø§Ù„Ø¥Ø¶Ø§ÙØ§Øª Ø§Ù„Ù…Ø·Ù„ÙˆØ¨Ø©:

### Backend:
```python
# Ø¥Ø¶Ø§ÙØ© Ù„Ù€ Equipment:
assigned_location = models.ForeignKey('farm.LocationNode', null=True, blank=True, ...)
# Ø±Ø¨Ø· Ø§Ø³ØªØ®Ø¯Ø§Ù… Ø§Ù„Ù…Ø¹Ø¯Ø§Øª Ø¨Ø§Ù„ØªÙ‚Ø§Ø±ÙŠØ± Ø§Ù„ÙŠÙˆÙ…ÙŠØ©:
class EquipmentUsageLog(TenantAwareModel):
    equipment = models.ForeignKey(Equipment, ...)
    report    = models.ForeignKey('reports.DailyTaskReport', null=True, blank=True, ...)
    date      = models.DateField()
    hours     = models.FloatField()
    operator  = models.ForeignKey(settings.AUTH_USER_MODEL, ...)
    notes     = models.TextField(blank=True)
```

### ÙÙŠ Ø§Ù„ØªÙ‚Ø±ÙŠØ± Ø§Ù„ÙŠÙˆÙ…ÙŠ â€” Ø¥Ø¶Ø§ÙØ©:
```
Ø§Ù„Ù…Ø¹Ø¯Ø§Øª Ø§Ù„Ù…Ø³ØªØ®Ø¯Ù…Ø©: [dropdown Ù…Ù† Ø§Ù„Ù…Ø¹Ø¯Ø§Øª] + Ø³Ø§Ø¹Ø§Øª Ø§Ù„Ø§Ø³ØªØ®Ø¯Ø§Ù…
```

### Frontend:
```
src/pages/equipment/
â”œâ”€â”€ FleetManager.jsx      â† Ù…ÙˆØ¬ÙˆØ¯ â€” Ø¥Ø¶Ø§ÙØ© Ø±Ø¨Ø· Ø¨Ø§Ù„ØªÙ‚Ø§Ø±ÙŠØ±
â”œâ”€â”€ MaintenanceLog.jsx    â† Ø¬Ø¯ÙŠØ¯ â€” Ø³Ø¬Ù„ Ø§Ù„ØµÙŠØ§Ù†Ø©
â””â”€â”€ UsageAnalytics.jsx    â† Ø¬Ø¯ÙŠØ¯ â€” ØªØ­Ù„ÙŠÙ„ Ø§Ø³ØªØ®Ø¯Ø§Ù… Ø§Ù„Ù…Ø¹Ø¯Ø§Øª
```

---

# ðŸŸ¢ PHASE 8 & 9 â€” Palm + Olive Records (ØªÙˆØ­ÙŠØ¯)

## Ø§Ù„Ù…Ø´ÙƒÙ„Ø© Ø§Ù„Ø­Ø§Ù„ÙŠØ©:
Ù…ÙˆØ¯ÙŠÙ„Ø§Ù† Ù…Ù†ÙØµÙ„Ø§Ù† (PalmRecord + OliveRecord) â€” ÙˆÙ‡Ø°Ø§ Ø®Ù„Ø§Ù Ù…Ø¨Ø¯Ø£ Ø§Ù„Ù€ SaaS.

## Ø§Ù„Ø­Ù„ (Ù…Ù† REFACTOR_PLAN):
```python
# Ù…ÙˆØ¯ÙŠÙ„ Ù…ÙˆØ­Ø¯ CropRecord:
class CropRecord(TenantAwareModel):
    CROP_TYPES = [
        ('palm',  'Ù†Ø®ÙŠÙ„'),
        ('olive', 'Ø²ÙŠØªÙˆÙ†'),
        ('grape', 'Ø¹Ù†Ø¨'),     # Ù‚Ø§Ø¨Ù„ Ù„Ù„ØªÙˆØ³Ø¹Ø© Ù„Ø£ÙŠ Ù…Ø­ØµÙˆÙ„
        ('other', 'Ø£Ø®Ø±Ù‰'),
    ]
    crop_type  = models.CharField(max_length=20, choices=CROP_TYPES)
    location   = models.ForeignKey('farm.LocationNode', ...)
    # Ø§Ù„Ø­Ù‚ÙˆÙ„ Ø§Ù„Ù…Ø´ØªØ±ÙƒØ©
    tree_count = models.IntegerField(default=0)
    area       = models.FloatField(null=True, blank=True, help_text="Ø¨Ø§Ù„ÙØ¯Ø§Ù†")
    variety    = models.ForeignKey('reports.Variety', null=True, blank=True, ...)
    notes      = models.TextField(blank=True)
    # Ø§Ù„Ø­Ù‚ÙˆÙ„ Ø§Ù„Ø¥Ø¶Ø§ÙÙŠØ© Ø§Ù„Ù…Ø®ØµØµØ© â†’ CustomField system
```

### Frontend:
```
src/pages/crops/
â”œâ”€â”€ CropRecords.jsx        â† Ù…ÙˆØ­Ø¯ Ø¨Ù€ type filter (ÙŠØ¹ÙˆØ¶ Palm + Olive)
â””â”€â”€ CropDetail.jsx         â† ØªÙØ§ØµÙŠÙ„ + Ø¥Ø­ØµØ§Ø¡Ø§Øª + ØµÙˆØ±
```

### Ù…Ù„Ø§Ø­Ø¸Ø© Ù„Ù„Ù€ SaaS:
Ø§Ù„Ù€ Admin ÙŠØ¶ÙŠÙ Ø£Ù†ÙˆØ§Ø¹ Ø§Ù„Ù…Ø­Ø§ØµÙŠÙ„ Ù…Ù† Admin Dashboard â€” Ù„Ø§ ØªØ¹Ø¯ÙŠÙ„ ÙƒÙˆØ¯.

---

# ðŸŸ¢ PHASE 10 â€” Production â€” Ø§Ù„Ù…Ø­ØµÙˆÙ„

## Ø§Ù„Ø¥Ø¶Ø§ÙØ§Øª Ø§Ù„Ù…Ø·Ù„ÙˆØ¨Ø©:

### Backend:
```python
# Ø¥Ø¶Ø§ÙØ© Ù„Ù€ YieldRecord:
location   = models.ForeignKey('farm.LocationNode', ...)   # Ø±Ø¨Ø· Ø¨Ø§Ù„Ù…ÙˆÙ‚Ø¹
crop_type  = models.CharField(max_length=20)               # Ù†ÙˆØ¹ Ø§Ù„Ù…Ø­ØµÙˆÙ„
variety    = models.ForeignKey('reports.Variety', null=True, ...)
# season tracking:
season     = models.CharField(max_length=50, blank=True)   # Ù…ÙˆØ³Ù… Ø§Ù„Ø­ØµØ§Ø¯
```

### Frontend:
```
src/pages/production/
â”œâ”€â”€ YieldTracking.jsx     â† Ù…ÙˆØ¬ÙˆØ¯ â€” Ø¥Ø¶Ø§ÙØ© location filter
â”œâ”€â”€ HarvestCalendar.jsx   â† Ø¬Ø¯ÙŠØ¯ â€” ØªÙ‚ÙˆÙŠÙ… Ø§Ù„Ù…Ø­ØµÙˆÙ„
â””â”€â”€ YieldAnalytics.jsx    â† Ø¬Ø¯ÙŠØ¯ â€” Ù…Ù‚Ø§Ø±Ù†Ø© Ø³Ù†Ø© Ø¨Ø³Ù†Ø©
```

---

# ðŸ“ Ø§Ù„Ù‡ÙŠÙƒÙ„ Ø§Ù„ÙƒØ§Ù…Ù„ Ù„Ù„Ù…Ù„ÙØ§Øª Ø§Ù„Ù†Ù‡Ø§Ø¦ÙŠ

## Backend:
```
Back-End/
â”œâ”€â”€ apps/
â”‚   â”œâ”€â”€ hr/
â”‚   â”‚   â”œâ”€â”€ models.py          â† ØªØ¹Ø¯ÙŠÙ„ (+ address, phone, EmployeeAttachment)
â”‚   â”‚   â”œâ”€â”€ views.py           â† Ø¬Ø¯ÙŠØ¯ ÙƒØ§Ù…Ù„
â”‚   â”‚   â””â”€â”€ migrations/        â† migration Ø¬Ø¯ÙŠØ¯Ø©
â”‚   â”œâ”€â”€ reports/
â”‚   â”‚   â””â”€â”€ models.py          â† Ø¥Ø¶Ø§ÙØ© employee FK Ø¥Ù„Ù‰ LaborEntry
â”‚   â”œâ”€â”€ farm/
â”‚   â”‚   â””â”€â”€ models.py          â† ØªÙ†Ø¸ÙŠÙ (Ø§Ù„Ù…ÙˆØ¯ÙŠÙ„Ø§Øª Ø§Ù„Ù‚Ø¯ÙŠÙ…Ø© deprecated)
â”‚   â””â”€â”€ crops/                 â† Ø¬Ø¯ÙŠØ¯ (ÙŠÙˆØ­Ø¯ Palm + Olive)
â”‚       â”œâ”€â”€ models.py          â† CropRecord
â”‚       â””â”€â”€ migrations/
â”œâ”€â”€ serializers/
â”‚   â”œâ”€â”€ hr_serializers.py      â† Ø¬Ø¯ÙŠØ¯
â”‚   â””â”€â”€ reports_serializers.py â† ØªØ­Ø¯ÙŠØ« LaborEntry
â”œâ”€â”€ api/endpoints/
â”‚   â”œâ”€â”€ hr_views.py            â† Ø¬Ø¯ÙŠØ¯
â”‚   â””â”€â”€ admin_views.py         â† Ø¬Ø¯ÙŠØ¯
â”œâ”€â”€ services/
â”‚   â””â”€â”€ user_service.py        â† ØªØ¹Ø¯ÙŠÙ„ (auto-create Employee)
â””â”€â”€ api/urls.py                â† Ø¥Ø¶Ø§ÙØ© Ø¬Ù…ÙŠØ¹ Ø§Ù„Ù€ routes
```

## Frontend:
```
Front-End/src/
â”œâ”€â”€ layouts/
â”‚   â”œâ”€â”€ DashboardLayout.jsx    â† ØªØ¹Ø¯ÙŠÙ„ (Ø¥Ø¶Ø§ÙØ© Sidebar)
â”‚   â””â”€â”€ Sidebar.jsx            â† Ø¬Ø¯ÙŠØ¯ (role-based navigation)
â”œâ”€â”€ features/
â”‚   â””â”€â”€ hr/
â”‚       â””â”€â”€ services.js        â† Ø¬Ø¯ÙŠØ¯
â”œâ”€â”€ pages/
â”‚   â”œâ”€â”€ farm/
â”‚   â”‚   â”œâ”€â”€ FarmStructure.jsx  â† ØªØ¹Ø¯ÙŠÙ„ (Adaptive Tree)
â”‚   â”‚   â””â”€â”€ FarmStructure.css  â† ØªØ¹Ø¯ÙŠÙ„
â”‚   â”œâ”€â”€ reports/DailyTaskReport/
â”‚   â”‚   â”œâ”€â”€ DailyTaskForm.jsx  â† ØªØ¹Ø¯ÙŠÙ„ (+ LaborEntry button)
â”‚   â”‚   â””â”€â”€ LaborEntryDrawer.jsx â† Ø¬Ø¯ÙŠØ¯
â”‚   â”œâ”€â”€ hr/
â”‚   â”‚   â”œâ”€â”€ HRDashboard.jsx    â† Ø¬Ø¯ÙŠØ¯
â”‚   â”‚   â”œâ”€â”€ EmployeeList.jsx   â† Ø¬Ø¯ÙŠØ¯
â”‚   â”‚   â”œâ”€â”€ EmployeeForm.jsx   â† Ø¬Ø¯ÙŠØ¯
â”‚   â”‚   â”œâ”€â”€ EmployeeDetail.jsx â† Ø¬Ø¯ÙŠØ¯
â”‚   â”‚   â””â”€â”€ LeaveManagement.jsx â† Ø¬Ø¯ÙŠØ¯
â”‚   â”œâ”€â”€ admin/
â”‚   â”‚   â”œâ”€â”€ AdminDashboard.jsx â† ØªØ¹Ø¯ÙŠÙ„ ÙƒØ¨ÙŠØ±
â”‚   â”‚   â””â”€â”€ sections/
â”‚   â”‚       â”œâ”€â”€ CustomFieldsAdmin.jsx  â† Ù†Ù‚Ù„ + ØªØ­Ø³ÙŠÙ†
â”‚   â”‚       â”œâ”€â”€ OperationsAdmin.jsx    â† Ø¬Ø¯ÙŠØ¯
â”‚   â”‚       â”œâ”€â”€ ContractorsAdmin.jsx   â† Ø¬Ø¯ÙŠØ¯
â”‚   â”‚       â”œâ”€â”€ DropdownsAdmin.jsx     â† Ø¬Ø¯ÙŠØ¯
â”‚   â”‚       â”œâ”€â”€ CropTypesAdmin.jsx     â† Ø¬Ø¯ÙŠØ¯ (Ù„Ù„Ù€ SaaS)
â”‚   â”‚       â””â”€â”€ CompanySettings.jsx    â† Ø¬Ø¯ÙŠØ¯
â”‚   â”œâ”€â”€ crops/
â”‚   â”‚   â”œâ”€â”€ CropRecords.jsx    â† Ø¬Ø¯ÙŠØ¯ (ÙŠÙˆØ­Ø¯ Palm + Olive)
â”‚   â”‚   â””â”€â”€ CropDetail.jsx     â† Ø¬Ø¯ÙŠØ¯
â”‚   â”œâ”€â”€ warehouse/
â”‚   â”‚   â””â”€â”€ InventoryLedger.jsx â† ØªØ­Ø³ÙŠÙ† + Ø¥Ø¶Ø§ÙØ§Øª
â”‚   â”œâ”€â”€ accounting/
â”‚   â”‚   â”œâ”€â”€ FinanceDashboard.jsx â† ØªØ­Ø³ÙŠÙ†
â”‚   â”‚   â””â”€â”€ PayrollPage.jsx    â† Ø¬Ø¯ÙŠØ¯
â”‚   â”œâ”€â”€ equipment/
â”‚   â”‚   â””â”€â”€ FleetManager.jsx   â† ØªØ­Ø³ÙŠÙ† + Ø±Ø¨Ø·
â”‚   â””â”€â”€ production/
â”‚       â””â”€â”€ YieldTracking.jsx  â† ØªØ­Ø³ÙŠÙ† + Ø±Ø¨Ø·
â””â”€â”€ routes/
    â””â”€â”€ AppRoutes.jsx          â† Ø¥Ø¶Ø§ÙØ© Ø¬Ù…ÙŠØ¹ Ø§Ù„Ù€ routes Ø§Ù„Ø¬Ø¯ÙŠØ¯Ø©
```

---

# ðŸš€ ØªØ±ØªÙŠØ¨ Ø§Ù„ØªÙ†ÙÙŠØ° Ø§Ù„ÙƒØ§Ù…Ù„

```
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
PHASE 1 â€” FarmStructure Adaptive Tree
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
Ø§Ù„Ø®Ø·ÙˆØ© 1.1: ØªØ¹Ø¯ÙŠÙ„ FarmStructure.jsx (getNodeConfig function)
Ø§Ù„Ø®Ø·ÙˆØ© 1.2: ØªØ¹Ø¯ÙŠÙ„ FarmStructure.css (size classes)
Ø§Ù„Ø®Ø·ÙˆØ© 1.3: Ø¥Ø¶Ø§ÙØ© Collapse/Expand
Ø§Ù„Ø®Ø·ÙˆØ© 1.4: Ø¥Ø¶Ø§ÙØ© Search/Filter
Ø§Ù„Ø®Ø·ÙˆØ© 1.5: Ø¥Ø¶Ø§ÙØ© Count badges

â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
PHASE 2 â€” LaborEntry Panel
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
Ø§Ù„Ø®Ø·ÙˆØ© 2.1: migration Ø¥Ø¶Ø§ÙØ© employee FK Ø¥Ù„Ù‰ LaborEntry
Ø§Ù„Ø®Ø·ÙˆØ© 2.2: ØªØ­Ø¯ÙŠØ« LaborEntrySerializer
Ø§Ù„Ø®Ø·ÙˆØ© 2.3: Ø¥Ù†Ø´Ø§Ø¡ LaborEntryDrawer.jsx
Ø§Ù„Ø®Ø·ÙˆØ© 2.4: ØªØ¹Ø¯ÙŠÙ„ DailyTaskForm.jsx (Ø¥Ø¶Ø§ÙØ© Ø§Ù„Ø²Ø± ÙˆØ§Ù„Ø±Ø¨Ø·)
Ø§Ù„Ø®Ø·ÙˆØ© 2.5: Ø¥Ø¶Ø§ÙØ© employee search endpoint

â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
PHASE 3 â€” HR Backend
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
Ø§Ù„Ø®Ø·ÙˆØ© 3.1: ØªØ¹Ø¯ÙŠÙ„ Employee model + Ø¥Ø¶Ø§ÙØ© EmployeeAttachment
Ø§Ù„Ø®Ø·ÙˆØ© 3.2: migration
Ø§Ù„Ø®Ø·ÙˆØ© 3.3: Ø¥Ù†Ø´Ø§Ø¡ hr_serializers.py
Ø§Ù„Ø®Ø·ÙˆØ© 3.4: Ø¥Ù†Ø´Ø§Ø¡ hr_views.py (ÙƒÙ„ Ø§Ù„Ù€ endpoints)
Ø§Ù„Ø®Ø·ÙˆØ© 3.5: ØªØ­Ø¯ÙŠØ« user_service.py (auto-create Employee)
Ø§Ù„Ø®Ø·ÙˆØ© 3.6: Ø¥Ø¶Ø§ÙØ© routes ÙÙŠ urls.py

â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
PHASE 4 â€” HR Frontend
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
Ø§Ù„Ø®Ø·ÙˆØ© 4.1: hr/services.js
Ø§Ù„Ø®Ø·ÙˆØ© 4.2: HRDashboard.jsx
Ø§Ù„Ø®Ø·ÙˆØ© 4.3: EmployeeList.jsx
Ø§Ù„Ø®Ø·ÙˆØ© 4.4: EmployeeForm.jsx
Ø§Ù„Ø®Ø·ÙˆØ© 4.5: EmployeeDetail.jsx (Ù…Ø¹ upload Ù…Ù„ÙØ§Øª Cloudinary)
Ø§Ù„Ø®Ø·ÙˆØ© 4.6: LeaveManagement.jsx

â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
PHASE 5 â€” Sidebar + Navigation
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
Ø§Ù„Ø®Ø·ÙˆØ© 5.1: Sidebar.jsx (role-based)
Ø§Ù„Ø®Ø·ÙˆØ© 5.2: ØªØ¹Ø¯ÙŠÙ„ DashboardLayout.jsx
Ø§Ù„Ø®Ø·ÙˆØ© 5.3: ØªØ­Ø¯ÙŠØ« AppRoutes.jsx
Ø§Ù„Ø®Ø·ÙˆØ© 5.4: BottomNav ØªØ­Ø¯ÙŠØ« (Ù„Ù„Ù…ÙˆØ¨Ø§ÙŠÙ„)

â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
PHASE 6 â€” Admin Dashboard
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
Ø§Ù„Ø®Ø·ÙˆØ© 6.1: Admin backend endpoints (operations, contractors, dropdowns)
Ø§Ù„Ø®Ø·ÙˆØ© 6.2: ØªØ¹Ø¯ÙŠÙ„ AdminDashboard.jsx (Ù‡ÙŠÙƒÙ„ Ø¬Ø¯ÙŠØ¯)
Ø§Ù„Ø®Ø·ÙˆØ© 6.3: Ù†Ù‚Ù„ CustomFields + ØªØ­Ø³ÙŠÙ†Ù‡Ø§
Ø§Ù„Ø®Ø·ÙˆØ© 6.4: OperationsAdmin + ContractorsAdmin
Ø§Ù„Ø®Ø·ÙˆØ© 6.5: DropdownsAdmin + CropTypesAdmin

â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
PHASE 7-10 â€” Ø¨Ø§Ù‚ÙŠ Ø§Ù„Ù€ Modules
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
Ø§Ù„Ø®Ø·ÙˆØ© 7: Warehouse ØªØ­Ø³ÙŠÙ†
Ø§Ù„Ø®Ø·ÙˆØ© 8: Accounting Ø±Ø¨Ø· + PayrollPage
Ø§Ù„Ø®Ø·ÙˆØ© 9: Fleet Ø±Ø¨Ø· Ø¨Ø§Ù„ØªÙ‚Ø§Ø±ÙŠØ±
Ø§Ù„Ø®Ø·ÙˆØ© 10: CropRecord ØªÙˆØ­ÙŠØ¯
Ø§Ù„Ø®Ø·ÙˆØ© 11: Production Ø±Ø¨Ø· Ø¨Ø§Ù„Ù…ÙˆØ§Ù‚Ø¹
```

---

# âš ï¸ Ù‚ÙˆØ§Ø¹Ø¯ Ù„Ù„Ù€ AI Coder

```
âŒ Ù„Ø§ ØªÙƒØ³Ø± Ø£ÙŠ API Ù…ÙˆØ¬ÙˆØ¯Ø© (Ø§Ù„Ù€ response shape Ø«Ø§Ø¨ØªØ©)
âŒ Ù„Ø§ ØªØ­Ø°Ù migrations â€” Ø£Ø¶Ù Ø¬Ø¯ÙŠØ¯Ø© ÙÙ‚Ø·
âŒ Ù„Ø§ ØªÙÙ†Ø´Ø¦ Ù…ÙˆØ¯ÙŠÙ„ Ø¬Ø¯ÙŠØ¯ Ø¥Ø°Ø§ ÙƒØ§Ù† Ù…Ø´Ø§Ø¨Ù‡ Ù…ÙˆØ¬ÙˆØ¯
âŒ Ù„Ø§ GenericForeignKey Ø¥Ù„Ø§ ÙÙŠ Ø§Ù„Ù€ CustomField system
âŒ Ù„Ø§ hardcoded roles ÙÙŠ Ø§Ù„Ù€ Frontend â€” Ø§Ø³ØªØ®Ø¯Ù… ROLE_PERMISSIONS object

âœ… ÙƒÙ„ queryset ÙŠÙ…Ø± Ø¹Ù„Ù‰ _for_company() Ø£Ùˆ .for_company()
âœ… ÙƒÙ„ endpoint Ù„Ù‡ permission_classes ØµØ±ÙŠØ­Ø©
âœ… Services layer Ù„Ù„Ù€ business logic
âœ… Serializers ØªØªØ­Ù‚Ù‚ Ù…Ù† Ø§Ù„Ù€ tenant scoping
âœ… ÙƒÙ„ migration ØªØ£ØªÙŠ Ø¨Ø¹Ø¯ Ø¥Ù†Ø´Ø§Ø¡ Ø§Ù„Ù€ model Ù…Ø¨Ø§Ø´Ø±Ø©
âœ… Ø§Ù„Ù€ Frontend ÙŠØ³ØªØ®Ø¯Ù… Ø§Ù„Ù€ role Ù…Ù† AuthContext Ù„Ù€ conditional rendering

# CLOUDINARY ÙÙŠ Frontend:
âœ… Ø§Ø³ØªØ®Ø¯Ù… unsigned upload Ù…Ø¹ upload_preset='atls_unsigned'
âœ… Ø§Ø­ÙØ¸ Ø§Ù„Ù€ secure_url ÙÙŠ DB â€” Ù…Ø´ Ø§Ù„Ù€ public_id
âœ… Ø§Ø¹Ø±Ø¶ preview Ù‚Ø¨Ù„ Ø§Ù„Ø±ÙØ¹
âœ… Ø§Ù‚Ø¨Ù„: jpg, jpeg, png, webp, pdf ÙÙ‚Ø·
```

---

# ðŸ“Š Ø®Ø±ÙŠØ·Ø© Ø§Ù„Ø±Ø¨Ø· Ø§Ù„ÙƒØ§Ù…Ù„Ø© (Entity Map)

```
Company
â”œâ”€â”€ User
â”‚   â””â”€â”€ Employee (OneToOne â€” auto Ø¹Ù„Ù‰ ENGINEER/MANAGER/HR/ACCOUNTANT/WAREHOUSE)
â”‚       â”œâ”€â”€ EmployeeAttachment[]  (Cloudinary URLs)
â”‚       â”œâ”€â”€ LeaveRequest[]
â”‚       â””â”€â”€ Attendance[]
â”‚
â”œâ”€â”€ Farm
â”‚   â””â”€â”€ LocationNode (MPTT tree)
â”‚       â”œâ”€â”€ DailyTaskReport[]
â”‚       â”‚   â”œâ”€â”€ LaborEntry[] â†’ Employee? (Ø±Ø¨Ø· Ø§Ø®ØªÙŠØ§Ø±ÙŠ Ø¨Ø§Ù„Ø§Ø³Ù…)
â”‚       â”‚   â””â”€â”€ Attachment[] (Cloudinary)
â”‚       â”œâ”€â”€ FertilizationReport[]
â”‚       â”œâ”€â”€ IrrigationReport[]
â”‚       â””â”€â”€ CropRecord[] (ÙŠÙˆØ­Ø¯ Palm + Olive)
â”‚
â”œâ”€â”€ Operation[]           (Ø¹Ù…Ù„ÙŠØ§Øª ÙÙ†ÙŠØ©)
â”œâ”€â”€ Contractor[]          (Ù…Ù‚Ø§ÙˆÙ„ÙˆÙ† â€” ÙŠØ¸Ù‡Ø±ÙˆØ§ ÙÙŠ LaborEntry)
â”œâ”€â”€ Variety[]             (Ø£ØµÙ†Ø§Ù)
â”œâ”€â”€ Unit[]                (ÙˆØ­Ø¯Ø§Øª)
â”œâ”€â”€ CustomFieldDefinition[] (Ø­Ù‚ÙˆÙ„ Ù…Ø®ØµØµØ© Ù„Ø£ÙŠ ØªÙ‚Ø±ÙŠØ±)
â”‚
â”œâ”€â”€ WarehouseItem[]
â”‚   â””â”€â”€ WarehouseMovement[]
â”‚
â”œâ”€â”€ Equipment[]
â”‚   â””â”€â”€ EquipmentUsageLog[]
â”‚
â”œâ”€â”€ Expense[]
â”œâ”€â”€ Revenue[]
â””â”€â”€ YieldRecord[]
```

---

*Ù‡Ø°Ø§ Ø§Ù„Ù…Ù„Ù Ù‡Ùˆ Ø§Ù„Ù…Ø±Ø¬Ø¹ Ø§Ù„Ø±Ø¦ÙŠØ³ÙŠ Ù„Ù„Ù…Ø´Ø±ÙˆØ¹ â€” ÙƒÙ„ ØªØ¹Ø¯ÙŠÙ„ ÙŠØ¬Ø¨ Ø£Ù† ÙŠØªÙˆØ§ÙÙ‚ Ù…Ø¹ Ù‡Ø°Ù‡ Ø§Ù„Ø®Ø·Ø©*
*Ø¢Ø®Ø± ØªØ­Ø¯ÙŠØ«: Ø¨Ø¹Ø¯ Ù…Ø±Ø§Ø¬Ø¹Ø© Ø§Ù„ÙƒÙˆØ¯ Ø§Ù„ÙƒØ§Ù…Ù„Ø©*

