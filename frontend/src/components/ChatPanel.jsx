import { useState, useEffect, useRef, useLayoutEffect } from 'react'
import { chatAPI, filesAPI } from '../services/api'
import { useTheme } from '../context/ThemeContext'
import UpgradeModal from './UpgradeModal'

export default function ChatPanel({
  bucketId,
  conversationId: externalConversationId,
  onConversationCreated,
  onFilesUpdate,
  files = [],
  selectedFiles = [],
  onSelectedFilesChange
}) {
  const { isDark } = useTheme()
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingMessage, setLoadingMessage] = useState('Thinking...')
  const [conversationId, setConversationId] = useState(externalConversationId)
  const [showUploadMenu, setShowUploadMenu] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [currentPhase, setCurrentPhase] = useState('idle') // idle, thinking, response
  const [thinkingContent, setThinkingContent] = useState('')
  const [expandedThinking, setExpandedThinking] = useState({}) // per message: { [msgIdx]: true/false }
  const [isTyping, setIsTyping] = useState(false) // Show typing cursor
  const [showUpgradeModal, setShowUpgradeModal] = useState(false)
  const [upgradeError, setUpgradeError] = useState(null)
  const [createFileMode, setCreateFileMode] = useState(false)
  const [createFileName, setCreateFileName] = useState('')
  const [createFileError, setCreateFileError] = useState('')
  const [createFileSaving, setCreateFileSaving] = useState(false)
  const [createFileDraftReady, setCreateFileDraftReady] = useState(false)
  const [lastCreatedFileName, setLastCreatedFileName] = useState('')
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)
  const uploadMenuRef = useRef(null)
  const fileInputRef = useRef(null)
  const folderInputRef = useRef(null)
  const isCreatingConversation = useRef(false)
  const abortControllerRef = useRef(null)

  // Toggle thinking expansion for a specific message
  const toggleThinking = (msgIdx) => {
    setExpandedThinking(prev => ({
      ...prev,
      [msgIdx]: !prev[msgIdx]
    }))
  }

  // Get confidence badge color
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

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Cleanup: abort any pending request on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [])

  // Update conversation ID when external prop changes
  useEffect(() => {
    // Skip if we're just creating a new conversation internally
    if (isCreatingConversation.current) {
      isCreatingConversation.current = false
      return
    }

    // Only reload if switching to a DIFFERENT conversation (not just setting ID on new chat)
    if (externalConversationId && externalConversationId !== conversationId) {
      setConversationId(externalConversationId)
      loadConversationMessages(externalConversationId)
    } else if (!externalConversationId && conversationId) {
      // New chat selected - clear everything
      setConversationId(null)
      setMessages([])
      setCreateFileMode(false)
      setCreateFileName('')
      setCreateFileError('')
      setCreateFileDraftReady(false)
    }
  }, [externalConversationId])

  const loadConversationMessages = async (convId) => {
    try {
      const messagesRes = await chatAPI.getMessages(convId)
      const loadedMessages = messagesRes.data?.messages || []

      // Convert to UI format
      const formattedMessages = loadedMessages.map(msg => ({
        role: msg.role,
        content: msg.content,
        sources: msg.sources || [],
        timestamp: new Date(msg.created_at),
        sent_by_color: msg.sent_by_color || null,
        sent_by_name: msg.sent_by_name || null,
      }))

      setMessages(formattedMessages)
    } catch (error) {
      console.error('Failed to load conversation messages:', error)
      setMessages([])
    }
  }

  useLayoutEffect(() => {
    // Auto-resize textarea - grows upward smoothly
    if (textareaRef.current) {
      // Reset to single line height first
      textareaRef.current.style.height = '24px'
      // Calculate needed height (max 6 lines = ~144px)
      const scrollHeight = textareaRef.current.scrollHeight
      const newHeight = Math.min(scrollHeight, 144)
      textareaRef.current.style.height = newHeight + 'px'
    }
  }, [input])

  // Close upload menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (uploadMenuRef.current && !uploadMenuRef.current.contains(event.target)) {
        setShowUploadMenu(false)
      }
    }

    if (showUploadMenu) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showUploadMenu])

  const handleFileUpload = async (files) => {
    if (!files || files.length === 0) return

    const allFiles = Array.from(files)
    const batchMeta = {
      count: allFiles.length,
      totalBytes: allFiles.reduce((sum, f) => sum + (f.size || 0), 0),
    }

    setUploading(true)
    setShowUploadMenu(false)
    let successCount = 0
    let errorCount = 0
    let limitError = null

    for (const file of allFiles) {
      try {
        let folderPath = null
        if (file.webkitRelativePath) {
          const pathParts = file.webkitRelativePath.split('/')
          if (pathParts.length > 1) {
            folderPath = pathParts.slice(0, -1).join('/')
          }
        }
        await filesAPI.upload(bucketId, file, folderPath, batchMeta)
        successCount++
      } catch (error) {
        console.error(`Upload failed for ${file.name}:`, error)
        if (error.response?.status === 402 || error.response?.status === 429) {
          limitError = error.response.data?.detail || { error: 'limit_exceeded', message: 'Plan limit reached' }
          break
        }
        errorCount++
      }
    }

    if (onFilesUpdate) onFilesUpdate()

    if (limitError) {
      setUpgradeError(limitError)
      setShowUpgradeModal(true)
    } else if (errorCount > 0) {
      alert(`Upload complete: ${successCount} successful, ${errorCount} failed`)
    }

    setUploading(false)
  }

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileUpload(e.target.files)
    }
    // Reset input so same file can be selected again
    e.target.value = ''
  }

  const handleUploadClick = (e) => {
    e.preventDefault()
    setShowUploadMenu(!showUploadMenu)
  }

  const handleUploadFileClick = () => {
    fileInputRef.current?.click()
  }

  const handleUploadFolderClick = () => {
    folderInputRef.current?.click()
  }

  const handleCreateDocClick = () => {
    setShowUploadMenu(false)
    setCreateFileMode(true)
    setCreateFileError('')
    setCreateFileDraftReady(false)
  }

  const removeSelectedFile = (fileId) => {
    if (onSelectedFilesChange) {
      onSelectedFilesChange(selectedFiles.filter(f => f.id !== fileId))
    }
  }

  const detectCreateIntent = (text) => {
    const trimmed = (text || '').trim()
    if (!trimmed) return null
    const lower = trimmed.toLowerCase()
    if (lower.includes('/createfile')) {
      return { mode: 'create', name: '' }
    }
    const nameMatch = trimmed.match(/([A-Za-z0-9_.-]+\.(md|txt))/i)
    const createMatch = /(create|make|generate|write|save)\s+(a\s+)?(file|doc|document|note|summary)/i.test(trimmed)
    const updateMatch = /(update|edit|revise|rewrite|improve|refine)\s+(the\s+)?(file|doc|document|note|summary)/i.test(trimmed)
    if (nameMatch || createMatch || updateMatch) {
      return {
        mode: updateMatch ? 'update' : 'create',
        name: nameMatch ? nameMatch[1] : ''
      }
    }
    return null
  }

  const requestFileDraft = async (prompt, intent, conversationIdForDraft) => {
    setLoading(true)
    setLoadingMessage('Creating file...')
    setCreateFileMode(true)
    setCreateFileDraftReady(false)
    setCreateFileError('')

    try {
      const response = await chatAPI.sendMessage(
        bucketId,
        prompt,
        conversationIdForDraft,
        null,
        null,
        {
          mode: intent.mode === 'update' ? 'file_update' : 'file_draft',
          file_name_hint: intent.name || (intent.mode === 'update' ? lastCreatedFileName : '')
        }
      )
      const data = response.data

      if (data.conversation_id && data.conversation_id !== conversationIdForDraft) {
        isCreatingConversation.current = true
        setConversationId(data.conversation_id)
        if (onConversationCreated) {
          onConversationCreated(data.conversation_id)
        }
      }

      if (data.file_draft && data.file_draft.file_name && data.file_draft.file_content) {
        // Auto-create file directly (no draft review)
        const fileName = data.file_draft.file_name
        const fileContent = data.file_draft.file_content

        try {
          const existing = files.find(f => f.name === fileName && f.source === 'created')
          if (existing) {
            await filesAPI.updateContent(bucketId, existing.id, fileContent)
          } else {
            await filesAPI.create(bucketId, fileName, fileContent)
          }

          if (onFilesUpdate) await onFilesUpdate()

          setMessages(prev => [...prev, {
            role: 'assistant',
            content: data.message || (existing ? `Updated file: ${fileName}` : `Created file: ${fileName}`),
            sources: data.sources,
            timestamp: new Date()
          }])

          setLastCreatedFileName(fileName)
          setCreateFileMode(false)
          setCreateFileName('')
          setCreateFileDraftReady(false)
          setInput('')
        } catch (createError) {
          console.error('Auto-create file failed:', createError)
          // Fallback: show draft for manual review
          setCreateFileName(fileName)
          setInput(fileContent)
          setCreateFileDraftReady(true)
          setCreateFileError(createError.response?.data?.detail || 'Auto-create failed. Review and try again.')

          setMessages(prev => [...prev, {
            role: 'assistant',
            content: data.message || 'File drafted. Review and press Create.',
            sources: data.sources,
            timestamp: new Date()
          }])
        }
      } else {
        setCreateFileError('AI failed to generate file. Try again with a clearer description.')
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.message || 'Could not generate file.',
          sources: data.sources,
          timestamp: new Date()
        }])
      }
    } catch (error) {
      console.error('File creation error:', error)
      setCreateFileError(error.response?.data?.detail || error.message || 'Failed to create file')
    } finally {
      setLoading(false)
      setCurrentPhase('idle')
      setThinkingContent('')
      setIsTyping(false)
    }
  }

  const handleCreateFile = async () => {
    if (createFileSaving) return
    const name = createFileName.trim()
    const content = input.trim()

    if (!name) {
      setCreateFileError('Filename is required (e.g., notes.md)')
      return
    }
    if (!name.toLowerCase().endsWith('.md') && !name.toLowerCase().endsWith('.txt')) {
      setCreateFileError('Only .md and .txt files are supported')
      return
    }
    if (!content) {
      setCreateFileError('File content is required')
      return
    }

    setCreateFileError('')
    setCreateFileSaving(true)

    try {
      const existing = files.find(f => f.name === name && f.source === 'created')
      if (existing) {
        await filesAPI.updateContent(bucketId, existing.id, content)
      } else {
        await filesAPI.create(bucketId, name, content)
      }

      if (onFilesUpdate) {
        await onFilesUpdate()
      }

      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: existing ? `Updated file: ${name}` : `Created file: ${name}`,
          timestamp: new Date()
        }
      ])

      setInput('')
      setCreateFileName('')
      setCreateFileMode(false)
      setCreateFileDraftReady(false)
      setLastCreatedFileName(name)
    } catch (error) {
      console.error('Create file failed:', error)
      setCreateFileError(error.response?.data?.detail || error.message || 'Failed to create file')
    } finally {
      setCreateFileSaving(false)
    }
  }

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
      setLoading(false)
      setCurrentPhase('idle')
      setThinkingContent('')
      setIsTyping(false)

      // Remove the user message since we're canceling
      setMessages(prev => prev.slice(0, -1))
    }
  }

  const handleSend = async (e) => {
    e.preventDefault()
    if (loading) return

    if (createFileMode && createFileDraftReady) {
      await handleCreateFile()
      return
    }

    if ((!input.trim() && selectedFiles.length === 0)) return

    // Build message with file references
    let userMessage = input.trim()
    if (selectedFiles.length > 0) {
      const fileRefs = selectedFiles.map(f => `@${f.name}`).join(' ')
      userMessage = fileRefs + (userMessage ? ` ${userMessage}` : '')
    }

    if (createFileMode && !createFileDraftReady) {
      const prompt = userMessage
      const newUserMessage = {
        role: 'user',
        content: prompt,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, newUserMessage])

      setInput('')
      if (onSelectedFilesChange) {
        onSelectedFilesChange([])
      }
      if (textareaRef.current) {
        textareaRef.current.style.height = '24px'
      }

      await requestFileDraft(prompt, { mode: 'create', name: '' }, conversationId)
      return
    }

    // Auto-detect create/update intent when mode is not active
    const createIntent = detectCreateIntent(userMessage)
    if (createIntent) {
      if (createIntent.mode === 'update' && !createIntent.name && !lastCreatedFileName) {
        setCreateFileMode(true)
        setCreateFileError('No created file to update yet.')
        return
      }
      const cleaned = userMessage.replace('/createfile', '').trim()
      const prompt = cleaned || userMessage
      if (!prompt.trim()) {
        setCreateFileMode(true)
        setCreateFileError('Describe the file you want to create.')
        return
      }

      const newUserMessage = {
        role: 'user',
        content: prompt,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, newUserMessage])

      setInput('')
      if (onSelectedFilesChange) {
        onSelectedFilesChange([])
      }
      if (textareaRef.current) {
        textareaRef.current.style.height = '24px'
      }

      await requestFileDraft(prompt, createIntent, conversationId)
      return
    }
    setInput('')
    // Clear selected files after sending
    if (onSelectedFilesChange) {
      onSelectedFilesChange([])
    }
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = '24px'
    }

    const newUserMessage = {
      role: 'user',
      content: userMessage,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, newUserMessage])
    setLoading(true)

    // Determine loading message based on query
    const queryLower = userMessage.toLowerCase()
    const searchKeywords = ['search', 'look up', 'find', 'what is', 'who is', 'how to', 'current', 'latest', 'today', 'recent', 'news', 'weather', 'price', 'now', 'stock']
    const isSearchQuery = searchKeywords.some(keyword => queryLower.includes(keyword))

    if (isSearchQuery) {
      // Extract topic - skip stop words and common question words
      const stopWords = ['the', 'a', 'an', 'is', 'are', 'was', 'were', 'what', 'who', 'where', 'when', 'why', 'how', 'to', 'search', 'find', 'look', 'up', 'tell', 'me', 'please', 'can', 'you', 'could', 'would', 'in', 'on', 'at', 'for', 'of', 'about', 'now']
      const words = userMessage.split(' ').filter(w => {
        const lower = w.toLowerCase()
        return !stopWords.includes(lower) && w.length > 2
      })
      const topic = words.slice(0, 4).join(' ')
      setLoadingMessage(`Searching ${topic || 'web'}...`)
    } else {
      setLoadingMessage('Thinking...')
    }

    // Create AbortController for this request
    abortControllerRef.current = new AbortController()

    // Add empty assistant message that will be updated as chunks arrive
    const assistantMsgIndex = messages.length + 1 // After user message
    setMessages(prev => [...prev, {
      role: 'assistant',
      content: '',
      sources: [],
      thinking: '',
      timestamp: new Date()
    }])

    let accumulatedText = ''
    let accumulatedThinking = ''

    // Reset phase state
    setCurrentPhase('idle')
    setThinkingContent('')

    try {
      const response = await chatAPI.sendMessage(
        bucketId,
        userMessage,
        conversationId,
        abortControllerRef.current.signal,
        (chunk) => {
          // Handle different event types
          if (typeof chunk === 'object') {
            switch (chunk.type) {
              case 'searching':
                setLoadingMessage(`Searching ${chunk.keywords}...`)
                break

              case 'phase_change':
                setCurrentPhase(chunk.phase)
                if (chunk.phase === 'thinking') {
                  setLoadingMessage('Reasoning...')
                  setIsTyping(false)
                } else if (chunk.phase === 'response') {
                  setLoadingMessage('')
                  setIsTyping(true) // Start showing typing cursor
                }
                break

              case 'thinking':
                accumulatedThinking += chunk.content
                setThinkingContent(accumulatedThinking)
                // Update message thinking content live
                setMessages(prev => {
                  const newMessages = [...prev]
                  if (newMessages[assistantMsgIndex]) {
                    newMessages[assistantMsgIndex].thinking = accumulatedThinking
                  }
                  return newMessages
                })
                break

              case 'response':
                accumulatedText += chunk.content
                // Update message content as chunks arrive
                setMessages(prev => {
                  const newMessages = [...prev]
                  if (newMessages[assistantMsgIndex]) {
                    newMessages[assistantMsgIndex].content = accumulatedText
                  }
                  return newMessages
                })
                break

              case 'done':
                // Stop typing cursor
                setIsTyping(false)
                break

              default:
                // Unknown event type, ignore
                break
            }
          }
        }
      )
      const data = response.data

      // Update final message with parsed content, sources, and thinking
      setMessages(prev => {
        const newMessages = [...prev]
        if (newMessages[assistantMsgIndex]) {
          newMessages[assistantMsgIndex].content = data.message
          newMessages[assistantMsgIndex].sources = data.sources
          newMessages[assistantMsgIndex].thinking = data.thinking || accumulatedThinking
        }
        return newMessages
      })

      // Reset phase
      setCurrentPhase('idle')

      console.log('📦 Assistant message sources:', data.sources)
      console.log('💭 Thinking content:', data.thinking?.slice(0, 100))

      // Update conversation ID if new conversation was created
      if (data.conversation_id && data.conversation_id !== conversationId) {
        isCreatingConversation.current = true
        setConversationId(data.conversation_id)
        if (onConversationCreated) {
          onConversationCreated(data.conversation_id)
        }
      }
    } catch (error) {
      // Don't show error if request was aborted by user
      if (error.name === 'AbortError' || error.message.includes('aborted')) {
        console.log('Request canceled by user')
        // Remove the empty assistant message
        setMessages(prev => prev.slice(0, -1))
        return
      }

      console.error('Chat error:', error)

      // Handle 402/429 upgrade/rate-limit errors
      if (error.status === 402 || error.status === 429) {
        const detail = error.detail || { error: 'limit_exceeded', message: 'Plan limit reached. Please upgrade.' }
        setUpgradeError(detail)
        setShowUpgradeModal(true)
        // Remove empty assistant message
        setMessages(prev => prev.slice(0, -1))
        return
      }

      // Update last message with error
      setMessages(prev => {
        const newMessages = [...prev]
        if (newMessages[assistantMsgIndex]) {
          newMessages[assistantMsgIndex].content = 'Sorry, I encountered an error. Please try again.'
          newMessages[assistantMsgIndex].error = true
        }
        return newMessages
      })
    } finally {
      abortControllerRef.current = null
      setLoading(false)
      setCurrentPhase('idle')
      setThinkingContent('')
      setIsTyping(false)
    }
  }

  return (
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
                  className={`group/msg max-w-[85%] rounded-3xl px-4 py-2 ${msg.role === 'user'
                    ? isDark
                      ? `bg-[${msg.sent_by_color || '#2DFFB7'}]/20 text-dark-text border`
                      : `bg-[${msg.sent_by_color || '#1FE0A5'}]/20 text-[#062A33] border`
                    : isDark
                      ? 'text-dark-text'
                      : 'text-[#062A33]'
                    }`}
                  style={msg.role === 'user' && msg.sent_by_color ? {
                    backgroundColor: `${msg.sent_by_color}20`,
                    borderColor: msg.sent_by_color
                  } : undefined}
                >
                  {/* Team member name - shows on hover only */}
                  {msg.sent_by_color && msg.sent_by_name && (
                    <span className="block text-xs opacity-0 group-hover/msg:opacity-50 transition-opacity mb-1">{msg.sent_by_name}</span>
                  )}
                  {/* Thinking Section (Collapsible) - Only for assistant messages with thinking */}
                  {msg.role === 'assistant' && msg.thinking && (
                    <div className={`mb-3 pb-3 border-b ${isDark ? 'border-white/10' : 'border-[#1FE0A5]/20'}`}>
                      <button
                        onClick={() => toggleThinking(idx)}
                        className={`flex items-center gap-2 text-xs transition-colors ${isDark ? 'text-yellow-400/70 hover:text-yellow-400' : 'text-yellow-600/70 hover:text-yellow-600'
                          }`}
                      >
                        {/* Lightbulb Icon */}
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7zm2.85 11.1l-.85.6V16h-4v-2.3l-.85-.6A4.997 4.997 0 017 9c0-2.76 2.24-5 5-5s5 2.24 5 5c0 1.63-.8 3.16-2.15 4.1z" />
                        </svg>
                        <span>{expandedThinking[idx] ? 'Hide reasoning' : 'View reasoning'}</span>
                        <svg
                          className={`w-3 h-3 transition-transform ${expandedThinking[idx] ? 'rotate-180' : ''}`}
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>
                      {expandedThinking[idx] && (
                        <div className={`mt-2 p-3 rounded-lg text-sm leading-relaxed ${isDark ? 'bg-yellow-500/10 text-white/60' : 'bg-yellow-500/10 text-gray-600'
                          }`}>
                          {msg.thinking}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Message Content */}
                  <div className="whitespace-pre-wrap leading-relaxed space-y-4">
                    {msg.content.split('\n\n').map((paragraph, i) => (
                      <p key={i}>{paragraph}</p>
                    ))}
                    {/* Typing cursor for last assistant message */}
                    {isTyping && msg.role === 'assistant' && idx === messages.length - 1 && (
                      <span className="inline-block w-2 h-5 ml-1 bg-current animate-pulse" />
                    )}
                  </div>

                  {/* Enhanced Sources Section */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className={`mt-3 pt-3 border-t ${isDark ? 'border-white/10' : 'border-[#1FE0A5]/20'}`}>
                      <p className="text-xs opacity-50 mb-2">Sources</p>
                      <div className="flex flex-wrap gap-2">
                        {msg.sources.map((source, i) => {
                          // Web search source
                          if (source.type === 'web_search') {
                            const domain = source.domain || (source.url ? new URL(source.url).hostname : 'web')
                            return (
                              <a
                                key={i}
                                href={source.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className={`text-xs px-2.5 py-1.5 rounded-lg hover:scale-105 transition-all flex items-center gap-1.5 ${isDark ? 'bg-blue-500/20 text-blue-300 hover:bg-blue-500/30' : 'bg-blue-500/10 text-blue-600 hover:bg-blue-500/20'
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
                          } else if (source.type === 'ai_knowledge') {
                            // AI Knowledge source (purple styling)
                            return (
                              <span
                                key={i}
                                className={`text-xs px-2.5 py-1.5 rounded-lg flex items-center gap-1.5 ${isDark ? 'bg-purple-500/20 text-purple-300' : 'bg-purple-500/15 text-purple-700'
                                  }`}
                                title={`AI Knowledge: ${source.topic}`}
                              >
                                {/* Brain/AI Icon */}
                                <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                                  <path d="M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7z" />
                                </svg>
                                <span>{source.topic?.length > 20 ? source.topic.substring(0, 20) + '...' : source.topic || 'AI Knowledge'}</span>
                              </span>
                            )
                          } else {
                            // Document source with confidence badge
                            const confidence = source.confidence || 'medium'
                            return (
                              <span
                                key={i}
                                className={`text-xs px-2.5 py-1.5 rounded-lg flex items-center gap-1.5 ${isDark ? 'bg-dark-accent/20 text-dark-accent' : 'bg-[#1FE0A5]/15 text-[#0B3C49]'
                                  }`}
                                title={source.quote ? `"${source.quote}"` : source.file_name}
                              >
                                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                                <span>{source.file_name?.length > 20 ? source.file_name.substring(0, 20) + '...' : source.file_name || 'Document'}</span>
                                {/* Confidence Badge */}
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
          {/* Loading indicator - only show during thinking phase, not during typing */}
          {loading && !isTyping && (
            <div className="flex justify-start">
              <div className="rounded-lg p-4">
                <div className="flex items-center gap-2">
                  {currentPhase === 'thinking' ? (
                    // Thinking phase indicator (lightbulb pulsing)
                    <svg className="w-5 h-5 animate-pulse text-yellow-400" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7zm2.85 11.1l-.85.6V16h-4v-2.3l-.85-.6A4.997 4.997 0 017 9c0-2.76 2.24-5 5-5s5 2.24 5 5c0 1.63-.8 3.16-2.15 4.1z" />
                    </svg>
                  ) : (
                    // Default spinner
                    <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-dark-accent"></div>
                  )}
                  <span className={`text-sm ${isDark ? 'text-dark-text/70' : 'text-[#062A33]/70'}`}>{loadingMessage}</span>
                </div>
                {/* Show live thinking content if in thinking phase */}
                {currentPhase === 'thinking' && thinkingContent && (
                  <div className={`mt-2 text-xs max-w-md p-2 rounded-lg ${isDark ? 'bg-yellow-500/10 text-white/50' : 'bg-yellow-500/10 text-gray-500'
                    }`}>
                    {thinkingContent.slice(-200)}...
                  </div>
                )}
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="pt-0 px-[16px] pb-0">
        <div className="max-w-4xl mx-auto">
          {/* Selected Files Mentions */}
          {selectedFiles.length > 0 && (
            <div className="mb-2 flex flex-wrap gap-2">
              {selectedFiles.map((file) => (
                <div
                  key={file.id}
                  className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm ${isDark
                    ? 'bg-dark-accent/20 border border-dark-accent/50'
                    : 'bg-[#1FE0A5]/10 border border-[#1FE0A5]'
                    }`}
                >
                  <span className={isDark ? 'text-dark-accent' : 'text-[#0B3C49]'}>@{file.name}</span>
                  <button
                    type="button"
                    onClick={() => removeSelectedFile(file.id)}
                    className="ml-1 hover:bg-dark-accent/20 rounded-full p-0.5 transition-colors"
                  >
                    <svg className="w-3 h-3 dark:text-dark-accent text-dark-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Create File Mode Chip */}
          {createFileMode && (
            <div className="mb-2 flex flex-wrap gap-2">
              <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm ${isDark
                ? 'bg-yellow-500/15 border border-yellow-500/40'
                : 'bg-yellow-500/10 border border-yellow-500/30'
                }`}
              >
                <span className={isDark ? 'text-yellow-300' : 'text-yellow-700'}>
                  {createFileDraftReady ? 'Draft ready' : '/createfile'}
                </span>
                <button
                  type="button"
                  onClick={() => {
                    setCreateFileMode(false)
                    setCreateFileError('')
                    setCreateFileDraftReady(false)
                  }}
                  className="ml-1 hover:bg-yellow-500/20 rounded-full p-0.5 transition-colors"
                  title="Exit create file mode"
                >
                  <svg className="w-3 h-3 text-current" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          )}

          <form onSubmit={handleSend}>
            {/* Create File Name Input */}
            {createFileMode && createFileDraftReady && (
              <div className="mb-2">
                <input
                  type="text"
                  value={createFileName}
                  onChange={(e) => setCreateFileName(e.target.value)}
                  placeholder="filename.md or filename.txt"
                  className={`w-full px-3 py-2 rounded-xl bg-transparent border ${isDark
                    ? 'border-white/10 text-dark-text placeholder:text-dark-text/50'
                    : 'border-[#1FE0A5]/30 text-[#062A33] placeholder:text-[#062A33]/50'
                    } focus:outline-none focus:ring-1 focus:ring-dark-accent/50 transition-all`}
                />
                {createFileError && (
                  <p className="mt-1 text-xs text-red-400">{createFileError}</p>
                )}
              </div>
            )}
            {createFileMode && !createFileDraftReady && createFileError && (
              <p className="mb-2 text-xs text-red-400">{createFileError}</p>
            )}
            {/* Hidden file inputs */}
            <input
              ref={fileInputRef}
              type="file"
              multiple
              className="hidden"
              onChange={handleFileInput}
              disabled={uploading}
            />
            <input
              ref={folderInputRef}
              type="file"
              webkitdirectory=""
              directory=""
              multiple
              className="hidden"
              onChange={handleFileInput}
              disabled={uploading}
            />

            {/* Input Bar - Dynamic layout */}
            <div className={`transition-all duration-200 ease-in-out border rounded-3xl flex items-center py-2 ${isDark
              ? 'bg-white/5 border-white/10'
              : 'bg-white/50 border-[#1FE0A5]/30'
              }`}>

              {/* + button on left */}
              <div className="relative pl-2 flex-shrink-0" ref={uploadMenuRef}>
                <button
                  type="button"
                  onClick={handleUploadClick}
                  disabled={uploading}
                  className="p-1.5 rounded-full hover:bg-white/10 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Upload files"
                >
                  {uploading ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-dark-accent"></div>
                  ) : (
                    <svg className={`w-5 h-5 ${isDark ? 'text-dark-text/70' : 'text-[#062A33]/70'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                  )}
                </button>
                {/* Upload Menu Dropdown */}
                {showUploadMenu && !uploading && (
                  <div className={`absolute bottom-full left-0 mb-2 w-48 rounded-lg backdrop-blur-xl border shadow-lg py-2 z-50 ${isDark ? 'bg-black/20 border-white/10' : 'bg-white/90 border-[#1FE0A5]/20'
                    }`}>
                    <button type="button" onClick={handleUploadFileClick} className={`w-full px-4 py-2 text-left text-sm transition-colors flex items-center gap-2 ${isDark ? 'text-dark-text hover:bg-white/10' : 'text-[#062A33] hover:bg-black/10'}`}>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                      Upload File
                    </button>
                    <button type="button" onClick={handleUploadFolderClick} className={`w-full px-4 py-2 text-left text-sm transition-colors flex items-center gap-2 ${isDark ? 'text-dark-text hover:bg-white/10' : 'text-[#062A33] hover:bg-black/10'}`}>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" /></svg>
                      Upload Folder
                    </button>
                    <button type="button" onClick={handleCreateDocClick} className={`w-full px-4 py-2 text-left text-sm transition-colors flex items-center gap-2 ${isDark ? 'text-dark-text hover:bg-white/10' : 'text-[#062A33] hover:bg-black/10'}`}>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                      </svg>
                      Create Doc
                    </button>
                  </div>
                )}
              </div>

              {/* Textarea */}
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={createFileMode
                  ? (createFileDraftReady ? 'Edit file content...' : 'Describe the file to create...')
                  : 'Ask about your documents...'}
                className={`flex-1 min-w-0 bg-transparent focus:outline-none resize-none overflow-y-auto text-[16px] leading-6 px-3 ${isDark
                    ? 'text-dark-text placeholder:text-dark-text/50'
                    : 'text-[#062A33] placeholder:text-[#062A33]/50'
                  }`}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSend(e)
                  }
                }}
                style={{
                  height: '24px',
                  maxHeight: '144px',
                }}
              />

              {/* Send button on right */}
              <button
                type={loading ? "button" : "submit"}
                onClick={loading ? handleStop : undefined}
                disabled={!loading && (createFileMode
                  ? (createFileDraftReady
                    ? (!input.trim() || !createFileName.trim())
                    : (!input.trim())
                  )
                  : (!input.trim() && selectedFiles.length === 0)
                )}
                className={`flex-shrink-0 w-8 h-8 mr-2 rounded-full text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center ${loading ? 'bg-red-500 hover:bg-red-600' : 'bg-dark-accent hover:bg-dark-accent/90'
                  }`}
                title={loading ? "Stop generation" : (createFileMode ? (createFileDraftReady ? "Create file" : "Generate draft") : "Send message")}
              >
                {loading ? (
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="12" rx="1" /></svg>
                ) : (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" /></svg>
                )}
              </button>
            </div>
          </form>

          {/* Disclaimer */}
          <p className={`text-center text-[10px] py-[3px] ${isDark ? 'text-white/30' : 'text-[#062A33]/30'}`}>
            AIveilix can make mistakes. Check important info.
          </p>
        </div>
      </div>

      {/* Upgrade Modal */}
      <UpgradeModal
        isOpen={showUpgradeModal}
        onClose={() => setShowUpgradeModal(false)}
        error={upgradeError}
      />
    </div>
  )
}
