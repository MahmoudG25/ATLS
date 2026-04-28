import React, { useState, useEffect, useCallback } from 'react';
import {
  TextField, Autocomplete, Alert, LinearProgress, CircularProgress
} from '@mui/material';
import { Add as AddIcon, Remove as RemoveIcon, Save as SaveIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import DynamicFieldsRenderer from '../shared/DynamicFieldsRenderer';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import dayjs from 'dayjs';
import { useAuth } from '../../../app/AuthContext';
import api from '../../../services/api';
import { reportsApi } from '../../../services/reportsApi';

// ── Schema ──────────────────────────────────────────────────────────────────
// `location` = the selected ENCLOSURE LocationNode ID (sent to backend)
// `stage_id` = UI-only state for filtering enclosures (not in form schema)
const taskSchema = z.object({
  report_date:          z.any(),
  engineer:             z.number({ required_error: 'المهندس مطلوب' }).min(1, 'المهندس مطلوب'),
  location:             z.number({ required_error: 'الحوشة / الموقع مطلوب' }).min(1, 'الحوشة مطلوبة'),
  operation:            z.number({ required_error: 'العملية مطلوبة' }).min(1, 'العملية مطلوبة'),
  variety:              z.number({ required_error: 'الصنف مطلوب' }).min(1, 'الصنف مطلوب'),
  unit:                 z.number({ required_error: 'الوحدة مطلوبة' }).min(1, 'الوحدة مطلوبة'),
  contractor:           z.number().nullable().optional(),
  company_workers:      z.coerce.number().min(0),
  contractor_workers:   z.coerce.number().min(0),
  actual_productivity:  z.coerce.number().min(0),
  work_hours:           z.coerce.number().min(0.5, 'يجب أن تكون ساعات العمل 0.5 على الأقل'),
  overtime_hours:       z.coerce.number().min(0).optional(),
  overtime_productivity:z.coerce.number().min(0).optional(),
  notes:                z.string().optional(),
  custom_fields:        z.record(z.any()).optional(),
});

// ── Styles ───────────────────────────────────────────────────────────────────
const inputSx = {
  '& .MuiOutlinedInput-root:not(.MuiInputBase-multiline)': { height: '40px' },
  '& .MuiOutlinedInput-root': {
    backgroundColor: '#f8faf6',
    borderRadius: '0.5rem',
    fontSize: '0.875rem',
    '& fieldset':             { borderColor: '#bfc9c1' },
    '&:hover fieldset':       { borderColor: '#0f5238' },
    '&.Mui-focused fieldset': { borderColor: '#0f5238', borderWidth: '1.5px' },
    '&.Mui-disabled':         { backgroundColor: '#e8ebe8' },
  },
};

const dropdownPaper = {
  paper: { sx: { bgcolor: '#fff', mt: 0.5, borderRadius: '8px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)', border: '1px solid #bfc9c1' } }
};

// ── Sub-components ────────────────────────────────────────────────────────────
const Label = ({ children }) => (
  <label className="block mb-2 font-medium text-sm text-[#191c1a]">{children}</label>
);

const Field = ({ label, children }) => (
  <div className="flex flex-col w-full">
    <Label>{label}</Label>
    {children}
  </div>
);

/** +/- stepper for integer counts */
const Stepper = ({ value, onChange, error }) => {
  const borderClass = error ? 'border-[#ba1a1a]' : 'border-[#bfc9c1]';
  return (
    <div className={`flex items-stretch h-[40px] border ${borderClass} rounded-lg bg-[#f8faf6] overflow-hidden focus-within:outline focus-within:outline-[1.5px] focus-within:outline-[#0f5238] focus-within:-outline-offset-1`}>
      <button type="button" onClick={() => onChange(value + 1)}
        className={`w-[40px] border-none border-l ${borderClass} bg-transparent cursor-pointer flex items-center justify-center text-[#404943] hover:bg-[#eceeea] transition-colors`}>
        <AddIcon sx={{ fontSize: 18 }} />
      </button>
      <input type="number" value={value} min={0}
        onChange={e => { const v = parseInt(e.target.value, 10); onChange(isNaN(v) ? 0 : Math.max(0, v)); }}
        className="flex-1 w-full border-none outline-none bg-transparent text-center font-semibold text-[15px] text-[#191c1a] [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none" />
      <button type="button" onClick={() => onChange(Math.max(0, value - 1))}
        className={`w-[40px] border-none border-r ${borderClass} bg-transparent cursor-pointer flex items-center justify-center text-[#404943] hover:bg-[#eceeea] transition-colors`}>
        <RemoveIcon sx={{ fontSize: 18 }} />
      </button>
    </div>
  );
};

/** FK Autocomplete — value is the integer ID */
const AC = ({ options, value, onChange, placeholder, error, helperText, disabled, getLabel }) => (
  <Autocomplete
    disabled={disabled}
    options={options}
    getOptionLabel={getLabel || (o => o.name || '')}
    value={options.find(o => o.id === value) || null}
    onChange={(_, d) => onChange(d?.id ?? null)}
    slotProps={dropdownPaper}
    sx={inputSx}
    noOptionsText="لا توجد خيارات"
    renderInput={params => (
      <TextField {...params} fullWidth placeholder={placeholder} size="small" error={error} helperText={helperText} />
    )}
  />
);

// ── Main Component ────────────────────────────────────────────────────────────
export default function DailyTaskForm() {
  const navigate = useNavigate();
  const { user } = useAuth();

  // Privileged roles can assign reports to any engineer
  const PRIVILEGED = ['MANAGER', 'SUPER_ADMIN', 'ADMIN', 'OWNER'];
  const isPrivileged = user && PRIVILEGED.includes(user.role);

  const [submitError, setSubmitError] = useState('');
  const [pendingFiles, setPendingFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState({});

  // ── Dropdown state ──────────────────────────────────────────────────────────
  const [engineers, setEngineers]     = useState([]);
  const [sectors, setSectors]         = useState([]);
  const [stages, setStages]           = useState([]);
  const [enclosures, setEnclosures]   = useState([]);
  const [operations, setOperations]   = useState([]);
  const [varieties, setVarieties]     = useState([]);
  const [units, setUnits]             = useState([]);
  const [contractors, setContractors] = useState([]);
  const [enclosuresLoading, setEnclosuresLoading] = useState(false);

  const [selectedSectorId, setSelectedSectorId] = useState(null);
  const [selectedStageId, setSelectedStageId]   = useState(null);
  const [hasStages, setHasStages]               = useState(false);

  // ── Form setup ──────────────────────────────────────────────────────────────
  const { control, handleSubmit, watch, formState: { errors, isSubmitting }, setValue } = useForm({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      report_date:           dayjs(),
      engineer:              user?.id ?? null,
      location:              null,
      operation:             null,
      variety:               null,
      unit:                  null,
      contractor:            null,
      company_workers:       0,
      contractor_workers:    0,
      actual_productivity:   0,
      work_hours:            8,
      overtime_hours:        0,
      overtime_productivity: 0,
      notes:                 '',
      custom_fields:         {},
    },
  });

  // Auto-fill engineer for non-privileged users
  useEffect(() => {
    if (user && !isPrivileged) setValue('engineer', user.id);
  }, [user, isPrivileged, setValue]);

  // ── Initial data fetch ──────────────────────────────────────────────────────
  useEffect(() => {
    (async () => {
      try {
        const [engRes, sectorsRes, opsRes, varRes, unitRes, conRes] = await Promise.allSettled([
          reportsApi.getEngineers(),
          reportsApi.getLocationNodes('SECTOR'),
          reportsApi.getOperations(),
          reportsApi.getVarieties(),
          reportsApi.getUnits(),
          reportsApi.getContractors(),
        ]);

        const r = res => Array.isArray(res.value?.data) ? res.value.data : (res.value?.data?.results ?? res.value ?? []);

        if (engRes.status === 'fulfilled')     setEngineers(r(engRes));
        if (sectorsRes.status === 'fulfilled') setSectors(r(sectorsRes));
        if (opsRes.status === 'fulfilled')     setOperations(r(opsRes));
        if (varRes.status === 'fulfilled')     setVarieties(r(varRes));
        if (unitRes.status === 'fulfilled')    setUnits(r(unitRes));
        if (conRes.status === 'fulfilled')     setContractors(r(conRes));
      } catch (e) {
        console.error('خطأ في تحميل بيانات النموذج:', e);
      }
    })();
  }, []);

  // ── Hierarchy Logic ─────────────────────────────────────────────────────────
  const handleSectorChange = async (sectorId) => {
    setSelectedSectorId(sectorId);
    setSelectedStageId(null);
    setStages([]);
    setEnclosures([]);
    setHasStages(false);
    setValue('location', null);

    if (!sectorId) return;

    try {
      setEnclosuresLoading(true);
      const children = await reportsApi.getLocationNodes(null, sectorId);
      const stgs = children.filter(c => c.type === 'STAGE');
      if (stgs.length > 0) {
        setStages(stgs);
        setHasStages(true);
      } else {
        setEnclosures(children.filter(c => c.type === 'ENCLOSURE'));
      }
    } catch (e) {
      console.error('خطأ في تحميل فروع القطاع:', e);
    } finally {
      setEnclosuresLoading(false);
    }
  };

  const handleStageChange = async (stageId) => {
    setSelectedStageId(stageId);
    setEnclosures([]);
    setValue('location', null);

    if (!stageId) return;

    try {
      setEnclosuresLoading(true);
      const encs = await reportsApi.getLocationNodes('ENCLOSURE', stageId);
      setEnclosures(encs);
    } catch (e) {
      console.error('خطأ في تحميل الحوشات:', e);
    } finally {
      setEnclosuresLoading(false);
    }
  };

  // ── Submit ──────────────────────────────────────────────────────────────────
  const onSubmit = async (data) => {
    setSubmitError('');
    try {
      const { custom_fields, report_date, ...rest } = data;

      // Payload: location = LocationNode ID of the selected enclosure
      // engineer is included only if privileged user (backend validates and stores it)
      // work_location is NOT sent — serializer defaults it to '' (blank=True)
      const payload = {
        ...rest,
        report_date: dayjs(report_date).format('YYYY-MM-DD'),
      };

      const res = await api.post('/reports/tasks/', payload);
      const reportId = res.data.id;

      // Upload attachments
      for (const file of pendingFiles) {
        const uploadRes = await reportsApi.uploadFile(file, (event) => {
          const ratio = event.total ? Math.round((event.loaded * 100) / event.total) : 0;
          setUploadProgress(prev => ({ ...prev, [file.name]: ratio }));
        });
        const fileType = file.type.startsWith('image/') ? 'IMAGE'
                       : file.type.startsWith('video/') ? 'VIDEO'
                       : 'FILE';
        await reportsApi.createAttachment({ report: reportId, file_url: uploadRes.data.file_url, file_type: fileType });
      }

      // Custom fields
      if (custom_fields && Object.keys(custom_fields).length > 0) {
        await Promise.all(Object.entries(custom_fields).map(([fieldId, val]) =>
          api.post('/reports/custom-field-values/', {
            field: parseInt(fieldId, 10), value: val.toString(),
            content_type_model: 'dailytaskreport', object_id: reportId,
          })
        ));
      }

      navigate('/reports/tasks');
    } catch (e) {
      const msg = e?.response?.data ? JSON.stringify(e.response.data) : 'حدث خطأ أثناء حفظ التقرير.';
      setSubmitError(msg);
    }
  };

  const onDropFiles = (event) => {
    event.preventDefault();
    const files = Array.from(event.dataTransfer?.files || event.target.files || []);
    if (files.length) setPendingFiles(prev => [...prev, ...files]);
  };

  // ── Render ───────────────────────────────────────────────────────────────────
  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <form onSubmit={handleSubmit(onSubmit)} className="pb-32 bg-[#f4f7f4] min-h-screen">
        <div className="container mx-auto px-4 md:px-6 py-6 md:py-10 max-w-6xl">

          {submitError && (
            <Alert severity="error" className="mb-6 rounded-lg whitespace-pre-wrap">{submitError}</Alert>
          )}

          <div className="bg-white rounded-2xl shadow-[0_2px_8px_rgba(0,0,0,0.04)] border border-[#bfc9c1] overflow-hidden">
            <div className="p-6 md:p-10">

              {/* Header */}
              <div className="mb-8 pb-6 border-b border-[#e1e3df]">
                <h2 className="font-semibold text-2xl text-[#191c1a]">تسجيل تقرير يومي</h2>
                <p className="text-[15px] text-[#404943] mt-1.5">يرجى إدخال تفاصيل العمل اليومي بدقة لضمان صحة البيانات.</p>
              </div>

              <div className="flex flex-col gap-8">

                {/* ── Row 1: التاريخ | المهندس | القطاع | (المرحلة) | الحوشة ── */}
                <div>
                  <p className="text-xs font-semibold text-[#0f5238] uppercase tracking-wider mb-4">معلومات أساسية</p>
                  <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-${hasStages ? '5' : '4'} gap-6`}>

                    {/* التاريخ */}
                    <Controller name="report_date" control={control} render={({ field }) => (
                      <Field label="التاريخ">
                        <DatePicker value={field.value} onChange={field.onChange}
                          slotProps={{ textField: { fullWidth: true, size: 'small', error: !!errors.report_date, sx: inputSx } }} />
                      </Field>
                    )} />

                    {/* المهندس المسؤول */}
                    <Controller name="engineer" control={control} render={({ field }) => (
                      <Field label="المهندس المسؤول">
                        {isPrivileged ? (
                          <AC
                            options={engineers}
                            value={field.value}
                            onChange={field.onChange}
                            placeholder="اختر المهندس"
                            error={!!errors.engineer}
                            helperText={errors.engineer?.message}
                            getLabel={o => o.name || o.email || ''}
                          />
                        ) : (
                          <TextField
                            value={engineers.find(e => e.id === field.value)?.name || user?.name || ''}
                            disabled
                            fullWidth
                            size="small"
                            sx={inputSx}
                            placeholder="المهندس المسؤول"
                          />
                        )}
                      </Field>
                    )} />

                    {/* القطاع */}
                    <Field label="القطاع">
                      <Autocomplete
                        options={sectors}
                        getOptionLabel={o => o.name || ''}
                        value={sectors.find(s => s.id === selectedSectorId) || null}
                        onChange={(_, d) => handleSectorChange(d?.id ?? null)}
                        slotProps={dropdownPaper}
                        sx={inputSx}
                        noOptionsText="لا توجد قطاعات"
                        renderInput={params => (
                          <TextField {...params} fullWidth placeholder="اختر القطاع" size="small" />
                        )}
                      />
                    </Field>

                    {/* المرحلة (تظهر فقط إذا كان القطاع يحتوي على مراحل) */}
                    {hasStages && (
                      <Field label="المرحلة">
                        <Autocomplete
                          options={stages}
                          getOptionLabel={o => o.name || ''}
                          value={stages.find(s => s.id === selectedStageId) || null}
                          onChange={(_, d) => handleStageChange(d?.id ?? null)}
                          slotProps={dropdownPaper}
                          sx={inputSx}
                          noOptionsText="لا توجد مراحل"
                          renderInput={params => (
                            <TextField {...params} fullWidth placeholder="اختر المرحلة" size="small" />
                          )}
                        />
                      </Field>
                    )}

                    {/* الحوشة / الموقع */}
                    <Controller name="location" control={control} render={({ field }) => (
                      <Field label="الحوشة / الموقع">
                        <Autocomplete
                          disabled={!selectedSectorId || (hasStages && !selectedStageId)}
                          loading={enclosuresLoading}
                          options={enclosures}
                          getOptionLabel={o => o.name || ''}
                          value={enclosures.find(e => e.id === field.value) || null}
                          onChange={(_, d) => field.onChange(d?.id ?? null)}
                          slotProps={dropdownPaper}
                          sx={inputSx}
                          noOptionsText={selectedSectorId ? 'لا توجد حوشات' : 'اختر القطاع أولاً'}
                          renderInput={params => (
                            <TextField
                              {...params}
                              fullWidth
                              placeholder={selectedSectorId ? 'اختر الحوشة' : 'اختر القطاع أولاً'}
                              size="small"
                              error={!!errors.location}
                              helperText={errors.location?.message}
                            />
                          )}
                        />
                      </Field>
                    )} />
                  </div>
                </div>

                {/* ── Row 2: العملية | الصنف | الوحدة | المقاول ── */}
                <div>
                  <p className="text-xs font-semibold text-[#0f5238] uppercase tracking-wider mb-4">تفاصيل العملية</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">

                    <Controller name="operation" control={control} render={({ field }) => (
                      <Field label="العملية الفنية">
                        <AC options={operations} value={field.value} onChange={field.onChange}
                          placeholder="اختر العملية" error={!!errors.operation} helperText={errors.operation?.message} />
                      </Field>
                    )} />

                    <Controller name="variety" control={control} render={({ field }) => (
                      <Field label="الصنف">
                        <AC options={varieties} value={field.value} onChange={field.onChange}
                          placeholder="اختر الصنف" error={!!errors.variety} helperText={errors.variety?.message} />
                      </Field>
                    )} />

                    <Controller name="unit" control={control} render={({ field }) => (
                      <Field label="وحدة القياس">
                        <AC options={units} value={field.value} onChange={field.onChange}
                          placeholder="اختر الوحدة" error={!!errors.unit} helperText={errors.unit?.message} />
                      </Field>
                    )} />

                    <Controller name="contractor" control={control} render={({ field }) => (
                      <Field label="المقاول (اختياري)">
                        <AC options={contractors} value={field.value} onChange={field.onChange}
                          placeholder="اختر المقاول" error={!!errors.contractor} helperText={errors.contractor?.message} />
                      </Field>
                    )} />
                  </div>
                </div>

                {/* ── Row 3: عمال الشركة | عمال المقاول ── */}
                <div>
                  <p className="text-xs font-semibold text-[#0f5238] uppercase tracking-wider mb-4">توزيع العمالة</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">

                    <Controller name="company_workers" control={control} render={({ field }) => (
                      <Field label="عمال الشركة">
                        <Stepper value={field.value} onChange={field.onChange} error={!!errors.company_workers} />
                      </Field>
                    )} />

                    <Controller name="contractor_workers" control={control} render={({ field }) => (
                      <Field label="عمال المقاول">
                        <Stepper value={field.value} onChange={field.onChange} error={!!errors.contractor_workers} />
                      </Field>
                    )} />
                  </div>
                </div>

                {/* ── Row 4: ساعات العمل | ساعات إضافية | الإنتاجية الفعلية | إنتاجية إضافية ── */}
                <div>
                  <p className="text-xs font-semibold text-[#0f5238] uppercase tracking-wider mb-4">الإنتاجية والوقت</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                    {[
                      { name: 'work_hours',            label: 'ساعات العمل',       placeholder: '8',    step: '0.5' },
                      { name: 'overtime_hours',         label: 'ساعات إضافية',      placeholder: '0',    step: '0.5' },
                      { name: 'actual_productivity',    label: 'الإنتاجية الفعلية', placeholder: '0.00', step: '0.01' },
                      { name: 'overtime_productivity',  label: 'إنتاجية إضافية',   placeholder: '0.00', step: '0.01' },
                    ].map(({ name, label, placeholder, step }) => (
                      <Controller key={name} name={name} control={control} render={({ field }) => (
                        <Field label={label}>
                          <TextField {...field} type="number" inputProps={{ min: 0, step }}
                            placeholder={placeholder} fullWidth size="small"
                            error={!!errors[name]} helperText={errors[name]?.message} sx={inputSx} />
                        </Field>
                      )} />
                    ))}
                  </div>
                </div>

                {/* ── Row 5: ملاحظات ── */}
                <div className="w-full">
                  <Controller name="notes" control={control} render={({ field }) => (
                    <Field label="ملاحظات / مشاهدات">
                      <TextField {...field} placeholder="أدخل أي ملاحظات هامة هنا..." fullWidth size="small" multiline rows={4} sx={inputSx} />
                    </Field>
                  )} />
                </div>

                {/* ── Row 6: مرفقات ── */}
                <div className="w-full">
                  <Field label="المرفقات">
                    <div
                      className="border-2 border-dashed border-[#bfc9c1] rounded-xl p-5 bg-[#f8faf6]"
                      onDragOver={e => e.preventDefault()}
                      onDrop={onDropFiles}
                    >
                      <input type="file" multiple onChange={onDropFiles} className="mb-3 block w-full text-sm" />
                      <p className="text-sm text-[#404943]">اسحب الملفات هنا أو اخترها للرفع إلى Cloudinary.</p>
                      <div className="mt-3 space-y-2">
                        {pendingFiles.map(file => (
                          <div key={`${file.name}-${file.size}`} className="rounded-md border border-[#d7ddd8] p-2 bg-white">
                            <div className="flex justify-between text-sm">
                              <span>{file.name}</span>
                              <span>{uploadProgress[file.name] ?? 0}%</span>
                            </div>
                            <LinearProgress variant="determinate" value={uploadProgress[file.name] ?? 0} sx={{ mt: 1 }} />
                          </div>
                        ))}
                      </div>
                    </div>
                  </Field>
                </div>

                {/* Custom fields (admin-defined) */}
                <DynamicFieldsRenderer modelName="dailytaskreport" control={control} errors={errors} />

              </div>
            </div>
          </div>
        </div>

        {/* Sticky save button */}
        <div className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-[#bfc9c1] py-4 px-6 md:px-12 flex justify-end items-center shadow-[0_-4px_12px_rgba(0,0,0,0.05)]">
          <button type="submit" disabled={isSubmitting}
            className="flex items-center justify-center gap-2 bg-[#0f5238] text-white font-medium text-sm px-8 py-3 rounded-xl transition-all shadow-sm hover:shadow-md hover:bg-[#0b3d2a] disabled:bg-[#a0b8a8] disabled:cursor-not-allowed">
            {isSubmitting ? <CircularProgress size={18} color="inherit" /> : <SaveIcon fontSize="small" />}
            {isSubmitting ? 'جاري الحفظ...' : 'حفظ التقرير'}
          </button>
        </div>
      </form>
    </LocalizationProvider>
  );
}
