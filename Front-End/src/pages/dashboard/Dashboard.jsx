import React, { useState, useEffect } from 'react';
import { Card, Typography, Box, Chip, Grid, useTheme, CircularProgress } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { getFinancialSummary } from '../../features/accounting/services';
import { getEquipmentList } from '../../features/equipment/services';
import { getItems } from '../../features/warehouse/services';
import { useAuth } from '../../app/AuthContext';
import PaymentsIcon    from '@mui/icons-material/Payments';
import AgricultureIcon from '@mui/icons-material/Agriculture';
import WarehouseIcon   from '@mui/icons-material/Warehouse';
import GrassIcon from '@mui/icons-material/Grass';
import AssessmentIcon from '@mui/icons-material/Assessment';
import BarChartIcon from '@mui/icons-material/BarChart';
import TrendingUpIcon  from '@mui/icons-material/TrendingUp';
import TrendingDownIcon  from '@mui/icons-material/TrendingDown';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

const ModuleCard = ({ title, description, icon: Icon, color, bgColor, path, count }) => {
  const navigate = useNavigate();
  const theme = useTheme();
  return (
    <Card
      onClick={() => navigate(path)}
      sx={{
        cursor: 'pointer',
        border: 1,
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        width: '100%',
        borderColor: 'border.subtle',
        boxShadow: theme.customTokens?.shadows?.subtle || 'none',
        transition: 'all 0.2s ease',
        '&:hover': {
          borderColor: color,
          boxShadow: `0 4px 20px ${theme.palette[color.split('.')[0]]?.main || theme.palette.primary.main}20`,
          transform: 'translateY(-3px)',
          '& .module-arrow': { transform: 'translateX(-4px)' },
        },
      }}
    >
      <Box sx={{ p: 3, display: 'flex', flexDirection: 'column', height: '100%' }}>
        <Box
          sx={{
            width: 52, height: 52, borderRadius: 2.5,
            bgcolor: bgColor, mb: 2,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}
        >
          <Icon sx={{ color, fontSize: 28 }} />
        </Box>

        <Typography variant="h6" color="text.primary" gutterBottom>
          {title}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2, flexGrow: 1 }}>
          {description}
        </Typography>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 'auto' }}>
          <Chip label={count} size="small" sx={{ bgcolor: bgColor, color, fontWeight: 600 }} />
          <ArrowBackIcon
            className="module-arrow"
            sx={{ color, fontSize: 18, transition: 'transform 0.2s' }}
          />
        </Box>
      </Box>
    </Card>
  );
};

const StatCard = ({ title, value, unit, icon: Icon, color, bgColor, trend, trendUp }) => {
  const theme = useTheme();
  return (
    <Card
      sx={{
        border: 1,
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        width: '100%',
        borderColor: 'border.subtle',
        boxShadow: theme.customTokens?.shadows?.subtle || 'none',
        transition: 'all 0.2s ease',
        '&:hover': {
          boxShadow: `0 4px 20px ${theme.palette[color.split('.')[0]]?.main || theme.palette.primary.main}20`,
          transform: 'translateY(-2px)',
        },
      }}
    >
      <Box sx={{ p: 3, display: 'flex', flexDirection: 'column', height: '100%' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Typography variant="body2" color="text.secondary" fontWeight={600}>
            {title}
          </Typography>
          <Box
            sx={{
              width: 44, height: 44, borderRadius: 2.5,
              bgcolor: bgColor,
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}
          >
            <Icon sx={{ color, fontSize: 22 }} />
          </Box>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1, mb: 1, flexGrow: 1 }}>
          <Typography variant="h4" color="text.primary" fontWeight={800}>
            {value}
          </Typography>
          {unit && (
            <Typography variant="body2" color="text.secondary">{unit}</Typography>
          )}
        </Box>

        {trend && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            {trendUp === true && <TrendingUpIcon sx={{ color: 'success.main', fontSize: 14 }} />}
            {trendUp === false && <TrendingDownIcon sx={{ color: 'error.main', fontSize: 14 }} />}
            <Typography
              variant="caption"
              color={trendUp === true ? 'success.main' : trendUp === false ? 'error.main' : 'text.secondary'}
              fontWeight={600}
            >
              {trend}
            </Typography>
          </Box>
        )}
      </Box>
    </Card>
  );
}

