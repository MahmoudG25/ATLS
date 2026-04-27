import React from 'react';
import { TextField, MenuItem, Button, Paper, Grid, Typography } from '@mui/material';
import { Clear as ClearIcon } from '@mui/icons-material';

const ReportFilters = ({ filters, onFilterChange, options = {} }) => {
  const operations = options.operations || [];
  const engineers = options.engineers || [];
  const locations = options.locations || [];

  const handleChange = (e) => {
    const { name, value } = e.target;
    onFilterChange({ ...filters, [name]: value });
  };

  const handleClear = () => {
    onFilterChange({
      start_date: '',
      end_date: '',
      operation: '',
      engineer: '',
      location: '',
    });
  };

  return (
    <Paper elevation={0} sx={{ p: 3, mb: 4, borderRadius: 3, border: '1px solid #e2e8f0', bgcolor: '#ffffff' }}>
      <Typography variant="subtitle1" fontWeight={700} mb={2}>فلاتر التقارير</Typography>
      <Grid container spacing={2.5} alignItems="center">
        <Grid item xs={12} md={2}>
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
        <Grid item xs={12} md={2}>
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
        <Grid item xs={12} md={2}>
          <TextField
            select
            fullWidth
            label="العملية"
            name="operation"
            value={filters.operation || ''}
            onChange={handleChange}
            size="small"
            sx={{ bgcolor: 'white', borderRadius: 1 }}
          >
            <MenuItem value="">الكل</MenuItem>
            {operations.map((option) => (
              <MenuItem key={option.id} value={option.id}>
                {option.name}
              </MenuItem>
            ))}
          </TextField>
        </Grid>
        <Grid item xs={12} md={2}>
          <TextField
            select
            fullWidth
            label="المهندس"
            name="engineer"
            value={filters.engineer || ''}
            onChange={handleChange}
            size="small"
            sx={{ bgcolor: 'white', borderRadius: 1 }}
          >
            <MenuItem value="">الكل</MenuItem>
            {engineers.map((option) => (
              <MenuItem key={option.id} value={option.id}>
                {option.name || option.full_name || option.email}
              </MenuItem>
            ))}
          </TextField>
        </Grid>
        <Grid item xs={12} md={2}>
          <TextField
            select
            label="الموقع"
            name="location"
            value={filters.location || ''}
            onChange={handleChange}
            fullWidth
            size="small"
            sx={{ bgcolor: 'white', borderRadius: 1 }}
          >
            <MenuItem value="">الكل</MenuItem>
            {locations.map((option) => (
              <MenuItem key={option.id} value={option.id}>
                {option.name}
              </MenuItem>
            ))}
          </TextField>
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
