import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Button, TextField, MenuItem, 
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, 
  Paper, IconButton, Dialog, DialogTitle, DialogContent, DialogActions, 
  CircularProgress, Chip, Switch, FormControlLabel, Tabs, Tab
} from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon, Add as AddIcon } from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useTranslation } from 'react-i18next';
import { reportsApi } from '../../../services/reportsApi';
import { useSnackbar } from '../../../contexts/SnackbarContext';
import ConfirmDialog from '../../../components/ConfirmDialog';

const customFieldSchema = z.object({
  name: z.string().min(1, 'اسم الحقل مطلوب'),
  field_type: z.enum(['text', 'number', 'date', 'dropdown', 'boolean'], { required_error: 'النوع مطلوب' }),
  applies_to: z.number().min(1, 'اختر النموذج الذي يطبق عليه'),
  is_required: z.boolean()
});

const optionSchema = z.object({
  name: z.string().min(1, 'اسم الخيار مطلوب'),
  category: z.enum(['variety', 'unit', 'contractor', 'enclosure'], { required_error: 'الفئة مطلوبة' }),
  is_active: z.boolean()
});

const FIELD_TYPES_AR = {
  text: 'نص', number: 'رقم', date: 'تاريخ', dropdown: 'قائمة منسدلة', boolean: 'نعم/لا'
};

const CATEGORIES_AR = {
  variety: 'الصنف', unit: 'الوحدة', contractor: 'المقاول', enclosure: 'الحوشة'
};

const MODEL_CHOICES = [
  { id: 14, name: 'تقرير المهام اليومية (DailyTaskReport)', model: 'dailytaskreport' },
  { id: 15, name: 'تقرير التسميد (FertilizationReport)', model: 'fertilizationreport' },
  { id: 16, name: 'تقرير الري (IrrigationReport)', model: 'irrigationreport' }
];

