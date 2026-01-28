import { useTheme } from '../context/ThemeContext'

export default function StatCard({ title, value, icon, formatValue }) {
  const { isDark } = useTheme()
  const formattedValue = formatValue ? formatValue(value) : value

  return (
    <div className={`rounded-xl p-6 backdrop-blur-xl border transition-all duration-300 cursor-pointer group ${
      isDark
        ? 'border-white/10 bg-white/5 hover:border-[#0B3C49]/50 hover:bg-[#0B3C49]/10'
        : 'border-light-accent/20 bg-light-surface hover:border-light-accent hover:bg-light-accent/5'
    }`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className={`text-sm font-medium transition-colors ${
          isDark
            ? 'text-dark-text/70 group-hover:text-[#0B3C49]'
            : 'text-[#062A33]/70 group-hover:text-light-accent'
        }`}>
          {title}
        </h3>
        {icon && (
          <div className={`transition-colors ${
            isDark
              ? 'text-dark-accent group-hover:text-[#0B3C49]'
              : 'text-light-accent group-hover:text-[#0B3C49]'
          }`}>
            {icon}
          </div>
        )}
      </div>
      <p className={`text-3xl font-bold transition-colors ${
        isDark
          ? 'text-dark-text group-hover:text-[#0B3C49]'
          : 'text-[#062A33] group-hover:text-light-accent'
      }`}>
        {formattedValue}
      </p>
    </div>
  )
}
