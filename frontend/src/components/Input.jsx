import { useTheme } from '../context/ThemeContext'

export default function Input({ 
  label, 
  type = 'text', 
  placeholder, 
  value, 
  onChange, 
  error,
  icon,
  ...props 
}) {
  const { isDark } = useTheme()
  
  return (
    <div className="mb-4">
      {label && (
        <label className={`block text-sm font-medium mb-2 ${
          isDark ? 'text-dark-text' : 'text-[#062A33]'
        }`}>
          {label}
        </label>
      )}
      <div className="relative">
        {icon && (
          <div className={`absolute left-3 top-1/2 -translate-y-1/2 ${
            isDark ? 'text-dark-text/50' : 'text-[#062A33]/50'
          }`}>
            {icon}
          </div>
        )}
        <input
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          className={`
            w-full px-4 py-3 rounded-xl
            ${icon ? 'pl-10' : ''}
            ${isDark 
              ? 'bg-black/20 border-white/10 text-dark-text placeholder:text-dark-text/40 focus:ring-dark-accent/50' 
              : 'bg-white/50 border-[#1FE0A5]/20 text-[#062A33] placeholder:text-[#062A33]/40 focus:ring-light-accent/50'
            }
            focus:outline-none focus:ring-2
            transition-all duration-200
            ${error ? 'border-red-500 focus:ring-red-500/50' : ''}
          `}
          {...props}
        />
      </div>
      {error && (
        <p className="mt-1 text-sm text-red-400">{error}</p>
      )}
    </div>
  )
}
