import { useEffect, useRef } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:7223'
const POLL_INTERVAL = 4000 // ms

/**
 * Dev-only hook: polls /dev/errors and prints new backend errors to the browser console.
 * Completely inactive in production builds.
 */
export default function useDevErrorTracker() {
  const seenIds = useRef(new Set())

  useEffect(() => {
    if (!import.meta.env.DEV) return

    console.info(
      '%c[AIveilix] Backend error tracker active — polling /dev/errors every 4s',
      'color: #2DFFB7; font-weight: bold;'
    )

    const poll = async () => {
      try {
        const res = await fetch(`${API_URL}/dev/errors?limit=50`)
        if (!res.ok) return
        const { errors } = await res.json()

        errors.forEach((err) => {
          if (seenIds.current.has(err.id)) return
          seenIds.current.add(err.id)

          console.groupCollapsed(
            `%c[Backend Error] ${err.type}: ${err.message}  [id: ${err.id}]`,
            'color: #ff4d4f; font-weight: bold;'
          )
          console.error('Type      :', err.type)
          console.error('Message   :', err.message)
          console.error('Time      :', err.timestamp)
          console.error('Context   :', err.context)
          console.error('Request   :', err.request)
          console.error('Traceback :\n' + err.traceback)
          console.groupEnd()
        })
      } catch {
        // Backend might be offline — silently ignore
      }
    }

    poll() // run immediately on mount
    const timer = setInterval(poll, POLL_INTERVAL)
    return () => clearInterval(timer)
  }, [])
}
