import { useState } from 'react'
import { Link } from 'react-router-dom'
import AuthLayout from '../components/AuthLayout'
import GlassCard from '../components/GlassCard'
import Input from '../components/Input'
import Button from '../components/Button'
import { useAuth } from '../context/AuthContext'

export default function ForgotPassword() {
  const { forgotPassword } = useAuth()
  
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [sent, setSent] = useState(false)

  const validate = () => {
    if (!email) {
      setError('Email is required')
      return false
    }
    if (!/\S+@\S+\.\S+/.test(email)) {
      setError('Invalid email')
      return false
    }
    return true
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!validate()) return

    setLoading(true)
    setError('')

    try {
      const result = await forgotPassword(email)
      if (result.success) {
        setSent(true)
      } else {
        setError(result.message || 'Failed to send reset email')
      }
    } catch (error) {
      setError(error.message || 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout>
      <GlassCard>
        {sent ? (
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-dark-accent/20 flex items-center justify-center">
              <svg className="w-8 h-8 text-dark-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold mb-2 dark:text-dark-text text-light-text">
              Check Your Email
            </h2>
            <p className="dark:text-dark-text/70 text-light-text/70 mb-6">
              We've sent a password reset link to<br />
              <span className="dark:text-dark-accent text-light-accent font-medium">{email}</span>
            </p>
            <Link to="/login">
              <Button variant="secondary">
                Back to Login
              </Button>
            </Link>
          </div>
        ) : (
          <>
            <h2 className="text-2xl font-bold text-center mb-2 dark:text-dark-text text-light-text">
              Forgot Password?
            </h2>
            <p className="text-center mb-6 dark:text-dark-text/70 text-light-text/70">
              No worries, we'll send you reset instructions.
            </p>

            {error && (
              <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm text-center">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <Input
                label="Email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value)
                  setError('')
                }}
                error={error && !email ? error : ''}
                icon={
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                  </svg>
                }
              />

              <div className="mt-6">
                <Button type="submit" loading={loading}>
                  Send Reset Link
                </Button>
              </div>
            </form>

            <p className="mt-6 text-center text-sm dark:text-dark-text/70 text-light-text/70">
              Remember your password?{' '}
              <Link to="/login" className="dark:text-dark-accent text-light-accent hover:underline font-medium">
                Sign in
              </Link>
            </p>
          </>
        )}
      </GlassCard>
    </AuthLayout>
  )
}
