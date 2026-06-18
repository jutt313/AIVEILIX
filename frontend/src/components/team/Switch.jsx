import React from 'react';
import { useAppTheme } from './theme';

/**
 * iOS-style toggle row. Borderless — just a subtle background that lifts on hover.
 */
export function Switch({ checked, onChange, disabled, label, hint }) {
  const { theme } = useAppTheme();
  const isDark = theme === 'dark';
  const trackOn = 'bg-blue-500';
  const trackOff = isDark ? 'bg-white/10' : 'bg-slate-300';
  const rowCls = isDark
    ? 'bg-white/[0.025] hover:bg-white/[0.05]'
    : 'bg-slate-50 hover:bg-slate-100';

  return (
    <button
      type="button"
      role="switch"
      aria-checked={!!checked}
      disabled={disabled}
      onClick={() => !disabled && onChange?.(!checked)}
      className={`group flex w-full items-center gap-3 rounded-2xl px-4 py-3 text-left transition ${rowCls} ${
        disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
      }`}
    >
      <div className="flex-1 min-w-0">
        <div className={`text-sm font-medium ${isDark ? 'text-white' : 'text-slate-900'}`}>
          {label}
        </div>
        {hint && (
          <div className={`mt-0.5 text-[11px] ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
            {hint}
          </div>
        )}
      </div>
      <div
        className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors ${
          checked ? trackOn : trackOff
        }`}
      >
        <span
          className="absolute top-0.5 left-0.5 h-5 w-5 rounded-full bg-white shadow-md transition-transform duration-200"
          style={{ transform: `translateX(${checked ? '20px' : '0px'})` }}
        />
      </div>
    </button>
  );
}

/**
 * Soft radio-card. Selected = blue tint, no rings.
 */
export function RadioCard({ checked, onChange, label, hint, disabled }) {
  const { theme } = useAppTheme();
  const isDark = theme === 'dark';
  const base = isDark ? 'bg-white/[0.025] hover:bg-white/[0.05]' : 'bg-slate-50 hover:bg-slate-100';
  const sel = isDark ? 'bg-blue-500/15' : 'bg-blue-50';

  return (
    <button
      type="button"
      role="radio"
      aria-checked={!!checked}
      disabled={disabled}
      onClick={() => !disabled && onChange?.()}
      className={`flex w-full items-start gap-3 rounded-2xl px-4 py-3 text-left transition ${
        checked ? sel : base
      } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
    >
      <div
        className={`mt-0.5 h-4 w-4 shrink-0 rounded-full transition-colors flex items-center justify-center ${
          checked
            ? 'bg-blue-500'
            : isDark
              ? 'bg-white/10'
              : 'bg-slate-300'
        }`}
      >
        {checked && <span className="h-1.5 w-1.5 rounded-full bg-white" />}
      </div>
      <div className="flex-1 min-w-0">
        <div className={`text-sm font-medium ${isDark ? 'text-white' : 'text-slate-900'}`}>
          {label}
        </div>
        {hint && (
          <div className={`mt-0.5 text-[11px] ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
            {hint}
          </div>
        )}
      </div>
    </button>
  );
}
