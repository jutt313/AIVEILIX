import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useTheme } from '../context/ThemeContext'

export default function ProfileSettingsGif() {
  const { isDark } = useTheme()
  const [phase, setPhase] = useState(0)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [activeTab, setActiveTab] = useState('profile')
  const [credentialView, setCredentialView] = useState('api-keys')
  const [scrollPosition, setScrollPosition] = useState(0)

  // Form states
  const [name, setName] = useState('')
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [apiKeyName, setApiKeyName] = useState('')
  const [showAPIKeyModal, setShowAPIKeyModal] = useState(false)
  const [showAPIKeyDisplay, setShowAPIKeyDisplay] = useState(false)
  const [createdKey, setCreatedKey] = useState('')

  useEffect(() => {
    const runAnimation = async () => {
      // Wait 1s before starting
      await new Promise(r => setTimeout(r, 1000))

      // Phase 1: Open modal (5s)
      setPhase(1)
      await new Promise(r => setTimeout(r, 1500))
      setIsModalOpen(true)
      await new Promise(r => setTimeout(r, 3500))

      // Phase 2: Show profile form (5s)
      setPhase(2)
      // Type name
      const fullName = 'John Doe'
      for (let i = 0; i <= fullName.length; i++) {
        setName(fullName.slice(0, i))
        await new Promise(r => setTimeout(r, 100))
      }
      await new Promise(r => setTimeout(r, 800))

      // Type current password
      const pwd = '••••••••'
      for (let i = 0; i <= pwd.length; i++) {
        setCurrentPassword(pwd.slice(0, i))
        await new Promise(r => setTimeout(r, 80))
      }
      await new Promise(r => setTimeout(r, 400))

      // Type new password
      for (let i = 0; i <= pwd.length; i++) {
        setNewPassword(pwd.slice(0, i))
        await new Promise(r => setTimeout(r, 80))
      }
      await new Promise(r => setTimeout(r, 400))

      // Type confirm password
      for (let i = 0; i <= pwd.length; i++) {
        setConfirmPassword(pwd.slice(0, i))
        await new Promise(r => setTimeout(r, 80))
      }
      await new Promise(r => setTimeout(r, 500))

      // Phase 3: Scroll to danger zone (5s)
      setPhase(3)
      for (let i = 0; i <= 100; i += 2) {
        setScrollPosition(i)
        await new Promise(r => setTimeout(r, 40))
      }
      await new Promise(r => setTimeout(r, 3000))

      // Phase 4: Switch to Credentials tab (5s)
      setPhase(4)
      setScrollPosition(0)
      await new Promise(r => setTimeout(r, 1000))
      setActiveTab('api-keys')
      await new Promise(r => setTimeout(r, 4000))

      // Phase 5: Create API key (5s)
      setPhase(5)
      await new Promise(r => setTimeout(r, 800))
      setShowAPIKeyModal(true)
      await new Promise(r => setTimeout(r, 1000))

      // Type API key name
      const keyName = 'Cursor Integration'
      for (let i = 0; i <= keyName.length; i++) {
        setApiKeyName(keyName.slice(0, i))
        await new Promise(r => setTimeout(r, 80))
      }
      await new Promise(r => setTimeout(r, 600))

      // Submit and show key
      setShowAPIKeyModal(false)
      await new Promise(r => setTimeout(r, 400))
      setCreatedKey('aiveilix_sk_live_abc123...xyz789')
      setShowAPIKeyDisplay(true)
      await new Promise(r => setTimeout(r, 2000))

      setShowAPIKeyDisplay(false)
      setCreatedKey('')
      await new Promise(r => setTimeout(r, 120))

      // Phase 6: Switch to OAuth view (5s)
      setPhase(6)
      await new Promise(r => setTimeout(r, 1000))
      setCredentialView('oauth')
      await new Promise(r => setTimeout(r, 4000))

      // Phase 7: Switch to Subscription tab (5s)
      setPhase(7)
      await new Promise(r => setTimeout(r, 1000))
      setActiveTab('subscription')
      await new Promise(r => setTimeout(r, 4000))

      // Reset
      setIsModalOpen(false)
      setActiveTab('profile')
      setCredentialView('api-keys')
      setScrollPosition(0)
      setName('')
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
      setApiKeyName('')
      setPhase(0)
    }

    runAnimation()
    const interval = setInterval(runAnimation, 37000) // 35s animation + 2s buffer
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="relative w-full h-[600px] dark:bg-dark-bg bg-light-bg overflow-hidden flex items-center justify-center">
      {/* Profile Modal */}
      <AnimatePresence>
        {isModalOpen && (
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="w-full max-w-[900px] h-[580px] rounded-3xl backdrop-blur-xl dark:border-white/10 border-black/10 dark:bg-white/5 bg-white/80 shadow-xl p-8 overflow-hidden flex flex-col"
          >
              {/* Modal Header */}
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold dark:text-dark-text text-light-text">
                  Profile Settings
                </h2>
                <button className="p-2 rounded-lg dark:hover:bg-white/10 hover:bg-black/10 transition-colors dark:text-dark-text/70 text-light-text/70">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Tabs */}
              <div className="flex gap-2 mb-6 border-b dark:border-white/10 border-black/10">
                <motion.button
                  animate={phase === 4 ? { scale: [1, 1.05, 1] } : {}}
                  onClick={() => setActiveTab('profile')}
                  className={`px-4 py-2 font-medium transition-colors relative ${
                    activeTab === 'profile'
                      ? 'dark:text-dark-accent text-light-accent'
                      : 'dark:text-dark-text/70 text-light-text/70'
                  }`}
                >
                  Profile
                  {activeTab === 'profile' && (
                    <span className="absolute bottom-0 left-0 right-0 h-0.5 dark:bg-dark-accent bg-light-accent"></span>
                  )}
                </motion.button>
                <motion.button
                  animate={phase === 4 ? { scale: [1, 1.05, 1] } : {}}
                  onClick={() => setActiveTab('api-keys')}
                  className={`px-4 py-2 font-medium transition-colors relative ${
                    activeTab === 'api-keys'
                      ? 'dark:text-dark-accent text-light-accent'
                      : 'dark:text-dark-text/70 text-light-text/70'
                  }`}
                >
                  Credentials
                  {activeTab === 'api-keys' && (
                    <span className="absolute bottom-0 left-0 right-0 h-0.5 dark:bg-dark-accent bg-light-accent"></span>
                  )}
                </motion.button>
                <motion.button
                  animate={phase === 7 ? { scale: [1, 1.05, 1] } : {}}
                  onClick={() => setActiveTab('subscription')}
                  className={`px-4 py-2 font-medium transition-colors relative ${
                    activeTab === 'subscription'
                      ? 'dark:text-dark-accent text-light-accent'
                      : 'dark:text-dark-text/70 text-light-text/70'
                  }`}
                >
                  Subscription
                  {activeTab === 'subscription' && (
                    <span className="absolute bottom-0 left-0 right-0 h-0.5 dark:bg-dark-accent bg-light-accent"></span>
                  )}
                </motion.button>
              </div>

              {/* Content Area */}
              <div className="flex-1 overflow-y-auto">
                {/* Profile Tab */}
                {activeTab === 'profile' && (
                  <div
                    className="space-y-6"
                    style={{ transform: `translateY(-${scrollPosition}px)`, transition: 'transform 0.04s linear' }}
                  >
                    {/* Avatar Section */}
                    <div className="flex items-center gap-6">
                      <div className="relative">
                        <div className="w-24 h-24 rounded-full bg-gradient-to-br dark:from-dark-accent from-light-accent to-emerald-400 flex items-center justify-center text-3xl font-bold dark:text-dark-bg text-white">
                          {name?.[0]?.toUpperCase() || 'U'}
                        </div>
                        <button className="absolute bottom-0 right-0 p-2 dark:bg-dark-accent bg-light-accent rounded-full transition-colors">
                          <svg className="w-4 h-4 dark:text-dark-bg text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                          </svg>
                        </button>
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold dark:text-dark-text text-light-text mb-1">Profile Picture</h3>
                        <p className="text-sm dark:text-dark-text/70 text-light-text/70">Click to upload a new avatar</p>
                      </div>
                    </div>

                    {/* Name */}
                    <div>
                      <label className="block text-sm font-medium mb-2 dark:text-dark-text text-light-text">Name</label>
                      <input
                        type="text"
                        value={name}
                        readOnly
                        placeholder="Your full name"
                        className="w-full px-4 py-3 rounded-xl dark:bg-black/10 bg-light-surface/80 dark:border-white/10 border-black/10 border dark:text-dark-text text-light-text"
                      />
                    </div>

                    {/* Email */}
                    <div>
                      <label className="block text-sm font-medium mb-2 dark:text-dark-text text-light-text">Email</label>
                      <input
                        type="email"
                        value="user@aiveilix.com"
                        disabled
                        className="w-full px-4 py-3 rounded-xl dark:bg-black/10 bg-light-surface/80 dark:border-white/5 border-black/10 border dark:text-dark-text/50 text-light-text/50 cursor-not-allowed"
                      />
                      <p className="mt-1 text-xs dark:text-dark-text/50 text-light-text/50">Email cannot be changed</p>
                    </div>

                    {/* Password Change */}
                    <div className="border-t dark:border-white/10 border-black/10 pt-6">
                      <h3 className="text-lg font-semibold dark:text-dark-text text-light-text mb-4">Change Password</h3>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium mb-2 dark:text-dark-text text-light-text">Current Password</label>
                          <input
                            type="password"
                            value={currentPassword}
                            readOnly
                            placeholder="Enter current password"
                            className="w-full px-4 py-3 rounded-xl dark:bg-black/10 bg-light-surface/80 dark:border-white/10 border-black/10 border dark:text-dark-text text-light-text"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2 dark:text-dark-text text-light-text">New Password</label>
                          <input
                            type="password"
                            value={newPassword}
                            readOnly
                            placeholder="Enter new password"
                            className="w-full px-4 py-3 rounded-xl dark:bg-black/10 bg-light-surface/80 dark:border-white/10 border-black/10 border dark:text-dark-text text-light-text"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2 dark:text-dark-text text-light-text">Confirm New Password</label>
                          <input
                            type="password"
                            value={confirmPassword}
                            readOnly
                            placeholder="Confirm new password"
                            className="w-full px-4 py-3 rounded-xl dark:bg-black/10 bg-light-surface/80 dark:border-white/10 border-black/10 border dark:text-dark-text text-light-text"
                          />
                        </div>
                        <button className="px-6 py-3 rounded-xl dark:bg-dark-accent bg-light-accent dark:text-dark-bg text-white font-medium">
                          Change Password
                        </button>
                      </div>
                    </div>

                    {/* Theme Toggle */}
                    <div className="border-t dark:border-white/10 border-black/10 pt-6">
                      <h3 className="text-lg font-semibold dark:text-dark-text text-light-text mb-4">Appearance</h3>
                      <div className="flex items-center justify-between p-4 rounded-xl dark:bg-black/10 bg-light-surface/80 dark:border-white/10 border-black/10 border">
                        <div>
                          <p className="font-medium dark:text-dark-text text-light-text">Theme</p>
                          <p className="text-sm dark:text-dark-text/70 text-light-text/70">{isDark ? 'Dark mode' : 'Light mode'}</p>
                        </div>
                        <button className="px-4 py-2 rounded-lg dark:bg-white/5 bg-black/5 transition-colors dark:text-dark-text text-light-text">
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
                          <button className="px-4 py-2 rounded-xl bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-400">
                            Delete All Buckets
                          </button>
                        </div>
                        <div className="p-4 rounded-xl bg-red-500/5 border border-red-500/20">
                          <p className="font-medium text-red-400 mb-2">Delete Account</p>
                          <p className="text-sm dark:text-dark-text/70 text-light-text/70 mb-4">
                            This will permanently delete your account and all associated data. This action cannot be undone.
                          </p>
                          <button className="px-4 py-2 rounded-xl bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-400">
                            Delete Account
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Credentials Tab */}
                {activeTab === 'api-keys' && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between mb-6">
                      <div>
                        <h3 className="text-lg font-semibold dark:text-dark-text text-light-text">Credentials</h3>
                        <p className="text-sm dark:text-dark-text/70 text-light-text/70">
                          Manage API keys and OAuth clients for external integrations
                        </p>
                      </div>
                      <motion.button
                        animate={phase === 5 ? { scale: [1, 1.05, 1] } : {}}
                        className="px-4 py-2 rounded-xl dark:bg-dark-accent bg-light-accent dark:text-dark-bg text-white font-medium"
                      >
                        Create Credential
                      </motion.button>
                    </div>

                    {/* View Toggle */}
                    <div className="flex gap-2 mb-4 border-b dark:border-white/10 border-black/10">
                      <motion.button
                        animate={phase === 6 ? { scale: [1, 1.05, 1] } : {}}
                        onClick={() => setCredentialView('api-keys')}
                        className={`px-4 py-2 font-medium transition-colors relative ${
                          credentialView === 'api-keys'
                            ? 'dark:text-dark-accent text-light-accent'
                            : 'dark:text-dark-text/70 text-light-text/70'
                        }`}
                      >
                        API Keys
                        {credentialView === 'api-keys' && (
                          <span className="absolute bottom-0 left-0 right-0 h-0.5 dark:bg-dark-accent bg-light-accent"></span>
                        )}
                      </motion.button>
                      <motion.button
                        animate={phase === 6 ? { scale: [1, 1.05, 1] } : {}}
                        onClick={() => setCredentialView('oauth')}
                        className={`px-4 py-2 font-medium transition-colors relative ${
                          credentialView === 'oauth'
                            ? 'dark:text-dark-accent text-light-accent'
                            : 'dark:text-dark-text/70 text-light-text/70'
                        }`}
                      >
                        OAuth Clients
                        {credentialView === 'oauth' && (
                          <span className="absolute bottom-0 left-0 right-0 h-0.5 dark:bg-dark-accent bg-light-accent"></span>
                        )}
                      </motion.button>
                    </div>

                    {/* API Keys View */}
                    {credentialView === 'api-keys' && (
                      <div className="space-y-3">
                        <div className="p-4 rounded-xl dark:bg-black/10 bg-light-surface/80 dark:border-white/10 border-black/10 border">
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-3 mb-2">
                                <h4 className="font-medium dark:text-dark-text text-light-text">My API Key</h4>
                                <span className="px-2 py-0.5 text-xs rounded bg-green-500/20 text-green-400">Active</span>
                              </div>
                              <code className="text-sm dark:text-dark-text/70 text-light-text/70 font-mono block mb-2">
                                aiveilix_sk_live_abc...
                              </code>
                              <div className="flex items-center gap-4 text-xs dark:text-dark-text/60 text-light-text/60">
                                <span>Last used: Jan 15, 2026</span>
                                <span>Requests: 245</span>
                              </div>
                            </div>
                            <button className="px-4 py-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400">
                              Delete
                            </button>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* OAuth Clients View */}
                    {credentialView === 'oauth' && (
                      <div className="space-y-3">
                        <div className="p-4 rounded-xl dark:bg-black/10 bg-light-surface/80 dark:border-white/10 border-black/10 border">
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-3 mb-2">
                                <h4 className="font-medium dark:text-dark-text text-light-text">ChatGPT Integration</h4>
                                <span className="px-2 py-0.5 text-xs rounded bg-green-500/20 text-green-400">Active</span>
                              </div>
                              <code className="text-sm dark:text-dark-text/70 text-light-text/70 font-mono block mb-2">
                                oauth_client_abc123...
                              </code>
                              <div className="flex items-center gap-4 text-xs dark:text-dark-text/60 text-light-text/60 mb-2">
                                <span>Redirect: https://chatgpt.com/oauth</span>
                                <span>Created: Jan 1, 2026</span>
                              </div>
                              <div className="flex flex-wrap gap-2">
                                <span className="px-2 py-0.5 text-xs rounded dark:bg-dark-accent/20 dark:text-dark-accent bg-light-accent/20 text-light-accent">read</span>
                                <span className="px-2 py-0.5 text-xs rounded dark:bg-dark-accent/20 dark:text-dark-accent bg-light-accent/20 text-light-accent">write</span>
                                <span className="px-2 py-0.5 text-xs rounded dark:bg-dark-accent/20 dark:text-dark-accent bg-light-accent/20 text-light-accent">query</span>
                              </div>
                            </div>
                            <button className="px-4 py-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400">
                              Revoke
                            </button>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Subscription Tab */}
                {activeTab === 'subscription' && (
                  <div className="space-y-6">
                    {/* Current Plan Card */}
                    <div className="p-6 rounded-2xl border dark:bg-dark-accent/10 dark:border-dark-accent/30 bg-light-accent/10 border-light-accent/30">
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <p className="text-sm dark:text-dark-text/70 text-light-text/70">Current Plan</p>
                          <h3 className="text-2xl font-bold dark:text-dark-accent text-light-accent">Pro</h3>
                        </div>
                        <span className="px-3 py-1 rounded-full text-sm bg-green-500/20 text-green-400">active</span>
                      </div>
                      <p className="text-sm dark:text-dark-text/70 text-light-text/70 mb-4">
                        Next billing: Feb 15, 2026
                      </p>
                      <div className="flex gap-3">
                        <button className="px-4 py-2 rounded-xl dark:bg-dark-accent bg-light-accent dark:text-dark-bg text-white font-medium">
                          Manage Billing
                        </button>
                        <button className="px-4 py-2 rounded-xl dark:bg-white/5 bg-black/5 dark:border-white/10 border-black/10 border dark:text-dark-text text-light-text font-medium">
                          Change Plan
                        </button>
                      </div>
                    </div>

                    {/* Usage Stats */}
                    <div>
                      <h3 className="text-lg font-semibold dark:text-dark-text text-light-text mb-4">Usage</h3>
                      <div className="space-y-4">
                        {/* Storage */}
                        <div className="p-4 rounded-xl dark:bg-black/10 bg-light-surface/80 dark:border-white/10 border-black/10 border">
                          <div className="flex justify-between mb-2">
                            <span className="dark:text-dark-text text-light-text">Storage</span>
                            <span className="dark:text-dark-text/70 text-light-text/70">2.45 GB / 10.00 GB</span>
                          </div>
                          <div className="h-2 rounded-full dark:bg-white/10 bg-black/10 overflow-hidden">
                            <div className="h-full rounded-full dark:bg-dark-accent bg-light-accent transition-all" style={{ width: '24%' }} />
                          </div>
                        </div>

                        {/* Documents */}
                        <div className="p-4 rounded-xl dark:bg-black/10 bg-light-surface/80 dark:border-white/10 border-black/10 border">
                          <div className="flex justify-between mb-2">
                            <span className="dark:text-dark-text text-light-text">Documents</span>
                            <span className="dark:text-dark-text/70 text-light-text/70">45 / 100</span>
                          </div>
                          <div className="h-2 rounded-full dark:bg-white/10 bg-black/10 overflow-hidden">
                            <div className="h-full rounded-full dark:bg-dark-accent bg-light-accent transition-all" style={{ width: '45%' }} />
                          </div>
                        </div>

                        {/* API Calls */}
                        <div className="p-4 rounded-xl dark:bg-black/10 bg-light-surface/80 dark:border-white/10 border-black/10 border">
                          <div className="flex justify-between mb-2">
                            <span className="dark:text-dark-text text-light-text">API Calls (Today)</span>
                            <span className="dark:text-dark-text/70 text-light-text/70">23 / 1000</span>
                          </div>
                          <div className="h-2 rounded-full dark:bg-white/10 bg-black/10 overflow-hidden">
                            <div className="h-full rounded-full dark:bg-dark-accent bg-light-accent transition-all" style={{ width: '2%' }} />
                          </div>
                        </div>

                        {/* Max File Size */}
                        <div className="p-4 rounded-xl dark:bg-black/10 bg-light-surface/80 dark:border-white/10 border-black/10 border">
                          <div className="flex justify-between">
                            <span className="dark:text-dark-text text-light-text">Max File Size</span>
                            <span className="dark:text-dark-text/70 text-light-text/70">100 MB</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
        )}
      </AnimatePresence>

      {/* Create API Key Modal */}
      <AnimatePresence>
        {showAPIKeyModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 z-[60] flex items-center justify-center p-4 dark:bg-black/70 bg-black/40 backdrop-blur-sm"
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.9 }}
              className="w-full max-w-md rounded-2xl backdrop-blur-xl dark:border-white/10 border-black/10 dark:bg-white/5 bg-white shadow-xl p-6"
            >
              <h3 className="text-xl font-bold dark:text-dark-text text-light-text mb-4">Create API Key</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2 dark:text-dark-text text-light-text">Name</label>
                  <input
                    type="text"
                    value={apiKeyName}
                    readOnly
                    placeholder="e.g., Cursor Integration"
                    className="w-full px-4 py-3 rounded-xl dark:bg-black/10 bg-light-surface/80 dark:border-white/10 border-black/10 border dark:text-dark-text text-light-text"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2 dark:text-dark-text text-light-text">Scopes</label>
                  <div className="space-y-2">
                    <label className="flex items-center gap-2">
                      <input type="checkbox" checked readOnly className="rounded" />
                      <span className="text-sm dark:text-dark-text text-light-text">read</span>
                    </label>
                    <label className="flex items-center gap-2">
                      <input type="checkbox" checked readOnly className="rounded" />
                      <span className="text-sm dark:text-dark-text text-light-text">write</span>
                    </label>
                  </div>
                </div>
                <button className="w-full px-4 py-3 rounded-xl dark:bg-dark-accent bg-light-accent dark:text-dark-bg text-white font-medium">
                  Create
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* API Key Display Modal */}
      <AnimatePresence>
        {showAPIKeyDisplay && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 z-[60] flex items-center justify-center p-4 dark:bg-black/70 bg-black/40 backdrop-blur-sm"
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.9 }}
              className="w-full max-w-2xl rounded-2xl backdrop-blur-xl dark:border-dark-accent/30 border-light-accent/30 dark:bg-white/5 bg-white shadow-xl p-8"
            >
              <h3 className="text-xl font-bold dark:text-dark-accent text-light-accent mb-2">
                API Key Created Successfully
              </h3>
              <p className="text-sm dark:text-dark-text/70 text-light-text/70 mb-4">
                Please copy your API key now. You won't be able to see it again!
              </p>
              <div className="mb-4 p-4 rounded-xl dark:bg-black/10 bg-light-surface/80 dark:border-white/10 border-black/10 border">
                <div className="flex items-center justify-between gap-3">
                  <code className="flex-1 text-sm dark:text-dark-text text-light-text font-mono">
                    {createdKey}
                  </code>
                  <button className="px-4 py-2 rounded-lg dark:bg-dark-accent bg-light-accent dark:text-dark-bg text-white font-medium">
                    Copy
                  </button>
                </div>
              </div>
              <button className="w-full px-4 py-3 rounded-xl dark:bg-dark-accent bg-light-accent dark:text-dark-bg text-white font-medium">
                I've Saved My Key
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
