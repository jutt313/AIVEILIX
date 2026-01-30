import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { useTheme } from '../context/ThemeContext'
import DateRangePicker from './DateRangePicker'

export default function DashboardGraph({ data, onDateRangeChange, startDate, endDate }) {
  const { isDark } = useTheme()
  const axisColor = isDark ? 'rgba(230, 241, 245, 0.6)' : 'rgba(6, 42, 51, 0.6)'
  const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(31, 224, 165, 0.2)'

  // Different colors for dark/light mode
  const bucketsColor = isDark ? '#10B981' : '#0B3C49' // Emerald for dark, dark blue for light
  
  // Show empty state if no data
  if (!data || data.length === 0) {
    return (
      <div className={`rounded-xl p-6 backdrop-blur-xl border ${
        isDark ? 'border-white/10 bg-white/5' : 'border-light-accent/20 bg-light-surface'
      }`}>
        <div className="flex items-center justify-between mb-4">
          <h3 className={`text-lg font-semibold ${isDark ? 'text-dark-text' : 'text-[#062A33]'}`}>
            Activity Overview
          </h3>
          {onDateRangeChange && (
            <DateRangePicker
              onDateRangeChange={onDateRangeChange}
              defaultDays={7}
            />
          )}
        </div>
        <div className={`flex items-center justify-center h-[300px] ${isDark ? 'text-dark-text/50' : 'text-[#062A33]/70'}`}>
          No activity data yet
        </div>
      </div>
    )
  }

  return (
    <div className={`rounded-xl p-6 backdrop-blur-xl border transition-all duration-300 ${
      isDark
        ? 'border-white/10 bg-white/5 hover:border-[#0B3C49]/50 hover:bg-[#0B3C49]/5'
        : 'border-light-accent/20 bg-light-surface hover:border-light-accent hover:bg-light-accent/5'
    }`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className={`text-lg font-semibold ${isDark ? 'text-dark-text' : 'text-[#062A33]'}`}>
          Activity Overview
        </h3>
        {onDateRangeChange && (
          <DateRangePicker
            onDateRangeChange={onDateRangeChange}
            defaultDays={7}
          />
        )}
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorFiles" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="colorBuckets" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={bucketsColor} stopOpacity={0.8}/>
              <stop offset="95%" stopColor={bucketsColor} stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="colorStorage" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#1FE0A5" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#1FE0A5" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
          <XAxis 
            dataKey="date" 
            tick={{ fill: axisColor, fontSize: 12 }}
            axisLine={{ stroke: gridColor }}
            tickLine={{ stroke: gridColor }}
            tickFormatter={(value) => {
              // Format date as MM/DD
              const date = new Date(value)
              return `${date.getMonth() + 1}/${date.getDate()}`
            }}
          />
          <YAxis 
            tick={{ fill: axisColor, fontSize: 12 }}
            axisLine={{ stroke: gridColor }}
            tickLine={{ stroke: gridColor }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: isDark ? 'rgba(5, 11, 13, 0.95)' : 'rgba(246, 255, 252, 0.95)',
              border: isDark ? '1px solid rgba(255, 255, 255, 0.1)' : '1px solid rgba(31, 224, 165, 0.3)',
              borderRadius: '8px',
              color: isDark ? '#E6F1F5' : '#0B3C49'
            }}
          />
          <Legend wrapperStyle={{ color: isDark ? '#E6F1F5' : '#062A33' }} />
          <Area type="monotone" dataKey="files" stackId="1" stroke="#3B82F6" fill="url(#colorFiles)" name="Files" />
          <Area type="monotone" dataKey="buckets" stackId="2" stroke={bucketsColor} fill="url(#colorBuckets)" name="Buckets" />
          <Area type="monotone" dataKey="storage" stroke="#1FE0A5" fill="url(#colorStorage)" name="Storage (MB)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
