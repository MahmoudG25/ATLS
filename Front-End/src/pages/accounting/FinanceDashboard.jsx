import React, { useState, useEffect } from 'react';
import { Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField, CircularProgress, Alert, Grid, Paper, Box, Typography, useMediaQuery, useTheme } from '@mui/material';
import { getFinancialSummary, getExpenses, createExpense, getRevenues, createRevenue } from '../../features/accounting/services';
import { useTranslation } from 'react-i18next';

const FinanceDashboard = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { t } = useTranslation();
  const [summary, setSummary]   = useState(null);
  const [expenses, setExpenses] = useState([]);
  const [revenues, setRevenues] = useState([]);
  const [loading, setLoading]   = useState(true);

  const [modalType, setModalType]   = useState(null);
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError]   = useState('');
  const [formData, setFormData]     = useState({ amount: '', date: new Date().toISOString().split('T')[0], textRef: '', notes: '' });

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [s, e, r] = await Promise.all([getFinancialSummary(), getExpenses(), getRevenues()]);
      setSummary(s); setExpenses(e); setRevenues(r);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const handleSubmit = async () => {
    setFormLoading(true); setFormError('');
    try {
      if (modalType === 'expense') {
        await createExpense({ amount: formData.amount, date: formData.date, category: formData.textRef, notes: formData.notes });
      } else {
        await createRevenue({ amount: formData.amount, date: formData.date, source: formData.textRef });
      }
      setModalType(null); fetchData();
    } catch { setFormError(t('common.error')); }
    finally { setFormLoading(false); }
  };

  const openModal = (type) => {
    setModalType(type);
    setFormData({ amount: '', date: new Date().toISOString().split('T')[0], textRef: '', notes: '' });
  };

  return (
    <Box sx={{ p: { xs: 2, sm: 4, md: 8 }, maxWidth: '1280px', mx: 'auto' }}>
      <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, justifyContent: 'space-between', alignItems: { xs: 'flex-start', sm: 'center' }, mb: 4, gap: 2 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 800, color: 'slate.900', tracking: '-0.02em' }}>{t('accounting.title')}</Typography>
          <Typography variant="body1" sx={{ color: 'slate.500', mt: 0.5 }}>{t('accounting.subtitle')}</Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2, width: { xs: '100%', sm: 'auto' } }}>
          <Button fullWidth variant="outlined" color="error" onClick={() => openModal('expense')} sx={{ borderRadius: 2.5 }}>{t('accounting.log_expense')}</Button>
          <Button fullWidth variant="contained" color="success" onClick={() => openModal('revenue')} sx={{ borderRadius: 2.5 }}>{t('accounting.log_revenue')}</Button>
        </Box>
      </Box>

      {loading || !summary ? (
        <Box display="flex" justifyContent="center" py={4}>
          <CircularProgress sx={{ color: '#16a34a' }} />
        </Box>
      ) : (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 3, border: '1px solid #f1f5f9', borderRadius: 4 }} elevation={0}>
              <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 700 }}>{t('accounting.total_revenue')}</Typography>
              <Typography variant="h4" sx={{ fontWeight: 900, color: 'success.main', mt: 1 }}>${Number(summary.total_revenue).toLocaleString()}</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 3, border: '1px solid #f1f5f9', borderRadius: 4 }} elevation={0}>
              <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 700 }}>{t('accounting.total_expenses')}</Typography>
              <Typography variant="h4" sx={{ fontWeight: 900, color: 'error.main', mt: 1 }}>${Number(summary.total_expense).toLocaleString()}</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 3, border: '1px solid #f1f5f9', borderRadius: 4 }} elevation={0}>
              <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 700 }}>{t('accounting.total_salaries')}</Typography>
              <Typography variant="h4" sx={{ fontWeight: 900, color: 'warning.main', mt: 1 }}>${Number(summary.total_salaries).toLocaleString()}</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 3, bgcolor: 'slate.900', borderRadius: 4, color: 'white' }} elevation={0}>
              <Typography variant="caption" sx={{ color: 'slate.400', fontWeight: 700 }}>{t('accounting.net_margin')}</Typography>
              <Typography variant="h4" sx={{ fontWeight: 900, color: Number(summary.net) >= 0 ? 'success.light' : 'error.light', mt: 1 }}>${Number(summary.net).toLocaleString()}</Typography>
            </Paper>
          </Grid>
        </Grid>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Revenues */}
        <div>
          <h3 className="text-xl font-bold text-slate-800 mb-4">{t('accounting.inflow_title')}</h3>
          <div className="space-y-3">
            {revenues.slice(0, 10).map(r => (
              <div key={`rev-${r.id}`} className="bg-white border border-slate-100 p-4 rounded-xl flex justify-between shadow-sm">
                <div>
                  <p className="font-bold text-slate-700">{r.source}</p>
                  <p className="text-xs text-slate-400">{r.date}</p>
                </div>
                <div className="text-emerald-600 font-black">+${r.amount}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Expenses */}
        <div>
          <h3 className="text-xl font-bold text-slate-800 mb-4">{t('accounting.outflow_title')}</h3>
          <div className="space-y-3">
            {expenses.slice(0, 10).map(e => (
              <div key={`exp-${e.id}`} className="bg-white border border-slate-100 p-4 rounded-xl flex justify-between shadow-sm">
                <div>
                  <p className="font-bold text-slate-700">{e.category}</p>
                  <p className="text-xs text-slate-400">{e.date}</p>
                </div>
                <div className="text-rose-600 font-black">-${e.amount}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <Dialog open={!!modalType} onClose={() => setModalType(null)} maxWidth="sm" fullWidth fullScreen={isMobile}>
        <DialogTitle sx={{ fontWeight: 800 }}>{modalType === 'expense' ? t('accounting.modal_expense_title') : t('accounting.modal_revenue_title')}</DialogTitle>
        <DialogContent sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
          {formError && <Alert severity="error">{formError}</Alert>}
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth type="date" label={t('accounting.date')} value={formData.date} onChange={(e) => setFormData({...formData, date: e.target.value})} InputLabelProps={{ shrink: true }} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth type="number" label={t('accounting.amount')} value={formData.amount} onChange={(e) => setFormData({...formData, amount: e.target.value})} />
            </Grid>
          </Grid>
          <TextField fullWidth label={modalType === 'expense' ? t('accounting.expense_category') : t('accounting.revenue_source')} value={formData.textRef} onChange={(e) => setFormData({...formData, textRef: e.target.value})} />
          {modalType === 'expense' && <TextField fullWidth multiline rows={2} label={t('accounting.notes')} value={formData.notes} onChange={(e) => setFormData({...formData, notes: e.target.value})} />}
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setModalType(null)} sx={{ fontWeight: 700 }}>{t('accounting.cancel')}</Button>
          <Button onClick={handleSubmit} variant="contained" color="primary" disabled={formLoading || !formData.amount || !formData.textRef} sx={{ borderRadius: 2, px: 4 }}>{t('accounting.commit_btn')}</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
export default FinanceDashboard;