const Dashboard = () => {
  const { user } = useAuth();
  const { t, i18n } = useTranslation();
  const [finance, setFinance]       = useState(null);
  const [equipCount, setEquipCount] = useState(0);
  const [itemCount, setItemCount]   = useState(0);
  const [loading, setLoading]       = useState(true);

  const canViewFinance = ['SUPER_ADMIN', 'OWNER', 'MANAGER', 'ACCOUNTANT'].includes(user?.role);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const promises = [getEquipmentList(), getItems()];
        if (canViewFinance) promises.push(getFinancialSummary());
        const results = await Promise.all(promises);
        setEquipCount(results[0]?.length ?? 0);
        setItemCount(results[1]?.length ?? 0);
        if (canViewFinance) setFinance(results[2]);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, [canViewFinance]);

  if (loading) {
    return (
      <Box sx={{ width: '100%', p: 3, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress sx={{ color: 'primary.main' }} />
      </Box>
    );
  }

  return (
    <Box
      sx={{
        width: '100%',
        maxWidth: '100%',
        px: { xs: 2, sm: 3, md: 4 },
        py: { xs: 2, md: 3 },
        boxSizing: 'border-box',
      }}
    >
      {/* Greeting */}
      <Box
        sx={{
          mb: 4,
          width: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center',
        }}
      >
        <Typography variant="h3" color="text.primary" gutterBottom>
          👋 {t('dashboard.welcome', 'مرحبًا بعودتك')}، <Box component="span" sx={{ color: 'primary.main' }}>{user?.name?.split(' ')[0]}</Box>
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {t('dashboard.overview', 'إليك نظرة عامة على عمليات مزرعتك اليوم')}
        </Typography>
        <Chip
          label={`📅 ${new Date().toLocaleDateString(i18n.language === 'ar' ? 'ar-DZ' : 'en-GB', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}`}
          size="small"
          sx={{ mt: 2, bgcolor: 'semanticBg.success', color: 'primary.main', fontWeight: 600 }}
        />
      </Box>

      {/* KPI Cards */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: {
            xs: '1fr',
            sm: 'repeat(2, 1fr)',
            md: canViewFinance ? 'repeat(3, 1fr)' : 'repeat(2, 1fr)'
          },
          gap: 3,
          mb: 4,
          width: '100%',
        }}
      >
        {canViewFinance && (
          <StatCard
            title={t('dashboard.net_margin', 'صافي الأرباح')}
            value={`$${parseFloat(finance?.net || 0).toLocaleString()}`}
            unit=""
            icon={TrendingUpIcon}
            color="success.main"
            bgColor="semanticBg.success"
            trend={t('dashboard.margin_trend', '+15% عن الشهر الماضي')}
            trendUp={true}
          />
        )}

        <StatCard
          title={t('dashboard.fleet_units', 'وحدات الأسطول النشطة')}
          value={equipCount}
          unit={t('dashboard.unit', 'وحدة')}
          icon={AgricultureIcon}
          color="warning.main"
          bgColor="semanticBg.warning"
          trend={t('dashboard.same_last_month', 'نفس الشهر الماضي')}
          trendUp={null}
        />

        <StatCard
          title={t('dashboard.warehouse_items', 'سلع المستودع')}
          value={itemCount}
          unit={t('dashboard.type', 'نوع')}
          icon={WarehouseIcon}
          color="info.main"
          bgColor="semanticBg.info"
          trend={t('dashboard.items_trend', '+2 هذا الشهر')}
          trendUp={true}
        />
      </Box>

      {/* Quick Actions (Module Cards) */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: {
            xs: '1fr',
            sm: 'repeat(2, 1fr)',
            md: 'repeat(3, 1fr)'
          },
          gap: 3,
          width: '100%',
        }}
      >
        <ModuleCard
          title={t('sidebar.equipment', 'الأسطول والمعدات')}
          description={t('dashboard.module_desc_equipment', 'إدارة آليات المزرعة والمعدات الزراعية')}
          icon={AgricultureIcon}
          color="info.main"
          bgColor="semanticBg.info"
          path="/equipment"
          count={equipCount > 0 ? `${equipCount} ${t('dashboard.active_unit', 'وحدة نشطة')}` : t('dashboard.no_units', 'لا توجد وحدات')}
        />
        <ModuleCard
          title={t('sidebar.production', 'الإنتاج والمحصول')}
          description={t('dashboard.module_desc_production', 'تتبع الإنتاج الزراعي الموسمي')}
          icon={GrassIcon}
          color="success.main"
          bgColor="semanticBg.success"
          path="/production"
          count={t('dashboard.current_season', 'الموسم الحالي')}
        />
        <ModuleCard
          title={t('sidebar.reports', 'التقارير اليومية')}
          description={t('dashboard.module_desc_reports', 'ملخصات يومية وتقارير العمليات')}
          icon={AssessmentIcon}
          color="warning.main"
          bgColor="semanticBg.warning"
          path="/reports"
          count={t('dashboard.last_updated_today', 'آخر تحديث: اليوم')}
        />
      </Box>

      {/* Chart placeholder -> Analytics Coming Soon */}
      <Card
        sx={{
          border: 2,
          borderStyle: 'dashed',
          borderColor: 'border.subtle',
          boxShadow: 'none',
          bgcolor: 'background.default',
          mt: 4,
          textAlign: 'center',
          p: 6
        }}
      >
        <Box
          sx={{
            width: 64, height: 64, borderRadius: 3,
            bgcolor: 'background.paper', mx: 'auto', mb: 2,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: (theme) => theme.customTokens?.shadows?.subtle
          }}
        >
          <BarChartIcon sx={{ color: 'text.disabled', fontSize: 32 }} />
        </Box>
        <Typography variant="h6" color="text.primary" gutterBottom fontWeight={700}>
          {t('dashboard.analytics_title', 'التحليلات والتقارير المتقدمة')}
        </Typography>
        <Typography variant="body2" color="text.secondary" maxWidth={400} mx="auto" mb={3}>
          {t('dashboard.analytics_desc', 'مساحة مخصصة للرسوم البيانية والتحليلات التفصيلية — ستكون متاحة في المرحلة الثانية')}
        </Typography>
        <Chip
          label={t('dashboard.analytics_soon', '🚧 قريباً — المرحلة الثانية')}
          sx={{ bgcolor: 'semanticBg.warning', color: 'warning.dark', fontWeight: 700 }}
        />
      </Card>
    </Box>
  );
};

export default Dashboard;
