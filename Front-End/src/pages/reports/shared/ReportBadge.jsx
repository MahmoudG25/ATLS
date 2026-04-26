import React from 'react';
import { Chip } from '@mui/material';

const SECTOR_COLORS = {
  A:          { bg: '#E8F5E9', border: '#4CAF50', text: '#1B5E20' },
  B:          { bg: '#E3F2FD', border: '#2196F3', text: '#0D47A1' },
  C:          { bg: '#FFF3E0', border: '#FF9800', text: '#E65100' },
  D:          { bg: '#F3E5F5', border: '#9C27B0', text: '#4A148C' },
  greenhouse: { bg: '#E0F2F1', border: '#00BCD4', text: '#006064' },
  new_farms:  { bg: '#FCE4EC', border: '#E91E63', text: '#880E4F' },
  default:    { bg: '#f1f5f9', border: '#cbd5e1', text: '#475569' }
};

export const VARIETY_ICONS = {
  medjool:   '🌴',
  saidi:     '🌿',
  lemon:     '🍋',
  greenhouse:'🏗️',
  other:     '🔧',
  default:   '📌'
};

const ReportBadge = ({ type, value, label }) => {
  if (type === 'sector') {
    const colorStyle = SECTOR_COLORS[value] || SECTOR_COLORS.default;
    return (
      <Chip 
        label={label || value}
        size="small"
        sx={{
          backgroundColor: colorStyle.bg,
          color: colorStyle.text,
          border: `1px solid ${colorStyle.border}`,
          fontWeight: 700,
          borderRadius: 1.5
        }}
      />
    );
  }

  if (type === 'variety') {
    const icon = VARIETY_ICONS[value] || VARIETY_ICONS.default;
    return (
      <span className="inline-flex items-center gap-1 font-semibold text-slate-700 bg-slate-50 px-2 py-0.5 rounded-md border border-slate-200">
        <span style={{ fontSize: '1.1rem' }}>{icon}</span> {label || value}
      </span>
    );
  }

  return <Chip label={label} size="small" />;
};

export default ReportBadge;
