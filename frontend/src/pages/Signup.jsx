import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AuthLayout from '../components/AuthLayout'
import GlassCard from '../components/GlassCard'
import Input from '../components/Input'
import Button from '../components/Button'
import { useAuth } from '../context/AuthContext'

export default function Signup() {
  const navigate = useNavigate()
  const { signup, signInWithGoogle } = useAuth()

  const [googleLoading, setGoogleLoading] = useState(false)

  const handleGoogleSignIn = async () => {
    setGoogleLoading(true)
    setMessage({ type: '', text: '' })
    const result = await signInWithGoogle()
    if (!result.success) {
      setMessage({ type: 'error', text: result.message || 'Google sign-in failed' })
      setGoogleLoading(false)
    }
  }

  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: ''
  })
  const [agreeToTerms, setAgreeToTerms] = useState(false)
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
    setErrors({ ...errors, [e.target.name]: '' })
  }

  const validate = () => {
    const newErrors = {}
    if (!formData.fullName) newErrors.fullName = 'Name is required'
    if (!formData.email) newErrors.email = 'Email is required'
    else if (!/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = 'Invalid email'
    if (!formData.password) newErrors.password = 'Password is required'
    else if (formData.password.length < 6) newErrors.password = 'Password must be at least 6 characters'
    if (formData.password !== formData.confirmPassword) newErrors.confirmPassword = 'Passwords do not match'
    if (!agreeToTerms) newErrors.agreeToTerms = 'You must agree to the Terms and Conditions'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!validate()) return

    setLoading(true)
    setMessage({ type: '', text: '' })

    try {
      const result = await signup(formData.email, formData.password, formData.fullName)
      if (result.success) {
        setMessage({ 
          type: 'success', 
          text: 'Account created! Please check your email to verify.' 
        })
      } else {
        setMessage({ type: 'error', text: result.message || 'Signup failed' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: error.message || 'An error occurred' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout lightConfig="signup">
      <GlassCard>
        <h2 className="text-2xl font-bold text-center mb-6 dark:text-dark-text text-light-text">
          Create Account
        </h2>

        {message.text && (
          <div className={`mb-4 p-3 rounded-lg text-sm text-center ${
            message.type === 'success' 
              ? 'bg-green-500/10 border border-green-500/20 text-green-400'
              : 'bg-red-500/10 border border-red-500/20 text-red-400'
          }`}>
            {message.text}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <Input
            label="Full Name"
            type="text"
            name="fullName"
            placeholder="John Doe"
            value={formData.fullName}
            onChange={handleChange}
            error={errors.fullName}
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            }
          />

          <Input
            label="Email"
            type="email"
            name="email"
            placeholder="you@example.com"
            value={formData.email}
            onChange={handleChange}
            error={errors.email}
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
              </svg>
            }
          />

          <Input
            label="Password"
            type="password"
            name="password"
            placeholder="••••••••"
            value={formData.password}
            onChange={handleChange}
            error={errors.password}
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            }
          />

          <Input
            label="Confirm Password"
            type="password"
            name="confirmPassword"
            placeholder="••••••••"
            value={formData.confirmPassword}
            onChange={handleChange}
            error={errors.confirmPassword}
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            }
          />

          <label className="mt-4 flex items-start gap-3 cursor-pointer group">
            <input
              type="checkbox"
              checked={agreeToTerms}
              onChange={(e) => {
                setAgreeToTerms(e.target.checked)
                setErrors((prev) => ({ ...prev, agreeToTerms: '' }))
              }}
              className="mt-1 w-4 h-4 rounded border dark:border-dark-border border-light-border dark:bg-dark-bg/50 bg-light-bg/50 dark:text-dark-accent text-light-accent focus:ring-2 focus:ring-offset-0 dark:focus:ring-dark-accent/40 focus:ring-light-accent/40"
            />
            <span className="text-sm dark:text-dark-text/80 text-light-text/80 group-hover:dark:text-dark-text group-hover:text-light-text">
              By creating an account, you agree to our{' '}
              <Link to="/terms" className="dark:text-dark-accent text-light-accent hover:underline font-medium" target="_blank" rel="noopener noreferrer">
                Terms and Conditions
              </Link>
              {' '}and{' '}
              <Link to="/privacy" className="dark:text-dark-accent text-light-accent hover:underline font-medium" target="_blank" rel="noopener noreferrer">
                Privacy Policy
              </Link>
              .
            </span>
          </label>
          {errors.agreeToTerms && (
            <p className="mt-1 text-sm text-red-400" role="alert">{errors.agreeToTerms}</p>
          )}

          <div className="mt-6">
            <Button type="submit" loading={loading} disabled={!agreeToTerms}>
              Create Account
            </Button>
          </div>
        </form>

        <div className="mt-6 flex items-center gap-3">
          <div className="flex-1 h-px dark:bg-dark-border bg-light-border" />
          <span className="text-xs dark:text-dark-text/50 text-light-text/50 uppercase tracking-wider">or</span>
          <div className="flex-1 h-px dark:bg-dark-border bg-light-border" />
        </div>

        <button
          onClick={handleGoogleSignIn}
          disabled={googleLoading}
          className="mt-4 w-full flex items-center justify-center gap-3 px-6 py-3 rounded-xl border dark:border-dark-border border-light-border dark:bg-white/5 bg-white/80 hover:dark:bg-white/10 hover:bg-white transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-[1.02] active:scale-[0.98]"
        >
          {googleLoading ? (
            <svg className="animate-spin h-5 w-5 dark:text-dark-text text-light-text" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          ) : (
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" />
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
          )}
          <span className="font-medium dark:text-dark-text text-light-text">
            {googleLoading ? 'Redirecting...' : 'Continue with Google'}
          </span>
        </button>

        <p className="mt-6 text-center text-sm dark:text-dark-text/70 text-light-text/70">
          Already have an account?{' '}
          <Link to="/login" className="dark:text-dark-accent text-light-accent hover:underline font-medium">
            Sign in
          </Link>
        </p>
      </GlassCard>
    </AuthLayout>
  )
}
