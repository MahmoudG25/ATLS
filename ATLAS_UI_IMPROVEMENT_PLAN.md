# 🌿 خطة تحسين واجهة المستخدم — Atlas Farm ERP
## شركة أطلس سيوة للتنمية الزراعية

> **تاريخ الخطة**: أبريل 2026  
> **النطاق**: تحسين UI/UX الشامل + تصميم Landing Page + Responsive Design  
> **المستوى**: تفصيلي لنموذج الذكاء الاصطناعي

---

## ⚠️ تعليمات مهمة قبل البدء (اقرأها أولاً)

```
1. لا تكسر أي كود موجود — قم بالتعديل فقط على ما هو مطلوب
2. كل ملف يُذكر اسمه هو الملف الذي يجب تعديله
3. المشروع يستخدم: React + Vite + MUI (Material UI) + Tailwind CSS + RTL (عربي)
4. الألوان الأساسية للمشروع: الأخضر الزراعي #16a34a
5. المشروع يدعم العربية بشكل افتراضي (dir="rtl")
6. لا تحذف أي import موجود إلا إذا استبدلته
7. نفذ كل مهمة بالترتيب من الأعلى للأسفل
```

---

## 📋 فهرس الخطة

| الرقم | المرحلة | الأولوية | الملفات المتأثرة |
|-------|---------|----------|-----------------|
| Phase A | تصحيح Responsive — سطح المكتب | 🔴 حرج | Layout files |
| Phase B | تصحيح Responsive — التابلت | 🟠 عالي | Layout + Pages |
| Phase C | تحسين الهاتف المحمول | 🟠 عالي | All components |
| Phase D | تحسين عام للـ UI | 🟡 متوسط | Global styles |
| Phase E | Landing Page جديدة | 🟢 تسويقي | LandingPage.jsx |

---

---

# ═══════════════════════════════════════════
# PHASE A — تصحيح Responsive: سطح المكتب (Desktop)
# ═══════════════════════════════════════════

## A.1 — تصحيح الـ Sidebar في سطح المكتب

### المشكلة:
الـ Sidebar قد لا يكون بعرض ثابت، مما يتسبب في اضطراب المحتوى الرئيسي.

### الملف المطلوب تعديله:
```
Front-End/src/layouts/DashboardLayout.jsx
```

### ما يجب فعله:
ابحث عن الـ Drawer أو Sidebar واجعل عرضه ثابتاً على سطح المكتب.

**أضف هذه الـ CSS variables في ملف CSS الرئيسي أو بالـ sx prop:**

```css
/* في الملف: Front-End/src/index.css أو App.css */
:root {
  --sidebar-width: 260px;
  --sidebar-collapsed-width: 72px;
  --topbar-height: 64px;
}
```

**عدّل الـ DashboardLayout.jsx لتكون هكذا:**

```jsx
// ابحث عن الـ Box الرئيسي الذي يحتوي Sidebar + المحتوى
// وعدّله ليبدو هكذا:

const drawerWidth = 260; // عرض ثابت للـ Sidebar

// الـ Sidebar (Drawer) يجب أن يكون:
<Drawer
  variant="permanent"  // ← هذا مهم جداً للـ Desktop
  sx={{
    width: drawerWidth,
    flexShrink: 0,
    '& .MuiDrawer-paper': {
      width: drawerWidth,
      boxSizing: 'border-box',
      borderLeft: 'none', // لأن الموقع RTL
      borderRight: '1px solid rgba(0,0,0,0.08)',
    },
    // إخفاء الـ Sidebar في الهاتف
    display: { xs: 'none', md: 'block' },
  }}
>
  {/* محتوى الـ Sidebar */}
</Drawer>

// الـ Box الرئيسي للمحتوى يجب أن يكون:
<Box
  component="main"
  sx={{
    flexGrow: 1,
    width: { md: `calc(100% - ${drawerWidth}px)` },
    minHeight: '100vh',
    mt: `64px`, // ارتفاع الـ Topbar
    overflow: 'auto',
  }}
>
  {/* المحتوى */}
</Box>
```

---

## A.2 — تصحيح الـ Topbar في سطح المكتب

### الملف المطلوب تعديله:
```
Front-End/src/layouts/DashboardTopbar.jsx
```

### ما يجب فعله:
الـ Topbar يجب أن يمتد بشكل صحيح بجانب الـ Sidebar.

```jsx
// ابحث عن AppBar وعدّل الـ sx الخاصة به:
<AppBar
  position="fixed"
  sx={{
    width: { md: `calc(100% - ${drawerWidth}px)` },
    mr: { md: `${drawerWidth}px` }, // RTL: استخدم mr بدلاً من ml
    zIndex: (theme) => theme.zIndex.drawer + 1,
    backgroundColor: '#fff',
    color: '#1a1a1a',
    boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
  }}
>
```

---

## A.3 — تصحيح الـ DataGrid / Tables في سطح المكتب

### المشكلة:
الجداول قد تتجاوز حدود الـ container أو تكون ضيقة جداً.

### الملف المطلوب تعديله:
```
أي صفحة تحتوي على جدول — ابحث في Front-End/src/pages/
```

### ما يجب فعله:
ضع الـ Table داخل container بهذه الخصائص:

```jsx
// اللف الخارجي للجدول
<Box
  sx={{
    width: '100%',
    overflowX: 'auto', // مهم جداً لمنع overflow
    borderRadius: 2,
    boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
  }}
>
  {/* الجدول هنا */}
</Box>
```

---

## A.4 — تصحيح الـ Grid Layout في الصفحات

### المشكلة:
بعض الصفحات تستخدم Grid لكن العمود قد يكون بعرض خاطئ على سطح المكتب.

### ما يجب فعله:
في كل صفحة تستخدم `<Grid container>`, تأكد من أن الأعمدة صحيحة:

```jsx
// ✅ صح — يستجيب للشاشات
<Grid container spacing={3}>
  <Grid item xs={12} sm={6} md={4} lg={3}>
    {/* بطاقة */}
  </Grid>
</Grid>

// ❌ خطأ — ثابت على كل الشاشات
<Grid item xs={12}>
  {/* هذا دائماً بعرض كامل، لا يستفيد من سطح المكتب */}
</Grid>
```

**القاعدة:**
- `xs={12}` → الهاتف: عمود كامل
- `sm={6}` → التابلت: نصفين
- `md={4}` → لابتوب: ثلاثة أعمدة
- `lg={3}` → شاشة كبيرة: أربعة أعمدة

