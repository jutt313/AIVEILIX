import { createContext, useContext, useState, useCallback, useEffect } from 'react'
import { registerToast } from '../services/api'

const ToastContext = createContext(null)

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const showToast = useCallback((message, type = 'error', onRetry = null) => {
    const id = Date.now() + Math.random()
    setToasts(prev => [...prev, { id, message, type, onRetry }])
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
    }, 4500)
  }, [])

  // Register with the axios interceptor bridge so api.js can trigger toasts
  useEffect(() => { registerToast(showToast) }, [showToast])

  const dismiss = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div
        style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          zIndex: 9999,
          display: 'flex',
          flexDirection: 'column',
          gap: '10px',
          maxWidth: '360px',
          width: '100%',
          pointerEvents: 'none',
        }}
      >
        {toasts.map(toast => (
          <ToastItem key={toast.id} toast={toast} onDismiss={dismiss} />
        ))}
      </div>
    </ToastContext.Provider>
  )
}

function ToastItem({ toast, onDismiss }) {
  const colors = {
    error:   { bg: '#1a0a0a', border: '#ef4444', icon: '✕', iconColor: '#ef4444' },
    success: { bg: '#071a12', border: '#2DFFB7', icon: '✓', iconColor: '#2DFFB7' },
    warning: { bg: '#1a1200', border: '#f59e0b', icon: '!', iconColor: '#f59e0b' },
    info:    { bg: '#0a0f1a', border: '#60a5fa', icon: 'i', iconColor: '#60a5fa' },
  }
  const c = colors[toast.type] || colors.error

  return (
    <div
      onClick={() => onDismiss(toast.id)}
      style={{
        pointerEvents: 'auto',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'flex-start',
        gap: '10px',
        padding: '12px 14px',
        borderRadius: '10px',
        border: `1px solid ${c.border}44`,
        backgroundColor: c.bg,
        backdropFilter: 'blur(12px)',
        boxShadow: `0 4px 24px rgba(0,0,0,0.5)`,
        animation: 'toastIn 0.2s ease',
        userSelect: 'none',
      }}
    >
      <span style={{
        flexShrink: 0,
        width: '20px',
        height: '20px',
        borderRadius: '50%',
        border: `1.5px solid ${c.iconColor}`,
        color: c.iconColor,
        fontSize: '11px',
        fontWeight: 700,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        marginTop: '1px',
      }}>
        {c.icon}
      </span>
      <span style={{
        flex: 1,
        fontSize: '13px',
        lineHeight: '1.5',
        color: '#E6F1F5',
      }}>
        {toast.message}
      </span>
      {toast.onRetry && (
        <span
          onClick={(e) => { e.stopPropagation(); toast.onRetry(); onDismiss(toast.id) }}
          style={{
            flexShrink: 0,
            color: c.iconColor,
            fontSize: '11px',
            fontWeight: 600,
            cursor: 'pointer',
            padding: '2px 6px',
            borderRadius: '4px',
            border: `1px solid ${c.iconColor}44`,
            whiteSpace: 'nowrap',
          }}
        >
          Retry
        </span>
      )}
      <span style={{
        flexShrink: 0,
        color: '#E6F1F566',
        fontSize: '16px',
        lineHeight: 1,
        marginTop: '0px',
      }}>
        ×
      </span>
    </div>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used inside ToastProvider')
  return ctx
}
