import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { supabase } from '../lib/supabase'

export default function AuthCallback() {
  const navigate = useNavigate()
  const { handleOAuthCallback } = useAuth()
  const [error, setError] = useState('')

  useEffect(() => {
    // Listen for Supabase to process the URL hash tokens
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (event === 'SIGNED_IN' && session) {
        const result = await handleOAuthCallback()
        if (result.success) {
          navigate('/dashboard', { replace: true })
        } else {
          setError(result.message || 'Authentication failed')
          setTimeout(() => navigate('/login', { replace: true }), 3000)
        }
      }
    })

    // Fallback: if no event fires within 5s, try manually
    const timeout = setTimeout(async () => {
      const result = await handleOAuthCallback()
      if (result.success) {
        navigate('/dashboard', { replace: true })
      } else {
        setError('Authentication timed out')
        setTimeout(() => navigate('/login', { replace: true }), 3000)
      }
    }, 5000)

    return () => {
      subscription.unsubscribe()
      clearTimeout(timeout)
    }
  }, [])

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center dark:bg-dark-bg bg-light-bg">
        <div className="text-center">
          <p className="text-red-400 mb-2">{error}</p>
          <p className="dark:text-dark-text/60 text-light-text/60 text-sm">Redirecting to login...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center dark:bg-dark-bg bg-light-bg">
      <div className="text-center">
        <svg className="animate-spin h-8 w-8 mx-auto mb-4 dark:text-dark-accent text-light-accent" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
        <p className="dark:text-dark-text/80 text-light-text/80">Signing you in...</p>
      </div>
    </div>
  )
}
