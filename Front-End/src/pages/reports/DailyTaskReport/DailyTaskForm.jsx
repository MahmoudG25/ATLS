import React, { useState, useEffect } from 'react';
import { 
  Box, Card, Typography, Button, TextField, 
  Stepper, Step, StepLabel, CircularProgress, Alert, Grid, Autocomplete, IconButton
} from '@mui/material';
import { Add as AddIcon, Remove as RemoveIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { reportsApi } from '../../../services/reportsApi';
import DynamicFieldsRenderer from '../shared/DynamicFieldsRenderer';

import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import dayjs from 'dayjs';

const taskSchema = z.object({
  report_date: z.any(), // dayjs object
  engineer: z.number().min(1, 'المهندس مطلوب'),
  sector: z.number().min(1, 'القطاع مطلوب'),
  variety: z.number().min(1, 'الصنف مطلوب'),
  enclosure: z.number().nullable().optional(),
  work_location: z.string().min(1, 'مكان العمل مطلوب'),
  
  operation: z.number().min(1, 'العملية الفنية مطلوبة'),
  unit: z.number().min(1, 'الوحدة مطلوبة'),
  company_workers: z.coerce.number().min(0),
  contractor_workers: z.coerce.number().min(0),
  contractor: z.number().nullable().optional(),
  
  actual_productivity: z.coerce.number().min(0),
  work_hours: z.coerce.number().min(0.5, 'يجب إدخال نصف ساعة على الأقل'),
  overtime_hours: z.coerce.number().optional(),
  overtime_productivity: z.coerce.number().optional(),
  notes: z.string().optional(),

  custom_fields: z.record(z.any()).optional()
});

const steps = ['البيانات الأساسية', 'تفاصيل العمل', 'الإنتاجية والحقول المخصصة'];

const StepperInput = ({ value, onChange, label, error, helperText }) => (
  <Box>
    <Typography variant="caption" color="textSecondary" sx={{ mb: 1, display: 'block' }}>{label}</Typography>
    <Box display="flex" alignItems="center" border="1px solid" borderColor={error ? 'error.main' : 'divider'} borderRadius={1} p={0.5}>
      <IconButton size="small" onClick={() => onChange(Math.max(0, value - 1))} color="error"><RemoveIcon /></IconButton>
      <Typography variant="h6" sx={{ flexGrow: 1, textAlign: 'center', width: 40 }}>{value}</Typography>
      <IconButton size="small" onClick={() => onChange(value + 1)} color="primary"><AddIcon /></IconButton>
    </Box>
    {error && <Typography variant="caption" color="error">{helperText}</Typography>}
  </Box>
);

const DailyTaskForm = () => {
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(0);
  const [submitError, setSubmitError] = useState('');

  // Dropdown options states
  const [users, setUsers] = useState([]);
  const [sectors, setSectors] = useState([]);
  const [operations, setOperations] = useState([]);
  const [varieties, setVarieties] = useState([]);
  const [units, setUnits] = useState([]);
  const [contractors, setContractors] = useState([]);
  const [enclosures, setEnclosures] = useState([]);

  const { control, handleSubmit, trigger, formState: { errors, isSubmitting } } = useForm({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      report_date: dayjs(),
      engineer: null, sector: null, variety: null, enclosure: null, work_location: '',
      operation: null, unit: null, company_workers: 0, contractor_workers: 0, contractor: null,
      actual_productivity: 0, work_hours: 8, overtime_hours: 0, overtime_productivity: 0, notes: '',
      custom_fields: {}
    }
  });

  useEffect(() => {
    reportsApi.getUsers().then(res => setUsers(res.data.results || res.data)).catch(console.error);
    reportsApi.getSectors().then(res => setSectors(res.data.results || res.data)).catch(console.error);
    reportsApi.getOperations().then(res => setOperations(res.data.results || res.data)).catch(console.error);
    
    reportsApi.getOptions('variety').then(res => setVarieties(res.data.results || res.data)).catch(console.error);
    reportsApi.getOptions('unit').then(res => setUnits(res.data.results || res.data)).catch(console.error);
    reportsApi.getOptions('contractor').then(res => setContractors(res.data.results || res.data)).catch(console.error);
    reportsApi.getOptions('enclosure').then(res => setEnclosures(res.data.results || res.data)).catch(console.error);
  }, []);

  const handleNext = async () => {
    let fieldsToValidate = [];
    if (activeStep === 0) fieldsToValidate = ['report_date', 'engineer', 'sector', 'variety', 'work_location'];
    if (activeStep === 1) fieldsToValidate = ['operation', 'unit', 'company_workers', 'contractor_workers'];
    
    const isStepValid = await trigger(fieldsToValidate);
    if (isStepValid) setActiveStep((prev) => prev + 1);
  };

  const handleBack = () => setActiveStep((prev) => prev - 1);

  const onSubmit = async (data) => {
    setSubmitError('');
    try {
      const { custom_fields, report_date, ...mainReportData } = data;
      
      const payload = {
        ...mainReportData,
        report_date: report_date.format('YYYY-MM-DD')
      };

      const res = await reportsApi.createTask(payload);
      const reportId = res.data.id;

      if (custom_fields && Object.keys(custom_fields).length > 0) {
        const customValuesPayload = Object.entries(custom_fields).map(([fieldId, value]) => ({
          field: parseInt(fieldId),
          value: value.toString(),
          content_type_model: 'dailytaskreport',
          object_id: reportId
        }));
        await Promise.all(customValuesPayload.map(cv => reportsApi.saveCustomFieldValues(cv)));
      }

      navigate('/reports/tasks');
    } catch (err) {
      setSubmitError('حدث خطأ أثناء حفظ التقرير. يرجى مراجعة البيانات المدخلة.');
    }
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Box maxWidth="800px" mx="auto">
        <Typography variant="h5" fontWeight="800" mb={3}>تسجيل تقرير يومي (إدخال ذكي)</Typography>
        
        <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 4 }}>
          {steps.map((label) => <Step key={label}><StepLabel>{label}</StepLabel></Step>)}
        </Stepper>

        <Card sx={{ p: 4, borderRadius: 4, boxShadow: '0 4px 20px -5px rgba(0,0,0,0.05)' }}>
          {submitError && <Alert severity="error" sx={{ mb: 3 }}>{submitError}</Alert>}
          
          <Box component="form" onSubmit={handleSubmit(onSubmit)}>
            {/* STEP 1: Identity & Location */}
            <Box display={activeStep === 0 ? 'block' : 'none'}>
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <Controller name="report_date" control={control} render={({ field }) => (
                    <DatePicker label="تاريخ التقرير" value={field.value} onChange={(newValue) => field.onChange(newValue)} slotProps={{ textField: { fullWidth: true, error: !!errors.report_date } }} />
                  )} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Controller name="engineer" control={control} render={({ field }) => (
                    <Autocomplete
                      options={users} getOptionLabel={(option) => option.username || option.email || ''}
                      value={users.find(u => u.id === field.value) || null}
                      onChange={(_, data) => field.onChange(data ? data.id : null)}
                      renderInput={(params) => <TextField {...params} label="المهندس" error={!!errors.engineer} helperText={errors.engineer?.message} />}
                    />
                  )} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Controller name="sector" control={control} render={({ field }) => (
                    <Autocomplete
                      options={sectors} getOptionLabel={(option) => option.name || ''}
                      value={sectors.find(s => s.id === field.value) || null}
                      onChange={(_, data) => field.onChange(data ? data.id : null)}
                      renderInput={(params) => <TextField {...params} label="القطاع" error={!!errors.sector} helperText={errors.sector?.message} />}
                    />
                  )} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Controller name="variety" control={control} render={({ field }) => (
                    <Autocomplete
                      options={varieties} getOptionLabel={(option) => option.name || ''}
                      value={varieties.find(v => v.id === field.value) || null}
                      onChange={(_, data) => field.onChange(data ? data.id : null)}
                      renderInput={(params) => <TextField {...params} label="الصنف" error={!!errors.variety} helperText={errors.variety?.message} />}
                    />
                  )} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Controller name="enclosure" control={control} render={({ field }) => (
                    <Autocomplete
                      options={enclosures} getOptionLabel={(option) => option.name || ''}
                      value={enclosures.find(e => e.id === field.value) || null}
                      onChange={(_, data) => field.onChange(data ? data.id : null)}
                      renderInput={(params) => <TextField {...params} label="الحوشة (اختياري)" />}
                    />
                  )} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  {/* Kept as text since it's highly variable, or can be converted to Autocomplete if requested, but "work_location" was text in schema */}
                  <Controller name="work_location" control={control} render={({ field }) => (
                    <TextField {...field} label="مكان العمل الدقيق (نص)" fullWidth error={!!errors.work_location} helperText={errors.work_location?.message} />
                  )} />
                </Grid>
              </Grid>
            </Box>

            {/* STEP 2: Work Details */}
            <Box display={activeStep === 1 ? 'block' : 'none'}>
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <Controller name="operation" control={control} render={({ field }) => (
                    <Autocomplete
                      options={operations} getOptionLabel={(option) => option.name || ''}
                      value={operations.find(o => o.id === field.value) || null}
                      onChange={(_, data) => field.onChange(data ? data.id : null)}
                      renderInput={(params) => <TextField {...params} label="العملية الفنية" error={!!errors.operation} helperText={errors.operation?.message} />}
                    />
                  )} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Controller name="unit" control={control} render={({ field }) => (
                    <Autocomplete
                      options={units} getOptionLabel={(option) => option.name || ''}
                      value={units.find(u => u.id === field.value) || null}
                      onChange={(_, data) => field.onChange(data ? data.id : null)}
                      renderInput={(params) => <TextField {...params} label="الوحدة" error={!!errors.unit} helperText={errors.unit?.message} />}
                    />
                  )} />
                </Grid>
                
                <Grid item xs={12} sm={4}>
                  <Controller name="company_workers" control={control} render={({ field }) => (
                    <StepperInput value={field.value} onChange={field.onChange} label="عمال الشركة" error={!!errors.company_workers} helperText={errors.company_workers?.message} />
                  )} />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Controller name="contractor_workers" control={control} render={({ field }) => (
                    <StepperInput value={field.value} onChange={field.onChange} label="عمال المقاول" error={!!errors.contractor_workers} helperText={errors.contractor_workers?.message} />
                  )} />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Controller name="contractor" control={control} render={({ field }) => (
                    <Autocomplete
                      options={contractors} getOptionLabel={(option) => option.name || ''}
                      value={contractors.find(c => c.id === field.value) || null}
                      onChange={(_, data) => field.onChange(data ? data.id : null)}
                      renderInput={(params) => <TextField {...params} label="المقاول" error={!!errors.contractor} helperText={errors.contractor?.message} />}
                    />
                  )} />
                </Grid>
              </Grid>
            </Box>

            {/* STEP 3: Productivity & Custom Fields */}
            <Box display={activeStep === 2 ? 'block' : 'none'}>
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <Controller name="actual_productivity" control={control} render={({ field }) => (
                    <TextField {...field} type="number" label="الإنتاجية الفعلية" fullWidth error={!!errors.actual_productivity} helperText={errors.actual_productivity?.message} />
                  )} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Controller name="work_hours" control={control} render={({ field }) => (
                    <TextField {...field} type="number" label="ساعات العمل" fullWidth error={!!errors.work_hours} helperText={errors.work_hours?.message} />
                  )} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Controller name="overtime_hours" control={control} render={({ field }) => (
                    <TextField {...field} type="number" label="ساعات الإضافي" fullWidth />
                  )} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Controller name="overtime_productivity" control={control} render={({ field }) => (
                    <TextField {...field} type="number" label="انتاجية الإضافي" fullWidth />
                  )} />
                </Grid>
                <Grid item xs={12}>
                  <Controller name="notes" control={control} render={({ field }) => (
                    <TextField {...field} multiline rows={3} label="ملاحظات" fullWidth />
                  )} />
                </Grid>
              </Grid>

              <DynamicFieldsRenderer modelName="dailytaskreport" control={control} errors={errors} />
            </Box>

            {/* Stepper Controls */}
            <Box display="flex" justifyContent="space-between" mt={4} pt={2} borderTop="1px solid #e2e8f0">
              <Button disabled={activeStep === 0} onClick={handleBack} sx={{ fontWeight: 700 }}>
                رجوع
              </Button>
              <Box>
                {activeStep < steps.length - 1 ? (
                  <Button variant="contained" onClick={handleNext} sx={{ borderRadius: 2, px: 4, fontWeight: 700 }}>
                    التالي
                  </Button>
                ) : (
                  <Button type="submit" variant="contained" disabled={isSubmitting} sx={{ borderRadius: 2, px: 4, fontWeight: 700 }}>
                    {isSubmitting ? <CircularProgress size={24} color="inherit" /> : 'حفظ التقرير'}
                  </Button>
                )}
              </Box>
            </Box>
          </Box>
        </Card>
      </Box>
    </LocalizationProvider>
  );
};

export default DailyTaskForm;
