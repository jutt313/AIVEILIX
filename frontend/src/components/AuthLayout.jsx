import { useEffect, useState } from 'react'

export default function AuthLayout({ children, lightConfig = 'login' }) {
  const [isDark, setIsDark] = useState(true)

  useEffect(() => {
    // Check system preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    setIsDark(prefersDark)
    document.documentElement.classList.toggle('dark', prefersDark)
  }, [])

  // Light configurations: 'login' or 'signup'
  const lights = {
    login: {
      topLeft: { color: '#2DFFB7', transform: 'translate(-50%, -50%)' }, // mint from top-left corner
      bottomRight: { color: '#1FE0A5', transform: 'translate(50%, 50%)' } // green from bottom-right corner
    },
    signup: {
      topRight: { color: '#1FE0A5', transform: 'translate(50%, -50%)' }, // green from top-right corner
      bottomLeft: { color: '#2DFFB7', transform: 'translate(-50%, 50%)' } // mint from bottom-left corner
    }
  }

  const currentLights = lights[lightConfig] || lights.login

  return (
    <div className={`h-screen overflow-hidden relative ${isDark ? 'dark' : ''}`}>
      {/* Fixed Background – covers viewport, no scroll */}
      <div
        className="fixed inset-0 -z-10"
        style={{ backgroundColor: isDark ? '#050B0D' : '#E5F2ED' }}
      />

      {/* Corner Light Effects */}
      {Object.entries(currentLights).map(([key, light]) => {
        const isTop = key.includes('top')
        const isLeft = key.includes('Left')
        const isRight = key.includes('Right')
        const isBottom = key.includes('bottom')
        
        const positionClasses = [
          isTop ? 'top-0' : '',
          isBottom ? 'bottom-0' : '',
          isLeft ? 'left-0' : '',
          isRight ? 'right-0' : ''
        ].filter(Boolean).join(' ')

        return (
          <div
            key={key}
            className={`fixed w-[600px] h-[600px] blur-3xl opacity-40 -z-[1] ${positionClasses}`}
            style={{
              background: `radial-gradient(ellipse, ${light.color} 0%, transparent 80%)`,
              transform: light.transform
            }}
          />
        )
      })}

      {/* Content – fixed viewport, no scroll */}
      <div className="relative z-10 h-screen flex flex-col items-center justify-center px-4 py-6 overflow-hidden">
        {/* Logo */}
        <div className="shrink-0 mb-6 text-center">
          <img
            src="/logo-with-name..png"
            alt="AIveilix"
            className="h-14 w-auto max-w-[280px] object-contain mx-auto"
          />
          <p 
            className="mt-2 text-sm"
            style={{ color: isDark ? '#E6F1F5' : '#062A33', opacity: 0.7 }}
          >
            Your Knowledge Bucket Platform
          </p>
        </div>

        {/* Card Container */}
        <div className="w-full max-w-md shrink-0">{children}</div>
      </div>
    </div>
  )
}
