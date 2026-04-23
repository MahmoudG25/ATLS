import React, { useState, useEffect } from 'react';
import { Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField, CircularProgress, Alert, Table, TableBody, TableCell, TableHead, TableRow, Paper, TableContainer, MenuItem, Grid } from '@mui/material';
import { getPalmRecords, createPalmRecord } from '../../features/palm/services';
import { getFarmStructure } from '../../features/farm/services';
import { useTranslation } from 'react-i18next';

const PalmRecords = () => {
  const { t } = useTranslation();
  const [records, setRecords]   = useState([]);
  const [structure, setStructure] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);

  const [openModal, setOpenModal]   = useState(false);
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError]   = useState('');

  const [formData, setFormData] = useState({
    plot: '', trees_count: '', palm_type: '', trees_age: '',
    last_year_production: '', expected_production: '',
    offshoots_count: '', sold_offshoots: ''
  });

  useEffect(() => { fetchInitialData(); }, []);

  const fetchInitialData = async () => {
    setLoading(true);
    try {
      const [recs, struct] = await Promise.all([getPalmRecords(), getFarmStructure()]);
      setRecords(recs); setStructure(struct);
    } catch { setError(t('palm.error_fetch')); }
    finally { setLoading(false); }
  };

  const handleCreate = async () => {
    setFormLoading(true); setFormError('');
    try {
      await createPalmRecord(formData);
      setOpenModal(false); fetchInitialData();
    } catch (err) {
      setFormError(err.response?.data ? Object.values(err.response.data).flat().join(', ') : t('common.error'));
    } finally { setFormLoading(false); }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-800 tracking-tight">{t('palm.title')}</h1>
          <p className="text-slate-500 mt-1">{t('palm.subtitle')}</p>
        </div>
        <Button variant="contained" onClick={() => setOpenModal(true)} sx={{ background: 'linear-gradient(to right,#16a34a,#15803d)' }}>
          {t('palm.add_record')}
        </Button>
      </div>

      {error && <Alert severity="error" className="mb-4">{error}</Alert>}

      {loading ? <CircularProgress sx={{ color: '#16a34a' }} /> : (
        <TableContainer component={Paper} elevation={0} className="border border-slate-100 rounded-xl overflow-hidden">
          <Table sx={{ minWidth: 650 }}>
            <TableHead sx={{ backgroundColor: '#f8fafc' }}>
              <TableRow>
                <TableCell sx={{ fontWeight: 700, color: '#475569' }}>{t('palm.col_plot')}</TableCell>
                <TableCell sx={{ fontWeight: 700, color: '#475569' }}>{t('palm.col_type')}</TableCell>
                <TableCell sx={{ fontWeight: 700, color: '#475569' }} align="right">{t('palm.col_trees')}</TableCell>
                <TableCell sx={{ fontWeight: 700, color: '#475569' }} align="right">{t('palm.col_age')}</TableCell>
                <TableCell sx={{ fontWeight: 700, color: '#475569' }} align="right">{t('palm.col_exp_yield')}</TableCell>
                <TableCell sx={{ fontWeight: 700, color: '#475569' }} align="right">{t('palm.col_act_yield')}</TableCell>
                <TableCell sx={{ fontWeight: 700, color: '#475569' }} align="right">{t('palm.col_offshoots')}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {records.length === 0 ? (
                <TableRow><TableCell colSpan={7} className="text-center text-slate-400 py-8">{t('palm.no_records')}</TableCell></TableRow>
              ) : records.map((row) => (
                <TableRow key={row.id} sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                  <TableCell>
                    <div className="font-medium text-slate-800">{row.plot_name}</div>
                    <div className="text-xs text-slate-400">{row.sector_name}</div>
                  </TableCell>
                  <TableCell>{row.palm_type}</TableCell>
                  <TableCell align="right">{row.trees_count}</TableCell>
                  <TableCell align="right">{row.trees_age || '-'}</TableCell>
                  <TableCell align="right">{row.expected_production || '-'}</TableCell>
                  <TableCell align="right">{row.last_year_production || '-'}</TableCell>
                  <TableCell align="right">{row.offshoots_count}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Dialog open={openModal} onClose={() => setOpenModal(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{t('palm.modal_title')}</DialogTitle>
        <DialogContent className="pt-4 space-y-4">
          {formError && <Alert severity="error" className="mb-4">{formError}</Alert>}
          <TextField select fullWidth label={t('palm.plot_link')} value={formData.plot} onChange={(e) => setFormData({...formData, plot: e.target.value})} variant="filled">
            {structure.flatMap(s => s.plots.map(p => <MenuItem key={p.id} value={p.id}>{p.name} - ({s.name})</MenuItem>))}
          </TextField>
          <Grid container spacing={2}>
            <Grid item xs={6}><TextField fullWidth label={t('palm.total_trees')} type="number" value={formData.trees_count} onChange={(e) => setFormData({...formData, trees_count: e.target.value})} variant="filled" /></Grid>
            <Grid item xs={6}><TextField fullWidth label={t('palm.palm_variety')} value={formData.palm_type} onChange={(e) => setFormData({...formData, palm_type: e.target.value})} variant="filled" /></Grid>
          </Grid>
          <Grid container spacing={2}>
            <Grid item xs={4}><TextField fullWidth label={t('palm.age_years')} type="number" value={formData.trees_age} onChange={(e) => setFormData({...formData, trees_age: e.target.value})} variant="filled" /></Grid>
            <Grid item xs={4}><TextField fullWidth label={t('palm.exp_yield')} type="number" value={formData.expected_production} onChange={(e) => setFormData({...formData, expected_production: e.target.value})} variant="filled" /></Grid>
            <Grid item xs={4}><TextField fullWidth label={t('palm.prev_yield')} type="number" value={formData.last_year_production} onChange={(e) => setFormData({...formData, last_year_production: e.target.value})} variant="filled" /></Grid>
          </Grid>
          <Grid container spacing={2}>
            <Grid item xs={6}><TextField fullWidth label={t('palm.offshoots_total')} type="number" value={formData.offshoots_count} onChange={(e) => setFormData({...formData, offshoots_count: e.target.value})} variant="filled" /></Grid>
            <Grid item xs={6}><TextField fullWidth label={t('palm.sold_offshoots')} type="number" value={formData.sold_offshoots} onChange={(e) => setFormData({...formData, sold_offshoots: e.target.value})} variant="filled" /></Grid>
          </Grid>
        </DialogContent>
        <DialogActions className="p-4">
          <Button onClick={() => setOpenModal(false)}>{t('palm.cancel')}</Button>
          <Button onClick={handleCreate} variant="contained" color="success" disabled={formLoading || !formData.plot || !formData.trees_count}>
            {formLoading ? <CircularProgress size={20} /> : t('palm.save')}
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};
export default PalmRecords;
