# PHASE 01 — FarmStructure Adaptive UI

## 🎯 الهدف
تحويل شجرة هيكل المزرعة من شجرة ثابتة الحجم إلى شجرة **ذكية متكيفة** — كلما زاد عدد العناصر، صغر حجم كل عنصر تلقائياً ليتناسبوا في نفس المساحة، مع إضافة Collapse/Expand وSearch.

---

## 📁 الملفات المتأثرة

```
Front-End/src/pages/farm/FarmStructure.jsx   ← إعادة كتابة كاملة
Front-End/src/pages/farm/FarmStructure.css   ← استبدال كامل
```

لا تغيير في Backend — الـ API موجودة وتعمل.

---

## 📐 قواعد التصميم

### الحجم يتحدد بعدد الأشقاء (siblings) في نفس المستوى:
```
1–3   عناصر → size: LG  → padding: 12px 16px  | font: 14px | icon: 24px | min-h: 64px
4–6   عناصر → size: MD  → padding: 8px 12px   | font: 12px | icon: 20px | min-h: 48px
7–12  عناصر → size: SM  → padding: 6px 8px    | font: 11px | icon: 16px | min-h: 36px
13+   عناصر → size: XS  → padding: 4px 6px    | font: 10px | icon: 14px | min-h: 28px
```

### Layout:
- SECTOR (level 0): كل قطاع في row منفصلة — عرض كامل
- STAGE (level 1): flex-wrap أفقي داخل القطاع الأب
- ENCLOSURE (level 2): CSS grid بـ columns ديناميكية:
  - 1–4   enclosures → `grid-cols-2`
  - 5–8   enclosures → `grid-cols-3`
  - 9–12  enclosures → `grid-cols-4`
  - 13+   enclosures → `grid-cols-5`
- كل branch يمكن طيّه (Collapse/Expand) بزر سهم
- الـ Container: `overflow-x: auto` لو الشجرة عريضة

---

## 🔁 الكود الكامل

### 1. استبدل `FarmStructure.css` بالكامل بهذا:

```css
/* ═══════════════════════════════════════════════
   FarmStructure.css — Adaptive Tree Styles
   ═══════════════════════════════════════════════ */

.farm-tree-root {
  overflow-x: auto;
  padding: 8px;
}

/* ── Node Sizes ── */
.tree-node { display: flex; align-items: center; border-radius: 12px; border: 1px solid; transition: all 0.2s ease; cursor: default; position: relative; }

.tree-node-lg { padding: 12px 16px; min-height: 64px; font-size: 14px; }
.tree-node-md { padding: 8px 12px;  min-height: 48px; font-size: 12px; }
.tree-node-sm { padding: 6px 8px;   min-height: 36px; font-size: 11px; }
.tree-node-xs { padding: 4px 6px;   min-height: 28px; font-size: 10px; }

.tree-node-icon-lg { width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.tree-node-icon-md { width: 28px; height: 28px; border-radius: 6px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.tree-node-icon-sm { width: 22px; height: 22px; border-radius: 5px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.tree-node-icon-xs { width: 18px; height: 18px; border-radius: 4px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }

/* ── Node Type Colors ── */
.node-sector    { background-color: #f0fdf4; border-color: #bbf7d0; }
.node-sector:hover { border-color: #16a34a; box-shadow: 0 2px 8px rgba(22,163,74,0.15); }
.node-sector .tree-node-icon-lg,
.node-sector .tree-node-icon-md,
.node-sector .tree-node-icon-sm,
.node-sector .tree-node-icon-xs { background-color: #dcfce7; color: #15803d; }

.node-stage     { background-color: #eff6ff; border-color: #bfdbfe; }
.node-stage:hover { border-color: #3b82f6; box-shadow: 0 2px 8px rgba(59,130,246,0.15); }
.node-stage .tree-node-icon-lg,
.node-stage .tree-node-icon-md,
.node-stage .tree-node-icon-sm,
.node-stage .tree-node-icon-xs { background-color: #dbeafe; color: #1d4ed8; }

.node-enclosure { background-color: #fff7ed; border-color: #fed7aa; }
.node-enclosure:hover { border-color: #f97316; box-shadow: 0 2px 8px rgba(249,115,22,0.15); }
.node-enclosure .tree-node-icon-lg,
.node-enclosure .tree-node-icon-md,
.node-enclosure .tree-node-icon-sm,
.node-enclosure .tree-node-icon-xs { background-color: #ffedd5; color: #c2410c; }

/* ── Actions (hidden by default, show on hover) ── */
.tree-node-actions { display: flex; gap: 2px; opacity: 0; transition: opacity 0.15s ease; margin-right: auto; }
.tree-node:hover .tree-node-actions { opacity: 1; }

/* ── Connector Lines ── */
.tree-children-connector { border-right: 2px dashed #e2e8f0; margin-right: 20px; padding-right: 12px; }

/* ── Count Badge ── */
.tree-count-badge {
  display: inline-flex; align-items: center; justify-content: center;
  background: #f1f5f9; color: #64748b; border-radius: 9999px;
  font-size: 10px; font-weight: 700; padding: 1px 6px; min-width: 20px;
  flex-shrink: 0;
}

/* ── Collapse Button ── */
.tree-collapse-btn {
  width: 20px; height: 20px; border-radius: 50%; background: #e2e8f0;
  border: none; cursor: pointer; display: flex; align-items: center; justify-content: center;
  color: #64748b; transition: all 0.2s; flex-shrink: 0; padding: 0;
}
.tree-collapse-btn:hover { background: #cbd5e1; color: #334155; }

/* ── Enclosure Grid ── */
.enclosure-grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; }
.enclosure-grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }
.enclosure-grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; }
.enclosure-grid-5 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; }

/* ── Stage Flex Wrap ── */
.stages-flex { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
.stage-item  { flex: 1 1 280px; min-width: 220px; max-width: 480px; }

/* ── Search Highlight ── */
.node-highlighted { outline: 2px solid #f59e0b; outline-offset: 2px; }
.node-dimmed      { opacity: 0.35; }
```

