// Shared atoms + page shell for the standalone demo experience.
// Its own minimal chrome — no dashboard sidebar, no back-to-dashboard.
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../lib/utils';

export const BRAND = '#6366F1';

// Full-bleed dark page background used by every demo screen.
export function DemoBackdrop({ children, className }) {
  return (
    <div className={cn('min-h-[100dvh] w-full bg-[#020617] text-slate-100 antialiased', className)}>
      {/* soft brand glow */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 left-1/2 h-[36rem] w-[36rem] -translate-x-1/2 rounded-full bg-indigo-600/20 blur-[120px]" />
        <div className="absolute bottom-0 right-0 h-[28rem] w-[28rem] rounded-full bg-fuchsia-600/10 blur-[120px]" />
      </div>
      <div className="relative">{children}</div>
    </div>
  );
}

export function DemoLogo({ size = 'md' }) {
  const dim = size === 'lg' ? 'h-10 w-10' : size === 'sm' ? 'h-7 w-7' : 'h-9 w-9';
  const text = size === 'lg' ? 'text-2xl' : size === 'sm' ? 'text-base' : 'text-xl';
  return (
    <div className="flex items-center gap-2.5">
      <div className={cn('grid place-items-center rounded-xl bg-gradient-to-br from-indigo-500 to-fuchsia-500 shadow-lg shadow-indigo-900/40', dim)}>
        <svg viewBox="0 0 24 24" fill="none" className="h-1/2 w-1/2 text-white">
          <path d="M12 2l2.4 6.3L21 11l-6.6 2.7L12 20l-2.4-6.3L3 11l6.6-2.7L12 2z" fill="currentColor" />
        </svg>
      </div>
      <span className={cn('font-extrabold tracking-tight', text)}>AIveilix</span>
    </div>
  );
}

export function DemoButton({ children, onClick, type = 'button', loading, disabled, variant = 'primary', className, ...rest }) {
  const base = 'inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed';
  const styles = {
    primary: 'bg-gradient-to-br from-indigo-500 to-indigo-600 text-white hover:from-indigo-400 hover:to-indigo-500 shadow-lg shadow-indigo-900/30',
    ghost: 'text-slate-300 hover:bg-white/5 ring-1 ring-white/10',
    subtle: 'bg-white/5 text-slate-200 hover:bg-white/10 ring-1 ring-white/10',
    danger: 'bg-rose-500/90 text-white hover:bg-rose-500',
  };
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={cn(base, styles[variant], className)}
      {...rest}
    >
      {loading && <Spinner className="h-4 w-4" />}
      {children}
    </button>
  );
}

export function Spinner({ className }) {
  return (
    <svg className={cn('animate-spin', className)} viewBox="0 0 24 24" fill="none">
      <circle className="opacity-20" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-90" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
    </svg>
  );
}

export function DemoField({ label, hint, children }) {
  return (
    <label className="block">
      {label && <span className="mb-1.5 block text-xs font-medium text-slate-400">{label}</span>}
      {children}
      {hint && <span className="mt-1 block text-[11px] text-slate-500">{hint}</span>}
    </label>
  );
}

export function DemoInput({ className, ...rest }) {
  return (
    <input
      className={cn(
        'w-full rounded-xl bg-slate-800/70 px-3.5 py-2.5 text-sm text-slate-100 outline-none ring-1 ring-white/10 placeholder:text-slate-500 focus:ring-2 focus:ring-indigo-500',
        className,
      )}
      {...rest}
    />
  );
}

export function DemoTextarea({ className, ...rest }) {
  return (
    <textarea
      className={cn(
        'w-full resize-none rounded-xl bg-slate-800/70 px-3.5 py-2.5 text-sm text-slate-100 outline-none ring-1 ring-white/10 placeholder:text-slate-500 focus:ring-2 focus:ring-indigo-500',
        className,
      )}
      {...rest}
    />
  );
}

export function Avatar({ name, color, size = 'md' }) {
  const dim = size === 'sm' ? 'h-6 w-6 text-[10px]' : size === 'lg' ? 'h-10 w-10 text-sm' : 'h-8 w-8 text-xs';
  const initials = (name || '?')
    .split(' ')
    .map((w) => w[0])
    .filter(Boolean)
    .slice(0, 2)
    .join('')
    .toUpperCase();
  return (
    <span
      className={cn('grid place-items-center rounded-full font-bold text-white ring-2 ring-[#020617]', dim)}
      style={{ background: color || BRAND }}
      title={name}
    >
      {initials}
    </span>
  );
}

// Centered modal with backdrop. Pass onClose to enable click-outside + Esc.
export function DemoModal({ open, onClose, children, widthClass = 'max-w-lg', dismissable = true }) {
  React.useEffect(() => {
    if (!open || !dismissable || !onClose) return;
    const onKey = (e) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, onClose, dismissable]);

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-[120] grid place-items-center p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <div
            className="absolute inset-0 bg-black/70 backdrop-blur-sm"
            onClick={() => dismissable && onClose && onClose()}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.96, y: 12 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.97, y: 8 }}
            transition={{ type: 'spring', stiffness: 320, damping: 28 }}
            className={cn(
              'relative w-full overflow-hidden rounded-2xl bg-[#0B1220] ring-1 ring-white/10 shadow-2xl',
              widthClass,
            )}
          >
            {children}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export function ErrorNote({ children }) {
  if (!children) return null;
  return (
    <div className="rounded-xl bg-rose-500/10 px-3.5 py-2.5 text-sm text-rose-300 ring-1 ring-rose-500/20">
      {children}
    </div>
  );
}
