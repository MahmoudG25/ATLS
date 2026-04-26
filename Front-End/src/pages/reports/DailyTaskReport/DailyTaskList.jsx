import React, { useState, useEffect } from 'react';
import { Box, Card, Typography, Button, CircularProgress, Alert, Grid } from '@mui/material';
import { Add as AddIcon, CalendarToday as CalendarIcon, Engineering as EngineerIcon } from '@mui/icons-material';
import { Link } from 'react-router-dom';
import { reportsApi } from '../../../services/reportsApi';
import ReportBadge from '../shared/ReportBadge';
import ReportFilters from '../shared/ReportFilters';

const DailyTaskList = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    start_date: '', end_date: '', sector: '', engineer_name: ''
  });

  useEffect(() => {
    fetchReports();
  }, [filters]);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const params = Object.fromEntries(Object.entries(filters).filter(([_, v]) => v !== ''));
      const res = await reportsApi.getTasks(params);
      setReports(res.data.results || res.data);
    } catch (err) {
      setError('فشل في جلب التقارير اليومية');
    } finally {
      setLoading(false);
    }
  };

  const getBorderColor = (sector) => {
    const colors = {
      'A': '#4CAF50', 'B': '#2196F3', 'C': '#FF9800', 'D': '#9C27B0', 
      'greenhouse': '#00BCD4', 'new_farms': '#E91E63'
    };
    return colors[sector] || '#cbd5e1';
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h5" fontWeight="800" display="flex" alignItems="center" gap={1}>
          📋 تقارير المهام اليومية
        </Typography>
        <Box display="flex" gap={2}>
          <Button 
            component={Link} 
            to="summary"
            variant="outlined" 
            sx={{ borderRadius: 2, fontWeight: 700 }}
          >
            الملخص
          </Button>
          <Button 
            component={Link} 
            to="new"
            variant="contained" 
            startIcon={<AddIcon />}
            sx={{ borderRadius: 2, fontWeight: 700, bgcolor: '#0f172a', '&:hover': { bgcolor: '#1e293b' } }}
          >
            تقرير جديد
          </Button>
        </Box>
      </Box>

      <ReportFilters filters={filters} onFilterChange={setFilters} />

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      {loading ? (
        <Box display="flex" justifyContent="center" p={4}><CircularProgress /></Box>
      ) : reports.length === 0 ? (
        <Card sx={{ p: 6, textAlign: 'center', borderRadius: 4, bgcolor: '#f8fafc', boxShadow: 'none', border: '1px dashed #cbd5e1' }}>
          <Typography color="text.secondary" fontWeight="600">لا توجد تقارير مطابقة.</Typography>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {reports.map((report) => (
            <Grid item xs={12} md={6} lg={4} key={report.id}>
              <Card 
                sx={{ 
                  p: 3, 
                  borderRadius: 4, 
                  borderLeft: `6px solid ${getBorderColor(report.sector)}`,
                  boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)',
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  transition: 'transform 0.2s',
                  '&:hover': { transform: 'translateY(-4px)', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }
                }}
              >
                <Box display="flex" justifyContent="space-between" mb={2}>
                  <Box>
                    <Typography variant="h6" fontWeight="800" color="text.primary">
                      {report.engineer_name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" display="flex" alignItems="center" gap={0.5} mt={0.5}>
                      <CalendarIcon fontSize="small" /> {report.report_date}
                    </Typography>
                  </Box>
                  <ReportBadge type="sector" value={report.sector} />
                </Box>

                <Box mb={2} flexGrow={1}>
                  <Typography variant="body1" fontWeight="700" color="text.primary" mb={1}>
                    {report.operation_name}
                  </Typography>
                  <Box display="flex" flexWrap="wrap" gap={1} mb={2}>
                    <ReportBadge type="variety" value={report.variety} label={report.variety} />
                    <span className="text-xs font-semibold bg-slate-100 px-2 py-1 rounded-md text-slate-600">
                      عمالة: {report.company_workers + report.contractor_workers}
                    </span>
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                    {report.notes || 'لا توجد ملاحظات.'}
                  </Typography>
                </Box>

                <Box pt={2} borderTop="1px solid #f1f5f9" display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="subtitle2" fontWeight="800" color="primary.main">
                    انتاجية: {report.actual_productivity} {report.unit}
                  </Typography>
                  <Button size="small" component={Link} to={`/reports/tasks/${report.id}`} sx={{ fontWeight: 700 }}>التفاصيل</Button>
                </Box>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default DailyTaskList;
