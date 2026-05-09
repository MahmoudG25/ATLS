import React, { useState } from 'react'

import { Box, Button, Container, Grid, Stack, Typography } from '@mui/material'
import { useNavigate, useParams } from 'react-router-dom'

import EnclosureHeader from './components/EnclosureHeader'
import OperationActionBar from './components/OperationActionBar'
import OperationalJournal from './components/OperationalJournal'
import { useEnclosureProfile } from './hooks/useEnclosureProfile'

/**
 * Enclosure Dashboard (ERP Operational Workspace)
 * The central command and history ledger for a single enclosure asset.
 */
const EnclosureDashboard = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [refreshKey, setRefreshKey] = useState(0)

  const { profile, loading, error } = useEnclosureProfile(id, refreshKey)

  const handleRefresh = () => setRefreshKey((prev) => prev + 1)

  if (error) {
    return (
      <Container sx={{ py: 10, textAlign: 'center' }}>
        <Typography variant="h5" color="error" gutterBottom>
          خطأ في الوصول إلى بيانات الأصل
        </Typography>
        <Button variant="contained" onClick={() => navigate('/farm/structure')}>
          العودة للهيكل التنظيمي
        </Button>
      </Container>
    )
  }

  return (
    <Box sx={{ bgcolor: '#f8fafc', minHeight: '100vh', pb: 10 }}>
      {/* 1. Identity & Context Header */}
      <EnclosureHeader profile={profile} loading={loading} />

      <Container maxWidth={false} sx={{ px: { xs: 1, sm: 2, md: 4 } }}>
        <Stack spacing={3} sx={{ mt: -3 }}>
          {/* 2. Operational Action Bar */}
          <OperationActionBar
            enclosureId={id}
            currentNotes={profile?.asset_profile?.general_notes}
            onAction={handleRefresh}
          />

          {/* 3. The Core: Operational Reports Operations Center */}
          <Box sx={{ flexGrow: 1 }}>
            <Box sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="h6" sx={{ fontWeight: 800, color: '#0f172a' }}>
                مركز إدارة التقارير التشغيلية
              </Typography>
              <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 600 }}>
                (Operational Ledger)
              </Typography>
            </Box>
            <OperationalJournal enclosureId={id} />
          </Box>
        </Stack>
      </Container>
    </Box>
  )
}

export default EnclosureDashboard