---

---

# ═══════════════════════════════════════════
# PHASE B — تصحيح Responsive: التابلت (Tablet: 768px - 1024px)
# ═══════════════════════════════════════════

## B.1 — الـ Sidebar في وضع التابلت

### المشكلة:
على التابلت، الـ Sidebar يجب أن يكون قابلاً للطي (collapsible) أو يتحول لـ Drawer مؤقت.

### الملف المطلوب تعديله:
```
Front-End/src/layouts/DashboardLayout.jsx
```

### ما يجب فعله:
أضف state للتحكم في فتح/إغلاق الـ Sidebar على التابلت:

```jsx
import { useState } from 'react';
import { useMediaQuery, useTheme } from '@mui/material';

// داخل الـ Component:
const theme = useTheme();
const isTablet = useMediaQuery(theme.breakpoints.between('sm', 'md'));
const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
const [mobileOpen, setMobileOpen] = useState(false);

const handleDrawerToggle = () => {
  setMobileOpen(!mobileOpen);
};

// الـ Sidebar يكون Drawer مؤقت على التابلت والهاتف:
<>
  {/* Drawer مؤقت للموبايل والتابلت */}
  <Drawer
    variant="temporary"
    open={mobileOpen}
    onClose={handleDrawerToggle}
    ModalProps={{ keepMounted: true }} // تحسين الأداء على الموبايل
    sx={{
      display: { xs: 'block', md: 'none' }, // يظهر فقط للهاتف والتابلت
      '& .MuiDrawer-paper': {
        boxSizing: 'border-box',
        width: 260,
      },
    }}
  >
    {sidebarContent}
  </Drawer>

  {/* Drawer دائم لسطح المكتب */}
  <Drawer
    variant="permanent"
    sx={{
      display: { xs: 'none', md: 'block' }, // يظهر فقط لسطح المكتب
      '& .MuiDrawer-paper': {
        boxSizing: 'border-box',
        width: 260,
      },
    }}
    open
  >
    {sidebarContent}
  </Drawer>
</>
```

---

## B.2 — زر فتح الـ Sidebar (Hamburger) على التابلت

### الملف المطلوب تعديله:
```
Front-End/src/layouts/DashboardTopbar.jsx
```

### ما يجب فعله:
أضف زر Hamburger يظهر فقط على التابلت والهاتف:

```jsx
import MenuIcon from '@mui/icons-material/Menu';

// داخل الـ Toolbar:
<IconButton
  color="inherit"
  aria-label="open drawer"
  edge="start"
  onClick={onMenuClick} // هذه الـ prop تأتي من DashboardLayout
  sx={{ 
    mr: 2,
    display: { md: 'none' }, // يختفي على سطح المكتب
  }}
>
  <MenuIcon />
</IconButton>
```

---

## B.3 — الـ Cards على التابلت

### المشكلة:
البطاقات (Cards) على التابلت قد تكون إما كبيرة جداً أو صغيرة جداً.

### الملف المطلوب تعديله:
```
أي صفحة تحتوي على Cards — خاصةً Dashboard
```

### ما يجب فعله:

```jsx
// بطاقات الإحصائيات في الـ Dashboard
<Grid container spacing={2}>
  <Grid item xs={12} sm={6} md={6} lg={3}>
    <StatCard title="إجمالي المبيعات" value="250,000 جنيه" />
  </Grid>
  <Grid item xs={12} sm={6} md={6} lg={3}>
    <StatCard title="المخزون المتاح" value="1,200 وحدة" />
  </Grid>
  {/* ... */}
</Grid>
```

---

## B.4 — الـ Typography على التابلت

### ما يجب فعله:
أضف هذا الـ CSS في ملف `index.css`:

```css
/* حجم الخط يتكيف مع الشاشة */
@media (max-width: 1024px) {
  .MuiTypography-h4 { font-size: 1.4rem !important; }
  .MuiTypography-h5 { font-size: 1.2rem !important; }
  .MuiTypography-h6 { font-size: 1.1rem !important; }
}
```

---

---

# ═══════════════════════════════════════════
# PHASE C — تحسين الهاتف المحمول (Mobile: < 768px)
# ═══════════════════════════════════════════

## C.1 — Bottom Navigation للهاتف

### المشكلة:
الـ Sidebar يختفي على الهاتف ولا يوجد بديل سهل للتنقل.

### ملف جديد يجب إنشاؤه:
```
Front-End/src/components/BottomNav.jsx
```

### الكود الكامل للملف الجديد:

```jsx
// Front-End/src/components/BottomNav.jsx
import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  BottomNavigation, 
  BottomNavigationAction, 
  Paper,
  useMediaQuery,
  useTheme 
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import InventoryIcon from '@mui/icons-material/Inventory';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import PeopleIcon from '@mui/icons-material/People';
import MoreHorizIcon from '@mui/icons-material/MoreHoriz';

export default function BottomNav() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const navigate = useNavigate();
  const location = useLocation();

  // لا تعرض الـ BottomNav إلا على الهاتف
  if (!isMobile) return null;

  // تحديد الـ tab النشط بناءً على الرابط الحالي
  const getActiveTab = () => {
    const path = location.pathname;
    if (path.includes('/inventory')) return 1;
    if (path.includes('/accounting')) return 2;
    if (path.includes('/hr')) return 3;
    if (path.includes('/admin') || path.includes('/profile')) return 4;
    return 0; // Dashboard
  };

  return (
    <Paper
      sx={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        zIndex: 1300,
        display: { sm: 'none' }, // فقط على الهاتف
        borderTop: '1px solid rgba(0,0,0,0.08)',
      }}
      elevation={3}
    >
      <BottomNavigation
        value={getActiveTab()}
        sx={{ bgcolor: '#fff' }}
      >
        <BottomNavigationAction
          label="الرئيسية"
          icon={<HomeIcon />}
          onClick={() => navigate('/dashboard')}
          sx={{ '&.Mui-selected': { color: '#16a34a' } }}
        />
        <BottomNavigationAction
          label="المخزون"
          icon={<InventoryIcon />}
          onClick={() => navigate('/inventory')}
          sx={{ '&.Mui-selected': { color: '#16a34a' } }}
        />
        <BottomNavigationAction
          label="المحاسبة"
          icon={<AccountBalanceIcon />}
          onClick={() => navigate('/accounting')}
          sx={{ '&.Mui-selected': { color: '#16a34a' } }}
        />
        <BottomNavigationAction
          label="الموارد"
          icon={<PeopleIcon />}
          onClick={() => navigate('/hr')}
          sx={{ '&.Mui-selected': { color: '#16a34a' } }}
        />
        <BottomNavigationAction
          label="المزيد"
          icon={<MoreHorizIcon />}
          onClick={() => navigate('/profile')}
          sx={{ '&.Mui-selected': { color: '#16a34a' } }}
        />
      </BottomNavigation>
    </Paper>
  );
}
```

