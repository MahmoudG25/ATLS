import React from 'react'

import { Add as AddIcon, Remove as RemoveIcon } from '@mui/icons-material'
import { Autocomplete, TextField } from '@mui/material'

// ── Styles ───────────────────────────────────────────────────────────────────
export const inputSx = {
  '& .MuiOutlinedInput-root:not(.MuiInputBase-multiline)': { height: '40px' },
  '& .MuiOutlinedInput-root': {
    backgroundColor: '#f8faf6',
    borderRadius: '0.5rem',
    fontSize: '0.875rem',
    '& fieldset': { borderColor: '#bfc9c1' },
    '&:hover fieldset': { borderColor: '#0f5238' },
    '&.Mui-focused fieldset': { borderColor: '#0f5238', borderWidth: '1.5px' },
    '&.Mui-disabled': { backgroundColor: '#e8ebe8' },
  },
}

export const dropdownPaper = {
  paper: {
    sx: {
      bgcolor: '#fff',
      mt: 0.5,
      borderRadius: '8px',
      boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
      border: '1px solid #bfc9c1',
    },
  },
}

// ── Sub-components ────────────────────────────────────────────────────────────
export const Label = ({ children }) => (
  <label className="block mb-2 font-medium text-sm text-[#191c1a]">{children}</label>
)

export const Field = ({ label, children }) => (
  <div className="flex flex-col w-full">
    <Label>{label}</Label>
    {children}
  </div>
)

export const Stepper = ({ value, onChange, error }) => {
  const borderClass = error ? 'border-[#ba1a1a]' : 'border-[#bfc9c1]'
  return (
    <div
      className={`flex items-stretch h-[40px] border ${borderClass} rounded-lg bg-[#f8faf6] overflow-hidden focus-within:outline focus-within:outline-[1.5px] focus-within:outline-[#0f5238] focus-within:-outline-offset-1`}
    >
      <button
        type="button"
        onClick={() => onChange(value + 1)}
        className={`w-[40px] border-none border-l ${borderClass} bg-transparent cursor-pointer flex items-center justify-center text-[#404943] hover:bg-[#eceeea] transition-colors`}
      >
        <AddIcon sx={{ fontSize: 18 }} />
      </button>
      <input
        type="number"
        value={value}
        min={0}
        onChange={(e) => {
          const v = parseInt(e.target.value, 10)
          onChange(isNaN(v) ? 0 : Math.max(0, v))
        }}
        className="flex-1 w-full border-none outline-none bg-transparent text-center font-semibold text-[15px] text-[#191c1a] [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
      />
      <button
        type="button"
        onClick={() => onChange(Math.max(0, value - 1))}
        className={`w-[40px] border-none border-r ${borderClass} bg-transparent cursor-pointer flex items-center justify-center text-[#404943] hover:bg-[#eceeea] transition-colors`}
      >
        <RemoveIcon sx={{ fontSize: 18 }} />
      </button>
    </div>
  )
}

export const AC = ({
  options,
  value,
  onChange,
  placeholder,
  error,
  helperText,
  disabled,
  getLabel,
}) => {
  // Safe synchronization: if value is set but not in options, purge it.
  React.useEffect(() => {
    if (value != null && options && options.length > 0) {
      const exists = options.some((o) => o.id === value)
      if (!exists) {
        onChange(null)
      }
    }
  }, [value, options, onChange])

  // Defensive guard: Ensure we only pass integer IDs or null to onChange
  const handleChange = (_, d) => {
    if (!d || !d.id) {
      onChange(null)
    } else {
      const parsedId = parseInt(d.id, 10)
      onChange(isNaN(parsedId) ? null : parsedId)
    }
  }

  return (
    <Autocomplete
      disabled={disabled}
      options={options}
      getOptionLabel={getLabel || ((o) => o.name || '')}
      value={options?.find((o) => o.id === value) || null}
      onChange={handleChange}
      slotProps={dropdownPaper}
      sx={inputSx}
      noOptionsText="لا توجد خيارات"
      renderInput={(params) => (
        <TextField
          {...params}
          fullWidth
          placeholder={placeholder}
          size="small"
          error={error}
          helperText={helperText}
        />
      )}
    />
  )
}
