import { createContext, useContext, useState, useEffect } from 'react'
import { authAPI } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check for existing session
    const storedUser = localStorage.getItem('user')
    const token = localStorage.getItem('access_token')
    
    if (storedUser && token) {
      setUser(JSON.parse(storedUser))
    }
    setLoading(false)
  }, [])

  const signup = async (email, password, fullName) => {
    try {
      const response = await authAPI.signup(email, password, fullName)
      const data = response.data
      
      if (data.success) {
        return { success: true, message: data.message }
      }
      return { success: false, message: data.message }
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.detail || 'Signup failed' 
      }
    }
  }

  const login = async (email, password) => {
    try {
      const response = await authAPI.login(email, password)
      const data = response.data
      
      if (data.success && data.session) {
        // Store tokens and user
        localStorage.setItem('access_token', data.session.access_token)
        localStorage.setItem('refresh_token', data.session.refresh_token)
        localStorage.setItem('user', JSON.stringify(data.user))
        
        setUser(data.user)
        return { success: true }
      }
      return { success: false, message: data.message }
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.detail || 'Login failed' 
      }
    }
  }

  const forgotPassword = async (email) => {
    try {
      const response = await authAPI.forgotPassword(email)
      return { success: true, message: response.data.message }
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.detail || 'Failed to send reset email' 
      }
    }
  }

  const logout = async () => {
    try {
      await authAPI.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      setUser(null)
    }
  }

  const value = {
    user,
    loading,
    signup,
    login,
    forgotPassword,
    logout,
    isAuthenticated: !!user,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