### بعد إنشاء الملف، أضف الـ BottomNav في:
```
Front-End/src/layouts/DashboardLayout.jsx
```

```jsx
// أضف هذا الـ import في الأعلى:
import BottomNav from '../components/BottomNav';

// أضف الـ BottomNav قبل آخر </Box> في الـ return:
<BottomNav />

// وأضف padding أسفل المحتوى الرئيسي على الهاتف:
<Box
  component="main"
  sx={{
    flexGrow: 1,
    // ... باقي الـ sx
    pb: { xs: 8, md: 0 }, // مسافة سفلية للهاتف بسبب BottomNav
  }}
>
```

---

## C.2 — تصحيح الـ Tables على الهاتف

### المشكلة:
الجداول الكبيرة لا تعرض بشكل صحيح على الهاتف.

### ما يجب فعله في كل صفحة تحتوي جدول:

```jsx
// أضف هذا المكون لعرض البيانات بطريقة بطاقات على الهاتف
// وجدول على سطح المكتب:

import { useMediaQuery, useTheme } from '@mui/material';

function DataDisplay({ data }) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  if (isMobile) {
    // عرض بطاقات على الهاتف
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {data.map((item) => (
          <Card key={item.id} sx={{ p: 2 }}>
            <Typography variant="subtitle1" fontWeight="bold">
              {item.name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {item.details}
            </Typography>
            {/* الأزرار */}
            <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
              <Button size="small" variant="outlined">تعديل</Button>
              <Button size="small" variant="outlined" color="error">حذف</Button>
            </Box>
          </Card>
        ))}
      </Box>
    );
  }

  // عرض جدول على سطح المكتب (الكود الحالي)
  return (
    <TableContainer>
      <Table>
        {/* ... */}
      </Table>
    </TableContainer>
  );
}
```

---

## C.3 — تصحيح الـ Forms على الهاتف

### المشكلة:
النماذج (Forms) قد تكون ضيقة جداً على الهاتف.

### ما يجب فعله:

```jsx
// في كل نموذج (Form) أو Dialog:
<Dialog
  fullWidth
  maxWidth="sm"
  // أضف هذا:
  fullScreen={useMediaQuery(useTheme().breakpoints.down('sm'))} // كامل الشاشة على الهاتف
>
  <DialogTitle>
    {/* أضف زر إغلاق واضح */}
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <Typography variant="h6">عنوان النموذج</Typography>
      <IconButton onClick={onClose}>
        <CloseIcon />
      </IconButton>
    </Box>
  </DialogTitle>
  <DialogContent>
    {/* المحتوى */}
  </DialogContent>
</Dialog>
```

---

## C.4 — تصحيح الـ Topbar على الهاتف

### الملف المطلوب تعديله:
```
Front-End/src/layouts/DashboardTopbar.jsx
```

### ما يجب فعله:
اجعل الـ Topbar أبسط على الهاتف وأخفِ بعض العناصر:

```jsx
// أخفِ بعض عناصر الـ Topbar على الهاتف:
<Typography
  variant="h6"
  sx={{ 
    display: { xs: 'none', sm: 'block' }, // أخفِ عنوان الصفحة على الهاتف
    flexGrow: 1 
  }}
>
  اسم الصفحة
</Typography>

// اجعل الـ Toolbar أصغر على الهاتف:
<Toolbar
  sx={{
    minHeight: { xs: '56px', sm: '64px' },
    px: { xs: 1, sm: 2 },
  }}
>
```

---

## C.5 — Font Size مناسب للهاتف

### الملف المطلوب تعديله:
```
Front-End/src/index.css  أو  Front-End/src/App.css
```

### ما يجب إضافته:

```css
/* تحسينات الهاتف العامة */
@media (max-width: 600px) {
  /* منع التكبير التلقائي للـ input على iOS */
  input, select, textarea {
    font-size: 16px !important;
  }
  
  /* تصغير العناوين */
  .MuiTypography-h4 { font-size: 1.3rem !important; }
  .MuiTypography-h5 { font-size: 1.15rem !important; }
  
  /* تحسين الأزرار */
  .MuiButton-root {
    min-height: 44px; /* Apple's minimum touch target */
  }
  
  /* تحسين الـ padding */
  .MuiCardContent-root {
    padding: 12px !important;
  }
}
```

---

---

# ═══════════════════════════════════════════
# PHASE D — تحسينات UI عامة
# ═══════════════════════════════════════════

## D.1 — نظام ألوان موحد

### الملف المطلوب تعديله أو إنشاؤه:
```
Front-End/src/theme/theme.js  (إذا لم يكن موجوداً، أنشئه)
```

```js
// Front-End/src/theme/theme.js
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  direction: 'rtl', // مهم جداً للغة العربية
  palette: {
    primary: {
      main: '#16a34a',       // الأخضر الزراعي
      light: '#4ade80',      // أخضر فاتح
      dark: '#15803d',       // أخضر داكن
      contrastText: '#fff',
    },
    secondary: {
      main: '#78350f',       // بني تمر
      light: '#b45309',
      dark: '#451a03',
    },
    success: { main: '#16a34a' },
    warning: { main: '#d97706' },
    error: { main: '#dc2626' },
    background: {
      default: '#f8fafc',    // خلفية رمادية ناعمة
      paper: '#ffffff',
    },
    text: {
      primary: '#1e293b',
      secondary: '#64748b',
    },
  },
  typography: {
    fontFamily: '"Cairo", "Segoe UI", sans-serif', // خط عربي احترافي
    h1: { fontWeight: 700 },
    h2: { fontWeight: 700 },
    h3: { fontWeight: 600 },
    h4: { fontWeight: 600 },
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
  },
  shape: {
    borderRadius: 10, // حواف مستديرة معتدلة
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none', // إيقاف الـ UPPERCASE
          fontWeight: 600,
          borderRadius: 8,
          minHeight: 44,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)',
        },
      },
    },
    MuiTextField: {
      defaultProps: {
        variant: 'outlined',
        fullWidth: true,
      },
    },
  },
});

export default theme;
```

