import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Button, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, MenuItem, CircularProgress, Alert, Card,
  IconButton, Box, Tooltip, Breadcrumbs, Typography, InputAdornment,
} from '@mui/material';
import {
  getLocationTree, createLocationNode, updateLocationNode, deleteLocationNode,
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
  ExpandMore as ExpandIcon,
  ChevronLeft as CollapseIcon,
  SearchOutlined as SearchIcon,
  ArrowBackIosNew as ArrowIcon,
} from '@mui/icons-material';
import './FarmStructure.css';

// ─── Constants ───────────────────────────────────────────────────────────────
const NT = { SECTOR: 'SECTOR', STAGE: 'STAGE', ENCLOSURE: 'ENCLOSURE' };

// Allowed children per node type
const ALLOWED_CHILDREN = {
  [NT.SECTOR]:    [NT.STAGE, NT.ENCLOSURE],
  [NT.STAGE]:     [NT.ENCLOSURE],
  [NT.ENCLOSURE]: [],
};

// ─── Helpers ─────────────────────────────────────────────────────────────────
const getSizeClass   = (n) => n <= 3 ? 'lg' : n <= 6 ? 'md' : n <= 12 ? 'sm' : 'xs';
const getIconSize    = (s) => ({ lg: 22, md: 18, sm: 15, xs: 13 }[s] || 18);
const getEnclosureGrid = (n) => n <= 4 ? 'enclosure-grid-2' : n <= 8 ? 'enclosure-grid-3' : n <= 12 ? 'enclosure-grid-4' : 'enclosure-grid-5';

const nodeMatchesSearch = (node, q) => {
  if (!q) return true;
  const lower = q.toLowerCase();
  if (node.name.toLowerCase().includes(lower)) return true;
  return (node.children || []).some(c => nodeMatchesSearch(c, q));
};

const isHighlighted = (node, q) =>
  q && node.name.toLowerCase().includes(q.toLowerCase());

// ─── NodeIcon ────────────────────────────────────────────────────────────────
const NodeIcon = ({ type, size }) => {
  const sx = { fontSize: getIconSize(size) };
  if (type === NT.SECTOR)    return <SectorIcon sx={sx} />;
  if (type === NT.STAGE)     return <StageIcon sx={sx} />;
  if (type === NT.ENCLOSURE) return <EnclosureIcon sx={sx} />;
  return <FarmIcon sx={sx} />;
};

