import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'
import { stripeAPI } from '../services/api'

export default function Pricing() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { user, isAuthenticated } = useAuth()
  const { isDark, toggleTheme } = useTheme()

  const [plans, setPlans] = useState([])
  const [loading, setLoading] = useState(true)
  const [checkoutLoading, setCheckoutLoading] = useState(null)
  const [currentPlan, setCurrentPlan] = useState(null)
  const [message, setMessage] = useState(null)

  useEffect(() => {
    loadPrices()
    if (isAuthenticated) {
      loadCurrentSubscription()
    }

    // Check for payment result from URL
    const payment = searchParams.get('payment')
    if (payment === 'success') {
      setMessage({ type: 'success', text: 'Payment successful! Your subscription is now active.' })
    } else if (payment === 'canceled') {
      setMessage({ type: 'info', text: 'Payment was canceled. You can try again anytime.' })
    }
  }, [isAuthenticated, searchParams])

  const loadPrices = async () => {
    try {
      const response = await stripeAPI.getPrices()
      setPlans(response.data.plans || [])
    } catch (error) {
      console.error('Failed to load prices:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadCurrentSubscription = async () => {
    try {
      const response = await stripeAPI.getSubscription()
      setCurrentPlan(response.data.plan)
    } catch (error) {
      console.error('Failed to load subscription:', error)
    }
  }

  const handleCheckout = async (planId) => {
    if (!isAuthenticated) {
      navigate('/login?redirect=/pricing')
      return
    }

    setCheckoutLoading(planId)
    try {
      const response = await stripeAPI.createCheckout(planId)
      // Redirect to Stripe Checkout
      window.location.href = response.data.url
    } catch (error) {
      console.error('Checkout error:', error)
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Failed to start checkout' })
    } finally {
      setCheckoutLoading(null)
    }
  }

  const handleManageBilling = async () => {
    try {
      const response = await stripeAPI.getPortal()
      window.location.href = response.data.url
    } catch (error) {
      console.error('Portal error:', error)
      setMessage({ type: 'error', text: 'Failed to open billing portal' })
    }
  }

  const formatPrice = (price) => {
    return `$${price.toFixed(2)}`
  }

  const isCurrentPlan = (planId) => {
    return currentPlan === planId
  }

  const isPlanUpgrade = (planId) => {
    const order = { free_trial: 0, starter: 1, pro: 2, premium: 3 }
    return order[planId] > (order[currentPlan] || 0)
  }

  return (
    <div className={`min-h-screen ${isDark ? 'bg-[#050B0D]' : 'bg-[#E5F2ED]'}`}>
      {/* Header */}
      <header className="relative z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <button
            onClick={() => navigate(isAuthenticated ? '/dashboard' : '/')}
            className={`text-2xl font-bold ${isDark ? 'text-dark-accent' : 'text-light-accent'}`}
          >
            AIveilix
          </button>

          <div className="flex items-center gap-3">
            {isAuthenticated ? (
              <button
                onClick={() => navigate('/dashboard')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  isDark
                    ? 'bg-white/10 hover:bg-white/20 text-dark-text'
                    : 'bg-black/10 hover:bg-black/20 text-light-text'
                }`}
              >
                Dashboard
              </button>
            ) : (
              <button
                onClick={() => navigate('/login')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  isDark
                    ? 'bg-dark-accent text-dark-bg hover:opacity-90'
                    : 'bg-light-accent text-white hover:opacity-90'
                }`}
              >
                Sign In
              </button>
            )}

            <button
              onClick={toggleTheme}
              className={`p-2 rounded-lg transition-colors ${
                isDark
                  ? 'hover:bg-white/10 text-dark-text/70'
                  : 'hover:bg-black/10 text-light-text/70'
              }`}
            >
              {isDark ? (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"/>
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"/>
                </svg>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-12">
        {/* Message Banner */}
        {message && (
          <div className={`mb-8 p-4 rounded-lg ${
            message.type === 'success' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
            message.type === 'error' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
            'bg-blue-500/20 text-blue-400 border border-blue-500/30'
          }`}>
            {message.text}
          </div>
        )}

        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className={`text-4xl md:text-5xl font-bold mb-4 ${isDark ? 'text-dark-text' : 'text-light-text'}`}>
            Simple, Transparent Pricing
          </h1>
          <p className={`text-lg ${isDark ? 'text-dark-text/70' : 'text-light-text/70'}`}>
            Start with a 14-day free trial. No credit card required.
          </p>
        </div>

        {/* Free Trial Banner */}
        <div className={`mb-12 p-6 rounded-2xl text-center ${
          isDark ? 'bg-dark-accent/10 border border-dark-accent/30' : 'bg-light-accent/10 border border-light-accent/30'
        }`}>
          <div className={`text-xl font-semibold mb-2 ${isDark ? 'text-dark-accent' : 'text-light-accent'}`}>
            14-Day Free Trial
          </div>
          <p className={`${isDark ? 'text-dark-text/70' : 'text-light-text/70'}`}>
            1GB storage, 50 documents, 10MB max file size, 50 API calls/day
          </p>
        </div>

        {/* Pricing Cards */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className={`animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 ${isDark ? 'border-dark-accent' : 'border-light-accent'}`}></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {plans.map((plan) => (
              <div
                key={plan.id}
                className={`relative rounded-2xl p-8 transition-all ${
                  plan.popular
                    ? isDark
                      ? 'bg-dark-accent/10 border-2 border-dark-accent shadow-lg shadow-dark-accent/20'
                      : 'bg-light-accent/10 border-2 border-light-accent shadow-lg shadow-light-accent/20'
                    : isDark
                      ? 'bg-white/5 border border-white/10'
                      : 'bg-white border border-black/10'
                }`}
              >
                {/* Popular Badge */}
                {plan.popular && (
                  <div className={`absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full text-sm font-medium ${
                    isDark ? 'bg-dark-accent text-dark-bg' : 'bg-light-accent text-white'
                  }`}>
                    Most Popular
                  </div>
                )}

                {/* Current Plan Badge */}
                {isCurrentPlan(plan.id) && (
                  <div className={`absolute -top-4 right-4 px-3 py-1 rounded-full text-xs font-medium ${
                    isDark ? 'bg-white/20 text-dark-text' : 'bg-black/20 text-light-text'
                  }`}>
                    Current Plan
                  </div>
                )}

                {/* Plan Name */}
                <h3 className={`text-2xl font-bold mb-2 ${isDark ? 'text-dark-text' : 'text-light-text'}`}>
                  {plan.name}
                </h3>

                {/* Price */}
                <div className="mb-6">
                  <span className={`text-4xl font-bold ${isDark ? 'text-dark-text' : 'text-light-text'}`}>
                    {formatPrice(plan.price)}
                  </span>
                  <span className={`text-sm ${isDark ? 'text-dark-text/50' : 'text-light-text/50'}`}>
                    /{plan.interval}
                  </span>
                </div>

                {/* Features */}
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start gap-3">
                      <svg
                        className={`w-5 h-5 mt-0.5 flex-shrink-0 ${isDark ? 'text-dark-accent' : 'text-light-accent'}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span className={`${isDark ? 'text-dark-text/80' : 'text-light-text/80'}`}>
                        {feature}
                      </span>
                    </li>
                  ))}
                </ul>

                {/* CTA Button */}
                {isCurrentPlan(plan.id) ? (
                  <button
                    onClick={handleManageBilling}
                    className={`w-full py-3 rounded-xl font-medium transition-all ${
                      isDark
                        ? 'bg-white/10 hover:bg-white/20 text-dark-text'
                        : 'bg-black/10 hover:bg-black/20 text-light-text'
                    }`}
                  >
                    Manage Billing
                  </button>
                ) : (
                  <button
                    onClick={() => handleCheckout(plan.id)}
                    disabled={checkoutLoading === plan.id}
                    className={`w-full py-3 rounded-xl font-medium transition-all disabled:opacity-50 ${
                      plan.popular || isPlanUpgrade(plan.id)
                        ? isDark
                          ? 'bg-dark-accent text-dark-bg hover:opacity-90'
                          : 'bg-light-accent text-white hover:opacity-90'
                        : isDark
                          ? 'bg-white/10 hover:bg-white/20 text-dark-text'
                          : 'bg-black/10 hover:bg-black/20 text-light-text'
                    }`}
                  >
                    {checkoutLoading === plan.id ? (
                      <span className="flex items-center justify-center gap-2">
                        <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                        </svg>
                        Processing...
                      </span>
                    ) : isPlanUpgrade(plan.id) ? (
                      'Upgrade Now'
                    ) : (
                      'Get Started'
                    )}
                  </button>
                )}
              </div>
            ))}
          </div>
        )}

        {/* FAQ Section */}
        <div className="mt-20">
          <h2 className={`text-2xl font-bold text-center mb-8 ${isDark ? 'text-dark-text' : 'text-light-text'}`}>
            Frequently Asked Questions
          </h2>

          <div className="max-w-3xl mx-auto space-y-6">
            <div className={`p-6 rounded-xl ${isDark ? 'bg-white/5' : 'bg-white'}`}>
              <h3 className={`font-semibold mb-2 ${isDark ? 'text-dark-text' : 'text-light-text'}`}>
                What happens after my free trial ends?
              </h3>
              <p className={`${isDark ? 'text-dark-text/70' : 'text-light-text/70'}`}>
                Your documents remain safe. You can still view them but cannot upload new files or use AI chat until you upgrade.
              </p>
            </div>

            <div className={`p-6 rounded-xl ${isDark ? 'bg-white/5' : 'bg-white'}`}>
              <h3 className={`font-semibold mb-2 ${isDark ? 'text-dark-text' : 'text-light-text'}`}>
                Can I change plans anytime?
              </h3>
              <p className={`${isDark ? 'text-dark-text/70' : 'text-light-text/70'}`}>
                Yes! You can upgrade or downgrade at any time. Changes take effect on your next billing cycle.
              </p>
            </div>

            <div className={`p-6 rounded-xl ${isDark ? 'bg-white/5' : 'bg-white'}`}>
              <h3 className={`font-semibold mb-2 ${isDark ? 'text-dark-text' : 'text-light-text'}`}>
                What payment methods do you accept?
              </h3>
              <p className={`${isDark ? 'text-dark-text/70' : 'text-light-text/70'}`}>
                We accept all major credit cards (Visa, Mastercard, American Express) through Stripe secure payment.
              </p>
            </div>

            <div className={`p-6 rounded-xl ${isDark ? 'bg-white/5' : 'bg-white'}`}>
              <h3 className={`font-semibold mb-2 ${isDark ? 'text-dark-text' : 'text-light-text'}`}>
                Is there a refund policy?
              </h3>
              <p className={`${isDark ? 'text-dark-text/70' : 'text-light-text/70'}`}>
                Yes, we offer a 30-day money-back guarantee. If you are not satisfied, contact support for a full refund.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className={`mt-20 py-8 border-t ${isDark ? 'border-white/10' : 'border-black/10'}`}>
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className={`${isDark ? 'text-dark-text/50' : 'text-light-text/50'}`}>
            Powered by Stripe. Your payment information is secure.
          </p>
        </div>
      </footer>
    </div>
  )
}
