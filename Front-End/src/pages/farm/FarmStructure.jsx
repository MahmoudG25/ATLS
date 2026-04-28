import React, { useState, useEffect, useCallback } from 'react';
import { 
  Button, Dialog, DialogTitle, DialogContent, DialogActions, 
  TextField, MenuItem, CircularProgress, Alert, Card, 
  IconButton, Box, Tooltip, Breadcrumbs, Typography
} from '@mui/material';
import { 
  getLocationTree, createLocationNode, updateLocationNode, 
  deleteLocationNode, getCropTypes 
} from '../../features/farm/services';
import { useTranslation } from 'react-i18next';
import {
  AccountTreeOutlined as FarmIcon,
  GridViewOutlined as SectorIcon,
  LayersOutlined as StageIcon,
  TerrainOutlined as EnclosureIcon,
  AddCircleOutlined as AddIcon,
  EditOutlined as EditIcon,
  DeleteOutlineOutlined as DeleteIcon,
  ArrowBackIosNew as ArrowIcon,
} from '@mui/icons-material';
import './FarmStructure.css';

const NODE_TYPES = {
  SECTOR: 'SECTOR',
  STAGE: 'STAGE',
  ENCLOSURE: 'ENCLOSURE'
};

const NodeIcon = ({ type, fontSize = "small" }) => {
  switch (type) {
    case NODE_TYPES.SECTOR: return <SectorIcon fontSize={fontSize} />;
    case NODE_TYPES.STAGE: return <StageIcon fontSize={fontSize} />;
    case NODE_TYPES.ENCLOSURE: return <EnclosureIcon fontSize={fontSize} />;
    default: return <FarmIcon fontSize={fontSize} />;
  }
};

const TreeItem = ({ node, onAdd, onEdit, onDelete, level = 0 }) => {
  const { t } = useTranslation();
  
  return (
    <li className="relative">
      <div className={`flex items-center gap-3 p-3 my-2 rounded-xl border transition-all group ${
        node.type === NODE_TYPES.SECTOR ? 'bg-slate-50 border-slate-200' : 
        node.type === NODE_TYPES.STAGE ? 'bg-white border-slate-100' : 'bg-white border-slate-50'
      } hover:border-green-300 hover:shadow-sm`}>
        
        <div className={`flex items-center justify-center w-10 h-10 rounded-lg ${
          node.type === NODE_TYPES.SECTOR ? 'bg-green-100 text-green-700' : 
          node.type === NODE_TYPES.STAGE ? 'bg-blue-50 text-blue-600' : 'bg-orange-50 text-orange-600'
        }`}>
          <NodeIcon type={node.type} />
        </div>

        <div className="flex-grow">
          <p className="text-sm font-bold text-slate-800">{node.name}</p>
          <p className="text-[0.65rem] font-bold uppercase tracking-wider text-slate-400">
            {node.type === NODE_TYPES.SECTOR ? t('farm.sector', 'قطاع') : 
             node.type === NODE_TYPES.STAGE ? t('farm.stage', 'مرحلة') : t('farm.enclosure', 'حوشة')}
          </p>
        </div>

        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          {node.type !== NODE_TYPES.ENCLOSURE && (
            <Tooltip title={t('farm.add_child', 'إضافة عنصر تابع')}>
              <IconButton size="small" onClick={() => onAdd(node)} sx={{ color: '#16a34a' }}>
                <AddIcon sx={{ fontSize: 18 }} />
              </IconButton>
            </Tooltip>
          )}
          <Tooltip title={t('common.edit', 'تعديل')}>
            <IconButton size="small" onClick={() => onEdit(node)} sx={{ color: '#64748b' }}>
              <EditIcon sx={{ fontSize: 18 }} />
            </IconButton>
          </Tooltip>
          <Tooltip title={t('common.delete', 'حذف')}>
            <IconButton size="small" onClick={() => onDelete(node)} sx={{ color: '#ef4444' }}>
              <DeleteIcon sx={{ fontSize: 18 }} />
            </IconButton>
          </Tooltip>
        </div>
      </div>

      {node.children && node.children.length > 0 && (
        <ul className="ms-8 border-s-2 border-slate-100 ps-4">
          {node.children.map(child => (
            <TreeItem key={child.id} node={child} onAdd={onAdd} onEdit={onEdit} onDelete={onDelete} level={level + 1} />
          ))}
        </ul>
      )}
    </li>
  );
};

