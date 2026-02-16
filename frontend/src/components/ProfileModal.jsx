import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'
import { authAPI, bucketsAPI, apiKeysAPI, oauthAPI, stripeAPI, teamAPI } from '../services/api'
import Input from './Input'
import Button from './Button'
import CreateAPIKeyModal from './CreateAPIKeyModal'
import CreateOAuthClientModal from './CreateOAuthClientModal'
import CreateCredentialModal from './CreateCredentialModal'
import AddTeamMemberModal from './AddTeamMemberModal'
import TeamMemberBucketPermissions from './TeamMemberBucketPermissions'
import TeamActivityFeed from './TeamActivityFeed'

export default function ProfileModal({ isOpen, onClose }) {
  const { user, logout, isTeamMember } = useAuth()
  const { isDark, toggleTheme } = useTheme()
  const [activeTab, setActiveTab] = useState('profile')
  
  // Profile form state
  const [name, setName] = useState(user?.full_name || '')
  const [email] = useState(user?.email || '')
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [passwordError, setPasswordError] = useState('')
  
  // Danger zone state
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false)
  const [dangerAction, setDangerAction] = useState(null) // 'delete-account' or 'delete-buckets'
  const [confirmPasswordValue, setConfirmPasswordValue] = useState('')
  const [dangerError, setDangerError] = useState('')
  const [dangerLoading, setDangerLoading] = useState(false)
  const [passwordLoading, setPasswordLoading] = useState(false)
  
  // API Keys state
  const [showCreateAPIKeyModal, setShowCreateAPIKeyModal] = useState(false)
  const [showAPIKeyDisplay, setShowAPIKeyDisplay] = useState(false)
  const [newAPIKey, setNewAPIKey] = useState(null)
  const [apiKeys, setAPIKeys] = useState([])
  const [apiKeysLoading, setAPIKeysLoading] = useState(false)
  const [buckets, setBuckets] = useState([])
  
  // OAuth Clients state
  const [showCreateOAuthModal, setShowCreateOAuthModal] = useState(false)
  const [showOAuthDisplay, setShowOAuthDisplay] = useState(false)
  const [newOAuthClient, setNewOAuthClient] = useState(null)
  const [oauthClients, setOAuthClients] = useState([])
  const [oauthClientsLoading, setOAuthClientsLoading] = useState(false)
  
  // Unified credential modal
  const [showCreateCredentialModal, setShowCreateCredentialModal] = useState(false)
  const [credentialView, setCredentialView] = useState('api-keys') // 'api-keys' or 'oauth'

  // Team state
  const [teamMembers, setTeamMembers] = useState([])
  const [teamLoading, setTeamLoading] = useState(false)
  const [showAddMemberModal, setShowAddMemberModal] = useState(false)
  const [expandedMember, setExpandedMember] = useState(null)
  const [showPermissions, setShowPermissions] = useState(null)

  // Subscription state
  const [subscription, setSubscription] = useState(null)
  const [usage, setUsage] = useState(null)
  const [subscriptionLoading, setSubscriptionLoading] = useState(false)
  const [cancelLoading, setCancelLoading] = useState(false)
  const navigate = useNavigate()

  // Load API keys, OAuth clients, and buckets when API Keys tab is active
  useEffect(() => {
    if (isOpen && activeTab === 'api-keys') {
      loadAPIKeys()
      loadOAuthClients()
      loadBuckets()
    }
  }, [isOpen, activeTab])

  // Load team data when team tab is active
  useEffect(() => {
    if (isOpen && activeTab === 'team') {
      loadTeamMembers()
    }
  }, [isOpen, activeTab])

  // Load subscription data when subscription tab is active
  useEffect(() => {
    if (isOpen && activeTab === 'subscription') {
      loadSubscriptionData()
    }
  }, [isOpen, activeTab])

  const loadTeamMembers = async () => {
    setTeamLoading(true)
    try {
      const res = await teamAPI.listMembers()
      setTeamMembers(res.data?.members || res.data || [])
    } catch (err) {
      console.error('Failed to load team:', err)
      setTeamMembers([])
    } finally {
      setTeamLoading(false)
    }
  }

  const handleAddMember = async (name, realEmail, password, color) => {
    await teamAPI.addMember(name, realEmail, password, color)
    loadTeamMembers()
  }

  const handleRemoveMember = async (memberId, memberName) => {
    if (!confirm(`Remove ${memberName} from your team? They will lose access to all buckets.`)) return
    try {
      await teamAPI.removeMember(memberId)
      loadTeamMembers()
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to remove member')
    }
  }

  const handleToggleShowName = async (memberId, currentValue) => {
    try {
      await teamAPI.updateMember(memberId, { show_name: !currentValue })
      loadTeamMembers()
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update')
    }
  }

  const loadSubscriptionData = async () => {
    setSubscriptionLoading(true)
    try {
      const [subRes, usageRes] = await Promise.all([
        stripeAPI.getSubscription(),
        stripeAPI.getUsage()
      ])
      setSubscription(subRes.data)
      setUsage(usageRes.data)
    } catch (error) {
      console.error('Failed to load subscription:', error)
    } finally {
      setSubscriptionLoading(false)
    }
  }

  const handleManageBilling = async () => {
    try {
      const response = await stripeAPI.getPortal()
      window.location.href = response.data.url
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to open billing portal')
    }
  }

  const handleCancelSubscription = async () => {
    if (!confirm('Are you sure you want to cancel your subscription? You will still have access until the end of your billing period.')) {
      return
    }
    setCancelLoading(true)
    try {
      await stripeAPI.cancelSubscription()
      loadSubscriptionData()
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to cancel subscription')
    } finally {
      setCancelLoading(false)
    }
  }

  const handleReactivate = async () => {
    setCancelLoading(true)
    try {
      await stripeAPI.reactivateSubscription()
      loadSubscriptionData()
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to reactivate subscription')
    } finally {
      setCancelLoading(false)
    }
  }

  const loadAPIKeys = async () => {
    try {
      setAPIKeysLoading(true)
      const response = await apiKeysAPI.list()
      setAPIKeys(response.data.keys || [])
    } catch (error) {
      console.error('Failed to load API keys:', error)
      setAPIKeys([])
    } finally {
      setAPIKeysLoading(false)
    }
  }

  const loadBuckets = async () => {
    try {
      const response = await bucketsAPI.list()
      setBuckets(response.data.buckets || [])
    } catch (error) {
      console.error('Failed to load buckets:', error)
      setBuckets([])
    }
  }

  const loadOAuthClients = async () => {
    try {
      setOAuthClientsLoading(true)
      const response = await oauthAPI.list()
      setOAuthClients(response.data || [])
    } catch (error) {
      console.error('Failed to load OAuth clients:', error)
      setOAuthClients([])
    } finally {
      setOAuthClientsLoading(false)
    }
  }

  const handleCreateAPIKey = async (name, scopes, allowedBuckets) => {
    try {
      const response = await apiKeysAPI.create(name, scopes, allowedBuckets)
      if (response.data.success) {
        setNewAPIKey(response.data.api_key)
        setShowCreateAPIKeyModal(false)
        setShowAPIKeyDisplay(true)
        loadAPIKeys() // Refresh list
      }
    } catch (error) {
      throw error
    }
  }

  const handleDeleteAPIKey = async (keyId) => {
    if (!confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
      return
    }
    
    try {
      await apiKeysAPI.delete(keyId)
      loadAPIKeys() // Refresh list
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to delete API key')
    }
  }

  const handleCreateOAuthClient = async (name, redirectUri, scopes) => {
    try {
      const response = await oauthAPI.create(name, redirectUri, scopes)
      if (response.data) {
        setNewOAuthClient({
          client_id: response.data.client_id,
          client_secret: response.data.client_secret
        })
        setShowCreateOAuthModal(false)
        setShowOAuthDisplay(true)
        loadOAuthClients() // Refresh list
      }
    } catch (error) {
      throw error
    }
  }

  const handleDeleteOAuthClient = async (clientId) => {
    if (!confirm('Are you sure you want to revoke this OAuth client? This action cannot be undone.')) {
      return
    }

    try {
      await oauthAPI.delete(clientId)
      loadOAuthClients() // Refresh list
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to revoke OAuth client')
    }
  }

  const handleCreateCredential = async ({ name, type, redirectUri, scopes, allowedBuckets }) => {
    if (type === 'api-key') {
      await handleCreateAPIKey(name, scopes, allowedBuckets)
    } else if (type === 'oauth') {
      await handleCreateOAuthClient(name, redirectUri, scopes)
    }
    setShowCreateCredentialModal(false)
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    alert('API key copied to clipboard!')
  }

  if (!isOpen) return null

  const tabs = [
    { id: 'profile', label: 'Profile' },
    ...(!isTeamMember ? [{ id: 'team', label: 'Team' }] : []),
    { id: 'api-keys', label: 'Credentials' },
    { id: 'subscription', label: 'Subscription' }
  ]

  const handlePasswordChange = async (e) => {
    e.preventDefault()
    setPasswordError('')
    setPasswordLoading(true)
    
    if (newPassword !== confirmPassword) {
      setPasswordError('New passwords do not match')
      setPasswordLoading(false)
      return
    }
    
    if (newPassword.length < 6) {
      setPasswordError('Password must be at least 6 characters')
      setPasswordLoading(false)
      return
    }
    
    try {
      const response = await authAPI.changePassword(currentPassword, newPassword)
      if (response.data.success) {
        setPasswordError('')
        setCurrentPassword('')
        setNewPassword('')
        setConfirmPassword('')
        alert('Password changed successfully')
      } else {
        const msg = response.data.message || 'Failed to change password'
        setPasswordError(msg)
        console.error('[Profile] Change password failed:', msg)
      }
    } catch (error) {
      const msg = error.response?.data?.detail || 'Failed to change password'
      setPasswordError(msg)
      console.error('[Profile] Change password error:', error?.response?.data ?? error?.message ?? error)
    } finally {
      setPasswordLoading(false)
    }
  }

  const handleDangerAction = (action) => {
    setDangerAction(action)
    setShowPasswordConfirm(true)
  }

  const handleDangerConfirm = async () => {
    if (!confirmPasswordValue) {
      setDangerError('Please enter your password to confirm')
      return
    }
    
    setDangerLoading(true)
    setDangerError('')
    
    try {
      if (dangerAction === 'delete-account') {
        const response = await authAPI.deleteAccount(confirmPasswordValue)
        if (response.data.success) {
          await logout()
          navigate('/login')
          return
        } else {
          setDangerError(response.data.message || 'Failed to delete account')
        }
      } else if (dangerAction === 'delete-buckets') {
        const response = await bucketsAPI.deleteAll(confirmPasswordValue)
        if (response.data.success) {
          setShowPasswordConfirm(false)
          setConfirmPasswordValue('')
          setDangerAction(null)
          alert(`Success: ${response.data.message}`)
          window.location.reload() // Reload to refresh bucket list
          return
        } else {
          setDangerError(response.data.message || 'Failed to delete buckets')
        }
      }
    } catch (error) {
      setDangerError(error.response?.data?.detail || 'Operation failed')
    } finally {
      setDangerLoading(false)
    }
  }

  const renderSubscriptionContent = () => {
    if (subscriptionLoading) {
      return (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 dark:border-dark-accent border-light-accent mx-auto"></div>
        </div>
      )
    }

    const planName = subscription?.plan || 'free_trial'
    const planLabels = {
      free_trial: 'Free Trial',
      starter: 'Starter',
      pro: 'Pro',
      premium: 'Premium',
      expired: 'Expired'
    }

    const formatBytes = (bytes) => {
      if (!bytes) return '0 GB'
      const gb = bytes / (1024 * 1024 * 1024)
      return `${gb.toFixed(2)} GB`
    }

    return (
      <div className="space-y-6">
        {/* Current Plan Card */}
        <div className={`p-6 rounded-2xl border ${
          planName === 'expired'
            ? 'bg-red-500/10 border-red-500/30'
            : 'dark:bg-dark-accent/10 dark:border-dark-accent/30 bg-light-accent/10 border-light-accent/30'
        }`}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-sm dark:text-dark-text/70 text-light-text/70">Current Plan</p>
              <h3 className={`text-2xl font-bold ${
                planName === 'expired' ? 'text-red-400' : 'dark:text-dark-accent text-light-accent'
              }`}>
                {planLabels[planName] || planName}
              </h3>
            </div>
            {subscription?.status && (
              <span className={`px-3 py-1 rounded-full text-sm ${
                subscription.status === 'active' ? 'bg-green-500/20 text-green-400' :
                subscription.status === 'trialing' ? 'bg-blue-500/20 text-blue-400' :
                subscription.cancel_at_period_end ? 'bg-yellow-500/20 text-yellow-400' :
                'bg-red-500/20 text-red-400'
              }`}>
                {subscription.cancel_at_period_end ? 'Canceling' : subscription.status}
              </span>
            )}
          </div>

          {subscription?.current_period_end && (
            <p className="text-sm dark:text-dark-text/70 text-light-text/70">
              {subscription.cancel_at_period_end
                ? `Access until: ${new Date(subscription.current_period_end).toLocaleDateString()}`
                : `Next billing: ${new Date(subscription.current_period_end).toLocaleDateString()}`
              }
            </p>
          )}

          <div className="flex gap-3 mt-4">
            {planName !== 'expired' && subscription?.stripe_customer_id && (
              <Button onClick={handleManageBilling} className="!w-auto">
                Manage Billing
              </Button>
            )}
            <Button
              onClick={() => { onClose(); navigate('/pricing') }}
              variant={planName === 'expired' ? 'primary' : 'secondary'}
              className="!w-auto"
            >
              {planName === 'expired' || planName === 'free_trial' ? 'Upgrade Now' : 'Change Plan'}
            </Button>
            {subscription?.status === 'active' && !subscription?.cancel_at_period_end && planName !== 'free_trial' && (
              <Button
                onClick={handleCancelSubscription}
                variant="secondary"
                className="!w-auto !text-red-400 !border-red-500/30 hover:!bg-red-500/10"
                loading={cancelLoading}
              >
                Cancel
              </Button>
            )}
            {subscription?.cancel_at_period_end && (
              <Button
                onClick={handleReactivate}
                variant="secondary"
                className="!w-auto"
                loading={cancelLoading}
              >
                Reactivate
              </Button>
            )}
          </div>
        </div>

        {/* Early Bird Badge */}
        {usage?.early_bird_active && (
          <div className={`p-4 rounded-xl border ${
            isDark ? 'bg-amber-500/10 border-amber-500/30' : 'bg-amber-50 border-amber-200'
          }`}>
            <div className="flex items-center gap-2">
              <span>🎉</span>
              <span className={`font-semibold text-sm ${isDark ? 'text-amber-400' : 'text-amber-600'}`}>
                Early Bird Bonus — 2x All Limits This Month!
              </span>
            </div>
          </div>
        )}

        {/* Usage Stats */}
        {usage && (
          <div>
            <h3 className="text-lg font-semibold dark:text-dark-text text-light-text mb-4">
              Usage
            </h3>
            <div className="space-y-3">
              {/* Usage bar helper */}
              {[
                { label: 'Storage', value: formatBytes(usage.usage?.storage?.used_bytes), limit: formatBytes(usage.usage?.storage?.limit_bytes), pct: usage.usage?.storage?.percentage },
                { label: 'Buckets', value: usage.usage?.buckets?.count, limit: usage.usage?.buckets?.limit === -1 ? '∞' : usage.usage?.buckets?.limit, pct: usage.usage?.buckets?.percentage },
                { label: 'Team Members', value: usage.usage?.team_members?.count, limit: usage.usage?.team_members?.limit === -1 ? '∞' : usage.usage?.team_members?.limit, pct: usage.usage?.team_members?.percentage },
                { label: 'Documents', value: usage.usage?.documents?.count, limit: usage.usage?.documents?.limit === -1 ? '∞' : usage.usage?.documents?.limit, pct: usage.usage?.documents?.percentage },
                { label: 'Chat Messages (Today)', value: usage.usage?.chat_messages?.today, limit: usage.usage?.chat_messages?.limit, pct: usage.usage?.chat_messages?.percentage },
                { label: 'Bucket Chat (Today)', value: usage.usage?.bucket_chat?.today, limit: usage.usage?.bucket_chat?.limit, pct: usage.usage?.bucket_chat?.percentage },
                { label: 'MCP Queries (Today)', value: usage.usage?.mcp_queries?.today, limit: usage.usage?.mcp_queries?.limit, pct: usage.usage?.mcp_queries?.percentage },
                { label: 'API Calls (Today)', value: usage.usage?.api_calls?.today, limit: usage.usage?.api_calls?.limit, pct: usage.usage?.api_calls?.percentage },
              ].map(({ label, value, limit, pct }) => (
                <div key={label} className="p-3 rounded-xl dark:bg-black/10 bg-light-surface/80 dark:border-white/10 border-black/10 border">
                  <div className="flex justify-between mb-1.5">
                    <span className="text-sm dark:text-dark-text text-light-text">{label}</span>
                    <span className="text-sm dark:text-dark-text/70 text-light-text/70">
                      {value ?? 0} / {limit ?? 0}
                    </span>
                  </div>
                  {limit !== '∞' && (
                    <div className="h-1.5 rounded-full dark:bg-white/10 bg-black/10 overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${
                          (pct || 0) >= 90 ? 'bg-red-500' : (pct || 0) >= 70 ? 'bg-amber-500' : 'dark:bg-dark-accent bg-light-accent'
                        }`}
                        style={{ width: `${Math.min(pct || 0, 100)}%` }}
                      />
                    </div>
                  )}
                </div>
              ))}

              {/* Max File Size (non-bar) */}
              <div className="p-3 rounded-xl dark:bg-black/10 bg-light-surface/80 dark:border-white/10 border-black/10 border">
                <div className="flex justify-between">
                  <span className="text-sm dark:text-dark-text text-light-text">Max File Size</span>
                  <span className="text-sm dark:text-dark-text/70 text-light-text/70">
                    {usage.usage?.max_file_size_mb || 0} MB
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    )
  }

  const renderAPIKeysContent = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold dark:text-dark-text text-light-text">
            Credentials
          </h3>
          <p className="text-sm dark:text-dark-text/70 text-light-text/70">
            Manage API keys and OAuth clients for external integrations
          </p>
        </div>
        <Button
          onClick={() => setShowCreateCredentialModal(true)}
          className="!w-auto px-3 py-2 text-sm"
        >
          Create Credential
        </Button>
      </div>

      {/* View Toggle */}
      <div className="flex gap-2 mb-4 border-b dark:border-white/10 border-black/10">
        <button
          onClick={() => setCredentialView('api-keys')}
          className={`px-4 py-2 font-medium transition-colors relative ${
            credentialView === 'api-keys'
              ? 'dark:text-dark-accent text-light-accent'
              : 'dark:text-dark-text/70 text-light-text/70 hover:dark:text-dark-text hover:text-light-text'
          }`}
        >
          API Keys
          {credentialView === 'api-keys' && (
            <span className="absolute bottom-0 left-0 right-0 h-0.5 dark:bg-dark-accent bg-light-accent"></span>
          )}
        </button>
        <button
          onClick={() => setCredentialView('oauth')}
          className={`px-4 py-2 font-medium transition-colors relative ${
            credentialView === 'oauth'
              ? 'dark:text-dark-accent text-light-accent'
              : 'dark:text-dark-text/70 text-light-text/70 hover:dark:text-dark-text hover:text-light-text'
          }`}
        >
          OAuth Clients
          {credentialView === 'oauth' && (
            <span className="absolute bottom-0 left-0 right-0 h-0.5 dark:bg-dark-accent bg-light-accent"></span>
          )}
        </button>
      </div>

      {/* API Keys View */}
      {credentialView === 'api-keys' && (
        <>

      {apiKeysLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 dark:border-dark-accent border-light-accent mx-auto"></div>
        </div>
      ) : apiKeys.length === 0 ? (
        <div className="text-center py-12 dark:text-dark-text/70 text-light-text/70">
          <p className="mb-4">No API keys created yet</p>
          <Button
            onClick={() => setShowCreateAPIKeyModal(true)}
            className="!w-auto"
          >
            Create Your First API Key
          </Button>
        </div>
      ) : (
        <div className="space-y-3">
          {apiKeys.map((key) => (
            <div
              key={key.id}
              className="flex items-center justify-between p-4 rounded-xl dark:bg-black/10 bg-light-surface/80 dark:border-white/10 border-black/10 border"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3 mb-2">
                  <h4 className="font-medium dark:text-dark-text text-light-text">
                    {key.name}
                  </h4>
                  {key.is_active ? (
                    <span className="px-2 py-0.5 text-xs rounded bg-green-500/20 text-green-400">
                      Active
                    </span>
                  ) : (
                    <span className="px-2 py-0.5 text-xs rounded bg-red-500/20 text-red-400">
                      Revoked
                    </span>
                  )}
                </div>
                <code className="text-sm dark:text-dark-text/70 text-light-text/70 font-mono block mb-2">
                  {key.key_prefix}
                </code>
                <div className="flex items-center gap-4 text-xs dark:text-dark-text/60 text-light-text/60">
                  {key.last_used_at && (
                    <span>Last used: {new Date(key.last_used_at).toLocaleDateString()}</span>
                  )}
                  <span>Requests: {key.request_count}</span>
                </div>
              </div>
              <button
                onClick={() => handleDeleteAPIKey(key.id)}
                className="px-4 py-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 transition-colors ml-4"
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
        </>
      )}

      {/* OAuth Clients View */}
      {credentialView === 'oauth' && (
        <>
          {oauthClientsLoading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 dark:border-dark-accent border-light-accent mx-auto"></div>
            </div>
          ) : oauthClients.length === 0 ? (
            <div className="text-center py-12 dark:text-dark-text/70 text-light-text/70">
              <p className="mb-4">No OAuth clients created yet</p>
              <Button
                onClick={() => setShowCreateOAuthModal(true)}
                className="!w-auto"
              >
                Create Your First OAuth Client
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {oauthClients.map((client) => (
                <div
                  key={client.client_id}
                  className="flex items-center justify-between p-4 rounded-xl dark:bg-black/10 bg-light-surface/80 dark:border-white/10 border-black/10 border"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-medium dark:text-dark-text text-light-text">
                        {client.name}
                      </h4>
                      {client.is_active ? (
                        <span className="px-2 py-0.5 text-xs rounded bg-green-500/20 text-green-400">
                          Active
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 text-xs rounded bg-red-500/20 text-red-400">
                          Revoked
                        </span>
                      )}
                    </div>
                    <code className="text-sm dark:text-dark-text/70 text-light-text/70 font-mono block mb-2">
                      {client.client_id.substring(0, 20)}...
                    </code>
                    <div className="flex items-center gap-4 text-xs dark:text-dark-text/60 text-light-text/60">
                      <span>Redirect: {client.redirect_uri}</span>
                      <span>Created: {new Date(client.created_at).toLocaleDateString()}</span>
                    </div>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {client.scopes && client.scopes.map((scope) => (
                        <span key={scope} className="px-2 py-0.5 text-xs rounded dark:bg-dark-accent/20 dark:text-dark-accent bg-light-accent/20 text-light-accent">
                          {scope}
                        </span>
                      ))}
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteOAuthClient(client.client_id)}
                    className="px-4 py-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 transition-colors ml-4"
                  >
                    Revoke
                  </button>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )

  const renderProfileContent = () => (
    <div className="space-y-6">
      {/* Avatar Section */}
      <div className="flex items-center gap-6">
        <div className="relative">
          <div className="w-24 h-24 rounded-full bg-gradient-to-br dark:from-dark-accent from-light-accent to-emerald-400 flex items-center justify-center text-3xl font-bold dark:text-dark-bg text-white">
            {user?.full_name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || 'U'}
          </div>
          <button
            className="absolute bottom-0 right-0 p-2 dark:bg-dark-accent bg-light-accent rounded-full hover:bg-emerald-400 transition-colors"
            title="Change avatar"
          >
            <svg className="w-4 h-4 dark:text-dark-bg text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
        </div>
        <div>
          <h3 className="text-lg font-semibold dark:text-dark-text text-light-text mb-1">
            Profile Picture
          </h3>
          <p className="text-sm dark:text-dark-text/70 text-light-text/70">
            Click to upload a new avatar
          </p>
        </div>
      </div>

      {/* Name */}
      <Input
        label="Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Your full name"
      />

      {/* Email (read-only) */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2 dark:text-dark-text text-light-text">
          Email
        </label>
        <input
          type="email"
          value={email}
          disabled
          className="w-full px-4 py-3 rounded-xl dark:bg-black/10 bg-light-surface/80 dark:border-white/5 border-black/10 border dark:text-dark-text/50 text-light-text/50 cursor-not-allowed"
        />
        <p className="mt-1 text-xs dark:text-dark-text/50 text-light-text/50">
          Email cannot be changed
        </p>
      </div>

      {/* Password Change */}
      <div className="border-t dark:border-white/10 border-black/10 pt-6">
        <h3 className="text-lg font-semibold dark:text-dark-text text-light-text mb-4">
          Change Password
        </h3>
        {passwordError && (
          <div className="mb-4 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm" role="alert">
            {passwordError}
          </div>
        )}
        <form onSubmit={handlePasswordChange}>
          <Input
            label="Current Password"
            type="password"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            placeholder="Enter current password"
            autoComplete="current-password"
          />
          <Input
            label="New Password"
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder="Enter new password"
            error={passwordError}
            autoComplete="new-password"
          />
          <Input
            label="Confirm New Password"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Confirm new password"
            autoComplete="new-password"
          />
          <Button type="submit" className="mt-4" loading={passwordLoading}>
            Change Password
          </Button>
        </form>
      </div>

      {/* Theme Toggle */}
      <div className="border-t dark:border-white/10 border-black/10 pt-6">
        <h3 className="text-lg font-semibold dark:text-dark-text text-light-text mb-4">
          Appearance
        </h3>
        <div className="flex items-center justify-between p-4 rounded-xl dark:bg-black/10 bg-light-surface/80 dark:border-white/10 border-black/10 border">
          <div>
            <p className="font-medium dark:text-dark-text text-light-text">Theme</p>
            <p className="text-sm dark:text-dark-text/70 text-light-text/70">
              {isDark ? 'Dark mode' : 'Light mode'}
            </p>
          </div>
          <button
            onClick={toggleTheme}
            className="px-4 py-2 rounded-lg dark:bg-white/5 bg-black/5 dark:hover:bg-white/20 hover:bg-black/10 transition-colors dark:text-dark-text text-light-text"
          >
            {isDark ? '🌙 Dark' : '☀️ Light'}
          </button>
        </div>
      </div>

      {/* Danger Zone */}
      <div className="border-t border-red-500/20 pt-6">
        <h3 className="text-lg font-semibold text-red-400 mb-4">Danger Zone</h3>
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-red-500/5 border border-red-500/20">
            <p className="font-medium text-red-400 mb-2">Delete All Buckets</p>
            <p className="text-sm dark:text-dark-text/70 text-light-text/70 mb-4">
              This will permanently delete all your buckets and files. This action cannot be undone.
            </p>
            <Button
              variant="secondary"
              onClick={() => handleDangerAction('delete-buckets')}
              className="!bg-red-500/10 hover:!bg-red-500/20 !border-red-500/30 !text-red-400"
            >
              Delete All Buckets
            </Button>
          </div>
          
          <div className="p-4 rounded-xl bg-red-500/5 border border-red-500/20">
            <p className="font-medium text-red-400 mb-2">Delete Account</p>
            <p className="text-sm dark:text-dark-text/70 text-light-text/70 mb-4">
              This will permanently delete your account and all associated data. This action cannot be undone.
            </p>
            <Button
              variant="secondary"
              onClick={() => handleDangerAction('delete-account')}
              className="!bg-red-500/10 hover:!bg-red-500/20 !border-red-500/30 !text-red-400"
            >
              Delete Account
            </Button>
          </div>
        </div>
      </div>
    </div>
  )

  const renderTeamContent = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold dark:text-dark-text text-light-text">Team Members</h3>
          <p className="text-sm dark:text-dark-text/70 text-light-text/70">
            Manage team members and their bucket permissions
          </p>
        </div>
        <Button onClick={() => setShowAddMemberModal(true)} className="!w-auto px-3 py-2 text-sm">
          Add Member
        </Button>
      </div>

      {teamLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 dark:border-dark-accent border-light-accent mx-auto" />
        </div>
      ) : teamMembers.length === 0 ? (
        <div className="text-center py-12 dark:text-dark-text/70 text-light-text/70">
          <p className="mb-4">No team members yet</p>
          <Button onClick={() => setShowAddMemberModal(true)} className="!w-auto">
            Add Your First Team Member
          </Button>
        </div>
      ) : (
        <div className="space-y-3">
          {teamMembers.map((member) => (
            <div key={member.id} className="rounded-xl dark:bg-black/10 bg-light-surface/80 dark:border-white/10 border-black/10 border overflow-hidden">
              <div
                className="flex items-center gap-3 p-4 cursor-pointer"
                onClick={() => setExpandedMember(expandedMember === member.id ? null : member.id)}
              >
                <div
                  className="w-3 h-3 rounded-full flex-shrink-0"
                  style={{ backgroundColor: member.color }}
                />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium dark:text-dark-text text-light-text">{member.name}</span>
                    {!member.is_active && (
                      <span className="px-2 py-0.5 text-xs rounded bg-red-500/20 text-red-400">Removed</span>
                    )}
                  </div>
                  <span className="text-xs dark:text-dark-text/50 text-light-text/50">{member.aiveilix_email}</span>
                </div>
                <svg
                  className={`w-4 h-4 dark:text-dark-text/50 text-light-text/50 transition-transform ${expandedMember === member.id ? 'rotate-180' : ''}`}
                  fill="none" stroke="currentColor" viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>

              {expandedMember === member.id && (
                <div className="px-4 pb-4 space-y-3 border-t dark:border-white/5 border-black/5 pt-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="dark:text-dark-text/70 text-light-text/70">Real email</span>
                    <span className="dark:text-dark-text text-light-text">{member.real_email}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="dark:text-dark-text/70 text-light-text/70">Show name on hover</span>
                    <button
                      onClick={() => handleToggleShowName(member.id, member.show_name)}
                      className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                        member.show_name
                          ? 'dark:bg-dark-accent/30 dark:text-dark-accent bg-light-accent/20 text-light-accent'
                          : 'dark:bg-white/5 dark:text-dark-text/50 bg-black/5 text-light-text/50'
                      }`}
                    >
                      {member.show_name ? 'On' : 'Off'}
                    </button>
                  </div>

                  {showPermissions === member.id ? (
                    <TeamMemberBucketPermissions
                      memberId={member.id}
                      onClose={() => setShowPermissions(null)}
                    />
                  ) : (
                    <Button
                      variant="secondary"
                      onClick={() => setShowPermissions(member.id)}
                      className="!w-full text-sm"
                    >
                      Manage Bucket Permissions
                    </Button>
                  )}

                  {member.is_active && (
                    <button
                      onClick={() => handleRemoveMember(member.id, member.name)}
                      className="w-full px-4 py-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 text-sm transition-colors"
                    >
                      Remove Member
                    </button>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Activity Feed */}
      {teamMembers.length > 0 && (
        <div className="border-t dark:border-white/10 border-black/10 pt-6">
          <h3 className="text-lg font-semibold dark:text-dark-text text-light-text mb-4">
            Recent Activity
          </h3>
          <TeamActivityFeed />
        </div>
      )}
    </div>
  )

  return (
    <>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 dark:bg-black/50 bg-black/30 backdrop-blur-sm">
        <div className="w-[900px] h-[700px] rounded-3xl backdrop-blur-xl dark:border-white/10 border-black/10 dark:bg-white/5 bg-white/80 shadow-xl p-8 overflow-y-auto flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold dark:text-dark-text text-light-text">
              Profile Settings
            </h2>
            <button
              onClick={onClose}
              className="p-2 rounded-lg dark:hover:bg-white/10 hover:bg-black/10 transition-colors dark:text-dark-text/70 text-light-text/70"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-6 border-b dark:border-white/10 border-black/10">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 font-medium transition-colors relative ${
                  activeTab === tab.id
                    ? 'dark:text-dark-accent text-light-accent'
                    : 'dark:text-dark-text/70 text-light-text/70 hover:dark:text-dark-text hover:text-light-text'
                }`}
              >
                {tab.label}
                {activeTab === tab.id && (
                  <span className="absolute bottom-0 left-0 right-0 h-0.5 dark:bg-dark-accent bg-light-accent"></span>
                )}
              </button>
            ))}
          </div>

          {/* Content Area */}
          <div className="flex-1">
            {activeTab === 'profile' && renderProfileContent()}
            {activeTab === 'team' && renderTeamContent()}
            {activeTab === 'api-keys' && renderAPIKeysContent()}
            {activeTab === 'subscription' && renderSubscriptionContent()}
          </div>
        </div>
      </div>

      {/* Unified Create Credential Modal */}
      <CreateCredentialModal
        isOpen={showCreateCredentialModal}
        onClose={() => setShowCreateCredentialModal(false)}
        onCreate={handleCreateCredential}
        buckets={buckets}
      />

      {/* Create API Key Modal (for legacy/fallback) */}
      <CreateAPIKeyModal
        isOpen={showCreateAPIKeyModal}
        onClose={() => setShowCreateAPIKeyModal(false)}
        onCreate={handleCreateAPIKey}
        buckets={buckets}
      />

      {/* Create OAuth Client Modal (for legacy/fallback) */}
      <CreateOAuthClientModal
        isOpen={showCreateOAuthModal}
        onClose={() => setShowCreateOAuthModal(false)}
        onCreate={handleCreateOAuthClient}
      />

      {/* API Key Display Modal (show full key once) */}
      {showAPIKeyDisplay && newAPIKey && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 dark:bg-black/70 bg-black/40 backdrop-blur-sm">
          <div className="w-full max-w-2xl rounded-2xl backdrop-blur-xl dark:border-dark-accent/30 border-light-accent/30 dark:bg-white/5 bg-white shadow-xl p-8">
            <h3 className="text-xl font-bold dark:text-dark-accent text-light-accent mb-2">
              API Key Created Successfully
            </h3>
            <p className="text-sm dark:text-dark-text/70 text-light-text/70 mb-4">
              Please copy your API key now. You won't be able to see it again!
            </p>
            <div className="mb-4 p-4 rounded-xl dark:bg-black/10 bg-light-surface/80 dark:border-white/10 border-black/10 border">
              <div className="flex items-center justify-between gap-3">
                <code className="flex-1 text-sm dark:text-dark-text text-light-text font-mono">
                  {newAPIKey.substring(0, 20)}...{newAPIKey.substring(newAPIKey.length - 10)}
                </code>
                <button
                  onClick={() => copyToClipboard(newAPIKey)}
                  className="px-4 py-2 rounded-lg dark:bg-dark-accent bg-light-accent hover:bg-emerald-400 dark:text-dark-bg text-white font-medium transition-colors whitespace-nowrap"
                >
                  Copy
                </button>
              </div>
            </div>
            <Button
              onClick={() => {
                setShowAPIKeyDisplay(false)
                setNewAPIKey(null)
              }}
            >
              I've Saved My Key
            </Button>
          </div>
        </div>
      )}

      {/* OAuth Client Display Modal (show client_id and secret once) */}
      {showOAuthDisplay && newOAuthClient && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 dark:bg-black/70 bg-black/40 backdrop-blur-sm">
          <div className="w-full max-w-2xl rounded-2xl backdrop-blur-xl dark:border-dark-accent/30 border-light-accent/30 dark:bg-white/5 bg-white shadow-xl p-8">
            <h3 className="text-xl font-bold dark:text-dark-accent text-light-accent mb-2">
              OAuth Client Created Successfully
            </h3>
            <p className="text-sm dark:text-dark-text/70 text-light-text/70 mb-4">
              Please save your Client ID and Client Secret now. The secret won't be shown again!
            </p>

            <div className="mb-4 space-y-3">
              <div className="p-4 rounded-xl dark:bg-black/10 bg-light-surface/80 dark:border-white/10 border-black/10 border">
                <label className="block text-xs font-medium mb-2 dark:text-dark-text/70 text-light-text/70">
                  Client ID
                </label>
                <div className="flex items-center justify-between gap-3">
                  <code className="flex-1 text-sm dark:text-dark-text text-light-text font-mono">
                    {newOAuthClient.client_id.substring(0, 20)}...{newOAuthClient.client_id.substring(newOAuthClient.client_id.length - 10)}
                  </code>
                  <button
                    onClick={() => copyToClipboard(newOAuthClient.client_id)}
                    className="px-4 py-2 rounded-lg dark:bg-dark-accent bg-light-accent hover:bg-emerald-400 dark:text-dark-bg text-white font-medium transition-colors whitespace-nowrap"
                  >
                    Copy
                  </button>
                </div>
              </div>

              <div className="p-4 rounded-xl dark:bg-black/10 bg-light-surface/80 dark:border-white/10 border-black/10 border">
                <label className="block text-xs font-medium mb-2 dark:text-dark-text/70 text-light-text/70">
                  Client Secret
                </label>
                <div className="flex items-center justify-between gap-3">
                  <code className="flex-1 text-sm dark:text-dark-text text-light-text font-mono">
                    {newOAuthClient.client_secret.substring(0, 20)}...{newOAuthClient.client_secret.substring(newOAuthClient.client_secret.length - 10)}
                  </code>
                  <button
                    onClick={() => copyToClipboard(newOAuthClient.client_secret)}
                    className="px-4 py-2 rounded-lg dark:bg-dark-accent bg-light-accent hover:bg-emerald-400 dark:text-dark-bg text-white font-medium transition-colors whitespace-nowrap"
                  >
                    Copy
                  </button>
                </div>
              </div>
            </div>
            
            <Button
              onClick={() => {
                setShowOAuthDisplay(false)
                setNewOAuthClient(null)
              }}
            >
              I've Saved My Credentials
            </Button>
          </div>
        </div>
      )}

      {/* Add Team Member Modal */}
      <AddTeamMemberModal
        isOpen={showAddMemberModal}
        onClose={() => setShowAddMemberModal(false)}
        onCreate={handleAddMember}
      />

      {/* Password Confirmation Modal */}
      {showPasswordConfirm && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 dark:bg-black/70 bg-black/40 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-2xl backdrop-blur-xl border border-red-500/20 dark:bg-white/5 bg-white shadow-xl p-6">
            <h3 className="text-xl font-bold text-red-400 mb-2">
              Confirm {dangerAction === 'delete-account' ? 'Account Deletion' : 'Delete All Buckets'}
            </h3>
            <p className="text-sm dark:text-dark-text/70 text-light-text/70 mb-6">
              This action is irreversible. Please enter your password to confirm.
            </p>
            <Input
              label="Password"
              type="password"
              value={confirmPasswordValue}
              onChange={(e) => {
                setConfirmPasswordValue(e.target.value)
                setDangerError('')
              }}
              placeholder="Enter your password"
              error={dangerError}
            />
            <div className="flex gap-3 mt-6">
              <Button
                variant="secondary"
                onClick={() => {
                  setShowPasswordConfirm(false)
                  setConfirmPasswordValue('')
                  setDangerAction(null)
                  setDangerError('')
                }}
                className="flex-1"
                disabled={dangerLoading}
              >
                Cancel
              </Button>
              <Button
                onClick={handleDangerConfirm}
                className="flex-1 !bg-red-500 hover:!bg-red-600"
                loading={dangerLoading}
              >
                Confirm
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
