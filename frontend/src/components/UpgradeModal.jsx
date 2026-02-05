import { useNavigate } from 'react-router-dom'
import { useTheme } from '../context/ThemeContext'

export default function UpgradeModal({ isOpen, onClose, error }) {
  const navigate = useNavigate()
  const { isDark } = useTheme()

  if (!isOpen) return null

  const errorType = error?.error || 'limit_exceeded'
  const message = error?.message || 'You have reached your plan limit.'

  const getTitle = () => {
    switch (errorType) {
      case 'storage_limit':
        return 'Storage Limit Reached'
      case 'document_limit':
        return 'Document Limit Reached'
      case 'file_size_limit':
        return 'File Too Large'
      case 'api_rate_limit':
        return 'API Limit Reached'
      default:
        return 'Upgrade Required'
    }
  }

  const getIcon = () => {
    switch (errorType) {
      case 'storage_limit':
        return (
          <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
          </svg>
        )
      case 'document_limit':
        return (
          <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        )
      case 'file_size_limit':
        return (
          <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        )
      case 'api_rate_limit':
        return (
          <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        )
      default:
        return (
          <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        )
    }
  }

  const handleUpgrade = () => {
    onClose()
    navigate('/pricing')
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className={`relative w-full max-w-md mx-4 rounded-2xl p-8 ${
        isDark ? 'bg-[#0a1214] border border-white/10' : 'bg-white border border-black/10'
      }`}>
        {/* Icon */}
        <div className={`flex justify-center mb-6 ${isDark ? 'text-dark-accent' : 'text-light-accent'}`}>
          {getIcon()}
        </div>

        {/* Title */}
        <h2 className={`text-2xl font-bold text-center mb-3 ${isDark ? 'text-dark-text' : 'text-light-text'}`}>
          {getTitle()}
        </h2>

        {/* Message */}
        <p className={`text-center mb-8 ${isDark ? 'text-dark-text/70' : 'text-light-text/70'}`}>
          {message}
        </p>

        {/* Plan Comparison */}
        <div className={`mb-8 p-4 rounded-xl ${isDark ? 'bg-white/5' : 'bg-black/5'}`}>
          <p className={`text-sm text-center ${isDark ? 'text-dark-text/60' : 'text-light-text/60'}`}>
            Upgrade to unlock:
          </p>
          <ul className={`mt-3 space-y-2 ${isDark ? 'text-dark-text' : 'text-light-text'}`}>
            <li className="flex items-center gap-2 text-sm">
              <svg className={`w-4 h-4 ${isDark ? 'text-dark-accent' : 'text-light-accent'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              More storage space (up to 50GB)
            </li>
            <li className="flex items-center gap-2 text-sm">
              <svg className={`w-4 h-4 ${isDark ? 'text-dark-accent' : 'text-light-accent'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Unlimited documents
            </li>
            <li className="flex items-center gap-2 text-sm">
              <svg className={`w-4 h-4 ${isDark ? 'text-dark-accent' : 'text-light-accent'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Larger file uploads (up to 100MB)
            </li>
            <li className="flex items-center gap-2 text-sm">
              <svg className={`w-4 h-4 ${isDark ? 'text-dark-accent' : 'text-light-accent'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              More API calls (up to 5000/day)
            </li>
          </ul>
        </div>

        {/* Buttons */}
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className={`flex-1 py-3 rounded-xl font-medium transition-all ${
              isDark
                ? 'bg-white/10 hover:bg-white/20 text-dark-text'
                : 'bg-black/10 hover:bg-black/20 text-light-text'
            }`}
          >
            Not Now
          </button>
          <button
            onClick={handleUpgrade}
            className={`flex-1 py-3 rounded-xl font-medium transition-all ${
              isDark
                ? 'bg-dark-accent text-dark-bg hover:opacity-90'
                : 'bg-light-accent text-white hover:opacity-90'
            }`}
          >
            View Plans
          </button>
        </div>
      </div>
    </div>
  )
}
