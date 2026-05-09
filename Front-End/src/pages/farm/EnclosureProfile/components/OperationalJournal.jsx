import React, { useEffect, useState } from 'react'

import {
  FilterList as FilterIcon,
  GetApp as DownloadIcon,
  Inbox as EmptyIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon,
} from '@mui/icons-material'
import {
  Box,
  Button,
  CircularProgress,
  IconButton,
  Paper,
  Stack,
  TextField,
  Tooltip,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material'

import { farmApi } from '../../../../api/farmApi'

import OperationalDetailsDrawer from './OperationalDetailsDrawer'
import OperationLedgerRow from './OperationLedgerRow'

const OperationalJournal = ({ enclosureId }) => {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)
  const [filters, setFilters] = useState({ search: '', type: 'all' })
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [selectedEvent, setSelectedEvent] = useState(null)

  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'))

  const fetchEvents = async (pageNumber = 1, isNewSearch = false) => {
    try {
      setLoading(true)
      const response = await farmApi.getLocationOperations(enclosureId, {
        page: pageNumber,
        search: filters.search,
      })

      const newEvents = response.data.results
      if (isNewSearch) {
        setEvents(newEvents)
      } else {
        setEvents((prev) => [...prev, ...newEvents])
      }

      setHasMore(!!response.data.next)
    } catch (error) {
      console.error('Failed to fetch operations:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchEvents(1, true)
  }, [enclosureId, filters.search])

  const loadMore = () => {
    if (!loading && hasMore) {
      const nextPage = page + 1
      setPage(nextPage)
      fetchEvents(nextPage)
    }
  }

  return (
    <Box sx={{ width: '100%', display: 'flex', flexDirection: 'column', gap: 2 }}>
      {/* 1. Header & Filters */}
      <Paper
        elevation={0}
        sx={{
          p: 2,
          borderRadius: '12px',
          border: '1px solid #e2e8f0',
          bgcolor: 'white',
          boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.05)',
        }}
      >
        <Stack
          direction={{ xs: 'column', md: 'row' }}
          spacing={2}
          alignItems="center"
          justifyContent="space-between"
        >
          <Stack direction="row" spacing={2} flexGrow={1} sx={{ width: '100%' }}>
            <TextField
              size="small"
              placeholder="البحث في السجل (عملية، مسؤول، ملاحظات)..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              InputProps={{
                startAdornment: <SearchIcon sx={{ color: '#94a3b8', mr: 1, fontSize: 20 }} />,
              }}
              sx={{
                width: { xs: '100%', md: 400 },
                '& .MuiOutlinedInput-root': { bgcolor: '#f8fafc', borderRadius: '8px' },
              }}
            />
            {!isMobile && (
              <Button
                variant="outlined"
                startIcon={<FilterIcon />}
                sx={{ borderRadius: '8px', borderColor: '#e2e8f0', color: '#475569' }}
              >
                تصفية
              </Button>
            )}
          </Stack>

          <Stack direction="row" spacing={1}>
            <Tooltip title="تحديث البيانات">
              <IconButton
                onClick={() => fetchEvents(1, true)}
                size="small"
                sx={{ border: '1px solid #e2e8f0' }}
              >
                <RefreshIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            {!isMobile && (
              <Button
                variant="contained"
                startIcon={<DownloadIcon />}
                disableElevation
                sx={{ borderRadius: '8px', bgcolor: '#0f172a' }}
              >
                تصدير PDF
              </Button>
            )}
          </Stack>
        </Stack>
      </Paper>

      {/* 2. Journal Content */}
      <Paper
        elevation={0}
        sx={{
          borderRadius: '12px',
          border: '1px solid #e2e8f0',
          overflow: 'hidden',
          flexGrow: 1,
          width: '100%',
          boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)',
        }}
      >
        {events.length === 0 && !loading ? (
          <Box sx={{ py: 10, textAlign: 'center', bgcolor: 'white' }}>
            <Box
              sx={{
                width: 64,
                height: 64,
                borderRadius: '50%',
                bgcolor: '#f1f5f9',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mx: 'auto',
                mb: 2,
              }}
            >
              <EmptyIcon sx={{ fontSize: 32, color: '#94a3b8' }} />
            </Box>
            <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#1e293b', mb: 1 }}>
              لا توجد عمليات زراعية
            </Typography>
            <Typography variant="body2" sx={{ color: '#64748b' }}>
              لم يتم تسجيل أي نشاط تشغيلي لهذه الحوشة حتى الآن.
            </Typography>
          </Box>
        ) : (
          <Box sx={{ width: '100%' }}>
            {/* Table Header */}
            <Box
              sx={{
                bgcolor: '#f8fafc',
                px: 3,
                py: 2,
                display: { xs: 'none', md: 'flex' },
                borderBottom: '2px solid #f1f5f9',
                alignItems: 'center',
              }}
            >
              <Typography
                variant="caption"
                sx={{ width: '15%', fontWeight: 800, color: '#475569', textTransform: 'uppercase' }}
              >
                التاريخ
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  width: '25%',
                  fontWeight: 800,
                  color: '#475569',
                  textTransform: 'uppercase',
                  px: 2,
                }}
              >
                العملية
              </Typography>
              <Typography
                variant="caption"
                sx={{ width: '20%', fontWeight: 800, color: '#475569', textTransform: 'uppercase' }}
              >
                المسؤول
              </Typography>
              <Typography
                variant="caption"
                sx={{ width: '20%', fontWeight: 800, color: '#475569', textTransform: 'uppercase' }}
              >
                المؤشرات
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  width: '20%',
                  fontWeight: 800,
                  color: '#475569',
                  textTransform: 'uppercase',
                  textAlign: 'right',
                  pr: 5,
                }}
              >
                الحالة
              </Typography>
            </Box>

            {/* List Rows */}
            <Box sx={{ width: '100%' }}>
              {events.map((event) => (
                <OperationLedgerRow
                  key={event.id}
                  event={event}
                  onOpenDetails={() => {
                    setSelectedEvent(event)
                    setDrawerOpen(true)
                  }}
                />
              ))}

              {loading && page > 1 && (
                <Box sx={{ p: 3, textAlign: 'center' }}>
                  <CircularProgress size={24} />
                </Box>
              )}

              {hasMore && !loading && (
                <Box
                  sx={{
                    p: 3,
                    textAlign: 'center',
                    borderTop: '1px solid #f1f5f9',
                    bgcolor: 'white',
                  }}
                >
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={loadMore}
                    sx={{
                      borderRadius: '8px',
                      px: 4,
                      py: 1,
                      borderColor: '#e2e8f0',
                      color: '#334155',
                      fontWeight: 700,
                    }}
                  >
                    عرض المزيد من العمليات التاريخية
                  </Button>
                </Box>
              )}
            </Box>
          </Box>
        )}
      </Paper>

      {/* 3. Details Drawer */}
      <OperationalDetailsDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        event={selectedEvent}
      />
    </Box>
  )
}

export default OperationalJournal
