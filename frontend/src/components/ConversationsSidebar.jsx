import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTheme } from '../context/ThemeContext'
import axios from 'axios'
import { config } from '../config'

export default function ConversationsSidebar({ bucket, bucketId, currentConversationId, onConversationSelect, onNewChat }) {
  const navigate = useNavigate()
  const { isDark } = useTheme()
  const [conversations, setConversations] = useState([])
  const [loading, setLoading] = useState(true)
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [editingTitle, setEditingTitle] = useState('')
  const [menuOpenId, setMenuOpenId] = useState(null)
  const menuRef = useRef(null)

  useEffect(() => {
    loadConversations()
  }, [bucketId])

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setMenuOpenId(null)
      }
    }

    if (menuOpenId) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [menuOpenId])

  const loadConversations = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem('access_token')
      const response = await axios.get(
        `${config.apiUrl}/api/buckets/${bucketId}/conversations`,
        { headers: { Authorization: `Bearer ${token}` } }
      )
      setConversations(response.data.conversations || [])
    } catch (error) {
      console.error('Failed to load conversations:', error)
    } finally {
      setLoading(false)
    }
  }

  const deleteConversation = async (convId) => {
    if (!confirm('Delete this conversation?')) return

    try {
      const token = localStorage.getItem('access_token')
      await axios.delete(
        `${config.apiUrl}/api/buckets/conversations/${convId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      )
      
      // Reload conversations
      await loadConversations()
      
      // If deleted current conversation, start new chat
      if (convId === currentConversationId) {
        onNewChat()
      }
      
      setMenuOpenId(null)
    } catch (error) {
      console.error('Failed to delete conversation:', error)
      alert('Failed to delete conversation')
    }
  }

  const startEditConversation = (conv) => {
    setEditingId(conv.id)
    setEditingTitle(conv.title || 'Untitled Chat')
    setMenuOpenId(null)
  }

  const saveConversationTitle = async (convId) => {
    if (!editingTitle.trim()) {
      setEditingId(null)
      return
    }

    try {
      const token = localStorage.getItem('access_token')
      await axios.patch(
        `${config.apiUrl}/api/buckets/conversations/${convId}`,
        { title: editingTitle.trim() },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      
      // Reload conversations
      await loadConversations()
      setEditingId(null)
    } catch (error) {
      console.error('Failed to update conversation:', error)
      alert('Failed to update conversation name')
    }
  }

  const cancelEdit = () => {
    setEditingId(null)
    setEditingTitle('')
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  return (
    <div 
      className={`h-full rounded-2xl backdrop-blur-xl flex flex-col transition-all duration-300 ${
        isDark ? 'bg-white/5' : 'bg-black/5'
      } ${isCollapsed ? 'w-16' : 'w-64'}`}
    >
      {/* Collapse Button - Always visible */}
      <div className="p-4 flex items-center justify-between">
        {!isCollapsed && (
          <h3 className={`font-semibold ${isDark ? 'text-dark-text' : 'text-[#062A33]'}`}>
            Menu
          </h3>
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className={`p-1.5 rounded transition-colors ml-auto ${
            isDark ? 'hover:bg-white/10' : 'hover:bg-black/10'
          }`}
          title={isCollapsed ? 'Expand' : 'Collapse'}
        >
          <svg 
            className={`w-5 h-5 transition-transform ${
              isCollapsed ? 'rotate-180' : ''
            } ${isDark ? 'text-dark-text/70' : 'text-[#062A33]/70'}`}
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
          </svg>
        </button>
      </div>

      {isCollapsed ? (
        /* Collapsed View - Icons Only */
        <div className="flex flex-col items-center gap-2 px-2">
          {/* Back to Dashboard Icon */}
          <button
            onClick={() => navigate('/dashboard')}
            className={`p-2.5 rounded-lg transition-colors ${
              isDark 
                ? 'hover:bg-white/10 text-dark-text/70 hover:text-dark-text' 
                : 'hover:bg-black/10 text-[#062A33]/70 hover:text-[#062A33]'
            }`}
            title="Back to Dashboard"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          {/* New Chat Icon */}
          <button
            onClick={onNewChat}
            className={`p-2.5 rounded-lg transition-all ${
              isDark 
                ? 'hover:bg-white/10 text-dark-text' 
                : 'hover:bg-black/10 text-[#062A33]'
            }`}
            title="New Chat"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
        </div>
      ) : (
        <>
          {/* Expanded View - Full Content */}
          {/* Back to Dashboard + Bucket Name */}
          <div className="px-4 pb-4">
            <button
              onClick={() => navigate('/dashboard')}
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
              {bucket?.name || 'Bucket'}
            </h2>
            {bucket?.description && (
              <p className={`text-xs mt-1 ${
                isDark ? 'text-dark-text/60' : 'text-[#062A33]/60'
              }`}>
                {bucket.description}
              </p>
            )}
          </div>

          {/* New Chat Button */}
          <div className="px-4 pb-4">
            <button
              onClick={onNewChat}
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

          {/* Conversations List */}
          <div className="flex-1 overflow-y-auto px-3">
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className={`animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 ${
                  isDark ? 'border-dark-accent' : 'border-light-accent'
                }`}></div>
              </div>
            ) : conversations.length === 0 ? (
              <div className={`text-center py-8 text-sm ${
                isDark ? 'text-dark-text/50' : 'text-[#062A33]/50'
              }`}>
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
                    {editingId === conv.id ? (
                      // Edit Mode
                      <div className="flex items-center gap-2">
                        <input
                          type="text"
                          value={editingTitle}
                          onChange={(e) => setEditingTitle(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') saveConversationTitle(conv.id)
                            if (e.key === 'Escape') cancelEdit()
                          }}
                          className={`flex-1 px-2 py-1 text-sm rounded border focus:outline-none ${
                            isDark 
                              ? 'bg-white/10 border-white/20 text-dark-text focus:border-dark-accent' 
                              : 'bg-black/10 border-black/20 text-[#062A33] focus:border-light-accent'
                          }`}
                          autoFocus
                        />
                        <button
                          onClick={() => saveConversationTitle(conv.id)}
                          className="p-1 text-green-400 hover:bg-green-500/10 rounded"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </button>
                        <button
                          onClick={cancelEdit}
                          className="p-1 text-red-400 hover:bg-red-500/10 rounded"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    ) : (
                      // View Mode
                      <div 
                        onClick={() => onConversationSelect(conv.id)}
                        className="flex items-start justify-between gap-2"
                      >
                        <div className="flex-1 min-w-0">
                          <p className={`text-sm font-medium truncate ${
                            isDark ? 'text-dark-text' : 'text-[#062A33]'
                          }`}>
                            {conv.title || 'Untitled Chat'}
                          </p>
                          <p className={`text-xs mt-1 ${
                            isDark ? 'text-dark-text/50' : 'text-[#062A33]/50'
                          }`}>
                            {formatDate(conv.updated_at || conv.created_at)}
                          </p>
                        </div>
                        
                        {/* Three-dot menu */}
                        <div className="relative">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              setMenuOpenId(menuOpenId === conv.id ? null : conv.id)
                            }}
                            className={`opacity-0 group-hover:opacity-100 p-1 rounded transition-all ${
                              isDark ? 'hover:bg-white/10' : 'hover:bg-black/10'
                            }`}
                          >
                            <svg className={`w-4 h-4 ${isDark ? 'text-dark-text/70' : 'text-[#062A33]/70'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                            </svg>
                          </button>
                          
                          {/* Dropdown Menu */}
                          {menuOpenId === conv.id && (
                            <div 
                              ref={menuRef}
                              className={`absolute right-0 mt-1 w-32 rounded-lg shadow-lg border z-10 ${
                                isDark 
                                  ? 'bg-dark-surface border-white/10' 
                                  : 'bg-[#F6FFFC] border-[#1FE0A5]/20'
                              }`}
                            >
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  startEditConversation(conv)
                                }}
                                className={`w-full px-3 py-2 text-left text-sm flex items-center gap-2 rounded-t-lg ${
                                  isDark 
                                    ? 'text-dark-text hover:bg-white/10' 
                                    : 'text-[#062A33] hover:bg-black/10'
                                }`}
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                </svg>
                                Rename
                              </button>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  deleteConversation(conv.id)
                                }}
                                className="w-full px-3 py-2 text-left text-sm flex items-center gap-2 text-red-400 hover:bg-red-500/10 rounded-b-lg"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                                Delete
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
