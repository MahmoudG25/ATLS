import React, { useEffect, useRef, useState } from 'react'

import {
  AccessTime as TimeIcon,
  Add as AddIcon,
  Engineering as EngineerIcon,
  Map as MapIcon,
  People as PeopleIcon,
  PrecisionManufacturing as OperationIcon,
  Update as UpdateIcon,
} from '@mui/icons-material'
import { Alert, Box, Button, CircularProgress, Pagination, Typography } from '@mui/material'
import { Link } from 'react-router-dom'
import dayjs from 'dayjs'
import isToday from 'dayjs/plugin/isToday'
import relativeTime from 'dayjs/plugin/relativeTime'

import { reportsApi } from '../../../services/reportsApi'
import ReportFilters from '../shared/ReportFilters'
import ReportStatusBadge from '../shared/ReportStatusBadge'

import 'dayjs/locale/ar'

dayjs.extend(relativeTime)
dayjs.extend(isToday)
dayjs.locale('ar')

const DailyTaskList = () => {
  const [reports, setReports] = useState([])
  const [filterOptions, setFilterOptions] = useState({
    operations: [],
    engineers: [],
    locations: [],
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [filters, setFilters] = useState({
    start_date: '',
    end_date: '',
    operation: '',
    engineer: '',
    location: '',
  })

  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const listTopRef = useRef(null)

  // Reset page to 1 when filters change
  useEffect(() => {
    setPage(1)
  }, [filters])

  useEffect(() => {
    fetchReports()
  }, [filters, page])

  useEffect(() => {
    const loadFilters = async () => {
      try {
        const [operationsRes, usersRes, hierarchyRes] = await Promise.all([
          reportsApi.getOperations(),
          reportsApi.getUsers(),
          reportsApi.getFarmHierarchy(),
        ])
        const flattenNodes = (nodes = []) =>
          nodes.flatMap((node) => [node, ...flattenNodes(node.children || [])])
        setFilterOptions({
          operations: operationsRes.data.results || operationsRes.data || [],
          engineers: usersRes.data.results || usersRes.data || [],
          locations: flattenNodes(hierarchyRes.data.location_nodes || []),
        })
      } catch {
        // Keep report list usable even if filter dictionaries fail.
      }
    }
    loadFilters()
  }, [])

  const fetchReports = async () => {
    try {
      setLoading(true)
      const params = Object.fromEntries(Object.entries(filters).filter(([_, v]) => v !== ''))
      params.page = page

      const res = await reportsApi.getTasks(params)

      if (res.data.results) {
        setReports(res.data.results)
        setTotalPages(Math.ceil(res.data.count / 10))
      } else {
        setReports(res.data)
        setTotalPages(1)
      }
    } catch (err) {
      setError('فشل في جلب التقارير اليومية')
    } finally {
      setLoading(false)
    }
  }

  const handlePageChange = (event, value) => {
    setPage(value)
    // Smooth scroll to top of list
    if (listTopRef.current) {
      window.scrollTo({
        top: listTopRef.current.offsetTop - 100,
        behavior: 'smooth',
      })
    }
  }

  const getExactTimeDisplay = (dateString) => {
    if (!dateString) return ''
    const d = dayjs(dateString)
    if (d.isToday()) {
      return `اليوم • ${d.format('hh:mm A')}`
    }
    return d.format('DD/MM/YYYY • hh:mm A')
  }

  const getRelativeTimeDisplay = (report) => {
    if (!report.updated_at) {
      return `مُنشأ منذ ${dayjs(report.created_at || report.report_date).fromNow(true)}`
    }
    const created = dayjs(report.created_at)
    const updated = dayjs(report.updated_at)
    if (updated.diff(created, 'minute') < 1) {
      return `مُنشأ منذ ${created.fromNow(true)}`
    }
    return `مُحدث منذ ${updated.fromNow(true)}`
  }

  return (
    <Box sx={{ maxWidth: '900px', margin: '0 auto', pb: 8 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography
          variant="h5"
          fontWeight="800"
          sx={{ display: 'flex', alignItems: 'center', gap: 1, color: '#0f172a' }}
        >
          السجل التشغيلي
        </Typography>
        <Button
          component={Link}
          to="new"
          variant="contained"
          startIcon={<AddIcon />}
          sx={{
            borderRadius: 1,
            fontWeight: 700,
            px: 3,
            bgcolor: '#0f5238',
            '&:hover': { bgcolor: '#064e3b' },
          }}
        >
          تقرير جديد
        </Button>
      </Box>

      <ReportFilters filters={filters} onFilterChange={setFilters} options={filterOptions} />

      <div ref={listTopRef} />

      {error && (
        <Alert severity="error" sx={{ mb: 5 }}>
          {error}
        </Alert>
      )}

      {loading && reports.length === 0 ? (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      ) : reports.length === 0 ? (
        <div className="p-8 text-center bg-[#f8fafc] border border-dashed border-[#cbd5e1] rounded-md">
          <Typography color="text.secondary" fontWeight="600">
            لا توجد تقارير تشغيلية مطابقة.
          </Typography>
        </div>
      ) : (
        <Box sx={{ opacity: loading ? 0.6 : 1, transition: 'opacity 0.2s ease-in-out' }}>
          <div className="flex flex-col gap-3">
            {reports.map((report) => (
              <Link
                key={report.id}
                to={`/reports/tasks/${report.id}`}
                className="block bg-white border border-[#e2e8f0] rounded-md hover:border-[#94a3b8] transition-colors shadow-sm"
                style={{ textDecoration: 'none', color: 'inherit' }}
              >
                <div className="p-4 flex flex-col md:flex-row md:items-start gap-4">
                  {/* Left side: Temporal & Status */}
                  <div className="flex-shrink-0 md:w-48 flex flex-col gap-2">
                    <div className="flex items-center gap-2">
                      <ReportStatusBadge status={report.status} />
                    </div>

                    <div className="flex flex-col gap-1 mt-1">
                      <div className="text-[12px] font-bold text-[#1e293b] flex items-center gap-1">
                        <TimeIcon sx={{ fontSize: 14, color: '#64748b' }} />
                        {getExactTimeDisplay(report.updated_at || report.created_at)}
                      </div>
                      <div className="text-[11px] font-bold text-[#64748b] flex items-center gap-1">
                        <UpdateIcon sx={{ fontSize: 13 }} />
                        {getRelativeTimeDisplay(report)}
                      </div>
                    </div>

                    <div className="text-xs text-[#475569] font-semibold mt-1">
                      تاريخ العمل: {report.report_date}
                    </div>
                  </div>

                  {/* Middle: Operations & Location */}
                  <div className="flex-grow flex flex-col gap-2">
                    <div className="flex items-start gap-2">
                      <OperationIcon sx={{ color: '#0f5238', mt: 0.5, fontSize: 18 }} />
                      <div>
                        <h3 className="font-bold text-[#0f172a] text-base leading-tight">
                          {report.operation_summary || report.operation_name}
                        </h3>
                        <div className="flex items-center gap-1 text-sm font-semibold text-[#334155] mt-1">
                          <MapIcon sx={{ fontSize: 16, color: '#64748b' }} />
                          {report.location_path || report.enclosure_name}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Right side: Engineer & Labor summary */}
                  <div className="flex-shrink-0 md:w-56 flex flex-col gap-2 md:border-r md:border-[#e2e8f0] md:pr-4">
                    <div className="flex items-center gap-1.5 text-sm font-semibold text-[#1e293b]">
                      <EngineerIcon sx={{ fontSize: 18, color: '#64748b' }} />
                      {report.engineer_name}
                    </div>
                    <div className="flex items-center gap-1.5 text-xs font-semibold text-[#475569]">
                      <PeopleIcon sx={{ fontSize: 16, color: '#64748b' }} />
                      إجمالي العمالة:{' '}
                      {(report.company_workers || 0) + (report.contractor_workers || 0)}
                    </div>
                    {report.operation_logs && report.operation_logs.length > 1 && (
                      <div className="inline-block mt-1 bg-[#f1f5f9] text-[#475569] text-[10px] font-bold px-2 py-0.5 rounded">
                        {report.operation_logs.length} أحداث تشغيلية
                      </div>
                    )}
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <Box display="flex" justifyContent="center" mt={4} pt={2}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={handlePageChange}
                color="primary"
                size="large"
                sx={{
                  '& .MuiPaginationItem-root': {
                    fontWeight: 700,
                  },
                }}
              />
            </Box>
          )}
        </Box>
      )}
    </Box>
  )
}

export default DailyTaskList
