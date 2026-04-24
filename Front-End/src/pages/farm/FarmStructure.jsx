import React, { useState, useEffect } from 'react';
import { SimpleTreeView, TreeItem } from '@mui/x-tree-view';
import { Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField, MenuItem, CircularProgress, Alert, Grid, Card } from '@mui/material';
import { getFarms, getCropTypes, getFarmStructure, createSector, createPlot, getPlotStats } from '../../features/farm/services';
import { useTranslation } from 'react-i18next';
import TerrainIcon  from '@mui/icons-material/Terrain';
import AutoGraphIcon from '@mui/icons-material/AutoGraph';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutlined';
import MapOutlinedIcon from '@mui/icons-material/MapOutlined';
import AccountTreeOutlinedIcon from '@mui/icons-material/AccountTreeOutlined';

const FarmStructure = () => {
  const { t } = useTranslation();
  const [structure, setStructure] = useState([]);
  const [farms, setFarms]         = useState([]);
  const [cropTypes, setCropTypes] = useState([]);
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState(null);

  const [activePlot, setActivePlot]   = useState(null);
  const [plotStats, setPlotStats]     = useState(null);
  const [loadingStats, setLoadingStats] = useState(false);

  const [openSectorModal, setOpenSectorModal] = useState(false);
  const [openPlotModal, setOpenPlotModal]     = useState(false);
  const [sectorForm, setSectorForm] = useState({ name: '', farm: '', crop_type: '' });
  const [plotForm, setPlotForm]     = useState({ name: '', sector: '', is_general: false });
  const [formLoading, setFormLoading] = useState(false);

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [farmsRes, cropsRes, structRes] = await Promise.all([getFarms(), getCropTypes(), getFarmStructure()]);
      setFarms(farmsRes); setCropTypes(cropsRes); setStructure(structRes);
    } catch { setError(t('farm.error_fetch')); }
    finally { setLoading(false); }
  };

  const fetchPlotDetails = async (plot) => {
    setActivePlot(plot); setLoadingStats(true);
    try { setPlotStats(await getPlotStats(plot.id)); }
    catch { setPlotStats(null); }
    finally { setLoadingStats(false); }
  };

  const handleCreateSector = async () => {
    setFormLoading(true);
    try { await createSector(sectorForm); setOpenSectorModal(false); fetchData(); }
    catch (err) { console.error(err); }
    finally { setFormLoading(false); }
  };

  const handleCreatePlot = async () => {
    setFormLoading(true);
    try { await createPlot(plotForm); setOpenPlotModal(false); fetchData(); }
    catch (err) { console.error(err); }
    finally { setFormLoading(false); }
  };

  if (loading) return <div className="p-8"><CircularProgress sx={{ color: '#16a34a' }} /></div>;

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-800 tracking-tight flex items-center gap-3">
            <div className="p-2 bg-green-50 rounded-xl text-green-600 flex items-center">
              <AccountTreeOutlinedIcon fontSize="large" />
            </div>
            {t('farm.title', 'هيكل المزرعة')}
          </h1>
          <p className="text-slate-500 mt-2 font-medium">{t('farm.subtitle', 'إدارة القطاعات والحقول الجغرافية')}</p>
        </div>
        <div className="flex gap-3 w-full sm:w-auto">
          <Button 
            fullWidth={false}
            variant="outlined" 
            startIcon={<AddCircleOutlineIcon />}
            onClick={() => setOpenSectorModal(true)}
            sx={{ borderRadius: 3, px: 3, py: 1, fontWeight: 700, borderColor: '#16a34a', color: '#16a34a', '&:hover': { borderColor: '#15803d', bgcolor: '#f0fdf4' } }}
          >
            {t('farm.add_sector', 'إضافة قطاع')}
          </Button>
          <Button 
            fullWidth={false}
            variant="contained" 
            startIcon={<TerrainIcon />}
            onClick={() => setOpenPlotModal(true)}
            sx={{ borderRadius: 3, px: 3, py: 1, fontWeight: 700, bgcolor: '#16a34a', '&:hover': { bgcolor: '#15803d' }, boxShadow: '0 4px 14px 0 rgba(22, 163, 74, 0.39)' }}
          >
            {t('farm.add_plot', 'إضافة حقل')}
          </Button>
        </div>
      </div>

      {error && <Alert severity="error" className="mb-6">{error}</Alert>}

      <Grid container spacing={6}>
        <Grid item xs={12} md={7}>
          <Card sx={{ p: 3, bgcolor: 'white', borderRadius: 4, border: '1px solid #e2e8f0', boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.05)', minHeight: '400px' }}>
            {structure.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full pt-16 pb-8">
                <AccountTreeOutlinedIcon sx={{ fontSize: 64, color: '#cbd5e1', mb: 2 }} />
                <p className="text-slate-400 font-semibold text-center">{t('farm.no_sectors', 'لا توجد قطاعات مسجلة')}</p>
              </div>
            ) : (
              <SimpleTreeView sx={{ '& .MuiTreeItem-root': { mb: 1 } }}>
                {structure.map((sector) => (
                  <TreeItem key={`sec-${sector.id}`} itemId={`sec-${sector.id}`}
                    label={<div className="font-bold text-slate-800 py-1.5 text-[1.05rem]">{sector.name} <span className="text-[0.65rem] font-bold text-green-700 bg-green-100 px-2 py-0.5 rounded-full ml-3">{sector.crop_type_name}</span></div>}>
                    {sector.plots.map((plot) => (
                      <TreeItem key={`plot-${plot.id}`} itemId={`plot-${plot.id}`}
                        onClick={(e) => { e.stopPropagation(); fetchPlotDetails(plot); }}
                        label={<div className="text-slate-600 font-semibold flex items-center gap-2 py-1.5 px-3 hover:bg-slate-50 rounded-xl transition-colors">{plot.name} {plot.is_general && <span className="text-[0.65rem] bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded-md">{t('farm.general_badge', 'عام')}</span>}</div>}
                      />
                    ))}
                  </TreeItem>
                ))}
              </SimpleTreeView>
            )}
          </Card>
        </Grid>

        <Grid item xs={12} md={5}>
          {activePlot ? (
            <Card sx={{ p: 4, borderRadius: 4, border: '1px solid #e2e8f0', boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.05)', position: 'sticky', top: 32 }}>
              <h3 className="text-2xl font-black text-slate-800 mb-1">{activePlot.name}</h3>
              <p className="text-xs font-bold tracking-widest text-green-600 uppercase mb-6">{t('farm.sector_coordinates', 'إحصائيات الحقل')}</p>
              {loadingStats ? (
                <div className="flex justify-center p-8"><CircularProgress sx={{ color: '#16a34a' }} /></div>
              ) : (
                <div className="space-y-4">
                  <div className="bg-slate-50 p-5 border border-slate-100 rounded-3xl flex items-center gap-5 transition-transform hover:-translate-y-1">
                    <div className="w-14 h-14 rounded-2xl bg-green-100 text-green-600 flex items-center justify-center shrink-0"><TerrainIcon fontSize="medium" /></div>
                    <div>
                      <p className="text-[0.7rem] text-slate-400 font-bold uppercase tracking-wider">{t('farm.trees_count', 'عدد الأشجار')}</p>
                      <p className="text-3xl font-black text-slate-800">{plotStats?.total_trees || 0} <span className="text-sm font-semibold text-slate-500">{t('farm.trunks', 'جذع')}</span></p>
                    </div>
                  </div>
                  <div className="bg-slate-50 p-5 border border-slate-100 rounded-3xl flex items-center gap-5 transition-transform hover:-translate-y-1">
                    <div className="w-14 h-14 rounded-2xl bg-indigo-100 text-indigo-600 flex items-center justify-center shrink-0"><AutoGraphIcon fontSize="medium" /></div>
                    <div>
                      <p className="text-[0.7rem] text-slate-400 font-bold uppercase tracking-wider">{t('farm.lifetime_yield', 'الإنتاج التراكمي')}</p>
                      <p className="text-3xl font-black text-slate-800">{parseFloat(plotStats?.lifetime_yield || 0).toLocaleString()} <span className="text-sm font-semibold text-slate-500">{t('farm.tonnes', 'طن')}</span></p>
                    </div>
                  </div>
                </div>
              )}
            </Card>
          ) : (
            <Card sx={{ borderRadius: 4, border: '1px dashed #cbd5e1', bgcolor: '#f8fafc', boxShadow: 'none', height: '100%', minHeight: '400px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', p: 4, textAlign: 'center' }}>
              <MapOutlinedIcon sx={{ fontSize: 64, color: '#cbd5e1', mb: 2 }} />
              <p className="text-slate-400 font-semibold">{t('farm.plot_hint', 'حدد حقلاً من القائمة لعرض تفاصيله وإحصائياته')}</p>
            </Card>
          )}
        </Grid>
      </Grid>

      {/* SECTOR MODAL */}
      <Dialog open={openSectorModal} onClose={() => setOpenSectorModal(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 3 } }}>
        <DialogTitle sx={{ fontWeight: 800, pb: 1 }}>{t('farm.add_sector_title', 'إضافة قطاع جديد')}</DialogTitle>
        <DialogContent className="space-y-5 pt-2">
          <TextField select fullWidth label={t('farm.select_farm', 'تحديد المزرعة')} value={sectorForm.farm} onChange={(e) => setSectorForm({...sectorForm, farm: e.target.value})} className="mt-2" variant="outlined" InputProps={{ sx: { borderRadius: 2 } }}>
            {farms.map((f) => <MenuItem key={f.id} value={f.id} sx={{ fontWeight: 600 }}>{f.name}</MenuItem>)}
          </TextField>
          <TextField fullWidth label={t('farm.sector_name', 'اسم القطاع')} value={sectorForm.name} onChange={(e) => setSectorForm({...sectorForm, name: e.target.value})} variant="outlined" InputProps={{ sx: { borderRadius: 2 } }} />
          <TextField select fullWidth label={t('farm.crop_type', 'نوع المحصول')} value={sectorForm.crop_type} onChange={(e) => setSectorForm({...sectorForm, crop_type: e.target.value})} variant="outlined" InputProps={{ sx: { borderRadius: 2 } }}>
            {cropTypes.map((c) => <MenuItem key={c.id} value={c.id} sx={{ fontWeight: 600 }}>{c.name}</MenuItem>)}
          </TextField>
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setOpenSectorModal(false)} sx={{ fontWeight: 700 }}>{t('farm.cancel', 'إلغاء')}</Button>
          <Button onClick={handleCreateSector} variant="contained" disabled={formLoading || !sectorForm.name || !sectorForm.farm || !sectorForm.crop_type} sx={{ borderRadius: 2, px: 4, fontWeight: 700, bgcolor: '#16a34a', '&:hover': { bgcolor: '#15803d' } }}>
            {formLoading ? <CircularProgress size={20} /> : t('farm.save_sector', 'حفظ القطاع')}
          </Button>
        </DialogActions>
      </Dialog>

      {/* PLOT MODAL */}
      <Dialog open={openPlotModal} onClose={() => setOpenPlotModal(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 3 } }}>
        <DialogTitle sx={{ fontWeight: 800, pb: 1 }}>{t('farm.add_plot_title', 'إضافة حقل جديد')}</DialogTitle>
        <DialogContent className="space-y-5 pt-2">
          <TextField select fullWidth label={t('farm.parent_sector', 'القطاع التابع')} value={plotForm.sector} onChange={(e) => setPlotForm({...plotForm, sector: e.target.value})} className="mt-2" variant="outlined" InputProps={{ sx: { borderRadius: 2 } }}>
            {structure.map((s) => <MenuItem key={s.id} value={s.id} sx={{ fontWeight: 600 }}>{s.name} ({s.crop_type_name})</MenuItem>)}
          </TextField>
          <TextField fullWidth label={t('farm.plot_name', 'اسم الحقل')} value={plotForm.name} onChange={(e) => setPlotForm({...plotForm, name: e.target.value})} variant="outlined" InputProps={{ sx: { borderRadius: 2 } }} />
          <TextField select fullWidth label={t('farm.plot_type', 'نوع الحقل')} value={plotForm.is_general} onChange={(e) => setPlotForm({...plotForm, is_general: e.target.value})} variant="outlined" InputProps={{ sx: { borderRadius: 2 } }}>
            <MenuItem value={false} sx={{ fontWeight: 600 }}>{t('farm.plot_specific', 'محصول محدد')}</MenuItem>
            <MenuItem value={true} sx={{ fontWeight: 600 }}>{t('farm.plot_general', 'مرافق عامة')}</MenuItem>
          </TextField>
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setOpenPlotModal(false)} sx={{ fontWeight: 700 }}>{t('farm.cancel', 'إلغاء')}</Button>
          <Button onClick={handleCreatePlot} variant="contained" disabled={formLoading || !plotForm.name || !plotForm.sector} sx={{ borderRadius: 2, px: 4, fontWeight: 700, bgcolor: '#16a34a', '&:hover': { bgcolor: '#15803d' } }}>
            {formLoading ? <CircularProgress size={20} /> : t('farm.save_plot', 'حفظ الحقل')}
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default FarmStructure;
