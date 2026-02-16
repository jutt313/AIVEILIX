import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTheme } from '../context/ThemeContext'
import { stripeAPI } from '../services/api'

export default function TrialBanner() {
  const { isDark } = useTheme()
  const navigate = useNavigate()
  const [usage, setUsage] = useState(null)
  const [loading, setLoading] = useState(true)
  const [dismissed, setDismissed] = useState(false)

  useEffect(() => {
    loadUsage()
    const interval = setInterval(loadUsage, 60000) // refresh every minute
    return () => clearInterval(interval)
  }, [])

  const loadUsage = async () => {
    try {
      const res = await stripeAPI.getUsage()
      setUsage(res.data)
    } catch {
      // silent
    } finally {
      setLoading(false)
    }
  }

  if (loading || !usage || dismissed) return null

  const plan = usage.plan
  const isExpired = plan === 'expired'
  const isTrial = plan === 'free_trial'
  const earlyBird = usage.early_bird_active
  const signupTime = usage.signup_time

  // Calculate trial days remaining
  let trialDaysLeft = null
  if (isTrial && usage.trial_end) {
    const end = new Date(usage.trial_end)
    const now = new Date()
    trialDaysLeft = Math.max(0, Math.ceil((end - now) / (1000 * 60 * 60 * 24)))
  }

  // Calculate 24hr bonus timer (hours left to subscribe for 2x)
  let bonusHoursLeft = null
  if (isTrial && signupTime) {
    const signup = new Date(signupTime)
    const deadline = new Date(signup.getTime() + 24 * 60 * 60 * 1000)
    const now = new Date()
    const msLeft = deadline - now
    if (msLeft > 0) {
      bonusHoursLeft = Math.floor(msLeft / (1000 * 60 * 60))
      const minsLeft = Math.floor((msLeft % (1000 * 60 * 60)) / (1000 * 60))
      bonusHoursLeft = { hours: bonusHoursLeft, minutes: minsLeft }
    }
  }

  // Don't show banner for paid plans (unless early bird active - show that)
  if (!isTrial && !isExpired && !earlyBird) return null

  // Expired trial
  if (isExpired) {
    return (
      <div className={`mb-6 p-4 rounded-2xl border ${
        isDark ? 'bg-red-500/10 border-red-500/30' : 'bg-red-50 border-red-200'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
              <p className={`font-semibold ${isDark ? 'text-red-400' : 'text-red-600'}`}>
                Your free trial has expired
              </p>
              <p className={`text-sm ${isDark ? 'text-red-400/70' : 'text-red-500/70'}`}>
                Upgrade now to continue using AIveilix
              </p>
            </div>
          </div>
          <button
            onClick={() => navigate('/pricing')}
            className="px-4 py-2 rounded-xl font-medium bg-red-500 text-white hover:bg-red-600 transition-colors"
          >
            Upgrade Now
          </button>
        </div>
      </div>
    )
  }

  // Early bird active (paid plan with 2x bonus)
  if (earlyBird && !isTrial) {
    return (
      <div className={`mb-6 p-4 rounded-2xl border ${
        isDark ? 'bg-amber-500/10 border-amber-500/30' : 'bg-amber-50 border-amber-200'
      }`}>
        <div className="flex items-center gap-3">
          <span className="text-xl">🎉</span>
          <div>
            <p className={`font-semibold ${isDark ? 'text-amber-400' : 'text-amber-600'}`}>
              Early Bird Bonus Active — 2x All Limits!
            </p>
            <p className={`text-sm ${isDark ? 'text-amber-400/70' : 'text-amber-500/70'}`}>
              You subscribed within 24 hours — enjoy double limits for your first month.
            </p>
          </div>
        </div>
      </div>
    )
  }

  // Free trial with bonus timer
  return (
    <div className={`mb-6 rounded-2xl border overflow-hidden ${
      isDark ? 'bg-dark-accent/5 border-dark-accent/20' : 'bg-light-accent/5 border-light-accent/20'
    }`}>
      <div className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 flex-1">
            {/* Trial info */}
            <div>
              <div className="flex items-center gap-2">
                <p className={`font-semibold ${isDark ? 'text-dark-text' : 'text-light-text'}`}>
                  Free Trial
                  {trialDaysLeft !== null && (
                    <span className={`ml-2 text-sm font-normal ${
                      trialDaysLeft <= 3
                        ? 'text-red-400'
                        : isDark ? 'text-dark-text/60' : 'text-light-text/60'
                    }`}>
                      — {trialDaysLeft} day{trialDaysLeft !== 1 ? 's' : ''} left
                    </span>
                  )}
                </p>
              </div>

              {/* 24hr bonus countdown */}
              {bonusHoursLeft && (
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-sm">⚡</span>
                  <p className={`text-sm font-medium ${isDark ? 'text-amber-400' : 'text-amber-600'}`}>
                    Subscribe in {bonusHoursLeft.hours}h {bonusHoursLeft.minutes}m for 2x limits on your first month!
                  </p>
                </div>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => navigate('/pricing')}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                isDark
                  ? 'bg-dark-accent text-dark-bg hover:opacity-90'
                  : 'bg-light-accent text-white hover:opacity-90'
              }`}
            >
              {bonusHoursLeft ? 'Claim 2x Bonus' : 'Upgrade'}
            </button>
            <button
              onClick={() => setDismissed(true)}
              className={`p-1.5 rounded-lg transition-colors ${
                isDark ? 'hover:bg-white/10 text-dark-text/40' : 'hover:bg-black/10 text-light-text/40'
              }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
