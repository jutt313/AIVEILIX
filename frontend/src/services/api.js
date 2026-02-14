import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:7223'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const url = error.config?.url || ''
      // Don't redirect for auth endpoints (login/signup) or if already on login page
      const isAuthEndpoint = url.includes('/api/auth/login') || url.includes('/api/auth/signup')
      const isOnLoginPage = window.location.pathname === '/login' || window.location.pathname === '/signup'
      if (!isAuthEndpoint && !isOnLoginPage) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        window.location.href = '/login'
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
  upload: (bucketId, file, folderPath = null) => {
    const formData = new FormData()
    formData.append('file', file)
    if (folderPath) {
      formData.append('folder_path', folderPath)
    }
    return api.post(`/api/buckets/${bucketId}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
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
    const response = await fetch(`${API_URL}/api/buckets/${bucketId}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ message, conversation_id: conversationId, ...options }),
      signal: abortSignal
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let fullResponse = ''
    let fullThinking = ''
    let sources = []
    let finalConversationId = conversationId
    let fileDraft = null

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))

            // Handle new 3-phase streaming events
            if (data.type === 'phase_change') {
              // Signal phase transition: thinking -> response
              if (onChunk) onChunk({ type: 'phase_change', phase: data.phase })
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
              // AI is searching the web with keywords
              if (onChunk) onChunk({ type: 'searching', keywords: data.keywords })
            } else if (data.type === 'done') {
              // Final event with cleaned message, sources and metadata
              sources = data.sources || []
              finalConversationId = data.conversation_id || conversationId
              if (data.file_draft) {
                fileDraft = data.file_draft
              }
              // Use cleaned message from server (removes [[SOURCES:...]] line)
              if (data.message) {
                fullResponse = data.message
              }
              // Include thinking from done event if not already captured
              if (data.thinking && !fullThinking) {
                fullThinking = data.thinking
              }
              if (onChunk) onChunk({ type: 'done', message: fullResponse, sources, thinking: fullThinking })
            } else if (data.type === 'error') {
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
