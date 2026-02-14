import { useState, useEffect } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import AuthLayout from '../components/AuthLayout'
import GlassCard from '../components/GlassCard'
import Input from '../components/Input'
import Button from '../components/Button'
import { authAPI } from '../services/api'
import { config } from '../config'

const API_URL = config.apiUrl

export default function OAuthAuthorize() {
  const [searchParams] = useSearchParams()
  const [step, setStep] = useState('login') // login | consent | error
  const [formData, setFormData] = useState({ email: '', password: '' })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [userToken, setUserToken] = useState(null)

  // OAuth params from URL
  const oauthParams = {
    client_id: searchParams.get('client_id'),
    redirect_uri: searchParams.get('redirect_uri'),
    scope: searchParams.get('scope') || 'read:buckets read:files query chat',
    state: searchParams.get('state'),
    response_type: searchParams.get('response_type'),
    code_challenge: searchParams.get('code_challenge'),
    code_challenge_method: searchParams.get('code_challenge_method'),
    resource: searchParams.get('resource'),
  }

  // Check if user is already logged in
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      setUserToken(token)
      setStep('consent')
    }
  }, [])

  // Validate OAuth params
  useEffect(() => {
    if (!oauthParams.client_id || !oauthParams.redirect_uri) {
      setStep('error')
      setMessage('Missing required OAuth parameters (client_id, redirect_uri)')
    }
  }, [])

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
    setErrors({ ...errors, [e.target.name]: '' })
  }

  const validate = () => {
    const newErrors = {}
    if (!formData.email) newErrors.email = 'Email is required'
    else if (!/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = 'Invalid email'
    if (!formData.password) newErrors.password = 'Password is required'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    if (!validate()) return

    setLoading(true)
    setMessage('')

    try {
      const response = await authAPI.login(formData.email, formData.password)
      const token = response.data?.access_token || response.data?.session?.access_token
      if (token) {
        setUserToken(token)
        setStep('consent')
      } else {
        setMessage('Login failed - no token received')
      }
    } catch (error) {
      setMessage(error.response?.data?.detail || error.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async () => {
    setLoading(true)
    setMessage('')

    try {
      // Submit approval to backend via form POST
      const form = document.createElement('form')
      form.method = 'POST'
      form.action = `${API_URL}/mcp/server/oauth/approve`

      const fields = {
        client_id: oauthParams.client_id,
        redirect_uri: oauthParams.redirect_uri,
        scope: oauthParams.scope,
        access_token: userToken,
      }
      if (oauthParams.state) fields.state = oauthParams.state
      if (oauthParams.code_challenge) fields.code_challenge = oauthParams.code_challenge
      if (oauthParams.code_challenge_method) fields.code_challenge_method = oauthParams.code_challenge_method
      if (oauthParams.resource) fields.resource = oauthParams.resource

      for (const [key, value] of Object.entries(fields)) {
        const input = document.createElement('input')
        input.type = 'hidden'
        input.name = key
        input.value = value
        form.appendChild(input)
      }

      document.body.appendChild(form)
      form.submit()
    } catch (error) {
      setMessage('Failed to approve authorization')
      setLoading(false)
    }
  }

  const handleDeny = () => {
    // Redirect back with access_denied error
    const params = new URLSearchParams({ error: 'access_denied', error_description: 'User denied authorization' })
    if (oauthParams.state) params.set('state', oauthParams.state)
    window.location.href = `${oauthParams.redirect_uri}?${params.toString()}`
  }

  const scopeLabels = {
    'read:buckets': 'View your buckets',
    'read:files': 'Read your files',
    'query': 'Search your documents',
    'chat': 'Chat with your documents',
  }

  if (step === 'error') {
    return (
      <AuthLayout>
        <GlassCard>
          <h2 className="text-2xl font-bold text-center mb-6 dark:text-dark-text text-light-text">
            Authorization Error
          </h2>
          <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm text-center">
            {message}
          </div>
          <Link to="/" className="block text-center dark:text-dark-accent text-light-accent hover:underline text-sm">
            Go to Home
          </Link>
        </GlassCard>
      </AuthLayout>
    )
  }

  if (step === 'consent') {
    const scopes = oauthParams.scope.split(' ').filter(Boolean)
    return (
      <AuthLayout>
        <GlassCard>
          <h2 className="text-2xl font-bold text-center mb-2 dark:text-dark-text text-light-text">
            Authorize Access
          </h2>
          <p className="text-center text-sm dark:text-dark-text/60 text-light-text/60 mb-6">
            An application wants to access your AIveilix account
          </p>

          {message && (
            <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm text-center">
              {message}
            </div>
          )}

          <div className="mb-6 p-4 rounded-lg dark:bg-white/5 bg-black/5">
            <p className="text-sm font-medium dark:text-dark-text text-light-text mb-3">
              This app is requesting permission to:
            </p>
            <ul className="space-y-2">
              {scopes.map((scope) => (
                <li key={scope} className="flex items-center gap-2 text-sm dark:text-dark-text/80 text-light-text/80">
                  <svg className="w-4 h-4 dark:text-dark-accent text-light-accent flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  {scopeLabels[scope] || scope}
                </li>
              ))}
            </ul>
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleDeny}
              className="flex-1 py-2.5 px-4 rounded-lg border dark:border-white/10 border-black/10 dark:text-dark-text/70 text-light-text/70 hover:dark:bg-white/5 hover:bg-black/5 transition-colors text-sm font-medium"
            >
              Deny
            </button>
            <Button onClick={handleApprove} loading={loading} className="flex-1">
              Authorize
            </Button>
          </div>
        </GlassCard>
      </AuthLayout>
    )
  }

  // Login step
  return (
    <AuthLayout lightConfig="login">
      <GlassCard>
        <h2 className="text-2xl font-bold text-center mb-2 dark:text-dark-text text-light-text">
          Sign in to Authorize
        </h2>
        <p className="text-center text-sm dark:text-dark-text/60 text-light-text/60 mb-6">
          Log in to grant access to your AIveilix account
        </p>

        {message && (
          <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm text-center">
            {message}
          </div>
        )}

        <form onSubmit={handleLogin}>
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

          <Button type="submit" loading={loading} className="mt-4">
            Sign In & Continue
          </Button>
        </form>

        <p className="mt-6 text-center text-sm dark:text-dark-text/70 text-light-text/70">
          Don't have an account?{' '}
          <Link to="/signup" className="dark:text-dark-accent text-light-accent hover:underline font-medium">
            Create one
          </Link>
        </p>
      </GlassCard>
    </AuthLayout>
  )
}
