import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import AuthLayout from '../components/AuthLayout'
import GlassCard from '../components/GlassCard'
import Input from '../components/Input'
import Button from '../components/Button'

export default function LoginPageGif({ embedded = false }) {
  const [step, setStep] = useState(0)
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  const fullEmail = 'user@aiveilix.com'
  const fullPassword = '••••••••••'

  useEffect(() => {
    const animateLogin = async () => {
      // Wait 1s
      await new Promise(r => setTimeout(r, 1000))

      // Step 1: Type email
      setStep(1)
      for (let i = 0; i <= fullEmail.length; i++) {
        setFormData(prev => ({ ...prev, email: fullEmail.slice(0, i) }))
        await new Promise(r => setTimeout(r, 100))
      }

      await new Promise(r => setTimeout(r, 400))

      // Step 2: Type password
      setStep(2)
      for (let i = 0; i <= fullPassword.length; i++) {
        setFormData(prev => ({ ...prev, password: fullPassword.slice(0, i) }))
        await new Promise(r => setTimeout(r, 80))
      }

      await new Promise(r => setTimeout(r, 600))

      // Step 3: Click login
      setStep(3)
      setLoading(true)
      await new Promise(r => setTimeout(r, 1500))

      // Step 4: Success
      setLoading(false)
      setSuccess(true)
      setStep(4)
      await new Promise(r => setTimeout(r, 2000))

      // Reset
      setSuccess(false)
      setFormData({ email: '', password: '' })
      setStep(0)
    }

    animateLogin()
    const interval = setInterval(animateLogin, 9000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="relative">
      <AuthLayout lightConfig="login">
        <GlassCard>
          <h2 className="text-2xl font-bold text-center mb-6 dark:text-dark-text text-light-text">
            Welcome Back
          </h2>

          {/* Success Overlay */}
          <AnimatePresence>
            {success && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                className="absolute inset-0 flex flex-col items-center justify-center bg-[#050B0D]/95 backdrop-blur-sm rounded-4xl z-50"
              >
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: 'spring', stiffness: 200, damping: 15, delay: 0.2 }}
                  className="w-20 h-20 bg-gradient-to-br from-[#2DFFB7] to-[#1FE0A5] rounded-full flex items-center justify-center mb-4"
                >
                  <svg className="w-10 h-10 text-[#050B0D]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <motion.path
                      initial={{ pathLength: 0 }}
                      animate={{ pathLength: 1 }}
                      transition={{ duration: 0.5, delay: 0.3 }}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={3}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </motion.div>
                <motion.h3
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="text-2xl font-bold text-[#2DFFB7] mb-2"
                >
                  Login Successful!
                </motion.h3>
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.5 }}
                  className="text-gray-400"
                >
                  Redirecting to dashboard...
                </motion.p>
              </motion.div>
            )}
          </AnimatePresence>

          <form onSubmit={(e) => e.preventDefault()}>
            <motion.div
              animate={step >= 1 ? { scale: [1, 1.02, 1] } : {}}
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
              animate={step >= 2 ? { scale: [1, 1.02, 1] } : {}}
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

            <div className="flex justify-end mb-6">
              <Link
                to="/forgot-password"
                className="text-sm dark:text-dark-accent text-light-accent hover:underline"
              >
                Forgot password?
              </Link>
            </div>

            <motion.div
              animate={step >= 3 ? { scale: [1, 0.98, 1] } : {}}
              transition={{ duration: 0.2 }}
            >
              <Button type="submit" loading={loading}>
                Sign In
              </Button>
            </motion.div>
          </form>

          <p className="mt-6 text-center text-sm dark:text-dark-text/70 text-light-text/70">
            Don't have an account?{' '}
            <Link to="/signup" className="dark:text-dark-accent text-light-accent hover:underline font-medium">
              Create one
            </Link>
          </p>
        </GlassCard>
      </AuthLayout>

      {/* Info Badge */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1 }}
        className={`${embedded ? 'absolute bottom-6' : 'fixed bottom-8'} left-1/2 -translate-x-1/2 z-50`}
      >
        <div className="px-6 py-3 bg-black/80 backdrop-blur-sm border border-white/10 rounded-full shadow-lg">
          <p className="text-sm text-gray-300 flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#2DFFB7] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-[#2DFFB7]"></span>
            </span>
            Animated Login Preview • Auto-loops every 9s
          </p>
        </div>
      </motion.div>
    </div>
  )
}
