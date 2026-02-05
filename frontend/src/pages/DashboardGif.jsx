import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import DashboardPreview from '../components/DashboardPreview'

export default function DashboardGif() {
  const [pulse, setPulse] = useState(false)

  useEffect(() => {
    const animate = async () => {
      setPulse(true)
      await new Promise(r => setTimeout(r, 1800))
      setPulse(false)
      await new Promise(r => setTimeout(r, 1200))
    }

    animate()
    const interval = setInterval(animate, 6000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="relative">
      <DashboardPreview />

      {/* Subtle highlight on Create Bucket button area */}
      <motion.div
        animate={pulse ? { opacity: [0, 0.6, 0], scale: [0.95, 1.05, 1.1] } : { opacity: 0 }}
        transition={{ duration: 1.8, ease: 'easeInOut' }}
        className="pointer-events-none absolute right-6 top-[92px] hidden md:block"
      >
        <div className="w-40 h-12 rounded-xl border border-[#2DFFB7]/60 shadow-[0_0_30px_rgba(45,255,183,0.25)]" />
      </motion.div>

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
            Animated Dashboard Preview • Auto-loops every 6s
          </p>
        </div>
      </motion.div>
    </div>
  )
}
