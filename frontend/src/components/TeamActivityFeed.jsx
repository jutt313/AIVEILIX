import { useState, useEffect } from 'react'
import { useTheme } from '../context/ThemeContext'
import { teamAPI } from '../services/api'

export default function TeamActivityFeed({ memberId = null, bucketId = null }) {
  const { isDark } = useTheme()
  const [activities, setActivities] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadActivity()
  }, [memberId, bucketId])

  const loadActivity = async () => {
    setLoading(true)
    try {
      const res = await teamAPI.getActivity(memberId, bucketId, 50)
      setActivities(res.data?.activities || res.data || [])
    } catch (err) {
      console.error('Failed to load activity:', err)
      setActivities([])
    } finally {
      setLoading(false)
    }
  }

  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  const getActionLabel = (action) => {
    switch (action) {
      case 'file_upload': return 'uploaded'
      case 'file_delete': return 'deleted'
      case 'chat_message': return 'sent message in'
      case 'api_key_create': return 'created API key'
      default: return action?.replace(/_/g, ' ') || 'performed action'
    }
  }

  if (loading) {
    return (
      <div className="text-center py-6">
        <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 dark:border-dark-accent border-light-accent mx-auto" />
      </div>
    )
  }

  if (activities.length === 0) {
    return (
      <p className="text-sm text-center py-6 dark:text-dark-text/50 text-light-text/50">
        No activity yet
      </p>
    )
  }

  return (
    <div className="space-y-2 max-h-80 overflow-y-auto">
      {activities.map((activity, idx) => (
        <div
          key={activity.id || idx}
          className="flex items-start gap-3 p-2 rounded-lg dark:hover:bg-white/5 hover:bg-black/5 transition-colors"
        >
          <div
            className="w-2.5 h-2.5 rounded-full flex-shrink-0 mt-1.5"
            style={{ backgroundColor: activity.member_color || '#888' }}
            title={activity.member_name || ''}
          />
          <div className="flex-1 min-w-0">
            <p className="text-sm dark:text-dark-text text-light-text">
              <span className="font-medium" style={{ color: activity.member_color || undefined }}>
                {activity.member_name || 'Member'}
              </span>
              {' '}{getActionLabel(activity.action_type)}
              {activity.resource_name && (
                <span className="dark:text-dark-text/70 text-light-text/70">
                  {' '}{activity.resource_name}
                </span>
              )}
            </p>
            <p className="text-xs dark:text-dark-text/40 text-light-text/40 mt-0.5">
              {formatTime(activity.created_at)}
            </p>
          </div>
        </div>
      ))}
    </div>
  )
}