### كيفية استخدام الـ Theme:
```
Front-End/src/main.jsx  أو  Front-End/src/App.jsx
```

```jsx
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from './theme/theme';

// في الـ return:
<ThemeProvider theme={theme}>
  <CssBaseline />
  {/* باقي التطبيق */}
</ThemeProvider>
```

---

## D.2 — تحسين الـ Loading States

### ملف جديد يجب إنشاؤه:
```
Front-End/src/components/LoadingSpinner.jsx
```

```jsx
// Front-End/src/components/LoadingSpinner.jsx
import { Box, CircularProgress, Typography } from '@mui/material';

export default function LoadingSpinner({ message = 'جاري التحميل...' }) {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '300px',
        gap: 2,
      }}
    >
      <CircularProgress sx={{ color: '#16a34a' }} size={48} />
      <Typography color="text.secondary">{message}</Typography>
    </Box>
  );
}

// استخدام الـ Skeleton للتحميل:
export function TableSkeleton({ rows = 5, cols = 4 }) {
  return (
    <Box>
      {[...Array(rows)].map((_, i) => (
        <Box key={i} sx={{ display: 'flex', gap: 2, mb: 1 }}>
          {[...Array(cols)].map((_, j) => (
            <Skeleton key={j} variant="rectangular" height={40} sx={{ flexGrow: 1 }} />
          ))}
        </Box>
      ))}
    </Box>
  );
}
```

---

## D.3 — تحسين الـ Empty States

### ملف جديد يجب إنشاؤه:
```
Front-End/src/components/EmptyState.jsx
```

```jsx
// Front-End/src/components/EmptyState.jsx
import { Box, Typography, Button } from '@mui/material';
import InboxIcon from '@mui/icons-material/Inbox';

export default function EmptyState({ 
  title = 'لا توجد بيانات',
  description = 'لم يتم العثور على أي نتائج',
  actionText,
  onAction,
  icon: Icon = InboxIcon
}) {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        py: 8,
        gap: 2,
        color: 'text.secondary',
      }}
    >
      <Icon sx={{ fontSize: 64, opacity: 0.3 }} />
      <Typography variant="h6" fontWeight={600} color="text.primary">
        {title}
      </Typography>
      <Typography variant="body2" textAlign="center" maxWidth={300}>
        {description}
      </Typography>
      {actionText && onAction && (
        <Button
          variant="contained"
          onClick={onAction}
          sx={{ mt: 1, bgcolor: '#16a34a' }}
        >
          {actionText}
        </Button>
      )}
    </Box>
  );
}
```

---

---

# ═══════════════════════════════════════════
# PHASE E — Landing Page الجديدة
# ═══════════════════════════════════════════

## معلومات الشركة (استخدمها في الصفحة)

```
الاسم الكامل: شركة أطلس سيوة للتنمية الزراعية (ش.م.م)
الشركة الأم: شركة أطلس للاستثمار والصناعات الغذائية
التأسيس: 2006
التسجيل: مقيدة بالبورصة المصرية (تابعة للشركة الأم المقيدة منذ 1997)
الموقع: الكيلو 43 طريق مصر-الإسكندرية الصحراوي، الشيخ زايد، الجيزة
المزارع: واحة سيوة، الصحراء الغربية، مصر
القطاعات:
  - نخيل المجدول (مشروع نخلاتي) — 370 فدان عبر 7 مواسم
  - أشجار الزيتون
  - أشجار الباولونيا (البولونيا)
  - البرسيم المصري
  - محاصيل أخرى
الرؤية: إنتاج تمور المجدول بمعايير عالمية للتصدير
السوق المستهدف: أوروبا وأمريكا (طلب عالمي يفوق العرض بكثير)
```

---

## E.1 — إنشاء Landing Page كاملة

### الملف المطلوب إنشاؤه أو تعديله:
```
Front-End/src/pages/LandingPage.jsx
```

### الكود الكامل للـ Landing Page:

