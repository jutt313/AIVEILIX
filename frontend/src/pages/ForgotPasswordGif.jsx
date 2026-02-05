import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import AuthLayout from '../components/AuthLayout'
import GlassCard from '../components/GlassCard'
import Input from '../components/Input'
import Button from '../components/Button'

export default function ForgotPasswordGif() {
  const [step, setStep] = useState(0)
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [sent, setSent] = useState(false)

  const fullEmail = 'sarah@aiveilix.com'

  useEffect(() => {
    const animateForgot = async () => {
      await new Promise(r => setTimeout(r, 900))

      setStep(1)
      for (let i = 0; i <= fullEmail.length; i++) {
        setEmail(fullEmail.slice(0, i))
        await new Promise(r => setTimeout(r, 100))
      }

      await new Promise(r => setTimeout(r, 500))

      setStep(2)
      setLoading(true)
      await new Promise(r => setTimeout(r, 1400))
      setLoading(false)
      setSent(true)
      setStep(3)
      await new Promise(r => setTimeout(r, 2000))

      setSent(false)
      setEmail('')
      setStep(0)
    }

    animateForgot()
    const interval = setInterval(animateForgot, 9000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="relative">
      <AuthLayout>
        <GlassCard>
          <AnimatePresence mode="wait">
            {sent ? (
              <motion.div
                key="sent"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                className="text-center"
              >
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
              </motion.div>
            ) : (
              <motion.div
                key="form"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
              >
                <h2 className="text-2xl font-bold text-center mb-2 dark:text-dark-text text-light-text">
                  Forgot Password?
                </h2>
                <p className="text-center mb-6 dark:text-dark-text/70 text-light-text/70">
                  No worries, we'll send you reset instructions.
                </p>

                <form onSubmit={(e) => e.preventDefault()}>
                  <motion.div
                    animate={step >= 1 ? { scale: [1, 1.02, 1] } : {}}
                    transition={{ duration: 0.3 }}
                  >
                    <Input
                      label="Email"
                      type="email"
                      placeholder="you@example.com"
                      value={email}
                      onChange={() => {}}
                      icon={
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                        </svg>
                      }
                    />
                  </motion.div>

                  <div className="mt-6">
                    <motion.div
                      animate={step >= 2 ? { scale: [1, 0.98, 1] } : {}}
                      transition={{ duration: 0.2 }}
                    >
                      <Button type="submit" loading={loading}>
                        Send Reset Link
                      </Button>
                    </motion.div>
                  </div>
                </form>

                <p className="mt-6 text-center text-sm dark:text-dark-text/70 text-light-text/70">
                  Remember your password?{' '}
                  <Link to="/login" className="dark:text-dark-accent text-light-accent hover:underline font-medium">
                    Sign in
                  </Link>
                </p>
              </motion.div>
            )}
          </AnimatePresence>
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
            Animated Reset Preview • Auto-loops every 9s
          </p>
        </div>
      </motion.div>
    </div>
  )
}
