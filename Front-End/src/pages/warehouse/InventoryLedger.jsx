import React, { useState, useEffect } from 'react';
import { Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField, CircularProgress, Alert, Table, TableBody, TableCell, TableHead, TableRow, Paper, TableContainer, MenuItem, Grid, Chip, Box, Typography, useMediaQuery, useTheme, Card } from '@mui/material';
import { getItems, getMovements, createItem, createMovement } from '../../features/warehouse/services';
import { useTranslation } from 'react-i18next';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import SyncAltIcon from '@mui/icons-material/SyncAlt';
import Inventory2OutlinedIcon from '@mui/icons-material/Inventory2Outlined';
import ReceiptLongOutlinedIcon from '@mui/icons-material/ReceiptLongOutlined';

const InventoryLedger = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { t } = useTranslation();
  const [items, setItems]         = useState([]);
  const [movements, setMovements] = useState([]);
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState(null);

  const [openItemModal, setOpenItemModal]         = useState(false);
  const [openMovementModal, setOpenMovementModal] = useState(false);
  const [formLoading, setFormLoading]             = useState(false);
  const [formError, setFormError]                 = useState('');

  const [itemForm, setItemForm]         = useState({ name: '', category: 'tools' });
  const [movementForm, setMovementForm] = useState({ item: '', movement_type: 'IN', quantity: '' });

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [i, m] = await Promise.all([getItems(), getMovements()]);
      setItems(i); setMovements(m);
    } catch { setError(t('warehouse.error_fetch')); }
    finally { setLoading(false); }
  };

  const handleCreateItem = async () => {
    setFormLoading(true); setFormError('');
    try { await createItem(itemForm); setOpenItemModal(false); fetchData(); }
    catch (err) { setFormError(Object.values(err.response?.data || {}).flat().join(', ') || t('common.error')); }
    finally { setFormLoading(false); }
  };

  const handleCreateMovement = async () => {
    setFormLoading(true); setFormError('');
    try { await createMovement(movementForm); setOpenMovementModal(false); fetchData(); }
    catch (err) { setFormError(err.response?.data ? Object.values(err.response.data).flat().join(', ') : t('common.error')); }
    finally { setFormLoading(false); }
  };

  const CAT_COLORS = {
    pesticides:  { bg: '#fecdd3', color: '#9f1239' },
    fertilizers: { bg: '#dcfce7', color: '#166534' },
    tools:       { bg: '#e0f2fe', color: '#075985' },
  };

  return (
    <Box sx={{ p: { xs: 2, sm: 4, md: 8 }, maxWidth: '1280px', mx: 'auto' }}>
      <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, justifyContent: 'space-between', alignItems: { xs: 'flex-start', sm: 'center' }, mb: 4, gap: 2 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 900, color: '#1e293b', letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Box sx={{ p: 1, bgcolor: '#f0fdf4', borderRadius: 2, display: 'flex', color: '#16a34a' }}>
              <Inventory2OutlinedIcon fontSize="large" />
            </Box>
            {t('warehouse.title', 'المستودع')}
          </Typography>
          <Typography variant="body1" sx={{ color: '#64748b', mt: 1, fontWeight: 500 }}>{t('warehouse.subtitle', 'إدارة الكميات المخزنة عبر قيود التوريد.')}</Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2, width: { xs: '100%', sm: 'auto' } }}>
          <Button 
            fullWidth 
            variant="outlined" 
            startIcon={<AddCircleOutlineIcon />}
            onClick={() => setOpenItemModal(true)} 
            sx={{ borderRadius: 3, px: 3, py: 1, fontWeight: 700, borderColor: '#16a34a', color: '#16a34a', '&:hover': { borderColor: '#15803d', bgcolor: '#f0fdf4' } }}
          >
            {t('warehouse.register_item', 'تسجيل صنف')}
          </Button>
          <Button 
            fullWidth 
            variant="contained" 
            startIcon={<SyncAltIcon />}
            onClick={() => setOpenMovementModal(true)} 
            sx={{ borderRadius: 3, px: 3, py: 1, fontWeight: 700, bgcolor: '#16a34a', '&:hover': { bgcolor: '#15803d' }, boxShadow: '0 4px 14px 0 rgba(22, 163, 74, 0.39)' }}
          >
            {t('warehouse.add_movement', 'إضافة حركة')}
          </Button>
        </Box>
      </Box>

      {error && <Alert severity="error">{error}</Alert>}

      <Grid container spacing={4}>
        {/* Stock Matrix */}
        <Grid item xs={12} lg={6}>
          <Card sx={{ p: 0, bgcolor: 'white', borderRadius: 4, border: '1px solid #e2e8f0', boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01)', overflow: 'hidden' }}>
            <Box sx={{ p: 3, borderBottom: '1px solid #f1f5f9', display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Typography variant="h6" sx={{ fontWeight: 800, color: '#0f172a' }}>{t('warehouse.stock_matrix', 'جرد المخزون')}</Typography>
            </Box>
            {loading ? <Box sx={{ p: 8, textAlign: 'center' }}><CircularProgress sx={{ color: '#16a34a' }} /></Box> : (
              <Box sx={{ overflowX: 'auto' }}>
                <TableContainer elevation={0}>
                  <Table size={isMobile ? 'small' : 'medium'}>
                    <TableHead>
                      <TableRow sx={{ bgcolor: '#f8fafc' }}>
                        <TableCell sx={{ fontWeight: 700, color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase', py: 2 }}>{t('warehouse.col_item', 'الصنف')}</TableCell>
                        <TableCell sx={{ fontWeight: 700, color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase', py: 2 }}>{t('warehouse.col_category', 'الفئة')}</TableCell>
                        <TableCell align="right" sx={{ fontWeight: 700, color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase', py: 2 }}>{t('warehouse.col_stock', 'المخزون الحالي')}</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {items.length === 0
                        ? <TableRow><TableCell colSpan={3} align="center" sx={{ py: 8 }}><Inventory2OutlinedIcon sx={{ fontSize: 48, color: '#cbd5e1', mb: 2 }} /><Typography sx={{ fontWeight: 600, color: '#94a3b8' }}>{t('warehouse.empty_catalog', 'المستودع فارغ')}</Typography></TableCell></TableRow>
                        : items.map(idx => (
                          <TableRow key={idx.id} hover sx={{ '&:last-child td, &:last-child th': { border: 0 }, '&:hover': { bgcolor: '#f8fafc' } }}>
                            <TableCell sx={{ fontWeight: 700, color: '#334155' }}>{idx.name}</TableCell>
                            <TableCell>
                              <Chip 
                                label={t(`warehouse.cat_${idx.category}`) || idx.category} 
                                size="small"
                                sx={{ 
                                  fontWeight: 700, 
                                  fontSize: '0.7rem',
                                  background: CAT_COLORS[idx.category]?.bg, 
                                  color: CAT_COLORS[idx.category]?.color,
                                  borderRadius: 1.5, px: 1
                                }} 
                              />
                            </TableCell>
                            <TableCell align="right" sx={{ fontWeight: 900, color: '#16a34a', fontSize: '1rem' }}>{parseFloat(idx.quantity).toLocaleString()}</TableCell>
                          </TableRow>
                        ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}
          </Card>
        </Grid>

        {/* Movements Ledger */}
        <Grid item xs={12} lg={6}>
          <Card sx={{ p: 0, bgcolor: 'white', borderRadius: 4, border: '1px solid #e2e8f0', boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01)', overflow: 'hidden', display: 'flex', flexDirection: 'column', height: '100%' }}>
            <Box sx={{ p: 3, borderBottom: '1px solid #f1f5f9', display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Typography variant="h6" sx={{ fontWeight: 800, color: '#0f172a' }}>{t('warehouse.movements_log', 'آخر الحركات')}</Typography>
            </Box>
            {loading ? <Box sx={{ p: 8, textAlign: 'center' }}><CircularProgress sx={{ color: '#16a34a' }} /></Box> : (
              <Box sx={{ overflowX: 'auto', flexGrow: 1, maxHeight: { xs: 400, lg: 'none' }, '&::-webkit-scrollbar': { width: '6px', height: '6px' }, '&::-webkit-scrollbar-thumb': { bgcolor: '#cbd5e1', borderRadius: '3px' } }}>
                <TableContainer elevation={0}>
                  <Table stickyHeader size={isMobile ? 'small' : 'medium'}>
                    <TableHead>
                      <TableRow>
                        <TableCell sx={{ fontWeight: 700, color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase', py: 2, bgcolor: '#f8fafc' }}>{t('warehouse.col_target', 'الصنف')}</TableCell>
                        <TableCell sx={{ fontWeight: 700, color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase', py: 2, bgcolor: '#f8fafc' }}>{t('warehouse.col_event', 'العملية')}</TableCell>
                        <TableCell align="right" sx={{ fontWeight: 700, color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase', py: 2, bgcolor: '#f8fafc' }}>{t('warehouse.col_qty', 'الكمية')}</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {movements.length === 0
                        ? <TableRow><TableCell colSpan={3} align="center" sx={{ py: 8 }}><ReceiptLongOutlinedIcon sx={{ fontSize: 48, color: '#cbd5e1', mb: 2 }} /><Typography sx={{ fontWeight: 600, color: '#94a3b8' }}>{t('warehouse.no_movements', 'لا توجد حركات')}</Typography></TableCell></TableRow>
                        : movements.map((mov, i) => (
                          <TableRow key={mov.id || i} hover sx={{ '&:last-child td, &:last-child th': { border: 0 }, '&:hover': { bgcolor: '#f8fafc' } }}>
                            <TableCell sx={{ fontSize: '0.9rem', fontWeight: 700, color: '#334155' }}>{mov.item_name}</TableCell>
                            <TableCell>
                              <Chip 
                                label={mov.movement_type === 'IN' ? 'وارد' : 'صادر'} 
                                size="small" 
                                sx={{ 
                                  fontWeight: 800, 
                                  fontSize: '0.65rem',
                                  color: mov.movement_type === 'IN' ? '#047857' : '#be123c',
                                  bgcolor: mov.movement_type === 'IN' ? '#d1fae5' : '#ffe4e6',
                                  borderRadius: 1.5, px: 0.5
                                }} 
                              />
                            </TableCell>
                            <TableCell align="right" sx={{ fontWeight: 900, fontSize: '1rem', color: mov.movement_type === 'IN' ? '#16a34a' : '#ef4444' }}>
                              {mov.movement_type === 'IN' ? '+' : '-'}{parseFloat(mov.quantity).toLocaleString()}
                            </TableCell>
                          </TableRow>
                        ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}
          </Card>
        </Grid>
      </Grid>

      {/* ITEM MODAL */}
      <Dialog open={openItemModal} onClose={() => setOpenItemModal(false)} maxWidth="sm" fullWidth fullScreen={isMobile}>
        <DialogTitle sx={{ fontWeight: 800 }}>{t('warehouse.item_modal_title')}</DialogTitle>
        <DialogContent sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
          {formError && <Alert severity="error">{formError}</Alert>}
          <TextField fullWidth label={t('warehouse.item_name')} value={itemForm.name} onChange={(e) => setItemForm({...itemForm, name: e.target.value})} />
          <TextField select fullWidth label={t('warehouse.item_category')} value={itemForm.category} onChange={(e) => setItemForm({...itemForm, category: e.target.value})}>
            <MenuItem value="tools">{t('warehouse.cat_tools')}</MenuItem>
            <MenuItem value="pesticides">{t('warehouse.cat_pesticides')}</MenuItem>
            <MenuItem value="fertilizers">{t('warehouse.cat_fertilizers')}</MenuItem>
          </TextField>
          <Typography variant="caption" sx={{ color: 'text.secondary', fontStyle: 'italic' }}>{t('warehouse.item_note')}</Typography>
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setOpenItemModal(false)} sx={{ fontWeight: 700 }}>{t('warehouse.cancel')}</Button>
          <Button onClick={handleCreateItem} variant="contained" disabled={formLoading || !itemForm.name} sx={{ borderRadius: 2, px: 4 }}>{t('warehouse.register_btn')}</Button>
        </DialogActions>
      </Dialog>

      {/* MOVEMENT MODAL */}
      <Dialog open={openMovementModal} onClose={() => setOpenMovementModal(false)} maxWidth="sm" fullWidth fullScreen={isMobile}>
        <DialogTitle sx={{ fontWeight: 800 }}>{t('warehouse.movement_modal_title')}</DialogTitle>
        <DialogContent sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
          {formError && <Alert severity="error">{formError}</Alert>}
          <TextField select fullWidth label={t('warehouse.movement_item')} value={movementForm.item} onChange={(e) => setMovementForm({...movementForm, item: e.target.value})}>
            {items.map(i => <MenuItem key={i.id} value={i.id}>{i.name} ({i.quantity})</MenuItem>)}
          </TextField>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <TextField select fullWidth label={t('warehouse.movement_type')} value={movementForm.movement_type} onChange={(e) => setMovementForm({...movementForm, movement_type: e.target.value})}
                sx={{ '& .MuiInputBase-input': { color: movementForm.movement_type === 'OUT' ? 'error.main' : 'success.main', fontWeight: 800 } }}>
                <MenuItem value="IN">{t('warehouse.movement_in')}</MenuItem>
                <MenuItem value="OUT">{t('warehouse.movement_out')}</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth type="number" label={t('warehouse.movement_qty')} value={movementForm.quantity} onChange={(e) => setMovementForm({...movementForm, quantity: e.target.value})} />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setOpenMovementModal(false)} sx={{ fontWeight: 700 }}>{t('warehouse.cancel')}</Button>
          <Button onClick={handleCreateMovement} variant="contained" disabled={formLoading || !movementForm.item || !movementForm.quantity}
            sx={{ borderRadius: 2, px: 4, background: movementForm.movement_type === 'IN' ? '#10b981' : '#f43f5e' }}>
            {t('warehouse.commit_btn')}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
export default InventoryLedger;