```jsx
// Front-End/src/pages/LandingPage.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Container, Typography, Button, Grid, Card, CardContent,
  Chip, Stack, Divider, useMediaQuery, useTheme, AppBar,
  Toolbar, IconButton, Drawer, List, ListItem, ListItemText,
  Avatar
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import AgricultureIcon from '@mui/icons-material/Agriculture';
import ForestIcon from '@mui/icons-material/Forest';
import GrassIcon from '@mui/icons-material/Grass';
import LocalFloristIcon from '@mui/icons-material/LocalFlorist';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import PublicIcon from '@mui/icons-material/Public';
import VerifiedIcon from '@mui/icons-material/Verified';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import BusinessIcon from '@mui/icons-material/Business';
import CloseIcon from '@mui/icons-material/Close';

// ═══════════════════════════════
// بيانات الأقسام والإحصائيات
// ═══════════════════════════════

const COMPANY_STATS = [
  { value: '370+', label: 'فدان مجدول مزروع', icon: AgricultureIcon },
  { value: '7', label: 'مواسم إنتاجية ناجحة', icon: TrendingUpIcon },
  { value: '2006', label: 'عام التأسيس', icon: BusinessIcon },
  { value: '200+', label: 'مزرعة حاصلة على شهادة عضوية', icon: VerifiedIcon },
];

const SECTORS = [
  {
    id: 1,
    title: 'نخيل المجدول',
    subtitle: 'مشروع نخلاتي',
    description:
      'نزرع أجود أنواع تمر المجدول في واحة سيوة الفريدة. المجدول هو "ملك التمور" ويحظى بطلب متزايد في أوروبا وأمريكا. إنتاجنا مطابق لأعلى معايير الجودة العالمية ومؤهل للتصدير.',
    color: '#16a34a',
    bgColor: '#f0fdf4',
    icon: AgricultureIcon,
    features: ['تمر مجدول عضوي معتمد', 'مؤهل للتصدير لأوروبا وأمريكا', 'إنتاج 370+ فدان'],
    tag: 'المنتج الرئيسي',
  },
  {
    id: 2,
    title: 'أشجار الزيتون',
    subtitle: 'زيتون سيوة العضوي',
    description:
      'يُعدّ الزيتون من أشهر محاصيل واحة سيوة تاريخياً. نزرع أصناف متميزة في المناخ الصحراوي الجاف المثالي لإنتاج زيت زيتون عالي الجودة وثمار الزيتون الطبيعية.',
    color: '#78350f',
    bgColor: '#fef3c7',
    icon: ForestIcon,
    features: ['زيت زيتون بكر ممتاز', 'مناخ صحراوي مثالي', 'تراث سيوة الزراعي'],
    tag: 'قطاع راسخ',
  },
  {
    id: 3,
    title: 'أشجار الباولونيا',
    subtitle: 'الشجرة الاقتصادية المعجزة',
    description:
      'شجرة الباولونيا من أسرع الأشجار نمواً في العالم، وتُستخدم في صناعة الأخشاب والورق والعلف. تُعدّ استثماراً زراعياً مجزياً بعوائد مرتفعة في وقت قصير.',
    color: '#1d4ed8',
    bgColor: '#eff6ff',
    icon: GrassIcon,
    features: ['أسرع نمو شجري في العالم', 'متعددة الاستخدامات', 'عوائد استثمارية مرتفعة'],
    tag: 'قطاع واعد',
  },
  {
    id: 4,
    title: 'البرسيم المصري',
    subtitle: 'علف طبيعي عالي الجودة',
    description:
      'ننتج البرسيم المصري (Berseem Clover) الشهير عالمياً كأفضل علف طبيعي للماشية. يُعزز الإنتاج الحيواني ويُحسّن خصوبة التربة ويُقلل الاحتياج للأسمدة الكيميائية.',
    color: '#15803d',
    bgColor: '#dcfce7',
    icon: LocalFloristIcon,
    features: ['أعلى قيمة غذائية للثروة الحيوانية', 'يُحسن خصوبة التربة', 'طلب تصديري مرتفع'],
    tag: 'قطاع داعم',
  },
];

const ERP_MODULES = [
  { name: 'المخزون', desc: 'تتبع المنتجات والمواد الخام لحظةً بلحظة', icon: '📦' },
  { name: 'المحاسبة', desc: 'فواتير ومصروفات وتقارير مالية شاملة', icon: '💰' },
  { name: 'الموارد البشرية', desc: 'إدارة الموظفين والحضور والرواتب', icon: '👥' },
  { name: 'الإشعارات', desc: 'تنبيهات فورية للمخزون والمهام', icon: '🔔' },
  { name: 'التقارير', desc: 'رسوم بيانية وتحليلات متقدمة', icon: '📊' },
  { name: 'إدارة المستخدمين', desc: 'صلاحيات وأدوار محكمة الأمان', icon: '🔐' },
];

// ═══════════════════════════════
// مكوّن الـ Navbar
// ═══════════════════════════════

function LandingNavbar({ onLogin }) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [drawerOpen, setDrawerOpen] = useState(false);

  const navLinks = [
    { label: 'من نحن', href: '#about' },
    { label: 'قطاعاتنا', href: '#sectors' },
    { label: 'النظام', href: '#erp' },
    { label: 'تواصل معنا', href: '#contact' },
  ];

  const scrollTo = (id) => {
    document.querySelector(id)?.scrollIntoView({ behavior: 'smooth' });
    setDrawerOpen(false);
  };

  return (
    <>
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          bgcolor: 'rgba(255,255,255,0.95)',
          backdropFilter: 'blur(8px)',
          borderBottom: '1px solid rgba(0,0,0,0.06)',
          color: '#1e293b',
        }}
      >
        <Toolbar sx={{ justifyContent: 'space-between', px: { xs: 2, md: 4 } }}>
          {/* الشعار */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box
              sx={{
                width: 40, height: 40, borderRadius: '50%',
                bgcolor: '#16a34a', display: 'flex',
                alignItems: 'center', justifyContent: 'center',
              }}
            >
              <AgricultureIcon sx={{ color: '#fff', fontSize: 22 }} />
            </Box>
            <Box>
              <Typography variant="subtitle1" fontWeight={700} lineHeight={1.2}>
                أطلس سيوة
              </Typography>
              <Typography variant="caption" color="text.secondary" lineHeight={1}>
                للتنمية الزراعية
              </Typography>
            </Box>
          </Box>

          {/* روابط سطح المكتب */}
          {!isMobile && (
            <Stack direction="row" spacing={3}>
              {navLinks.map((link) => (
                <Button
                  key={link.label}
                  onClick={() => scrollTo(link.href)}
                  sx={{ color: '#1e293b', fontWeight: 500 }}
                >
                  {link.label}
                </Button>
              ))}
            </Stack>
          )}

          {/* زر الدخول */}
          <Box sx={{ display: 'flex', gap: 1 }}>
            {isMobile ? (
              <IconButton onClick={() => setDrawerOpen(true)}>
                <MenuIcon />
              </IconButton>
            ) : (
              <Button
                variant="contained"
                onClick={onLogin}
                sx={{ bgcolor: '#16a34a', '&:hover': { bgcolor: '#15803d' } }}
              >
                دخول النظام
              </Button>
            )}
          </Box>
        </Toolbar>
      </AppBar>

      {/* Drawer للموبايل */}
      <Drawer anchor="right" open={drawerOpen} onClose={() => setDrawerOpen(false)}>
        <Box sx={{ width: 280, p: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" fontWeight={700}>القائمة</Typography>
            <IconButton onClick={() => setDrawerOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
          <Divider sx={{ mb: 2 }} />
          <List>
            {navLinks.map((link) => (
              <ListItem
                key={link.label}
                button
                onClick={() => scrollTo(link.href)}
                sx={{ borderRadius: 2, mb: 0.5 }}
              >
                <ListItemText primary={link.label} />
              </ListItem>
            ))}
          </List>
          <Button
            fullWidth
            variant="contained"
            onClick={() => { onLogin(); setDrawerOpen(false); }}
            sx={{ mt: 2, bgcolor: '#16a34a', py: 1.5 }}
          >
            دخول النظام
          </Button>
        </Box>
      </Drawer>
    </>
  );
}

// ═══════════════════════════════
// الـ Component الرئيسي للـ Landing Page
// ═══════════════════════════════

export default function LandingPage() {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const handleLogin = () => navigate('/login');

  return (
    <Box sx={{ bgcolor: '#f8fafc', direction: 'rtl', overflowX: 'hidden' }}>
      {/* ── الـ Navbar ─────────────────────── */}
      <LandingNavbar onLogin={handleLogin} />

      {/* ── قسم Hero ───────────────────────── */}
      <Box
        sx={{
          minHeight: '100vh',
          background: 'linear-gradient(135deg, #052e16 0%, #14532d 40%, #15803d 100%)',
          display: 'flex',
          alignItems: 'center',
          position: 'relative',
          overflow: 'hidden',
          pt: 8, // مسافة للـ Navbar
        }}
      >
        {/* خلفية ديكورية */}
        <Box
          sx={{
            position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
            backgroundImage: 'radial-gradient(circle at 20% 80%, rgba(255,255,255,0.03) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(255,255,255,0.05) 0%, transparent 50%)',
          }}
        />

        <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1, py: { xs: 8, md: 4 } }}>
          <Grid container spacing={6} alignItems="center">
            <Grid item xs={12} md={7}>
              {/* شارة */}
              <Chip
                label="🌿 مقيدة بالبورصة المصرية"
                sx={{ bgcolor: 'rgba(255,255,255,0.15)', color: '#fff', mb: 3, fontWeight: 600 }}
              />

              <Typography
                variant={isMobile ? 'h3' : 'h2'}
                fontWeight={800}
                color="#fff"
                lineHeight={1.2}
                sx={{ mb: 2 }}
              >
                أطلس سيوة
                <Box component="span" sx={{ color: '#4ade80', display: 'block' }}>
                  للتنمية الزراعية
                </Box>
              </Typography>

              <Typography
                variant="h6"
                sx={{ color: 'rgba(255,255,255,0.8)', mb: 1, fontWeight: 400 }}
              >
                من قلب واحة سيوة — أرض النخيل والزيتون
              </Typography>

              <Typography
                variant="body1"
                sx={{ color: 'rgba(255,255,255,0.65)', mb: 4, maxWidth: 500, lineHeight: 1.8 }}
              >
                شركة رائدة في الزراعة المستدامة منذ 2006، نزرع تمر المجدول والزيتون والباولونيا
                في واحة سيوة الفريدة — إنتاج يطابق المعايير الدولية ويصل إلى أسواق أوروبا وأمريكا.
              </Typography>

              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                <Button
                  variant="contained"
                  size="large"
                  onClick={handleLogin}
                  sx={{
                    bgcolor: '#4ade80', color: '#052e16', fontWeight: 700,
                    px: 4, py: 1.5, fontSize: '1rem',
                    '&:hover': { bgcolor: '#22c55e' },
                  }}
                >
                  دخول نظام ERP
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  onClick={() => document.querySelector('#about')?.scrollIntoView({ behavior: 'smooth' })}
                  sx={{
                    borderColor: 'rgba(255,255,255,0.4)', color: '#fff',
                    px: 4, py: 1.5, fontSize: '1rem',
                    '&:hover': { borderColor: '#fff', bgcolor: 'rgba(255,255,255,0.1)' },
                  }}
                >
                  تعرف علينا
                </Button>
              </Stack>
            </Grid>

            {/* إحصائيات */}
            <Grid item xs={12} md={5}>
              <Grid container spacing={2}>
                {COMPANY_STATS.map((stat) => (
                  <Grid item xs={6} key={stat.label}>
                    <Card
                      sx={{
                        bgcolor: 'rgba(255,255,255,0.1)',
                        backdropFilter: 'blur(8px)',
                        border: '1px solid rgba(255,255,255,0.15)',
                        textAlign: 'center',
                        p: 2,
                      }}
                    >
                      <stat.icon sx={{ color: '#4ade80', fontSize: 32, mb: 1 }} />
                      <Typography variant="h4" fontWeight={800} color="#fff">
                        {stat.value}
                      </Typography>
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                        {stat.label}
                      </Typography>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* ── قسم "من نحن" ────────────────────── */}
      <Box id="about" sx={{ py: { xs: 8, md: 12 }, bgcolor: '#fff' }}>
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', mb: 6 }}>
            <Chip label="من نحن" sx={{ bgcolor: '#f0fdf4', color: '#16a34a', fontWeight: 700, mb: 2 }} />
            <Typography variant={isMobile ? 'h4' : 'h3'} fontWeight={800} gutterBottom>
              قصة أطلس سيوة
            </Typography>
            <Typography variant="body1" color="text.secondary" maxWidth={600} mx="auto">
              رحلة من الرؤية إلى الواقع — من واحة سيوة إلى الأسواق العالمية
            </Typography>
          </Box>

          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Box sx={{ p: 4, bgcolor: '#f0fdf4', borderRadius: 4 }}>
                <Typography variant="h5" fontWeight={700} color="#16a34a" gutterBottom>
                  🌴 واحة سيوة — قلب المشروع
                </Typography>
                <Typography variant="body1" color="text.secondary" lineHeight={2} paragraph>
                  تقع واحة سيوة في قلب الصحراء الغربية المصرية على بعد 830 كم من القاهرة.
                  اسمها مشتق من "سيخت-آم" بالمصرية القديمة، وتعني <strong>"أرض النخيل"</strong>.
                  مناخها الصحراوي الجاف هو البيئة المثالية لزراعة النخيل والزيتون.
                </Typography>
                <Typography variant="body1" color="text.secondary" lineHeight={2}>
                  اختار خبراؤنا سيوة لأنها تجمع بين المناخ المثالي والمياه الجوفية الوفيرة،
                  ما يجعلها أرضاً خصبة لإنتاج يطابق أعلى المعايير الدولية.
                </Typography>
              </Box>
            </Grid>

            <Grid item xs={12} md={6}>
              <Stack spacing={3}>
                {[
                  {
                    title: '2006 — التأسيس',
                    desc: 'تأسست شركة أطلس سيوة كشركة تابعة لأطلس للاستثمار والصناعات الغذائية المقيدة بالبورصة المصرية.',
                    color: '#16a34a',
                  },
                  {
                    title: 'الرؤية — التصدير العالمي',
                    desc: 'رصد خبراؤنا فجوة ضخمة بين الطلب العالمي على المجدول وإنتاجه (0.5% فقط من إجمالي التمور)، فانطلقنا لملئها.',
                    color: '#d97706',
                  },
                  {
                    title: 'الإنجاز — 370 فداناً',
                    desc: 'وصلنا إلى 370 فداناً مزروعة بتمر المجدول عبر 7 مواسم، مع شهادات عضوية معتمدة دولياً.',
                    color: '#1d4ed8',
                  },
                ].map((item) => (
                  <Box key={item.title} sx={{ display: 'flex', gap: 2 }}>
                    <Box
                      sx={{
                        width: 4, borderRadius: 2,
                        bgcolor: item.color, flexShrink: 0,
                      }}
                    />
                    <Box>
                      <Typography variant="subtitle1" fontWeight={700}>{item.title}</Typography>
                      <Typography variant="body2" color="text.secondary">{item.desc}</Typography>
                    </Box>
                  </Box>
                ))}
              </Stack>
            </Grid>
          </Grid>

          {/* الموقع والمعلومات */}
          <Box
            sx={{
              mt: 6, p: 3, bgcolor: '#f8fafc',
              borderRadius: 3, border: '1px solid #e2e8f0',
              display: 'flex', flexWrap: 'wrap', gap: 3,
              justifyContent: 'center',
            }}
          >
            {[
              { icon: <LocationOnIcon />, label: 'المقر الرئيسي', value: 'كم 43 طريق مصر-إسكندرية الصحراوي، الشيخ زايد' },
              { icon: <PublicIcon />, label: 'المزارع', value: 'واحة سيوة، الصحراء الغربية، مصر' },
              { icon: <BusinessIcon />, label: 'القيد', value: 'البورصة المصرية (شركة تابعة)' },
            ].map((item) => (
              <Box key={item.label} sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                <Box sx={{ color: '#16a34a' }}>{item.icon}</Box>
                <Box>
                  <Typography variant="caption" color="text.secondary">{item.label}</Typography>
                  <Typography variant="body2" fontWeight={600}>{item.value}</Typography>
                </Box>
              </Box>
            ))}
          </Box>
        </Container>
      </Box>

      {/* ── قسم القطاعات ────────────────────── */}
      <Box id="sectors" sx={{ py: { xs: 8, md: 12 }, bgcolor: '#f8fafc' }}>
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', mb: 6 }}>
            <Chip label="قطاعاتنا" sx={{ bgcolor: '#f0fdf4', color: '#16a34a', fontWeight: 700, mb: 2 }} />
            <Typography variant={isMobile ? 'h4' : 'h3'} fontWeight={800} gutterBottom>
              محاصيلنا وقطاعاتنا الزراعية
            </Typography>
            <Typography variant="body1" color="text.secondary" maxWidth={500} mx="auto">
              تنوع زراعي متكامل في بيئة سيوة الفريدة
            </Typography>
          </Box>

          <Grid container spacing={3}>
            {SECTORS.map((sector) => (
              <Grid item xs={12} sm={6} key={sector.id}>
                <Card
                  sx={{
                    height: '100%',
                    borderRadius: 4,
                    border: `2px solid ${sector.color}20`,
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: `0 12px 30px ${sector.color}20`,
                    },
                  }}
                >
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Box
                        sx={{
                          width: 52, height: 52, borderRadius: 2,
                          bgcolor: sector.bgColor, display: 'flex',
                          alignItems: 'center', justifyContent: 'center',
                        }}
                      >
                        <sector.icon sx={{ color: sector.color, fontSize: 28 }} />
                      </Box>
                      <Chip
                        label={sector.tag}
                        size="small"
                        sx={{ bgcolor: sector.bgColor, color: sector.color, fontWeight: 600 }}
                      />
                    </Box>

                    <Typography variant="h6" fontWeight={700} gutterBottom>
                      {sector.title}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                      {sector.subtitle}
                    </Typography>

                    <Divider sx={{ my: 2 }} />

                    <Typography variant="body2" color="text.secondary" lineHeight={1.8} paragraph>
                      {sector.description}
                    </Typography>

                    <Stack spacing={0.5}>
                      {sector.features.map((feature) => (
                        <Box key={feature} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <VerifiedIcon sx={{ color: sector.color, fontSize: 16 }} />
                          <Typography variant="body2" fontWeight={500}>
                            {feature}
                          </Typography>
                        </Box>
                      ))}
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* ── قسم نظام ERP ─────────────────────── */}
      <Box id="erp" sx={{ py: { xs: 8, md: 12 }, bgcolor: '#fff' }}>
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', mb: 6 }}>
            <Chip label="النظام الإداري" sx={{ bgcolor: '#f0fdf4', color: '#16a34a', fontWeight: 700, mb: 2 }} />
            <Typography variant={isMobile ? 'h4' : 'h3'} fontWeight={800} gutterBottom>
              نظام ERP المتكامل
            </Typography>
            <Typography variant="body1" color="text.secondary" maxWidth={500} mx="auto">
              إدارة شاملة لكل عمليات الشركة من مكان واحد
            </Typography>
          </Box>

          <Grid container spacing={3} sx={{ mb: 6 }}>
            {ERP_MODULES.map((mod) => (
              <Grid item xs={12} sm={6} md={4} key={mod.name}>
                <Card
                  sx={{
                    p: 3, borderRadius: 3, border: '1px solid #e2e8f0',
                    transition: 'all 0.2s',
                    '&:hover': { borderColor: '#16a34a', boxShadow: '0 4px 12px rgba(22,163,74,0.1)' },
                  }}
                >
                  <Typography variant="h2" sx={{ mb: 1 }}>{mod.icon}</Typography>
                  <Typography variant="h6" fontWeight={700} gutterBottom>{mod.name}</Typography>
                  <Typography variant="body2" color="text.secondary">{mod.desc}</Typography>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* CTA */}
          <Box
            sx={{
              p: { xs: 4, md: 6 },
              borderRadius: 4,
              background: 'linear-gradient(135deg, #052e16, #15803d)',
              textAlign: 'center',
            }}
          >
            <Typography variant="h4" fontWeight={800} color="#fff" gutterBottom>
              ابدأ إدارة مزارعك الآن
            </Typography>
            <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.8)', mb: 4 }}>
              نظام ERP مصمم خصيصاً للعمليات الزراعية في شركة أطلس سيوة
            </Typography>
            <Button
              variant="contained"
              size="large"
              onClick={handleLogin}
              sx={{
                bgcolor: '#4ade80', color: '#052e16', fontWeight: 700,
                px: 6, py: 1.5, fontSize: '1.1rem',
                '&:hover': { bgcolor: '#22c55e' },
              }}
            >
              دخول النظام ←
            </Button>
          </Box>
        </Container>
      </Box>

      {/* ── قسم التواصل ─────────────────────── */}
      <Box id="contact" sx={{ py: { xs: 8, md: 10 }, bgcolor: '#f8fafc' }}>
        <Container maxWidth="md">
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Chip label="تواصل معنا" sx={{ bgcolor: '#f0fdf4', color: '#16a34a', fontWeight: 700, mb: 2 }} />
            <Typography variant={isMobile ? 'h4' : 'h3'} fontWeight={800} gutterBottom>
              نحن هنا لمساعدتك
            </Typography>
          </Box>

          <Grid container spacing={3} justifyContent="center">
            {[
              { icon: '📍', title: 'المقر الرئيسي', info: 'كم 43 طريق مصر-إسكندرية الصحراوي، الشيخ زايد، الجيزة' },
              { icon: '🌴', title: 'المزارع', info: 'واحة سيوة، الصحراء الغربية، محافظة مطروح، مصر' },
              { icon: '📈', title: 'الشركة الأم', info: 'أطلس للاستثمار والصناعات الغذائية — مقيدة بالبورصة المصرية' },
            ].map((item) => (
              <Grid item xs={12} sm={4} key={item.title}>
                <Card sx={{ p: 3, textAlign: 'center', borderRadius: 3, height: '100%' }}>
                  <Typography variant="h2" sx={{ mb: 1 }}>{item.icon}</Typography>
                  <Typography variant="subtitle1" fontWeight={700} gutterBottom>{item.title}</Typography>
                  <Typography variant="body2" color="text.secondary">{item.info}</Typography>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* ── الـ Footer ───────────────────────── */}
      <Box sx={{ bgcolor: '#052e16', py: 4, px: 2 }}>
        <Container maxWidth="lg">
          <Box
            sx={{
              display: 'flex',
              flexDirection: { xs: 'column', sm: 'row' },
              justifyContent: 'space-between',
              alignItems: 'center',
              gap: 2,
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <AgricultureIcon sx={{ color: '#4ade80', fontSize: 24 }} />
              <Typography variant="body2" color="rgba(255,255,255,0.8)">
                © {new Date().getFullYear()} أطلس سيوة للتنمية الزراعية — جميع الحقوق محفوظة
              </Typography>
            </Box>
            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.4)' }}>
              تابعة لشركة أطلس للاستثمار والصناعات الغذائية | البورصة المصرية
            </Typography>
          </Box>
        </Container>
      </Box>
    </Box>
  );
}
```

