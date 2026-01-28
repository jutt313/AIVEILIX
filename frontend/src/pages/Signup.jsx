import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AuthLayout from '../components/AuthLayout'
import GlassCard from '../components/GlassCard'
import Input from '../components/Input'
import Button from '../components/Button'
import { useAuth } from '../context/AuthContext'

export default function Signup() {
  const navigate = useNavigate()
  const { signup } = useAuth()
  
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