// ─── EnclosureNode ────────────────────────────────────────────────────────────
const EnclosureNode = ({ node, size, onEdit, onDelete, searchQuery }) => {
  const { t } = useTranslation();
  const matched = nodeMatchesSearch(node, searchQuery);
  return (
    <div className={`tree-node node-enclosure tree-node-${size} ${!matched ? 'node-dimmed' : ''} ${isHighlighted(node, searchQuery) ? 'node-highlighted' : ''}`}>
      <div className={`tree-node-icon-${size}`}><NodeIcon type={NT.ENCLOSURE} size={size} /></div>
      <div style={{ flex: 1, minWidth: 0, margin: '0 6px' }}>
        <p style={{ fontWeight: 700, color: '#1e293b', margin: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{node.name}</p>
        {size === 'lg' && <p style={{ fontSize: 9, fontWeight: 800, textTransform: 'uppercase', color: '#94a3b8', margin: 0 }}>{t('farm.enclosure', 'حوشة')}</p>}
      </div>
      <div className="tree-node-actions">
        <Tooltip title={t('common.edit', 'تعديل')}><IconButton size="small" onClick={() => onEdit(node)} sx={{ color: '#64748b', p: '3px' }}><EditIcon sx={{ fontSize: 14 }} /></IconButton></Tooltip>
        <Tooltip title={t('common.delete', 'حذف')}><IconButton size="small" onClick={() => onDelete(node)} sx={{ color: '#ef4444', p: '3px' }}><DeleteIcon sx={{ fontSize: 14 }} /></IconButton></Tooltip>
      </div>
    </div>
  );
};

// ─── StageNode ────────────────────────────────────────────────────────────────
const StageNode = ({ node, siblingCount, onAdd, onEdit, onDelete, searchQuery }) => {
  const { t } = useTranslation();
  const [collapsed, setCollapsed] = useState(false);
  const size = getSizeClass(siblingCount);
  const enclosures = (node.children || []).filter(c => c.type === NT.ENCLOSURE);
  const encSize = getSizeClass(enclosures.length);
  const matched = nodeMatchesSearch(node, searchQuery);

  return (
    <div className="stage-item">
      <div
        className={`tree-node node-stage tree-node-${size} ${!matched ? 'node-dimmed' : ''} ${isHighlighted(node, searchQuery) ? 'node-highlighted' : ''}`}
        style={{ marginBottom: enclosures.length > 0 && !collapsed ? 6 : 0 }}
      >
        {enclosures.length > 0 && (
          <button className="tree-collapse-btn" onClick={() => setCollapsed(!collapsed)}>
            {collapsed ? <CollapseIcon sx={{ fontSize: 12 }} /> : <ExpandIcon sx={{ fontSize: 12 }} />}
          </button>
        )}
        <div className={`tree-node-icon-${size}`} style={{ margin: '0 6px' }}><NodeIcon type={NT.STAGE} size={size} /></div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <p style={{ fontWeight: 700, color: '#1e293b', margin: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{node.name}</p>
          {size !== 'xs' && <p style={{ fontSize: 9, fontWeight: 800, textTransform: 'uppercase', color: '#94a3b8', margin: 0 }}>{t('farm.stage', 'مرحلة')}</p>}
        </div>
        {enclosures.length > 0 && <span className="tree-count-badge">{enclosures.length}</span>}
        <div className="tree-node-actions" style={{ marginRight: 0, marginLeft: 4 }}>
          <Tooltip title={t('farm.add_enclosure', 'إضافة حوشة')}><IconButton size="small" onClick={() => onAdd(node, NT.ENCLOSURE)} sx={{ color: '#16a34a', p: '3px' }}><AddIcon sx={{ fontSize: 14 }} /></IconButton></Tooltip>
          <Tooltip title={t('common.edit', 'تعديل')}><IconButton size="small" onClick={() => onEdit(node)} sx={{ color: '#64748b', p: '3px' }}><EditIcon sx={{ fontSize: 14 }} /></IconButton></Tooltip>
          <Tooltip title={t('common.delete', 'حذف')}><IconButton size="small" onClick={() => onDelete(node)} sx={{ color: '#ef4444', p: '3px' }}><DeleteIcon sx={{ fontSize: 14 }} /></IconButton></Tooltip>
        </div>
      </div>
      {!collapsed && enclosures.length > 0 && (
        <div className={getEnclosureGrid(enclosures.length)} style={{ marginTop: 4, paddingRight: 8, borderRight: '2px dashed #e2e8f0' }}>
          {enclosures.map(enc => (
            <EnclosureNode key={enc.id} node={enc} size={encSize} onEdit={onEdit} onDelete={onDelete} searchQuery={searchQuery} />
          ))}
        </div>
      )}
    </div>
  );
};

// ─── SectorNode ───────────────────────────────────────────────────────────────
const SectorNode = ({ node, siblingCount, onAdd, onEdit, onDelete, searchQuery }) => {
  const { t } = useTranslation();
  const [collapsed, setCollapsed] = useState(false);
  const size = getSizeClass(siblingCount);
  const stages = (node.children || []).filter(c => c.type === NT.STAGE);
  const directEnclosures = (node.children || []).filter(c => c.type === NT.ENCLOSURE);
  const hasChildren = stages.length > 0 || directEnclosures.length > 0;
  const childCount = stages.length || directEnclosures.length;
  const matched = nodeMatchesSearch(node, searchQuery);

  return (
    <li style={{ listStyle: 'none', marginBottom: 12 }}>
      <div className={`tree-node node-sector tree-node-${size} ${!matched ? 'node-dimmed' : ''} ${isHighlighted(node, searchQuery) ? 'node-highlighted' : ''}`}>
        {hasChildren && (
          <button className="tree-collapse-btn" onClick={() => setCollapsed(!collapsed)}>
            {collapsed ? <CollapseIcon sx={{ fontSize: 12 }} /> : <ExpandIcon sx={{ fontSize: 12 }} />}
          </button>
        )}
        <div className={`tree-node-icon-${size}`} style={{ margin: '0 8px' }}><NodeIcon type={NT.SECTOR} size={size} /></div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <p style={{ fontWeight: 800, color: '#1e293b', margin: 0, fontSize: size === 'xs' ? 11 : 14 }}>{node.name}</p>
          {size !== 'xs' && <p style={{ fontSize: 9, fontWeight: 800, textTransform: 'uppercase', color: '#94a3b8', margin: 0 }}>{t('farm.sector', 'قطاع')}</p>}
        </div>
        {childCount > 0 && <span className="tree-count-badge">{childCount}</span>}
        <div className="tree-node-actions" style={{ marginRight: 0, marginLeft: 4 }}>
          {/* Sector can add Stage OR Enclosure directly */}
          <Tooltip title={t('farm.add_stage', 'إضافة مرحلة')}><IconButton size="small" onClick={() => onAdd(node, NT.STAGE)} sx={{ color: '#3b82f6', p: '3px' }}><AddIcon sx={{ fontSize: 16 }} /></IconButton></Tooltip>
          <Tooltip title={t('farm.add_enclosure', 'إضافة حوشة مباشرة')}><IconButton size="small" onClick={() => onAdd(node, NT.ENCLOSURE)} sx={{ color: '#f97316', p: '3px' }}><AddIcon sx={{ fontSize: 14 }} /></IconButton></Tooltip>
          <Tooltip title={t('common.edit', 'تعديل')}><IconButton size="small" onClick={() => onEdit(node)} sx={{ color: '#64748b', p: '3px' }}><EditIcon sx={{ fontSize: 16 }} /></IconButton></Tooltip>
          <Tooltip title={t('common.delete', 'حذف')}><IconButton size="small" onClick={() => onDelete(node)} sx={{ color: '#ef4444', p: '3px' }}><DeleteIcon sx={{ fontSize: 16 }} /></IconButton></Tooltip>
        </div>
      </div>

      {!collapsed && hasChildren && (
        <div style={{ paddingRight: 24, marginTop: 6, borderRight: '2px solid #dcfce7' }}>
          {stages.length > 0 ? (
            <div className="stages-flex">
              {stages.map(stage => (
                <StageNode key={stage.id} node={stage} siblingCount={stages.length} onAdd={onAdd} onEdit={onEdit} onDelete={onDelete} searchQuery={searchQuery} />
              ))}
            </div>
          ) : (
            <div className={getEnclosureGrid(directEnclosures.length)} style={{ marginTop: 6 }}>
              {directEnclosures.map(enc => (
                <EnclosureNode key={enc.id} node={enc} size={getSizeClass(directEnclosures.length)} onEdit={onEdit} onDelete={onDelete} searchQuery={searchQuery} />
              ))}
            </div>
          )}
        </div>
      )}
    </li>
  );
};

// ─── Root-level Stage (Stage directly under Farm, no Sector parent) ───────────
const RootStageNode = ({ node, siblingCount, onAdd, onEdit, onDelete, searchQuery }) => (
  <li style={{ listStyle: 'none', marginBottom: 12 }}>
    <StageNode node={node} siblingCount={siblingCount} onAdd={onAdd} onEdit={onEdit} onDelete={onDelete} searchQuery={searchQuery} />
  </li>
);

// ─── Main Component ───────────────────────────────────────────────────────────
const FarmStructure = () => {
  const { t } = useTranslation();
  const [tree, setTree]         = useState([]);
  const [farmInfo, setFarmInfo] = useState(null);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Modal state
  const [modalOpen, setModalOpen]   = useState(false);
  const [modalType, setModalType]   = useState(NT.SECTOR);
  const [editMode, setEditMode]     = useState(false);
  const [currentNode, setCurrentNode] = useState(null);
  const [form, setForm]             = useState({ name: '', parentId: '' });
  const [formLoading, setFormLoading] = useState(false);

  // ── Fetch ────────────────────────────────────────────────────────────────
  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getLocationTree();
      setTree(data.tree || []);
      setFarmInfo(data.farm);
    } catch {
      setError(t('farm.error_fetch', 'فشل تحميل هيكل المزرعة'));
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => { fetchData(); }, [fetchData]);

  // ── Derived ──────────────────────────────────────────────────────────────
  const sectors     = useMemo(() => tree.filter(n => n.type === NT.SECTOR), [tree]);
  const rootStages  = useMemo(() => tree.filter(n => n.type === NT.STAGE), [tree]);

  /** All valid parent nodes for a given child type */
  const getValidParents = useCallback((type) => {
    const result = [];
    const walk = (nodes) => {
      for (const n of nodes) {
        if (ALLOWED_CHILDREN[n.type]?.includes(type)) result.push(n);
        walk(n.children || []);
      }
    };
    walk(tree);
    return result;
  }, [tree]);

  // ── Handlers ─────────────────────────────────────────────────────────────
  const handleOpenAdd = (parent, type) => {
    setEditMode(false);
    setCurrentNode(null);
    setModalType(type);
    setForm({ name: '', parentId: parent ? String(parent.id) : '' });
    setModalOpen(true);
  };

  const handleOpenEdit = (node) => {
    setEditMode(true);
    setCurrentNode(node);
    setModalType(node.type);
    setForm({ name: node.name, parentId: '' });
    setModalOpen(true);
  };

  const handleSave = async () => {
    setFormLoading(true);
    try {
      if (editMode) {
        await updateLocationNode(currentNode.id, { name: form.name });
      } else {
        const parentId = form.parentId ? Number(form.parentId) : null;
        await createLocationNode({ name: form.name, type: modalType, parent: parentId });
      }
      setModalOpen(false);
      fetchData();
    } catch (err) {
      const data = err.response?.data || {};
      const msg  = data.parent || data.name || data.detail || t('common.error_save', 'فشل الحفظ');
      alert(Array.isArray(msg) ? msg[0] : msg);
    } finally {
      setFormLoading(false);
    }
  };

  const handleDelete = async (node) => {
    if (!window.confirm(t('farm.confirm_delete_node', 'هل أنت متأكد؟ سيتم حذف جميع العناصر التابعة.'))) return;
    try { await deleteLocationNode(node.id); fetchData(); }
    catch { alert(t('common.error_delete', 'فشل الحذف')); }
  };

  // ── Modal helpers ─────────────────────────────────────────────────────────
  const validParents = useMemo(() => getValidParents(modalType), [getValidParents, modalType]);

  // ENCLOSURE requires a parent; STAGE & SECTOR do not
  const isSaveDisabled = formLoading || !form.name ||
    (!editMode && modalType === NT.ENCLOSURE && !form.parentId);

  // ── Render ────────────────────────────────────────────────────────────────
  if (loading && !tree.length) return (
    <Box sx={{ p: 8, display: 'flex', justifyContent: 'center' }}>
      <CircularProgress sx={{ color: '#16a34a' }} />
    </Box>
  );

  return (
    <div className="p-6 w-full max-w-6xl mx-auto" dir="rtl">

      {/* ── Header ── */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
        <div>
          <Breadcrumbs separator={<ArrowIcon sx={{ fontSize: 10, mx: 0.5, color: '#94a3b8' }} />}>
            <Typography variant="caption" sx={{ fontWeight: 700, color: '#64748b', display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <FarmIcon sx={{ fontSize: 14 }} /> {farmInfo?.name || t('farm.farm', 'المزرعة')}
            </Typography>
            <Typography variant="caption" sx={{ fontWeight: 800, color: '#1e293b' }}>
              {t('farm.structure_title', 'الهيكل التنظيمي')}
            </Typography>
          </Breadcrumbs>
          <h1 className="text-2xl font-black text-slate-800 tracking-tight mt-1">
            {t('farm.manage_hierarchy', 'إدارة الهيكل الهرمي')}
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            {t('farm.hierarchy_desc', 'قم بتنظيم القطاعات، المراحل، والحوشات بشكل ديناميكي')}
          </p>
        </div>

        {/* Action buttons at farm root level */}
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', justifyContent: 'flex-end' }}>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenAdd(null, NT.SECTOR)}
            sx={{ borderRadius: 3, px: 2.5, py: 1.2, fontWeight: 800, bgcolor: '#16a34a', '&:hover': { bgcolor: '#15803d' }, boxShadow: '0 4px 12px rgba(22,163,74,0.25)', whiteSpace: 'nowrap', fontSize: '0.82rem' }}
          >
            {t('farm.add_sector_btn', 'إضافة قطاع')}
          </Button>
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={() => handleOpenAdd(null, NT.STAGE)}
            sx={{ borderRadius: 3, px: 2.5, py: 1.2, fontWeight: 800, borderColor: '#3b82f6', color: '#3b82f6', '&:hover': { borderColor: '#1d4ed8', bgcolor: '#eff6ff' }, whiteSpace: 'nowrap', fontSize: '0.82rem' }}
          >
            {t('farm.add_stage_btn', 'إضافة مرحلة')}
          </Button>
        </div>
      </div>

      {error && <Alert severity="error" sx={{ mb: 3, borderRadius: 3 }}>{error}</Alert>}

      {/* ── Search ── */}
      <TextField
        fullWidth size="small"
        placeholder={t('farm.search_placeholder', 'ابحث باسم قطاع أو مرحلة أو حوشة...')}
        value={searchQuery}
        onChange={e => setSearchQuery(e.target.value)}
        InputProps={{
          startAdornment: <InputAdornment position="start"><SearchIcon sx={{ color: '#94a3b8', fontSize: 18 }} /></InputAdornment>,
          sx: { borderRadius: 3, bgcolor: '#f8fafc', fontSize: '0.875rem' },
        }}
        sx={{ mb: 4, '& .MuiOutlinedInput-root': { '& fieldset': { borderColor: '#e2e8f0' }, '&:hover fieldset': { borderColor: '#16a34a' } } }}
      />

      {/* ── Tree ── */}
      <Card sx={{ borderRadius: 4, border: '1px solid #f1f5f9', boxShadow: '0 4px 24px rgba(0,0,0,0.05)' }}>
        <div className="farm-tree-root p-6">
          {tree.length === 0 ? (
            <div className="py-16 flex flex-col items-center justify-center text-slate-400">
              <FarmIcon sx={{ fontSize: 56, mb: 2, opacity: 0.2 }} />
              <p className="font-bold text-sm">{t('farm.no_structure', 'لا يوجد هيكل معرف. ابدأ بإضافة أول قطاع أو مرحلة.')}</p>
            </div>
          ) : (
            <ul style={{ padding: 0, margin: 0 }}>
              {/* Sectors at root */}
              {sectors.map(sector => (
                <SectorNode
                  key={sector.id}
                  node={sector}
                  siblingCount={sectors.length}
                  onAdd={handleOpenAdd}
                  onEdit={handleOpenEdit}
                  onDelete={handleDelete}
                  searchQuery={searchQuery}
                />
              ))}
              {/* Stages directly under farm (no sector parent) */}
              {rootStages.length > 0 && (
                <>
                  {sectors.length > 0 && (
                    <li style={{ listStyle: 'none', borderTop: '1px dashed #e2e8f0', margin: '12px 0 8px', paddingTop: 4 }}>
                      <Typography variant="caption" sx={{ color: '#94a3b8', fontWeight: 700, fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                        مراحل مباشرة
                      </Typography>
                    </li>
                  )}
                  <li style={{ listStyle: 'none' }}>
                    <div className="stages-flex">
                      {rootStages.map(stage => (
                        <StageNode
                          key={stage.id}
                          node={stage}
                          siblingCount={rootStages.length}
                          onAdd={handleOpenAdd}
                          onEdit={handleOpenEdit}
                          onDelete={handleDelete}
                          searchQuery={searchQuery}
                        />
                      ))}
                    </div>
                  </li>
                </>
              )}
            </ul>
          )}
        </div>
      </Card>

      {/* ── Modal ── */}
      <Dialog open={modalOpen} onClose={() => setModalOpen(false)} maxWidth="xs" fullWidth PaperProps={{ sx: { borderRadius: 4, p: 1 } }}>
        <DialogTitle sx={{ fontWeight: 900, fontSize: '1.1rem', color: '#1e293b' }}>
          {editMode
            ? t('farm.edit_node', 'تعديل العنصر')
            : modalType === NT.SECTOR    ? t('farm.add_sector_title',    'إضافة قطاع جديد')
            : modalType === NT.STAGE     ? t('farm.add_stage_title',     'إضافة مرحلة جديدة')
            : t('farm.add_enclosure_title', 'إضافة حوشة جديدة')}
        </DialogTitle>

        <DialogContent sx={{ pt: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>

          {/* Parent selector — shown for STAGE (optional) and ENCLOSURE (required) */}
          {!editMode && modalType !== NT.SECTOR && (
            <TextField
              select fullWidth
              label={
                modalType === NT.STAGE
                  ? t('farm.parent_sector_optional', 'القطاع الأب (اختياري)')
                  : t('farm.parent_node_required', 'العنصر الأب')
              }
              value={form.parentId}
              onChange={e => setForm({ ...form, parentId: e.target.value })}
              InputProps={{ sx: { borderRadius: 2 } }}
            >
              {/* STAGE: allow no parent (root-level stage) */}
              {modalType === NT.STAGE && (
                <MenuItem value="">
                  <em style={{ color: '#94a3b8' }}>{t('farm.no_parent', 'بدون قطاع — مرحلة مستقلة')}</em>
                </MenuItem>
              )}
              {validParents.map(p => (
                <MenuItem key={p.id} value={String(p.id)} sx={{ fontWeight: 600 }}>
                  <span style={{ fontSize: 10, fontWeight: 800, textTransform: 'uppercase', color: p.type === NT.SECTOR ? '#16a34a' : '#3b82f6', marginLeft: 6 }}>
                    [{p.type === NT.SECTOR ? 'قطاع' : 'مرحلة'}]
                  </span>
                  {' '}{p.name}
                </MenuItem>
              ))}
            </TextField>
          )}

          {/* Name */}
          <TextField
            fullWidth autoFocus
            label={
              modalType === NT.SECTOR    ? t('farm.sector_name',    'اسم القطاع')
              : modalType === NT.STAGE   ? t('farm.stage_name',     'اسم المرحلة')
              : t('farm.enclosure_name', 'اسم الحوشة')
            }
            value={form.name}
            onChange={e => setForm({ ...form, name: e.target.value })}
            onKeyDown={e => e.key === 'Enter' && !isSaveDisabled && handleSave()}
            InputProps={{ sx: { borderRadius: 2 } }}
          />
        </DialogContent>

        <DialogActions sx={{ p: 2, gap: 1 }}>
          <Button onClick={() => setModalOpen(false)} sx={{ fontWeight: 700, color: '#64748b' }}>
            {t('common.cancel', 'إلغاء')}
          </Button>
          <Button
            onClick={handleSave}
            variant="contained"
            disabled={isSaveDisabled}
            sx={{ borderRadius: 2, px: 3, fontWeight: 800, bgcolor: '#16a34a', '&:hover': { bgcolor: '#15803d' } }}
          >
            {formLoading ? <CircularProgress size={18} color="inherit" /> : t('common.save', 'حفظ')}
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default FarmStructure;
