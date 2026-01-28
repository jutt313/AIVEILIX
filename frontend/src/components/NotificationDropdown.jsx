import { useNavigate } from 'react-router-dom'
import { useTheme } from '../context/ThemeContext'

export default function NotificationDropdown({
  notifications,
  loading,
  error,
  onMarkAsRead,
  onDelete,
  onMarkAllAsRead,
  onDeleteAllRead,
  onRefresh,
  onClose
}) {
  const navigate = useNavigate()
  const { isDark } = useTheme()

  const formatTime = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  const getIcon = (type, icon) => {
    if (icon) {
      // Use custom icon if provided
      switch (icon) {
        case 'check': return '✓'
        case 'error': return '✕'
        case 'file': return '📄'
        case 'folder': return '📁'
        case 'key': return '🔑'
        case 'terminal': return '💻'
        case 'message': return '💬'
        default: return '🔔'
      }
    }
    
    // Default icons based on type
    switch (type) {
      case 'login': return '✓'
      case 'mcp_run': return '💻'
      case 'file_uploaded': return '📄'
      case 'file_processed': return '✓'
      case 'bucket_created': return '📁'
      case 'api_key_created': return '🔑'
      case 'conversation_created': return '💬'
      case 'error': return '✕'
      default: return '🔔'
    }
  }

  const handleNotificationClick = (notification) => {
    if (notification.action_url) {
      navigate(notification.action_url)
      onClose()
    }
    if (!notification.is_read) {
      onMarkAsRead(notification.id)
    }
  }

  const unreadCount = notifications.filter(n => !n.is_read).length
  const readCount = notifications.filter(n => n.is_read).length

  return (
    <div 
      className={`absolute right-0 mt-2 w-96 rounded-lg shadow-2xl border z-[9999] ${
        isDark 
          ? 'bg-dark-surface border-white/10' 
          : 'bg-[#F6FFFC] border-[#1FE0A5]/20'
      }`}
      style={{ maxHeight: '600px' }}
    >
      {/* Header */}
      <div className={`flex items-center justify-between p-4 border-b ${
        isDark ? 'border-white/10' : 'border-[#1FE0A5]/20'
      }`}>
        <h3 className={`font-semibold ${isDark ? 'text-dark-text' : 'text-light-text'}`}>
          Notifications
          {unreadCount > 0 && (
            <span className={`ml-2 px-2 py-0.5 rounded-full text-xs ${
              isDark ? 'bg-red-500/20 text-red-400' : 'bg-red-100 text-red-600'
            }`}>
              {unreadCount} new
            </span>
          )}
        </h3>
        <div className="flex items-center gap-2">
          <button
            onClick={onRefresh}
            className={`p-1.5 rounded transition-colors ${
              isDark 
                ? 'hover:bg-white/10 text-dark-text/70' 
                : 'hover:bg-black/10 text-light-text/70'
            }`}
            title="Refresh"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
          <button
            onClick={onClose}
            className={`p-1.5 rounded transition-colors ${
              isDark 
                ? 'hover:bg-white/10 text-dark-text/70' 
                : 'hover:bg-black/10 text-light-text/70'
            }`}
            title="Close"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Actions */}
      {(unreadCount > 0 || readCount > 0) && (
        <div className={`flex items-center gap-2 px-4 py-2 border-b ${
          isDark ? 'border-white/10' : 'border-[#1FE0A5]/20'
        }`}>
          {unreadCount > 0 && (
            <button
              onClick={onMarkAllAsRead}
              className={`text-xs px-2 py-1 rounded transition-colors ${
                isDark 
                  ? 'hover:bg-white/10 text-dark-text/70' 
                  : 'hover:bg-black/10 text-light-text/70'
              }`}
            >
              Mark all as read
            </button>
          )}
          {readCount > 0 && (
            <button
              onClick={onDeleteAllRead}
              className={`text-xs px-2 py-1 rounded transition-colors ${
                isDark 
                  ? 'hover:bg-white/10 text-red-400' 
                  : 'hover:bg-black/10 text-red-600'
              }`}
            >
              Delete all read
            </button>
          )}
        </div>
      )}

      {/* Notifications List */}
      <div className="overflow-y-auto" style={{ maxHeight: '500px' }}>
        {error ? (
          <div className={`p-4 m-4 rounded-lg border ${
            isDark 
              ? 'bg-red-500/10 border-red-500/20 text-red-400' 
              : 'bg-red-50 border-red-200 text-red-600'
          }`}>
            <p className="text-sm font-medium mb-1">Error loading notifications</p>
            <p className="text-xs opacity-80">{error}</p>
            <button
              onClick={onRefresh}
              className={`mt-2 text-xs underline ${
                isDark ? 'text-red-300' : 'text-red-500'
              }`}
            >
              Try again
            </button>
          </div>
        ) : loading ? (
          <div className="flex items-center justify-center py-8">
            <div className={`animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 ${
              isDark ? 'border-dark-accent' : 'border-light-accent'
            }`}></div>
          </div>
        ) : notifications.length === 0 ? (
          <div className={`text-center py-8 text-sm ${
            isDark ? 'text-dark-text/50' : 'text-light-text/50'
          }`}>
            No notifications
          </div>
        ) : (
          <div className={`divide-y ${
            isDark ? 'divide-white/10' : 'divide-[#1FE0A5]/20'
          }`}>
            {notifications.map((notification) => (
              <div
                key={notification.id}
                onClick={() => handleNotificationClick(notification)}
                className={`group relative p-4 transition-colors cursor-pointer ${
                  notification.is_read
                    ? isDark
                      ? 'bg-transparent hover:bg-white/5'
                      : 'bg-transparent hover:bg-black/5'
                    : isDark
                      ? 'bg-white/5 hover:bg-white/10'
                      : 'bg-blue-50 hover:bg-blue-100'
                }`}
              >
                <div className="flex items-start gap-3">
                  {/* Icon */}
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm ${
                    isDark ? 'bg-white/10' : 'bg-black/10'
                  }`}>
                    {getIcon(notification.type, notification.icon)}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <p className={`font-medium text-sm ${
                      isDark ? 'text-dark-text' : 'text-light-text'
                    }`}>
                      {notification.title}
                    </p>
                    <p className={`text-xs mt-1 ${
                      isDark ? 'text-dark-text/70' : 'text-light-text/70'
                    }`}>
                      {notification.message}
                    </p>
                    <p className={`text-xs mt-1 ${
                      isDark ? 'text-dark-text/50' : 'text-light-text/50'
                    }`}>
                      {formatTime(notification.created_at)}
                    </p>
                  </div>

                  {/* Actions */}
                  <div className="flex-shrink-0 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    {!notification.is_read && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          onMarkAsRead(notification.id)
                        }}
                        className={`p-1.5 rounded transition-colors ${
                          isDark 
                            ? 'hover:bg-white/10 text-dark-text/70' 
                            : 'hover:bg-black/10 text-light-text/70'
                        }`}
                        title="Mark as read"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </button>
                    )}
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        onDelete(notification.id)
                      }}
                      className={`p-1.5 rounded hover:bg-red-500/10 transition-colors text-red-400`}
                      title="Delete"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
