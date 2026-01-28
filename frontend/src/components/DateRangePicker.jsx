import { useState, useRef, useEffect } from 'react'
import { useTheme } from '../context/ThemeContext'

export default function DateRangePicker({ onDateRangeChange, defaultDays = 30 }) {
  const { isDark } = useTheme()
  const [isOpen, setIsOpen] = useState(false)
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const pickerRef = useRef(null)

  // Set default dates (30 days ago to today)
  useEffect(() => {
    const end = new Date()
    const start = new Date()
    start.setDate(start.getDate() - defaultDays)
    
    setEndDate(end.toISOString().split('T')[0])
    setStartDate(start.toISOString().split('T')[0])
  }, [defaultDays])

  // Close picker when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (pickerRef.current && !pickerRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const handleApply = () => {
    if (startDate && endDate) {
      if (new Date(startDate) <= new Date(endDate)) {
        onDateRangeChange(startDate, endDate)
        setIsOpen(false)
      } else {
        alert('Start date must be before or equal to end date')
      }
    }
  }

  const formatDateRange = () => {
    if (!startDate || !endDate) return 'Select Date Range'
    const start = new Date(startDate)
    const end = new Date(endDate)
    return `${start.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${end.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`
  }

  return (
    <div className="relative" ref={pickerRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition-colors ${
          isOpen
            ? isDark
              ? 'bg-dark-accent text-dark-bg'
              : 'bg-light-accent text-white'
            : isDark
              ? 'bg-white/5 hover:bg-white/10 text-dark-text/70'
              : 'bg-black/5 hover:bg-black/10 text-[#062A33]/70'
        }`}
        title="Select Date Range"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <span className="text-xs font-medium">{formatDateRange()}</span>
      </button>

      {isOpen && (
        <div className={`absolute right-0 mt-2 w-80 rounded-lg shadow-lg border z-50 ${
          isDark
            ? 'bg-dark-surface border-white/10'
            : 'bg-[#F6FFFC] border-[#1FE0A5]/20'
        }`}>
          <div className="p-4 space-y-4">
            <div>
              <label className={`block text-sm font-medium mb-2 ${
                isDark ? 'text-dark-text' : 'text-[#062A33]'
              }`}>
                From Date
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                max={endDate || undefined}
                className={`w-full px-3 py-2 rounded-lg border focus:outline-none focus:ring-2 ${
                  isDark
                    ? 'bg-black/20 border-white/10 text-dark-text focus:ring-dark-accent/50'
                    : 'bg-white/50 border-[#1FE0A5]/20 text-[#062A33] focus:ring-light-accent/50'
                }`}
              />
            </div>
            <div>
              <label className={`block text-sm font-medium mb-2 ${
                isDark ? 'text-dark-text' : 'text-[#062A33]'
              }`}>
                To Date
              </label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                min={startDate || undefined}
                max={new Date().toISOString().split('T')[0]}
                className={`w-full px-3 py-2 rounded-lg border focus:outline-none focus:ring-2 ${
                  isDark
                    ? 'bg-black/20 border-white/10 text-dark-text focus:ring-dark-accent/50'
                    : 'bg-white/50 border-[#1FE0A5]/20 text-[#062A33] focus:ring-light-accent/50'
                }`}
              />
            </div>
            <div className="flex items-center gap-2 pt-2">
              <button
                onClick={handleApply}
                className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
                  isDark
                    ? 'bg-dark-accent hover:bg-emerald-400 text-dark-bg'
                    : 'bg-light-accent hover:bg-[#1FE0A5] text-white'
                }`}
              >
                Apply
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  isDark
                    ? 'bg-white/5 hover:bg-white/10 text-dark-text/70'
                    : 'bg-black/5 hover:bg-black/10 text-[#062A33]/70'
                }`}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
