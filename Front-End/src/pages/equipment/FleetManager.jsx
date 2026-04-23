import React, { useState, useEffect } from 'react';
import { Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField, CircularProgress, Alert, Card, Grid } from '@mui/material';
import { getEquipmentList, createEquipment, getEquipmentDetails, logMaintenance, logUsage } from '../../features/equipment/services';
import { useTranslation } from 'react-i18next';

const FleetManager = () => {
  const { t } = useTranslation();
  const [equipmentList, setEquipmentList] = useState([]);
  const [selectedEqId, setSelectedEqId]   = useState(null);
  const [details, setDetails]             = useState(null);
  const [loading, setLoading]             = useState(true);

  const [openEqModal, setOpenEqModal]       = useState(false);
  const [openMaintModal, setOpenMaintModal] = useState(false);
  const [openUsageModal, setOpenUsageModal] = useState(false);
  const [formLoading, setFormLoading]       = useState(false);
  const [formError, setFormError]           = useState('');

  const [eqName, setEqName]     = useState('');
  const [maintForm, setMaintForm] = useState({ date: new Date().toISOString().split('T')[0], notes: '' });
  const [usageForm, setUsageForm] = useState({ date: new Date().toISOString().split('T')[0], hours_used: '', fuel_consumption: '' });

  useEffect(() => { fetchMaster(); }, []);
  useEffect(() => { if (selectedEqId) fetchDetails(selectedEqId); }, [selectedEqId]);

  const fetchMaster = async () => {
    try { setEquipmentList(await getEquipmentList()); setLoading(false); }
    catch (err) { console.error(err); }
  };
  const fetchDetails = async (id) => {
    try { setDetails(null); setDetails(await getEquipmentDetails(id)); }
    catch (err) { console.error(err); }
  };
  const handleCreateMaster = async () => {
    setFormLoading(true); setFormError('');
    try { const res = await createEquipment({ name: eqName }); setOpenEqModal(false); await fetchMaster(); setSelectedEqId(res.id); }
    catch { setFormError(t('common.error')); }
    finally { setFormLoading(false); }
  };
  const handleCreateMaintenance = async () => {
    setFormLoading(true); setFormError('');
    try { await logMaintenance({ equipment: selectedEqId, ...maintForm }); setOpenMaintModal(false); fetchDetails(selectedEqId); }
    catch { setFormError(t('common.error')); }
    finally { setFormLoading(false); }
  };
  const handleCreateUsage = async () => {
    setFormLoading(true); setFormError('');
    try { await logUsage({ equipment: selectedEqId, ...usageForm }); setOpenUsageModal(false); fetchDetails(selectedEqId); }
    catch { setFormError(t('common.error')); }
    finally { setFormLoading(false); }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-800 tracking-tight">{t('equipment.title')}</h1>
          <p className="text-slate-500 mt-1">{t('equipment.subtitle')}</p>
        </div>
        <Button variant="contained" onClick={() => setOpenEqModal(true)} sx={{ background: '#0f172a' }}>
          {t('equipment.deploy_btn')}
        </Button>
      </div>

      <div className="flex flex-col md:flex-row gap-6">
        {/* Equipment list */}
        <div className="w-full md:w-1/3 space-y-2">
          {loading ? <CircularProgress sx={{ color: '#16a34a' }} /> : equipmentList.map(eq => (
            <div key={eq.id} onClick={() => setSelectedEqId(eq.id)}
              className={`p-4 rounded-xl cursor-pointer transition-all border ${selectedEqId === eq.id ? 'bg-green-50 border-green-200 shadow-sm' : 'bg-white border-slate-100 hover:border-slate-300'}`}>
              <h3 className={`font-bold ${selectedEqId === eq.id ? 'text-green-800' : 'text-slate-700'}`}>{eq.name}</h3>
              <p className="text-xs text-slate-400 mt-1">{t('equipment.registry_id')}: HW-{String(eq.id).padStart(4, '0')}</p>
            </div>
          ))}
          {equipmentList.length === 0 && !loading && <div className="text-slate-400 italic">{t('equipment.no_fleet')}</div>}
        </div>

        {/* Details panel */}
        <div className="w-full md:w-2/3 bg-white border border-slate-100 shadow-sm rounded-2xl p-6 min-h-[500px]">
          {!selectedEqId ? (
            <div className="flex h-full items-center justify-center text-slate-400">{t('common.empty')}</div>
          ) : !details ? (
            <div className="flex h-full items-center justify-center"><CircularProgress sx={{ color: '#16a34a' }} /></div>
          ) : (
            <div className="space-y-8">
              <div className="flex justify-between items-start border-b border-slate-100 pb-4">
                <div>
                  <h2 className="text-2xl font-black text-slate-800">{details.equipment.name}</h2>
                  <p className="text-sm text-slate-500 mt-1 uppercase tracking-wider font-semibold">{t('equipment.registry_id')}: HW-{String(selectedEqId).padStart(4,'0')}</p>
                </div>
                <div className="flex gap-2">
                  <Button onClick={() => setOpenMaintModal(true)} variant="outlined" size="small" color="secondary">{t('equipment.log_maintenance')}</Button>
                  <Button onClick={() => setOpenUsageModal(true)} variant="contained" size="small" sx={{ background: '#3b82f6' }}>{t('equipment.log_usage')}</Button>
                </div>
              </div>

              <Grid container spacing={4}>
                <Grid item xs={12} lg={6}>
                  <h3 className="text-slate-800 font-bold mb-4">{t('equipment.runtime_title')}</h3>
                  <div className="space-y-3">
                    {details.usages.length === 0
                      ? <p className="text-slate-400 italic text-sm">{t('equipment.no_usage')}</p>
                      : details.usages.map(u => (
                        <div key={u.id} className="bg-slate-50 border border-slate-100 p-3 rounded-lg flex justify-between items-center text-sm">
                          <span className="font-semibold text-slate-700">{u.date}</span>
                          <div className="text-right">
                            <div className="text-blue-700 font-bold">{u.hours_used} {t('equipment.hours')}</div>
                            {u.fuel_consumption && <div className="text-xs text-slate-500">{u.fuel_consumption} {t('equipment.fuel_short')}</div>}
                          </div>
                        </div>
                      ))}
                  </div>
                </Grid>
                <Grid item xs={12} lg={6}>
                  <h3 className="text-slate-800 font-bold mb-4">{t('equipment.maintenance_title')}</h3>
                  <div className="space-y-3">
                    {details.maintenances.length === 0
                      ? <p className="text-slate-400 italic text-sm">{t('equipment.no_maintenance')}</p>
                      : details.maintenances.map(m => (
                        <div key={m.id} className="bg-rose-50 border border-rose-100 p-3 rounded-lg text-sm">
                          <div className="flex justify-between mb-1">
                            <span className="font-bold text-rose-800">{t('equipment.event_label')}</span>
                            <span className="text-rose-600 font-medium">{m.date}</span>
                          </div>
                          <p className="text-rose-700/80 mt-1">{m.notes}</p>
                        </div>
                      ))}
                  </div>
                </Grid>
              </Grid>
            </div>
          )}
        </div>
      </div>

      {/* REGISTER EQUIPMENT MODAL */}
      <Dialog open={openEqModal} onClose={() => setOpenEqModal(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{t('equipment.deploy_modal_title')}</DialogTitle>
        <DialogContent className="pt-4 space-y-4">
          {formError && <Alert severity="error">{formError}</Alert>}
          <TextField fullWidth label={t('equipment.eq_name')} value={eqName} onChange={(e) => setEqName(e.target.value)} variant="filled" />
        </DialogContent>
        <DialogActions className="p-4">
          <Button onClick={() => setOpenEqModal(false)}>{t('equipment.cancel')}</Button>
          <Button onClick={handleCreateMaster} variant="contained" disabled={formLoading || !eqName}>{t('equipment.initialize_btn')}</Button>
        </DialogActions>
      </Dialog>

      {/* MAINTENANCE MODAL */}
      <Dialog open={openMaintModal} onClose={() => setOpenMaintModal(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{t('equipment.maint_modal_title')}</DialogTitle>
        <DialogContent className="pt-4 space-y-4">
          {formError && <Alert severity="error">{formError}</Alert>}
          <TextField fullWidth type="date" label={t('equipment.maint_date')} value={maintForm.date} onChange={(e) => setMaintForm({...maintForm, date: e.target.value})} variant="filled" InputLabelProps={{ shrink: true }} />
          <TextField fullWidth multiline rows={3} label={t('equipment.maint_notes')} value={maintForm.notes} onChange={(e) => setMaintForm({...maintForm, notes: e.target.value})} variant="filled" />
        </DialogContent>
        <DialogActions className="p-4">
          <Button onClick={() => setOpenMaintModal(false)}>{t('equipment.cancel')}</Button>
          <Button onClick={handleCreateMaintenance} color="secondary" variant="contained" disabled={formLoading || !maintForm.date || !maintForm.notes}>{t('equipment.maint_save')}</Button>
        </DialogActions>
      </Dialog>

      {/* USAGE MODAL */}
      <Dialog open={openUsageModal} onClose={() => setOpenUsageModal(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{t('equipment.usage_modal_title')}</DialogTitle>
        <DialogContent className="pt-4 space-y-4">
          {formError && <Alert severity="error">{formError}</Alert>}
          <TextField fullWidth type="date" label={t('equipment.usage_date')} value={usageForm.date} onChange={(e) => setUsageForm({...usageForm, date: e.target.value})} variant="filled" InputLabelProps={{ shrink: true }} />
          <Grid container spacing={2}>
            <Grid item xs={6}><TextField fullWidth type="number" label={t('equipment.usage_hours')} value={usageForm.hours_used} onChange={(e) => setUsageForm({...usageForm, hours_used: e.target.value})} variant="filled" /></Grid>
            <Grid item xs={6}><TextField fullWidth type="number" label={t('equipment.usage_fuel')} value={usageForm.fuel_consumption} onChange={(e) => setUsageForm({...usageForm, fuel_consumption: e.target.value})} variant="filled" /></Grid>
          </Grid>
        </DialogContent>
        <DialogActions className="p-4">
          <Button onClick={() => setOpenUsageModal(false)}>{t('equipment.cancel')}</Button>
          <Button onClick={handleCreateUsage} variant="contained" disabled={formLoading || !usageForm.date || !usageForm.hours_used} sx={{ background: '#3b82f6' }}>{t('equipment.usage_save')}</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};
export default FleetManager;
