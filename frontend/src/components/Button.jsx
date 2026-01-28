import { useTheme } from '../context/ThemeContext'

export default function Button({ 
  children, 
  variant = 'primary', 
  loading = false, 
  disabled = false,
  type = 'button',
  onClick,
  className = '',
  ...props 
}) {
  const { isDark } = useTheme()
  
  const variants = {
    primary: isDark ? `
      bg-gradient-to-r from-dark-accent to-emerald-400
      hover:from-emerald-400 hover:to-dark-accent
      text-dark-bg font-semibold
      shadow-lg shadow-dark-accent/25
      hover:shadow-dark-accent/40
    ` : `
      bg-gradient-to-r from-light-accent to-[#1FE0A5]
      hover:from-[#1FE0A5] hover:to-light-accent
      text-white font-semibold
      shadow-lg shadow-light-accent/25
      hover:shadow-light-accent/40
    `,
    secondary: `
      bg-white/10 dark:bg-white/5
      hover:bg-white/20 dark:hover:bg-white/10
      dark:text-dark-text text-light-text
      border border-white/20
    `,
    ghost: `
      bg-transparent
      hover:bg-white/10
      dark:text-dark-text text-light-text
    `
  }

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`
        w-full px-6 py-3 rounded-xl
        font-medium
        transition-all duration-300
        disabled:opacity-50 disabled:cursor-not-allowed
        transform hover:scale-[1.02] active:scale-[0.98]
        ${variants[variant]}
        ${className}
      `}
      {...props}
    >
      {loading ? (
        <div className="flex items-center justify-center gap-2">
          <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
            <circle 
              className="opacity-25" 
              cx="12" cy="12" r="10" 
              stroke="currentColor" 
              strokeWidth="4"
              fill="none"
            />
            <path 
              className="opacity-75" 
              fill="currentColor" 
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <span>Loading...</span>
        </div>
      ) : children}
    </button>
  )
}
