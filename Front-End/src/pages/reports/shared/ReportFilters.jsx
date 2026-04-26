import React from 'react';
import { Box, TextField, MenuItem, Button, Paper, Grid } from '@mui/material';
import { FilterList as FilterIcon, Clear as ClearIcon } from '@mui/icons-material';

const SECTORS = [
  { value: '', label: 'الكل' },
  { value: 'A', label: 'قطاع A' },
  { value: 'B', label: 'قطاع B' },
  { value: 'C', label: 'قطاع C' },
  { value: 'D', label: 'قطاع D' },
  { value: 'greenhouse', label: 'الصوب الزراعية' },
  { value: 'new_farms', label: 'المزارع الجديدة' },
];

const ReportFilters = ({ filters, onFilterChange }) => {
  const handleChange = (e) => {
    const { name, value } = e.target;
    onFilterChange({ ...filters, [name]: value });
  };

  const handleClear = () => {
    onFilterChange({
      start_date: '',
      end_date: '',
      sector: '',
      engineer_name: ''
    });
  };

  return (
    <Paper elevation={0} sx={{ p: 3, mb: 4, borderRadius: 3, border: '1px solid #e2e8f0', bgcolor: '#f8fafc' }}>
      <Grid container spacing={2} alignItems="center">
        <Grid item xs={12} sm={6} md={3}>
          <TextField
            fullWidth
            label="تاريخ البدء"
            type="date"
            name="start_date"
            value={filters.start_date || ''}
            onChange={handleChange}
            InputLabelProps={{ shrink: true }}
            size="small"
            sx={{ bgcolor: 'white', borderRadius: 1 }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <TextField
            fullWidth
            label="تاريخ الانتهاء"
            type="date"
            name="end_date"
            value={filters.end_date || ''}
            onChange={handleChange}
            InputLabelProps={{ shrink: true }}
            size="small"
            sx={{ bgcolor: 'white', borderRadius: 1 }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <TextField
            select
            fullWidth
            label="القطاع"
            name="sector"
            value={filters.sector || ''}
            onChange={handleChange}
            size="small"
            sx={{ bgcolor: 'white', borderRadius: 1 }}
          >
            {SECTORS.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </TextField>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <TextField
            fullWidth
            label="اسم المهندس"
            name="engineer_name"
            value={filters.engineer_name || ''}
            onChange={handleChange}
            size="small"
            sx={{ bgcolor: 'white', borderRadius: 1 }}
          />
        </Grid>
        <Grid item xs={12} md={2} display="flex" gap={1}>
          <Button
            variant="outlined"
            color="error"
            fullWidth
            onClick={handleClear}
            startIcon={<ClearIcon />}
            sx={{ fontWeight: 600 }}
          >
            مسح
          </Button>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default ReportFilters;
