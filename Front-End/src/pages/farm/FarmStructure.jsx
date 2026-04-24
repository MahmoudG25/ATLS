import React, { useState, useEffect } from 'react';
import { Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField, MenuItem, CircularProgress, Alert, Grid, Card, Drawer, IconButton, Box } from '@mui/material';
import { getFarms, getCropTypes, getFarmStructure, createSector, createPlot, getPlotStats } from '../../features/farm/services';
import { useTranslation } from 'react-i18next';
import TerrainIcon  from '@mui/icons-material/Terrain';
import AutoGraphIcon from '@mui/icons-material/AutoGraph';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutlined';
import MapOutlinedIcon from '@mui/icons-material/MapOutlined';
import AccountTreeOutlinedIcon from '@mui/icons-material/AccountTreeOutlined';
import CloseIcon from '@mui/icons-material/Close';
import './FarmStructure.css';

const OrgNode = ({ title, subtitle, isRoot, isSector, active, onClick, badge }) => (
  <div 
    onClick={onClick}
    className={`relative flex flex-col items-center justify-center px-4 py-3 rounded-lg border cursor-pointer transition-all ${
      active 
        ? 'border-green-600 bg-green-50 shadow-sm ring-1 ring-green-600 z-10' 
        : 'border-slate-200 bg-white hover:border-slate-300 hover:shadow-sm z-0'
    }`}
    style={{ minWidth: '150px' }}
    dir="rtl"
  >
    {badge && <span className="absolute -top-2.5 -right-2 bg-slate-800 text-white text-[0.65rem] px-2 py-0.5 rounded shadow-sm tracking-wide">{badge}</span>}
    <div className={`w-10 h-10 rounded-md flex items-center justify-center mb-2 ${isRoot ? 'bg-slate-800 text-white shadow-sm' : isSector ? 'bg-slate-100 text-slate-700' : 'bg-slate-50 text-slate-500'}`}>
      {isRoot ? <AccountTreeOutlinedIcon fontSize="small" /> : isSector ? <AutoGraphIcon fontSize="small" /> : <TerrainIcon fontSize="small" />}
    </div>
    <p className="font-semibold text-slate-800 text-sm tracking-tight">{title}</p>
    {subtitle && <p className="text-[0.7rem] font-medium text-slate-500 mt-1">{subtitle}</p>}
  </div>
);

const FarmStructure = () => {
  const { t, i18n } = useTranslation();
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
    <div className="p-8 w-full">
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

      <Card sx={{ p: 4, bgcolor: 'white', borderRadius: 3, border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)', width: '100%', minHeight: '600px', display: 'flex', flexDirection: 'column' }}>
        {structure.length === 0 ? (
          <div className="flex flex-col items-center justify-center flex-grow pt-16 pb-8">
            <AccountTreeOutlinedIcon sx={{ fontSize: 64, color: '#cbd5e1', mb: 2 }} />
            <p className="text-slate-400 font-semibold text-center">{t('farm.no_sectors', 'لا توجد قطاعات مسجلة')}</p>
          </div>
        ) : (
          <div className="org-tree-container flex-grow">
            <div className="org-tree">
              <ul>
                <li>
                  <OrgNode 
                    title={t('farm.main_farm', 'المزرعة الرئيسية')} 
                    isRoot={true} 
                    active={!activePlot}
                    onClick={() => setActivePlot(null)}
                  />
                  <ul>
                    {structure.map((sector) => (
                      <li key={`sec-${sector.id}`}>
                        <OrgNode 
                          title={sector.name} 
                          subtitle={sector.crop_type_name} 
                          isSector={true} 
                        />
                        {sector.plots && sector.plots.length > 0 && (
                          <ul>
                            {sector.plots.map((plot) => (
                              <li key={`plot-${plot.id}`}>
                                <OrgNode 
                                  title={plot.name} 
                                  badge={plot.is_general ? t('farm.general_badge', 'عام') : null}
                                  active={activePlot?.id === plot.id}
                                  onClick={(e) => { e.stopPropagation(); fetchPlotDetails(plot); }}
                                />
                              </li>
                            ))}
                          </ul>
                        )}
                      </li>
                    ))}
                  </ul>
                </li>
              </ul>
            </div>
          </div>
        )}
      </Card>

      {/* PLOT DETAILS DRAWER */}
      <Drawer
        anchor={i18n.language === 'ar' ? 'left' : 'right'}
        open={!!activePlot}
        onClose={() => setActivePlot(null)}
        PaperProps={{ sx: { width: { xs: '100%', sm: 400 }, p: 0, bgcolor: '#f8fafc' } }}
      >
        {activePlot && (
          <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <Box sx={{ p: 3, borderBottom: '1px solid #e2e8f0', bgcolor: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box>
                <h3 className="text-xl font-bold text-slate-800 mb-1">{activePlot.name}</h3>
                <p className="text-xs font-semibold tracking-widest text-green-600 uppercase">{t('farm.sector_coordinates', 'إحصائيات الحقل')}</p>
              </Box>
              <IconButton onClick={() => setActivePlot(null)} size="small" sx={{ bgcolor: '#f1f5f9', color: '#64748b', '&:hover': { bgcolor: '#e2e8f0' } }}>
                <CloseIcon fontSize="small" />
              </IconButton>
            </Box>
            
            <Box sx={{ p: 3, flexGrow: 1, overflowY: 'auto' }}>
              {loadingStats ? (
                <div className="flex justify-center p-8"><CircularProgress sx={{ color: '#16a34a' }} /></div>
              ) : (
                <div className="space-y-4">
                  <div className="bg-white p-5 border border-slate-200 rounded-xl flex items-center gap-4 shadow-sm">
                    <div className="w-12 h-12 rounded-lg bg-green-50 text-green-600 flex items-center justify-center shrink-0 border border-green-100">
                      <TerrainIcon fontSize="medium" />
                    </div>
                    <div>
                      <p className="text-[0.65rem] text-slate-400 font-bold uppercase tracking-wider">{t('farm.trees_count', 'عدد الأشجار')}</p>
                      <p className="text-2xl font-bold text-slate-800">{plotStats?.total_trees || 0} <span className="text-xs font-medium text-slate-500">{t('farm.trunks', 'جذع')}</span></p>
                    </div>
                  </div>
                  <div className="bg-white p-5 border border-slate-200 rounded-xl flex items-center gap-4 shadow-sm">
                    <div className="w-12 h-12 rounded-lg bg-slate-50 text-slate-600 flex items-center justify-center shrink-0 border border-slate-100">
                      <AutoGraphIcon fontSize="medium" />
                    </div>
                    <div>
                      <p className="text-[0.65rem] text-slate-400 font-bold uppercase tracking-wider">{t('farm.lifetime_yield', 'الإنتاج التراكمي')}</p>
                      <p className="text-2xl font-bold text-slate-800">{parseFloat(plotStats?.lifetime_yield || 0).toLocaleString()} <span className="text-xs font-medium text-slate-500">{t('farm.tonnes', 'طن')}</span></p>
                    </div>
                  </div>
                </div>
              )}
            </Box>
          </Box>
        )}
      </Drawer>

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