---

## E.2 — تحديث الـ Routes لإضافة Landing Page

### الملف المطلوب تعديله:
```
Front-End/src/routes/AppRoutes.jsx
```

### ما يجب فعله:
أضف الـ Route الخاص بالـ Landing Page:

```jsx
// أضف هذا الـ import في الأعلى:
import LandingPage from '../pages/LandingPage';

// أضف هذا الـ Route:
<Route path="/" element={<LandingPage />} />

// تأكد أن صفحة الـ Login تكون على:
<Route path="/login" element={<Login />} />
```

---

---

# ═══════════════════════════════════════════
# PHASE F — تثبيت التبعيات المطلوبة
# ═══════════════════════════════════════════

## F.1 — تثبيت خط Cairo العربي

### الملف المطلوب تعديله:
```
Front-End/index.html
```

```html
<!-- أضف هذا داخل <head> -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap" rel="stylesheet">
```

---

## F.2 — إضافة RTL Support لـ MUI

### الملف المطلوب تعديله:
```
Front-End/src/main.jsx
```

```jsx
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { ThemeProvider } from '@mui/material/styles';
import { CacheProvider } from '@emotion/react';
import createCache from '@emotion/cache';
import { prefixer } from 'stylis';
import rtlPlugin from 'stylis-plugin-rtl';
import CssBaseline from '@mui/material/CssBaseline';
import theme from './theme/theme';
import App from './App';
import './index.css';

// إنشاء Cache للـ RTL
const cacheRtl = createCache({
  key: 'muirtl',
  stylisPlugins: [prefixer, rtlPlugin],
});

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <CacheProvider value={cacheRtl}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <App />
      </ThemeProvider>
    </CacheProvider>
  </StrictMode>,
);
```

