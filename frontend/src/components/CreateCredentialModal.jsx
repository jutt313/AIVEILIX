import { useState } from 'react'
import Input from './Input'
import Button from './Button'

export default function CreateCredentialModal({ isOpen, onClose, onCreate, buckets }) {
  const [name, setName] = useState('')
  const [credentialType, setCredentialType] = useState('api-key') // 'api-key' or 'oauth'
  const [redirectUri, setRedirectUri] = useState('')
  const [scope, setScope] = useState('delete') // Default to full access for API keys
  const [selectedBuckets, setSelectedBuckets] = useState([]) // Empty array = all buckets (full access)
  const [showBucketDropdown, setShowBucketDropdown] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (!isOpen) return null

  const availableScopes = credentialType === 'api-key'
    ? [
        { value: 'delete', label: 'Full Access (Read, Write, Delete)' },
        { value: 'write', label: 'Read + Write' },
        { value: 'read', label: 'Read Only' }
      ]
    : [
        { value: 'chat', label: 'Full Access (Chat, Query, Read)' },
        { value: 'query', label: 'Query/Search + Read' },
        { value: 'read:files', label: 'Read Files' },
        { value: 'read:buckets', label: 'Read Buckets Only' }
      ]

  const handleBucketToggle = (bucketId) => {
    if (selectedBuckets.includes(bucketId)) {
      setSelectedBuckets(selectedBuckets.filter(id => id !== bucketId))
    } else {
      setSelectedBuckets([...selectedBuckets, bucketId])
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!name.trim()) {
      setError('Name is required')
      return
    }

    if (credentialType === 'oauth' && !redirectUri.trim()) {
      setError('Redirect URI is required for OAuth')
      return
    }

    if (!scope) {
      setError('Select a permission level')
      return
    }

    setLoading(true)
    try {
      // Convert single scope to array for backend
      const scopesArray = credentialType === 'api-key'
        ? (scope === 'read' ? ['read'] : scope === 'write' ? ['read', 'write'] : ['read', 'write', 'delete'])
        : (scope === 'chat' ? ['read:buckets', 'read:files', 'query', 'chat'] :
           scope === 'query' ? ['read:buckets', 'read:files', 'query'] : [scope])

      await onCreate({
        name: name.trim(),
        type: credentialType,
        redirectUri: credentialType === 'oauth' ? redirectUri.trim() : null,
        scopes: scopesArray,
        allowedBuckets: selectedBuckets.length > 0 ? selectedBuckets : null // null = all buckets
      })
      // Reset form
      setName('')
      setCredentialType('api-key')
      setRedirectUri('')
      setScope('delete')
      setSelectedBuckets([])
      onClose() // Close modal on success
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create credential')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="w-full max-w-2xl rounded-2xl backdrop-blur-xl border dark:border-white/10 border-black/10 dark:bg-white/5 bg-white/80 p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold dark:text-dark-text text-light-text">
            Create Credential
          </h3>
          <button
            onClick={onClose}
            className="p-2 rounded-lg dark:hover:bg-white/10 hover:bg-black/10 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name */}
          <Input
            label="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="My API Key / OAuth Client"
            required
          />

          {/* Type Selector */}
          <div>
            <label className="block text-sm font-medium mb-2 dark:text-dark-text text-light-text">
              Credential Type
            </label>
            <select
              value={credentialType}
              onChange={(e) => {
                setCredentialType(e.target.value)
                // Reset scope when switching type - default to full access
                setScope(e.target.value === 'api-key' ? 'delete' : 'chat')
              }}
              className="w-full px-4 py-3 rounded-xl dark:bg-white/5 bg-black/5 border dark:border-white/10 border-black/10 dark:text-dark-text text-light-text focus:outline-none focus:ring-2 dark:focus:ring-dark-accent focus:ring-light-accent"
            >
              <option value="api-key">API Key (for Cursor, Claude Desktop, CLI)</option>
              <option value="oauth">OAuth Client (for ChatGPT, web apps)</option>
            </select>
            <p className="mt-1 text-xs dark:text-dark-text/60 text-light-text/60">
              {credentialType === 'api-key'
                ? 'Direct access with a secret key'
                : 'Standard OAuth2 flow with authorization'}
            </p>
          </div>

          {/* Redirect URI (OAuth only) */}
          {credentialType === 'oauth' && (
            <Input
              label="Redirect URI"
              value={redirectUri}
              onChange={(e) => setRedirectUri(e.target.value)}
              placeholder="https://your-app.com/callback"
              required
            />
          )}

          {/* Permissions */}
          <div>
            <label className="block text-sm font-medium mb-2 dark:text-dark-text text-light-text">
              Permission Level
            </label>
            <select
              value={scope}
              onChange={(e) => setScope(e.target.value)}
              className="w-full px-4 py-3 rounded-xl dark:bg-white/5 bg-black/5 border dark:border-white/10 border-black/10 dark:text-dark-text text-light-text focus:outline-none focus:ring-2 dark:focus:ring-dark-accent focus:ring-light-accent"
            >
              {availableScopes.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>

          {/* Bucket Access */}
          <div className="relative">
            <label className="block text-sm font-medium mb-2 dark:text-dark-text text-light-text">
              Bucket Access
            </label>
            <button
              type="button"
              onClick={() => setShowBucketDropdown(!showBucketDropdown)}
              className="w-full px-4 py-3 rounded-xl dark:bg-white/5 bg-black/5 border dark:border-white/10 border-black/10 dark:text-dark-text text-light-text focus:outline-none focus:ring-2 dark:focus:ring-dark-accent focus:ring-light-accent text-left flex items-center justify-between"
            >
              <span>
                {selectedBuckets.length === 0
                  ? 'All Buckets (Full Access)'
                  : `${selectedBuckets.length} Bucket(s) Selected`}
              </span>
              <svg
                className={`w-4 h-4 transition-transform ${showBucketDropdown ? 'rotate-180' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {showBucketDropdown && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setShowBucketDropdown(false)}
                ></div>
                <div className="absolute z-20 w-full mt-2 rounded-xl dark:bg-black/95 bg-white shadow-xl dark:border-white/10 border-black/10 backdrop-blur-xl max-h-64 overflow-y-auto">
                  <label
                    className="flex items-center gap-2 cursor-pointer dark:hover:bg-white/10 hover:bg-black/5 p-3 transition-colors border-b dark:border-white/10 border-black/10"
                  >
                    <input
                      type="checkbox"
                      checked={selectedBuckets.length === 0}
                      onChange={() => setSelectedBuckets([])}
                      className="w-4 h-4 rounded dark:bg-white/10 bg-black/10 border dark:border-white/20 border-black/20 dark:text-dark-accent text-light-accent focus:ring-2 dark:focus:ring-dark-accent focus:ring-light-accent"
                    />
                    <span className="text-sm font-medium dark:text-dark-accent text-light-accent">
                      All Buckets (Full Access) ✓
                    </span>
                  </label>
                  {buckets && buckets.length > 0 ? (
                    buckets.map((bucket) => (
                      <label
                        key={bucket.id}
                        className="flex items-center gap-2 cursor-pointer dark:hover:bg-white/10 hover:bg-black/5 p-3 transition-colors"
                      >
                        <input
                          type="checkbox"
                          checked={selectedBuckets.includes(bucket.id)}
                          onChange={() => handleBucketToggle(bucket.id)}
                          className="w-4 h-4 rounded dark:bg-white/10 bg-black/10 border dark:border-white/20 border-black/20 dark:text-dark-accent text-light-accent focus:ring-2 dark:focus:ring-dark-accent focus:ring-light-accent"
                        />
                        <span className="text-sm dark:text-dark-text text-light-text">
                          {bucket.name}
                        </span>
                      </label>
                    ))
                  ) : (
                    <div className="p-3 text-sm dark:text-dark-text/60 text-light-text/60">
                      No buckets available
                    </div>
                  )}
                </div>
              </>
            )}

            <p className="mt-1 text-xs dark:text-dark-text/60 text-light-text/60">
              {selectedBuckets.length === 0
                ? 'Full access to all buckets (default). Click to select specific buckets.'
                : `Access restricted to ${selectedBuckets.length} selected bucket(s). Select "All Buckets" for full access.`}
            </p>
          </div>

          {error && (
            <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20">
              <p className="text-sm text-red-400">{error}</p>
            </div>
          )}

          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="secondary"
              onClick={onClose}
              className="flex-1"
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              className="flex-1"
              loading={loading}
            >
              Create {credentialType === 'api-key' ? 'API Key' : 'OAuth Client'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
