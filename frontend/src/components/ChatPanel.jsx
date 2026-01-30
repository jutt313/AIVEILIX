import { useState, useEffect, useRef } from 'react'
import { chatAPI, filesAPI } from '../services/api'
import { useTheme } from '../context/ThemeContext'

export default function ChatPanel({ 
  bucketId, 
  conversationId: externalConversationId, 
  onConversationCreated,
  onFilesUpdate, 
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
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)
  const uploadMenuRef = useRef(null)
  const fileInputRef = useRef(null)
  const folderInputRef = useRef(null)
  const isCreatingConversation = useRef(false)
  const abortControllerRef = useRef(null)

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
        timestamp: new Date(msg.created_at)
      }))
      
      setMessages(formattedMessages)
    } catch (error) {
      console.error('Failed to load conversation messages:', error)
      setMessages([])
    }
  }

  useEffect(() => {
    // Auto-resize textarea (grows upward)
    if (textareaRef.current) {
      textareaRef.current.style.height = '24px'
      const newHeight = Math.min(textareaRef.current.scrollHeight, 128)
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

    setUploading(true)
    setShowUploadMenu(false)
    let successCount = 0
    let errorCount = 0

    for (const file of Array.from(files)) {
      try {
        // Extract folder path from webkitRelativePath if available
        let folderPath = null
        if (file.webkitRelativePath) {
          const pathParts = file.webkitRelativePath.split('/')
          if (pathParts.length > 1) {
            // Remove the filename, keep only the folder path
            folderPath = pathParts.slice(0, -1).join('/')
          }
        }
        await filesAPI.upload(bucketId, file, folderPath)
        successCount++
      } catch (error) {
        console.error(`Upload failed for ${file.name}:`, error)
        errorCount++
        // Continue with next file
      }
    }

    if (onFilesUpdate) onFilesUpdate()

    if (errorCount > 0) {
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

  const removeSelectedFile = (fileId) => {
    if (onSelectedFilesChange) {
      onSelectedFilesChange(selectedFiles.filter(f => f.id !== fileId))
    }
  }

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
      setLoading(false)

      // Remove the user message since we're canceling
      setMessages(prev => prev.slice(0, -1))
    }
  }

  const handleSend = async (e) => {
    e.preventDefault()
    if ((!input.trim() && selectedFiles.length === 0) || loading) return

    // Build message with file references
    let userMessage = input.trim()
    if (selectedFiles.length > 0) {
      const fileRefs = selectedFiles.map(f => `@${f.name}`).join(' ')
      userMessage = fileRefs + (userMessage ? ` ${userMessage}` : '')
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
    const searchKeywords = ['search', 'look up', 'find', 'what is', 'who is', 'how to', 'current', 'latest', 'today', 'recent', 'news', 'weather', 'price']
    const isSearchQuery = searchKeywords.some(keyword => queryLower.includes(keyword))

    if (isSearchQuery) {
      // Extract topic (first 3 words, skip common words)
      const words = userMessage.split(' ').filter(w => !['the', 'a', 'an', 'is', 'what', 'who', 'how', 'to', 'search', 'find', 'look', 'up'].includes(w.toLowerCase()))
      const topic = words.slice(0, 3).join(' ')
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
      timestamp: new Date()
    }])

    try {
      const response = await chatAPI.sendMessage(
        bucketId,
        userMessage,
        conversationId,
        abortControllerRef.current.signal,
        (chunk) => {
          // Update message content as chunks arrive
          setMessages(prev => {
            const newMessages = [...prev]
            if (newMessages[assistantMsgIndex]) {
              newMessages[assistantMsgIndex].content += chunk
            }
            return newMessages
          })
        }
      )
      const data = response.data

      // Update final message with sources
      setMessages(prev => {
        const newMessages = [...prev]
        if (newMessages[assistantMsgIndex]) {
          newMessages[assistantMsgIndex].sources = data.sources
        }
        return newMessages
      })

      console.log('📦 Assistant message sources:', data.sources)

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
                </div>
                {msg.sources && msg.sources.length > 0 && (
                  <div className={`mt-3 pt-3 border-t ${isDark ? 'border-white/10' : 'border-[#1FE0A5]/20'}`}>
                    <p className="text-xs opacity-70 mb-2">Sources:</p>
                    <div className="flex flex-wrap gap-1.5">
                      {msg.sources.map((source, i) => {
                        // Handle different source types
                        if (source.type === 'web_search') {
                          return (
                            <a
                              key={i}
                              href={source.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className={`text-xs px-2 py-1 rounded hover:opacity-80 transition-opacity flex items-center gap-1 ${isDark ? 'bg-blue-500/20 text-blue-400' : 'bg-blue-500/10 text-blue-600'}`}
                              title={source.snippet || source.title}
                            >
                              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                              </svg>
                              {source.title.length > 30 ? source.title.substring(0, 30) + '...' : source.title}
                            </a>
                          )
                        } else {
                          // File source
                          return (
                            <span key={i} className={`text-xs px-2 py-1 rounded ${isDark ? 'bg-white/10' : 'bg-[#1FE0A5]/10 text-[#0B3C49]'}`}>
                              {source.file_name || 'Document'}
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
        {loading && (
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
      <div className="p-4">
        <div className="max-w-4xl mx-auto">
        {/* Selected Files Mentions */}
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
        
        <form onSubmit={handleSend}>
          {/* Input Bar with rounded corners (not full pill) */}
          <div className={`flex-1 flex items-center gap-3 px-4 py-3 rounded-[32px] border ${
            isDark
              ? 'bg-white/5 border-white/5'
              : 'bg-white/50 border-[#1FE0A5]/30'
          }`}>
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

            {/* Upload Button (left) - Stays at bottom */}
            <div className="relative flex-shrink-0" ref={uploadMenuRef}>
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
                <div className={`absolute bottom-full left-0 mb-2 w-48 rounded-lg backdrop-blur-xl border shadow-lg py-2 z-50 ${
                  isDark 
                    ? 'bg-black/20 border-white/10' 
                    : 'bg-white/90 border-[#1FE0A5]/20'
                }`}>
                  <button
                    type="button"
                    onClick={handleUploadFileClick}
                    className={`w-full px-4 py-2 text-left text-sm transition-colors flex items-center gap-2 ${
                      isDark 
                        ? 'text-dark-text hover:bg-white/10' 
                        : 'text-[#062A33] hover:bg-black/10'
                    }`}
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Upload File
                  </button>
                  <button
                    type="button"
                    onClick={handleUploadFolderClick}
                    className={`w-full px-4 py-2 text-left text-sm transition-colors flex items-center gap-2 ${
                      isDark 
                        ? 'text-dark-text hover:bg-white/10' 
                        : 'text-[#062A33] hover:bg-black/10'
                    }`}
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                    </svg>
                    Upload Folder
                  </button>
                </div>
              )}
            </div>

            {/* Message Input - Multi-line */}
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about your documents..."
              className={`flex-1 bg-transparent focus:outline-none resize-none overflow-y-auto leading-6 ${
                isDark 
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
                maxHeight: '128px',
              }}
            />

            {/* Send/Stop Button - Transforms while loading */}
            <button
              type={loading ? "button" : "submit"}
              onClick={loading ? handleStop : undefined}
              disabled={!loading && (!input.trim() && selectedFiles.length === 0)}
              className={`flex-shrink-0 w-8 h-8 rounded-full text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center ${
                loading
                  ? 'bg-red-500 hover:bg-red-600'
                  : 'bg-dark-accent hover:bg-dark-accent/90'
              }`}
              title={loading ? "Stop generation" : "Send message"}
            >
              {loading ? (
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <rect x="6" y="6" width="12" height="12" rx="1" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                </svg>
              )}
            </button>
          </div>
        </form>
        </div>
      </div>
    </div>
  )
}