### تثبيت حزمة الـ RTL:
```bash
npm install stylis-plugin-rtl
```

---

---

# ═══════════════════════════════════════════
# ملخص الملفات المطلوب إنشاؤها / تعديلها
# ═══════════════════════════════════════════

## ملفات جديدة يجب إنشاؤها:

| الملف | الغرض |
|-------|-------|
| `Front-End/src/theme/theme.js` | نظام الألوان والـ Theme الموحد |
| `Front-End/src/components/BottomNav.jsx` | التنقل السفلي للهاتف |
| `Front-End/src/components/LoadingSpinner.jsx` | شاشات التحميل |
| `Front-End/src/components/EmptyState.jsx` | حالة عدم وجود بيانات |
| `Front-End/src/pages/LandingPage.jsx` | صفحة الهبوط الكاملة |

## ملفات موجودة يجب تعديلها:

| الملف | التعديل المطلوب |
|-------|----------------|
| `Front-End/src/layouts/DashboardLayout.jsx` | إصلاح Sidebar للـ Responsive |
| `Front-End/src/layouts/DashboardTopbar.jsx` | إصلاح Topbar + زر Hamburger |
| `Front-End/src/routes/AppRoutes.jsx` | إضافة Route للـ Landing Page |
| `Front-End/src/main.jsx` | إضافة ThemeProvider + RTL Cache |
| `Front-End/index.html` | إضافة خط Cairo |
| `Front-End/src/index.css` | إضافة CSS Responsive |

