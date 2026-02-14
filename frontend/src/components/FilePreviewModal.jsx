import { useState, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { useTheme } from '../context/ThemeContext'
import { filesAPI } from '../services/api'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

function MarkdownContent({ text, isDark }) {
  const isMarkdown = /^#{1,6}\s|^\*\*|^\- |^\d+\.|```|^\|/.test(text || '')

  if (!isMarkdown) {
    return (
      <div className={`whitespace-pre-wrap text-[15px] leading-7 rounded-xl p-6 ${
        isDark ? 'text-dark-text/90 bg-white/[0.03]' : 'text-light-text/90 bg-black/[0.02]'
      }`}>
        {text}
      </div>
    )
  }

  const components = {
    h1: ({ children }) => (
      <div className={`flex items-center gap-3 mt-8 mb-4 pb-3 border-b ${
        isDark ? 'border-white/10' : 'border-black/10'
      }`}>
        <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${
          isDark ? 'bg-dark-accent/20' : 'bg-[#1FE0A5]/15'
        }`}>
          <svg className={`w-4.5 h-4.5 ${isDark ? 'text-dark-accent' : 'text-light-accent'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
          </svg>
        </div>
        <h1 className={`text-2xl font-bold tracking-tight ${isDark ? 'text-white' : 'text-gray-900'}`}>{children}</h1>
      </div>
    ),
    h2: ({ children }) => (
      <div className={`flex items-center gap-2.5 mt-7 mb-3 pb-2 border-b ${
        isDark ? 'border-white/[0.06]' : 'border-black/[0.06]'
      }`}>
        <div className={`flex-shrink-0 w-7 h-7 rounded-md flex items-center justify-center ${
          isDark ? 'bg-blue-500/15' : 'bg-blue-500/10'
        }`}>
          <svg className={`w-4 h-4 ${isDark ? 'text-blue-400' : 'text-blue-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
        <h2 className={`text-xl font-semibold ${isDark ? 'text-white/95' : 'text-gray-800'}`}>{children}</h2>
      </div>
    ),
    h3: ({ children }) => (
      <div className="flex items-center gap-2 mt-5 mb-2">
        <div className={`flex-shrink-0 w-1.5 h-5 rounded-full ${isDark ? 'bg-dark-accent/60' : 'bg-light-accent/60'}`} />
        <h3 className={`text-lg font-semibold ${isDark ? 'text-white/90' : 'text-gray-700'}`}>{children}</h3>
      </div>
    ),
    h4: ({ children }) => (
      <h4 className={`text-base font-semibold mt-4 mb-1.5 ${isDark ? 'text-white/85' : 'text-gray-700'}`}>{children}</h4>
    ),
    p: ({ children }) => (
      <p className={`text-[15px] leading-7 mb-3 ${isDark ? 'text-dark-text/80' : 'text-light-text/80'}`}>{children}</p>
    ),
    ul: ({ children }) => (
      <ul className="space-y-1.5 mb-4 ml-1">{children}</ul>
    ),
    ol: ({ children }) => (
      <ol className="space-y-1.5 mb-4 ml-1 list-none counter-reset-item">{children}</ol>
    ),
    li: ({ children, ordered, index }) => (
      <li className="flex items-start gap-2.5">
        <span className={`flex-shrink-0 mt-[7px] ${ordered
          ? `text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center ${isDark ? 'bg-dark-accent/15 text-dark-accent' : 'bg-light-accent/15 text-light-accent'}`
          : `w-1.5 h-1.5 rounded-full ${isDark ? 'bg-dark-accent/50' : 'bg-light-accent/50'}`
        }`}>
          {ordered ? (index + 1) : ''}
        </span>
        <span className={`text-[15px] leading-7 ${isDark ? 'text-dark-text/80' : 'text-light-text/80'}`}>{children}</span>
      </li>
    ),
    strong: ({ children }) => (
      <strong className={`font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>{children}</strong>
    ),
    em: ({ children }) => (
      <em className={`italic ${isDark ? 'text-dark-accent/80' : 'text-light-accent'}`}>{children}</em>
    ),
    blockquote: ({ children }) => (
      <blockquote className={`border-l-3 pl-4 py-1 my-4 rounded-r-lg ${
        isDark
          ? 'border-dark-accent/40 bg-dark-accent/[0.06]'
          : 'border-light-accent/40 bg-light-accent/[0.04]'
      }`}>
        {children}
      </blockquote>
    ),
    code: ({ inline, children, className }) => {
      if (inline) {
        return (
          <code className={`px-1.5 py-0.5 rounded-md text-sm font-mono ${
            isDark ? 'bg-white/10 text-dark-accent' : 'bg-black/[0.06] text-light-accent'
          }`}>{children}</code>
        )
      }
      return (
        <div className={`relative my-4 rounded-xl overflow-hidden border ${
          isDark ? 'border-white/10 bg-black/40' : 'border-black/10 bg-gray-50'
        }`}>
          {className && (
            <div className={`px-4 py-1.5 text-xs font-mono border-b ${
              isDark ? 'border-white/10 text-white/40 bg-white/[0.03]' : 'border-black/10 text-black/40 bg-black/[0.02]'
            }`}>
              {className.replace('language-', '')}
            </div>
          )}
          <pre className="overflow-x-auto p-4">
            <code className={`text-sm font-mono leading-6 ${isDark ? 'text-green-300' : 'text-gray-800'}`}>{children}</code>
          </pre>
        </div>
      )
    },
    hr: () => (
      <div className="my-6 flex items-center gap-2">
        <div className={`flex-1 h-px ${isDark ? 'bg-white/10' : 'bg-black/10'}`} />
        <div className={`w-1.5 h-1.5 rounded-full ${isDark ? 'bg-dark-accent/30' : 'bg-light-accent/30'}`} />
        <div className={`flex-1 h-px ${isDark ? 'bg-white/10' : 'bg-black/10'}`} />
      </div>
    ),
    a: ({ href, children }) => (
      <a href={href} target="_blank" rel="noopener noreferrer"
        className={`underline decoration-1 underline-offset-2 transition-colors ${
          isDark ? 'text-dark-accent hover:text-dark-accent/80' : 'text-light-accent hover:text-light-accent/80'
        }`}>{children}</a>
    ),
    table: ({ children }) => (
      <div className={`my-4 rounded-xl overflow-hidden border ${isDark ? 'border-white/10' : 'border-black/10'}`}>
        <table className="w-full">{children}</table>
      </div>
    ),
    thead: ({ children }) => (
      <thead className={isDark ? 'bg-white/[0.05]' : 'bg-black/[0.03]'}>{children}</thead>
    ),
    th: ({ children }) => (
      <th className={`px-4 py-2.5 text-left text-sm font-semibold ${isDark ? 'text-white/80' : 'text-gray-700'}`}>{children}</th>
    ),
    td: ({ children }) => (
      <td className={`px-4 py-2.5 text-sm border-t ${
        isDark ? 'text-dark-text/70 border-white/[0.06]' : 'text-light-text/70 border-black/[0.06]'
      }`}>{children}</td>
    ),
    input: ({ checked, type }) => {
      if (type === 'checkbox') {
        return (
          <span className={`inline-flex items-center justify-center w-4.5 h-4.5 rounded mr-2 flex-shrink-0 mt-0.5 ${
            checked
              ? isDark ? 'bg-dark-accent text-black' : 'bg-light-accent text-white'
              : isDark ? 'border border-white/20 bg-white/5' : 'border border-black/20 bg-black/5'
          }`}>
            {checked && (
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
            )}
          </span>
        )
      }
      return null
    },
  }

  return (
    <div className="px-2">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {text}
      </ReactMarkdown>
    </div>
  )
}

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

  const isMarkdownFile = file?.name?.toLowerCase().endsWith('.md')

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
            <div className={`p-2.5 rounded-xl ${
              isDark ? 'bg-dark-accent/15' : 'bg-[#1FE0A5]/15'
            }`}>
              {isMarkdownFile ? (
                <svg className={`w-5 h-5 ${isDark ? 'text-dark-accent' : 'text-light-accent'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                </svg>
              ) : (
                <svg className={`w-5 h-5 ${isDark ? 'text-dark-accent' : 'text-light-accent'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              )}
            </div>
            <div>
              <h2 className={`text-lg font-semibold ${isDark ? 'text-dark-text' : 'text-light-text'}`}>
                {file?.name || 'File Preview'}
              </h2>
              {content && (
                <div className="flex items-center gap-2 mt-0.5">
                  <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full ${
                    isDark ? 'bg-white/[0.06] text-dark-text/50' : 'bg-black/[0.04] text-light-text/50'
                  }`}>
                    {formatSize(content.size_bytes)}
                  </span>
                  <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full ${
                    isDark ? 'bg-white/[0.06] text-dark-text/50' : 'bg-black/[0.04] text-light-text/50'
                  }`}>
                    {content.word_count || 0} words
                  </span>
                  <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full ${
                    isDark ? 'bg-white/[0.06] text-dark-text/50' : 'bg-black/[0.04] text-light-text/50'
                  }`}>
                    {content.chunk_count} chunks
                  </span>
                  {file?.source === 'created' && (
                    <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full ${
                      isDark ? 'bg-dark-accent/15 text-dark-accent/70' : 'bg-light-accent/10 text-light-accent/80'
                    }`}>
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      AI Created
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            className={`p-2 rounded-lg transition-colors ${
              isDark ? 'hover:bg-white/10' : 'hover:bg-black/10'
            }`}
          >
            <svg className={`w-5 h-5 ${isDark ? 'text-dark-text' : 'text-light-text'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Tabs */}
        <div className={`flex gap-1 px-6 pt-4 border-b pb-3 ${isDark ? 'border-white/[0.06]' : 'border-black/[0.06]'}`}>
          <button
            onClick={() => setActiveTab('content')}
            className={`px-4 py-2 text-sm rounded-lg transition-colors flex items-center gap-1.5 ${
              activeTab === 'content'
                ? isDark
                  ? 'bg-dark-accent/20 text-dark-accent'
                  : 'bg-[#1FE0A5]/20 text-light-accent'
                : isDark
                  ? 'hover:bg-white/5 text-dark-text/70'
                  : 'hover:bg-black/5 text-light-text/70'
            }`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Content
          </button>
          <button
            onClick={() => setActiveTab('summary')}
            className={`px-4 py-2 text-sm rounded-lg transition-colors flex items-center gap-1.5 ${
              activeTab === 'summary'
                ? isDark
                  ? 'bg-dark-accent/20 text-dark-accent'
                  : 'bg-[#1FE0A5]/20 text-light-accent'
                : isDark
                  ? 'hover:bg-white/5 text-dark-text/70'
                  : 'hover:bg-black/5 text-light-text/70'
            }`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            AI Summary
          </button>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-16 gap-3">
              <div className={`animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 ${
                isDark ? 'border-dark-accent' : 'border-light-accent'
              }`}></div>
              <span className={`text-sm ${isDark ? 'text-dark-text/40' : 'text-light-text/40'}`}>Loading content...</span>
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <p className="text-red-400">{error}</p>
              <button
                onClick={loadContent}
                className={`mt-4 px-4 py-2 text-sm rounded-lg transition-colors ${
                  isDark ? 'bg-white/10 hover:bg-white/20 text-dark-text' : 'bg-black/10 hover:bg-black/20 text-light-text'
                }`}
              >
                Retry
              </button>
            </div>
          ) : content ? (
            <div>
              {activeTab === 'content' ? (
                <MarkdownContent text={content.content || 'No content available'} isDark={isDark} />
              ) : (
                <MarkdownContent text={content.summary || 'No summary available. Click "Analyze" on the file to generate one.'} isDark={isDark} />
              )}
            </div>
          ) : null}
        </div>
      </div>
    </div>,
    document.body
  )
}