const FarmStructure = () => {
  const { t } = useTranslation();
  const [tree, setTree] = useState([]);
  const [farmInfo, setFarmInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Modal States
  const [modalOpen, setModalOpen] = useState(false);
  const [modalType, setModalType] = useState(NODE_TYPES.SECTOR); // SECTOR, STAGE, ENCLOSURE
  const [editMode, setEditMode] = useState(false);
  const [currentNode, setCurrentNode] = useState(null);
  
  // Form State
  const [form, setForm] = useState({
    name: '',
    parent: null,
    parentId: '', // for enclosure selection of Sector -> Stage
    sectorId: '',
    stageId: '',
  });
  const [formLoading, setFormLoading] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getLocationTree();
      setTree(data.tree);
      setFarmInfo(data.farm);
    } catch (err) {
      setError(t('farm.error_fetch', 'فشل تحميل هيكل المزرعة'));
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleOpenAdd = (parent = null, type = NODE_TYPES.SECTOR) => {
    setEditMode(false);
    setCurrentNode(null);
    setModalType(type);
    
    let initialForm = { name: '', parent: parent?.id || null };
    
    if (type === NODE_TYPES.STAGE) {
      initialForm.sectorId = parent?.id || '';
    } else if (type === NODE_TYPES.ENCLOSURE) {
      if (parent?.type === NODE_TYPES.SECTOR) {
        initialForm.sectorId = parent.id;
        initialForm.stageId = '';
      } else if (parent?.type === NODE_TYPES.STAGE) {
        // Find parent sector
        const findSector = (nodes, targetId) => {
          for (let n of nodes) {
            if (n.children?.some(c => c.id === targetId)) return n.id;
            const res = findSector(n.children || [], targetId);
            if (res) return res;
          }
          return '';
        };
        initialForm.sectorId = findSector(tree, parent.id);
        initialForm.stageId = parent.id;
      }
    }
    
    setForm(initialForm);
    setModalOpen(true);
  };

  const handleOpenEdit = (node) => {
    setEditMode(true);
    setCurrentNode(node);
    setModalType(node.type);
    setForm({ name: node.name, parent: node.parent_id });
    setModalOpen(true);
  };

  const handleSave = async () => {
    setFormLoading(true);
    try {
      const payload = {
        name: form.name,
        type: modalType,
        parent: modalType === NODE_TYPES.SECTOR ? null : (form.stageId || form.sectorId || form.parent)
      };

      if (editMode) {
        await updateLocationNode(currentNode.id, { name: form.name });
      } else {
        await createLocationNode(payload);
      }
      setModalOpen(false);
      fetchData();
    } catch (err) {
      const msg = err.response?.data?.parent || err.response?.data?.name || t('common.error_save');
      alert(Array.isArray(msg) ? msg[0] : msg);
    } finally {
      setFormLoading(false);
    }
  };

  const handleDelete = async (node) => {
    if (window.confirm(t('farm.confirm_delete_node', 'هل أنت متأكد من حذف هذا العنصر؟ سيتم أرشفة جميع العناصر التابعة له.'))) {
      try {
        await deleteLocationNode(node.id);
        fetchData();
      } catch (err) {
        alert(t('common.error_delete'));
      }
    }
  };

  // Helper to find sectors for dropdowns
  const sectors = tree.filter(n => n.type === NODE_TYPES.SECTOR);
  const stages = form.sectorId ? (tree.find(n => n.id === form.sectorId)?.children?.filter(c => c.type === NODE_TYPES.STAGE) || []) : [];

  if (loading && !tree.length) return <Box sx={{ p: 8, display: 'flex', justifyContent: 'center' }}><CircularProgress sx={{ color: '#16a34a' }} /></Box>;

  return (
    <div className="p-8 w-full max-w-6xl mx-auto" dir="rtl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-10 gap-6">
        <div>
          <Breadcrumbs separator={<ArrowIcon sx={{ fontSize: 10, mx: 0.5, color: '#94a3b8' }} />}>
            <Typography variant="caption" sx={{ fontWeight: 700, color: '#64748b', display: 'flex', itemsCenter: 'center', gap: 0.5 }}>
              <FarmIcon sx={{ fontSize: 14 }} /> {farmInfo?.name || t('farm.farm', 'المزرعة')}
            </Typography>
            <Typography variant="caption" sx={{ fontWeight: 800, color: '#1e293b' }}>
              {t('farm.structure_title', 'الهيكل التنظيمي')}
            </Typography>
          </Breadcrumbs>
          <h1 className="text-3xl font-black text-slate-800 tracking-tight mt-2">
            {t('farm.manage_hierarchy', 'إدارة الهيكل الهرمي')}
          </h1>
          <p className="text-slate-500 font-medium mt-1">{t('farm.hierarchy_desc', 'قم بتنظيم القطاعات، المراحل، والحوشات بشكل ديناميكي')}</p>
        </div>
        
        <div className="flex gap-3">
          <Button 
            variant="contained" 
            startIcon={<AddIcon />}
            onClick={() => handleOpenAdd(null, NODE_TYPES.SECTOR)}
            sx={{ borderRadius: 3, px: 4, py: 1.5, fontWeight: 800, bgcolor: '#16a34a', '&:hover': { bgcolor: '#15803d' }, boxShadow: '0 4px 12px rgba(22, 163, 74, 0.25)' }}
          >
            {t('farm.add_sector_btn', 'إضافة قطاع جديد')}
          </Button>
        </div>
      </div>

      {error && <Alert severity="error" sx={{ mb: 4, borderRadius: 3 }}>{error}</Alert>}

      <Card sx={{ borderRadius: 4, border: '1px solid #f1f5f9', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.05)', overflow: 'visible' }}>
        <div className="p-8">
          {tree.length === 0 ? (
            <div className="py-20 flex flex-col items-center justify-center text-slate-400">
              <FarmIcon sx={{ fontSize: 64, mb: 2, opacity: 0.2 }} />
              <p className="font-bold">{t('farm.no_structure', 'لا يوجد هيكل معرف بعد. ابدأ بإضافة أول قطاع.')}</p>
            </div>
          ) : (
            <ul className="space-y-4">
              {tree.map(node => (
                <TreeItem 
                  key={node.id} 
                  node={node} 
                  onAdd={(p) => handleOpenAdd(p, p.type === NODE_TYPES.SECTOR ? NODE_TYPES.STAGE : NODE_TYPES.ENCLOSURE)}
                  onEdit={handleOpenEdit}
                  onDelete={handleDelete}
                />
              ))}
            </ul>
          )}
        </div>
      </Card>

      {/* Dynamic Modal */}
      <Dialog 
        open={modalOpen} 
        onClose={() => setModalOpen(false)} 
        maxWidth="xs" 
        fullWidth 
        PaperProps={{ sx: { borderRadius: 4, p: 1 } }}
      >
        <DialogTitle sx={{ fontWeight: 900, fontSize: '1.25rem', color: '#1e293b' }}>
          {editMode ? t('farm.edit_node', 'تعديل العنصر') : (
            modalType === NODE_TYPES.SECTOR ? t('farm.add_sector_title', 'إضافة قطاع') :
            modalType === NODE_TYPES.STAGE ? t('farm.add_stage_title', 'إضافة مرحلة') : t('farm.add_enclosure_title', 'إضافة حوشة')
          )}
        </DialogTitle>
        
        <DialogContent className="space-y-6 pt-2">
          {/* Parent Selection Logic */}
          {!editMode && modalType !== NODE_TYPES.SECTOR && (
            <>
              <TextField
                select
                fullWidth
                label={t('farm.select_sector', 'اختر القطاع')}
                value={form.sectorId}
                onChange={(e) => setForm({ ...form, sectorId: e.target.value, stageId: '' })}
                variant="outlined"
                InputProps={{ sx: { borderRadius: 3 } }}
              >
                {sectors.map(s => <MenuItem key={s.id} value={s.id} sx={{ fontWeight: 600 }}>{s.name}</MenuItem>)}
              </TextField>

              {modalType === NODE_TYPES.ENCLOSURE && form.sectorId && (tree.find(n => n.id === form.sectorId)?.has_stages) && (
                <TextField
                  select
                  fullWidth
                  label={t('farm.select_stage_optional', 'اختر المرحلة (اختياري)')}
                  value={form.stageId}
                  onChange={(e) => setForm({ ...form, stageId: e.target.value })}
                  variant="outlined"
                  InputProps={{ sx: { borderRadius: 3 } }}
                >
                  <MenuItem value=""><em>{t('common.none', 'بدون مرحلة')}</em></MenuItem>
                  {stages.map(st => <MenuItem key={st.id} value={st.id} sx={{ fontWeight: 600 }}>{st.name}</MenuItem>)}
                </TextField>
              )}
            </>
          )}

          <TextField 
            fullWidth 
            label={
              modalType === NODE_TYPES.SECTOR ? t('farm.sector_name', 'اسم القطاع') :
              modalType === NODE_TYPES.STAGE ? t('farm.stage_name', 'اسم المرحلة') : t('farm.enclosure_name', 'اسم الحوشة')
            }
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            autoFocus
            variant="outlined"
            InputProps={{ sx: { borderRadius: 3 } }}
          />
        </DialogContent>

        <DialogActions sx={{ p: 3, gap: 1 }}>
          <Button onClick={() => setModalOpen(false)} sx={{ fontWeight: 800, color: '#64748b' }}>{t('common.cancel', 'إلغاء')}</Button>
          <Button 
            onClick={handleSave} 
            variant="contained" 
            disabled={formLoading || !form.name || (!editMode && modalType !== NODE_TYPES.SECTOR && !form.sectorId)}
            sx={{ borderRadius: 3, px: 4, fontWeight: 800, bgcolor: '#16a34a', '&:hover': { bgcolor: '#15803d' } }}
          >
            {formLoading ? <CircularProgress size={20} color="inherit" /> : t('common.save', 'حفظ')}
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default FarmStructure;

