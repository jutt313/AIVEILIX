import { useState, useEffect } from 'react'
import { useTheme } from '../context/ThemeContext'
import { bucketsAPI } from '../services/api'
import Button from './Button'
import Input from './Input'

const PRESET_COLORS = [
  '#2DFFB7', '#FF6B6B', '#4ECDC4', '#FFE66D', '#A78BFA',
  '#FB923C', '#38BDF8', '#F472B6', '#34D399', '#FBBF24',
  '#818CF8', '#F87171', '#22D3EE', '#C084FC', '#A3E635',
  '#FF8A65',
]

const PERMISSION_OPTIONS = [
  { key: 'can_view', label: 'View' },
  { key: 'can_chat', label: 'Chat' },
  { key: 'can_upload', label: 'Upload' },
  { key: 'can_delete', label: 'Delete' },
]

export default function AddTeamMemberModal({ isOpen, onClose, onCreate }) {
  const { isDark } = useTheme()
  const [name, setName] = useState('')
  const [realEmail, setRealEmail] = useState('')
  const [password, setPassword] = useState('')
  const [color, setColor] = useState(PRESET_COLORS[0])
  const [customColor, setCustomColor] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const [permissions, setPermissions] = useState({
    can_view: true,
    can_chat: true,
    can_upload: false,
    can_delete: false,
  })
  const [buckets, setBuckets] = useState([])
  const [selectedBuckets, setSelectedBuckets] = useState([])
  const [bucketsLoading, setBucketsLoading] = useState(false)

  useEffect(() => {
    if (isOpen) loadBuckets()
  }, [isOpen])

  const loadBuckets = async () => {
    setBucketsLoading(true)
    try {
      const res = await bucketsAPI.list()
      setBuckets(res.data?.buckets || res.data || [])
    } catch {
      setBuckets([])
    } finally {
      setBucketsLoading(false)
    }
  }

  const togglePermission = (key) => {
    setPermissions(prev => ({ ...prev, [key]: !prev[key] }))
  }

  const toggleBucket = (bucketId) => {
    setSelectedBuckets(prev =>
      prev.includes(bucketId) ? prev.filter(id => id !== bucketId) : [...prev, bucketId]
    )
  }

  if (!isOpen) return null

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!name.trim()) { setError('Name is required'); return }
    if (!realEmail.trim()) { setError('Email is required'); return }
    if (!password || password.length < 6) { setError('Password must be at least 6 characters'); return }

    setLoading(true)
    try {
      await onCreate(name.trim(), realEmail.trim(), password, customColor || color, selectedBuckets, permissions)
      setName('')
      setRealEmail('')
      setPassword('')
      setColor(PRESET_COLORS[0])
      setCustomColor('')
      setSelectedBuckets([])
      setPermissions({ can_view: true, can_chat: true, can_upload: false, can_delete: false })
      onClose()
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to add team member')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 dark:bg-black/50 bg-black/30 backdrop-blur-sm">
      <div className="w-full max-w-lg rounded-3xl backdrop-blur-xl dark:border-white/10 border-black/10 dark:bg-white/5 bg-white/80 shadow-xl p-8 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold dark:text-dark-text text-light-text">
            Add Team Member
          </h2>
          <button onClick={onClose} className="p-2 rounded-lg dark:hover:bg-white/10 hover:bg-black/10 transition-colors dark:text-dark-text/70 text-light-text/70">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <Input label="Name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Member's display name" />
          <Input label="Real Email" type="email" value={realEmail} onChange={(e) => setRealEmail(e.target.value)} placeholder="Their personal email (for reference)" />
          <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Login password (min 6 chars)" autoComplete="new-password" />

          {/* Color Picker */}
          <div>
            <label className="block text-sm font-medium mb-2 dark:text-dark-text text-light-text">
              Tracking Color
            </label>
            <div className="flex flex-wrap gap-2 mb-2">
              {PRESET_COLORS.map((c) => (
                <button
                  key={c}
                  type="button"
                  onClick={() => { setColor(c); setCustomColor('') }}
                  className={`w-7 h-7 rounded-full border-2 transition-all ${
                    color === c && !customColor ? 'border-white scale-110' : 'border-transparent'
                  }`}
                  style={{ backgroundColor: c }}
                  title={c}
                />
              ))}
            </div>
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={customColor}
                onChange={(e) => setCustomColor(e.target.value)}
                placeholder="#hex"
                className="w-24 px-3 py-1.5 rounded-lg bg-transparent border dark:border-white/10 border-black/10 text-sm dark:text-dark-text text-light-text focus:outline-none"
              />
              {customColor && (
                <div className="w-6 h-6 rounded-full border border-white/20" style={{ backgroundColor: customColor }} />
              )}
            </div>
          </div>

          {/* Permissions */}
          <div>
            <label className="block text-sm font-medium mb-2 dark:text-dark-text text-light-text">
              Permissions
            </label>
            <div className="flex flex-wrap gap-2">
              {PERMISSION_OPTIONS.map(({ key, label }) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => togglePermission(key)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors border ${
                    permissions[key]
                      ? 'dark:bg-dark-accent/30 dark:text-dark-accent dark:border-dark-accent/50 bg-light-accent/20 text-light-accent border-light-accent/50'
                      : 'dark:bg-white/5 dark:text-dark-text/50 dark:border-white/10 bg-black/5 text-light-text/50 border-black/10'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
            <p className="text-xs dark:text-dark-text/40 text-light-text/40 mt-1.5">
              Applied to all assigned buckets
            </p>
          </div>

          {/* Bucket Access */}
          <div>
            <label className="block text-sm font-medium mb-2 dark:text-dark-text text-light-text">
              Bucket Access
              {selectedBuckets.length > 0 && (
                <span className="ml-2 px-2 py-0.5 rounded-full text-xs dark:bg-dark-accent/20 dark:text-dark-accent bg-light-accent/20 text-light-accent">
                  {selectedBuckets.length} selected
                </span>
              )}
            </label>
            {bucketsLoading ? (
              <div className="flex justify-center py-4">
                <div className="animate-spin rounded-full h-5 w-5 border-t-2 dark:border-dark-accent border-light-accent" />
              </div>
            ) : buckets.length === 0 ? (
              <p className="text-sm dark:text-dark-text/40 text-light-text/40">No buckets available</p>
            ) : (
              <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                {buckets.map(bucket => {
                  const selected = selectedBuckets.includes(bucket.id)
                  return (
                    <button
                      key={bucket.id}
                      type="button"
                      onClick={() => toggleBucket(bucket.id)}
                      className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-left transition-colors border ${
                        selected
                          ? 'dark:bg-dark-accent/15 dark:border-dark-accent/30 dark:text-dark-text bg-light-accent/10 border-light-accent/30 text-light-text'
                          : 'dark:bg-white/3 dark:border-white/5 dark:text-dark-text/60 bg-black/3 border-black/5 text-light-text/60 dark:hover:bg-white/8 hover:bg-black/8'
                      }`}
                    >
                      <div className={`w-4 h-4 rounded flex items-center justify-center border flex-shrink-0 transition-colors ${
                        selected
                          ? 'dark:bg-dark-accent dark:border-dark-accent bg-light-accent border-light-accent'
                          : 'dark:border-white/20 border-black/20'
                      }`}>
                        {selected && (
                          <svg className="w-2.5 h-2.5 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                          </svg>
                        )}
                      </div>
                      <span className="text-sm truncate">{bucket.name}</span>
                      <span className="ml-auto text-xs dark:text-dark-text/30 text-light-text/30 flex-shrink-0">
                        {bucket.file_count || 0} files
                      </span>
                    </button>
                  )
                })}
              </div>
            )}
          </div>

          <div className="flex gap-3 pt-2">
            <Button variant="secondary" onClick={onClose} className="flex-1" disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" className="flex-1" loading={loading}>
              Add Member
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
