import { useState, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { useTheme } from '../context/ThemeContext'
import { filesAPI } from '../services/api'

export default function FilePreviewModal({ isOpen, onClose, bucketId, file }) {
  const { isDark } = useTheme()
  const [content, setContent] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('content')

  useEffect(() => {
    if (isOpen && file && bucketId) {
      loadContent()
    }
  }, [isOpen, file, bucketId])

  const loadContent = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await filesAPI.getContent(bucketId, file.id)
      setContent(response.data)
    } catch (err) {
      console.error('Failed to load file content:', err)
      setError('Failed to load file content')
    } finally {
      setLoading(false)
    }
  }

  const formatSize = (bytes) => {
    if (!bytes) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  if (!isOpen) return null

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className={`absolute inset-0 backdrop-blur-sm ${
          isDark ? 'bg-black/60' : 'bg-white/60'
        }`}
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className={`relative w-[90vw] max-w-7xl max-h-[90vh] rounded-2xl backdrop-blur-xl border shadow-2xl flex flex-col ${
        isDark 
          ? 'border-white/10 bg-dark-surface/95' 
          : 'border-[#1FE0A5]/20 bg-[#F6FFFC]'
      }`}>
        {/* Header */}
        <div className={`flex items-center justify-between p-6 border-b ${
          isDark ? 'border-white/10' : 'border-[#1FE0A5]/20'
        }`}>
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${
              isDark ? 'bg-dark-accent/20' : 'bg-[#1FE0A5]/20'
            }`}>
              <svg className={`w-5 h-5 ${isDark ? 'text-dark-accent' : 'text-light-accent'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h2 className="text-lg font-semibold dark:text-dark-text text-light-text">
                {file?.name || 'File Preview'}
              </h2>
              {content && (
                <p className="text-sm dark:text-dark-text/60 text-light-text/60">
                  {formatSize(content.size_bytes)} • {content.word_count || 0} words • {content.chunk_count} chunks
                </p>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            className={`p-2 rounded-lg transition-colors ${
              isDark ? 'hover:bg-white/10' : 'hover:bg-black/10'
            }`}
          >
            <svg className="w-5 h-5 dark:text-dark-text text-light-text" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 px-6 pt-4">
          <button
            onClick={() => setActiveTab('content')}
            className={`px-4 py-2 text-sm rounded-lg transition-colors ${
              activeTab === 'content'
                ? isDark
                  ? 'bg-dark-accent/20 text-dark-accent'
                  : 'bg-[#1FE0A5]/20 text-light-accent'
                : isDark
                  ? 'hover:bg-white/5 text-dark-text/70'
                  : 'hover:bg-black/5 text-light-text/70'
            }`}
          >
            Content
          </button>
          <button
            onClick={() => setActiveTab('summary')}
            className={`px-4 py-2 text-sm rounded-lg transition-colors ${
              activeTab === 'summary'
                ? isDark
                  ? 'bg-dark-accent/20 text-dark-accent'
                  : 'bg-[#1FE0A5]/20 text-light-accent'
                : isDark
                  ? 'hover:bg-white/5 text-dark-text/70'
                  : 'hover:bg-black/5 text-light-text/70'
            }`}
          >
            AI Summary
          </button>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className={`animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 ${
                isDark ? 'border-dark-accent' : 'border-light-accent'
              }`}></div>
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <p className="text-red-400">{error}</p>
              <button
                onClick={loadContent}
                className="mt-4 px-4 py-2 text-sm rounded-lg bg-white/10 hover:bg-white/20 transition-colors dark:text-dark-text text-light-text"
              >
                Retry
              </button>
            </div>
          ) : content ? (
            <div className="prose prose-invert max-w-none">
              {activeTab === 'content' ? (
                <div className={`whitespace-pre-wrap text-base leading-relaxed font-mono rounded-xl p-6 ${
                  isDark 
                    ? 'text-dark-text/90 bg-white/5' 
                    : 'text-light-text/90 bg-black/5'
                }`}>
                  {content.content || 'No content available'}
                </div>
              ) : (
                <div className="whitespace-pre-wrap text-base leading-relaxed dark:text-dark-text/90 text-light-text/90">
                  {content.summary || 'No summary available'}
                </div>
              )}
            </div>
          ) : null}
        </div>
      </div>
    </div>,
    document.body
  )
}
