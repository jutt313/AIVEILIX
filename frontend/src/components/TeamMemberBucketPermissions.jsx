import { useState, useEffect } from 'react'
import { useTheme } from '../context/ThemeContext'
import { teamAPI, bucketsAPI } from '../services/api'
import Button from './Button'

export default function TeamMemberBucketPermissions({ memberId, onClose }) {
  const { isDark } = useTheme()
  const [buckets, setBuckets] = useState([])
  const [access, setAccess] = useState([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    loadData()
  }, [memberId])

  const loadData = async () => {
    setLoading(true)
    try {
      const [bucketsRes, accessRes] = await Promise.all([
        bucketsAPI.list(),
        teamAPI.getMemberBuckets(memberId),
      ])
      const allBuckets = bucketsRes.data?.buckets || bucketsRes.data || []
      const memberAccess = accessRes.data || []

      // Build permission map
      const accessMap = {}
      memberAccess.forEach(a => {
        accessMap[a.bucket_id] = {
          can_view: a.can_view,
          can_chat: a.can_chat,
          can_upload: a.can_upload,
          can_delete: a.can_delete,
        }
      })

      setBuckets(allBuckets)
      setAccess(accessMap)
    } catch (err) {
      setError('Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const togglePermission = (bucketId, perm) => {
    setAccess(prev => {
      const current = prev[bucketId] || { can_view: false, can_chat: false, can_upload: false, can_delete: false }
      return {
        ...prev,
        [bucketId]: { ...current, [perm]: !current[perm] }
      }
    })
  }

  const handleSave = async () => {
    setSaving(true)
    setError('')
    try {
      const permissions = Object.entries(access)
        .filter(([, perms]) => perms.can_view || perms.can_chat || perms.can_upload || perms.can_delete)
        .map(([bucketId, perms]) => ({
          bucket_id: bucketId,
          ...perms,
        }))

      await teamAPI.assignBuckets(memberId, permissions)
      if (onClose) onClose()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save permissions')
    } finally {
      setSaving(false)
    }
  }

  const permLabels = [
    { key: 'can_view', label: 'View' },
    { key: 'can_chat', label: 'Chat' },
    { key: 'can_upload', label: 'Upload' },
    { key: 'can_delete', label: 'Delete' },
  ]

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 dark:border-dark-accent border-light-accent mx-auto" />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold dark:text-dark-text text-light-text">Bucket Permissions</h3>

      {error && (
        <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
          {error}
        </div>
      )}

      {buckets.length === 0 ? (
        <p className="text-sm dark:text-dark-text/70 text-light-text/70">No buckets available</p>
      ) : (
        <div className="space-y-2 max-h-80 overflow-y-auto">
          {buckets.map(bucket => {
            const perms = access[bucket.id] || { can_view: false, can_chat: false, can_upload: false, can_delete: false }
            return (
              <div
                key={bucket.id}
                className="p-3 rounded-xl dark:bg-black/10 bg-light-surface/80 dark:border-white/10 border-black/10 border"
              >
                <p className="font-medium text-sm dark:text-dark-text text-light-text mb-2">{bucket.name}</p>
                <div className="flex flex-wrap gap-2">
                  {permLabels.map(({ key, label }) => (
                    <button
                      key={key}
                      type="button"
                      onClick={() => togglePermission(bucket.id, key)}
                      className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                        perms[key]
                          ? 'dark:bg-dark-accent/30 dark:text-dark-accent bg-light-accent/20 text-light-accent border border-dark-accent/50'
                          : 'dark:bg-white/5 dark:text-dark-text/50 bg-black/5 text-light-text/50 border border-transparent'
                      }`}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      )}

      <div className="flex gap-3 pt-2">
        <Button variant="secondary" onClick={onClose} className="flex-1" disabled={saving}>Cancel</Button>
        <Button onClick={handleSave} className="flex-1" loading={saving}>Save Permissions</Button>
      </div>
    </div>
  )
}
