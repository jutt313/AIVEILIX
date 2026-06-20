// Shared atoms for the demo — themed with the app's real palette (blue/cyan +
// slate, light/dark) and the real /logo-tight.png mark. No invented colors.
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../lib/utils';
import { themeOptions, LOGO_SRC } from './demoTheme';

// AIveilix brand lockup — real logo image + wordmark (matches the app header).
export function DemoLogo({ theme = 'light', size = 'md' }) {
  const p = themeOptions[theme];
  const dim = size === 'lg' ? 'h-9 w-9' : size === 'sm' ? 'h-6 w-6' : 'h-7 w-7';
  const text = size === 'lg' ? 'text-xl' : size === 'sm' ? 'text-sm' : 'text-base';
  return (
    <div className="flex items-center gap-2">
      <img src={LOGO_SRC} alt="AIveilix" className={cn('rounded-md object-contain', dim)} />
      <span className={cn('font-semibold tracking-tight', text, p.title)}>AIveilix</span>
    </div>
  );
}

// Auth-style branded backdrop (matches AuthShell): subtle blue + cyan glows.
export function DemoBackdrop({ theme = 'light', children, className }) {
  const p = themeOptions[theme];
  return (
    <main className={cn('relative min-h-[100dvh] overflow-hidden transition-colors duration-300', p.app, className)}>
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute left-1/2 top-[-12rem] h-80 w-80 -translate-x-1/2 rounded-full bg-blue-500/10 blur-3xl" />
        <div className="absolute bottom-[-8rem] right-[-4rem] h-72 w-72 rounded-full bg-cyan-400/10 blur-3xl" />
      </div>
      <div className="relative">{children}</div>
    </main>
  );
}

export function Spinner({ className }) {
  return (
    <svg className={cn('animate-spin', className)} viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="12" r="10" strokeOpacity=".25" stroke="currentColor" strokeWidth="2" />
      <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="2" />
    </svg>
  );
}

export function DemoButton({ children, onClick, type = 'button', loading, disabled, theme = 'light', variant = 'primary', className, ...rest }) {
  const p = themeOptions[theme];
  const base = 'inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed';
  const styles = {
    primary: p.primary,
    secondary: `border ${p.secondary}`,
    ghost: theme === 'dark' ? 'text-slate-300 hover:bg-white/5' : 'text-slate-600 hover:bg-slate-100',
  };
  return (
    <button type={type} onClick={onClick} disabled={disabled || loading} className={cn(base, styles[variant], className)} {...rest}>
      {loading && <Spinner className="h-4 w-4" />}
      {children}
    </button>
  );
}

export function DemoField({ label, hint, theme = 'light', children }) {
  const p = themeOptions[theme];
  return (
    <label className="block">
      {label && <span className={cn('mb-1.5 block text-xs font-medium', p.muted)}>{label}</span>}
      {children}
      {hint && <span className={cn('mt-1 block text-[11px]', p.muted)}>{hint}</span>}
    </label>
  );
}

export function DemoInput({ theme = 'light', className, ...rest }) {
  const p = themeOptions[theme];
  return (
    <input
      className={cn('w-full rounded-xl border px-3.5 py-2.5 text-sm outline-none transition focus:ring-2 focus:ring-blue-500/30', p.input, className)}
      {...rest}
    />
  );
}

export function DemoTextarea({ theme = 'light', className, ...rest }) {
  const p = themeOptions[theme];
  return (
    <textarea
      className={cn('w-full resize-none rounded-xl border px-3.5 py-2.5 text-sm outline-none transition focus:ring-2 focus:ring-blue-500/30', p.input, className)}
      {...rest}
    />
  );
}

export function Avatar({ name, color, size = 'md' }) {
  const dim = size === 'sm' ? 'h-6 w-6 text-[10px]' : size === 'lg' ? 'h-10 w-10 text-sm' : 'h-8 w-8 text-xs';
  const initials = (name || '?').split(' ').map((w) => w[0]).filter(Boolean).slice(0, 2).join('').toUpperCase();
  return (
    <span className={cn('grid shrink-0 place-items-center rounded-full font-bold text-white', dim)} style={{ background: color || '#2563EB' }} title={name}>
      {initials}
    </span>
  );
}

export function ThemeToggle({ theme, onToggle }) {
  const isDark = theme === 'dark';
  return (
    <button
      type="button"
      onClick={onToggle}
      title={isDark ? 'Switch to light' : 'Switch to dark'}
      className={cn('flex h-8 w-8 items-center justify-center rounded-full transition', isDark ? 'text-white/60 hover:bg-white/10' : 'text-slate-500 hover:bg-slate-100')}
    >
      {isDark ? (
        <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="5" /><path d="M12 1v2M12 21v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M1 12h2M21 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4" /></svg>
      ) : (
        <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" /></svg>
      )}
    </button>
  );
}

export function ErrorNote({ theme = 'light', children }) {
  if (!children) return null;
  const p = themeOptions[theme];
  return <div className={cn('rounded-xl border px-3.5 py-2.5 text-sm', p.error)}>{children}</div>;
}

// Centered modal with backdrop. Themed surface.
export function DemoModal({ open, onClose, theme = 'light', children, widthClass = 'max-w-lg', dismissable = true }) {
  const isDark = theme === 'dark';
  React.useEffect(() => {
    if (!open || !dismissable || !onClose) return;
    const onKey = (e) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, onClose, dismissable]);

  return (
    <AnimatePresence>
      {open && (
        <motion.div className="fixed inset-0 z-[120] grid place-items-center p-4" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
          <div className={cn('absolute inset-0 backdrop-blur-sm', isDark ? 'bg-slate-950/80' : 'bg-slate-900/40')} onClick={() => dismissable && onClose && onClose()} />
          <motion.div
            initial={{ opacity: 0, scale: 0.96, y: 12 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.97, y: 8 }}
            transition={{ type: 'spring', stiffness: 320, damping: 28 }}
            className={cn('relative w-full overflow-hidden rounded-[1.35rem] border shadow-2xl', widthClass, isDark ? 'border-white/10 bg-[#0b1424]' : 'border-slate-200 bg-white')}
          >
            {children}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
