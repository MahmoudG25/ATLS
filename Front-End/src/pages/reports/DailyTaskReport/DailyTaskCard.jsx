import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Box, Card, Typography, Button, CircularProgress, Alert, Grid, Divider, Paper } from '@mui/material';
import { ArrowBack as ArrowBackIcon, CalendarToday as CalendarIcon, Engineering as EngineerIcon, Map as MapIcon, Person as PersonIcon } from '@mui/icons-material';
import { reportsApi } from '../../../services/reportsApi';
import ReportBadge from '../shared/ReportBadge';

const DailyTaskCard = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchReportDetails();
  }, [id]);

  const fetchReportDetails = async () => {
    try {
      setLoading(true);
      const res = await reportsApi.getTask(id);
      setReport(res.data);
    } catch (err) {
      setError('فشل في جلب تفاصيل التقرير');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Box display="flex" justifyContent="center" p={8}><CircularProgress /></Box>;
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!report) {
    return <Alert severity="warning">التقرير غير موجود</Alert>;
  }

  return (
    <Box>
      <Button 
        startIcon={<ArrowBackIcon />} 
        onClick={() => navigate(-1)} 
        sx={{ mb: 3, fontWeight: 700 }}
      >
        العودة للقائمة
      </Button>

      <Card sx={{ p: { xs: 3, md: 5 }, borderRadius: 2, boxShadow: '0 4px 20px rgba(0,0,0,0.05)' }}>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" flexWrap="wrap" gap={2} mb={4}>
          <Box>
            <Typography variant="h4" fontWeight="800" color="primary.main" gutterBottom>
              {report.operation_name}
            </Typography>
            <Box display="flex" gap={2} color="text.secondary" flexWrap="wrap">
              <Typography variant="body1" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <CalendarIcon fontSize="small" /> {report.report_date}
              </Typography>
              <Typography variant="body1" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <EngineerIcon fontSize="small" /> {report.engineer_name}
              </Typography>
            </Box>
          </Box>
          <Box display="flex" gap={1}>
            <ReportBadge type="sector" value={report.sector} />
            <ReportBadge type="variety" value={report.variety} label={report.variety} />
          </Box>
        </Box>

        <Divider sx={{ mb: 4 }} />

        {/* Details Grid */}
        <Grid container spacing={4}>
          {/* Main Info */}
          <Grid item xs={12} md={6}>
            <Typography variant="h6" fontWeight="700" sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
              <MapIcon color="action" /> بيانات الموقع والإنتاجية
            </Typography>
            
            <Paper elevation={0} sx={{ p: 3, bgcolor: '#f8fafc', borderRadius: 3, border: '1px solid #e2e8f0' }}>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">القطاع</Typography>
                  <Typography variant="body1" fontWeight="600">{report.sector}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">الصنف</Typography>
                  <Typography variant="body1" fontWeight="600">{report.variety}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">الإنتاجية المستهدفة</Typography>
                  <Typography variant="body1" fontWeight="600">{report.target_productivity} {report.unit}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">الإنتاجية الفعلية</Typography>
                  <Typography variant="body1" fontWeight="600" color={report.actual_productivity >= report.target_productivity ? 'success.main' : 'error.main'}>
                    {report.actual_productivity} {report.unit}
                  </Typography>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* Workers Info */}
          <Grid item xs={12} md={6}>
            <Typography variant="h6" fontWeight="700" sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
              <PersonIcon color="action" /> بيانات العمالة
            </Typography>
            
            <Paper elevation={0} sx={{ p: 3, bgcolor: '#f8fafc', borderRadius: 3, border: '1px solid #e2e8f0' }}>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">عمالة الشركة</Typography>
                  <Typography variant="body1" fontWeight="600">{report.company_workers}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">عمالة المقاول</Typography>
                  <Typography variant="body1" fontWeight="600">{report.contractor_workers}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">إجمالي العمالة</Typography>
                  <Typography variant="body1" fontWeight="600" color="primary.main">
                    {report.company_workers + report.contractor_workers} عامل
                  </Typography>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* Notes */}
          {report.notes && (
            <Grid item xs={12}>
              <Typography variant="h6" fontWeight="700" mb={2}>الملاحظات</Typography>
              <Paper elevation={0} sx={{ p: 3, bgcolor: '#fffbed', borderRadius: 3, border: '1px solid #fef08a' }}>
                <Typography variant="body1">{report.notes}</Typography>
              </Paper>
            </Grid>
          )}

          {/* Custom Fields - We can render them if they exist in the response */}
          {report.custom_fields && Object.keys(report.custom_fields).length > 0 && (
            <Grid item xs={12}>
              <Typography variant="h6" fontWeight="700" mb={2}>بيانات إضافية (مخصصة)</Typography>
              <Paper elevation={0} sx={{ p: 3, bgcolor: '#f0fdf4', borderRadius: 3, border: '1px solid #bbf7d0' }}>
                <Grid container spacing={2}>
                  {Object.entries(report.custom_fields).map(([key, value]) => (
                    <Grid item xs={12} sm={6} md={4} key={key}>
                      <Typography variant="body2" color="text.secondary">{key}</Typography>
                      <Typography variant="body1" fontWeight="600">{String(value)}</Typography>
                    </Grid>
                  ))}
                </Grid>
              </Paper>
            </Grid>
          )}
        </Grid>
      </Card>
    </Box>
  );
};

export default DailyTaskCard;
