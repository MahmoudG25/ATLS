import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  direction: 'rtl', // Default to RTL for Arabic
  palette: {
    primary: {
      main: '#16a34a',       // Agricultural Green
      light: '#4ade80',
      dark: '#15803d',
      contrastText: '#fff',
    },
    secondary: {
      main: '#78350f',       // Date Brown
      light: '#b45309',
      dark: '#451a03',
    },
    success: { main: '#16a34a' },
    warning: { main: '#d97706' },
    error: { main: '#dc2626' },
    background: {
      default: '#f8fafc',
      paper: '#ffffff',
    },
    text: {
      primary: '#1e293b',
      secondary: '#64748b',
    },
  },
  typography: {
    fontFamily: '"Cairo", "Outfit", "Segoe UI", sans-serif',
    h1: { fontWeight: 800 },
    h2: { fontWeight: 800 },
    h3: { fontWeight: 700 },
    h4: { fontWeight: 700 },
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
    button: { textTransform: 'none', fontWeight: 600 },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          padding: '8px 20px',
        },
        containedPrimary: {
          background: 'linear-gradient(135deg, #16a34a 0%, #15803d 100%)',
          '&:hover': { background: 'linear-gradient(135deg, #15803d 0%, #166534 100%)' },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)',
        },
      },
    },
    MuiTextField: {
      defaultProps: {
        variant: 'outlined',
        fullWidth: true,
      },
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 10,
          },
        },
      },
    },
  },
});

export default theme;
