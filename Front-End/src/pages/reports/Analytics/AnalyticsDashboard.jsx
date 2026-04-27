import React, { useState, useEffect, useCallback } from 'react';
import { Box, Grid, Typography, CircularProgress, Alert } from '@mui/material';
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
      const [kpi, trends, cost, insights, ops, locs] = await Promise.all([
        reportsApi.getKpiAnalytics(),
        reportsApi.getTrendsAnalytics(),
        reportsApi.getCostAnalytics(),
        reportsApi.getSmartInsights(),
        reportsApi.getOperations(),
        reportsApi.getSectors() // Using sectors as locations for filter
      ]);

      setKpiData(kpi.data);
      setTrendsData(trends.data.trends || []);
      setCostData(cost.data);
      setInsightsData(insights.data);
      setOperations(ops.data);
      setLocations(locs.data);
      
      await fetchReports();
      
      setError(null);
    } catch (err) {
      console.error('Error fetching analytics data:', err);
      setError('Failed to load analytics data. Please try again later.');
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
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress sx={{ color: '#10b981' }} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  // Map worker data for pie chart
  const workerDist = [
    { name: t('analytics.company_workers', 'عمال الشركة'), value: kpiData?.total_company_workers || 0 },
    { name: t('analytics.contractor_workers', 'عمال المقاول'), value: kpiData?.total_contractor_workers || 0 }
  ];

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* Top KPI Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <StatCard 
            title={t('analytics.total_reports', 'إجمالي التقارير')}
            value={kpiData?.total_reports || 0}
            icon={AssessmentIcon}
            color="#3b82f6"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <StatCard 
            title={t('analytics.total_cost', 'إجمالي التكاليف')}
            value={`${costData?.total_cost?.toLocaleString() || 0} EGP`}
            icon={MonetizationOnIcon}
            color="#10b981"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <StatCard 
            title={t('analytics.avg_productivity', 'متوسط الإنتاجية')}
            value={kpiData?.avg_productivity?.toFixed(2) || 0}
            icon={PrecisionManufacturingIcon}
            color="#f59e0b"
          />
        </Grid>
      </Grid>

      {/* Charts Section */}
      <Grid container spacing={3} mb={4}>
        <Grid size={{ xs: 12, lg: 8 }}>
          <TrendsChart 
            data={trendsData} 
            title={t('analytics.trends_title', 'اتجاهات التقارير والتكاليف')} 
          />
        </Grid>
        <Grid size={{ xs: 12, lg: 4 }}>
          <WorkerDistributionChart 
            data={workerDist} 
            title={t('analytics.workers_dist', 'توزيع العمالة')} 
          />
        </Grid>
      </Grid>

      <Grid container spacing={3} mb={4}>
        <Grid size={{ xs: 12, lg: 4 }}>
          <InsightsSection data={insightsData} t={t} />
        </Grid>
        <Grid size={{ xs: 12, lg: 8 }}>
          <CostsBarChart 
            data={costData?.cost_per_operation || []} 
            title={t('analytics.cost_per_op', 'التكلفة حسب العملية')} 
          />
        </Grid>
      </Grid>

      {/* Reports Table */}
      <Box mb={4}>
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
