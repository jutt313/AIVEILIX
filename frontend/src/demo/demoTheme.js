// Brand theme for the demo — mirrors the main app EXACTLY so the demo looks like
// the real bucket page. Values copied from App.jsx (themeOptions + BucketPage
// shell tokens). Keep in sync with App.jsx if the brand palette ever changes.

export const themeOptions = {
  dark: {
    app: 'bg-slate-950 text-slate-100',
    card: 'border-white/10 bg-white/[0.02] hover:border-white/20',
    title: 'text-white',
    text: 'text-slate-300',
    muted: 'text-slate-400',
    input: 'border-white/10 bg-white/[0.03] text-slate-100 placeholder:text-slate-500 focus:border-blue-400',
    primary: 'bg-blue-600 text-white hover:bg-blue-500',
    secondary: 'border-white/10 bg-transparent text-slate-100 hover:bg-white/[0.04]',
    accent: 'text-blue-400',
    error: 'text-red-400 bg-red-500/10 border-red-500/20',
    success: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    overlay: 'bg-slate-950/80',
    option: 'border-white/10 bg-transparent hover:bg-white/[0.04] text-slate-200',
  },
  light: {
    app: 'bg-slate-100 text-slate-800',
    card: 'border-slate-200 bg-white hover:border-slate-300',
    title: 'text-slate-900',
    text: 'text-slate-600',
    muted: 'text-slate-500',
    input: 'border-slate-200 bg-white text-slate-900 placeholder:text-slate-400 focus:border-blue-500',
    primary: 'bg-blue-600 text-white hover:bg-blue-500',
    secondary: 'border-slate-200 bg-white text-slate-800 hover:bg-slate-50',
    accent: 'text-blue-600',
    error: 'text-red-600 bg-red-50 border-red-200',
    success: 'text-emerald-600 bg-emerald-50 border-emerald-200',
    overlay: 'bg-slate-900/40',
    option: 'border-slate-200 bg-white hover:bg-slate-50 text-slate-700',
  },
};

export const THEME_KEY = 'aiveilix-theme';

export function getInitialTheme() {
  if (typeof window === 'undefined') return 'light';
  const stored = window.localStorage.getItem(THEME_KEY);
  if (stored === 'dark' || stored === 'light') return stored;
  return 'light';
}

export function saveTheme(theme) {
  try { window.localStorage.setItem(THEME_KEY, theme); } catch { /* ignore */ }
}

// Derived class tokens used by the BucketPage shell — copied verbatim.
export function bucketClasses(isDark) {
  return {
    isDark,
    bg: isDark ? 'bg-[#020617] text-slate-100' : 'bg-[#f5f7fb] text-slate-900',
    shell: isDark
      ? 'border-white/10 bg-[#020617] shadow-[0_20px_70px_rgba(0,0,0,0.55)]'
      : 'border-white/80 bg-white/78 backdrop-blur-xl shadow-[0_18px_55px_rgba(148,163,184,0.16)]',
    subtle: isDark ? 'bg-white/[0.025]' : 'bg-slate-50/90',
    line: isDark ? 'border-white/10' : 'border-slate-200',
    muted: isDark ? 'text-white/55' : 'text-slate-500',
    titleCls: isDark ? 'text-white' : 'text-slate-900',
    bodyCls: isDark ? 'text-white/88' : 'text-slate-700',
    threadActive: isDark
      ? 'border-blue-400/55 bg-[#0e2660] shadow-[inset_0_0_0_1px_rgba(255,255,255,0.06)]'
      : 'border-blue-300 bg-blue-50',
    threadIdle: isDark
      ? 'border-white/10 bg-[#020617] hover:bg-white/[0.04]'
      : 'border-transparent bg-transparent hover:bg-slate-100/90',
    fileRowIdle: isDark
      ? 'border-white/10 bg-[#020617] hover:bg-white/[0.04]'
      : 'border-transparent bg-transparent hover:bg-slate-100/90',
    menuBg: isDark ? 'border-white/10 bg-[#020617] text-white' : 'border-slate-200 bg-white text-slate-900',
    rightAside: isDark ? 'border-white/10 bg-[#020617]' : 'border-white/80',
    primary: 'bg-blue-600 text-white hover:bg-blue-500',
  };
}

export const LOGO_SRC = '/logo-tight.png';
