import React from 'react';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Card, Typography, Box, Chip, TablePagination, TextField, MenuItem
} from '@mui/material';
import dayjs from 'dayjs';

const ReportsTable = ({ data, totalCount, page, rowsPerPage, onPageChange, onRowsPerPageChange, filters, onFilterChange, operations, locations, t }) => {
  const fieldSx = { flex: '1 1 180px', minWidth: 0 };
  const inputSx = { '& .MuiOutlinedInput-root': { borderRadius: 1 }, width: '100%' };

  return (
    <Card sx={{ borderRadius: 2, boxShadow: '0 4px 20px 0 rgba(0,0,0,0.05)', border: '1px solid #f1f5f9', overflow: 'hidden' }}>
      <Box sx={{ p: 3, borderBottom: '1px solid #f1f5f9' }}>
        <Typography variant="h6" fontWeight="700" sx={{ mb: 2 }}>
          {t('reports.list_title', 'قائمة التقارير')}
        </Typography>

        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, alignItems: 'flex-end' }}>
          {/* العملية */}
          <Box sx={fieldSx}>
            <Typography variant="body2" fontWeight="600" sx={{ mb: 1 }}>
              {t('filters.operation', 'العملية')}
            </Typography>
            <TextField
              fullWidth
              select
              size="small"
              value={filters.operation || ''}
              onChange={(e) => onFilterChange('operation', e.target.value)}
              displayEmpty
              sx={inputSx}
            >
              <MenuItem value="">{t('filters.all', 'الكل')}</MenuItem>
              {operations?.map(op => (
                <MenuItem key={op.id} value={op.id}>{op.name}</MenuItem>
              ))}
            </TextField>
          </Box>

          {/* الموقع */}
          <Box sx={fieldSx}>
            <Typography variant="body2" fontWeight="600" sx={{ mb: 1 }}>
              {t('filters.location', 'الموقع')}
            </Typography>
            <TextField
              fullWidth
              select
              size="small"
              value={filters.location || ''}
              onChange={(e) => onFilterChange('location', e.target.value)}
              displayEmpty
              sx={inputSx}
            >
              <MenuItem value="">{t('filters.all', 'الكل')}</MenuItem>
              {locations?.map(loc => (
                <MenuItem key={loc.id} value={loc.id}>{loc.name}</MenuItem>
              ))}
            </TextField>
          </Box>

          {/* التاريخ */}
          <Box sx={fieldSx}>
            <Typography variant="body2" fontWeight="600" sx={{ mb: 1 }}>
              {t('filters.date', 'التاريخ')}
            </Typography>
            <TextField
              fullWidth
              type="date"
              size="small"
              InputLabelProps={{ shrink: true }}
              value={filters.report_date || ''}
              onChange={(e) => onFilterChange('report_date', e.target.value)}
              sx={inputSx}
            />
          </Box>
        </Box>
      </Box>

      <TableContainer>
        <Table sx={{ minWidth: 650 }}>
          <TableHead sx={{ bgcolor: '#f8fafc' }}>
            <TableRow>
              <TableCell sx={{ fontWeight: 700 }}>{t('reports.id', 'ID')}</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>{t('reports.date', 'التاريخ')}</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>{t('reports.operation', 'العملية')}</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>{t('reports.location', 'الموقع')}</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>{t('reports.productivity', 'الإنتاجية')}</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>{t('reports.engineer', 'المهندس')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data?.map((row) => (
              <TableRow key={row.id} hover sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                <TableCell>#{row.id}</TableCell>
                <TableCell>{dayjs(row.report_date).format('DD/MM/YYYY')}</TableCell>
                <TableCell>
                  <Chip
                    label={row.operation_name}
                    size="small"
                    sx={{ fontWeight: 600, bgcolor: '#e0f2fe', color: '#0369a1' }}
                  />
                </TableCell>
                <TableCell>{row.location_name}</TableCell>
                <TableCell>{row.actual_productivity} {row.unit_name}</TableCell>
                <TableCell>{row.engineer_name}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <TablePagination
        rowsPerPageOptions={[5, 10, 25]}
        component="div"
        count={totalCount}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={onPageChange}
        onRowsPerPageChange={onRowsPerPageChange}
        labelRowsPerPage={t('table.rows_per_page', 'صفوف لكل صفحة')}
      />
    </Card>
  );
};

export default ReportsTable;
