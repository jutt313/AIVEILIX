import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useAppTheme } from './theme';

/**
 * Shared modal shell that matches the existing dashboard modals — rounded-[1.4rem],
 * border, palette.card surface, backdrop-blur overlay.
 *
 * Rendered through a portal to document.body so a transformed ancestor
 * (e.g. the dashboard header uses `-translate-x-[20px]`) doesn't capture
 * `position: fixed` and pin the modal off-center.
 */
export default function Modal({
  open,
  onClose,
  title,
  subtitle,
  children,
  maxWidth = '2xl',
  fixedSize = false,
  bare = false,
}) {
  const { theme, palette } = useAppTheme();

  useEffect(() => {
    if (!open) return;
    function onKey(e) {
      if (e.key === 'Escape') onClose?.();
    }
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    document.addEventListener('keydown', onKey);
    return () => {
      document.body.style.overflow = prevOverflow;
      document.removeEventListener('keydown', onKey);
    };
  }, [open, onClose]);

  if (!open) return null;
  if (typeof document === 'undefined') return null;

  const overlayCls = theme === 'light' ? 'bg-white/55' : palette.overlay;
  const panelShell = theme === 'dark'
    ? 'border-white/10 bg-[#0b1220] text-white shadow-[0_30px_100px_rgba(2,6,23,0.62)]'
    : 'border-slate-300 bg-[#f8fafc] text-slate-900 shadow-[0_24px_80px_rgba(148,163,184,0.22)]';

  const widthCls = fixedSize
    ? 'w-full max-w-[62rem]'
    : `w-full ${
        { sm: 'max-w-md', md: 'max-w-lg', lg: 'max-w-xl', xl: 'max-w-2xl', '2xl': 'max-w-3xl' }[maxWidth] || 'max-w-2xl'
      }`;
  const heightCls = fixedSize ? 'h-[min(88dvh,52rem)]' : 'max-h-[88vh]';

  return createPortal(
    <div
      className={`fixed inset-0 z-[100] flex items-center justify-center px-4 py-6 backdrop-blur-sm ${overlayCls}`}
      onClick={onClose}
      role="dialog"
      aria-modal="true"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className={`${widthCls} ${heightCls} flex flex-col overflow-hidden rounded-[1.6rem] border ${panelShell}`}
      >
        {bare ? (
          children
        ) : (
          <>
            <header className={`px-7 pt-6 pb-4 border-b ${palette.divider} flex items-start justify-between gap-4`}>
              <div className="min-w-0">
                <h2 className={`text-lg font-semibold tracking-tight ${palette.title}`}>{title}</h2>
                {subtitle && <p className={`mt-1 text-xs ${palette.muted}`}>{subtitle}</p>}
              </div>
              <button
                onClick={onClose}
                aria-label="Close"
                className={`shrink-0 rounded-full border p-1.5 transition ${palette.secondary}`}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </header>
            <div className="flex-1 overflow-y-auto px-7 py-6">{children}</div>
          </>
        )}
      </div>
    </div>,
    document.body,
  );
}
