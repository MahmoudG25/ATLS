import React, { useState, useEffect, useCallback } from 'react';
import { Box, Typography, CircularProgress, Alert } from '@mui/material';
import { useTranslation } from 'react-i18next';
import StatCard from './StatCard';
import { TrendsChart, CostsBarChart, WorkerDistributionChart } from './AnalyticsCharts';
import InsightsSection from './InsightsSection';
import ReportsTable from './ReportsTable';
import { reportsApi } from '../../../services/reportsApi';

// Icons
import AssessmentIcon from '@mui/icons-material/Assessment';
import MonetizationOnIcon from '@mui/icons-material/MonetizationOn';
import PrecisionManufacturingIcon from '@mui/icons-material/PrecisionManufacturing';

const AnalyticsDashboard = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Data States
  const [kpiData, setKpiData] = useState(null);
  const [trendsData, setTrendsData] = useState([]);
  const [costData, setCostData] = useState(null);
  const [insightsData, setInsightsData] = useState(null);
  const [reportsData, setReportsData] = useState([]);
  
  // Filter States
  const [filters, setFilters] = useState({
    operation: '',
    location: '',
    report_date: ''
  });
  const [pagination, setPagination] = useState({
    page: 0,
    rowsPerPage: 10,
    totalCount: 0
  });

  // Dropdown States
  const [operations, setOperations] = useState([]);
  const [locations, setLocations] = useState([]);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [kpiRes, trendsRes, costRes, insightsRes, opsRes, locsRes] = await Promise.allSettled([
        reportsApi.getKpiAnalytics(),
        reportsApi.getTrendsAnalytics(),
        reportsApi.getCostAnalytics(),
        reportsApi.getSmartInsights(),
        reportsApi.getOperations(),
        reportsApi.getFarmHierarchy(),
      ]);

      if (kpiRes.status === 'fulfilled') setKpiData(kpiRes.value.data);
      if (trendsRes.status === 'fulfilled') setTrendsData(trendsRes.value.data.trends || []);
      if (costRes.status === 'fulfilled') setCostData(costRes.value.data);
      if (insightsRes.status === 'fulfilled') setInsightsData(insightsRes.value.data);
      if (opsRes.status === 'fulfilled') {
        const opsData = opsRes.value.data;
        setOperations(Array.isArray(opsData) ? opsData : (opsData.results ?? []));
      }
      if (locsRes.status === 'fulfilled') {
        const hier = locsRes.value.data;
        const flatLocs = [];
        (hier.crops || []).forEach(crop => {
          (crop.stages || []).forEach(stage => (stage.enclosures || []).forEach(e => flatLocs.push(e)));
          (crop.regions || []).forEach(r => flatLocs.push(r));
        });
        setLocations(flatLocs);
      }

      await fetchReports();
      setError(null);
    } catch (err) {
      console.error('Error fetching analytics data:', err);
      setError('فشل تحميل بيانات التحليلات. يرجى المحاولة مرة أخرى.');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchReports = async (page = pagination.page, rowsPerPage = pagination.rowsPerPage, currentFilters = filters) => {
    try {
      const params = {
        page: page + 1,
        page_size: rowsPerPage,
        ...currentFilters
      };
      const response = await reportsApi.getTasks(params);
      setReportsData(response.data.results || response.data);
      setPagination(prev => ({
        ...prev,
        page,
        rowsPerPage,
        totalCount: response.data.count || (response.data.results ? response.data.results.length : response.data.length)
      }));
    } catch (err) {
      console.error('Error fetching reports:', err);
    }
  };

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleFilterChange = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    fetchReports(0, pagination.rowsPerPage, newFilters);
  };

  const handlePageChange = (event, newPage) => {
    fetchReports(newPage, pagination.rowsPerPage);
  };

  const handleRowsPerPageChange = (event) => {
    const newRowsPerPage = parseInt(event.target.value, 10);
    fetchReports(0, newRowsPerPage);
  };

  if (loading && !kpiData) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress sx={{ color: '#10b981' }} />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  const workerDist = [
    { name: t('analytics.company_workers', 'عمال الشركة'), value: kpiData?.total_company_workers || 0 },
    { name: t('analytics.contractor_workers', 'عمال المقاول'), value: kpiData?.total_contractor_workers || 0 }
  ];

  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h4" fontWeight="800" sx={{ mb: 3 }} color="primary.main">
        {t('analytics.dashboard_title', 'لوحة تحليلات التقارير')}
      </Typography>

      {/* Top KPI Cards — Flexbox for reliable RTL fill */}
      <Box sx={{ display: 'flex', gap: 3, mb: 3, flexDirection: { xs: 'column', sm: 'row' } }}>
        <Box sx={{ flex: 1 }}>
          <StatCard
            title={t('analytics.total_reports', 'إجمالي التقارير')}
            value={kpiData?.total_reports || 0}
            icon={AssessmentIcon}
            color="#3b82f6"
          />
        </Box>
        <Box sx={{ flex: 1 }}>
          <StatCard
            title={t('analytics.total_cost', 'إجمالي التكاليف')}
            value={`${costData?.total_cost?.toLocaleString() || 0} EGP`}
            icon={MonetizationOnIcon}
            color="#10b981"
          />
        </Box>
        <Box sx={{ flex: 1 }}>
          <StatCard
            title={t('analytics.avg_productivity', 'متوسط الإنتاجية')}
            value={kpiData?.avg_productivity?.toFixed(2) || 0}
            icon={PrecisionManufacturingIcon}
            color="#f59e0b"
          />
        </Box>
      </Box>

      {/* Charts Section — اتجاهات التقارير (2/3) + توزيع العمالة (1/3) */}
      <Box sx={{ display: 'flex', gap: 3, mb: 3, flexDirection: { xs: 'column', lg: 'row' } }}>
        <Box sx={{ flex: 2 }}>
          <TrendsChart
            data={trendsData}
            title={t('analytics.trends_title', 'اتجاهات التقارير والتكاليف')}
          />
        </Box>
        <Box sx={{ flex: 1 }}>
          <WorkerDistributionChart
            data={workerDist}
            title={t('analytics.workers_dist', 'توزيع العمالة')}
          />
        </Box>
      </Box>

      {/* التكلفة حسب العملية (2/3) يمين + Insights (1/3) يسار */}
      <Box sx={{ display: 'flex', gap: 3, mb: 3, flexDirection: { xs: 'column', lg: 'row' } }}>
        <Box sx={{ flex: 2 }}>
          <CostsBarChart
            data={costData?.cost_per_operation || []}
            title={t('analytics.cost_per_op', 'التكلفة حسب العملية')}
          />
        </Box>
        <Box sx={{ flex: 1 }}>
          <InsightsSection data={insightsData} t={t} />
        </Box>
      </Box>

      {/* Reports Table */}
      <Box sx={{ mb: 3 }}>
        <ReportsTable
          data={reportsData}
          totalCount={pagination.totalCount}
          page={pagination.page}
          rowsPerPage={pagination.rowsPerPage}
          onPageChange={handlePageChange}
          onRowsPerPageChange={handleRowsPerPageChange}
          filters={filters}
          onFilterChange={handleFilterChange}
          operations={operations}
          locations={locations}
          t={t}
        />
      </Box>
    </Box>
  );
};

export default AnalyticsDashboard;

