import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { useTheme } from '../context/ThemeContext'

export default function BucketFullWorkflowGif({ onPhaseChange }) {
  const { isDark } = useTheme()
  const [step, setStep] = useState(0)

  // Bucket & Files State
  const [bucket] = useState({ name: 'Research Papers', description: 'AI and ML research collection' })
  const [files, setFiles] = useState([
    { id: '1', name: 'AI-Research-2024.pdf', size: 2456789, status: 'ready', mime_type: 'application/pdf' },
    { id: '2', name: 'Machine-Learning.docx', size: 876543, status: 'ready', mime_type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' },
    { id: '3', name: 'Neural-Networks.pdf', size: 3456789, status: 'ready', mime_type: 'application/pdf' }
  ])
  const [selectedFiles, setSelectedFiles] = useState([])
  const [showUploadMenu, setShowUploadMenu] = useState(false)
  const [uploading, setUploading] = useState(false)

  // Chat State
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingMessage, setLoadingMessage] = useState('Thinking...')
  const [isTyping, setIsTyping] = useState(false)

  // Conversations State
  const [conversations, setConversations] = useState([])
  const [currentConversationId, setCurrentConversationId] = useState(null)

  const messagesEndRef = useRef(null)

  const formatSize = (bytes) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i)) + ' ' + sizes[i]
  }

  const getConfidenceColor = (confidence, isDark) => {
    switch (confidence) {
      case 'high':
        return isDark ? 'bg-green-500/20 text-green-300' : 'bg-green-500/15 text-green-700'
      case 'medium':
        return isDark ? 'bg-yellow-500/20 text-yellow-300' : 'bg-yellow-500/15 text-yellow-700'
      case 'low':
        return isDark ? 'bg-orange-500/20 text-orange-300' : 'bg-orange-500/15 text-orange-700'
      default:
        return isDark ? 'bg-gray-500/20 text-gray-300' : 'bg-gray-500/15 text-gray-700'
    }
  }

  useEffect(() => {
    const runAnimation = async () => {
      // Reset
      setFiles(files.slice(0, 3))
      setSelectedFiles([])
      setMessages([])
      setInput('')
      setCurrentConversationId(null)
      setConversations([])
      setStep(0)
      if (onPhaseChange) onPhaseChange('')
      await new Promise(r => setTimeout(r, 500))

      // Phase 1: Show bucket with files (5s)
      setStep(1)
      if (onPhaseChange) onPhaseChange('view_bucket')
      await new Promise(r => setTimeout(r, 5000))

      // Phase 2: Upload files (5s)
      setStep(2)
      if (onPhaseChange) onPhaseChange('upload_files')
      setShowUploadMenu(true)
      await new Promise(r => setTimeout(r, 800))
      setShowUploadMenu(false)
      setUploading(true)
      await new Promise(r => setTimeout(r, 1200))
      setUploading(false)
      const newFile = { id: '4', name: 'Data-Science.pdf', size: 1234567, status: 'processing', mime_type: 'application/pdf' }
      setFiles([...files.slice(0, 3), newFile])
      await new Promise(r => setTimeout(r, 1000))
      setFiles([...files.slice(0, 3), { ...newFile, status: 'ready' }])
      await new Promise(r => setTimeout(r, 2000))

      // Phase 3: Select files (5s)
      setStep(3)
      if (onPhaseChange) onPhaseChange('select_files')
      await new Promise(r => setTimeout(r, 1000))
      setSelectedFiles([files[0]])
      await new Promise(r => setTimeout(r, 1500))
      setSelectedFiles([files[0], files[2]])
      await new Promise(r => setTimeout(r, 2500))

      // Phase 4: Chat with Documents (5s)
      setStep(4)
      if (onPhaseChange) onPhaseChange('chat_with_docs')
      await new Promise(r => setTimeout(r, 500))
      const message = 'What are the main topics?'
      for (let i = 0; i <= message.length; i++) {
        setInput(message.slice(0, i))
        await new Promise(r => setTimeout(r, 80))
      }
      await new Promise(r => setTimeout(r, 600))
      const firstConvId = 'conv1'
      setCurrentConversationId(firstConvId)
      setConversations([{ id: firstConvId, title: 'Research Discussion', created_at: new Date(), updated_at: new Date() }])
      const userMsg = {
        role: 'user',
        content: message,
        timestamp: new Date()
      }
      setMessages([userMsg])
      setInput('')
      setSelectedFiles([])
      await new Promise(r => setTimeout(r, 300))
      setLoading(true)
      await new Promise(r => setTimeout(r, 1600))

      // Phase 5: AI Analyzes Files (5s)
      setStep(5)
      if (onPhaseChange) onPhaseChange('ai_analyzes')
      setLoading(false)
      const aiResponse = 'The main topics include Deep Learning, Training Optimization, and AI Ethics.'
      const aiMsg = {
        role: 'assistant',
        content: aiResponse,
        sources: [
          { type: 'document', file_name: 'AI-Research-2024.pdf', confidence: 'high' },
          { type: 'document', file_name: 'Neural-Networks.pdf', confidence: 'high' }
        ],
        timestamp: new Date()
      }
      setMessages([userMsg, aiMsg])
      await new Promise(r => setTimeout(r, 5000))

      // Phase 6: New Conversation (5s)
      setStep(6)
      if (onPhaseChange) onPhaseChange('new_conversation')
      const secondConvId = 'conv2'
      setCurrentConversationId(secondConvId)
      setConversations([
        { id: firstConvId, title: 'Research Discussion', created_at: new Date(Date.now() - 300000), updated_at: new Date(Date.now() - 300000) },
        { id: secondConvId, title: 'Quick Questions', created_at: new Date(), updated_at: new Date() }
      ])
      setMessages([])
      await new Promise(r => setTimeout(r, 5000))

      // Phase 7: Web Search (5s)
      setStep(7)
      if (onPhaseChange) onPhaseChange('web_search')
      await new Promise(r => setTimeout(r, 500))
      const webQuery = 'Latest AI models 2026'
      for (let i = 0; i <= webQuery.length; i++) {
        setInput(webQuery.slice(0, i))
        await new Promise(r => setTimeout(r, 70))
      }
      await new Promise(r => setTimeout(r, 600))
      const webUserMsg = { role: 'user', content: webQuery, timestamp: new Date() }
      setMessages([webUserMsg])
      setInput('')
      await new Promise(r => setTimeout(r, 300))
      setLoading(true)
      setLoadingMessage('Searching web...')
      await new Promise(r => setTimeout(r, 1200))
      setLoading(false)
      const webAiMsg = {
        role: 'assistant',
        content: 'GPT-4o continues as OpenAI\'s flagship model in 2026.',
        sources: [
          { type: 'web_search', url: 'https://openai.com', title: 'OpenAI', domain: 'openai.com' }
        ],
        timestamp: new Date()
      }
      setMessages([webUserMsg, webAiMsg])
      await new Promise(r => setTimeout(r, 1200))
    }

    runAnimation()
    const interval = setInterval(runAnimation, 40000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className={`min-h-screen ${isDark ? 'bg-[#050B0D]' : 'bg-[#E5F2ED]'} p-6`}>
      {/* Main Layout - 3 columns (EXACT copy from Bucket.jsx) */}
      <div className="max-w-[1800px] mx-auto h-[calc(100vh-3rem)] flex gap-4">

        {/* Left Sidebar - ConversationsSidebar EXACT COPY */}
        <div
          className={`h-full rounded-2xl backdrop-blur-xl flex flex-col transition-all duration-300 ${
            isDark ? 'bg-white/5' : 'bg-black/5'
          } w-64`}
        >
          <div className="p-4 flex items-center justify-between">
            <h3 className={`font-semibold ${isDark ? 'text-dark-text' : 'text-[#062A33]'}`}>
              Menu
            </h3>
          </div>

          <div className="px-4 pb-4">
            <button
              className={`flex items-center gap-2 p-2 rounded-lg transition-colors mb-3 w-full ${
                isDark
                  ? 'hover:bg-white/10 text-dark-text/70 hover:text-dark-text'
                  : 'hover:bg-black/10 text-[#062A33]/70 hover:text-[#062A33]'
              }`}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span className="text-sm font-medium">Dashboard</span>
            </button>

            <h2 className={`text-lg font-bold ${isDark ? 'text-dark-text' : 'text-[#062A33]'}`}>
              {bucket.name}
            </h2>
            <p className={`text-xs mt-1 ${isDark ? 'text-dark-text/60' : 'text-[#062A33]/60'}`}>
              {bucket.description}
            </p>
          </div>

          <div className="px-4 pb-4">
            <button
              className={`w-full p-2.5 rounded-lg transition-all flex items-center gap-2 ${
                isDark
                  ? 'hover:bg-white/10 text-dark-text'
                  : 'hover:bg-black/10 text-[#062A33]'
              }`}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              <span className="font-medium">New Chat</span>
            </button>
          </div>

          <div className="flex-1 overflow-y-auto px-3">
            {conversations.length === 0 ? (
              <div className={`text-center py-8 text-sm ${isDark ? 'text-dark-text/50' : 'text-[#062A33]/50'}`}>
                No conversations yet
              </div>
            ) : (
              <div className="space-y-1 py-2">
                {conversations.map((conv) => (
                  <div
                    key={conv.id}
                    className={`group relative p-3 rounded-lg cursor-pointer transition-all ${
                      currentConversationId === conv.id
                        ? isDark
                          ? 'bg-white/10'
                          : 'bg-[#1FE0A5]/10'
                        : isDark
                          ? 'hover:bg-white/5'
                          : 'hover:bg-black/5'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm font-medium truncate ${
                          isDark ? 'text-dark-text' : 'text-[#062A33]'
                        }`}>
                          {conv.title}
                        </p>
                        <p className={`text-xs mt-1 ${
                          isDark ? 'text-dark-text/50' : 'text-[#062A33]/50'
                        }`}>
                          5m ago
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Center - ChatPanel EXACT COPY */}
        <div className="flex-1 flex flex-col">
          <div className="h-full flex flex-col">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto px-6 py-4">
              <div className="max-w-4xl mx-auto space-y-4">
                {messages.length === 0 ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <p className={`${isDark ? 'text-dark-text/70' : 'text-[#062A33]/70'} mb-1`}>
                        Start a conversation
                      </p>
                      <p className={`text-sm ${isDark ? 'text-dark-text/50' : 'text-[#062A33]/50'}`}>
                        Ask questions about your documents
                      </p>
                    </div>
                  </div>
                ) : (
                  messages.map((msg, idx) => (
                    <div
                      key={idx}
                      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[85%] rounded-3xl px-4 py-2 ${
                          msg.role === 'user'
                            ? isDark
                              ? 'bg-[#2DFFB7]/20 text-dark-text border border-[#2DFFB7]'
                              : 'bg-[#1FE0A5]/20 text-[#062A33] border border-[#1FE0A5]'
                            : isDark
                              ? 'text-dark-text'
                              : 'text-[#062A33]'
                        }`}
                      >
                        <div className="whitespace-pre-wrap leading-relaxed space-y-4">
                          {msg.content.split('\n\n').map((paragraph, i) => (
                            <p key={i}>{paragraph}</p>
                          ))}
                          {isTyping && msg.role === 'assistant' && idx === messages.length - 1 && (
                            <span className="inline-block w-2 h-5 ml-1 bg-current animate-pulse" />
                          )}
                        </div>

                        {msg.sources && msg.sources.length > 0 && (
                          <div className={`mt-3 pt-3 border-t ${isDark ? 'border-white/10' : 'border-[#1FE0A5]/20'}`}>
                            <p className="text-xs opacity-50 mb-2">Sources</p>
                            <div className="flex flex-wrap gap-2">
                              {msg.sources.map((source, i) => {
                                if (source.type === 'web_search') {
                                  const domain = source.domain || (source.url ? new URL(source.url).hostname : 'web')
                                  return (
                                    <a
                                      key={i}
                                      href={source.url}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className={`text-xs px-2.5 py-1.5 rounded-lg hover:scale-105 transition-all flex items-center gap-1.5 ${
                                        isDark ? 'bg-blue-500/20 text-blue-300 hover:bg-blue-500/30' : 'bg-blue-500/10 text-blue-600 hover:bg-blue-500/20'
                                      }`}
                                      title={source.title}
                                    >
                                      <img
                                        src={`https://www.google.com/s2/favicons?domain=${domain}&sz=16`}
                                        alt=""
                                        className="w-3.5 h-3.5 rounded-sm"
                                        onError={(e) => { e.target.style.display = 'none' }}
                                      />
                                      <span>{domain.replace('www.', '')}</span>
                                    </a>
                                  )
                                } else {
                                  const confidence = source.confidence || 'medium'
                                  return (
                                    <span
                                      key={i}
                                      className={`text-xs px-2.5 py-1.5 rounded-lg flex items-center gap-1.5 ${
                                        isDark ? 'bg-dark-accent/20 text-dark-accent' : 'bg-[#1FE0A5]/15 text-[#0B3C49]'
                                      }`}
                                      title={source.file_name}
                                    >
                                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                      </svg>
                                      <span>{source.file_name?.length > 20 ? source.file_name.substring(0, 20) + '...' : source.file_name || 'Document'}</span>
                                      {source.confidence && (
                                        <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${getConfidenceColor(confidence, isDark)}`}>
                                          {confidence}
                                        </span>
                                      )}
                                    </span>
                                  )
                                }
                              })}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}
                {loading && !isTyping && (
                  <div className="flex justify-start">
                    <div className="rounded-lg p-4">
                      <div className="flex items-center gap-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-dark-accent"></div>
                        <span className={`text-sm ${isDark ? 'text-dark-text/70' : 'text-[#062A33]/70'}`}>{loadingMessage}</span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </div>

            {/* Input Area */}
            <div className="pt-0 px-[16px] pb-0">
              <div className="max-w-4xl mx-auto">
                {selectedFiles.length > 0 && (
                  <div className="mb-2 flex flex-wrap gap-2">
                    {selectedFiles.map((file) => (
                      <div
                        key={file.id}
                        className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm ${
                          isDark
                            ? 'bg-dark-accent/20 border border-dark-accent/50'
                            : 'bg-[#1FE0A5]/10 border border-[#1FE0A5]'
                        }`}
                      >
                        <span className={isDark ? 'text-dark-accent' : 'text-[#0B3C49]'}>@{file.name}</span>
                      </div>
                    ))}
                  </div>
                )}

                <form onSubmit={(e) => e.preventDefault()}>
                  <div className={`transition-all duration-200 ease-in-out border rounded-3xl flex items-center py-2 ${
                    isDark
                      ? 'bg-white/5 border-white/10'
                      : 'bg-white/50 border-[#1FE0A5]/30'
                  }`}>
                    <div className="relative pl-2 flex-shrink-0">
                      <button
                        type="button"
                        onClick={() => setShowUploadMenu(!showUploadMenu)}
                        className="p-1.5 rounded-full hover:bg-white/10 transition-colors"
                      >
                        {uploading ? (
                          <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-dark-accent"></div>
                        ) : (
                          <svg className={`w-5 h-5 ${isDark ? 'text-dark-text/70' : 'text-[#062A33]/70'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                          </svg>
                        )}
                      </button>
                      {showUploadMenu && !uploading && (
                        <div className={`absolute bottom-full left-0 mb-2 w-48 rounded-lg backdrop-blur-xl border shadow-lg py-2 z-50 ${
                          isDark ? 'bg-black/20 border-white/10' : 'bg-white/90 border-[#1FE0A5]/20'
                        }`}>
                          <button type="button" className={`w-full px-4 py-2 text-left text-sm transition-colors flex items-center gap-2 ${
                            isDark ? 'text-dark-text hover:bg-white/10' : 'text-[#062A33] hover:bg-black/10'
                          }`}>
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                            Upload File
                          </button>
                          <button type="button" className={`w-full px-4 py-2 text-left text-sm transition-colors flex items-center gap-2 ${
                            isDark ? 'text-dark-text hover:bg-white/10' : 'text-[#062A33] hover:bg-black/10'
                          }`}>
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" /></svg>
                            Upload Folder
                          </button>
                        </div>
                      )}
                    </div>

                    <textarea
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      placeholder="Ask about your documents..."
                      className={`flex-1 min-w-0 bg-transparent focus:outline-none resize-none overflow-y-auto text-[16px] leading-6 px-3 ${
                        isDark
                          ? 'text-dark-text placeholder:text-dark-text/50'
                          : 'text-[#062A33] placeholder:text-[#062A33]/50'
                      }`}
                      style={{
                        height: '24px',
                        maxHeight: '144px',
                      }}
                    />

                    <button
                      type="submit"
                      disabled={!input.trim() && selectedFiles.length === 0}
                      className={`flex-shrink-0 w-8 h-8 mr-2 rounded-full text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center bg-dark-accent hover:bg-dark-accent/90`}
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" /></svg>
                    </button>
                  </div>
                </form>

                <p className={`text-center text-[10px] py-[3px] ${isDark ? 'text-white/30' : 'text-[#062A33]/30'}`}>
                  AIveilix can make mistakes. Check important info.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Sidebar - FilesCard EXACT COPY */}
        <div className={`w-80 rounded-2xl backdrop-blur-xl flex flex-col overflow-hidden ${
          isDark ? 'bg-white/5' : 'bg-black/5'
        }`}>
          <div className="p-4 flex items-center justify-between">
            <h3 className={`font-semibold ${isDark ? 'text-dark-text' : 'text-[#062A33]'}`}>Files & Folders</h3>
            <button
              className={`p-1.5 rounded transition-colors ml-auto ${isDark ? 'hover:bg-white/10' : 'hover:bg-black/10'}`}
              title="Collapse"
            >
              <svg
                className={`w-5 h-5 ${isDark ? 'text-dark-text/70' : 'text-[#062A33]/70'}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          <div className="flex-1 overflow-y-auto px-3">
            {files.length === 0 ? (
              <div className={`text-center py-12 text-sm ${isDark ? 'text-dark-text/50' : 'text-[#062A33]/50'}`}>
                No files yet
              </div>
            ) : (
              <div className="space-y-1">
                {files.map((file) => {
                  const isSelected = selectedFiles.some(f => f.id === file.id)
                  return (
                    <motion.div
                      key={file.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`p-3 rounded-lg cursor-pointer transition-all ${
                        isSelected
                          ? isDark
                            ? 'bg-dark-accent/20 border border-dark-accent/50'
                            : 'bg-[#1FE0A5]/20 border border-[#1FE0A5]/50'
                          : isDark
                            ? 'hover:bg-white/5'
                            : 'hover:bg-black/5'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <svg className={`w-5 h-5 flex-shrink-0 mt-0.5 ${
                          isDark ? 'text-dark-accent' : 'text-[#1FE0A5]'
                        }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <div className="flex-1 min-w-0">
                          <p className={`text-sm font-medium truncate ${
                            isDark ? 'text-dark-text' : 'text-[#062A33]'
                          }`}>{file.name}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <span className={`text-xs ${
                              isDark ? 'text-dark-text/50' : 'text-[#062A33]/50'
                            }`}>{formatSize(file.size)}</span>
                            {file.status === 'ready' && (
                              <span className="text-xs text-green-400 flex items-center gap-1">
                                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                </svg>
                              </span>
                            )}
                            {file.status === 'processing' && (
                              <span className="text-xs text-yellow-400 flex items-center gap-1">
                                <div className="animate-spin rounded-full h-3 w-3 border-t border-b border-yellow-400"></div>
                              </span>
                            )}
                          </div>
                        </div>
                        {isSelected && (
                          <svg className={`w-5 h-5 flex-shrink-0 ${
                            isDark ? 'text-dark-accent' : 'text-[#1FE0A5]'
                          }`} fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                        )}
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