---

### 2. استبدل `FarmStructure.jsx` بالكامل بهذا:

```jsx
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

// ─── Helpers ─────────────────────────────────────────────────────────────────

/** حساب الـ size class بناءً على عدد الأشقاء */
const getSizeClass = (count) => {
  if (count <= 3)  return 'lg';
  if (count <= 6)  return 'md';
  if (count <= 12) return 'sm';
  return 'xs';
};

/** حساب الـ icon size بناءً على الـ size class */
const getIconSize = (size) => ({ lg: 22, md: 18, sm: 15, xs: 13 }[size] || 18);

/** حساب grid columns للـ enclosures */
const getEnclosureGrid = (count) => {
  if (count <= 4)  return 'enclosure-grid-2';
  if (count <= 8)  return 'enclosure-grid-3';
  if (count <= 12) return 'enclosure-grid-4';
  return 'enclosure-grid-5';
};

/** هل العنصر أو أحد أبنائه يطابق البحث */
const nodeMatchesSearch = (node, q) => {
  if (!q) return true;
  const lower = q.toLowerCase();
  if (node.name.toLowerCase().includes(lower)) return true;
  return (node.children || []).some(c => nodeMatchesSearch(c, q));
};

// ─── NodeIcon ────────────────────────────────────────────────────────────────
const NodeIcon = ({ type, size }) => {
  const px = getIconSize(size);
  const sx = { fontSize: px };
  switch (type) {
    case NT.SECTOR:    return <SectorIcon sx={sx} />;
    case NT.STAGE:     return <StageIcon sx={sx} />;
    case NT.ENCLOSURE: return <EnclosureIcon sx={sx} />;
    default:           return <FarmIcon sx={sx} />;
  }
};

// ─── EnclosureNode (leaf) ────────────────────────────────────────────────────
const EnclosureNode = ({ node, size, onEdit, onDelete, searchQuery }) => {
  const { t } = useTranslation();
  const matched = nodeMatchesSearch(node, searchQuery);
  return (
    <div
      className={`tree-node node-enclosure tree-node-${size} ${!matched ? 'node-dimmed' : ''} ${matched && searchQuery && node.name.toLowerCase().includes(searchQuery.toLowerCase()) ? 'node-highlighted' : ''}`}
    >
      <div className={`tree-node-icon-${size}`}>
        <NodeIcon type={NT.ENCLOSURE} size={size} />
      </div>
      <div style={{ flex: 1, minWidth: 0, margin: '0 6px' }}>
        <p style={{ fontWeight: 700, color: '#1e293b', margin: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{node.name}</p>
        {size === 'lg' && (
          <p style={{ fontSize: 9, fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#94a3b8', margin: 0 }}>
            {t('farm.enclosure', 'حوشة')}
          </p>
        )}
      </div>
      <div className="tree-node-actions">
        <Tooltip title={t('common.edit', 'تعديل')}><IconButton size="small" onClick={() => onEdit(node)} sx={{ color: '#64748b', p: '3px' }}><EditIcon sx={{ fontSize: 14 }} /></IconButton></Tooltip>
        <Tooltip title={t('common.delete', 'حذف')}><IconButton size="small" onClick={() => onDelete(node)} sx={{ color: '#ef4444', p: '3px' }}><DeleteIcon sx={{ fontSize: 14 }} /></IconButton></Tooltip>
      </div>
    </div>
  );
};

// ─── StageNode ───────────────────────────────────────────────────────────────
const StageNode = ({ node, siblingCount, onAdd, onEdit, onDelete, searchQuery }) => {
  const { t } = useTranslation();
  const [collapsed, setCollapsed] = useState(false);
  const size = getSizeClass(siblingCount);
  const enclosures = (node.children || []).filter(c => c.type === NT.ENCLOSURE);
  const gridClass = getEnclosureGrid(enclosures.length);
  const encSize = getSizeClass(enclosures.length);
  const matched = nodeMatchesSearch(node, searchQuery);

  return (
    <div className="stage-item">
      <div
        className={`tree-node node-stage tree-node-${size} ${!matched ? 'node-dimmed' : ''} ${matched && searchQuery && node.name.toLowerCase().includes(searchQuery.toLowerCase()) ? 'node-highlighted' : ''}`}
        style={{ marginBottom: enclosures.length > 0 && !collapsed ? 6 : 0 }}
      >
        {enclosures.length > 0 && (
          <button className="tree-collapse-btn" onClick={() => setCollapsed(!collapsed)}>
            {collapsed ? <CollapseIcon sx={{ fontSize: 12 }} /> : <ExpandIcon sx={{ fontSize: 12 }} />}
          </button>
        )}
        <div className={`tree-node-icon-${size}`} style={{ margin: '0 6px' }}>
          <NodeIcon type={NT.STAGE} size={size} />
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <p style={{ fontWeight: 700, color: '#1e293b', margin: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{node.name}</p>
          {size !== 'xs' && (
            <p style={{ fontSize: 9, fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#94a3b8', margin: 0 }}>
              {t('farm.stage', 'مرحلة')}
            </p>
          )}
        </div>
        {enclosures.length > 0 && <span className="tree-count-badge">{enclosures.length}</span>}
        <div className="tree-node-actions" style={{ marginRight: 0, marginLeft: 4 }}>
          <Tooltip title={t('farm.add_enclosure', 'إضافة حوشة')}><IconButton size="small" onClick={() => onAdd(node, NT.ENCLOSURE)} sx={{ color: '#16a34a', p: '3px' }}><AddIcon sx={{ fontSize: 14 }} /></IconButton></Tooltip>
          <Tooltip title={t('common.edit', 'تعديل')}><IconButton size="small" onClick={() => onEdit(node)} sx={{ color: '#64748b', p: '3px' }}><EditIcon sx={{ fontSize: 14 }} /></IconButton></Tooltip>
          <Tooltip title={t('common.delete', 'حذف')}><IconButton size="small" onClick={() => onDelete(node)} sx={{ color: '#ef4444', p: '3px' }}><DeleteIcon sx={{ fontSize: 14 }} /></IconButton></Tooltip>
        </div>
      </div>

      {!collapsed && enclosures.length > 0 && (
        <div className={gridClass} style={{ marginTop: 4, paddingRight: 8, borderRight: '2px dashed #e2e8f0' }}>
          {enclosures.map(enc => (
            <EnclosureNode key={enc.id} node={enc} size={encSize} onEdit={onEdit} onDelete={onDelete} searchQuery={searchQuery} />
          ))}
        </div>
      )}
    </div>
  );
};

// ─── SectorNode ──────────────────────────────────────────────────────────────
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
      {/* Sector Header */}
      <div
        className={`tree-node node-sector tree-node-${size} ${!matched ? 'node-dimmed' : ''} ${matched && searchQuery && node.name.toLowerCase().includes(searchQuery.toLowerCase()) ? 'node-highlighted' : ''}`}
      >
        {hasChildren && (
          <button className="tree-collapse-btn" onClick={() => setCollapsed(!collapsed)}>
            {collapsed ? <CollapseIcon sx={{ fontSize: 12 }} /> : <ExpandIcon sx={{ fontSize: 12 }} />}
          </button>
        )}
        <div className={`tree-node-icon-${size}`} style={{ margin: '0 8px' }}>
          <NodeIcon type={NT.SECTOR} size={size} />
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <p style={{ fontWeight: 800, color: '#1e293b', margin: 0, fontSize: size === 'xs' ? 11 : 14 }}>{node.name}</p>
          {size !== 'xs' && (
            <p style={{ fontSize: 9, fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#94a3b8', margin: 0 }}>
              {t('farm.sector', 'قطاع')}
            </p>
          )}
        </div>
        {childCount > 0 && <span className="tree-count-badge">{childCount}</span>}
        <div className="tree-node-actions" style={{ marginRight: 0, marginLeft: 4 }}>
          <Tooltip title={t('farm.add_stage', 'إضافة مرحلة')}><IconButton size="small" onClick={() => onAdd(node, NT.STAGE)} sx={{ color: '#16a34a', p: '3px' }}><AddIcon sx={{ fontSize: 16 }} /></IconButton></Tooltip>
          <Tooltip title={t('common.edit', 'تعديل')}><IconButton size="small" onClick={() => onEdit(node)} sx={{ color: '#64748b', p: '3px' }}><EditIcon sx={{ fontSize: 16 }} /></IconButton></Tooltip>
          <Tooltip title={t('common.delete', 'حذف')}><IconButton size="small" onClick={() => onDelete(node)} sx={{ color: '#ef4444', p: '3px' }}><DeleteIcon sx={{ fontSize: 16 }} /></IconButton></Tooltip>
        </div>
      </div>

      {/* Children */}
      {!collapsed && hasChildren && (
        <div style={{ paddingRight: 24, marginTop: 6, borderRight: '2px solid #dcfce7' }}>
          {stages.length > 0 ? (
            <div className="stages-flex">
              {stages.map(stage => (
                <StageNode
                  key={stage.id}
                  node={stage}
                  siblingCount={stages.length}
                  onAdd={onAdd}
                  onEdit={onEdit}
                  onDelete={onDelete}
                  searchQuery={searchQuery}
                />
              ))}
            </div>
          ) : (
            /* Enclosures مباشرة تحت القطاع (بدون مراحل) */
            <div className={getEnclosureGrid(directEnclosures.length)} style={{ marginTop: 6 }}>
              {directEnclosures.map(enc => (
                <EnclosureNode
                  key={enc.id}
                  node={enc}
                  size={getSizeClass(directEnclosures.length)}
                  onEdit={onEdit}
                  onDelete={onDelete}
                  searchQuery={searchQuery}
                />
              ))}
            </div>
          )}
        </div>
      )}
    </li>
  );
};

// ─── Main Component ───────────────────────────────────────────────────────────
const FarmStructure = () => {
  const { t } = useTranslation();
  const [tree, setTree] = useState([]);
  const [farmInfo, setFarmInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [modalType, setModalType] = useState(NT.SECTOR);
  const [editMode, setEditMode] = useState(false);
  const [currentNode, setCurrentNode] = useState(null);
  const [form, setForm] = useState({ name: '', sectorId: '', stageId: '' });
  const [formLoading, setFormLoading] = useState(false);

  // ── Fetch ──────────────────────────────────────────────────────────────────
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

  // ── Derived ────────────────────────────────────────────────────────────────
  const sectors = useMemo(() => tree.filter(n => n.type === NT.SECTOR), [tree]);
  const stagesOfSelectedSector = useMemo(() => {
    if (!form.sectorId) return [];
    return (tree.find(n => n.id === Number(form.sectorId))?.children || []).filter(c => c.type === NT.STAGE);
  }, [tree, form.sectorId]);

  // ── Handlers ───────────────────────────────────────────────────────────────
  const handleOpenAdd = (parent, type) => {
    setEditMode(false);
    setCurrentNode(null);
    setModalType(type);
    const sectorId = type === NT.STAGE ? String(parent?.id || '') : (type === NT.ENCLOSURE && parent?.type === NT.SECTOR ? String(parent.id) : '');
    const stageId  = type === NT.ENCLOSURE && parent?.type === NT.STAGE ? String(parent.id) : '';
    setForm({ name: '', sectorId, stageId });
    setModalOpen(true);
  };

  const handleOpenEdit = (node) => {
    setEditMode(true);
    setCurrentNode(node);
    setModalType(node.type);
    setForm({ name: node.name, sectorId: '', stageId: '' });
    setModalOpen(true);
  };

  const handleSave = async () => {
    setFormLoading(true);
    try {
      if (editMode) {
        await updateLocationNode(currentNode.id, { name: form.name });
      } else {
        const parent = modalType === NT.SECTOR ? null : (form.stageId || form.sectorId || null);
        await createLocationNode({ name: form.name, type: modalType, parent: parent ? Number(parent) : null });
      }
      setModalOpen(false);
      fetchData();
    } catch (err) {
      const msg = err.response?.data?.parent || err.response?.data?.name || err.response?.data?.detail || t('common.error_save', 'فشل الحفظ');
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

  // ── Render ─────────────────────────────────────────────────────────────────
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
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenAdd(null, NT.SECTOR)}
          sx={{ borderRadius: 3, px: 3, py: 1.2, fontWeight: 800, bgcolor: '#16a34a', '&:hover': { bgcolor: '#15803d' }, boxShadow: '0 4px 12px rgba(22,163,74,0.25)', whiteSpace: 'nowrap' }}
        >
          {t('farm.add_sector_btn', 'إضافة قطاع')}
        </Button>
      </div>

      {error && <Alert severity="error" sx={{ mb: 3, borderRadius: 3 }}>{error}</Alert>}

      {/* ── Search ── */}
      <TextField
        fullWidth
        size="small"
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
              <p className="font-bold text-sm">{t('farm.no_structure', 'لا يوجد هيكل معرف. ابدأ بإضافة أول قطاع.')}</p>
            </div>
          ) : (
            <ul style={{ padding: 0, margin: 0 }}>
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
            </ul>
          )}
        </div>
      </Card>

      {/* ── Modal ── */}
      <Dialog open={modalOpen} onClose={() => setModalOpen(false)} maxWidth="xs" fullWidth PaperProps={{ sx: { borderRadius: 4, p: 1 } }}>
        <DialogTitle sx={{ fontWeight: 900, fontSize: '1.1rem', color: '#1e293b' }}>
          {editMode ? t('farm.edit_node', 'تعديل العنصر') : (
            modalType === NT.SECTOR ? t('farm.add_sector_title', 'إضافة قطاع جديد') :
            modalType === NT.STAGE  ? t('farm.add_stage_title', 'إضافة مرحلة جديدة') :
            t('farm.add_enclosure_title', 'إضافة حوشة جديدة')
          )}
        </DialogTitle>

        <DialogContent sx={{ pt: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* Sector select (for STAGE and ENCLOSURE) */}
          {!editMode && modalType !== NT.SECTOR && (
            <TextField select fullWidth label={t('farm.select_sector', 'اختر القطاع')} value={form.sectorId}
              onChange={e => setForm({ ...form, sectorId: e.target.value, stageId: '' })}
              InputProps={{ sx: { borderRadius: 2 } }}>
              {sectors.map(s => <MenuItem key={s.id} value={String(s.id)} sx={{ fontWeight: 600 }}>{s.name}</MenuItem>)}
            </TextField>
          )}

          {/* Stage select (for ENCLOSURE only) */}
          {!editMode && modalType === NT.ENCLOSURE && form.sectorId && stagesOfSelectedSector.length > 0 && (
            <TextField select fullWidth label={t('farm.select_stage_optional', 'اختر المرحلة (اختياري)')} value={form.stageId}
              onChange={e => setForm({ ...form, stageId: e.target.value })}
              InputProps={{ sx: { borderRadius: 2 } }}>
              <MenuItem value=""><em>{t('common.none', 'بدون مرحلة')}</em></MenuItem>
              {stagesOfSelectedSector.map(st => <MenuItem key={st.id} value={String(st.id)} sx={{ fontWeight: 600 }}>{st.name}</MenuItem>)}
            </TextField>
          )}

          {/* Name */}
          <TextField
            fullWidth autoFocus
            label={
              modalType === NT.SECTOR ? t('farm.sector_name', 'اسم القطاع') :
              modalType === NT.STAGE  ? t('farm.stage_name', 'اسم المرحلة') :
              t('farm.enclosure_name', 'اسم الحوشة')
            }
            value={form.name}
            onChange={e => setForm({ ...form, name: e.target.value })}
            onKeyDown={e => e.key === 'Enter' && form.name && handleSave()}
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
            disabled={formLoading || !form.name || (!editMode && modalType !== NT.SECTOR && !form.sectorId)}
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
```

---

## ✅ Checklist للتحقق بعد التنفيذ

- [ ] الشجرة تظهر بشكل صحيح مع بيانات حقيقية
- [ ] كلما زاد عدد العناصر في مستوى → حجم كل عنصر يصغر
- [ ] زر Collapse/Expand يخفي/يظهر الأبناء
- [ ] البحث يبرز العناصر المطابقة ويخفف الأخرى
- [ ] عند الـ hover → تظهر أزرار الإضافة/التعديل/الحذف
- [ ] الـ count badge يظهر عدد الأبناء
- [ ] الـ RTL يعمل صح (الـ connectors على اليمين)
- [ ] الـ Enclosures تتوزع في grid حسب عددها
- [ ] الـ Stages تتوزع أفقياً وتتكسر لصف جديد إذا زادوا

## 🚫 لا تغير
- لا تغيير في Backend API
- لا تغيير في `features/farm/services.js`
- لا تغيير في أي ملف آخر
