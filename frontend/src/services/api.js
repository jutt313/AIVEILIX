import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:7223'

// Global toast bridge — ToastContext registers itself here on mount
let _showToast = null
export function registerToast(fn) { _showToast = fn }
export function showGlobalToast(msg, type = 'error') {
  if (_showToast) _showToast(msg, type)
}

// ─── Network debug logger ───────────────────────────────────────────────────
// TODO: set NET_LOG = false before production hardening
const NET_LOG = true
if (NET_LOG) {
  console.log(
    '%c[AIveilix] Network logging ON — API base: ' + (import.meta.env.VITE_API_URL || 'http://localhost:7223'),
    'background:#1a1a2e;color:#2DFFB7;font-weight:bold;padding:4px 8px;border-radius:4px'
  )
}

const _reqColors = {
  GET:    '#4CAF50',
  POST:   '#2196F3',
  PUT:    '#FF9800',
  PATCH:  '#9C27B0',
  DELETE: '#F44336',
}

function _bytes(n) {
  if (!n) return '?'
  if (n < 1024) return `${n}B`
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)}KB`
  return `${(n / (1024 * 1024)).toFixed(2)}MB`
}

function _netLog(method, url, status, ms, resSize, extra) {
  if (!NET_LOG) return
  const color = status >= 500 ? '#F44336' : status >= 400 ? '#FF9800' : status >= 300 ? '#9C27B0' : '#4CAF50'
  const badge = `color:${_reqColors[method] || '#607D8B'};font-weight:bold`
  const timeBadge = ms > 3000 ? 'color:#F44336;font-weight:bold' : ms > 1000 ? 'color:#FF9800' : 'color:#888'
  console.groupCollapsed(
    `%c${method}%c ${url}  %c${status}%c  ${ms}ms  ${_bytes(resSize)}`,
    badge, 'color:inherit', `color:${color};font-weight:bold`, timeBadge
  )
  console.log('⏱  Duration :', `${ms}ms`, ms > 3000 ? '🔴 SLOW' : ms > 1000 ? '🟡 SLOW' : '🟢')
  console.log('📡 Status   :', status)
  console.log('📦 Res size :', _bytes(resSize))
  if (extra) console.log('📋 Detail   :', extra)
  console.groupEnd()
}
// ─────────────────────────────────────────────────────────────────────────────

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token + start-time stamp to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  config._t0 = performance.now()
  if (NET_LOG) {
    const badge = `color:${_reqColors[config.method?.toUpperCase()] || '#607D8B'};font-weight:bold`
    console.log(`%c→ ${config.method?.toUpperCase()} %c${config.baseURL || ''}${config.url}`, badge, 'color:#aaa', config.params || '')
  }
  return config
})

// Log every response (success + error)
api.interceptors.response.use(
  (response) => {
    const ms = Math.round(performance.now() - (response.config._t0 || 0))
    const resSize = JSON.stringify(response.data)?.length
    _netLog(
      response.config.method?.toUpperCase(),
      response.config.url,
      response.status,
      ms,
      resSize,
      null
    )
    return response
  },
  (error) => {
    const status = error.response?.status
    const config = error.config || {}
    const url = config.url || ''
    const ms = config._t0 ? Math.round(performance.now() - config._t0) : 0
    const resSize = error.response?.data ? JSON.stringify(error.response.data)?.length : 0
    const detail = error.response?.data?.detail || error.message

    if (NET_LOG) {
      console.groupCollapsed(
        `%c✖ ${config.method?.toUpperCase()} %c${url}  %c${status || 'ERR'}%c  ${ms}ms`,
        'color:#F44336;font-weight:bold', 'color:inherit', 'color:#F44336;font-weight:bold', 'color:#888'
      )
      console.log('⏱  Duration :', `${ms}ms`)
      console.log('❌ Status   :', status)
      console.log('📦 Res size :', _bytes(resSize))
      console.log('💬 Detail   :', detail)
      if (error.response?.data) console.log('📋 Body     :', error.response.data)
      console.groupEnd()
    }

    const isAuthEndpoint = url.includes('/api/auth/login') || url.includes('/api/auth/signup') || url.includes('/api/auth/forgot-password') || url.includes('/api/auth/me')
    const isOnAuthPage = ['/login', '/signup', '/forgot-password'].includes(window.location.pathname)

    if (status === 401) {
      if (!isAuthEndpoint && !isOnAuthPage) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
    } else if (status === 429) {
      showGlobalToast('Too many requests. Please slow down and try again.', 'warning')
    } else if (status >= 500) {
      // Only show toast for non-auth endpoints (auth pages handle their own errors)
      if (!isAuthEndpoint && !isOnAuthPage) {
        const msg = error.response?.data?.detail
        showGlobalToast(typeof msg === 'string' ? msg : 'Something went wrong. Please try again.', 'error')
      }
    }

    return Promise.reject(error)
  }
)

export const authAPI = {
  signup: (email, password, fullName) => 
    api.post('/api/auth/signup', { email, password, full_name: fullName }),
  
  login: (email, password) => 
    api.post('/api/auth/login', { email, password }),
  
  forgotPassword: (email) => 
    api.post('/api/auth/forgot-password', { email }),
  
  resetPassword: (accessToken, newPassword) => 
    api.post('/api/auth/reset-password', { access_token: accessToken, new_password: newPassword }),
  
  logout: () => 
    api.post('/api/auth/logout'),
  
  getMe: () => 
    api.get('/api/auth/me'),
  
  changePassword: (currentPassword, newPassword) =>
    api.post('/api/auth/change-password', { current_password: currentPassword, new_password: newPassword }),
  
  deleteAccount: (password) =>
    api.post('/api/auth/delete-account', { password }),
}

export const apiKeysAPI = {
  list: () => api.get('/api/api-keys/'),
  create: (name, scopes, allowedBuckets) => 
    api.post('/api/api-keys/', { name, scopes, allowed_buckets: allowedBuckets }),
  delete: (keyId) => api.delete(`/api/api-keys/${keyId}`),
}

export const oauthAPI = {
  list: () => api.get('/api/oauth/clients'),
  create: (name, redirectUri, scopes) => 
    api.post('/api/oauth/clients', { name, redirect_uri: redirectUri, scopes }),
  delete: (clientId) => api.delete(`/api/oauth/clients/${clientId}`),
}

export const bucketsAPI = {
  list: () => api.get('/api/buckets/'),
  get: (bucketId) => api.get(`/api/buckets/${bucketId}`),
  create: (name, description) => api.post('/api/buckets/', { name, description }),
  delete: (bucketId) => api.delete(`/api/buckets/${bucketId}`),
  deleteAll: (password) => api.post('/api/buckets/delete-all', { password }),
  getStats: () => api.get('/api/buckets/stats/dashboard'),
  getActivity: (days = 30, startDate = null, endDate = null) => {
    const params = {}
    if (days) params.days = days
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    return api.get('/api/buckets/stats/activity', { params })
      .catch((error) => {
        // Silently handle 404 - endpoint doesn't exist yet
        if (error.response?.status === 404) {
          return { data: { data: [] } }
        }
        throw error
      })
  },
}

export const filesAPI = {
  upload: async (bucketId, file, folderPath = null, batchMeta = null, conversationId = null) => {
    const ext = file?.name?.includes('.') ? `.${file.name.split('.').pop().toLowerCase()}` : ''
    const blockedDirectExtensions = new Set([
      '.dmg', '.exe', '.msi', '.pkg', '.iso', '.apk', '.app', '.bin', '.img',
    ])
    const shouldTryDirectUpload = file.size > 5 * 1024 * 1024 && !blockedDirectExtensions.has(ext)

    // Try direct-to-Supabase upload for files > 5MB
    if (shouldTryDirectUpload) {
      try {
        const { supabase } = await import('../lib/supabase')
        const userId = JSON.parse(localStorage.getItem('user') || '{}').id
        if (!userId) throw new Error('No user ID')

        const storagePath = `${userId}/${bucketId}/${crypto.randomUUID()}${ext}`

        const { error: uploadError } = await supabase.storage
          .from('files')
          .upload(storagePath, file)

        if (uploadError) throw uploadError

        // Register with backend
        const formData = new FormData()
        formData.append('storage_path', storagePath)
        formData.append('filename', file.name)
        formData.append('size_bytes', file.size.toString())
        formData.append('mime_type', file.type || 'application/octet-stream')
        if (folderPath) formData.append('folder_path', folderPath)
        if (conversationId) formData.append('conversation_id', conversationId)
        if (batchMeta?.count) formData.append('batch_count', String(batchMeta.count))
        if (batchMeta?.totalBytes) formData.append('batch_total_bytes', String(batchMeta.totalBytes))

        return api.post(`/api/buckets/${bucketId}/register-upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      } catch (directErr) {
        console.warn('Direct upload failed, falling back to backend upload:', directErr)
        // Fall through to backend upload
      }
    }

    // Standard backend upload (small files or fallback)
    const formData = new FormData()
    formData.append('file', file)
    if (folderPath) {
      formData.append('folder_path', folderPath)
    }
    if (conversationId) {
      formData.append('conversation_id', conversationId)
    }
    if (batchMeta?.count) formData.append('batch_count', String(batchMeta.count))
    if (batchMeta?.totalBytes) formData.append('batch_total_bytes', String(batchMeta.totalBytes))
    return api.post(`/api/buckets/${bucketId}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  getProgress: (bucketId, activeOnly = true) =>
    api.get(`/api/buckets/${bucketId}/files/progress`, { params: { active_only: activeOnly } }),
  create: (bucketId, name, content) =>
    api.post(`/api/buckets/${bucketId}/files/create`, { name, content }),
  updateContent: (bucketId, fileId, content) =>
    api.put(`/api/buckets/${bucketId}/files/${fileId}/content`, { content }),
  getContent: (bucketId, fileId) =>
    api.get(`/api/buckets/${bucketId}/files/${fileId}/content`),
  list: (bucketId) => api.get(`/api/buckets/${bucketId}/files`),
  delete: (bucketId, fileId) => api.delete(`/api/buckets/${bucketId}/files/${fileId}`),
}

export const chatAPI = {
  sendMessage: async (bucketId, message, conversationId, abortSignal = null, onChunk = null, options = {}) => {
    const token = localStorage.getItem('access_token')
    const _chatT0 = performance.now()
    const _chatUrl = `${API_URL}/api/buckets/${bucketId}/chat`

    if (NET_LOG) {
      console.groupCollapsed(`%c→ POST (stream) %c${_chatUrl}`, 'color:#2196F3;font-weight:bold', 'color:#aaa')
      console.log('💬 Message  :', message.slice(0, 120) + (message.length > 120 ? '…' : ''))
      console.log('🗂  Bucket   :', bucketId)
      console.log('💬 ConvID   :', conversationId || 'new')
      console.groupEnd()
    }

    const response = await fetch(_chatUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ message, conversation_id: conversationId, ...options }),
      signal: abortSignal
    })

    const _firstByteMs = Math.round(performance.now() - _chatT0)
    if (NET_LOG) console.log(`%c← stream headers ${response.status} %c(first byte: ${_firstByteMs}ms)`, `color:${response.ok ? '#4CAF50' : '#F44336'};font-weight:bold`, 'color:#888')

    if (!response.ok) {
      // Parse error body for 402/429 upgrade/rate-limit errors
      let detail = null
      try {
        const errBody = await response.json()
        detail = errBody.detail || errBody
      } catch {}
      const err = new Error(`HTTP ${response.status}`)
      err.status = response.status
      err.detail = detail
      if (NET_LOG) console.error(`✖ Chat stream error ${response.status}:`, detail)
      throw err
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let fullResponse = ''
    let fullThinking = ''
    let sources = []
    let finalConversationId = conversationId
    let fileDraft = null
    let _chunkCount = 0

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      _chunkCount++
      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))

            // Handle new 3-phase streaming events
            if (data.type === 'phase_change') {
              if (NET_LOG) console.log(`%c⚡ phase → ${data.phase}`, 'color:#9C27B0', `(${Math.round(performance.now() - _chatT0)}ms)`)
              if (onChunk) onChunk({ type: 'phase_change', phase: data.phase })
            } else if (data.type === 'investigation') {
              if (onChunk) onChunk({ type: 'investigation', content: data.content || '' })
            } else if (data.type === 'thinking') {
              // AI's reasoning/thinking content
              fullThinking += data.content
              if (onChunk) onChunk({ type: 'thinking', content: data.content })
            } else if (data.type === 'response') {
              // AI's actual response content (new event type)
              fullResponse += data.content
              if (onChunk) onChunk({ type: 'response', content: data.content })
            } else if (data.type === 'content') {
              // Legacy content event (backward compatibility)
              fullResponse += data.content
              if (onChunk) onChunk({ type: 'response', content: data.content })
            } else if (data.type === 'searching') {
              if (NET_LOG) console.log(`%c🔍 web search%c keywords: ${JSON.stringify(data.keywords)}`, 'color:#FF9800;font-weight:bold', 'color:#aaa')
              if (onChunk) onChunk({ type: 'searching', keywords: data.keywords })
            } else if (data.type === 'done') {
              // Final event with cleaned message, sources and metadata
              sources = data.sources || []
              finalConversationId = data.conversation_id || conversationId
              if (data.file_draft) fileDraft = data.file_draft
              if (data.message) fullResponse = data.message
              if (data.thinking && !fullThinking) fullThinking = data.thinking
              const _totalMs = Math.round(performance.now() - _chatT0)
              if (NET_LOG) {
                console.groupCollapsed(`%c✔ stream done%c  ${_totalMs}ms  ${_chunkCount} chunks  ${sources.length} sources`, 'color:#4CAF50;font-weight:bold', 'color:#888')
                console.log('⏱  Total     :', `${_totalMs}ms`, _totalMs > 10000 ? '🔴 VERY SLOW' : _totalMs > 5000 ? '🟡 SLOW' : '🟢')
                console.log('📦 Chunks    :', _chunkCount)
                console.log('🔗 Sources   :', sources)
                console.log('💬 ConvID    :', finalConversationId)
                console.log('📝 Res length:', fullResponse.length, 'chars')
                console.groupEnd()
              }
              if (onChunk) onChunk({ type: 'done', message: fullResponse, sources, thinking: fullThinking })
            } else if (data.type === 'error') {
              if (NET_LOG) console.error('✖ Stream error event:', data.error)
              throw new Error(data.error)
            }
          } catch (parseError) {
            // Skip malformed JSON lines
            console.warn('Failed to parse SSE line:', line, parseError)
          }
        }
      }
    }

    // Return response with thinking content
    return {
      data: {
        message: fullResponse.trim(),
        sources,
        thinking: fullThinking,
        conversation_id: finalConversationId,
        file_draft: fileDraft
      }
    }
  },
  getConversations: (bucketId) => api.get(`/api/buckets/${bucketId}/conversations`),
  getMessages: (conversationId) => api.get(`/api/buckets/conversations/${conversationId}/messages`),
}

export const notificationsAPI = {
  list: (limit = 50, offset = 0, unreadOnly = false) =>
    api.get('/api/notifications', { params: { limit, offset, unread_only: unreadOnly } }),
  getUnreadCount: () => api.get('/api/notifications/unread-count'),
  markAsRead: (notificationId) => api.patch(`/api/notifications/${notificationId}/read`),
  markAllAsRead: () => api.patch('/api/notifications/mark-all-read'),
  delete: (notificationId) => api.delete(`/api/notifications/${notificationId}`),
  deleteAllRead: () => api.delete('/api/notifications/delete-all-read'),
}

export const teamAPI = {
  listMembers: () => api.get('/api/team/members'),
  getMember: (memberId) => api.get(`/api/team/members/${memberId}`),
  addMember: (name, realEmail, password, color) =>
    api.post('/api/team/members', { name, real_email: realEmail, password, color }),
  updateMember: (memberId, data) => api.patch(`/api/team/members/${memberId}`, data),
  removeMember: (memberId) => api.delete(`/api/team/members/${memberId}`),
  getMemberBuckets: (memberId) => api.get(`/api/team/members/${memberId}/buckets`),
  assignBuckets: (memberId, permissions) =>
    api.post(`/api/team/members/${memberId}/buckets`, { permissions }),
  removeBucketAccess: (memberId, bucketId) =>
    api.delete(`/api/team/members/${memberId}/buckets/${bucketId}`),
  getActivity: (memberId = null, bucketId = null, limit = 50) => {
    const params = { limit }
    if (memberId) params.member_id = memberId
    if (bucketId) params.bucket_id = bucketId
    return api.get('/api/team/activity', { params })
  },
  getMyTeamInfo: () => api.get('/api/team/me'),
}

export const stripeAPI = {
  getPrices: () => api.get('/api/stripe/prices'),
  createCheckout: (plan, successUrl = null, cancelUrl = null) =>
    api.post('/api/stripe/checkout', { plan, success_url: successUrl, cancel_url: cancelUrl }),
  getSubscription: () => api.get('/api/stripe/subscription'),
  getPortal: () => api.get('/api/stripe/portal'),
  getUsage: () => api.get('/api/stripe/usage'),
  cancelSubscription: () => api.post('/api/stripe/cancel'),
  reactivateSubscription: () => api.post('/api/stripe/reactivate'),
}

export default api
