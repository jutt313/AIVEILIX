// Tiny mirror of App.jsx's themeOptions, so team components style themselves
// the same way as the rest of the dashboard without prop-drilling theme down
// through every modal.

import { useEffect, useState } from 'react';

export const teamThemeOptions = {
  dark: {
    app: 'bg-slate-950 text-slate-100',
    surface: 'border-white/10 bg-slate-950/95',
    card: 'border-white/10 bg-white/[0.02]',
    cardHover: 'hover:border-white/20',
    title: 'text-white',
    text: 'text-slate-300',
    muted: 'text-slate-400',
    subtle: 'text-slate-500',
    input:
      'border-white/10 bg-white/[0.03] text-slate-100 placeholder:text-slate-500 focus:border-blue-400 focus:ring-blue-400/20',
    primary: 'bg-blue-600 text-white hover:bg-blue-500',
    secondary: 'border-white/10 bg-transparent text-slate-100 hover:bg-white/[0.04]',
    danger: 'text-red-300 hover:bg-red-500/10 hover:text-red-200',
    accent: 'text-blue-400',
    overlay: 'bg-slate-950/80',
    badgePending: 'bg-amber-500/15 text-amber-300 border border-amber-500/30',
    badgeAccepted: 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30',
    badgeRejected: 'bg-white/5 text-slate-400 border border-white/10',
    error: 'text-red-300 bg-red-500/10 border border-red-500/20',
    divider: 'border-white/10',
    rowHover: 'hover:bg-white/[0.03]',
    checkbox: 'accent-blue-500',
  },
  light: {
    app: 'bg-slate-100 text-slate-800',
    surface: 'border-slate-200 bg-white',
    card: 'border-slate-200 bg-white',
    cardHover: 'hover:border-slate-300',
    title: 'text-slate-900',
    text: 'text-slate-600',
    muted: 'text-slate-500',
    subtle: 'text-slate-400',
    input:
      'border-slate-200 bg-white text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:ring-blue-500/20',
    primary: 'bg-blue-600 text-white hover:bg-blue-500',
    secondary: 'border-slate-200 bg-white text-slate-800 hover:bg-slate-50',
    danger: 'text-red-600 hover:bg-red-50 hover:text-red-500',
    accent: 'text-blue-600',
    overlay: 'bg-slate-900/40',
    badgePending: 'bg-amber-50 text-amber-700 border border-amber-200',
    badgeAccepted: 'bg-emerald-50 text-emerald-700 border border-emerald-200',
    badgeRejected: 'bg-slate-100 text-slate-600 border border-slate-200',
    error: 'text-red-600 bg-red-50 border border-red-200',
    divider: 'border-slate-200',
    rowHover: 'hover:bg-slate-50',
    checkbox: 'accent-blue-600',
  },
};

function readStoredTheme() {
  if (typeof window === 'undefined') return 'light';
  const stored = window.localStorage.getItem('aiveilix-theme');
  if (stored === 'dark' || stored === 'light') return stored;
  return 'light';
}

// Subscribes to storage changes so a theme toggle elsewhere updates these
// modals live, without prop-drilling theme through every component.
export function useAppTheme() {
  const [theme, setTheme] = useState(readStoredTheme);
  useEffect(() => {
    function onStorage(e) {
      if (e.key === 'aiveilix-theme' && (e.newValue === 'dark' || e.newValue === 'light')) {
        setTheme(e.newValue);
      }
    }
    function onPoll() {
      setTheme(readStoredTheme());
    }
    window.addEventListener('storage', onStorage);
    const intervalId = window.setInterval(onPoll, 800);
    return () => {
      window.removeEventListener('storage', onStorage);
      window.clearInterval(intervalId);
    };
  }, []);
  return { theme, palette: teamThemeOptions[theme] };
}
