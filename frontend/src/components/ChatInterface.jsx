import { useState, useEffect, useRef } from 'react'
import { chatAPI } from '../services/api'
import Button from './Button'
import { useTheme } from '../context/ThemeContext'

export default function ChatInterface({ bucketId }) {
  const { isDark } = useTheme()
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    
    // Add user message to UI
    const newUserMessage = {
      role: 'user',
      content: userMessage,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, newUserMessage])
    setLoading(true)

    try {
      const response = await chatAPI.sendMessage(bucketId, userMessage, conversationId)
      const data = response.data

      // Add assistant response
      const assistantMessage = {
        role: 'assistant',
        content: data.message,
        sources: data.sources,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, assistantMessage])
      setConversationId(data.conversation_id)
    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        error: true,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto mb-4 space-y-4 p-4">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <p className="dark:text-dark-text/70 text-light-text/70 mb-2">
              Start a conversation about your bucket
            </p>
            <p className="text-sm dark:text-dark-text/50 text-light-text/50">
              Ask questions about your uploaded documents
            </p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  msg.role === 'user'
                    ? 'bg-[#0B3C49] text-white'
                    : 'dark:text-dark-text text-light-text'
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-white/10">
                    <p className="text-xs opacity-70 mb-1">Sources:</p>
                    <div className="flex flex-wrap gap-1">
                      {msg.sources.slice(0, 3).map((source, i) => (
                        <span key={i} className="text-xs px-2 py-1 rounded bg-white/10">
                          {source.file_name}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex justify-start">
            <div className="rounded-lg p-3">
              <div className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-dark-accent"></div>
                <span className="text-sm dark:text-dark-text/70 text-light-text/70">Thinking...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form onSubmit={handleSend} className="flex gap-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about your documents..."
          rows={2}
          className="flex-1 px-4 py-3 rounded-lg bg-white/5 dark:bg-black/10 border border-white/10 dark:text-dark-text text-light-text placeholder:dark:text-dark-text/40 placeholder:text-light-text/40 focus:outline-none focus:ring-1 focus:ring-dark-accent/50 transition-all duration-200 resize-none"
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              handleSend(e)
            }
          }}
        />
        <Button
          type="submit"
          disabled={!input.trim() || loading}
          className="px-6"
        >
          Send
        </Button>
      </form>
    </div>
  )
}
