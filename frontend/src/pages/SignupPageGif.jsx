import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import AuthLayout from '../components/AuthLayout'
import GlassCard from '../components/GlassCard'
import Input from '../components/Input'
import Button from '../components/Button'

export default function SignupPageGif() {
  const [step, setStep] = useState(0)
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: ''
  })
  const [agreeToTerms, setAgreeToTerms] = useState(false)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })

  const fullName = 'Sarah Mitchell'
  const fullEmail = 'sarah@aiveilix.com'
  const fullPassword = '••••••••'

  useEffect(() => {
    const animateSignup = async () => {
      await new Promise(r => setTimeout(r, 1000))

      setStep(1)
      for (let i = 0; i <= fullName.length; i++) {
        setFormData(prev => ({ ...prev, fullName: fullName.slice(0, i) }))
        await new Promise(r => setTimeout(r, 90))
      }

      await new Promise(r => setTimeout(r, 350))

      setStep(2)
      for (let i = 0; i <= fullEmail.length; i++) {
        setFormData(prev => ({ ...prev, email: fullEmail.slice(0, i) }))
        await new Promise(r => setTimeout(r, 100))
      }

      await new Promise(r => setTimeout(r, 350))

      setStep(3)
      for (let i = 0; i <= fullPassword.length; i++) {
        setFormData(prev => ({ ...prev, password: fullPassword.slice(0, i) }))
        await new Promise(r => setTimeout(r, 80))
      }

      await new Promise(r => setTimeout(r, 300))

      setStep(4)
      for (let i = 0; i <= fullPassword.length; i++) {
        setFormData(prev => ({ ...prev, confirmPassword: fullPassword.slice(0, i) }))
        await new Promise(r => setTimeout(r, 80))
      }

      await new Promise(r => setTimeout(r, 400))

      setStep(5)
      setAgreeToTerms(true)

      await new Promise(r => setTimeout(r, 450))

      setStep(6)
      setLoading(true)
      await new Promise(r => setTimeout(r, 1500))

      setLoading(false)
      setMessage({ type: 'success', text: 'Account created! Please check your email to verify.' })
      setStep(7)
      await new Promise(r => setTimeout(r, 2000))

      setMessage({ type: '', text: '' })
      setAgreeToTerms(false)
      setFormData({ fullName: '', email: '', password: '', confirmPassword: '' })
      setStep(0)
    }

    animateSignup()
    const interval = setInterval(animateSignup, 10000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="relative">
      <AuthLayout lightConfig="signup">
        <GlassCard>
          <h2 className="text-2xl font-bold text-center mb-6 dark:text-dark-text text-light-text">
            Create Account
          </h2>

          <AnimatePresence>
            {message.text && (
              <motion.div
                initial={{ opacity: 0, y: -6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -6 }}
                className={`mb-4 p-3 rounded-lg text-sm text-center ${
                  message.type === 'success'
                    ? 'bg-green-500/10 border border-green-500/20 text-green-400'
                    : 'bg-red-500/10 border border-red-500/20 text-red-400'
                }`}
              >
                {message.text}
              </motion.div>
            )}
          </AnimatePresence>

          <form onSubmit={(e) => e.preventDefault()}>
            <motion.div
              animate={step >= 1 ? { scale: [1, 1.02, 1] } : {}}
              transition={{ duration: 0.3 }}
            >
              <Input
                label="Full Name"
                type="text"
                name="fullName"
                placeholder="John Doe"
                value={formData.fullName}
                onChange={() => {}}
                icon={
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                }
              />
            </motion.div>

            <motion.div
              animate={step >= 2 ? { scale: [1, 1.02, 1] } : {}}
              transition={{ duration: 0.3 }}
            >
              <Input
                label="Email"
                type="email"
                name="email"
                placeholder="you@example.com"
                value={formData.email}
                onChange={() => {}}
                icon={
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                  </svg>
                }
              />
            </motion.div>

            <motion.div
              animate={step >= 3 ? { scale: [1, 1.02, 1] } : {}}
              transition={{ duration: 0.3 }}
            >
              <Input
                label="Password"
                type="password"
                name="password"
                placeholder="••••••••"
                value={formData.password}
                onChange={() => {}}
                icon={
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                }
              />
            </motion.div>

            <motion.div
              animate={step >= 4 ? { scale: [1, 1.02, 1] } : {}}
              transition={{ duration: 0.3 }}
            >
              <Input
                label="Confirm Password"
                type="password"
                name="confirmPassword"
                placeholder="••••••••"
                value={formData.confirmPassword}
                onChange={() => {}}
                icon={
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                }
              />
            </motion.div>

            <motion.label
              animate={step >= 5 ? { scale: [1, 1.01, 1] } : {}}
              transition={{ duration: 0.2 }}
              className="mt-4 flex items-start gap-3 cursor-pointer group"
            >
              <input
                type="checkbox"
                checked={agreeToTerms}
                onChange={() => {}}
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
            </motion.label>

            <div className="mt-6">
              <motion.div
                animate={step >= 6 ? { scale: [1, 0.98, 1] } : {}}
                transition={{ duration: 0.2 }}
              >
                <Button type="submit" loading={loading} disabled={!agreeToTerms}>
                  Create Account
                </Button>
              </motion.div>
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

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1 }}
        className="absolute bottom-6 left-1/2 -translate-x-1/2 z-50"
      >
        <div className="px-6 py-3 bg-black/80 backdrop-blur-sm border border-white/10 rounded-full shadow-lg">
          <p className="text-sm text-gray-300 flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#2DFFB7] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-[#2DFFB7]"></span>
            </span>
            Animated Signup Preview • Auto-loops every 10s
          </p>
        </div>
      </motion.div>
    </div>
  )
}
