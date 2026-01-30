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
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
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
  list: (bucketId) => api.get(`/api/buckets/${bucketId}/files`),
  delete: (bucketId, fileId) => api.delete(`/api/buckets/${bucketId}/files/${fileId}`),
}

export const chatAPI = {
  sendMessage: async (bucketId, message, conversationId, abortSignal = null, onChunk = null) => {
    const token = localStorage.getItem('access_token')
    const response = await fetch(`${API_URL}/api/buckets/${bucketId}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ message, conversation_id: conversationId }),
      signal: abortSignal
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let fullMessage = ''
    let sources = []
    let finalConversationId = conversationId

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6))

          if (data.type === 'content') {
            fullMessage += data.content
            if (onChunk) onChunk(data.content)
          } else if (data.type === 'done') {
            sources = data.sources || []
            finalConversationId = data.conversation_id || conversationId
          } else if (data.type === 'error') {
            throw new Error(data.error)
          }
        }
      }
    }

    return {
      data: {
        message: fullMessage,
        sources,
        conversation_id: finalConversationId
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

export default api
