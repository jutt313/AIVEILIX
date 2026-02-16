import { createContext, useContext, useState, useEffect } from 'react'
import { authAPI } from '../services/api'
import { supabase } from '../lib/supabase'

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

    // Listen for OAuth sign-in (Google redirect lands here with hash tokens)
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (event === 'SIGNED_IN' && session && !localStorage.getItem('access_token')) {
        localStorage.setItem('access_token', session.access_token)
        localStorage.setItem('refresh_token', session.refresh_token)

        const userData = {
          id: session.user.id,
          email: session.user.email,
          full_name: session.user.user_metadata?.full_name || session.user.user_metadata?.name || '',
        }

        try {
          const meRes = await authAPI.getMe()
          const meData = meRes.data
          userData.is_team_member = meData.is_team_member || false
          userData.team_owner_id = meData.team_owner_id || null
          userData.team_member_id = meData.team_member_id || null
          userData.team_member_color = meData.team_member_color || null
          userData.team_member_name = meData.team_member_name || null
        } catch {}

        localStorage.setItem('user', JSON.stringify(userData))
        setUser(userData)
        // Redirect to dashboard
        window.location.href = '/dashboard'
      }
    })

    return () => subscription.unsubscribe()
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

        // Fetch team info from /me endpoint
        try {
          const meRes = await authAPI.getMe()
          const meData = meRes.data
          const enrichedUser = {
            ...data.user,
            is_team_member: meData.is_team_member || false,
            team_owner_id: meData.team_owner_id || null,
            team_member_id: meData.team_member_id || null,
            team_member_color: meData.team_member_color || null,
            team_member_name: meData.team_member_name || null,
          }
          localStorage.setItem('user', JSON.stringify(enrichedUser))
          setUser(enrichedUser)
        } catch {
          localStorage.setItem('user', JSON.stringify(data.user))
          setUser(data.user)
        }

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

  const signInWithGoogle = async () => {
    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
        },
      })
      if (error) {
        return { success: false, message: error.message }
      }
      return { success: true }
    } catch (error) {
      return { success: false, message: error.message || 'Google sign-in failed' }
    }
  }

  const handleOAuthCallback = async () => {
    try {
      const { data, error } = await supabase.auth.getSession()
      if (error) throw error
      if (data.session) {
        localStorage.setItem('access_token', data.session.access_token)
        localStorage.setItem('refresh_token', data.session.refresh_token)

        const userData = {
          id: data.session.user.id,
          email: data.session.user.email,
          full_name: data.session.user.user_metadata?.full_name || data.session.user.user_metadata?.name || '',
        }

        // Enrich with team info
        try {
          const meRes = await authAPI.getMe()
          const meData = meRes.data
          userData.is_team_member = meData.is_team_member || false
          userData.team_owner_id = meData.team_owner_id || null
          userData.team_member_id = meData.team_member_id || null
          userData.team_member_color = meData.team_member_color || null
          userData.team_member_name = meData.team_member_name || null
        } catch {}

        localStorage.setItem('user', JSON.stringify(userData))
        setUser(userData)
        return { success: true }
      }
      return { success: false, message: 'No session found' }
    } catch (error) {
      return { success: false, message: error.message || 'OAuth callback failed' }
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
    signInWithGoogle,
    handleOAuthCallback,
    forgotPassword,
    logout,
    isAuthenticated: !!user,
    isTeamMember: user?.is_team_member || false,
    teamOwnerColor: user?.team_member_color || null,
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
