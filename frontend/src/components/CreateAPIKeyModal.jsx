import { useState } from 'react'
import { useTheme } from '../context/ThemeContext'
import Button from './Button'
import Input from './Input'

export default function CreateAPIKeyModal({ isOpen, onClose, onCreate, buckets = [] }) {
  const { isDark } = useTheme()
  const [name, setName] = useState('')
  const [accessMode, setAccessMode] = useState('all') // 'all' or 'custom'
  const [selectedBuckets, setSelectedBuckets] = useState([])
  const [showDropdown, setShowDropdown] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (!isOpen) return null

  const handleBucketToggle = (bucketId) => {
    if (bucketId === 'all') {
      setSelectedBuckets([])
      setAccessMode('all')
    } else {
      if (selectedBuckets.includes(bucketId)) {
        const newSelected = selectedBuckets.filter(id => id !== bucketId)
        setSelectedBuckets(newSelected)
        setAccessMode(newSelected.length === 0 ? 'all' : 'custom')
      } else {
        const newSelected = [...selectedBuckets, bucketId]
        setSelectedBuckets(newSelected)
        setAccessMode('custom')
      }
    }
    setShowDropdown(false)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    
    if (!name.trim()) {
      setError('API key name is required')
      return
    }

    if (accessMode === 'custom' && selectedBuckets.length === 0) {
      setError('Please select at least one bucket')
      return
    }

    setLoading(true)

    try {
      // Always use all permissions (read, write, delete)
      const scopesToUse = ['read', 'write', 'delete']
      
      // If all buckets, send null, otherwise send selected bucket IDs
      const bucketsToUse = accessMode === 'all' 
        ? null 
        : selectedBuckets.length > 0 ? selectedBuckets : null

      await onCreate(name, scopesToUse, bucketsToUse)
      setName('')
      setAccessMode('all')
      setSelectedBuckets([])
      setShowDropdown(false)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to create API key')
    } finally {
      setLoading(false)
    }
  }

  const getDisplayText = () => {
    if (accessMode === 'all') {
      return 'All Buckets'
    }
    if (selectedBuckets.length === 0) {
      return 'Select buckets...'
    }
    if (selectedBuckets.length === 1) {
      const bucket = buckets.find(b => b.id === selectedBuckets[0])
      return bucket ? bucket.name : '1 bucket selected'
    }
    return `${selectedBuckets.length} buckets selected`
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="w-full max-w-2xl rounded-3xl backdrop-blur-xl border border-white/10 dark:bg-white/5 bg-black/5 p-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold dark:text-dark-text text-light-text">
            Create API Key
          </h2>
          <button
            onClick={onClose}
            className={`p-2 rounded-lg transition-colors ${
              isDark 
                ? 'hover:bg-white/10 text-dark-text/70' 
                : 'hover:bg-black/10 text-light-text/70'
            }`}
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
            label="API Key Name"
            value={name}
            onChange={(e) => {
              setName(e.target.value)
              setError('')
            }}
            placeholder="My API Key"
            required
          />

          <div className="mb-6">
            <label className="block text-sm font-medium mb-2 dark:text-dark-text text-light-text">
              Access
            </label>
            <div className="relative">
              <button
                type="button"
                onClick={() => setShowDropdown(!showDropdown)}
                className={`w-full px-4 py-3 rounded-xl border text-left flex items-center justify-between transition-colors ${
                  isDark 
                    ? 'bg-black/10 border-white/10 text-dark-text hover:bg-white/10' 
                    : 'bg-white/50 border-[#1FE0A5]/20 text-light-text hover:bg-black/10'
                }`}
              >
                <span>{getDisplayText()}</span>
                <svg 
                  className={`w-5 h-5 transition-transform ${showDropdown ? 'rotate-180' : ''}`}
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {showDropdown && (
                <>
                  <div 
                    className="fixed inset-0 z-10" 
                    onClick={() => setShowDropdown(false)}
                  ></div>
                  <div className={`absolute z-20 w-full mt-2 rounded-xl backdrop-blur-xl border shadow-lg max-h-64 overflow-y-auto ${
                    isDark 
                      ? 'bg-black/95 border-white/10' 
                      : 'bg-[#F6FFFC] border-[#1FE0A5]/20'
                  }`}>
                    {buckets.length > 0 ? (
                      <div className="p-2">
                        <button
                          type="button"
                          onClick={() => handleBucketToggle('all')}
                          className={`w-full px-4 py-2 rounded-lg text-left transition-colors ${
                            accessMode === 'all'
                              ? isDark
                                ? 'bg-dark-accent/20 text-dark-accent'
                                : 'bg-[#1FE0A5]/20 text-light-accent'
                              : isDark
                                ? 'text-dark-text hover:bg-white/10'
                                : 'text-light-text hover:bg-black/10'
                          }`}
                        >
                          <div className="flex items-center gap-3">
                            <div className={`w-4 h-4 rounded border-2 flex items-center justify-center ${
                              accessMode === 'all' 
                                ? isDark
                                  ? 'border-dark-accent bg-dark-accent'
                                  : 'border-light-accent bg-light-accent'
                                : isDark
                                  ? 'border-white/30'
                                  : 'border-[#1FE0A5]/30'
                            }`}>
                              {accessMode === 'all' && (
                                <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                              )}
                            </div>
                            <span className="font-medium">All Buckets</span>
                          </div>
                        </button>
                        {buckets.map((bucket) => (
                          <button
                            key={bucket.id}
                            type="button"
                            onClick={() => handleBucketToggle(bucket.id)}
                            className={`w-full px-4 py-2 rounded-lg text-left transition-colors mt-1 ${
                              selectedBuckets.includes(bucket.id)
                                ? isDark
                                  ? 'bg-dark-accent/20 text-dark-accent'
                                  : 'bg-[#1FE0A5]/20 text-light-accent'
                                : isDark
                                  ? 'text-dark-text hover:bg-white/10'
                                  : 'text-light-text hover:bg-black/10'
                            }`}
                          >
                            <div className="flex items-center gap-3">
                              <div className={`w-4 h-4 rounded border-2 flex items-center justify-center ${
                                selectedBuckets.includes(bucket.id) 
                                  ? isDark
                                    ? 'border-dark-accent bg-dark-accent'
                                    : 'border-light-accent bg-light-accent'
                                  : isDark
                                    ? 'border-white/30'
                                    : 'border-[#1FE0A5]/30'
                              }`}>
                                {selectedBuckets.includes(bucket.id) && (
                                  <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                  </svg>
                                )}
                              </div>
                              <span>{bucket.name}</span>
            </div>
                          </button>
                  ))}
                </div>
                    ) : (
                      <div className="p-4 text-center dark:text-dark-text/60 text-light-text/60 text-sm">
                        No buckets available. Create a bucket first.
              </div>
            )}
                  </div>
                </>
              )}
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
              Create API Key
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