## حزمة npm يجب تثبيتها:

```bash
npm install stylis-plugin-rtl
```

---

# ═══════════════════════════════════════════
# ترتيب التنفيذ الموصى به
# ═══════════════════════════════════════════

```
الخطوة 1: ثبّت الحزمة:  npm install stylis-plugin-rtl
الخطوة 2: أنشئ theme.js وطبّقه في main.jsx
الخطوة 3: أضف خط Cairo في index.html
الخطوة 4: أصلح DashboardLayout.jsx (Sidebar Responsive)
الخطوة 5: أصلح DashboardTopbar.jsx (زر Hamburger)
الخطوة 6: أنشئ BottomNav.jsx وأضفه للـ DashboardLayout
الخطوة 7: أضف CSS الـ Responsive في index.css
الخطوة 8: أنشئ LandingPage.jsx بالكود الكامل أعلاه
الخطوة 9: أضف Route للـ Landing Page في AppRoutes.jsx
الخطوة 10: أنشئ LoadingSpinner.jsx و EmptyState.jsx
```

---

> **ملاحظة للنموذج**: كل كود في هذا الملف جاهز للتطبيق المباشر. لا تعدّل المنطق الداخلي للكود الموجود، فقط أضف ما هو مطلوب في الأماكن المحددة.
