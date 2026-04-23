import React, { useState, useEffect } from 'react';
import { SimpleTreeView, TreeItem } from '@mui/x-tree-view';
import { Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField, MenuItem, CircularProgress, Alert, Grid, Card } from '@mui/material';
import { getFarms, getCropTypes, getFarmStructure, createSector, createPlot, getPlotStats } from '../../features/farm/services';
import { useTranslation } from 'react-i18next';
import TerrainIcon  from '@mui/icons-material/Terrain';
import AutoGraphIcon from '@mui/icons-material/AutoGraph';

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
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-800 tracking-tight">{t('farm.title')}</h1>
          <p className="text-slate-500 mt-1">{t('farm.subtitle')}</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outlined" color="primary" onClick={() => setOpenSectorModal(true)}>{t('farm.add_sector')}</Button>
          <Button variant="contained" color="primary" onClick={() => setOpenPlotModal(true)}>{t('farm.add_plot')}</Button>
        </div>
      </div>

      {error && <Alert severity="error" className="mb-4">{error}</Alert>}

      <Grid container spacing={6}>
        <Grid item xs={12} md={7}>
          <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 min-h-[400px]">
            {structure.length === 0 ? (
              <p className="text-slate-400 italic text-center mt-12">{t('farm.no_sectors')}</p>
            ) : (
              <SimpleTreeView>
                {structure.map((sector) => (
                  <TreeItem key={`sec-${sector.id}`} itemId={`sec-${sector.id}`}
                    label={<div className="font-semibold text-slate-700 py-1">{sector.name} <span className="text-xs text-green-600 bg-green-50 px-2 py-0.5 rounded-full ml-2">{sector.crop_type_name}</span></div>}>
                    {sector.plots.map((plot) => (
                      <TreeItem key={`plot-${plot.id}`} itemId={`plot-${plot.id}`}
                        onClick={(e) => { e.stopPropagation(); fetchPlotDetails(plot); }}
                        label={<div className="text-slate-600 flex items-center gap-2 py-1 px-2 hover:bg-slate-50 rounded-lg">{plot.name} {plot.is_general && <span className="text-[10px] bg-amber-100 text-amber-700 px-1.5 rounded">{t('farm.general_badge')}</span>}</div>}
                      />
                    ))}
                  </TreeItem>
                ))}
              </SimpleTreeView>
            )}
          </div>
        </Grid>

        <Grid item xs={12} md={5}>
          {activePlot ? (
            <Card elevation={0} className="p-8 border border-slate-200 shadow-sm rounded-3xl sticky top-8">
              <h3 className="text-xl font-black text-slate-800 mb-2">{activePlot.name}</h3>
              <p className="text-sm font-bold tracking-widest text-green-600 uppercase mb-6">{t('farm.sector_coordinates')}</p>
              {loadingStats ? (
                <div className="flex justify-center p-8"><CircularProgress sx={{ color: '#16a34a' }} /></div>
              ) : (
                <div className="space-y-4">
                  <div className="bg-slate-50 p-4 border border-slate-100 rounded-2xl flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-green-100 text-green-600 flex items-center justify-center shrink-0"><TerrainIcon /></div>
                    <div>
                      <p className="text-xs text-slate-400 font-bold uppercase tracking-wider">{t('farm.trees_count')}</p>
                      <p className="text-2xl font-black text-slate-800">{plotStats?.total_trees || 0} {t('farm.trunks')}</p>
                    </div>
                  </div>
                  <div className="bg-slate-50 p-4 border border-slate-100 rounded-2xl flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-purple-100 text-purple-600 flex items-center justify-center shrink-0"><AutoGraphIcon /></div>
                    <div>
                      <p className="text-xs text-slate-400 font-bold uppercase tracking-wider">{t('farm.lifetime_yield')}</p>
                      <p className="text-2xl font-black text-slate-800">{parseFloat(plotStats?.lifetime_yield || 0).toLocaleString()} {t('farm.tonnes')}</p>
                    </div>
                  </div>
                </div>
              )}
            </Card>
          ) : (
            <div className="border border-dashed border-slate-300 rounded-3xl h-full flex items-center justify-center text-slate-400 p-8 text-center bg-slate-50">
              {t('farm.plot_hint')}
            </div>
          )}
        </Grid>
      </Grid>

      {/* SECTOR MODAL */}
      <Dialog open={openSectorModal} onClose={() => setOpenSectorModal(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{t('farm.add_sector_title')}</DialogTitle>
        <DialogContent className="space-y-4 pt-4">
          <TextField select fullWidth label={t('farm.select_farm')} value={sectorForm.farm} onChange={(e) => setSectorForm({...sectorForm, farm: e.target.value})} className="mt-2" variant="filled">
            {farms.map((f) => <MenuItem key={f.id} value={f.id}>{f.name}</MenuItem>)}
          </TextField>
          <TextField fullWidth label={t('farm.sector_name')} value={sectorForm.name} onChange={(e) => setSectorForm({...sectorForm, name: e.target.value})} variant="filled" />
          <TextField select fullWidth label={t('farm.crop_type')} value={sectorForm.crop_type} onChange={(e) => setSectorForm({...sectorForm, crop_type: e.target.value})} variant="filled">
            {cropTypes.map((c) => <MenuItem key={c.id} value={c.id}>{c.name}</MenuItem>)}
          </TextField>
        </DialogContent>
        <DialogActions className="p-4">
          <Button onClick={() => setOpenSectorModal(false)}>{t('farm.cancel')}</Button>
          <Button onClick={handleCreateSector} variant="contained" disabled={formLoading || !sectorForm.name || !sectorForm.farm || !sectorForm.crop_type}>
            {formLoading ? <CircularProgress size={20} /> : t('farm.save_sector')}
          </Button>
        </DialogActions>
      </Dialog>

      {/* PLOT MODAL */}
      <Dialog open={openPlotModal} onClose={() => setOpenPlotModal(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{t('farm.add_plot_title')}</DialogTitle>
        <DialogContent className="space-y-4 pt-4">
          <TextField select fullWidth label={t('farm.parent_sector')} value={plotForm.sector} onChange={(e) => setPlotForm({...plotForm, sector: e.target.value})} className="mt-2" variant="filled">
            {structure.map((s) => <MenuItem key={s.id} value={s.id}>{s.name} ({s.crop_type_name})</MenuItem>)}
          </TextField>
          <TextField fullWidth label={t('farm.plot_name')} value={plotForm.name} onChange={(e) => setPlotForm({...plotForm, name: e.target.value})} variant="filled" />
          <TextField select fullWidth label={t('farm.plot_type')} value={plotForm.is_general} onChange={(e) => setPlotForm({...plotForm, is_general: e.target.value})} variant="filled">
            <MenuItem value={false}>{t('farm.plot_specific')}</MenuItem>
            <MenuItem value={true}>{t('farm.plot_general')}</MenuItem>
          </TextField>
        </DialogContent>
        <DialogActions className="p-4">
          <Button onClick={() => setOpenPlotModal(false)}>{t('farm.cancel')}</Button>
          <Button onClick={handleCreatePlot} variant="contained" color="secondary" disabled={formLoading || !plotForm.name || !plotForm.sector}>
            {formLoading ? <CircularProgress size={20} /> : t('farm.save_plot')}
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default FarmStructure;
