import React, { useState, useEffect } from 'react';
import { Card, CircularProgress, Typography, Box, Chip } from '@mui/material';
import { Grid } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { getFinancialSummary } from '../../features/accounting/services';
import { getEquipmentList } from '../../features/equipment/services';
import { getItems } from '../../features/warehouse/services';
import { useAuth } from '../../app/AuthContext';
import PaymentsIcon    from '@mui/icons-material/Payments';
import AgricultureIcon from '@mui/icons-material/Agriculture';
import WarehouseIcon   from '@mui/icons-material/Warehouse';
import AutoGraphIcon   from '@mui/icons-material/AutoGraph';
import TrendingUpIcon  from '@mui/icons-material/TrendingUp';
import TrendingDownIcon  from '@mui/icons-material/TrendingDown';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import GrassIcon from '@mui/icons-material/Grass';
import AssessmentIcon from '@mui/icons-material/Assessment';
import BarChartIcon from '@mui/icons-material/BarChart';

const ModuleCard = ({ title, description, icon: Icon, color, bgColor, path, count }) => {
  const navigate = useNavigate();
  return (
    <Card
      onClick={() => navigate(path)}
      sx={{
        cursor: 'pointer',
        borderRadius: 3,
        border: '1px solid #e2e8f0',
        boxShadow: 'none',
        transition: 'all 0.2s ease',
        '&:hover': {
          borderColor: color,
          boxShadow: `0 4px 20px ${color}20`,
          transform: 'translateY(-3px)',
          '& .module-arrow': { transform: 'translateX(-4px)' },
        },
      }}
    >
      <div className="p-6">
        <Box
          sx={{
            width: 52, height: 52, borderRadius: 2.5,
            bgcolor: bgColor, mb: 2,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}
        >
          <Icon sx={{ color, fontSize: 28 }} />
        </Box>

        <Typography variant="h6" fontWeight={700} gutterBottom color="#1e293b">
          {title}
        </Typography>
        <Typography variant="body2" color="text.secondary" lineHeight={1.6} sx={{ mb: 2 }}>
          {description}
        </Typography>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Chip label={count} size="small" sx={{ bgcolor: bgColor, color, fontWeight: 600 }} />
          <ArrowBackIcon
            className="module-arrow"
            sx={{ color, fontSize: 18, transition: 'transform 0.2s' }}
          />
        </Box>
      </div>
    </Card>
  );
};

const StatCard = ({ title, value, unit, icon: Icon, color, bgColor, trend, trendUp }) => (
  <Card
    sx={{
      borderRadius: 3,
      border: `1px solid ${color}20`,
      boxShadow: 'none',
      transition: 'all 0.2s',
      '&:hover': {
        boxShadow: `0 4px 20px ${color}20`,
        transform: 'translateY(-2px)',
      },
    }}
  >
    <div className="p-6">
      {/* Top row: title + icon */}
      <div className="flex justify-between items-start mb-4">
        <Typography variant="body2" color="text.secondary" fontWeight={600}>
          {title}
        </Typography>
        <div
          style={{ backgroundColor: bgColor }}
          className="w-11 h-11 rounded-xl flex items-center justify-center"
        >
          <Icon sx={{ color, fontSize: 22 }} />
        </div>
      </div>

      {/* Value */}
      <div className="flex items-baseline gap-1 mb-2">
        <Typography variant="h4" fontWeight={800} color="#1e293b">
          {value}
        </Typography>
        {unit && (
          <Typography variant="body2" color="text.secondary">{unit}</Typography>
        )}
      </div>

      {/* Trend */}
      {trend && (
        <div className="flex items-center gap-1">
          {trendUp === true && <TrendingUpIcon sx={{ color: '#16a34a', fontSize: 14 }} />}
          {trendUp === false && <TrendingDownIcon sx={{ color: '#dc2626', fontSize: 14 }} />}
          <Typography
            variant="caption"
            color={trendUp === true ? '#16a34a' : trendUp === false ? '#dc2626' : 'text.secondary'}
            fontWeight={600}
          >
            {trend}
          </Typography>
        </div>
      )}
    </div>
  </Card>
);

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
      <div className="p-12 flex justify-center">
        <CircularProgress sx={{ color: '#16a34a' }} />
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Greeting */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h4" fontWeight={800} color="#1e293b" gutterBottom>
          👋 {t('dashboard.welcome', 'مرحبًا بعودتك')}، <Box component="span" sx={{ color: '#16a34a' }}>{user?.name?.split(' ')[0]}</Box>
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {t('dashboard.overview', 'إليك نظرة عامة على عمليات مزرعتك اليوم')}
        </Typography>
        <Chip
          label={`📅 ${new Date().toLocaleDateString(i18n.language === 'ar' ? 'ar-DZ' : 'en-GB', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}`}
          size="small"
          sx={{ mt: 1, bgcolor: '#f0fdf4', color: '#16a34a', fontWeight: 600 }}
        />
      </Box>

      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {canViewFinance && (
          <Grid xs={12} sm={6} md={4}>
            <StatCard
              title={t('dashboard.net_margin')}
              value={`$${parseFloat(finance?.net || 0).toLocaleString()}`}
              unit=""
              icon={TrendingUpIcon}
              color="#16a34a"
              bgColor="#f0fdf4"
              trend={t('dashboard.margin_trend', '+15% عن الشهر الماضي')}
              trendUp={true}
            />
          </Grid>
        )}

        <Grid xs={12} sm={6} md={canViewFinance ? 4 : 6}>
          <StatCard
            title={t('dashboard.fleet_units', 'وحدات الأسطول النشطة')}
            value={equipCount}
            unit={t('dashboard.unit', 'وحدة')}
            icon={AgricultureIcon}
            color="#d97706"
            bgColor="#fffbeb"
            trend={t('dashboard.same_last_month', 'نفس الشهر الماضي')}
            trendUp={null}
          />
        </Grid>

        <Grid xs={12} sm={6} md={canViewFinance ? 4 : 6}>
          <StatCard
            title={t('dashboard.warehouse_items', 'سلع المستودع')}
            value={itemCount}
            unit={t('dashboard.type', 'نوع')}
            icon={WarehouseIcon}
            color="#16a34a"
            bgColor="#f0fdf4"
            trend={t('dashboard.items_trend', '+2 هذا الشهر')}
            trendUp={true}
          />
        </Grid>
      </Grid>

      {/* Quick Actions (Module Cards) */}
      <Grid container spacing={3}>
        <Grid xs={12} md={4}>
          <ModuleCard
            title={t('sidebar.equipment', 'الأسطول والمعدات')}
            description={t('dashboard.module_desc_equipment', 'إدارة آليات المزرعة والمعدات الزراعية')}
            icon={AgricultureIcon}
            color="#1d4ed8"
            bgColor="#eff6ff"
            path="/equipment"
            count={equipCount > 0 ? `${equipCount} ${t('dashboard.active_unit', 'وحدة نشطة')}` : t('dashboard.no_units', 'لا توجد وحدات')}
          />
        </Grid>
        <Grid xs={12} md={4}>
          <ModuleCard
            title={t('sidebar.production', 'الإنتاج والمحصول')}
            description={t('dashboard.module_desc_production', 'تتبع الإنتاج الزراعي الموسمي')}
            icon={GrassIcon}
            color="#16a34a"
            bgColor="#f0fdf4"
            path="/production"
            count={t('dashboard.current_season', 'الموسم الحالي')}
          />
        </Grid>
        <Grid xs={12} md={4}>
          <ModuleCard
            title={t('sidebar.reports', 'التقارير اليومية')}
            description={t('dashboard.module_desc_reports', 'ملخصات يومية وتقارير العمليات')}
            icon={AssessmentIcon}
            color="#d97706"
            bgColor="#fffbeb"
            path="/reports"
            count={t('dashboard.last_updated_today', 'آخر تحديث: اليوم')}
          />
        </Grid>
      </Grid>

      {/* Chart placeholder -> Analytics Coming Soon */}
      <Card
        sx={{
          borderRadius: 3,
          border: '1px dashed #cbd5e1',
          boxShadow: 'none',
          bgcolor: '#fafafa',
          mt: 3,
        }}
      >
        <div className="p-8 text-center">
          <Box
            sx={{
              width: 64, height: 64, borderRadius: 3,
              bgcolor: '#f0fdf4', mx: 'auto', mb: 2,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}
          >
            <BarChartIcon sx={{ color: '#16a34a', fontSize: 32 }} />
          </Box>
          <Typography variant="h6" fontWeight={700} gutterBottom color="#1e293b">
            {t('dashboard.analytics_title', 'التحليلات والتقارير المتقدمة')}
          </Typography>
          <Typography variant="body2" color="text.secondary" maxWidth={400} mx="auto" mb={2}>
            {t('dashboard.analytics_desc', 'مساحة مخصصة للرسوم البيانية والتحليلات التفصيلية — ستكون متاحة في المرحلة الثانية')}
          </Typography>
          <Chip
            label={t('dashboard.analytics_soon', '🚧 قريباً — المرحلة الثانية')}
            sx={{ bgcolor: '#fff7ed', color: '#d97706', fontWeight: 700, border: '1px solid #fed7aa' }}
          />
        </div>
      </Card>
    </div>
  );
};

export default Dashboard;
