import React, { useState, useEffect } from 'react';
import { Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField, CircularProgress, Alert, MenuItem, Grid, Card } from '@mui/material';
import { getReports, createReport } from '../../features/reports/services';
import { getFarmStructure } from '../../features/farm/services';
import { useTranslation } from 'react-i18next';

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
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">{t('reports.title')}</h1>
          <p className="text-slate-500 mt-1">{t('reports.subtitle')}</p>
        </div>
        <Button variant="contained" onClick={() => setOpenModal(true)} sx={{ background: '#3b82f6' }}>
          {t('reports.add_btn')}
        </Button>
      </div>

      {error && <Alert severity="error">{error}</Alert>}

      <div className="space-y-4">
        {loading ? <CircularProgress sx={{ color: '#16a34a' }} /> :
         reports.length === 0 ? <p className="text-slate-400 italic">{t('reports.no_data')}</p> :
         reports.map(r => (
          <Card key={r.id} elevation={0} className="p-6 border border-slate-100 rounded-2xl flex flex-col md:flex-row justify-between gap-4 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-1 h-full bg-blue-500" />
            <div>
              <div className="flex gap-2 items-center mb-2">
                <span className="font-black text-slate-800 text-lg">{r.operation_type}</span>
                <span className="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded font-bold">{r.date}</span>
              </div>
              <p className="text-slate-600 text-sm max-w-prose mb-3">{r.notes}</p>
              <div className="flex gap-4 text-xs font-medium text-slate-400">
                <div className="flex items-center gap-1">📍 {r.sector_name} {r.plot_name ? `/ ${r.plot_name}` : ''}</div>
                <div className="flex items-center gap-1">👷 {r.workers} {t('reports.workers_active')}</div>
              </div>
            </div>
            <div className="md:text-right flex flex-col justify-between">
              <div className="text-sm font-bold text-slate-700 bg-slate-50 px-3 py-1 rounded-full w-fit md:ml-auto">
                {t('reports.signed_by')}: {r.engineer_name}
              </div>
            </div>
          </Card>
        ))}
      </div>

      <Dialog open={openModal} onClose={() => setOpenModal(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{t('reports.modal_title')}</DialogTitle>
        <DialogContent className="pt-4 space-y-4">
          {formError && <Alert severity="error">{formError}</Alert>}
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <TextField fullWidth type="date" label={t('reports.field_date')} value={formData.date} onChange={(e) => setFormData({...formData, date: e.target.value})} variant="filled" InputLabelProps={{ shrink: true }} />
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label={t('reports.field_operation')} value={formData.operation_type} onChange={(e) => setFormData({...formData, operation_type: e.target.value})} variant="filled" />
            </Grid>
          </Grid>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <TextField select fullWidth label={t('reports.field_sector')} value={formData.sector} onChange={(e) => setFormData({...formData, sector: e.target.value, plot: ''})} variant="filled">
                {structure.map(s => <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>)}
              </TextField>
            </Grid>
            <Grid item xs={6}>
              <TextField select fullWidth label={t('reports.field_plot')} value={formData.plot} onChange={(e) => setFormData({...formData, plot: e.target.value})} variant="filled" disabled={!formData.sector}>
                <MenuItem value="">{t('reports.entire_zone')}</MenuItem>
                {availablePlots.map(p => <MenuItem key={p.id} value={p.id}>{p.name}</MenuItem>)}
              </TextField>
            </Grid>
          </Grid>
          <TextField fullWidth type="number" label={t('reports.field_workers')} value={formData.workers} onChange={(e) => setFormData({...formData, workers: e.target.value})} variant="filled" />
          <TextField fullWidth multiline rows={3} label={t('reports.field_notes')} value={formData.notes} onChange={(e) => setFormData({...formData, notes: e.target.value})} variant="filled" />
        </DialogContent>
        <DialogActions className="p-4">
          <Button onClick={() => setOpenModal(false)}>{t('reports.cancel')}</Button>
          <Button onClick={handleCreate} variant="contained" disabled={formLoading || !formData.date || !formData.operation_type || !formData.sector || !formData.workers}>
            {t('reports.save_btn')}
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};
export default DailyLogs;
