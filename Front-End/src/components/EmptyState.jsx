import { Box, Typography, Button } from '@mui/material';
import InboxIcon from '@mui/icons-material/Inbox';

export default function EmptyState({ 
  title = 'لا توجد بيانات',
  description = 'لم يتم العثور على أي نتائج في الوقت الحالي.',
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
        px: 3,
        textAlign: 'center',
        bgcolor: '#f8fafc',
        borderRadius: 6,
        border: '2px border-dashed #e2e8f0',
        gap: 2,
        maxWidth: 400,
        mx: 'auto'
      }}
    >
      <Box sx={{ 
        bgcolor: 'white', 
        p: 2, 
        borderRadius: '50%', 
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        mb: 1
      }}>
        <Icon sx={{ fontSize: 48, color: '#94a3b8' }} />
      </Box>
      <Box>
        <Typography variant="h6" sx={{ fontWeight: 800, color: 'slate.800' }}>
          {title}
        </Typography>
        <Typography variant="body2" sx={{ color: 'slate.500', mt: 0.5 }}>
          {description}
        </Typography>
      </Box>
      {actionText && onAction && (
        <Button 
          variant="contained" 
          onClick={onAction}
          sx={{ 
            mt: 1, 
            borderRadius: 2.5, 
            px: 4,
            fontWeight: 700
          }}
        >
          {actionText}
        </Button>
      )}
    </Box>
  );
}
