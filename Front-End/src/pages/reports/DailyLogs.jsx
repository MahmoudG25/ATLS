import React, { useState, useEffect } from 'react';
import { Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField, CircularProgress, Alert, MenuItem, Grid, Card, Box } from '@mui/material';
import { getReports, createReport } from '../../features/reports/services';
import { getFarmStructure } from '../../features/farm/services';
import { useTranslation } from 'react-i18next';
import AssignmentOutlinedIcon from '@mui/icons-material/AssignmentOutlined';
import AddCircleOutlinedIcon from '@mui/icons-material/AddCircleOutlined';
import ArticleOutlinedIcon from '@mui/icons-material/ArticleOutlined';
import LocationOnOutlinedIcon from '@mui/icons-material/LocationOnOutlined';
import EngineeringOutlinedIcon from '@mui/icons-material/EngineeringOutlined';

const DailyLogs = () => {
  const { t } = useTranslation();
  const [reports, setReports]     = useState([]);
  const [structure, setStructure] = useState([]);
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState(null);

  const [openModal, setOpenModal]     = useState(false);
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError]     = useState('');

  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    sector: '', plot: '', operation_type: '', workers: '', notes: ''
  });

  useEffect(() => { fetchInitialData(); }, []);

  const fetchInitialData = async () => {
    setLoading(true);
    try {
      const [r, struct] = await Promise.all([getReports(), getFarmStructure()]);
      setReports(r); setStructure(struct);
    } catch { setError(t('reports.error_fetch')); }
    finally { setLoading(false); }
  };

  const handleCreate = async () => {
    setFormLoading(true); setFormError('');
    try {
      const payload = { ...formData };
      if (!payload.plot) delete payload.plot;
      await createReport(payload);
      setOpenModal(false); fetchInitialData();
    } catch { setFormError(t('common.error')); }
    finally { setFormLoading(false); }
  };

  const availablePlots = formData.sector ? (structure.find(s => s.id === formData.sector)?.plots || []) : [];

  return (
    <div className="p-8 w-full space-y-8">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-800 tracking-tight flex items-center gap-3">
            <div className="p-2 bg-blue-50 rounded-xl text-blue-600 flex items-center">
              <AssignmentOutlinedIcon fontSize="large" />
            </div>
            {t('reports.title', 'التقارير اليومية')}
          </h1>
          <p className="text-slate-500 mt-2 font-medium">{t('reports.subtitle', 'سجلات العمل والنشاطات اليومية في المزرعة')}</p>
        </div>
        <Button 
          variant="contained" 
          startIcon={<AddCircleOutlinedIcon />}
          onClick={() => setOpenModal(true)} 
          sx={{ borderRadius: 3, px: 3, py: 1, fontWeight: 700, bgcolor: '#0f172a', '&:hover': { bgcolor: '#1e293b' }, boxShadow: '0 4px 14px 0 rgba(15, 23, 42, 0.39)' }}
        >
          {t('reports.add_btn', 'تسجيل تقرير جديد')}
        </Button>
      </div>

      {error && <Alert severity="error">{error}</Alert>}

      <div className="space-y-4">
        {loading ? <div className="flex justify-center p-12"><CircularProgress sx={{ color: '#0f172a' }} /></div> :
         reports.length === 0 ? (
           <Card sx={{ p: 8, borderRadius: 4, border: '1px solid #e2e8f0', boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.05)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }} elevation={0}>
             <ArticleOutlinedIcon sx={{ fontSize: 64, color: '#cbd5e1', mb: 2 }} />
             <p className="text-slate-400 font-semibold">{t('reports.no_data', 'لا توجد تقارير يومية حتى الآن')}</p>
           </Card>
         ) :
         reports.map(r => (
          <Card key={r.id} elevation={0} sx={{ p: 4, borderRadius: 4, border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)', display: 'flex', flexDirection: { xs: 'column', md: 'row' }, justifyContent: 'space-between', gap: 4, position: 'relative', overflow: 'hidden', transition: 'transform 0.2s ease, box-shadow 0.2s ease', '&:hover': { transform: 'translateY(-2px)', boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)' } }}>
            <Box sx={{ position: 'absolute', top: 0, left: 0, width: '4px', height: '100%', bgcolor: '#3b82f6' }} />
            <div>
              <div className="flex gap-3 items-center mb-3">
                <span className="font-black text-slate-800 text-xl">{r.operation_type}</span>
                <span className="text-xs bg-slate-100 border border-slate-200 text-slate-600 px-2 py-0.5 rounded-md font-bold">{r.date}</span>
              </div>
              <p className="text-slate-600 font-medium text-sm max-w-prose mb-4 leading-relaxed">{r.notes}</p>
              <div className="flex flex-wrap gap-4 text-sm font-semibold text-slate-500">
                <div className="flex items-center gap-1 bg-slate-50 px-2 py-1 rounded-lg border border-slate-100"><LocationOnOutlinedIcon fontSize="small" color="primary" /> {r.sector_name} {r.plot_name ? `/ ${r.plot_name}` : ''}</div>
                <div className="flex items-center gap-1 bg-slate-50 px-2 py-1 rounded-lg border border-slate-100"><EngineeringOutlinedIcon fontSize="small" color="secondary" /> {r.workers} {t('reports.workers_active', 'عمال')}</div>
              </div>
            </div>
            <div className="md:text-right flex flex-col justify-between items-start md:items-end border-t md:border-t-0 md:border-l border-slate-100 pt-4 md:pt-0 md:pl-4">
              <div className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">{t('reports.signed_by', 'المشرف المسؤول')}</div>
              <div className="text-sm font-black text-slate-800 bg-slate-100 px-3 py-1.5 rounded-xl border border-slate-200">{r.engineer_name}</div>
            </div>
          </Card>
        ))}
      </div>

      <Dialog open={openModal} onClose={() => setOpenModal(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 4, p: 1 } }}>
        <DialogTitle sx={{ fontWeight: 900, fontSize: '1.5rem', display: 'flex', alignItems: 'center', gap: 1.5, color: '#0f172a' }}>
          <AssignmentOutlinedIcon fontSize="large" color="primary" />
          {t('reports.modal_title', 'تسجيل تقرير جديد')}
        </DialogTitle>
        <DialogContent sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 3 }}>
          {formError && <Alert severity="error" sx={{ borderRadius: 2 }}>{formError}</Alert>}
          <Grid container spacing={3} sx={{ mt: 0.5 }}>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth type="date" label={t('reports.field_date', 'التاريخ')} value={formData.date} onChange={(e) => setFormData({...formData, date: e.target.value})} variant="outlined" InputLabelProps={{ shrink: true }} InputProps={{ sx: { borderRadius: 2.5 } }} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth label={t('reports.field_operation', 'نوع العملية')} value={formData.operation_type} onChange={(e) => setFormData({...formData, operation_type: e.target.value})} variant="outlined" InputProps={{ sx: { borderRadius: 2.5 } }} />
            </Grid>
          </Grid>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <TextField select fullWidth label={t('reports.field_sector', 'القطاع')} value={formData.sector} onChange={(e) => setFormData({...formData, sector: e.target.value, plot: ''})} variant="outlined" InputProps={{ sx: { borderRadius: 2.5 } }}>
                {structure.map(s => <MenuItem key={s.id} value={s.id} sx={{ fontWeight: 600 }}>{s.name}</MenuItem>)}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField select fullWidth label={t('reports.field_plot', 'الحقل (اختياري)')} value={formData.plot} onChange={(e) => setFormData({...formData, plot: e.target.value})} variant="outlined" disabled={!formData.sector} InputProps={{ sx: { borderRadius: 2.5 } }}>
                <MenuItem value="" sx={{ fontStyle: 'italic', color: 'text.secondary' }}>{t('reports.entire_zone', 'القطاع بالكامل')}</MenuItem>
                {availablePlots.map(p => <MenuItem key={p.id} value={p.id} sx={{ fontWeight: 600 }}>{p.name}</MenuItem>)}
              </TextField>
            </Grid>
          </Grid>
          <TextField fullWidth type="number" label={t('reports.field_workers', 'عدد العمال')} value={formData.workers} onChange={(e) => setFormData({...formData, workers: e.target.value})} variant="outlined" InputProps={{ sx: { borderRadius: 2.5 } }} />
          <TextField fullWidth multiline rows={4} label={t('reports.field_notes', 'ملاحظات وتفاصيل العمل')} value={formData.notes} onChange={(e) => setFormData({...formData, notes: e.target.value})} variant="outlined" InputProps={{ sx: { borderRadius: 2.5 } }} />
        </DialogContent>
        <DialogActions sx={{ p: 3, pt: 1 }}>
          <Button onClick={() => setOpenModal(false)} sx={{ fontWeight: 800, color: 'text.secondary' }}>{t('reports.cancel', 'إلغاء')}</Button>
          <Button onClick={handleCreate} variant="contained" disabled={formLoading || !formData.date || !formData.operation_type || !formData.sector || !formData.workers} sx={{ borderRadius: 2.5, px: 5, py: 1.5, fontWeight: 800, bgcolor: '#0f172a', '&:hover': { bgcolor: '#1e293b' } }}>
            {t('reports.save_btn', 'حفظ التقرير')}
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};
export default DailyLogs;
