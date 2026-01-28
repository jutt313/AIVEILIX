import { useState } from 'react'
import Button from './Button'
import Input from './Input'

export default function CreateOAuthClientModal({ isOpen, onClose, onCreate }) {
  const [name, setName] = useState('')
  const [redirectUri, setRedirectUri] = useState('https://chatgpt.com/connector_platform_oauth_redirect')
  const [selectedScopes, setSelectedScopes] = useState(['read:buckets', 'read:files', 'query', 'chat'])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (!isOpen) return null

  const availableScopes = [
    { value: 'read:buckets', label: 'Read Buckets' },
    { value: 'read:files', label: 'Read Files' },
    { value: 'query', label: 'Query Content' },
    { value: 'chat', label: 'Chat with Buckets' },
    { value: 'offline_access', label: 'Offline Access (Refresh Tokens)' }
  ]

  const handleScopeToggle = (scope) => {
    if (selectedScopes.includes(scope)) {
      setSelectedScopes(selectedScopes.filter(s => s !== scope))
    } else {
      setSelectedScopes([...selectedScopes, scope])
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    
    if (!name.trim()) {
      setError('Client name is required')
      return
    }

    if (!redirectUri.trim()) {
      setError('Redirect URI is required')
      return
    }

    // Basic URL validation
    try {
      new URL(redirectUri)
    } catch {
      setError('Invalid redirect URI format')
      return
    }

    if (selectedScopes.length === 0) {
      setError('Please select at least one scope')
      return
    }

    setLoading(true)

    try {
      await onCreate(name, redirectUri, selectedScopes)
      setName('')
      setRedirectUri('https://chatgpt.com/connector_platform_oauth_redirect')
      setSelectedScopes(['read:buckets', 'read:files', 'query', 'chat'])
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to create OAuth client')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="w-full max-w-2xl rounded-3xl backdrop-blur-xl border border-white/10 dark:bg-white/5 bg-black/5 p-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold dark:text-dark-text text-light-text">
            Create OAuth Client
          </h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-white/10 transition-colors dark:text-dark-text/70 text-light-text/70"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <Input
            label="Client Name"
            value={name}
            onChange={(e) => {
              setName(e.target.value)
              setError('')
            }}
            placeholder="My ChatGPT Integration"
            required
          />

          <Input
            label="Redirect URI"
            value={redirectUri}
            onChange={(e) => {
              setRedirectUri(e.target.value)
              setError('')
            }}
            placeholder="https://chatgpt.com/connector_platform_oauth_redirect"
            required
          />
          <p className="mt-1 text-xs dark:text-dark-text/50 text-light-text/50 mb-4">
            For ChatGPT, use: https://chatgpt.com/connector_platform_oauth_redirect
          </p>

          <div className="mb-6">
            <label className="block text-sm font-medium mb-3 dark:text-dark-text text-light-text">
              Scopes
            </label>
            <div className="space-y-2">
              {availableScopes.map((scope) => (
                <label
                  key={scope.value}
                  className="flex items-center gap-3 p-3 rounded-xl bg-white/5 dark:bg-black/10 border border-white/10 cursor-pointer hover:bg-white/10 transition-colors"
                >
                  <input
                    type="checkbox"
                    checked={selectedScopes.includes(scope.value)}
                    onChange={() => handleScopeToggle(scope.value)}
                    className="w-4 h-4 rounded border-white/30 text-dark-accent focus:ring-dark-accent"
                  />
                  <div className="flex-1">
                    <span className="font-medium dark:text-dark-text text-light-text">{scope.label}</span>
                    <span className="ml-2 text-xs dark:text-dark-text/60 text-light-text/60">({scope.value})</span>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div className="flex gap-3 mt-6">
            <Button
              variant="secondary"
              onClick={onClose}
              type="button"
              className="flex-1"
              disabled={loading}
            >
              Cancel
            </Button>
            <Button type="submit" loading={loading} className="flex-1">
              Create OAuth Client
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
