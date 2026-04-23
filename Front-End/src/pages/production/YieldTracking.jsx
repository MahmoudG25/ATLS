import React, { useState, useEffect } from 'react';
import { Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField, CircularProgress, Alert, Table, TableBody, TableCell, TableHead, TableRow, Paper, TableContainer, MenuItem, Grid } from '@mui/material';
import { getYields, createYield } from '../../features/production/services';
import { getFarmStructure } from '../../features/farm/services';
import { useTranslation } from 'react-i18next';

const YieldTracking = () => {
  const { t } = useTranslation();
  const [yields, setYields]       = useState([]);
  const [structure, setStructure] = useState([]);
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState(null);

  const [openModal, setOpenModal]     = useState(false);
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError]     = useState('');

  const [formData, setFormData] = useState({
    plot: '', year: new Date().getFullYear(), production_amount: ''
  });

  useEffect(() => { fetchInitialData(); }, []);

  const fetchInitialData = async () => {
    setLoading(true);
    try {
      const [y, struct] = await Promise.all([getYields(), getFarmStructure()]);
      setYields(y); setStructure(struct);
    } catch { setError(t('production.error_fetch')); }
    finally { setLoading(false); }
  };

  const handleCreate = async () => {
    setFormLoading(true); setFormError('');
    try { await createYield(formData); setOpenModal(false); fetchInitialData(); }
    catch (err) {
      if (err.response?.data) setFormError(Object.values(err.response.data).flat().join(', '));
      else setFormError(t('common.error'));
    } finally { setFormLoading(false); }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">{t('production.title')}</h1>
          <p className="text-slate-500 mt-1">{t('production.subtitle')}</p>
        </div>
        <Button variant="contained" onClick={() => setOpenModal(true)} sx={{ background: '#0f172a' }}>{t('production.add_btn')}</Button>
      </div>

      {error && <Alert severity="error">{error}</Alert>}

      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-2">
        {loading ? <div className="p-6"><CircularProgress sx={{ color: '#16a34a' }} /></div> : (
          <TableContainer component={Paper} elevation={0}>
            <Table>
              <TableHead sx={{ backgroundColor: '#f8fafc' }}>
                <TableRow>
                  <TableCell sx={{ fontWeight: 700, color: '#475569' }}>{t('production.col_location')}</TableCell>
                  <TableCell sx={{ fontWeight: 700, color: '#475569' }}>{t('production.col_year')}</TableCell>
                  <TableCell sx={{ fontWeight: 700, color: '#475569', textAlign: 'right' }}>{t('production.col_production')}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {yields.length === 0 ? (
                  <TableRow><TableCell colSpan={3} className="text-center text-slate-400 py-8">{t('production.no_data')}</TableCell></TableRow>
                ) : yields.map((row) => (
                  <TableRow key={row.id}>
                    <TableCell>
                      <div className="font-bold text-slate-800">{row.plot_name}</div>
                      <div className="text-xs text-slate-400">{row.sector_name}</div>
                    </TableCell>
                    <TableCell className="font-medium text-indigo-700">{row.year}</TableCell>
                    <TableCell align="right" className="font-black text-slate-700">{row.production_amount}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </div>

      <Dialog open={openModal} onClose={() => setOpenModal(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{t('production.modal_title')}</DialogTitle>
        <DialogContent className="pt-4 space-y-4">
          {formError && <Alert severity="error">{formError}</Alert>}
          <TextField select fullWidth label={t('production.plot_label')} value={formData.plot} onChange={(e) => setFormData({...formData, plot: e.target.value})} variant="filled">
            {structure.flatMap(s => s.plots.map(p => <MenuItem key={p.id} value={p.id}>{p.name} - ({s.name})</MenuItem>))}
          </TextField>
          <Grid container spacing={2}>
            <Grid item xs={6}><TextField fullWidth type="number" label={t('production.year_label')} value={formData.year} onChange={(e) => setFormData({...formData, year: e.target.value})} variant="filled" /></Grid>
            <Grid item xs={6}><TextField fullWidth type="number" label={t('production.qty_label')} value={formData.production_amount} onChange={(e) => setFormData({...formData, production_amount: e.target.value})} variant="filled" /></Grid>
          </Grid>
          <div className="text-xs text-slate-400 italic">{t('production.note')}</div>
        </DialogContent>
        <DialogActions className="p-4">
          <Button onClick={() => setOpenModal(false)}>{t('production.cancel')}</Button>
          <Button onClick={handleCreate} variant="contained" disabled={formLoading || !formData.plot || !formData.production_amount}>{t('production.save_btn')}</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};
export default YieldTracking;