const CustomFieldsManager = () => {
  const { t } = useTranslation();
  const { showSnackbar } = useSnackbar();
  
  const [tabIndex, setTabIndex] = useState(0);
  
  const [fields, setFields] = useState([]);
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(true);

  const [openFieldModal, setOpenFieldModal] = useState(false);
  const [openOptionModal, setOpenOptionModal] = useState(false);
  const [editingId, setEditingId] = useState(null);

  const [confirmOpen, setConfirmOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null); // { type: 'field'|'option', id }

  const fieldForm = useForm({
    resolver: zodResolver(customFieldSchema),
    defaultValues: { name: '', field_type: 'text', applies_to: 14, is_required: false }
  });

  const optionForm = useForm({
    resolver: zodResolver(optionSchema),
    defaultValues: { name: '', category: 'variety', is_active: true }
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      const [fieldsRes, optionsRes] = await Promise.all([
        reportsApi.getCustomFields(),
        reportsApi.getOptions()
      ]);
      setFields(fieldsRes.data.results || fieldsRes.data);
      setOptions(optionsRes.data.results || optionsRes.data);
    } catch (err) {
      showSnackbar('فشل في جلب البيانات', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleOpenFieldModal = (field = null) => {
    if (field) {
      setEditingId(field.id);
      fieldForm.reset(field);
    } else {
      setEditingId(null);
      fieldForm.reset({ name: '', field_type: 'text', applies_to: 14, is_required: false });
    }
    setOpenFieldModal(true);
  };

  const handleOpenOptionModal = (opt = null) => {
    if (opt) {
      setEditingId(opt.id);
      optionForm.reset(opt);
    } else {
      setEditingId(null);
      optionForm.reset({ name: '', category: 'variety', is_active: true });
    }
    setOpenOptionModal(true);
  };

  const onFieldSubmit = async (data) => {
    try {
      if (editingId) await reportsApi.updateCustomField(editingId, data);
      else await reportsApi.createCustomField(data);
      setOpenFieldModal(false);
      showSnackbar('تم الحفظ بنجاح');
      fetchData();
    } catch (err) {
      showSnackbar('حدث خطأ أثناء الحفظ', 'error');
    }
  };

  const onOptionSubmit = async (data) => {
    try {
      if (editingId) await reportsApi.updateOption(editingId, data);
      else await reportsApi.createOption(data);
      setOpenOptionModal(false);
      showSnackbar('تم الحفظ بنجاح');
      fetchData();
    } catch (err) {
      showSnackbar('حدث خطأ أثناء الحفظ', 'error');
    }
  };

  const executeDelete = async () => {
    try {
      if (deleteTarget.type === 'field') {
        await reportsApi.deleteCustomField(deleteTarget.id);
      } else {
        await reportsApi.deleteOption(deleteTarget.id);
      }
      showSnackbar('تم الحذف بنجاح');
      fetchData();
    } catch (err) {
      showSnackbar('فشل الحذف. قد يكون العنصر مستخدماً.', 'error');
    } finally {
      setConfirmOpen(false);
    }
  };

  if (loading && !fields.length && !options.length) return <CircularProgress sx={{ display: 'block', mx: 'auto', mt: 4 }} />;

  return (
    <Box>
      <Typography variant="h5" fontWeight="800" mb={3}>إعدادات النماذج الديناميكية</Typography>
      
      <Paper elevation={0} sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabIndex} onChange={(e, v) => setTabIndex(v)} sx={{ '& .MuiTab-root': { fontWeight: 700 } }}>
          <Tab label="قوائم الخيارات" />
          <Tab label="الحقول المخصصة" />
        </Tabs>
      </Paper>

      {/* Options Tab */}
      {tabIndex === 0 && (
        <Box>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6" fontWeight="700">إدارة قوائم الخيارات</Typography>
            <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpenOptionModal()}>إضافة خيار</Button>
          </Box>
          <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid #e2e8f0', borderRadius: 3 }}>
            <Table>
              <TableHead sx={{ bgcolor: '#f8fafc' }}>
                <TableRow>
                  <TableCell sx={{ fontWeight: 600 }}>الاسم</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>الفئة</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>مفعل</TableCell>
                  <TableCell sx={{ fontWeight: 600 }} align="right">إجراءات</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {options.map(opt => (
                  <TableRow key={opt.id} hover>
                    <TableCell fontWeight="500">{opt.name}</TableCell>
                    <TableCell><Chip size="small" label={CATEGORIES_AR[opt.category]} color="primary" variant="outlined" /></TableCell>
                    <TableCell>{opt.is_active ? <Chip size="small" label="نعم" color="success"/> : <Chip size="small" label="لا" color="error"/>}</TableCell>
                    <TableCell align="right">
                      <IconButton size="small" color="primary" onClick={() => handleOpenOptionModal(opt)}><EditIcon fontSize="small"/></IconButton>
                      <IconButton size="small" color="error" onClick={() => { setDeleteTarget({ type: 'option', id: opt.id }); setConfirmOpen(true); }}><DeleteIcon fontSize="small"/></IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}

      {/* Fields Tab */}
      {tabIndex === 1 && (
        <Box>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6" fontWeight="700">إدارة الحقول المخصصة</Typography>
            <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpenFieldModal()}>إضافة حقل</Button>
          </Box>
          <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid #e2e8f0', borderRadius: 3 }}>
            <Table>
              <TableHead sx={{ bgcolor: '#f8fafc' }}>
                <TableRow>
                  <TableCell sx={{ fontWeight: 600 }}>اسم الحقل</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>النوع</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>يطبق على</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>مطلوب</TableCell>
                  <TableCell sx={{ fontWeight: 600 }} align="right">إجراءات</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {fields.map(field => (
                  <TableRow key={field.id} hover>
                    <TableCell fontWeight="500">{field.name}</TableCell>
                    <TableCell><Chip size="small" label={FIELD_TYPES_AR[field.field_type]} color="primary" variant="outlined" /></TableCell>
                    <TableCell>{field.applies_to_model || 'DailyTaskReport'}</TableCell>
                    <TableCell>{field.is_required ? <Chip size="small" label="نعم" color="error"/> : <Chip size="small" label="لا" color="default"/>}</TableCell>
                    <TableCell align="right">
                      <IconButton size="small" color="primary" onClick={() => handleOpenFieldModal(field)}><EditIcon fontSize="small"/></IconButton>
                      <IconButton size="small" color="error" onClick={() => { setDeleteTarget({ type: 'field', id: field.id }); setConfirmOpen(true); }}><DeleteIcon fontSize="small"/></IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}

      {/* Option Modal */}
      <Dialog open={openOptionModal} onClose={() => setOpenOptionModal(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 3 } }}>
        <DialogTitle sx={{ fontWeight: 700 }}>{editingId ? 'تعديل خيار' : 'إضافة خيار جديد'}</DialogTitle>
        <DialogContent dividers>
          <Box component="form" id="option-form" onSubmit={optionForm.handleSubmit(onOptionSubmit)} sx={{ display: 'flex', flexDirection: 'column', gap: 3, pt: 1 }}>
            <Controller name="name" control={optionForm.control} render={({ field }) => (
              <TextField {...field} label="الاسم" fullWidth error={!!optionForm.formState.errors.name} helperText={optionForm.formState.errors.name?.message} />
            )} />
            <Controller name="category" control={optionForm.control} render={({ field }) => (
              <TextField {...field} select label="الفئة" fullWidth error={!!optionForm.formState.errors.category} helperText={optionForm.formState.errors.category?.message}>
                {Object.entries(CATEGORIES_AR).map(([k, v]) => <MenuItem key={k} value={k}>{v}</MenuItem>)}
              </TextField>
            )} />
            <Controller name="is_active" control={optionForm.control} render={({ field }) => (
              <FormControlLabel control={<Switch checked={field.value} onChange={(e) => field.onChange(e.target.checked)} color="primary" />} label="مفعل" />
            )} />
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 2, px: 3 }}>
          <Button onClick={() => setOpenOptionModal(false)}>إلغاء</Button>
          <Button type="submit" form="option-form" variant="contained" disabled={optionForm.formState.isSubmitting}>حفظ</Button>
        </DialogActions>
      </Dialog>

      {/* Field Modal */}
      <Dialog open={openFieldModal} onClose={() => setOpenFieldModal(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 3 } }}>
        <DialogTitle sx={{ fontWeight: 700 }}>{editingId ? 'تعديل حقل' : 'إضافة حقل جديد'}</DialogTitle>
        <DialogContent dividers>
          <Box component="form" id="field-form" onSubmit={fieldForm.handleSubmit(onFieldSubmit)} sx={{ display: 'flex', flexDirection: 'column', gap: 3, pt: 1 }}>
            <Controller name="name" control={fieldForm.control} render={({ field }) => (
              <TextField {...field} label="الاسم" fullWidth error={!!fieldForm.formState.errors.name} helperText={fieldForm.formState.errors.name?.message} />
            )} />
            <Controller name="field_type" control={fieldForm.control} render={({ field }) => (
              <TextField {...field} select label="النوع" fullWidth error={!!fieldForm.formState.errors.field_type}>
                {Object.entries(FIELD_TYPES_AR).map(([k, v]) => <MenuItem key={k} value={k}>{v}</MenuItem>)}
              </TextField>
            )} />
            <Controller name="applies_to" control={fieldForm.control} render={({ field }) => (
              <TextField {...field} select label="يطبق على" fullWidth error={!!fieldForm.formState.errors.applies_to}>
                {MODEL_CHOICES.map(m => <MenuItem key={m.id} value={m.id}>{m.name}</MenuItem>)}
              </TextField>
            )} />
            <Controller name="is_required" control={fieldForm.control} render={({ field }) => (
              <FormControlLabel control={<Switch checked={field.value} onChange={(e) => field.onChange(e.target.checked)} color="primary" />} label="إجباري" />
            )} />
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 2, px: 3 }}>
          <Button onClick={() => setOpenFieldModal(false)}>إلغاء</Button>
          <Button type="submit" form="field-form" variant="contained" disabled={fieldForm.formState.isSubmitting}>حفظ</Button>
        </DialogActions>
      </Dialog>

      <ConfirmDialog 
        open={confirmOpen} 
        title="تأكيد الحذف" 
        message="هل أنت متأكد من الحذف؟ سيؤدي ذلك إلى إزالة العنصر نهائياً." 
        onConfirm={executeDelete} 
        onCancel={() => setConfirmOpen(false)} 
      />
    </Box>
  );
};

export default CustomFieldsManager;
