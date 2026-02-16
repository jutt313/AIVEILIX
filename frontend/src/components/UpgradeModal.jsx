import { useNavigate } from 'react-router-dom'
import { useTheme } from '../context/ThemeContext'

export default function UpgradeModal({ isOpen, onClose, error }) {
  const navigate = useNavigate()
  const { isDark } = useTheme()

  if (!isOpen) return null

  const detail = typeof error === 'object' ? error : {}
  const errorType = detail.error || 'limit_exceeded'
  const message = detail.message || 'You have reached your plan limit.'
  const currentPlanName = detail.current_plan_name || 'Free Trial'
  const nextPlanName = detail.next_plan_name || ''
  const nextLimits = detail.next_plan_limits || {}

  const getTitle = () => {
    switch (errorType) {
      case 'storage_limit': return 'Storage Limit Reached'
      case 'document_limit': return 'Document Limit Reached'
      case 'file_size_limit': return 'File Too Large'
      case 'file_image_limit': return 'Too Many Images In File'
      case 'api_rate_limit': return 'API Limit Reached'
      case 'chat_limit': return 'Chat Limit Reached'
      case 'bucket_limit': return 'Bucket Limit Reached'
      case 'bucket_chat_limit': return 'Bucket Chat Limit'
      case 'mcp_limit': return 'MCP Query Limit'
      case 'concurrent_limit': return 'Processing Limit'
      case 'batch_limit': return 'Batch Upload Limit'
      case 'conversation_limit': return 'Conversation Limit'
      case 'team_member_limit': return 'Team Member Limit'
      default: return 'Upgrade Required'
    }
  }

  const getIcon = () => {
    if (['chat_limit', 'bucket_chat_limit', 'conversation_limit'].includes(errorType)) {
      return (
        <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      )
    }
    if (['mcp_limit', 'api_rate_limit'].includes(errorType)) {
      return (
        <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      )
    }
    return (
      <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    )
  }

  const formatLimit = (key, val) => {
    if (val === -1) return 'Unlimited'
    if (key.includes('storage') || key.includes('batch_size')) return `${(val / (1024 * 1024 * 1024)).toFixed(0)}GB`
    if (key.includes('file_size')) return `${(val / (1024 * 1024)).toFixed(0)}MB`
    return val?.toLocaleString()
  }

  const highlightKeys = [
    ['storage_bytes', 'Storage'],
    ['chat_messages_per_day', 'Chat/day'],
    ['max_buckets', 'Buckets'],
    ['max_team_members', 'Team members'],
    ['max_file_size_bytes', 'Max file size'],
    ['mcp_queries_per_day', 'MCP queries/day'],
    ['bucket_chat_per_day', 'Bucket chat/day'],
    ['active_conversations_per_bucket', 'Conversations/bucket'],
    ['concurrent_processing_jobs', 'Concurrent processing'],
  ]

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />

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
        <p className={`text-center mb-2 ${isDark ? 'text-dark-text/70' : 'text-light-text/70'}`}>
          {message}
        </p>

        {/* Current plan badge */}
        <div className="flex justify-center mb-6">
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${isDark ? 'bg-white/10 text-dark-text/60' : 'bg-black/5 text-light-text/60'}`}>
            Current: {currentPlanName}
          </span>
        </div>

        {/* Next plan highlights */}
        {nextPlanName && Object.keys(nextLimits).length > 0 && (
          <div className={`mb-6 p-4 rounded-xl ${isDark ? 'bg-dark-accent/10 border border-dark-accent/20' : 'bg-light-accent/10 border border-light-accent/20'}`}>
            <p className={`text-sm font-semibold mb-3 ${isDark ? 'text-dark-accent' : 'text-light-accent'}`}>
              Upgrade to {nextPlanName}
            </p>
            <div className="grid grid-cols-2 gap-2">
              {highlightKeys.map(([key, label]) => {
                const val = nextLimits[key]
                if (val === undefined) return null
                return (
                  <div key={key} className="flex items-center gap-2">
                    <svg className={`w-3.5 h-3.5 flex-shrink-0 ${isDark ? 'text-dark-accent' : 'text-light-accent'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className={`text-xs ${isDark ? 'text-dark-text/80' : 'text-light-text/80'}`}>
                      {formatLimit(key, val)} {label}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Buttons */}
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className={`flex-1 py-3 rounded-xl font-medium transition-all ${
              isDark ? 'bg-white/10 hover:bg-white/20 text-dark-text' : 'bg-black/10 hover:bg-black/20 text-light-text'
            }`}
          >
            Not Now
          </button>
          <button
            onClick={() => { onClose(); navigate('/pricing') }}
            className={`flex-1 py-3 rounded-xl font-medium transition-all ${
              isDark ? 'bg-dark-accent text-dark-bg hover:opacity-90' : 'bg-light-accent text-white hover:opacity-90'
            }`}
          >
            View Plans
          </button>
        </div>
      </div>
    </div>
  )
}
