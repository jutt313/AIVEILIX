import { useEffect, useRef, useState } from 'react';
import {
  BrowserRouter,
  Link,
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
  useParams,
} from 'react-router-dom';
import {
  Background,
  Controls,
  MarkerType,
  MiniMap,
  ReactFlow,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark, oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { authApi, signOut, bucketApi, dashboardApi, billingApi, adminApi, enterpriseApi } from './api/auth';
import { uploadFilesDirect } from './api/uploads';
import { teamApi } from './api/team';
import threadChatIcon from './thread-chat-icon.svg';
import LandingPage from './LandingPage';
import LandingPageV2 from './LandingPageV2';
import ConnectGuide from './ConnectGuide';
import InviteAcceptPage from './components/team/InviteAcceptPage';
import TeamFacepile from './components/team/TeamFacepile';
import TeamRoleBanner from './components/team/TeamRoleBanner';
import BucketMembers from './components/team/BucketMembers';
import MemberDashboard from './components/team/MemberDashboard';
import WorkspaceSwitcher from './components/team/WorkspaceSwitcher';
import { useTeamContext } from './components/team/useTeamContext';
import SenderBadge, { bubbleStyleForSender } from './components/team/SenderBadge';
import DemoPage from './demo/DemoPage';
import DemoInvitePage from './demo/DemoInvitePage';
import DemoAdminPanel from './demo/DemoAdminPanel';

const themeOptions = {
  dark: {
    app: 'bg-slate-950 text-slate-100',
    card: 'border-white/10 bg-white/[0.02] hover:border-white/20',
    title: 'text-white',
    text: 'text-slate-300',
    muted: 'text-slate-400',
    input: 'border-white/10 bg-white/[0.03] text-slate-100 placeholder:text-slate-500 focus:border-blue-400',
    primary: 'bg-blue-600 text-white hover:bg-blue-500',
    secondary: 'border-white/10 bg-transparent text-slate-100 hover:bg-white/[0.04]',
    divider: 'before:bg-white/10 after:bg-white/10 text-slate-500',
    toggle: 'border-white/10 bg-transparent text-slate-100 hover:bg-white/[0.04]',
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
    divider: 'before:bg-slate-200 after:bg-slate-200 text-slate-400',
    toggle: 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50',
    accent: 'text-blue-600',
    error: 'text-red-600 bg-red-50 border-red-200',
    success: 'text-emerald-600 bg-emerald-50 border-emerald-200',
    overlay: 'bg-slate-900/40',
    option: 'border-slate-200 bg-white hover:bg-slate-50 text-slate-700',
  },
};

function getInitialTheme() {
  if (typeof window === 'undefined') return 'light';
  const stored = window.localStorage.getItem('aiveilix-theme');
  if (stored === 'dark' || stored === 'light') return stored;
  return 'light';
}

function GoogleIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="h-5 w-5">
      <path fill="#4285F4" d="M21.6 12.23c0-.68-.06-1.33-.18-1.95H12v3.69h5.39a4.61 4.61 0 0 1-2 3.03v2.52h3.24c1.9-1.75 2.97-4.33 2.97-7.29Z" />
      <path fill="#34A853" d="M12 22c2.7 0 4.96-.89 6.61-2.42l-3.24-2.52c-.9.6-2.05.96-3.37.96-2.59 0-4.79-1.75-5.57-4.1H3.08v2.59A9.99 9.99 0 0 0 12 22Z" />
      <path fill="#FBBC05" d="M6.43 13.92A5.99 5.99 0 0 1 6.12 12c0-.67.11-1.32.31-1.92V7.49H3.08A9.99 9.99 0 0 0 2 12c0 1.61.38 3.14 1.08 4.51l3.35-2.59Z" />
      <path fill="#EA4335" d="M12 5.98c1.47 0 2.78.51 3.81 1.5l2.86-2.86C16.95 3 14.69 2 12 2A9.99 9.99 0 0 0 3.08 7.49l3.35 2.59c.78-2.35 2.98-4.1 5.57-4.1Z" />
    </svg>
  );
}

function AuthShell({ theme, title, subtitle, children, footer }) {
  const palette = themeOptions[theme];
  return (
    <main className={`relative h-[100dvh] overflow-hidden transition-colors duration-300 ${palette.app}`}>
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute left-1/2 top-[-12rem] h-80 w-80 -translate-x-1/2 rounded-full bg-blue-500/10 blur-3xl" />
        <div className="absolute bottom-[-8rem] right-[-4rem] h-72 w-72 rounded-full bg-cyan-400/10 blur-3xl" />
      </div>
      <div className="relative mx-auto flex h-full w-full max-w-7xl items-center justify-center px-4 pb-4 pt-16 sm:px-6 sm:pb-6 sm:pt-20">
        <div className="w-full max-w-[28rem]">
          <section className={`rounded-[2rem] border px-5 py-4 transition-all duration-300 sm:px-7 sm:py-6 ${palette.card}`}>
            <div className="text-center">
              <p className={`text-xs font-semibold uppercase tracking-[0.35em] ${palette.accent}`}>Aiveilix</p>
              <h1 className={`mt-3 text-2xl font-semibold tracking-tight sm:mt-4 sm:text-3xl ${palette.title}`}>{title}</h1>
              <p className={`mt-2 text-sm leading-5 sm:leading-6 ${palette.text}`}>{subtitle}</p>
            </div>
            <div className="mt-5 sm:mt-6">{children}</div>
            {footer ? <div className="mt-4 sm:mt-5">{footer}</div> : null}
          </section>
        </div>
      </div>
    </main>
  );
}

function formatTimeRemaining(totalSeconds) {
  const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, '0');
  const seconds = String(totalSeconds % 60).padStart(2, '0');
  return `${minutes}:${seconds}`;
}

function Input({ label, type = 'text', placeholder, theme, value, onChange, name, disabled }) {
  const palette = themeOptions[theme];
  return (
    <label className="block">
      <span className={`mb-2 block text-sm font-medium ${palette.title}`}>{label}</span>
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        name={name}
        disabled={disabled}
        className={`w-full rounded-2xl border px-4 py-3 text-sm outline-none transition disabled:opacity-50 ${palette.input}`}
      />
    </label>
  );
}

function PrimaryButton({ children, theme, loading, type = 'submit', onClick, disabled = false }) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={loading || disabled}
      className={`w-full rounded-2xl px-4 py-3 text-sm font-semibold transition disabled:opacity-60 ${themeOptions[theme].primary}`}
    >
      {loading ? 'Please wait...' : children}
    </button>
  );
}

function SocialButton({ theme, icon, children, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex w-full items-center justify-center gap-3 rounded-2xl border px-4 py-3 text-sm font-medium transition ${themeOptions[theme].secondary}`}
    >
      {icon}
      <span>{children}</span>
    </button>
  );
}

function Divider({ theme, label = 'or continue with' }) {
  return (
    <div className={`flex items-center gap-4 text-[11px] uppercase tracking-[0.28em] before:h-px before:flex-1 after:h-px after:flex-1 ${themeOptions[theme].divider}`}>
      {label}
    </div>
  );
}

function Alert({ theme, message, type = 'error' }) {
  if (!message) return null;
  const palette = themeOptions[theme];
  return (
    <div className={`rounded-2xl border px-4 py-3 text-sm ${type === 'error' ? palette.error : palette.success}`}>
      {message}
    </div>
  );
}

function buildOAuthRedirectUri() {
  if (typeof window === 'undefined') return '';
  return `${window.location.origin}/oauth/callback`;
}

function buildOAuthStateStorageKey(mode, provider) {
  return `aiveilix-oauth-state:${mode}:${provider}`;
}

function createOAuthStateToken() {
  if (typeof window === 'undefined') return '';
  if (window.crypto?.randomUUID) return window.crypto.randomUUID();
  if (window.crypto?.getRandomValues) {
    const bytes = new Uint8Array(16);
    window.crypto.getRandomValues(bytes);
    return Array.from(bytes, (byte) => byte.toString(16).padStart(2, '0')).join('');
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function rememberOAuthState(mode, provider, token) {
  if (typeof window === 'undefined' || !token) return;
  sessionStorage.setItem(buildOAuthStateStorageKey(mode, provider), token);
}

function consumeOAuthState(mode, provider) {
  if (typeof window === 'undefined') return '';
  const key = buildOAuthStateStorageKey(mode, provider);
  const token = sessionStorage.getItem(key) || '';
  sessionStorage.removeItem(key);
  return token;
}

function parseOAuthState(rawState) {
  if (!rawState) return { mode: 'login', provider: '' };
  const [mode, provider, token = ''] = String(rawState).split(':');
  return {
    mode: mode === 'connect' ? 'connect' : 'login',
    provider: provider || '',
    token,
  };
}

function TextArea({ label, placeholder, theme, value, onChange, disabled, rows = 5 }) {
  const palette = themeOptions[theme];
  return (
    <label className="block">
      <span className={`mb-2 block text-sm font-medium ${palette.title}`}>{label}</span>
      <textarea
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        disabled={disabled}
        rows={rows}
        className={`w-full resize-none rounded-2xl border px-4 py-3 text-sm outline-none transition disabled:opacity-50 ${palette.input}`}
      />
    </label>
  );
}

function ModalShell({ theme, title, subtitle, children, onClose, widthClass = 'max-w-lg' }) {
  const palette = themeOptions[theme];
  const isDark = theme === 'dark';
  return (
    <div className={`fixed inset-0 z-50 flex items-center justify-center px-4 ${isDark ? palette.overlay : 'bg-white/45'} backdrop-blur-sm`}>
      <div className={`w-full ${widthClass} rounded-[1.35rem] border p-6 shadow-2xl ${isDark ? palette.card : 'border-slate-200 bg-white text-slate-900 shadow-[0_24px_80px_rgba(148,163,184,0.22)]'}`}>
        <div className="mb-5 flex items-start justify-between gap-4">
          <div>
            <h2 className={`text-lg font-semibold ${palette.title}`}>{title}</h2>
            {subtitle ? <p className={`mt-1 text-sm ${palette.text}`}>{subtitle}</p> : null}
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close dialog"
            className={`flex h-9 w-9 items-center justify-center rounded-full transition ${isDark ? 'text-white/70 hover:bg-white/10 hover:text-white' : 'text-slate-500 hover:bg-slate-100 hover:text-slate-900'}`}
          >
            <CloseIcon />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

function ConfirmDialog({
  theme,
  open,
  title,
  subtitle,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  tone = 'danger',
  loading = false,
  onConfirm,
  onCancel,
}) {
  const palette = themeOptions[theme];
  const confirmClass = tone === 'danger'
    ? theme === 'dark'
      ? 'bg-red-500/18 text-red-200 hover:bg-red-500/24'
      : 'bg-red-600 text-white hover:bg-red-500'
    : palette.primary;

  if (!open) return null;

  return (
    <ModalShell theme={theme} title={title} subtitle={subtitle} onClose={onCancel}>
      <div className="flex gap-2 pt-2">
        <button
          type="button"
          onClick={onCancel}
          disabled={loading}
          className={`flex-1 rounded-2xl border px-4 py-2.5 text-sm font-medium transition ${palette.secondary}`}
        >
          {cancelLabel}
        </button>
        <button
          type="button"
          onClick={onConfirm}
          disabled={loading}
          className={`flex-1 rounded-2xl px-4 py-2.5 text-sm font-semibold transition disabled:opacity-60 ${confirmClass}`}
        >
          {loading ? 'Please wait...' : confirmLabel}
        </button>
      </div>
    </ModalShell>
  );
}

function InputDialog({
  theme,
  open,
  title,
  subtitle,
  label,
  placeholder,
  value,
  onChange,
  confirmLabel = 'Save',
  cancelLabel = 'Cancel',
  loading = false,
  onConfirm,
  onCancel,
  secret = false,
}) {
  const palette = themeOptions[theme];

  if (!open) return null;

  return (
    <ModalShell theme={theme} title={title} subtitle={subtitle} onClose={onCancel}>
      <div className="space-y-4">
        <Input
          label={label}
          type={secret ? 'password' : 'text'}
          placeholder={placeholder}
          theme={theme}
          value={value}
          onChange={onChange}
          disabled={loading}
        />
        <div className="flex gap-2 pt-1">
          <button
            type="button"
            onClick={onCancel}
            disabled={loading}
            className={`flex-1 rounded-2xl border px-4 py-2.5 text-sm font-medium transition ${palette.secondary}`}
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={loading || !value.trim()}
            className={`flex-1 rounded-2xl px-4 py-2.5 text-sm font-semibold transition disabled:opacity-60 ${palette.primary}`}
          >
            {loading ? 'Please wait...' : confirmLabel}
          </button>
        </div>
      </div>
    </ModalShell>
  );
}

const PLAN_GLYPH = {
  pending: '◻',
  in_progress: '▶',
  done: '✓',
  blocked: '✗',
};

function PlanChecklist({ plan = [], isDark, dense = false }) {
  if (!plan || plan.length === 0) return null;
  const textTone = isDark ? 'text-white/70' : 'text-slate-600';
  const doneTone = isDark ? 'text-white/40 line-through' : 'text-slate-400 line-through';
  const activeTone = isDark ? 'text-white' : 'text-slate-900';
  return (
    <ul
      className={`flex flex-col gap-1 ${dense ? 'pl-1' : 'pl-1 py-1'} ${textTone}`}
      style={{ fontSize: '16px', lineHeight: '1.45' }}
    >
      {plan.map((item) => {
        const glyph = PLAN_GLYPH[item.status] || '◻';
        const itemTone =
          item.status === 'done' || item.status === 'blocked'
            ? doneTone
            : item.status === 'in_progress'
              ? activeTone
              : textTone;
        return (
          <li key={item.id} className={`flex items-start gap-2 ${itemTone}`}>
            <span className="select-none">{glyph}</span>
            <span className="min-w-0 break-words">{item.task}</span>
          </li>
        );
      })}
    </ul>
  );
}

function AgentWorkPanel({ steps = [], currentStep, plan = [], done = false, isDark }) {
  if (done) return null;

  const latest = currentStep || steps[steps.length - 1] || { type: 'thinking', label: 'Thinking...' };
  const label = latest.label || 'Thinking...';
  const textTone = isDark ? 'text-white/60' : 'text-slate-500';

  return (
    <div className={`flex max-w-full flex-col gap-1 px-1 py-2 text-sm leading-5 ${textTone}`}>
      <div className="inline-flex items-center gap-2">
        <span className="relative flex h-5 w-5 shrink-0 items-center justify-center" aria-hidden="true">
          <span className="absolute h-5 w-5 animate-ping rounded-full bg-blue-500/20" />
          <img
            src="/logo-tight.png"
            alt=""
            className="relative h-5 w-5 animate-pulse rounded-md object-contain"
          />
        </span>
        <span className="min-w-0 truncate">{label}</span>
      </div>
      {plan.length > 0 && (
        <PlanChecklist plan={plan} isDark={isDark} dense />
      )}
    </div>
  );
}

function SearchingGroup({ steps = [], plan = [], isDark }) {
  const [open, setOpen] = useState(false);
  const hasSteps = Array.isArray(steps) && steps.length > 0;
  const hasPlan = Array.isArray(plan) && plan.length > 0;
  if (!hasSteps && !hasPlan) return null;
  const textTone = isDark ? 'text-white/50' : 'text-slate-500';
  const lineTone = isDark ? 'text-white/60' : 'text-slate-600';
  return (
    <div className={`mt-1 ${textTone}`} style={{ fontSize: '13px' }}>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 ${isDark ? 'hover:bg-white/5' : 'hover:bg-slate-100'}`}
      >
        <span>{open ? '▾' : '▸'}</span>
        <span>Searching{hasSteps ? `… ${steps.length} step${steps.length === 1 ? '' : 's'}` : '…'}</span>
      </button>
      {open && (
        <div className="mt-1 space-y-2 pl-3">
          {hasPlan && <PlanChecklist plan={plan} isDark={isDark} />}
          {hasSteps && (
            <ul className={`space-y-0.5 ${lineTone}`}>
              {steps.map((s, i) => (
                <li key={i} className="leading-5">• {s.label || ''}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

// ---------- Onboarding Modal ----------

const QUESTIONS = [
  {
    key: 'useCase',
    question: 'How will you use Aiveilix?',
    options: ['Personal knowledge', 'Work or business', 'AI agents', 'Other'],
  },
  {
    key: 'need',
    question: 'What do you mainly need?',
    options: ['Persistent memory', 'Document search', 'Connect to Claude / ChatGPT', 'Other'],
  },
  {
    key: 'referral',
    question: 'How did you find us?',
    options: ['Twitter / X', 'YouTube', 'Friend or colleague', 'Google Search'],
  },
];

function OnboardingModal({ theme, onDone }) {
  const palette = themeOptions[theme];
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState({ useCase: '', need: '', referral: '' });
  const [saving, setSaving] = useState(false);

  const current = QUESTIONS[step];

  const handleSelect = async (option) => {
    const updated = { ...answers, [current.key]: option };
    setAnswers(updated);

    if (step < QUESTIONS.length - 1) {
      setStep((s) => s + 1);
      return;
    }

    // Last question — save to DB
    setSaving(true);
    try {
      await authApi.saveOnboarding(updated.useCase, updated.need, updated.referral);
      localStorage.setItem('aiveilix-onboarded', '1');
    } catch {
      // non-blocking — proceed even if save fails
    } finally {
      setSaving(false);
      onDone();
    }
  };

  return (
    <div className={`fixed inset-0 z-50 flex items-center justify-center px-4 ${palette.overlay} backdrop-blur-sm`}>
      <div className={`w-full max-w-sm rounded-[2rem] border p-6 shadow-2xl ${palette.card}`}>
        {/* Progress dots */}
        <div className="mb-5 flex items-center justify-between">
          <p className={`text-xs uppercase tracking-[0.28em] ${palette.accent}`}>
            {step + 1} of {QUESTIONS.length}
          </p>
          <div className="flex gap-1.5">
            {QUESTIONS.map((_, i) => (
              <div
                key={i}
                className={`h-1.5 rounded-full transition-all ${
                  i === step ? 'w-5 bg-blue-500' : i < step ? 'w-1.5 bg-blue-500/50' : 'w-1.5 bg-slate-500/30'
                }`}
              />
            ))}
          </div>
        </div>

        {/* Question */}
        <h2 className={`mb-4 text-base font-semibold ${palette.title}`}>{current.question}</h2>

        {/* Options as row lines */}
        <div className="flex flex-col gap-2">
          {current.options.map((opt) => (
            <button
              key={opt}
              type="button"
              disabled={saving}
              onClick={() => handleSelect(opt)}
              className={`w-full rounded-2xl border px-4 py-3 text-left text-sm font-medium transition disabled:opacity-50 ${palette.option}`}
            >
              {opt}
            </button>
          ))}
        </div>

        {/* Back + Skip */}
        <div className="mt-4 flex gap-2">
          <button
            type="button"
            disabled={step === 0 || saving}
            onClick={() => setStep((s) => s - 1)}
            className={`flex-1 rounded-2xl border px-4 py-2.5 text-sm font-medium transition disabled:opacity-30 ${palette.secondary}`}
          >
            Back
          </button>
          <button
            type="button"
            disabled={saving}
            onClick={() => { localStorage.setItem('aiveilix-onboarded', '1'); onDone(); }}
            className={`flex-1 rounded-2xl border px-4 py-2.5 text-sm font-medium transition disabled:opacity-30 ${palette.secondary}`}
          >
            Skip
          </button>
        </div>
      </div>
    </div>
  );
}

// Decide where to land a user right after authentication. Team members never
// go through onboarding, so they always head to the dashboard; owners who
// haven't onboarded yet are sent to the onboarding flow.
async function resolvePostAuthRoute() {
  if (localStorage.getItem('aiveilix-onboarded')) return '/dashboard';
  try {
    const me = await teamApi.getMe();
    if (me?.is_member) {
      // Remember it so future logins skip the membership check.
      localStorage.setItem('aiveilix-onboarded', '1');
      return '/dashboard';
    }
  } catch {
    // Membership unknown — fall through to onboarding.
  }
  return '/onboarding';
}

// ---------- Login ----------

function LoginPage({ theme }) {
  const palette = themeOptions[theme];
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const result = await authApi.login(form.email, form.password);
      if (result.requires_2fa) {
        navigate(`/2fa?temp_token=${result.temp_token}`);
        return;
      }
      localStorage.setItem('refresh_token', result.refresh_token);
      sessionStorage.setItem('access_token', result.access_token);
      navigate(await resolvePostAuthRoute());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSocialAuth = async (provider) => {
    setError('');
    try {
      const stateToken = createOAuthStateToken();
      rememberOAuthState('login', provider, stateToken);
      const result = await authApi.getOAuthAuthorizeUrl(provider, buildOAuthRedirectUri(), 'login', stateToken);
      window.location.href = result.url;
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <AuthShell
      theme={theme}
      title="Login"
      subtitle="Sign in to your account."
      footer={
        <p className={`text-center text-sm ${palette.text}`}>
          Need an account?{' '}
          <Link className="font-semibold text-blue-500" to="/signup">Create account</Link>
        </p>
      }
    >
      <form className="space-y-4" onSubmit={handleSubmit}>
        <Alert theme={theme} message={error} />
        <Input label="Email" type="email" name="email" placeholder="you@example.com" theme={theme} value={form.email} onChange={handleChange} disabled={loading} />
        <Input label="Password" type="password" name="password" placeholder="Enter your password" theme={theme} value={form.password} onChange={handleChange} disabled={loading} />
        <div className="flex items-center justify-end">
          <Link className="text-sm font-medium text-blue-500" to="/forgot-password">Forgot password?</Link>
        </div>
        <PrimaryButton theme={theme} loading={loading}>Login</PrimaryButton>
        <Divider theme={theme} />
        <div className="grid gap-3">
          <SocialButton theme={theme} icon={<GoogleIcon />} onClick={() => handleSocialAuth('google')}>Continue with Google</SocialButton>
        </div>
      </form>
    </AuthShell>
  );
}

// ---------- Signup ----------

function SignupPage({ theme }) {
  const palette = themeOptions[theme];
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await authApi.register(form.name, form.email, form.password);
      const params = new URLSearchParams({ name: form.name, email: form.email });
      navigate(`/confirm-email?${params.toString()}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSocialAuth = async (provider) => {
    setError('');
    try {
      const stateToken = createOAuthStateToken();
      rememberOAuthState('login', provider, stateToken);
      const result = await authApi.getOAuthAuthorizeUrl(provider, buildOAuthRedirectUri(), 'login', stateToken);
      window.location.href = result.url;
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <AuthShell
      theme={theme}
      title="Create Account"
      subtitle="Create your account to get started."
      footer={
        <p className={`text-center text-sm ${palette.text}`}>
          Already have an account?{' '}
          <Link className="font-semibold text-blue-500" to="/login">Login</Link>
        </p>
      }
    >
      <form className="space-y-4" onSubmit={handleSubmit}>
        <Alert theme={theme} message={error} />
        <Input label="Name" name="name" placeholder="Your full name" theme={theme} value={form.name} onChange={handleChange} disabled={loading} />
        <Input label="Email" type="email" name="email" placeholder="you@example.com" theme={theme} value={form.email} onChange={handleChange} disabled={loading} />
        <Input label="Password" type="password" name="password" placeholder="Create a password" theme={theme} value={form.password} onChange={handleChange} disabled={loading} />
        <PrimaryButton theme={theme} loading={loading}>Create Account</PrimaryButton>
        <p className={`text-center text-xs leading-5 ${palette.muted}`}>
          By continuing, you agree to our{' '}
          <Link to="/terms" className="font-medium hover:underline">Terms</Link>{' '}
          and{' '}
          <Link to="/privacy-policy" className="font-medium hover:underline">Privacy Policy</Link>.
        </p>
        <Divider theme={theme} />
        <div className="grid gap-3">
          <SocialButton theme={theme} icon={<GoogleIcon />} onClick={() => handleSocialAuth('google')}>Continue with Google</SocialButton>
        </div>
      </form>
    </AuthShell>
  );
}

function OAuthCallbackPage({ theme }) {
  const palette = themeOptions[theme];
  const location = useLocation();
  const navigate = useNavigate();
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;

    async function handleOAuthCallback() {
      const params = new URLSearchParams(location.search);
      const oauthError = params.get('error');
      const code = params.get('code');
      const { mode, provider, token } = parseOAuthState(params.get('state'));
      const redirectUri = buildOAuthRedirectUri();
      const expectedToken = provider ? consumeOAuthState(mode, provider) : '';

      if (oauthError) {
        if (!cancelled) setError('The provider denied the sign-in request.');
        return;
      }
      if (!code || !provider) {
        if (!cancelled) setError('OAuth callback is missing required details.');
        return;
      }
      if (!token || !expectedToken || token !== expectedToken) {
        if (!cancelled) setError('OAuth callback state did not match. Please try again.');
        return;
      }

      try {
        if (mode === 'connect') {
          const token = sessionStorage.getItem('access_token');
          if (!token) throw new Error('Sign in first, then connect your provider.');
          const result = await dashboardApi.connectAuthProvider(provider, code, redirectUri);
          localStorage.setItem('aiveilix-profile-open', '1');
          localStorage.setItem('aiveilix-profile-feedback', JSON.stringify({
            message: result.message || `${provider} connected successfully.`,
            type: 'success',
          }));
          navigate('/dashboard', { replace: true });
          return;
        }

        const result = await authApi.exchangeOAuth(provider, code, redirectUri);
        localStorage.setItem('refresh_token', result.refresh_token);
        sessionStorage.setItem('access_token', result.access_token);
        navigate(await resolvePostAuthRoute(), { replace: true });
      } catch (err) {
        if (!cancelled) setError(err.message || 'OAuth sign-in failed.');
      }
    }

    handleOAuthCallback();
    return () => { cancelled = true; };
  }, [location.search, navigate]);

  return (
    <AuthShell
      theme={theme}
      title={error ? 'Connection Failed' : 'Connecting Account'}
      subtitle={error ? 'The provider connection could not be completed.' : 'Finalizing your provider sign-in...'}
    >
      <div className="space-y-4">
        <Alert theme={theme} message={error} />
        {!error ? (
          <div className={`rounded-2xl border px-4 py-4 text-sm ${theme === 'dark' ? 'border-white/10 bg-white/5 text-slate-300' : 'border-slate-200 bg-white text-slate-600'}`}>
            Please wait while we finish the OAuth flow.
          </div>
        ) : (
          <button
            type="button"
            onClick={() => navigate('/login')}
            className={`w-full rounded-2xl px-4 py-3 text-sm font-semibold transition ${palette.primary}`}
          >
            Back to Login
          </button>
        )}
      </div>
    </AuthShell>
  );
}

// ---------- Confirm Email ----------

function ConfirmEmailPage({ theme }) {
  const palette = themeOptions[theme];
  const location = useLocation();
  const navigate = useNavigate();
  const searchParams = new URLSearchParams(location.search);
  const name = searchParams.get('name') || 'User';
  const email = searchParams.get('email') || 'you@example.com';
  const [timeRemaining, setTimeRemaining] = useState(120);
  const [resendMsg, setResendMsg] = useState('');
  const [resendLoading, setResendLoading] = useState(false);

  useEffect(() => {
    if (timeRemaining <= 0) return undefined;
    const timer = window.setInterval(() => setTimeRemaining((t) => (t > 0 ? t - 1 : 0)), 1000);
    return () => window.clearInterval(timer);
  }, [timeRemaining]);

  const handleResend = async () => {
    setResendLoading(true);
    setResendMsg('');
    try {
      await authApi.resendVerification(email);
      setTimeRemaining(120);
      setResendMsg('Confirmation email sent.');
    } catch {
      setResendMsg('Could not resend. Please try again.');
    } finally {
      setResendLoading(false);
    }
  };

  return (
    <AuthShell
      theme={theme}
      title="Confirm Email"
      subtitle="We sent a confirmation email to your inbox."
      footer={
        <p className={`text-center text-sm ${palette.text}`}>
          Wrong email?{' '}
          <Link className="font-semibold text-blue-500" to="/signup">Go back</Link>
        </p>
      }
    >
      <div className="space-y-4">
        <div className={`rounded-2xl border px-4 py-4 text-sm ${palette.secondary}`}>
          <p className={`font-medium ${palette.title}`}>{name}</p>
          <p className={`mt-1 break-all ${palette.text}`}>{email}</p>
        </div>
        <div className={`rounded-2xl border px-4 py-4 text-center ${palette.secondary}`}>
          <p className={`text-xs uppercase tracking-[0.28em] ${palette.muted}`}>Confirm within</p>
          <p className={`mt-2 text-3xl font-semibold tracking-tight ${palette.title}`}>{formatTimeRemaining(timeRemaining)}</p>
        </div>
        {resendMsg && <Alert theme={theme} message={resendMsg} type="success" />}
        <button
          type="button"
          onClick={handleResend}
          disabled={timeRemaining > 0 || resendLoading}
          className={`w-full rounded-2xl border px-4 py-3 text-sm font-medium transition ${
            timeRemaining > 0 || resendLoading
              ? 'cursor-not-allowed border-slate-300/40 bg-slate-400/10 text-slate-400'
              : themeOptions[theme].secondary
          }`}
        >
          {resendLoading ? 'Sending...' : timeRemaining > 0 ? `Resend in ${formatTimeRemaining(timeRemaining)}` : 'Resend Email'}
        </button>
      </div>
    </AuthShell>
  );
}

// ---------- Verify Email ----------

function VerifyEmailPage({ theme }) {
  const palette = themeOptions[theme];
  const location = useLocation();
  const navigate = useNavigate();
  const token = new URLSearchParams(location.search).get('token');
  const [status, setStatus] = useState('verifying'); // 'verifying' | 'error'
  const [error, setError] = useState('');
  const ran = useRef(false);

  useEffect(() => {
    // The verification token is single-use; guard against React StrictMode's
    // double-invoke so a success isn't immediately overwritten by a 2nd call.
    if (ran.current) return;
    ran.current = true;

    if (!token) {
      setStatus('error');
      setError('This verification link is missing its token.');
      return;
    }

    (async () => {
      try {
        const result = await authApi.verifyEmail(token);
        // Backend auto-logs-in on verify: persist the session, then send the
        // brand-new user straight into the onboarding flow.
        if (result.refresh_token) localStorage.setItem('refresh_token', result.refresh_token);
        if (result.access_token) sessionStorage.setItem('access_token', result.access_token);
        navigate('/onboarding', { replace: true });
      } catch (err) {
        setStatus('error');
        setError(err.message || 'This verification link is invalid or has expired.');
      }
    })();
  }, [token, navigate]);

  return (
    <AuthShell
      theme={theme}
      title="Verify Email"
      subtitle={status === 'error' ? 'We could not verify your email.' : 'Confirming your email address...'}
      footer={
        <p className={`text-center text-sm ${palette.text}`}>
          Need a new link?{' '}
          <Link className="font-semibold text-blue-500" to="/login">Go to login</Link>
        </p>
      }
    >
      <div className="space-y-4">
        {status === 'verifying' && (
          <div className={`rounded-2xl border px-4 py-6 text-center ${palette.secondary}`}>
            <p className={`text-sm ${palette.text}`}>Please wait a moment while we verify your email...</p>
          </div>
        )}
        {status === 'error' && (
          <>
            <Alert theme={theme} message={error} />
            <button
              type="button"
              onClick={() => navigate('/login')}
              className={`w-full rounded-2xl border px-4 py-3 text-sm font-medium transition ${palette.secondary}`}
            >
              Go to login
            </button>
          </>
        )}
      </div>
    </AuthShell>
  );
}

// ---------- Forgot Password ----------

function ForgotPasswordPage({ theme }) {
  const palette = themeOptions[theme];
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSendCode = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await authApi.forgotPassword(email);
      setStep(2);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCodeChange = (e) => {
    const val = e.target.value.replace(/\D/g, '').slice(0, 6);
    setCode(val);
    if (val.length === 6) setStep(3);
  };

  const handleReset = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await authApi.resetPassword(code, newPassword);
      navigate('/login');
    } catch (err) {
      setError(err.message);
      setStep(2);
      setCode('');
      setNewPassword('');
    } finally {
      setLoading(false);
    }
  };

  const subtitles = {
    1: 'Enter your email and we will send you a reset code.',
    2: 'Enter the 6-digit code sent to your email.',
    3: 'Enter your new password.',
  };

  return (
    <AuthShell
      theme={theme}
      title="Forgot Password"
      subtitle={subtitles[step]}
      footer={
        <p className={`text-center text-sm ${palette.text}`}>
          <Link className="font-semibold text-blue-500" to="/login">Back to login</Link>
        </p>
      }
    >
      <div className="space-y-4">
        <Alert theme={theme} message={error} type="error" />
        <form className="space-y-4" onSubmit={handleSendCode}>
          <Input label="Email" type="email" placeholder="you@example.com" theme={theme} value={email} onChange={(e) => setEmail(e.target.value)} disabled={loading || step > 1} />
          {step === 1 && <PrimaryButton theme={theme} loading={loading}>Send Code</PrimaryButton>}
        </form>
        {step >= 2 && (
          <Input label="Reset Code" type="text" placeholder="6-digit code" theme={theme} value={code} onChange={handleCodeChange} disabled={loading || step === 3} />
        )}
        {step === 3 && (
          <form className="space-y-4" onSubmit={handleReset}>
            <Input label="New Password" type="password" placeholder="Enter new password" theme={theme} value={newPassword} onChange={(e) => setNewPassword(e.target.value)} disabled={loading} />
            <PrimaryButton theme={theme} loading={loading}>Reset Password</PrimaryButton>
          </form>
        )}
      </div>
    </AuthShell>
  );
}

// ---------- Policy / Legal Pages ----------

const POLICY_LAST_UPDATED = 'May 25, 2026';

function PolicyShell({ theme, onToggleTheme, children, maxWidth = 'max-w-5xl' }) {
  const palette = themeOptions[theme];
  const isDark = theme === 'dark';
  const headerBg = isDark
    ? 'border-white/10 bg-slate-950/70'
    : 'border-slate-200 bg-white/85';

  return (
    <main className={`relative min-h-[100dvh] transition-colors duration-300 ${palette.app}`}>
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute left-1/2 top-[-12rem] h-80 w-80 -translate-x-1/2 rounded-full bg-blue-500/10 blur-3xl" />
        <div className="absolute bottom-[-8rem] right-[-4rem] h-72 w-72 rounded-full bg-cyan-400/10 blur-3xl" />
      </div>

      <div className={`sticky top-0 z-20 border-b backdrop-blur-md ${headerBg}`}>
        <div className={`mx-auto flex w-full ${maxWidth} items-center justify-between px-4 py-3 sm:px-6`}>
          <Link to="/login" className="flex items-center gap-2 transition-opacity hover:opacity-90">
            <span className={`text-xs font-semibold uppercase tracking-[0.35em] ${palette.accent}`}>Aiveilix</span>
          </Link>
          <div className="flex items-center gap-2">
            <Link
              to="/login"
              className={`rounded-full border px-3 py-1.5 text-xs font-medium transition ${palette.secondary}`}
            >
              Back to app
            </Link>
            <button
              type="button"
              onClick={onToggleTheme}
              className={`rounded-full border px-3 py-1.5 text-xs font-medium transition ${palette.toggle}`}
            >
              {theme === 'dark' ? 'Light' : 'Dark'}
            </button>
          </div>
        </div>
      </div>

      <div className={`relative mx-auto w-full ${maxWidth} px-4 py-10 sm:px-6 sm:py-14`}>
        {children}
      </div>
    </main>
  );
}

function PolicySectionHeading({ theme, children }) {
  const palette = themeOptions[theme];
  const borderTone = theme === 'dark' ? 'border-blue-400/30' : 'border-blue-500/30';
  return (
    <h2 className={`mb-4 border-b pb-2 text-xl font-semibold ${palette.title} ${borderTone}`}>
      {children}
    </h2>
  );
}

function PrivacyPolicyPage({ theme, onToggleTheme }) {
  const palette = themeOptions[theme];
  return (
    <PolicyShell theme={theme} onToggleTheme={onToggleTheme}>
      <header className="mb-10">
        <h1 className={`text-3xl font-semibold tracking-tight sm:text-4xl ${palette.title}`}>Privacy Policy</h1>
        <p className={`mt-2 text-sm ${palette.muted}`}>Last updated: {POLICY_LAST_UPDATED}</p>
      </header>

      <div className={`space-y-8 leading-relaxed ${palette.text}`}>
        <section>
          <PolicySectionHeading theme={theme}>1. Introduction</PolicySectionHeading>
          <p>
            AIveilix (“we”, “us”, “our”) is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our document intelligence service, including our website and application (the “Service”).
          </p>
          <p className="mt-3">
            By using AIveilix, you agree to this Privacy Policy. If you do not agree, please do not use the Service.
          </p>
        </section>

        <section>
          <PolicySectionHeading theme={theme}>2. Information We Collect</PolicySectionHeading>
          <p>We collect information you give us, and some that is created when you use the Service.</p>
          <h3 className={`mt-6 mb-2 text-lg font-medium ${palette.title}`}>2.1 Information you provide</h3>
          <ul className="list-disc space-y-1 pl-6">
            <li><strong className={palette.title}>Account:</strong> Email, password, and name when you sign up</li>
            <li><strong className={palette.title}>Documents and content:</strong> Files and text you upload into buckets (PDFs, images, etc.)</li>
            <li><strong className={palette.title}>Usage in product:</strong> Bucket names, chat messages, and conversation history</li>
            <li><strong className={palette.title}>API keys and OAuth:</strong> If you use API access, we store and use API keys and OAuth client details you provide</li>
            <li><strong className={palette.title}>Support:</strong> Anything you send when you contact us</li>
          </ul>
          <h3 className={`mt-6 mb-2 text-lg font-medium ${palette.title}`}>2.2 Information we collect automatically</h3>
          <ul className="list-disc space-y-1 pl-6">
            <li><strong className={palette.title}>Usage:</strong> How you use the Service (e.g. buckets, file counts, activity)</li>
            <li><strong className={palette.title}>Technical:</strong> IP address, browser type, device type, and similar technical data</li>
            <li><strong className={palette.title}>Logs:</strong> Access times and errors for security and operations</li>
          </ul>
        </section>

        <section>
          <PolicySectionHeading theme={theme}>3. How We Use Your Information</PolicySectionHeading>
          <p>We use your information to:</p>
          <ul className="mt-2 list-disc space-y-1 pl-6">
            <li>Provide and operate the Service (storage, search, chat, embeddings)</li>
            <li>Create and manage your account and buckets</li>
            <li>Process and index your documents for search and AI chat</li>
            <li>Send notifications you have requested (e.g. file processed, login)</li>
            <li>Improve the Service and fix issues</li>
            <li>Comply with law and protect our rights and security</li>
            <li>Respond to your requests (e.g. support, privacy requests)</li>
          </ul>
        </section>

        <section>
          <PolicySectionHeading theme={theme}>4. Sharing and Disclosure</PolicySectionHeading>
          <p>We do not sell your personal information. We may share it only:</p>
          <ul className="mt-2 list-disc space-y-1 pl-6">
            <li><strong className={palette.title}>Service providers:</strong> With vendors that help us run the Service (e.g. hosting, auth). They are required to protect your data and use it only for our instructions.</li>
            <li><strong className={palette.title}>AI / embeddings:</strong> Your document content may be sent to third‑party AI/embedding services we use to power search and chat. Use of the Service means you accept that.</li>
            <li><strong className={palette.title}>Legal:</strong> When required by law, court order, or to protect rights and safety.</li>
            <li><strong className={palette.title}>With your consent:</strong> Where you have agreed to a specific sharing.</li>
          </ul>
        </section>

        <section>
          <PolicySectionHeading theme={theme}>5. Data Security</PolicySectionHeading>
          <p>
            We use safeguards (e.g. encryption in transit, access controls, secure storage) to protect your data. No system is completely secure; you use the Service at your own risk. You are responsible for keeping your password and API keys secret and for activity under your account.
          </p>
        </section>

        <section>
          <PolicySectionHeading theme={theme}>6. Data Retention</PolicySectionHeading>
          <p>
            We keep your data for as long as your account is active and as needed to provide the Service, comply with law, and resolve disputes. If you delete your account or data, we will delete or anonymize it within a reasonable time, except where we must keep it by law.
          </p>
        </section>

        <section>
          <PolicySectionHeading theme={theme}>7. Your Rights</PolicySectionHeading>
          <p>
            Depending on where you live, you may have the right to access, correct, delete, or export your personal data, or to object to or restrict certain processing. To request this, contact us at{' '}
            <a href="mailto:contact@aiveilix.com" className={`font-medium hover:underline ${palette.accent}`}>contact@aiveilix.com</a>. We will respond as required by law.
          </p>
          <p className="mt-3">You can also update account details and preferences in the app where we provide those options.</p>
        </section>

        <section>
          <PolicySectionHeading theme={theme}>8. Cookies and Similar Technologies</PolicySectionHeading>
          <p>
            We use cookies and similar technologies for sign‑in, preferences, and security. You can adjust your browser settings, but some features may not work if you disable them.
          </p>
        </section>

        <section>
          <PolicySectionHeading theme={theme}>9. International Transfers</PolicySectionHeading>
          <p>
            Your data may be stored and processed in countries other than your own. We take steps so that it receives adequate protection where required by law.
          </p>
        </section>

        <section>
          <PolicySectionHeading theme={theme}>10. Children</PolicySectionHeading>
          <p>
            The Service is not intended for children under 16. We do not knowingly collect data from them. If you learn a child has given us data, contact us and we will delete it.
          </p>
        </section>

        <section>
          <PolicySectionHeading theme={theme}>11. Changes to This Policy</PolicySectionHeading>
          <p>
            We may update this Privacy Policy from time to time. We will post the new version here and update the “Last updated” date. For big changes we may notify you by email or in the app. Continued use after changes means you accept the updated policy.
          </p>
        </section>

        <section>
          <PolicySectionHeading theme={theme}>12. Data Breach Notification (GDPR)</PolicySectionHeading>
          <p>
            In the event of a personal data breach, AIveilix will act promptly in accordance with applicable law, including the EU General Data Protection Regulation (GDPR).
          </p>
          <h3 className={`mt-4 mb-2 text-lg font-medium ${palette.title}`}>What we will do:</h3>
          <ul className="list-disc space-y-1 pl-6">
            <li><strong className={palette.title}>Detect and contain:</strong> Upon becoming aware of a breach, we will immediately assess the scope, contain it, and begin investigation.</li>
            <li><strong className={palette.title}>Notify authorities:</strong> If the breach is likely to result in a risk to individuals' rights and freedoms, we will notify the relevant supervisory authority within <strong className={palette.title}>72 hours</strong> of becoming aware.</li>
            <li><strong className={palette.title}>Notify affected users:</strong> If the breach is likely to result in a high risk to individuals, we will notify affected users without undue delay, clearly explaining what happened, what data was affected, and what steps we are taking.</li>
            <li><strong className={palette.title}>Document:</strong> All breaches, regardless of severity, will be documented internally including the facts, effects, and remedial actions taken.</li>
          </ul>
          <h3 className={`mt-4 mb-2 text-lg font-medium ${palette.title}`}>What a breach notification will include:</h3>
          <ul className="list-disc space-y-1 pl-6">
            <li>A description of the nature of the breach</li>
            <li>The categories and approximate number of individuals and records affected</li>
            <li>The likely consequences of the breach</li>
            <li>Measures taken or proposed to address the breach</li>
            <li>Contact details for our data protection inquiries</li>
          </ul>
          <p className="mt-3">
            To report a suspected security issue, contact us immediately at{' '}
            <a href="mailto:contact@aiveilix.com" className={`font-medium hover:underline ${palette.accent}`}>contact@aiveilix.com</a>.
          </p>
        </section>

        <section>
          <PolicySectionHeading theme={theme}>13. Contact</PolicySectionHeading>
          <p>For privacy questions, requests, or complaints, contact us at:</p>
          <p className="mt-2">
            <strong className={palette.title}>Email:</strong>{' '}
            <a href="mailto:contact@aiveilix.com" className={`font-medium hover:underline ${palette.accent}`}>contact@aiveilix.com</a>
          </p>
        </section>

        <div className={`mt-10 border-t pt-8 text-center text-sm ${palette.muted} ${theme === 'dark' ? 'border-white/10' : 'border-slate-200'}`}>
          <p>By using AIveilix, you acknowledge that you have read and agree to this Privacy Policy.</p>
          <p className="mt-2">
            <Link to="/login" className={`font-medium hover:underline ${palette.accent}`}>Return to AIveilix</Link>
          </p>
        </div>
      </div>
    </PolicyShell>
  );
}

function TermsPage({ theme, onToggleTheme }) {
  const palette = themeOptions[theme];
  return (
    <PolicyShell theme={theme} onToggleTheme={onToggleTheme} maxWidth="max-w-3xl">
      <header className="mb-10">
        <h1 className={`text-3xl font-semibold tracking-tight sm:text-4xl ${palette.title}`}>Terms and Conditions</h1>
        <p className={`mt-2 text-sm ${palette.muted}`}>Last updated: {POLICY_LAST_UPDATED}</p>
      </header>

      <div className={`space-y-8 leading-relaxed ${palette.text}`}>
        <section>
          <PolicySectionHeading theme={theme}>1. Agreement to Terms</PolicySectionHeading>
          <p>
            By accessing or using AIveilix (“Service”, “we”, “us”, “our”), you agree to be bound by these Terms and Conditions (“Terms”). If you do not agree, you may not use the Service.
          </p>
          <p className="mt-3">
            AIveilix is a document intelligence platform that lets you upload files, organize them in buckets, and chat with AI over your documents. These Terms apply to all users.
          </p>
        </section>

        <section>
          <PolicySectionHeading theme={theme}>2. Description of the Service</PolicySectionHeading>
          <p>AIveilix provides:</p>
          <ul className="mt-2 list-disc space-y-1 pl-6">
            <li>Document buckets to organize your files</li>
            <li>File upload and processing (including PDFs and images)</li>
            <li>Semantic search over your documents</li>
            <li>AI chat over your document content</li>
            <li>API keys and optional OAuth for programmatic access</li>
            <li>Notifications and conversation history</li>
          </ul>
          <p className="mt-3">We may change or discontinue parts of the Service with reasonable notice where practical.</p>
        </section>

        <section>
          <PolicySectionHeading theme={theme}>3. Accounts and Security</PolicySectionHeading>
          <p>
            You must register and keep your account information accurate. You are responsible for all activity under your account.
          </p>
          <p className={`mt-3 font-medium ${palette.title}`}>You must not expose, share, or allow others to use:</p>
          <ul className="mt-2 list-disc space-y-1 pl-6">
            <li>Your password or login credentials</li>
            <li>Your API keys</li>
            <li>OAuth client secrets or other tokens</li>
            <li>Any means of accessing another user's data</li>
          </ul>
          <p className="mt-3">
            If you suspect unauthorized access or misuse, you must notify us promptly and change your credentials. We may suspend or terminate accounts that violate these Terms or pose a security risk.
          </p>
        </section>

        <section>
          <PolicySectionHeading theme={theme}>4. Acceptable Use – What You Must Not Do</PolicySectionHeading>
          <p>You may use the Service only for lawful purposes. You must not:</p>
          <ul className="mt-2 list-disc space-y-1 pl-6">
            <li>Expose, leak, or share API keys, credentials, or access tokens with anyone else</li>
            <li>Use the Service to distribute malware, spam, or harmful code</li>
            <li>Upload or process content that infringes others' rights, is illegal, or violates applicable law</li>
            <li>Attempt to gain unauthorized access to our systems, other users' accounts, or third‑party services</li>
            <li>Reverse engineer, scrape, or abuse the Service in a way that harms us or other users</li>
            <li>Use the Service to build a product that competes with AIveilix by copying its functionality or data</li>
            <li>Resell or sublicense access to the Service in a way we have not explicitly allowed</li>
          </ul>
          <p className="mt-3">
            We may remove content, suspend, or terminate accounts that breach this section, and we may report illegal activity to authorities.
          </p>
        </section>

        <section>
          <PolicySectionHeading theme={theme}>5. Your Data and Privacy</PolicySectionHeading>
          <p>
            We process your data as described in our{' '}
            <Link to="/privacy-policy" className={`font-medium hover:underline ${palette.accent}`}>Privacy Policy</Link>. You keep ownership of your documents and content. By using the Service, you give us the rights we need to store, process, and serve your content (including to power search and chat).
          </p>
          <p className="mt-3">
            You must not upload or process personal data (e.g. about others) unless you have the right to do so and comply with applicable data protection laws.
          </p>
        </section>

        <section>
          <PolicySectionHeading theme={theme}>6. Confidentiality and No Exposure</PolicySectionHeading>
          <p>You must keep confidential and not expose:</p>
          <ul className="mt-2 list-disc space-y-1 pl-6">
            <li>Your account credentials and API keys</li>
            <li>OAuth client secrets and tokens</li>
            <li>Any non‑public technical or commercial information we share with you about the Service</li>
          </ul>
          <p className="mt-3">
            You may disclose information only where required by law, and then only to the extent required, and you must try to get confidential treatment for that disclosure.
          </p>
        </section>

        <section>
          <PolicySectionHeading theme={theme}>7. Intellectual Property</PolicySectionHeading>
          <p>
            AIveilix's name, logo, software, and documentation are owned by us or our licensors. You do not get any ownership in them. You may use the Service only as allowed by these Terms.
          </p>
          <p className="mt-3">
            You retain rights in the content you upload. You grant us a license to use, store, and process that content to provide and improve the Service.
          </p>
        </section>

        <section>
          <PolicySectionHeading theme={theme}>8. Disclaimers</PolicySectionHeading>
          <p>
            The Service is provided “as is” and “as available”. We do not guarantee uninterrupted, error‑free, or secure operation. AI outputs (e.g. chat answers) are not legal, medical, or professional advice. You use them at your own risk.
          </p>
        </section>

        <section>
          <PolicySectionHeading theme={theme}>9. Limitation of Liability</PolicySectionHeading>
          <p>
            To the maximum extent permitted by law, we are not liable for indirect, incidental, special, or consequential damages, or loss of data or profits, arising from your use of the Service. Our total liability to you for any claim shall not exceed the amount you paid us in the twelve (12) months before the claim, or one hundred US dollars, whichever is greater.
          </p>
        </section>

        <section>
          <PolicySectionHeading theme={theme}>10. Termination</PolicySectionHeading>
          <p>
            We may suspend or terminate your access at any time for breach of these Terms or for operational or legal reasons. You may stop using the Service at any time. On termination, your right to use the Service ends. We may delete your data after a reasonable period.
          </p>
        </section>

        <section>
          <PolicySectionHeading theme={theme}>11. Changes to Terms</PolicySectionHeading>
          <p>
            We may update these Terms by posting a new version and updating the “Last updated” date. Material changes may be notified by email or in‑app notice. Continued use after changes means you accept the new Terms.
          </p>
        </section>

        <section>
          <PolicySectionHeading theme={theme}>12. Contact</PolicySectionHeading>
          <p>For questions about these Terms, contact us at:</p>
          <p className="mt-2">
            <strong className={palette.title}>Email:</strong>{' '}
            <a href="mailto:contact@aiveilix.com" className={`font-medium hover:underline ${palette.accent}`}>contact@aiveilix.com</a>
          </p>
          <p className="mt-3">We will respond to reasonable requests as soon as practicable.</p>
        </section>

        <div className={`mt-10 border-t pt-8 text-center text-sm ${palette.muted} ${theme === 'dark' ? 'border-white/10' : 'border-slate-200'}`}>
          <p>By using AIveilix, you confirm that you have read, understood, and agree to these Terms and Conditions.</p>
          <p className="mt-2">
            <Link to="/login" className={`font-medium hover:underline ${palette.accent}`}>Return to AIveilix</Link>
          </p>
        </div>
      </div>
    </PolicyShell>
  );
}

function TokushoPage({ theme, onToggleTheme }) {
  const palette = themeOptions[theme];
  const isDark = theme === 'dark';
  const tableBorder = isDark ? 'border-white/10' : 'border-slate-200';
  const rowBorder = isDark ? 'border-white/5' : 'border-slate-200/70';
  const headCellBg = isDark ? 'bg-white/5' : 'bg-slate-100/70';
  const tableBg = isDark ? 'bg-slate-950/40' : 'bg-white/70';

  return (
    <PolicyShell theme={theme} onToggleTheme={onToggleTheme}>
      <header className="mb-10">
        <h1 className={`text-3xl font-semibold tracking-tight sm:text-4xl ${palette.title}`}>特定商取引法に基づく表記</h1>
        <p className={`mt-1 text-sm ${palette.muted}`}>Specified Commercial Transactions Act Disclosure</p>
        <p className={`mt-1 text-sm ${palette.muted}`}>最終更新日: {POLICY_LAST_UPDATED}</p>
      </header>

      <div className={`space-y-8 leading-relaxed ${palette.text}`}>
        <section>
          <p>本サービスは、特定商取引法に基づき、以下の通り表記いたします。</p>
        </section>

        <section>
          <div className={`overflow-hidden rounded-2xl border ${tableBorder} ${tableBg}`}>
            <table className="w-full border-collapse">
              <tbody>
                {[
                  ['事業者名', <>株式会社 SAAD INTERNATIONAL</>],
                  ['代表者', <>CHAUDHARY ABDUL JABBAR JUTT</>],
                  ['所在地', <>〒455-0834<br />愛知県名古屋市港区神宮寺1丁目1303-1<br />レンダイスクォッター401</>],
                  ['電話番号', <>070-9114-6677</>],
                  ['メールアドレス', <a href="mailto:contact@aiveilix.com" className={`font-medium hover:underline ${palette.accent}`}>contact@aiveilix.com</a>],
                  ['販売価格', (
                    <>
                      <p>料金はサービス内の表示に従います。無料でご利用いただける場合があります。</p>
                      <p className={`mt-2 text-xs ${palette.muted}`}>※ 価格は予告なく変更される場合があります。</p>
                    </>
                  )],
                  ['商品代金以外の必要料金', (
                    <>
                      <ul className="list-disc space-y-1 pl-5">
                        <li>決済手数料：無料（当社負担）</li>
                        <li>送料：該当なし（デジタルサービス）</li>
                        <li>その他：なし</li>
                      </ul>
                      <p className={`mt-2 text-xs ${palette.muted}`}>※ お客様が利用するAI・埋め込み等の第三者サービスの利用料は、各提供者にお問い合わせください。</p>
                    </>
                  )],
                  ['代金の支払方法', <p>有料プランがある場合、サービス内で案内する方法（クレジットカード等）に従います。決済方法の詳細はお問い合わせください。</p>],
                  ['代金の支払時期', <p>有料プランがある場合、サービス内で案内する時期（例：月額の契約開始日等）に従います。</p>],
                  ['サービス提供時期', <p>アカウント登録後、即時にご利用いただけます。インターネット接続が必要です。</p>],
                  ['返品・交換・キャンセルについて', (
                    <>
                      <h3 className={`mb-2 font-semibold ${palette.title}`}>返金ポリシー</h3>
                      <p>本サービスはデジタルサービス（SaaS）のため、以下のとおりとします。</p>
                      <ul className="mt-2 list-disc space-y-1 pl-5">
                        <li><strong className={palette.title}>返金：</strong>返金は行いません。デジタルサービスの性質上、ご利用開始後・お支払い後の返金はお受けしておりません。</li>
                        <li><strong className={palette.title}>キャンセル：</strong>有料プランをご利用の場合は、サービス内の手順または contact@aiveilix.com へのご連絡でキャンセルできます。</li>
                      </ul>
                      <p className={`mt-2 text-xs ${palette.muted}`}>※ 返金に関する例外は法令で認められる場合を除き、ご対応しておりません。</p>
                    </>
                  )],
                  ['動作環境', (
                    <ul className="list-disc space-y-1 pl-5">
                      <li>インターネット接続</li>
                      <li>モダンなウェブブラウザ（Chrome、Firefox、Safari、Edgeの最新版）</li>
                      <li>JavaScript有効</li>
                    </ul>
                  )],
                  ['サービス内容', (
                    <>
                      <p>AIveilixは、お客様のドキュメントをアップロード・整理し、AIとチャットで対話できるドキュメント活用プラットフォームです。</p>
                      <ul className="mt-2 list-disc space-y-1 pl-5">
                        <li>ドキュメントをバケット単位で整理・管理</li>
                        <li>ファイルのアップロードと処理（PDF、画像等）</li>
                        <li>文書の意味検索（セマンティック検索）</li>
                        <li>ドキュメント内容に基づくAIチャット</li>
                        <li>APIキー・OAuthによるプログラムからの利用（オプション）</li>
                        <li>通知機能・会話履歴</li>
                      </ul>
                    </>
                  )],
                  ['個人情報の取り扱い', (
                    <p>
                      個人情報の取り扱いについては、<Link to="/privacy-policy" className={`font-medium hover:underline ${palette.accent}`}>プライバシーポリシー</Link>をご確認ください。
                    </p>
                  )],
                  ['お問い合わせ', (
                    <>
                      <p>ご不明な点やご質問がございましたら、以下の連絡先までお気軽にお問い合わせください。</p>
                      <p className="mt-2">
                        <strong className={palette.title}>メール:</strong>{' '}
                        <a href="mailto:contact@aiveilix.com" className={`font-medium hover:underline ${palette.accent}`}>contact@aiveilix.com</a><br />
                        <strong className={palette.title}>電話:</strong> 070-9114-6677<br />
                        <strong className={palette.title}>受付時間:</strong> 平日 9:00 - 18:00（日本時間）
                      </p>
                      <p className={`mt-2 text-xs ${palette.muted}`}>※ お問い合わせへの返信には、通常1-2営業日かかります。</p>
                    </>
                  )],
                ].map(([label, value], idx, arr) => (
                  <tr key={label} className={idx < arr.length - 1 ? `border-b ${rowBorder}` : ''}>
                    <th className={`w-48 border-r px-4 py-4 text-left align-top text-sm font-semibold sm:w-56 ${palette.title} ${headCellBg} ${rowBorder}`}>
                      {label}
                    </th>
                    <td className={`px-4 py-4 align-top text-sm ${palette.text}`}>{value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section>
          <PolicySectionHeading theme={theme}>免責事項</PolicySectionHeading>
          <p>当社は、本サービスの提供に関して、以下の事項について責任を負いません。</p>
          <ul className="mt-2 list-disc space-y-1 pl-6">
            <li>第三者のAI・埋め込み等サービスの可用性・性能・正確性</li>
            <li>お客様がアップロードするデータの内容・正確性</li>
            <li>APIキー・認証情報の管理</li>
            <li>ネットワーク・端末・ソフトウェアの不具合</li>
            <li>本サービスの一時的な停止・メンテナンス</li>
          </ul>
        </section>

        <section>
          <PolicySectionHeading theme={theme}>その他の重要事項</PolicySectionHeading>
          <ul className="list-disc space-y-1 pl-6">
            <li>本サービスの利用は、<Link to="/terms" className={`font-medium hover:underline ${palette.accent}`}>利用規約</Link>に従うものとします。</li>
            <li>本表記は日本の特定商取引法に基づくものです。海外からのご利用には当該国の法律が適用される場合があります。</li>
          </ul>
        </section>

        <div className={`mt-10 border-t pt-8 text-center text-sm ${palette.muted} ${theme === 'dark' ? 'border-white/10' : 'border-slate-200'}`}>
          <p>本表記は特定商取引法に基づき作成しています。最新情報は本ページでご確認ください。</p>
          <p className="mt-2">
            <Link to="/login" className={`font-medium hover:underline ${palette.accent}`}>Return to AIveilix</Link>
          </p>
        </div>
      </div>
    </PolicyShell>
  );
}

// ---------- Docs Page ----------

const DOCS_SECTIONS = [
  { id: 'quickstart', label: 'Quickstart' },
  { id: 'buckets', label: 'Buckets' },
  { id: 'uploading', label: 'Uploading files' },
  { id: 'chat', label: 'Chat' },
  { id: 'mcp', label: 'MCP' },
  { id: 'account', label: 'Account' },
  { id: 'faq', label: 'FAQ' },
];

function docsPalette(theme) {
  const isDark = theme === 'dark';
  return {
    isDark,
    bg: isDark ? 'bg-slate-950' : 'bg-slate-100',
    text: isDark ? 'text-slate-300' : 'text-slate-600',
    title: isDark ? 'text-white' : 'text-slate-900',
    muted: isDark ? 'text-slate-400' : 'text-slate-500',
    accent: isDark ? 'text-blue-400' : 'text-blue-600',
    border: isDark ? 'border-white/10' : 'border-slate-200',
    sidebarItem: isDark
      ? 'text-slate-400 hover:text-white'
      : 'text-slate-500 hover:text-slate-900',
    sidebarActive: isDark ? 'text-white' : 'text-slate-900',
    code: isDark ? 'bg-white/[0.06] text-slate-200' : 'bg-white text-slate-800 border border-slate-200',
    codeBlock: isDark ? 'bg-white/[0.03] border-white/10' : 'bg-white border-slate-200',
    callout: isDark ? 'border-white/10 bg-white/[0.02]' : 'border-slate-200 bg-white',
    link: isDark ? 'text-blue-400 hover:text-blue-300' : 'text-blue-600 hover:text-blue-700',
  };
}

function DocsSection({ theme, id, title, children }) {
  const p = docsPalette(theme);
  return (
    <section id={id} className="scroll-mt-20 pt-16 first:pt-0">
      <h2 className={`text-3xl font-semibold tracking-tight ${p.title}`}>{title}</h2>
      <div className={`mt-6 space-y-5 leading-7 ${p.text}`}>{children}</div>
    </section>
  );
}

function DocsCallout({ theme, children }) {
  const p = docsPalette(theme);
  return (
    <div className={`rounded-md border-l-2 px-4 py-3 text-sm leading-6 ${p.callout} ${p.isDark ? 'border-l-blue-400' : 'border-l-blue-500'}`}>
      <div className={p.text}>{children}</div>
    </div>
  );
}

function DocsChip({ theme, children }) {
  const p = docsPalette(theme);
  return (
    <code className={`rounded px-1.5 py-0.5 font-mono text-[0.85em] ${p.code}`}>
      {children}
    </code>
  );
}

function DocsUrlBlock({ theme, url }) {
  const p = docsPalette(theme);
  return (
    <pre className={`overflow-x-auto rounded-md border px-4 py-3 font-mono text-sm ${p.codeBlock} ${p.title}`}>
      <code>{url}</code>
    </pre>
  );
}

function DocsFaqItem({ theme, q, children }) {
  const p = docsPalette(theme);
  return (
    <details className={`group border-b py-4 ${p.border}`}>
      <summary className={`flex cursor-pointer list-none items-center justify-between gap-4 text-base font-medium ${p.title}`}>
        <span>{q}</span>
        <span className={`flex h-5 w-5 flex-none items-center justify-center text-sm transition group-open:rotate-45 ${p.muted}`}>
          +
        </span>
      </summary>
      <div className={`mt-3 text-sm leading-6 ${p.text}`}>
        {children}
      </div>
    </details>
  );
}

function DocsPage({ theme, onToggleTheme }) {
  const p = docsPalette(theme);
  const navigate = useNavigate();
  const [activeId, setActiveId] = useState(DOCS_SECTIONS[0].id);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible[0]) setActiveId(visible[0].target.id);
      },
      { rootMargin: '-80px 0px -70% 0px', threshold: 0 },
    );
    DOCS_SECTIONS.forEach((s) => {
      const el = document.getElementById(s.id);
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
  }, []);

  return (
    <main className={`min-h-[100dvh] ${p.bg} ${p.text}`}>
      {/* Top bar */}
      <header className="sticky top-0 z-30 bg-transparent backdrop-blur">
        <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-4">
          <Link to="/login" className="flex items-baseline gap-2">
            <span className={`text-base font-semibold tracking-tight ${p.title}`}>AIveilix</span>
            <span className={`text-sm ${p.muted}`}>docs</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link to="/login" className={`text-sm font-medium ${p.sidebarItem}`}>
              Sign in
            </Link>
            <button
              type="button"
              onClick={onToggleTheme}
              className={`text-sm font-medium ${p.sidebarItem}`}
            >
              {theme === 'dark' ? 'Light' : 'Dark'}
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto w-full max-w-7xl px-6">
        <div className="grid gap-12 lg:grid-cols-[14rem_minmax(0,1fr)]">
          {/* Sidebar */}
          <aside className="hidden lg:block">
            <nav className="sticky top-20 max-h-[calc(100dvh-5rem)] overflow-y-auto py-10">
              <p className={`mb-4 text-xs font-semibold uppercase tracking-wider ${p.muted}`}>Guide</p>
              <ul className="space-y-1">
                {DOCS_SECTIONS.map((s) => (
                  <li key={s.id}>
                    <a
                      href={`#${s.id}`}
                      className={`block py-1.5 text-sm transition ${activeId === s.id ? p.sidebarActive + ' font-medium' : p.sidebarItem}`}
                    >
                      {s.label}
                    </a>
                  </li>
                ))}
              </ul>
            </nav>
          </aside>

          {/* Content */}
          <article className="min-w-0 max-w-3xl py-10 lg:py-16">
            <header className="mb-12">
              <p className={`text-sm font-medium ${p.accent}`}>Documentation</p>
              <h1 className={`mt-2 text-4xl font-semibold tracking-tight ${p.title}`}>
                AIveilix docs
              </h1>
              <p className={`mt-4 text-lg leading-7 ${p.text}`}>
                A short, practical guide to AIveilix — create a bucket, upload documents, chat with them,
                and connect them to Claude, ChatGPT, or any other AI through MCP.
              </p>
            </header>

            {/* Mobile TOC */}
            <nav className={`mb-10 rounded-md border p-4 lg:hidden ${p.border}`}>
              <p className={`mb-2 text-xs font-semibold uppercase tracking-wider ${p.muted}`}>On this page</p>
              <ul className="flex flex-wrap gap-x-4 gap-y-1">
                {DOCS_SECTIONS.map((s) => (
                  <li key={s.id}>
                    <a href={`#${s.id}`} className={`text-sm ${p.sidebarItem}`}>
                      {s.label}
                    </a>
                  </li>
                ))}
              </ul>
            </nav>

            <DocsSection theme={theme} id="quickstart" title="Quickstart">
              <p>
                Four steps and you're live. Most people go from signup to a working MCP link in under five minutes.
              </p>
              <ol className={`mt-4 list-decimal space-y-3 pl-6 marker:font-medium ${p.text}`}>
                <li>
                  <strong className={p.title}>Create an account.</strong>{' '}
                  Sign up with email or Google. Verify your email and you'll land on the dashboard.
                </li>
                <li>
                  <strong className={p.title}>Create a bucket.</strong>{' '}
                  A bucket is your private knowledge vault. Click <DocsChip theme={theme}>New Bucket</DocsChip>, name it, and open it.
                </li>
                <li>
                  <strong className={p.title}>Upload your files.</strong>{' '}
                  Drag PDFs, documents, or images into the left panel. AIveilix reads them and prepares them for search and chat.
                </li>
                <li>
                  <strong className={p.title}>Chat or share with an AI.</strong>{' '}
                  Ask questions in the right‑side chat — or copy your MCP URL and paste it into Claude or ChatGPT so they can use your documents in real time.
                </li>
              </ol>
            </DocsSection>

            <DocsSection theme={theme} id="buckets" title="Buckets">
              <p>
                A <strong className={p.title}>bucket</strong> is your private knowledge space inside AIveilix.
                Think of it as a folder that doesn't forget — once you put documents in, they stay indexed and
                searchable, ready for chat or for any AI you connect.
              </p>
              <p>You can create as many buckets as your plan allows. A typical setup:</p>
              <ul className="list-disc space-y-1 pl-6">
                <li>One bucket per project or client</li>
                <li>One bucket for your personal research and notes</li>
                <li>One bucket for company handbooks or policies</li>
              </ul>
              <p>
                Inside a bucket you can organize files into <strong className={p.title}>categories</strong> to keep
                large libraries tidy. Renaming, deleting, or moving files is always available from the file list.
              </p>
              <DocsCallout theme={theme}>
                Each bucket is fully isolated. A chat or MCP connection scoped to one bucket can never see another bucket's files.
              </DocsCallout>
            </DocsSection>

            <DocsSection theme={theme} id="uploading" title="Uploading files">
              <p>
                Open a bucket and drop files into the upload zone on the left, or click to browse. You can upload one file or many at once.
              </p>
              <p>
                <strong className={p.title}>Supported formats:</strong> PDF, Word (DOCX), plain text, CSV, Markdown,
                and common image formats (PNG, JPG, WEBP). Scanned PDFs and images are also supported — AIveilix
                reads the text and any charts or diagrams inside them.
              </p>
              <p>Each file goes through three statuses in the file list:</p>
              <ul className="list-disc space-y-1 pl-6">
                <li><strong className={p.title}>Uploading</strong> — the file is being transferred</li>
                <li><strong className={p.title}>Processing</strong> — AIveilix is reading and indexing the content</li>
                <li><strong className={p.title}>Ready</strong> — searchable in chat and over MCP</li>
              </ul>
              <DocsCallout theme={theme}>
                Large PDFs (hundreds of pages) can take a couple of minutes. You can keep using the app while files are indexed in the background.
              </DocsCallout>
            </DocsSection>

            <DocsSection theme={theme} id="chat" title="Chat">
              <p>
                Every bucket has a chat panel on the right. Ask questions in plain language and AIveilix will pull
                the most relevant parts of your documents to answer you — with citations so you can trace where each answer came from.
              </p>
              <p>
                You can have multiple conversation <strong className={p.title}>threads</strong> per bucket (up to 20). Pin the important ones to the top.
              </p>

              <h3 className={`pt-2 text-xl font-semibold ${p.title}`}>What chat can do</h3>
              <ul className="list-disc space-y-2 pl-6">
                <li>
                  <strong className={p.title}>Document Q&amp;A.</strong>{' '}
                  Default mode. Ask anything and AIveilix searches every file in the bucket to compose an answer.
                </li>
                <li>
                  <strong className={p.title}>File‑scoped chat.</strong>{' '}
                  Type <DocsChip theme={theme}>@filename</DocsChip> in your message to focus the conversation on one specific file.
                </li>
                <li>
                  <strong className={p.title}>Web search mode.</strong>{' '}
                  Toggle the web icon on a thread to also pull in fresh information from the public web alongside your documents.
                </li>
                <li>
                  <strong className={p.title}>Speech to text.</strong>{' '}
                  Click the microphone in the message box to dictate instead of typing.
                </li>
              </ul>

              <DocsCallout theme={theme}>
                Every answer includes citations at the bottom — file names for document sources and domains for web sources. Click them to see exactly where the information came from.
              </DocsCallout>
            </DocsSection>

            <DocsSection theme={theme} id="mcp" title="MCP — connect to any AI">
              <p>
                <strong className={p.title}>MCP (Model Context Protocol)</strong> is the bridge that lets tools like
                Claude and ChatGPT use your AIveilix knowledge in real time. Instead of re‑uploading files to every
                new chat, you give the AI a single secure link and it can read your documents whenever it needs to.
              </p>

              <h3 className={`pt-2 text-xl font-semibold ${p.title}`}>Two kinds of links</h3>
              <p className={`text-sm ${p.muted}`}>Bucket URL — access a single bucket</p>
              <DocsUrlBlock theme={theme} url="https://mcp.aiveilix.com/bucket/<your-token>" />
              <p className={`text-sm ${p.muted}`}>Account URL — manage all your buckets</p>
              <DocsUrlBlock theme={theme} url="https://mcp.aiveilix.com/account/<your-token>" />

              <p>
                Open a bucket, click <DocsChip theme={theme}>MCP</DocsChip>, and copy the link. The link contains a
                secret token, so treat it like a password: anyone with the link can read that bucket.
              </p>

              <h3 className={`pt-2 text-xl font-semibold ${p.title}`}>How to use it</h3>
              <ul className="list-disc space-y-1 pl-6">
                <li>In <strong className={p.title}>Claude Desktop</strong>: add it as a Custom Connector / MCP server in settings.</li>
                <li>In <strong className={p.title}>ChatGPT</strong> and other clients that support MCP: paste it where the client asks for an MCP server URL.</li>
                <li>From your own tools: any client that speaks MCP can connect — no extra setup on our side.</li>
              </ul>

              <h3 className={`pt-2 text-xl font-semibold ${p.title}`}>What the AI can do</h3>
              <ul className="list-disc space-y-1 pl-6">
                <li>Search your bucket for relevant passages</li>
                <li>Ask deeper questions across all your files</li>
                <li>List files and categories</li>
                <li>Open a specific file and read its content</li>
                <li>From the Account URL: create, list, or delete buckets too</li>
              </ul>

              <DocsCallout theme={theme}>
                If a link is ever exposed, open the MCP panel and regenerate it. The old link stops working immediately and a new one is issued.
              </DocsCallout>
            </DocsSection>

            <DocsSection theme={theme} id="account" title="Account & notifications">
              <p>Click your avatar in the dashboard to open profile and account settings. From there you can:</p>
              <ul className="list-disc space-y-1 pl-6">
                <li>Update your name and profile photo</li>
                <li>Change your password</li>
                <li>Connect or disconnect Google sign‑in</li>
                <li>Turn on two‑factor authentication (recommended)</li>
                <li>Review your plan, usage, and billing history</li>
                <li>Delete your account</li>
              </ul>
              <p>
                <strong className={p.title}>Notifications</strong> appear in the bell icon on the dashboard —
                file processed, sign‑in alerts, billing updates. You can choose which categories you receive.
              </p>
            </DocsSection>

            <DocsSection theme={theme} id="faq" title="FAQ">
              <div className={`border-t ${p.border}`}>
                <DocsFaqItem theme={theme} q="Who can see my documents?">
                  Only you. Documents in a bucket are private to your account. They're never shared with other users,
                  and they're never used to train public AI models. Sharing only happens when you copy an MCP link or
                  invite a teammate — both fully under your control.
                </DocsFaqItem>

                <DocsFaqItem theme={theme} q="My file is stuck on “Processing” — what's happening?">
                  Larger files (long PDFs, image‑heavy documents) take longer because AIveilix is reading the full
                  content so the AI can find anything inside it. If a file stays in processing for more than a few
                  minutes, refresh the page; if it still doesn't move, contact support.
                </DocsFaqItem>

                <DocsFaqItem theme={theme} q="Can I delete a file or a whole bucket?">
                  Yes. Files can be deleted from the file list. Buckets can be deleted from the dashboard.
                  Deletion is immediate and the data is removed from search and from MCP right away.
                </DocsFaqItem>

                <DocsFaqItem theme={theme} q="How does billing work?">
                  You start on a free tier with a generous allowance for files and storage. If you need more,
                  upgrade from the billing panel in your profile. Paid plans renew monthly and can be cancelled
                  any time — your data stays put even after you downgrade.
                </DocsFaqItem>

                <DocsFaqItem theme={theme} q="What if I lose my MCP link?">
                  Open the MCP panel inside the bucket and regenerate it. A new link is created and the previous one is immediately invalidated.
                </DocsFaqItem>

                <DocsFaqItem theme={theme} q="I forgot my password.">
                  Use the “Forgot password?” link on the login page. We'll email you a 6‑digit code so you can set a new one.
                </DocsFaqItem>

                <DocsFaqItem theme={theme} q="Can I delete my account?">
                  Yes — from your profile settings. Account deletion removes your buckets, files, and chat history.
                </DocsFaqItem>

                <DocsFaqItem theme={theme} q="Where do I get help?">
                  Email <a href="mailto:contact@aiveilix.com" className={p.link}>contact@aiveilix.com</a> and we'll get back to you.
                  Include screenshots if something looks wrong — it helps us answer faster.
                </DocsFaqItem>
              </div>
            </DocsSection>

            {/* Footer */}
            <div className={`mt-20 border-t pt-10 ${p.border}`}>
              <p className={`text-sm ${p.muted}`}>Ready to start?</p>
              <div className="mt-3 flex flex-wrap items-center gap-x-6 gap-y-2">
                <button
                  type="button"
                  onClick={() => navigate('/signup')}
                  className={`text-base font-medium ${p.link}`}
                >
                  Create an account →
                </button>
                <button
                  type="button"
                  onClick={() => navigate('/login')}
                  className={`text-base font-medium ${p.sidebarItem}`}
                >
                  Open the app
                </button>
              </div>
            </div>
          </article>
        </div>
      </div>
    </main>
  );
}

function NotFoundPage({ theme, onToggleTheme }) {
  const palette = themeOptions[theme];
  const navigate = useNavigate();
  const hasSession = typeof window !== 'undefined' && Boolean(window.sessionStorage.getItem('access_token'));

  return (
    <main className={`relative min-h-[100dvh] overflow-hidden transition-colors duration-300 ${palette.app}`}>
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute left-[-8rem] top-20 h-72 w-72 rounded-full bg-blue-500/12 blur-3xl" />
        <div className="absolute bottom-[-6rem] right-[-4rem] h-80 w-80 rounded-full bg-cyan-400/10 blur-3xl" />
        <div className={`absolute left-1/2 top-1/2 h-[32rem] w-[32rem] -translate-x-1/2 -translate-y-1/2 rounded-full border ${theme === 'dark' ? 'border-white/5' : 'border-blue-100'} opacity-80`} />
      </div>

      <div className="relative mx-auto flex min-h-[100dvh] w-full max-w-7xl flex-col px-4 py-6 sm:px-6 sm:py-8">
        <div>
          <div>
            <p className={`text-xs font-semibold uppercase tracking-[0.35em] ${palette.accent}`}>Aiveilix</p>
            <p className={`mt-3 text-sm ${palette.text}`}>The page you tried to open does not exist.</p>
          </div>
        </div>

        <div className="flex flex-1 items-center justify-center py-10">
          <section className="w-full max-w-3xl px-6 py-8 text-center sm:px-10 sm:py-12">
            <div className={`mx-auto inline-flex rounded-full border px-4 py-2 text-xs font-semibold uppercase tracking-[0.28em] ${palette.secondary}`}>
              Error 404
            </div>
            <p className={`mt-6 text-[5.5rem] font-semibold leading-none tracking-[-0.06em] sm:text-[8rem] ${palette.title}`}>404</p>
            <h1 className={`mt-4 text-3xl font-semibold tracking-tight sm:text-4xl ${palette.title}`}>Page Not Found</h1>
            <p className={`mx-auto mt-4 max-w-xl text-sm leading-7 sm:text-base ${palette.text}`}>
              The route is invalid, the page was moved, or the URL was typed incorrectly. Use one of the actions below to get back into AIveilix.
            </p>

            <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <button
                type="button"
                onClick={() => navigate(hasSession ? '/dashboard' : '/login')}
                className={`min-w-44 rounded-2xl px-5 py-3 text-sm font-semibold transition ${palette.primary}`}
              >
                {hasSession ? 'Back to Dashboard' : 'Go to Login'}
              </button>
              <button
                type="button"
                onClick={() => navigate(-1)}
                className={`min-w-44 rounded-2xl border px-5 py-3 text-sm font-semibold transition ${palette.secondary}`}
              >
                Go Back
              </button>
            </div>

            <div className={`mt-10 grid gap-3 text-left sm:grid-cols-3 ${theme === 'dark' ? 'text-slate-300' : 'text-slate-600'}`}>
              {[
                ['Dashboard', 'See buckets, stats, and workspace activity.'],
                ['Buckets', 'Open your documents and continue working.'],
                ['Auth', 'Log in again if your session expired.'],
              ].map(([label, copy]) => (
                <div key={label} className={`rounded-[1.25rem] border px-4 py-4 ${theme === 'dark' ? 'border-white/10 bg-white/[0.03]' : 'border-slate-200/90 bg-white/72'}`}>
                  <p className={`text-sm font-semibold ${palette.title}`}>{label}</p>
                  <p className="mt-2 text-xs leading-6">{copy}</p>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}

// ---------- Onboarding Page ----------

function OnboardingPage({ theme, onToggleTheme }) {
  const palette = themeOptions[theme];
  const navigate = useNavigate();

  return (
    <main className={`relative h-[100dvh] transition-colors duration-300 ${palette.app}`}>
      <OnboardingModal theme={theme} onDone={() => navigate('/dashboard')} />
    </main>
  );
}

// ---------- Shared helpers ----------

function generateThreadTitle(text) {
  const clean = text.trim().replace(/\n+/g, ' ');
  const firstSentence = clean.match(/^[^.!?\n]{4,}/)?.[0] || clean;
  const short = firstSentence.length > 48
    ? firstSentence.slice(0, 48).replace(/\s+\S*$/, '') + '…'
    : firstSentence;
  return short.charAt(0).toUpperCase() + short.slice(1);
}

function renderUserMessage(content) {
  // Split on @filename patterns and render file refs as inline chips
  const parts = content.split(/(@\S+)/g);
  if (parts.length === 1) return content;
  return parts.map((part, i) => {
    if (part.startsWith('@') && part.length > 1) {
      return (
        <span key={i} className="mx-0.5 inline-flex items-center rounded-full bg-white/20 px-2 py-0.5 text-xs font-medium">
          {part.slice(1)}
        </span>
      );
    }
    return part;
  });
}

const INLINE_MD_RE = /\*\*([^*]+)\*\*|\*([^*]+)\*|`([^`]+)`|\[([^\]]+)\]\(([^)]+)\)/g;

function renderInlineMarkdown(text, keyPrefix) {
  const nodes = [];
  let last = 0;
  let match;
  let i = 0;
  INLINE_MD_RE.lastIndex = 0;
  while ((match = INLINE_MD_RE.exec(text)) !== null) {
    if (match.index > last) nodes.push(text.slice(last, match.index));
    const key = `${keyPrefix}-${i++}`;
    if (match[1] != null) nodes.push(<strong key={key} className="font-semibold">{match[1]}</strong>);
    else if (match[2] != null) nodes.push(<em key={key}>{match[2]}</em>);
    else if (match[3] != null) {
      nodes.push(
        <code key={key} className="rounded px-1 py-0.5 text-[0.9em] font-mono bg-black/10 dark:bg-white/10">
          {match[3]}
        </code>,
      );
    } else if (match[4] != null) {
      nodes.push(
        <a key={key} href={match[5]} target="_blank" rel="noopener noreferrer" className="underline underline-offset-2 hover:opacity-80">
          {match[4]}
        </a>,
      );
    }
    last = INLINE_MD_RE.lastIndex;
  }
  if (last < text.length) nodes.push(text.slice(last));
  return nodes.length ? nodes : [text];
}

let mermaidPromise = null;
const loadMermaid = () => {
  if (!mermaidPromise) {
    mermaidPromise = import('mermaid').then(m => {
      const mermaid = m.default;
      mermaid.initialize({
        startOnLoad: false,
        securityLevel: 'strict',
        fontFamily: 'inherit',
      });
      return mermaid;
    });
  }
  return mermaidPromise;
};

const buildMermaidThemed = (code, isDark) => {
  const init = isDark
    ? `%%{init: {'theme':'base','themeVariables':{'background':'#020617','primaryColor':'#0e2660','primaryTextColor':'#e2e8f0','primaryBorderColor':'#3b82f6','lineColor':'#60a5fa','secondaryColor':'#091a44','tertiaryColor':'#020617','fontFamily':'inherit'}}}%%\n`
    : `%%{init: {'theme':'base','themeVariables':{'background':'#ffffff','primaryColor':'#dbeafe','primaryTextColor':'#0f172a','primaryBorderColor':'#2563eb','lineColor':'#3b82f6','secondaryColor':'#eff5ff','tertiaryColor':'#f8fafc','fontFamily':'inherit'}}}%%\n`;
  return init + code;
};

let mermaidIdCounter = 0;
function MermaidDiagram({ code, isDark = true }) {
  const ref = useRef(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    loadMermaid()
      .then(async (mermaid) => {
        if (cancelled || !ref.current) return;
        const id = `mmd-${++mermaidIdCounter}`;
        try {
          const { svg } = await mermaid.render(id, buildMermaidThemed(code, isDark));
          if (!cancelled && ref.current) ref.current.innerHTML = svg;
        } catch (e) {
          if (!cancelled) setError(String(e?.message || e));
        }
      })
      .catch((e) => { if (!cancelled) setError(String(e?.message || e)); });
    return () => { cancelled = true; };
  }, [code, isDark]);

  if (error) {
    return (
      <div className={`rounded-lg border p-3 text-xs ${isDark ? 'border-red-500/30 bg-red-500/5 text-red-300' : 'border-red-300 bg-red-50 text-red-700'}`}>
        Mermaid render error: {error}
        <pre className="mt-2 whitespace-pre-wrap font-mono text-[11px] opacity-80">{code}</pre>
      </div>
    );
  }
  return (
    <div
      ref={ref}
      className={`flex justify-center overflow-x-auto rounded-lg border p-3 ${isDark ? 'border-white/10 bg-[#020617]' : 'border-slate-200 bg-white'}`}
    />
  );
}

const buildMarkdownComponents = (isDark) => {
  const inlineCode = isDark ? 'bg-white/10 text-blue-200' : 'bg-slate-100 text-blue-700';
  const blockCode = isDark ? 'bg-black/30 text-slate-100' : 'bg-slate-100 text-slate-800';
  const linkCls = isDark
    ? 'text-blue-400 decoration-blue-400/40 hover:decoration-blue-400'
    : 'text-blue-600 decoration-blue-600/40 hover:decoration-blue-600';
  const tableBorder = isDark ? 'border-white/10' : 'border-slate-200';
  const theadBg = isDark ? 'bg-white/[0.04]' : 'bg-slate-50';
  const thText = isDark ? 'text-white/90' : 'text-slate-700';
  const tdText = isDark ? 'text-white/85' : 'text-slate-700';
  const bqBorder = isDark ? 'border-white/25' : 'border-slate-300';

  return {
    h1: ({ node, ...p }) => <h1 className="mt-2 text-lg font-semibold" {...p} />,
    h2: ({ node, ...p }) => <h2 className="mt-2 text-lg font-semibold" {...p} />,
    h3: ({ node, ...p }) => <h3 className="mt-2 text-base font-semibold" {...p} />,
    h4: ({ node, ...p }) => <h4 className="mt-2 text-base font-semibold" {...p} />,
    h5: ({ node, ...p }) => <h5 className="mt-2 text-sm font-semibold" {...p} />,
    h6: ({ node, ...p }) => <h6 className="mt-2 text-sm font-semibold" {...p} />,
    p:  ({ node, ...p }) => <p className="whitespace-pre-wrap break-words leading-7" {...p} />,
    ul: ({ node, ...p }) => <ul className="my-1 list-disc space-y-1 pl-5" {...p} />,
    ol: ({ node, ...p }) => <ol className="my-1 list-decimal space-y-1 pl-5" {...p} />,
    li: ({ node, ...p }) => <li className="leading-7" {...p} />,
    hr: ({ node, ...p }) => <hr className={`my-3 ${tableBorder}`} {...p} />,
    a:  ({ node, ...p }) => <a className={`underline underline-offset-2 ${linkCls}`} target="_blank" rel="noopener noreferrer" {...p} />,
    strong: ({ node, ...p }) => <strong className="font-semibold" {...p} />,
    em: ({ node, ...p }) => <em className="italic" {...p} />,
    blockquote: ({ node, ...p }) => <blockquote className={`my-2 border-l-2 pl-3 italic opacity-90 ${bqBorder}`} {...p} />,
    code: ({ node, inline, className, children, ...rest }) => (
      inline === false
        ? <code className={`block whitespace-pre overflow-x-auto rounded-md px-3 py-2 font-mono text-[13px] ${blockCode} ${className || ''}`} {...rest}>{children}</code>
        : <code className={`rounded px-1 py-0.5 font-mono text-[0.9em] ${inlineCode}`} {...rest}>{children}</code>
    ),
    table: ({ node, ...p }) => (
      <div className={`my-2 overflow-x-auto rounded-lg border ${tableBorder}`}>
        <table className="w-full border-collapse text-sm" {...p} />
      </div>
    ),
    thead: ({ node, ...p }) => <thead className={theadBg} {...p} />,
    tbody: ({ node, ...p }) => <tbody {...p} />,
    tr: ({ node, ...p }) => <tr className={`border-b last:border-b-0 ${tableBorder}`} {...p} />,
    th: ({ node, style, ...p }) => (
      <th
        style={style}
        className={`px-3 py-2 text-left font-semibold border-r last:border-r-0 ${thText} ${tableBorder}`}
        {...p}
      />
    ),
    td: ({ node, style, ...p }) => (
      <td
        style={style}
        className={`px-3 py-2 align-top border-r last:border-r-0 ${tdText} ${tableBorder}`}
        {...p}
      />
    ),
  };
};

const MARKDOWN_COMPONENTS_DARK = buildMarkdownComponents(true);
const MARKDOWN_COMPONENTS_LIGHT = buildMarkdownComponents(false);

function renderAssistantLines(lines, keyPrefix = 'assistant', isDark = true) {
  const text = Array.isArray(lines) ? lines.join('\n') : String(lines || '');
  return (
    <ReactMarkdown
      key={keyPrefix}
      remarkPlugins={[remarkGfm]}
      components={isDark ? MARKDOWN_COMPONENTS_DARK : MARKDOWN_COMPONENTS_LIGHT}
    >
      {text}
    </ReactMarkdown>
  );
}

function splitAssistantBlocks(text) {
  const body = text.replace(/^Assistant:\s*/i, '');
  const blocks = [];
  const codeRe = /```([A-Za-z0-9_+#.-]*)\n?([\s\S]*?)```/g;
  let last = 0;
  let match;

  while ((match = codeRe.exec(body)) !== null) {
    if (match.index > last) {
      blocks.push(...splitAssistantTextBlocks(body.slice(last, match.index)));
    }
    blocks.push({
      type: 'code',
      language: (match[1] || 'text').trim() || 'text',
      content: match[2].replace(/\n$/, ''),
    });
    last = codeRe.lastIndex;
  }
  if (last < body.length) {
    blocks.push(...splitAssistantTextBlocks(body.slice(last)));
  }
  return blocks.filter(block => block.type !== 'text' || block.content.trim());
}

function splitAssistantTextBlocks(text) {
  const lines = text.split('\n');
  const blocks = [];
  let buffer = [];

  const flushText = () => {
    if (buffer.length) {
      blocks.push({ type: 'text', content: buffer.join('\n') });
      buffer = [];
    }
  };

  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    if (!/^\s*\d+[.)]\s+/.test(line)) {
      buffer.push(line);
      continue;
    }

    const candidate = [line];
    let numberedCount = 1;
    let hasIndentedDetail = false;
    let j = i + 1;
    while (j < lines.length) {
      const next = lines[j];
      if (/^\s*\d+[.)]\s+/.test(next)) {
        numberedCount += 1;
        candidate.push(next);
        j += 1;
        continue;
      }
      if (!next.trim()) {
        candidate.push(next);
        j += 1;
        continue;
      }
      if (/^\s{2,}\S/.test(next)) {
        hasIndentedDetail = true;
        candidate.push(next);
        j += 1;
        continue;
      }
      break;
    }

    if (numberedCount >= 2 && hasIndentedDetail) {
      flushText();
      blocks.push({ type: 'preformatted', content: candidate.join('\n').trimEnd() });
      i = j - 1;
    } else {
      buffer.push(line);
    }
  }
  flushText();
  return blocks;
}

function escapeHtml(value) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function renderAssistantMessage(text, options = {}) {
  const { onCopy, copiedKey, copyKeyPrefix = 'assistant-message', isDark = false } = options;
  const body = text.replace(/^Assistant:\s*/i, '');
  const blocks = splitAssistantBlocks(body);
  const cardTone = isDark
    ? 'border-white/10 bg-[#020617] text-slate-100 shadow-black/40'
    : 'border-slate-200 bg-white text-slate-900 shadow-slate-200/70';
  const cardHeaderTone = isDark
    ? 'border-white/10 bg-white/[0.03] text-white/70'
    : 'border-slate-200 bg-slate-50 text-slate-500';
  const iconButtonTone = isDark
    ? 'text-white/70 hover:bg-white/10 hover:text-white'
    : 'text-slate-500 hover:bg-slate-100 hover:text-slate-900';
  const copyIconButton = (key, label, value) => (
    <button
      type="button"
      title={copiedKey === key ? 'Copied' : label}
      onClick={() => onCopy?.(value, key)}
      className={`inline-flex h-8 w-8 items-center justify-center rounded-full transition ${iconButtonTone}`}
    >
      <CopyIcon />
    </button>
  );

  return (
    <div className="space-y-3">
      {blocks.map((block, blockIdx) => {
        if (block.type === 'code' || block.type === 'preformatted') {
          const key = `${copyKeyPrefix}-block-${blockIdx}`;
          const lang = (block.language || '').toLowerCase();
          const label = block.type === 'code' ? (block.language || '').toUpperCase() : '';
          const content = block.content.trimEnd();
          const isMermaid = lang === 'mermaid';
          return (
            <div key={key} className={`overflow-hidden rounded-2xl border shadow-sm ${cardTone}`}>
              <div className={`flex items-center justify-between border-b px-4 py-2 ${cardHeaderTone}`}>
                <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide">
                  {block.type === 'code' && <span className="text-base leading-none">&lt;/&gt;</span>}
                  {label && <span>{isMermaid ? 'DIAGRAM' : label}</span>}
                </div>
                {onCopy && copyIconButton(key, 'Copy block', content)}
              </div>
              {isMermaid ? (
                <div className="px-4 py-4">
                  <MermaidDiagram code={content} isDark={isDark} />
                </div>
              ) : (
                <SyntaxHighlighter
                  language={lang || 'text'}
                  style={isDark ? oneDark : oneLight}
                  PreTag="pre"
                  customStyle={{
                    margin: 0,
                    padding: '1rem',
                    background: 'transparent',
                    fontSize: '13px',
                    lineHeight: '1.6',
                    maxHeight: '28rem',
                    overflow: 'auto',
                  }}
                  codeTagProps={{ className: 'font-mono' }}
                >
                  {content}
                </SyntaxHighlighter>
              )}
            </div>
          );
        }
        return (
          <div key={`${copyKeyPrefix}-text-${blockIdx}`} className="space-y-2">
            {renderAssistantLines(block.content.split('\n'), `${copyKeyPrefix}-${blockIdx}`, isDark)}
          </div>
        );
      })}
    </div>
  );
}

function parseAssistantContent(content) {
  const stripUsedMarker = (value) => value
    .replace(/(?:^|\n)\s*USED\s*:\s*(?:none|[A-Z0-9,#\s]+)\s*$/i, '')
    .trim();
  const sep = '\n\n---\n\nSources:';
  const idx = content.indexOf(sep);
  if (idx === -1) return { text: stripUsedMarker(content), sources: [] };
  const text = stripUsedMarker(content.slice(0, idx));
  const block = content.slice(idx + sep.length).trim();
  if (!block || block.startsWith('No document')) return { text, sources: [] };
  const sources = block.split('\n').map(l => l.trim()).filter(Boolean).map(label => {
    if (label.startsWith('[web]') || label.startsWith('🌐')) {
      const raw = label.replace(/^(\[web\]|🌐)\s*/, '').trim();
      return { kind: 'web', label: raw, url: `https://${raw}` };
    }
    if (label.startsWith('[memory]')) {
      return { kind: 'memory', label: label.replace(/^\[memory\]\s*/, '').trim() };
    }
    if (label.startsWith('[general]')) {
      return { kind: 'general', label: label.replace(/^\[general\]\s*/, '').trim() };
    }
    const docLabel = label.replace(/^(\[doc\]|📄)\s*/, '').trim();
    const pageMatch = docLabel.match(/^(.*?)\s+—\s+Page\s+(\d+)$/i);
    const overviewMatch = docLabel.match(/^(.*?)\s+—\s+Overview$/i);
    if (pageMatch) {
      return {
        kind: 'doc',
        label: docLabel,
        fileName: pageMatch[1].trim(),
        page: Number(pageMatch[2]),
      };
    }
    if (overviewMatch) {
      return {
        kind: 'doc',
        label: docLabel,
        fileName: overviewMatch[1].trim(),
        page: null,
        isOverview: true,
      };
    }
    return { kind: 'doc', label: docLabel };
  });
  const seen = new Set();
  const uniqueSources = sources.filter((s) => {
    const key = s.kind === 'web'
      ? `web:${s.url}`
      : s.kind === 'doc'
        ? `doc:${s.fileName ?? s.label}:${s.page ?? (s.isOverview ? 'overview' : '')}`
        : `${s.kind}:${s.label}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
  return { text, sources: uniqueSources };
}

function fmtFileSize(bytes) {
  if (!bytes) return '0 B';
  if (bytes >= 1e9) return `${(bytes / 1e9).toFixed(1)} GB`;
  if (bytes >= 1e6) return `${(bytes / 1e6).toFixed(1)} MB`;
  if (bytes >= 1e3) return `${(bytes / 1e3).toFixed(0)} KB`;
  return `${bytes} B`;
}

function fmtMimeType(mime, name) {
  if (name) {
    const ext = name.split('.').pop().toUpperCase();
    if (ext && ext.length <= 5) return ext;
  }
  if (!mime) return 'FILE';
  const map = {
    'application/pdf': 'PDF',
    'application/msword': 'DOC',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'DOCX',
    'text/plain': 'TXT',
    'text/csv': 'CSV',
    'application/zip': 'ZIP',
    'image/png': 'PNG',
    'image/jpeg': 'JPG',
    'image/gif': 'GIF',
    'image/webp': 'WEBP',
  };
  return map[mime] || mime.split('/').pop().toUpperCase().slice(0, 6);
}

// ---------- Dashboard helpers ----------

function fmtStorage(gb) {
  if (gb < 0.01) return '0 GB';
  return `${gb.toFixed(2)} GB`;
}

function fmtBucketStorage(storageBytes, storageGb = null) {
  const bytes = Number(storageBytes);
  if (Number.isFinite(bytes) && bytes >= 0) {
    if (bytes >= 1024 ** 3) return `${(bytes / (1024 ** 3)).toFixed(2)} GB`;
    if (bytes >= 1024 ** 2) return `${(bytes / (1024 ** 2)).toFixed(2)} MB`;
    if (bytes >= 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${bytes.toFixed(0)} B`;
  }

  const gb = Number(storageGb) || 0;
  if (gb >= 1) return `${gb.toFixed(2)} GB`;
  return `${(gb * 1024).toFixed(2)} MB`;
}

const LIMIT_FIELD_LABELS = {
  max_users: 'Seats',
  max_buckets: 'Buckets',
  max_documents: 'Documents',
  max_pages: 'Pages',
  max_storage_bytes: 'Storage',
  max_chat_messages: 'AI chats / month',
  mcp_rate_per_min: 'MCP req / min',
  max_images: 'Visuals',
  max_file_size_bytes: 'Max file size',
};

const REQUESTABLE_LIMIT_FIELDS = [
  'max_documents',
  'max_pages',
  'max_storage_bytes',
  'max_chat_messages',
  'max_buckets',
  'max_users',
  'max_images',
];

function fmtBytes(bytes) {
  const value = Number(bytes) || 0;
  if (value >= 1024 ** 4) return `${(value / (1024 ** 4)).toFixed(2)} TB`;
  if (value >= 1024 ** 3) return `${(value / (1024 ** 3)).toFixed(2)} GB`;
  if (value >= 1024 ** 2) return `${(value / (1024 ** 2)).toFixed(2)} MB`;
  if (value >= 1024) return `${(value / 1024).toFixed(2)} KB`;
  return `${value} B`;
}

function fmtLimitValue(field, value) {
  if (field === 'max_storage_bytes' || field === 'max_file_size_bytes') return fmtBytes(value);
  return Number(value || 0).toLocaleString();
}

function fmtDate(iso) {
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function fmtTime(iso) {
  const d = new Date(iso);
  const diff = Date.now() - d.getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

function toMonthInputValue(dateLike) {
  const value = dateLike instanceof Date ? dateLike : new Date(dateLike);
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, '0');
  return `${year}-${month}`;
}

function shiftMonthInputValue(monthValue, delta) {
  const [year, month] = monthValue.split('-').map(Number);
  return toMonthInputValue(new Date(year, (month - 1) + delta, 1));
}

function formatMonthInputValue(monthValue) {
  const [year, month] = monthValue.split('-').map(Number);
  return new Date(year, month - 1, 1).toLocaleDateString('en-US', {
    month: 'long',
    year: 'numeric',
  });
}

function MultiLineChart({ data, theme }) {
  const [hoverIndex, setHoverIndex] = useState(null);
  const isDark = theme === 'dark';
  const W = 900;
  const H = 320;
  const padL = 10;
  const padR = 10;
  const padT = 14;
  const padB = 34;
  const pointPadding = 18;
  const chartW = W - padL - padR;
  const chartH = H - padT - padB;
  const plotTop = padT + pointPadding;
  const plotBottom = padT + chartH - pointPadding;
  const plotHeight = plotBottom - plotTop;

  const safe = data && data.length > 0
    ? data
    : Array(6).fill({ month: '', storage_gb: 0, files: 0, buckets: 0 });
  const n = safe.length;

  const series = [
    { key: 'buckets', label: 'Buckets', color: '#10B981', dash: '0', axis: 'count' },
    { key: 'files', label: 'Files', color: '#8B5CF6', dash: '8 7', axis: 'count' },
    { key: 'storage_gb', label: 'Storage (GB)', color: '#3B82F6', dash: '0', axis: 'storage' },
  ];
  const renderSeries = [series[2], series[1], series[0]];
  const countSeries = series.filter(s => s.axis === 'count');
  const countMax = Math.max(
    ...safe.flatMap(d => countSeries.map(s => Number(d[s.key]) || 0)),
    1
  );
  const storageMax = Math.max(...safe.map(d => Number(d.storage_gb) || 0), 0.001);

  function xPos(i) {
    if (n <= 1) return padL + chartW / 2;
    return padL + (i / (n - 1)) * chartW;
  }

  function buildPoints(seriesItem) {
    const { key, axis } = seriesItem;
    const max = axis === 'storage' ? storageMax : countMax;
    return safe.map((d, i) => {
      const x = xPos(i);
      const ratio = (Number(d[key]) || 0) / max;
      const baseY = plotBottom - ratio * plotHeight;
      const y = Math.max(padT + 6, Math.min(padT + chartH - 6, baseY));
      return { x, y };
    });
  }

  const gridColor = isDark ? 'rgba(255,255,255,0.05)' : 'rgba(15,23,42,0.05)';
  const labelColor = isDark ? '#475569' : '#94a3b8';
  const hoverLineColor = isDark ? 'rgba(148,163,184,0.18)' : 'rgba(15,23,42,0.14)';
  const tooltipBg = isDark ? 'rgba(10,14,32,0.96)' : 'rgba(255,255,255,0.98)';
  const tooltipBorder = isDark ? 'rgba(96,165,250,0.25)' : 'rgba(59,130,246,0.22)';
  const tooltipText = isDark ? '#E5E7EB' : '#0F172A';
  const axisTextColor = isDark ? '#64748b' : '#94a3b8';

  const monthLabels = safe.map(d => {
    if (!d.month) return '';
    const parts = String(d.month).split('-');
    const dt = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, 1);
    return dt.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
  });

  const lastEntry = data && data.length > 0 ? data[data.length - 1] : null;
  const hoverEntry = hoverIndex != null ? safe[hoverIndex] : null;
  const hoverLabel = hoverEntry?.month
    ? (() => {
        const parts = String(hoverEntry.month).split('-');
        const dt = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, 1);
        return dt.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
      })()
    : '';
  const hoverX = hoverIndex != null ? xPos(hoverIndex) : null;
  const hoverBandWidth = n > 1 ? chartW / (n - 1) : chartW;
  const tooltipWidth = 178;
  const tooltipHeight = 100;
  const tooltipX = hoverX == null
    ? padL
    : Math.max(padL, Math.min(hoverX - tooltipWidth / 2, padL + chartW - tooltipWidth));
  const tooltipY = padT + 12;

  return (
    <div className="w-full">
      <div className="mb-5 flex flex-wrap gap-6">
        {series.map(s => (
          <div key={s.key} className="flex items-center gap-2.5">
            <span className="inline-block h-[3px] w-7 rounded-full" style={{ background: s.color }} />
            <span className="text-[13px] font-medium" style={{ color: labelColor }}>{s.label}</span>
            {lastEntry && (
              <span className="text-[13px] font-semibold" style={{ color: s.color }}>
                {s.key === 'storage_gb'
                  ? `${Number(lastEntry.storage_gb).toFixed(2)} GB`
                  : lastEntry[s.key]}
              </span>
            )}
          </div>
        ))}
      </div>

      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="w-full"
        style={{ height: 250 }}
        aria-hidden="true"
        onMouseLeave={() => setHoverIndex(null)}
      >
        {[0, 0.25, 0.5, 0.75, 1].map((t, i) => (
          <line
            key={i}
            x1={padL} y1={padT + chartH * (1 - t)}
            x2={padL + chartW} y2={padT + chartH * (1 - t)}
            stroke={gridColor}
            strokeWidth="1"
          />
        ))}

        <text
          x={padL}
          y={padT - 2}
          textAnchor="start"
          fontSize="10.5"
          fontFamily="system-ui, sans-serif"
          fill={axisTextColor}
        >
          {`Counts max: ${countMax}`}
        </text>

        <text
          x={padL + chartW}
          y={padT - 2}
          textAnchor="end"
          fontSize="10.5"
          fontFamily="system-ui, sans-serif"
          fill={axisTextColor}
        >
          {`Storage max: ${storageMax.toFixed(2)} GB`}
        </text>

        {safe.map((_, i) => {
          const centerX = xPos(i);
          const startX = i === 0 ? padL : centerX - hoverBandWidth / 2;
          const endX = i === n - 1 ? padL + chartW : centerX + hoverBandWidth / 2;
          return (
            <rect
              key={`hover-${i}`}
              x={startX}
              y={padT}
              width={Math.max(1, endX - startX)}
              height={chartH}
              fill="transparent"
              onMouseEnter={() => setHoverIndex(i)}
              onMouseMove={() => setHoverIndex(i)}
            />
          );
        })}

        {hoverX != null && (
          <line
            x1={hoverX}
            y1={padT}
            x2={hoverX}
            y2={padT + chartH}
            stroke={hoverLineColor}
            strokeWidth="1"
            strokeDasharray="4 6"
          />
        )}

        {renderSeries.map(s => {
          const pts = buildPoints(s);
          const polyPts = pts.map(p => `${p.x},${p.y}`).join(' ');
          return (
            <polyline
              key={s.key}
              points={polyPts}
              fill="none"
              stroke={s.color}
              strokeWidth="3"
              strokeDasharray={s.dash}
              strokeOpacity="0.95"
              strokeLinecap="round"
              strokeLinejoin="round"
              style={{
                filter: hoverIndex != null ? 'drop-shadow(0 0 8px rgba(59,130,246,0.08))' : 'none',
              }}
            />
          );
        })}

        {renderSeries.map(s =>
          buildPoints(s).map((pt, i) => (
            <circle
              key={`${s.key}-${i}`}
              cx={pt.x}
              cy={pt.y}
              r={hoverIndex === i ? 5.5 : 4.5}
              fill={s.color}
              stroke={isDark ? '#0f172a' : '#ffffff'}
              strokeWidth="2"
              opacity={hoverIndex == null || hoverIndex === i ? 1 : 0.92}
            />
          ))
        )}

        {hoverEntry && hoverX != null && (
          <g>
            <rect
              x={tooltipX}
              y={tooltipY}
              width={tooltipWidth}
              height={tooltipHeight}
              rx="14"
              fill={tooltipBg}
              stroke={tooltipBorder}
              strokeWidth="1.2"
            />
            <text
              x={tooltipX + 14}
              y={tooltipY + 22}
              fontSize="12"
              fontWeight="700"
              fontFamily="system-ui, sans-serif"
              fill={tooltipText}
            >
              {hoverLabel}
            </text>
            {series.map((s, index) => (
              <g key={`tooltip-${s.key}`}>
                <circle
                  cx={tooltipX + 18}
                  cy={tooltipY + 42 + index * 18}
                  r="4"
                  fill={s.color}
                />
                <text
                  x={tooltipX + 30}
                  y={tooltipY + 46 + index * 18}
                  fontSize="11.5"
                  fontFamily="system-ui, sans-serif"
                  fill={tooltipText}
                >
                  {`${s.label}: ${
                    s.key === 'storage_gb'
                      ? `${Number(hoverEntry.storage_gb || 0).toFixed(2)} GB`
                      : Number(hoverEntry[s.key] || 0)
                  }`}
                </text>
              </g>
            ))}
          </g>
        )}

        {monthLabels.map((label, i) => (
          <text
            key={i}
            x={xPos(i)}
            y={H - 8}
            textAnchor="middle"
            fontSize="11"
            fontFamily="system-ui, sans-serif"
            fill={labelColor}
          >
            {label}
          </text>
        ))}
      </svg>
    </div>
  );
}

function ThemeModeIcon({ theme }) {
  if (theme === 'dark') {
    return (
      <svg viewBox="0 0 24 24" className="h-[18px] w-[18px]" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
      </svg>
    );
  }

  return (
    <svg viewBox="0 0 24 24" className="h-[18px] w-[18px]" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" />
    </svg>
  );
}

function BellIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-[18px] w-[18px]" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10.268 21a2 2 0 0 0 3.464 0" />
      <path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326" />
    </svg>
  );
}

function UserIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-[18px] w-[18px]" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 20a6 6 0 0 0-12 0" />
      <circle cx="12" cy="10" r="4" />
      <circle cx="12" cy="12" r="10" />
    </svg>
  );
}

function PlusIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-[18px] w-[18px]" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 5v14M5 12h14" />
    </svg>
  );
}

function PencilIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
    </svg>
  );
}

function CopyIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
    </svg>
  );
}

function CloseIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-[18px] w-[18px]" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <path d="M6 6l12 12M18 6 6 18" />
    </svg>
  );
}

function EyeIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-[18px] w-[18px]" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

function EyeOffIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-[18px] w-[18px]" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c6.5 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68M6.6 6.6A13.13 13.13 0 0 0 2 11s3.5 7 10 7a9.12 9.12 0 0 0 5.4-1.6M14.12 14.12A3 3 0 1 1 9.88 9.88" />
      <path d="M2 2l20 20" />
    </svg>
  );
}

function ChevronLeftIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-[18px] w-[18px]" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="m15 18-6-6 6-6" />
    </svg>
  );
}

function ChevronRightIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-[18px] w-[18px]" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="m9 18 6-6-6-6" />
    </svg>
  );
}

function ArrowLeftIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-[18px] w-[18px]" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M19 12H5M12 19l-7-7 7-7" />
    </svg>
  );
}

function SendIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-[18px] w-[18px]" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 2 11 13" />
      <path d="m22 2-7 20-4-9-9-4 20-7Z" />
    </svg>
  );
}

function FileStackIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-[18px] w-[18px]" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M7 3h8l4 4v14H7z" />
      <path d="M15 3v5h5" />
      <path d="M5 7H4v14h12v-1" />
    </svg>
  );
}

function ThumbsUpIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3H14z"/>
      <path d="M7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/>
    </svg>
  );
}

function ThumbsDownIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3H10z"/>
      <path d="M17 2h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"/>
    </svg>
  );
}

function StopIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-[14px] w-[14px]" aria-hidden="true" fill="currentColor">
      <rect x="4" y="4" width="16" height="16" rx="2" />
    </svg>
  );
}

function AttachmentIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-[18px] w-[18px]" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="m21.44 11.05-8.49 8.49a6 6 0 0 1-8.49-8.49l9.2-9.19a4 4 0 0 1 5.66 5.65l-9.2 9.2a2 2 0 1 1-2.83-2.83l8.49-8.48" />
    </svg>
  );
}

function MoreHorizontalIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-[18px] w-[18px]" aria-hidden="true" fill="currentColor">
      <circle cx="5" cy="12" r="1.8" />
      <circle cx="12" cy="12" r="1.8" />
      <circle cx="19" cy="12" r="1.8" />
    </svg>
  );
}

function PinIcon({ filled = false }) {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-[15px] w-[15px]"
      aria-hidden="true"
      fill={filled ? 'currentColor' : 'none'}
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 17v5" />
      <path d="M9 10.76a2 2 0 0 1-1.11 1.79l-1.78.9A2 2 0 0 0 5 15.24V16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-.76a2 2 0 0 0-1.11-1.79l-1.78-.9A2 2 0 0 1 15 10.76V7a1 1 0 0 1 1-1 2 2 0 0 0 0-4H8a2 2 0 0 0 0 4 1 1 0 0 1 1 1z" />
    </svg>
  );
}

function AccountMcpSection({ theme, open }) {
  const isDark = theme === 'dark';
  const palette = themeOptions[theme];
  const helper = isDark ? 'text-white/62' : 'text-slate-500';
  const cardBg = isDark ? 'border-white/10 bg-white/[0.03]' : 'border-slate-200 bg-slate-50/75';
  const inputCls = isDark
    ? 'border-white/12 bg-white/[0.04] text-white placeholder:text-white/35'
    : 'border-slate-300 bg-white text-slate-900 placeholder:text-slate-400';

  const [tokens, setTokens] = useState([]);
  const [buckets, setBuckets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [copiedId, setCopiedId] = useState(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await dashboardApi.listAccountMcpTokens();
      setTokens(data.tokens || []);
      setBuckets(data.buckets || []);
    } catch (e) {
      setError(e.message || 'Failed to load account MCP tokens.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open) load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  const patchToken = async (tokenId, payload) => {
    setBusy(true);
    setError(null);
    try {
      const updated = await dashboardApi.updateAccountMcpToken(tokenId, payload);
      setTokens(prev => prev.map(t => (t.id === tokenId ? updated : t)));
    } catch (e) {
      setError(e.message || 'Update failed.');
      await load();
    } finally {
      setBusy(false);
    }
  };

  const createToken = async () => {
    setBusy(true);
    setError(null);
    try {
      await dashboardApi.createAccountMcpToken({ name: 'Account MCP', bucket_mode: 'all', allowed_bucket_ids: [] });
      await load();
    } catch (e) {
      setError(e.message || 'Could not create token.');
    } finally {
      setBusy(false);
    }
  };

  const deleteToken = async (tokenId) => {
    setBusy(true);
    setError(null);
    try {
      await dashboardApi.deleteAccountMcpToken(tokenId);
      setTokens(prev => prev.filter(t => t.id !== tokenId));
    } catch (e) {
      setError(e.message || 'Delete failed.');
    } finally {
      setBusy(false);
    }
  };

  const copyUrl = (token) => {
    navigator.clipboard?.writeText(token.account_mcp_url);
    setCopiedId(token.id);
    setTimeout(() => setCopiedId((c) => (c === token.id ? null : c)), 1600);
  };

  const toggleBucket = (token, bucketId) => {
    const current = new Set(token.allowed_bucket_ids || []);
    if (current.has(bucketId)) current.delete(bucketId);
    else current.add(bucketId);
    patchToken(token.id, { bucket_mode: 'selected', allowed_bucket_ids: [...current] });
  };

  return (
    <div className="space-y-4">
      {error && (
        <p className={`rounded-lg px-3 py-2 text-sm ${isDark ? 'bg-red-500/12 text-red-300' : 'bg-red-50 text-red-600'}`}>{error}</p>
      )}

      {loading ? (
        <div className={`h-20 animate-pulse rounded-[1rem] border ${cardBg}`} />
      ) : tokens.length === 0 ? (
        <p className={`text-sm ${helper}`}>No account MCP URLs yet. Create one to connect Claude to several buckets through a single URL.</p>
      ) : (
        tokens.map((token) => (
          <div key={token.id} className={`rounded-[1rem] border p-4 ${cardBg}`}>
            <div className="flex items-center gap-2">
              <input
                value={token.name}
                onChange={(e) => setTokens(prev => prev.map(t => (t.id === token.id ? { ...t, name: e.target.value } : t)))}
                onBlur={(e) => { if (e.target.value.trim() && e.target.value !== token._savedName) patchToken(token.id, { name: e.target.value.trim() }); }}
                className={`flex-1 rounded-lg border px-3 py-1.5 text-sm font-semibold ${inputCls}`}
                placeholder="Token name"
              />
              <button
                type="button"
                onClick={() => patchToken(token.id, { is_active: !token.is_active })}
                className={`rounded-lg px-2.5 py-1.5 text-xs font-semibold transition ${token.is_active ? (isDark ? 'bg-emerald-500/15 text-emerald-300' : 'bg-emerald-50 text-emerald-600') : (isDark ? 'bg-white/8 text-white/50' : 'bg-slate-100 text-slate-500')}`}
              >
                {token.is_active ? 'Active' : 'Disabled'}
              </button>
              <button
                type="button"
                onClick={() => deleteToken(token.id)}
                disabled={busy}
                className={`rounded-lg px-2.5 py-1.5 text-xs font-semibold transition ${isDark ? 'bg-red-500/12 text-red-300 hover:bg-red-500/20' : 'bg-red-50 text-red-600 hover:bg-red-100'}`}
              >
                Delete
              </button>
            </div>

            <div className={`mt-3 flex items-center gap-2 rounded-lg border px-3 py-2 ${isDark ? 'border-white/10 bg-black/20' : 'border-slate-200 bg-white'}`}>
              <code className={`flex-1 truncate text-xs ${isDark ? 'text-slate-300' : 'text-slate-600'}`}>{token.account_mcp_url}</code>
              <button
                type="button"
                onClick={() => copyUrl(token)}
                className={`shrink-0 rounded-md px-2.5 py-1 text-xs font-semibold transition ${isDark ? 'bg-blue-500/15 text-blue-300 hover:bg-blue-500/25' : 'bg-blue-50 text-blue-600 hover:bg-blue-100'}`}
              >
                {copiedId === token.id ? 'Copied' : 'Copy'}
              </button>
            </div>

            <div className="mt-3">
              <p className={`mb-2 text-xs font-semibold uppercase tracking-[0.18em] ${helper}`}>Bucket access</p>
              <div className="flex gap-2">
                {['all', 'selected'].map((mode) => (
                  <button
                    key={mode}
                    type="button"
                    onClick={() => patchToken(token.id, { bucket_mode: mode, allowed_bucket_ids: mode === 'all' ? [] : (token.allowed_bucket_ids || []) })}
                    className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition ${token.bucket_mode === mode ? (isDark ? 'bg-blue-500/20 text-blue-200' : 'bg-blue-600 text-white') : (isDark ? 'bg-white/6 text-white/55' : 'bg-slate-100 text-slate-500')}`}
                  >
                    {mode === 'all' ? 'All buckets' : 'Selected buckets'}
                  </button>
                ))}
              </div>

              {token.bucket_mode === 'selected' && (
                <div className="mt-3 grid gap-1.5 sm:grid-cols-2">
                  {buckets.length === 0 ? (
                    <p className={`text-xs ${helper}`}>No buckets yet — this URL will only see buckets it creates itself.</p>
                  ) : (
                    buckets.map((b) => {
                      const checked = (token.allowed_bucket_ids || []).includes(b.id);
                      return (
                        <label key={b.id} className={`flex cursor-pointer items-center gap-2 rounded-lg border px-3 py-2 text-sm transition ${checked ? (isDark ? 'border-blue-500/40 bg-blue-500/10' : 'border-blue-300 bg-blue-50') : (isDark ? 'border-white/10 hover:bg-white/[0.03]' : 'border-slate-200 hover:bg-slate-50')}`}>
                          <input type="checkbox" checked={checked} onChange={() => toggleBucket(token, b.id)} className="accent-blue-500" />
                          <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ background: b.color }} />
                          <span className={`truncate ${palette.title}`}>{b.name}</span>
                        </label>
                      );
                    })
                  )}
                </div>
              )}
            </div>
          </div>
        ))
      )}

      <button
        type="button"
        onClick={createToken}
        disabled={busy || loading}
        className={`rounded-xl px-4 py-2.5 text-sm font-semibold transition disabled:opacity-50 ${palette.primary}`}
      >
        {busy ? 'Working…' : '+ New Account MCP URL'}
      </button>
    </div>
  );
}

function ProfileDrawer({
  theme,
  profile,
  stats,
  billingPlan,
  open,
  onClose,
  draft,
  onDraftChange,
  passwordDraft,
  onPasswordChange,
  onToggleTheme,
  feedback,
  savingProfile,
  changingPassword,
  connectingProvider,
  disconnectingProvider,
  uploadingAvatar,
  deletingBuckets,
  deletingAccount,
  onSaveProfile,
  onAvatarPick,
  onChangePassword,
  onConnectProvider,
  onDisconnectProvider,
  onRequestLimitIncrease,
  onDeleteAllBuckets,
  onDeleteAccount,
  onLogout,
}) {
  const palette = themeOptions[theme];
  const isDark = theme === 'dark';
  const [avatarPreviewError, setAvatarPreviewError] = useState(false);
  const [billingBusy, setBillingBusy] = useState('');
  const [billingError, setBillingError] = useState('');

  const planKey = billingPlan?.plan;
  const isEnterprise = planKey === 'business';
  const isPaidPlan = !!billingPlan && !billingPlan.is_trial && !billingPlan.locked
    && (planKey === 'individual' || planKey === 'team');

  const handleSubscribe = async (plan) => {
    setBillingError('');
    setBillingBusy(plan);
    try {
      const { url } = await billingApi.createCheckout(plan);
      if (url) window.location.href = url;
      else { setBillingError('Could not start checkout.'); setBillingBusy(''); }
    } catch (e) {
      setBillingError(e.message || 'Could not start checkout.');
      setBillingBusy('');
    }
  };

  const handleManageBilling = async () => {
    setBillingError('');
    setBillingBusy('portal');
    try {
      const { url } = await billingApi.openPortal();
      if (url) window.location.href = url;
      else { setBillingError('Could not open billing portal.'); setBillingBusy(''); }
    } catch (e) {
      setBillingError(e.message || 'Could not open billing portal.');
      setBillingBusy('');
    }
  };

  const handleCancelSubscription = async () => {
    if (!window.confirm('Cancel your subscription? You keep access until the end of the current billing period.')) return;
    setBillingError('');
    setBillingBusy('cancel');
    try {
      await billingApi.cancelSubscription();
      window.alert('Your subscription will be cancelled at the end of the current period.');
    } catch (e) {
      setBillingError(e.message || 'Could not cancel subscription.');
    } finally {
      setBillingBusy('');
    }
  };
  const panelShell = isDark
    ? 'border-white/10 bg-[#0b1220] text-white shadow-[0_30px_100px_rgba(2,6,23,0.62)]'
    : 'border-slate-300 bg-[#f8fafc] text-slate-900 shadow-[0_24px_80px_rgba(148,163,184,0.22)]';
  const helperText = isDark ? 'text-white/62' : 'text-slate-500';
  const sectionBorder = isDark ? 'border-white/10' : 'border-slate-200';
  const subtleSurface = isDark ? 'bg-white/[0.025]' : 'bg-slate-50/75';
  const dangerCard = isDark ? 'border-red-500/18 bg-red-500/[0.045]' : 'border-red-200 bg-red-50/72';
  const nameInitial = (draft.fullName || profile?.full_name || 'U')[0]?.toUpperCase() || 'U';
  const storageUsed = stats?.storage_gb != null ? `${Number(stats.storage_gb).toFixed(2)} GB` : '0.00 GB';
  const planLimits = billingPlan?.limits || {};
  const planUsage = billingPlan?.usage || {};
  const planFields = REQUESTABLE_LIMIT_FIELDS.filter((field) => planLimits[field] != null);
  const visibleAuthProvider = profile?.auth_provider === 'google' ? 'google' : 'email';
  const usesSocialProvider = visibleAuthProvider === 'google';
  const providerAccent = visibleAuthProvider === 'google'
    ? 'from-rose-500/18 via-amber-500/14 to-blue-500/18'
    : (isDark ? 'from-emerald-500/10 via-cyan-500/6 to-emerald-500/10' : 'from-emerald-500/12 via-cyan-500/10 to-emerald-500/12');
  const providerLabel = visibleAuthProvider === 'google' ? (profile?.auth_provider_label || 'Google') : 'Email';
  const providerInitial = providerLabel[0]?.toUpperCase() || 'E';
  const providerOptions = [
    {
      key: 'google',
      label: 'Google',
      connected: Boolean(profile?.google_connected),
      available: Boolean(profile?.google_available),
      icon: <GoogleIcon />,
    },
  ];

  useEffect(() => {
    setAvatarPreviewError(false);
  }, [profile?.avatar_url]);

  return (
    <div className={`fixed inset-0 z-[70] transition ${open ? 'pointer-events-auto' : 'pointer-events-none'}`}>
      <div
        onClick={onClose}
        className={`absolute inset-0 transition duration-300 ${open ? `${theme === 'light' ? 'bg-white/45' : palette.overlay} opacity-100 backdrop-blur-sm` : 'opacity-0'}`}
      />

      <div className="absolute inset-0 flex items-center justify-center px-4 py-6 sm:px-6">
        <section
          className={`flex h-[min(88dvh,52rem)] w-full max-w-[62rem] flex-col overflow-hidden rounded-[1.6rem] border transition duration-300 ${panelShell} ${open ? 'scale-100 opacity-100' : 'scale-[0.96] opacity-0'}`}
        >
          <div className={`px-5 pb-4 pt-5 sm:px-7 ${sectionBorder} border-b`}>
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className={`text-2xl font-semibold tracking-tight ${palette.title}`}>Profile settings</h2>
                <p className={`mt-1 text-sm ${palette.text}`}>Manage your account details here.</p>
              </div>
              <button
                type="button"
                onClick={onClose}
                aria-label="Close profile panel"
                className={`flex h-10 w-10 items-center justify-center rounded-full transition ${isDark ? 'text-white/70 hover:bg-white/8 hover:text-white' : 'text-slate-500 hover:bg-slate-100 hover:text-slate-900'}`}
              >
                <CloseIcon />
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto px-5 py-6 sm:px-7">
            <div className="space-y-8">
              <Alert theme={theme} message={feedback?.message} type={feedback?.type || 'success'} />

              <section className={`pb-8 ${sectionBorder} border-b`}>
                <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`relative flex h-24 w-24 shrink-0 items-center justify-center overflow-hidden rounded-full border text-2xl font-semibold ${sectionBorder} ${subtleSurface} ${isDark ? 'text-white' : 'text-slate-900'}`}>
                      {profile?.avatar_url && !avatarPreviewError
                        ? <img src={profile.avatar_url} alt="" className="h-full w-full rounded-full object-cover object-center" onError={() => setAvatarPreviewError(true)} />
                        : nameInitial
                      }
                    </div>
                    <div>
                      <p className={`text-lg font-semibold ${palette.title}`}>{draft.fullName || profile?.full_name || 'User'}</p>
                      <p className={`mt-1 text-sm ${helperText}`}>{profile?.email || 'user@example.com'}</p>
                      <p className={`mt-2 text-sm ${palette.text}`}>Click to upload a new avatar</p>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={onAvatarPick}
                    disabled={uploadingAvatar}
                    className={`rounded-xl border px-4 py-2.5 text-sm font-medium transition ${palette.secondary}`}
                  >
                    {uploadingAvatar ? 'Uploading...' : 'Upload Avatar'}
                  </button>
                </div>
              </section>

              <section className={`pb-8 ${sectionBorder} border-b`}>
                <div className="mb-5">
                  <p className={`text-lg font-semibold ${palette.title}`}>Profile</p>
                </div>

                <div className="grid gap-4 lg:grid-cols-2">
                  <Input
                    label="Name"
                    theme={theme}
                    value={draft.fullName}
                    onChange={(e) => onDraftChange('fullName', e.target.value)}
                    placeholder="Your full name"
                  />

                  <label className="block">
                    <span className={`mb-2 block text-sm font-medium ${palette.title}`}>Email</span>
                    <div className={`flex min-h-[50px] items-center rounded-2xl px-4 text-sm ${subtleSurface} ${isDark ? 'text-white/72' : 'text-slate-600'}`}>
                      {profile?.email || 'user@example.com'}
                    </div>
                    <p className={`mt-2 text-xs ${helperText}`}>Email cannot be changed</p>
                  </label>
                </div>

                <div className="mt-5">
                  <button
                    type="button"
                    onClick={onSaveProfile}
                    disabled={savingProfile}
                    className={`rounded-xl px-5 py-2.5 text-sm font-semibold transition ${palette.primary}`}
                  >
                    {savingProfile ? 'Saving...' : 'Save Profile'}
                  </button>
                </div>
              </section>

              <section className={`pb-8 ${sectionBorder} border-b`}>
                <div className="mb-5">
                  <p className={`text-lg font-semibold ${palette.title}`}>Connected Account</p>
                  <p className={`mt-1 text-sm ${palette.text}`}>See how this account signs in and manage the provider connection.</p>
                </div>

                <div className={`overflow-hidden rounded-[1.2rem] border ${sectionBorder}`}>
                  <div className={`flex items-center gap-4 border-b px-5 py-4 ${sectionBorder} bg-gradient-to-r ${providerAccent}`}>
                    <div className={`flex h-11 w-11 items-center justify-center rounded-full border text-sm font-semibold ${sectionBorder} ${isDark ? 'bg-white/8 text-white' : 'bg-white/85 text-slate-900'}`}>
                      {providerInitial}
                    </div>
                    <div>
                      <p className={`text-sm font-semibold ${palette.title}`}>Connected with {providerLabel}</p>
                      <p className={`mt-1 text-xs ${helperText}`}>Primary sign-in method</p>
                    </div>
                  </div>

                  <div className={`space-y-4 p-5 ${subtleSurface}`}>
                    <div>
                      <p className={`text-sm ${helperText}`}>
                        {usesSocialProvider
                          ? `Your primary sign-in provider is ${providerLabel}.`
                          : 'Your account currently uses email/password sign-in.'}
                      </p>
                      {usesSocialProvider && !profile?.can_disconnect_provider && (
                        <p className={`mt-2 text-xs ${helperText}`}>
                          Add a password first, then you can disconnect {providerLabel}.
                        </p>
                      )}
                    </div>

                    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                      <div className={`rounded-full px-3 py-1 text-xs font-semibold ${isDark ? 'bg-white/8 text-white/78' : 'bg-slate-200/80 text-slate-700'}`}>
                        {usesSocialProvider ? `${providerLabel} Connected` : 'Email Sign-In Active'}
                      </div>
                    </div>

                    <div className="grid gap-3">
                      {providerOptions.map((item) => {
                        const isPrimary = profile?.auth_provider === item.key;
                        const canDisconnect = item.connected && (!isPrimary || profile?.has_password);
                        const statusText = item.connected
                          ? (isPrimary ? 'Connected and primary sign-in method' : 'Connected as an additional sign-in method')
                          : (item.available ? 'Not connected yet' : 'Not configured on this workspace');

                        return (
                          <div key={item.key} className={`flex flex-col gap-3 rounded-[1rem] border px-4 py-4 sm:flex-row sm:items-center sm:justify-between ${sectionBorder} ${isDark ? 'bg-white/[0.03]' : 'bg-white/70'}`}>
                            <div className="flex items-center gap-3">
                              <div className={`flex h-10 w-10 items-center justify-center rounded-full border ${sectionBorder} ${isDark ? 'bg-white/6 text-white' : 'bg-slate-100 text-slate-900'}`}>
                                {item.icon}
                              </div>
                              <div>
                                <p className={`text-sm font-semibold ${palette.title}`}>{item.label}</p>
                                <p className={`mt-1 text-xs ${helperText}`}>{statusText}</p>
                              </div>
                            </div>

                            <div className="flex items-center gap-2">
                              {item.connected ? (
                                <>
                                  <div className={`rounded-full px-3 py-1 text-xs font-semibold ${isDark ? 'bg-emerald-500/14 text-emerald-300' : 'bg-emerald-50 text-emerald-700'}`}>
                                    Connected
                                  </div>
                                  <button
                                    type="button"
                                    onClick={() => onDisconnectProvider(item.key)}
                                    disabled={disconnectingProvider === item.key || !canDisconnect}
                                    className={`rounded-xl border px-4 py-2.5 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-50 ${palette.secondary}`}
                                  >
                                    {disconnectingProvider === item.key ? 'Disconnecting...' : 'Disconnect'}
                                  </button>
                                </>
                              ) : (
                                <button
                                  type="button"
                                  onClick={() => onConnectProvider(item.key)}
                                  disabled={connectingProvider === item.key || !item.available}
                                  className={`rounded-xl border px-4 py-2.5 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-50 ${palette.secondary}`}
                                >
                                  {connectingProvider === item.key ? 'Connecting...' : (item.available ? 'Connect' : 'Unavailable')}
                                </button>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </section>

              <section className={`pb-8 ${sectionBorder} border-b`}>
                <div className="mb-5">
                  <p className={`text-lg font-semibold ${palette.title}`}>{profile?.has_password ? 'Change Password' : 'Create Password'}</p>
                </div>

                <div className={`grid gap-4 ${profile?.has_password ? 'lg:grid-cols-3' : 'lg:grid-cols-2'}`}>
                  {profile?.has_password && (
                    <Input
                      label="Current Password"
                      type="password"
                      theme={theme}
                      value={passwordDraft.current}
                      onChange={(e) => onPasswordChange('current', e.target.value)}
                      placeholder="Enter current password"
                    />
                  )}
                  <Input
                    label={profile?.has_password ? 'New Password' : 'Password'}
                    type="password"
                    theme={theme}
                    value={passwordDraft.next}
                    onChange={(e) => onPasswordChange('next', e.target.value)}
                    placeholder="Enter new password"
                  />
                  <Input
                    label="Confirm New Password"
                    type="password"
                    theme={theme}
                    value={passwordDraft.confirm}
                    onChange={(e) => onPasswordChange('confirm', e.target.value)}
                    placeholder="Confirm new password"
                  />
                </div>

                <div className="mt-5">
                  <button
                    type="button"
                    onClick={onChangePassword}
                    disabled={changingPassword}
                    className={`rounded-xl px-5 py-2.5 text-sm font-semibold transition ${palette.primary}`}
                  >
                    {changingPassword ? 'Updating...' : (profile?.has_password ? 'Change Password' : 'Create Password')}
                  </button>
                </div>
              </section>

              <section className={`pb-8 ${sectionBorder} border-b`}>
                <div className="mb-5">
                  <p className={`text-lg font-semibold ${palette.title}`}>Appearance</p>
                  <p className={`mt-1 text-sm ${palette.text}`}>Theme</p>
                </div>

                <button
                  type="button"
                  onClick={onToggleTheme}
                  className={`flex w-full items-center justify-between rounded-[1rem] px-4 py-4 text-left transition ${isDark ? 'bg-blue-500/[0.08]' : 'bg-blue-50/80'}`}
                >
                  <div>
                    <p className={`text-base font-semibold ${palette.title}`}>Dark mode</p>
                    <p className={`mt-1 text-sm ${palette.text}`}>🌙 Dark</p>
                  </div>
                  <span className={`text-sm font-medium ${palette.accent}`}>{theme === 'dark' ? 'Active' : 'Switch'}</span>
                </button>
              </section>

              <section className={`pb-8 ${sectionBorder} border-b`}>
                <div className="mb-5">
                  <p className={`text-lg font-semibold ${palette.title}`}>Billing</p>
                  <p className={`mt-1 text-sm ${palette.text}`}>Current plan, usage, and limits.</p>
                </div>

                <div className="grid gap-4 lg:grid-cols-3">
                  <div className={`rounded-[1rem] px-4 py-4 ${subtleSurface}`}>
                    <p className={`text-xs font-medium uppercase tracking-[0.2em] ${helperText}`}>Current Plan</p>
                    <p className={`mt-2 text-base font-semibold ${palette.title}`}>{billingPlan?.name || 'Loading...'}</p>
                  </div>
                  <div className={`rounded-[1rem] px-4 py-4 ${subtleSurface}`}>
                    <p className={`text-xs font-medium uppercase tracking-[0.2em] ${helperText}`}>Storage Used</p>
                    <p className={`mt-2 text-base font-semibold ${palette.title}`}>
                      {billingPlan?.usage?.max_storage_bytes != null ? fmtBytes(billingPlan.usage.max_storage_bytes) : storageUsed}
                    </p>
                  </div>
                  <div className={`rounded-[1rem] px-4 py-4 ${subtleSurface}`}>
                    <p className={`text-xs font-medium uppercase tracking-[0.2em] ${helperText}`}>Status</p>
                    <p className={`mt-2 text-base font-semibold ${palette.title}`}>{billingPlan?.status || 'Active'}</p>
                  </div>
                </div>

                {planFields.length > 0 && (
                  <div className={`mt-4 overflow-hidden rounded-[1rem] border ${sectionBorder}`}>
                    {planFields.map((field) => {
                      const used = planUsage[field] || 0;
                      const limit = planLimits[field] || 0;
                      const pct = billingPlan?.percent_used?.[field] || 0;
                      return (
                        <div key={field} className={`grid grid-cols-[minmax(0,1fr)_auto] gap-3 border-b px-4 py-3 last:border-b-0 ${sectionBorder}`}>
                          <div className="min-w-0">
                            <p className={`text-sm font-medium ${palette.title}`}>{LIMIT_FIELD_LABELS[field] || field}</p>
                            <div className={`mt-2 h-1.5 overflow-hidden rounded-full ${isDark ? 'bg-white/8' : 'bg-slate-200'}`}>
                              <div className="h-full rounded-full bg-blue-500" style={{ width: `${Math.max(0, Math.min(100, pct))}%` }} />
                            </div>
                          </div>
                          <p className={`text-right text-sm ${helperText}`}>
                            {fmtLimitValue(field, used)} / {fmtLimitValue(field, limit)}
                          </p>
                        </div>
                      );
                    })}
                  </div>
                )}

                {billingError && (
                  <p className="mt-4 rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-500">{billingError}</p>
                )}

                {isEnterprise ? (
                  <p className={`mt-5 text-sm ${helperText}`}>Enterprise account — billing and limits are managed by our team.</p>
                ) : isPaidPlan ? (
                  <div className="mt-5 flex flex-wrap gap-3">
                    <button
                      type="button"
                      onClick={handleManageBilling}
                      disabled={!!billingBusy}
                      className={`rounded-xl px-5 py-2.5 text-sm font-semibold transition disabled:opacity-60 ${palette.primary}`}
                    >
                      {billingBusy === 'portal' ? 'Opening...' : 'Upgrade plan'}
                    </button>
                    <button
                      type="button"
                      onClick={handleCancelSubscription}
                      disabled={!!billingBusy}
                      className={`rounded-xl px-5 py-2.5 text-sm font-semibold transition disabled:opacity-60 ${isDark ? 'bg-white/8 text-slate-100 hover:bg-white/12' : 'bg-slate-100 text-slate-800 hover:bg-slate-200'}`}
                    >
                      {billingBusy === 'cancel' ? 'Cancelling...' : 'Cancel subscription'}
                    </button>
                  </div>
                ) : (
                  <div className="mt-5 flex flex-wrap gap-3">
                    <button
                      type="button"
                      onClick={() => handleSubscribe('individual')}
                      disabled={!!billingBusy}
                      className={`rounded-xl px-5 py-2.5 text-sm font-semibold transition disabled:opacity-60 ${palette.primary}`}
                    >
                      {billingBusy === 'individual' ? 'Redirecting...' : 'Upgrade to Individual · $15/mo'}
                    </button>
                    <button
                      type="button"
                      onClick={() => handleSubscribe('team')}
                      disabled={!!billingBusy}
                      className={`rounded-xl px-5 py-2.5 text-sm font-semibold transition disabled:opacity-60 ${isDark ? 'bg-white/8 text-slate-100 hover:bg-white/12' : 'bg-slate-100 text-slate-800 hover:bg-slate-200'}`}
                    >
                      {billingBusy === 'team' ? 'Redirecting...' : 'Upgrade to Team · $49/mo'}
                    </button>
                  </div>
                )}

                <button
                  type="button"
                  onClick={() => onRequestLimitIncrease?.(billingPlan)}
                  className={`mt-3 rounded-xl px-5 py-2.5 text-sm font-semibold transition ${isDark ? 'bg-white/8 text-slate-100 hover:bg-white/12' : 'bg-slate-100 text-slate-800 hover:bg-slate-200'}`}
                >
                  {isEnterprise ? 'Request More Limits' : 'Increase Limits'}
                </button>
              </section>

              <section className={`pb-8 ${sectionBorder} border-b`}>
                <div className="mb-5">
                  <p className={`text-lg font-semibold ${palette.title}`}>Account MCP</p>
                  <p className={`mt-1 text-sm ${palette.text}`}>
                    Connect Claude or any MCP client to multiple buckets through one URL. Each URL has its own bucket permissions.
                  </p>
                </div>
                <AccountMcpSection theme={theme} open={open} />
              </section>

              <section className={`pb-8 ${sectionBorder} border-b`}>
                <div className="mb-4">
                  <p className={`text-lg font-semibold ${palette.title}`}>Session</p>
                  <p className={`mt-1 text-sm ${palette.text}`}>Sign out of your account on this device.</p>
                </div>
                <button
                  type="button"
                  onClick={onLogout}
                  className={`rounded-xl px-5 py-2.5 text-sm font-semibold transition ${isDark ? 'bg-white/8 text-slate-100 hover:bg-white/12' : 'bg-slate-100 text-slate-800 hover:bg-slate-200'}`}
                >
                  Log out
                </button>
              </section>

              <section className="space-y-4">
                <div>
                  <p className={`text-lg font-semibold ${palette.title}`}>Danger Zone</p>
                </div>

                <div className={`rounded-[1.25rem] border p-5 ${dangerCard}`}>
                  <p className={`text-base font-semibold ${isDark ? 'text-red-300' : 'text-red-700'}`}>Delete All Buckets</p>
                  <p className={`mt-2 text-sm leading-6 ${isDark ? 'text-red-100/78' : 'text-red-900/72'}`}>
                    This will permanently delete all your buckets and files. This action cannot be undone.
                  </p>
                  <button
                    type="button"
                    onClick={onDeleteAllBuckets}
                    disabled={deletingBuckets}
                    className={`mt-4 rounded-xl px-4 py-2.5 text-sm font-semibold transition ${isDark ? 'bg-red-500/16 text-red-200 hover:bg-red-500/22' : 'bg-red-600 text-white hover:bg-red-500'}`}
                  >
                    {deletingBuckets ? 'Deleting...' : 'Delete All Buckets'}
                  </button>
                </div>

                <div className={`rounded-[1.25rem] border p-5 ${dangerCard}`}>
                  <p className={`text-base font-semibold ${isDark ? 'text-red-300' : 'text-red-700'}`}>Delete Account</p>
                  <p className={`mt-2 text-sm leading-6 ${isDark ? 'text-red-100/78' : 'text-red-900/72'}`}>
                    This will permanently delete your account and all associated data. This action cannot be undone.
                  </p>
                  <button
                    type="button"
                    onClick={onDeleteAccount}
                    disabled={deletingAccount}
                    className={`mt-4 rounded-xl px-4 py-2.5 text-sm font-semibold transition ${isDark ? 'bg-red-500/16 text-red-200 hover:bg-red-500/22' : 'bg-red-600 text-white hover:bg-red-500'}`}
                  >
                    {deletingAccount ? 'Deleting...' : 'Delete Account'}
                  </button>
                </div>
              </section>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

const BUCKET_ICONS = ['folder', 'book', 'code', 'star', 'lock', 'globe'];
const BUCKET_COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EC4899', '#8B5CF6', '#14B8A6'];

// ---------- Dashboard ----------

function DashboardPage({ theme, onToggleTheme, workspaces, activeWorkspace }) {
  const palette = themeOptions[theme];
  const navigate = useNavigate();
  const currentMonth = toMonthInputValue(new Date());

  const [profile, setProfile] = useState(null);
  const [stats, setStats] = useState(null);
  const [billingPlan, setBillingPlan] = useState(null);
  const [monthly, setMonthly] = useState([]);
  const [buckets, setBuckets] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [chartLoading, setChartLoading] = useState(true);
  const [rangePickerOpen, setRangePickerOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [avatarLoadError, setAvatarLoadError] = useState(false);
  const [profileDraft, setProfileDraft] = useState({ fullName: '', bio: '' });
  const [passwordDraft, setPasswordDraft] = useState({ current: '', next: '', confirm: '' });
  const [profileFeedback, setProfileFeedback] = useState(null);
  const [savingProfile, setSavingProfile] = useState(false);
  const [uploadingAvatar, setUploadingAvatar] = useState(false);
  const [changingPassword, setChangingPassword] = useState(false);
  const [connectingProvider, setConnectingProvider] = useState(null);
  const [disconnectingProvider, setDisconnectingProvider] = useState(null);
  const [deletingBuckets, setDeletingBuckets] = useState(false);
  const [deletingAccount, setDeletingAccount] = useState(false);
  const [deletingBucketId, setDeletingBucketId] = useState(null);
  const [bucketToDelete, setBucketToDelete] = useState(null);
  const [confirmDeleteAllOpen, setConfirmDeleteAllOpen] = useState(false);
  const [confirmDeleteAccountOpen, setConfirmDeleteAccountOpen] = useState(false);
  const [deleteAccountPassword, setDeleteAccountPassword] = useState('');
  const [newBucket, setNewBucket] = useState({ name: '', description: '', color: '#3B82F6', icon: 'folder' });
  const [chartRange, setChartRange] = useState(() => ({
    startMonth: shiftMonthInputValue(currentMonth, -5),
    endMonth: currentMonth,
  }));
  const [creating, setCreating] = useState(false);
  const notifRef = useRef(null);
  const avatarInputRef = useRef(null);
  const rangePickerRef = useRef(null);

  async function loadDashboardData() {
    const [p, s, b, n, planData] = await Promise.all([
      dashboardApi.getProfile(),
      dashboardApi.getStats(),
      dashboardApi.listBuckets(),
      dashboardApi.listNotifications(),
      billingApi.getPlan(),
    ]);
    setProfile(p);
    setStats(s);
    setBuckets(b);
    setNotifications(n);
    setBillingPlan(planData);
  }

  async function loadMonthlyData(startMonth, endMonth) {
    const data = await dashboardApi.getMonthlyStats(startMonth, endMonth);
    setMonthly(Array.isArray(data) ? data : []);
  }

  useEffect(() => {
    const token = sessionStorage.getItem('access_token');
    if (!token) { navigate('/login'); return; }
    loadDashboardData().finally(() => setLoading(false));
  }, [navigate]);

  useEffect(() => {
    const token = sessionStorage.getItem('access_token');
    if (!token) return;
    setChartLoading(true);
    loadMonthlyData(chartRange.startMonth, chartRange.endMonth)
      .finally(() => setChartLoading(false));
  }, [chartRange.endMonth, chartRange.startMonth]);

  useEffect(() => {
    function handleClick(e) {
      if (notifRef.current && !notifRef.current.contains(e.target)) setNotifOpen(false);
      if (rangePickerRef.current && !rangePickerRef.current.contains(e.target)) setRangePickerOpen(false);
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  useEffect(() => {
    if (!profile) return;
    setProfileDraft({
      fullName: profile.full_name || '',
      bio: profile.bio || '',
    });
  }, [profile]);

  useEffect(() => {
    setAvatarLoadError(false);
  }, [profile?.avatar_url]);

  useEffect(() => {
    const openProfile = localStorage.getItem('aiveilix-profile-open');
    const rawFeedback = localStorage.getItem('aiveilix-profile-feedback');
    if (openProfile === '1') {
      setProfileOpen(true);
      localStorage.removeItem('aiveilix-profile-open');
    }
    if (rawFeedback) {
      try {
        const parsed = JSON.parse(rawFeedback);
        if (parsed?.message) setProfileFeedback(parsed);
      } catch {}
      localStorage.removeItem('aiveilix-profile-feedback');
    }
  }, [profile]);

  const unreadCount = notifications.filter(n => !n.is_read).length;

  const handleMarkAllRead = async () => {
    await dashboardApi.markAllRead();
    setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
  };

  const handleMarkNotificationRead = async (notificationId) => {
    const target = notifications.find((notification) => notification.id === notificationId);
    if (!target || target.is_read) return;
    await dashboardApi.markNotificationRead(notificationId);
    setNotifications(prev => prev.map((notification) =>
      notification.id === notificationId ? { ...notification, is_read: true } : notification
    ));
  };

  const handleDeleteNotification = async (notificationId) => {
    await dashboardApi.deleteNotification(notificationId);
    setNotifications(prev => prev.filter((notification) => notification.id !== notificationId));
  };

  const handleDeleteAllNotifications = async () => {
    await dashboardApi.deleteAllNotifications();
    setNotifications([]);
  };

  const handleStartMonthChange = (nextStartMonth) => {
    setChartRange((prev) => ({
      startMonth: nextStartMonth,
      endMonth: nextStartMonth > prev.endMonth ? nextStartMonth : prev.endMonth,
    }));
  };

  const handleEndMonthChange = (nextEndMonth) => {
    setChartRange((prev) => ({
      startMonth: nextEndMonth < prev.startMonth ? nextEndMonth : prev.startMonth,
      endMonth: nextEndMonth,
    }));
  };

  const handleResetChartRange = () => {
    setChartRange({
      startMonth: shiftMonthInputValue(currentMonth, -5),
      endMonth: currentMonth,
    });
    setRangePickerOpen(false);
  };

  const setFeedback = (message, type = 'success') => setProfileFeedback({ message, type });

  const handleSaveProfile = async () => {
    setSavingProfile(true);
    setProfileFeedback(null);
    try {
      await dashboardApi.updateProfile({
        full_name: profileDraft.fullName,
        bio: profileDraft.bio,
        theme,
        language: profile?.language || 'en',
        timezone: profile?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
      });
      setProfile(prev => prev ? { ...prev, full_name: profileDraft.fullName, bio: profileDraft.bio, theme } : prev);
      setFeedback('Profile updated successfully.');
    } catch (err) {
      setFeedback(err.message, 'error');
    } finally {
      setSavingProfile(false);
    }
  };

  const handleAvatarChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadingAvatar(true);
    setProfileFeedback(null);
    try {
      const result = await dashboardApi.uploadAvatar(file);
      setProfile(prev => prev ? { ...prev, avatar_url: result.avatar_url } : prev);
      setFeedback('Profile picture updated.');
    } catch (err) {
      setFeedback(err.message, 'error');
    } finally {
      e.target.value = '';
      setUploadingAvatar(false);
    }
  };

  const handleChangePassword = async () => {
    if ((!profile?.has_password && (!passwordDraft.next || !passwordDraft.confirm)) || (profile?.has_password && (!passwordDraft.current || !passwordDraft.next || !passwordDraft.confirm))) {
      setFeedback('Please complete all password fields.', 'error');
      return;
    }
    if (passwordDraft.next !== passwordDraft.confirm) {
      setFeedback('New password confirmation does not match.', 'error');
      return;
    }

    setChangingPassword(true);
    setProfileFeedback(null);
    try {
      await dashboardApi.changePassword(profile?.has_password ? passwordDraft.current : '', passwordDraft.next);
      setPasswordDraft({ current: '', next: '', confirm: '' });
      setProfile(prev => prev ? { ...prev, has_password: true, can_disconnect_provider: prev.auth_provider === 'google' } : prev);
      setFeedback(profile?.has_password ? 'Password changed successfully.' : 'Password created successfully.');
    } catch (err) {
      setFeedback(err.message, 'error');
    } finally {
      setChangingPassword(false);
    }
  };

  const handleStartConnectProvider = async (provider) => {
    setConnectingProvider(provider);
    setProfileFeedback(null);
    try {
      const stateToken = createOAuthStateToken();
      rememberOAuthState('connect', provider, stateToken);
      const result = await dashboardApi.getProviderConnectUrl(provider, buildOAuthRedirectUri(), stateToken);
      localStorage.setItem('aiveilix-profile-open', '1');
      window.location.href = result.url;
    } catch (err) {
      setFeedback(err.message, 'error');
      setConnectingProvider(null);
    }
  };

  const handleDisconnectProvider = async (provider) => {
    setDisconnectingProvider(provider);
    setProfileFeedback(null);
    try {
      const result = await dashboardApi.disconnectAuthProvider(provider);
      setProfile(prev => prev ? {
        ...prev,
        auth_provider: prev.auth_provider === provider ? 'email' : prev.auth_provider,
        auth_provider_label: prev.auth_provider === provider ? 'Email' : prev.auth_provider_label,
        connected_providers: Array.isArray(result.connected_providers)
          ? result.connected_providers
          : (prev.connected_providers || []).filter(item => item !== provider),
        google_connected: provider === 'google' ? false : prev.google_connected,
        can_disconnect_provider: prev.auth_provider === provider ? false : prev.can_disconnect_provider,
      } : prev);
      setFeedback(result.message || 'Provider disconnected successfully.');
    } catch (err) {
      setFeedback(err.message, 'error');
    } finally {
      setDisconnectingProvider(null);
    }
  };

  const handleDeleteAllBuckets = async () => {
    setDeletingBuckets(true);
    setProfileFeedback(null);
    try {
      await dashboardApi.deleteAllBuckets();
      await loadDashboardData();
      setFeedback('All buckets deleted successfully.');
      setConfirmDeleteAllOpen(false);
    } catch (err) {
      setFeedback(err.message, 'error');
    } finally {
      setDeletingBuckets(false);
    }
  };

  const handleDeleteBucket = async (bucketId) => {
    setDeletingBucketId(bucketId);
    try {
      await dashboardApi.deleteBucket(bucketId);
      setBuckets(prev => prev.filter((bucket) => bucket.id !== bucketId));
      setBucketToDelete(null);
    } catch (err) {
      setFeedback(err.message, 'error');
    } finally {
      setDeletingBucketId(null);
    }
  };

  const handleLogout = async () => {
    await signOut();
    navigate('/login');
  };

  const handleDeleteAccount = async () => {
    setDeletingAccount(true);
    setProfileFeedback(null);
    try {
      await dashboardApi.deleteAccount(deleteAccountPassword);
      window.localStorage.removeItem('refresh_token');
      window.sessionStorage.removeItem('access_token');
      setDeleteAccountPassword('');
      setConfirmDeleteAccountOpen(false);
      navigate('/login');
    } catch (err) {
      setFeedback(err.message, 'error');
      setDeletingAccount(false);
      return;
    }
  };

  const handleCreateBucket = async (e) => {
    e.preventDefault();
    if (!newBucket.name.trim()) return;
    setCreating(true);
    try {
      const b = await dashboardApi.createBucket(newBucket.name, newBucket.description || null, newBucket.color, newBucket.icon);
      setBuckets(prev => [b, ...prev]);
      setCreateOpen(false);
      setNewBucket({ name: '', description: '', color: '#3B82F6', icon: 'folder' });
      navigate(`/bucket/${b.id}`, { state: { bucket: b } });
    } finally {
      setCreating(false);
    }
  };

  const isDark = theme === 'dark';
  const navBg = 'border-transparent bg-transparent';
  const cardBg = themeOptions[theme].card;
  const mutedText = isDark ? 'text-white/78' : 'text-black/72';
  const titleText = isDark ? 'text-white' : 'text-slate-900';
  const bodyText = isDark ? 'text-white/88' : 'text-black/82';
  const iconBtn = isDark
    ? 'relative inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-white/70 transition-colors hover:bg-white/10 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-400/60'
    : 'relative inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-slate-500 transition-colors hover:bg-slate-900/[0.06] hover:text-slate-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/50';
  const groupBg = isDark
    ? 'border-white/10 bg-white/[0.04]'
    : 'border-slate-200/80 bg-slate-50/80';
  const dropBg = isDark
    ? 'border-white/10 bg-slate-950/72 shadow-[0_28px_80px_rgba(2,6,23,0.42)] backdrop-blur-2xl'
    : 'border-white/80 bg-white/82 shadow-[0_24px_60px_rgba(148,163,184,0.18)] backdrop-blur-2xl';
  const tableShell = isDark
    ? 'border-white/10 bg-white/[0.03] backdrop-blur-xl'
    : 'border-slate-300 bg-white/72 backdrop-blur-xl';
  const tableRow = isDark ? 'border-white/10 bg-transparent hover:bg-white/[0.03]' : 'border-slate-300 bg-transparent hover:bg-white/80';
  const tableHead = isDark ? 'text-white/54' : 'text-slate-500';
  const tableDivider = isDark ? 'border-white/10' : 'border-slate-300';
  const bucketCard = isDark ? 'border-white/10 bg-white/[0.03] hover:bg-white/[0.05]' : 'border-white/80 bg-white/78 hover:bg-white';

  const metricCards = [
    { label: 'Storage Used', value: stats ? fmtStorage(stats.storage_gb) : '—', sub: 'total across buckets', color: '#3B82F6' },
    { label: 'Files', value: stats ? String(stats.files_count) : '—', sub: 'uploaded across all buckets', color: '#8B5CF6' },
    { label: 'Chat Messages', value: stats ? String(stats.chat_messages) : '—', sub: 'this month', color: '#10B981' },
    { label: 'MCP Calls', value: stats ? String(stats.mcp_calls) : '—', sub: 'this month', color: '#F59E0B' },
  ];
  const hasChartActivity = monthly.some((entry) =>
    Number(entry?.storage_gb || 0) > 0
    || Number(entry?.files || 0) > 0
    || Number(entry?.buckets || 0) > 0
  );
  const rangeLabel = `${formatMonthInputValue(chartRange.startMonth)} to ${formatMonthInputValue(chartRange.endMonth)}`;

  return (
    <div className={`min-h-[100dvh] ${palette.app}`}>
      <input
        ref={avatarInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleAvatarChange}
      />

      {/* Top Nav */}
      <nav className={`sticky top-0 z-30 border-b px-4 py-4 sm:px-6 ${navBg}`}>
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4">
          {/* Welcome */}
          <div className="min-w-0">
            {loading ? (
              <div className={`h-7 w-48 animate-pulse rounded-full ${isDark ? 'bg-white/10' : 'bg-slate-200'}`} />
            ) : (
              <p className={`truncate text-lg font-semibold tracking-tight sm:text-xl ${titleText}`}>
                Welcome back, <span className="text-blue-500">{profile?.full_name?.split(' ')[0] || 'User'}</span>
              </p>
            )}
            <p className={`mt-0.5 truncate text-sm ${mutedText}`}>Your workspace overview in one place.</p>
          </div>

          {/* Right actions */}
          <div className="flex shrink-0 items-center gap-2 sm:gap-3">
            <WorkspaceSwitcher workspaces={workspaces} active={activeWorkspace} />
            {/* Team facepile — overlapping member avatars (owners only) */}
            <TeamFacepile />

            {/* Control cluster: theme · notifications */}
            <div className={`flex items-center gap-0.5 rounded-full border p-1 ${groupBg}`}>
              {/* Theme toggle */}
              <button
                type="button"
                onClick={onToggleTheme}
                aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
                className={iconBtn}
              >
                <ThemeModeIcon theme={theme} />
              </button>

              {/* Notifications */}
              <div className="relative" ref={notifRef}>
                <button
                  type="button"
                  onClick={() => setNotifOpen(o => !o)}
                  aria-label="Open notifications"
                  className={`relative ${iconBtn}`}
                >
                  <BellIcon />
                  {unreadCount > 0 && (
                    <span className={`pointer-events-none absolute -right-0.5 -top-0.5 flex h-[18px] min-w-[18px] items-center justify-center rounded-full bg-blue-500 px-1 text-[10px] font-bold leading-none text-white ring-2 ${isDark ? 'ring-slate-950' : 'ring-white'}`}>{unreadCount > 99 ? '99+' : unreadCount}</span>
                  )}
                </button>

                {notifOpen && (
                  <div className={`absolute right-0 top-12 z-50 w-[28rem] max-w-[94vw] rounded-[1.1rem] border p-4 ${dropBg}`}>
                    <div className="mb-2 flex items-center justify-between">
                      <p className={`text-xs font-semibold uppercase tracking-widest ${mutedText}`}>Notifications</p>
                      <div className="flex items-center gap-3">
                        {unreadCount > 0 && (
                          <button type="button" onClick={handleMarkAllRead} className="text-xs text-blue-500 hover:underline">Mark all read</button>
                        )}
                        {notifications.length > 0 && (
                          <button type="button" onClick={handleDeleteAllNotifications} className="text-xs text-red-400 hover:underline">Delete all</button>
                        )}
                      </div>
                    </div>
                    {notifications.length === 0 ? (
                      <p className={`py-4 text-center text-sm ${mutedText}`}>You are all caught up.</p>
                    ) : (
                      <div className="space-y-1 max-h-72 overflow-y-auto">
                        {notifications.map(n => (
                          <div
                            key={n.id}
                            role="button"
                            tabIndex={0}
                            onClick={() => handleMarkNotificationRead(n.id)}
                            onKeyDown={(event) => {
                              if (event.key === 'Enter' || event.key === ' ') {
                                event.preventDefault();
                                handleMarkNotificationRead(n.id);
                              }
                            }}
                            className={`group rounded-xl px-3 py-2.5 transition ${n.is_read ? (isDark ? 'hover:bg-white/[0.04]' : 'hover:bg-slate-50') : isDark ? 'bg-blue-500/10 hover:bg-blue-500/14' : 'bg-blue-50 hover:bg-blue-100/70'}`}
                          >
                            <div className="flex items-start justify-between gap-3">
                              <div className="min-w-0 flex-1">
                                <p className={`text-xs font-semibold ${n.type === 'error' ? 'text-red-400' : n.type === 'warning' ? 'text-amber-400' : n.type === 'success' ? 'text-green-400' : 'text-blue-400'}`}>{n.title}</p>
                                <p className={`mt-0.5 text-xs ${bodyText}`}>{n.message}</p>
                                <p className={`mt-1 text-[11px] ${mutedText}`}>{fmtTime(n.created_at)}</p>
                              </div>
                              <button
                                type="button"
                                aria-label="Delete notification"
                                onClick={(event) => {
                                  event.stopPropagation();
                                  handleDeleteNotification(n.id);
                                }}
                                className={`mt-0.5 shrink-0 rounded-full p-1.5 opacity-0 transition group-hover:opacity-100 ${isDark ? 'text-white/60 hover:bg-white/10 hover:text-white' : 'text-slate-500 hover:bg-slate-200 hover:text-slate-900'}`}
                              >
                                <CloseIcon />
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Divider */}
            <div className={`hidden h-7 w-px sm:block ${isDark ? 'bg-white/10' : 'bg-slate-200'}`} />

            {/* Profile */}
            <button
              type="button"
              aria-label="Open profile"
              onClick={() => setProfileOpen(true)}
              className="group inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/60"
            >
              {profile?.avatar_url && !avatarLoadError ? (
                <img
                  src={profile.avatar_url}
                  alt=""
                  onError={() => setAvatarLoadError(true)}
                  className={`h-10 w-10 rounded-full object-cover ring-2 transition group-hover:ring-blue-500/70 ${isDark ? 'ring-white/15' : 'ring-slate-200'}`}
                />
              ) : (
                <span className={`flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-indigo-500 text-sm font-semibold text-white ring-2 transition group-hover:ring-blue-500/70 ${isDark ? 'ring-white/15' : 'ring-white'}`}>
                  {(profile?.full_name?.charAt(0) || 'U').toUpperCase()}
                </span>
              )}
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 pb-8 pt-4 sm:px-6 sm:pb-10 sm:pt-5">
        <div className="mb-6 flex justify-end">
          <button
            type="button"
            onClick={() => setCreateOpen(true)}
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-[0_14px_34px_rgba(37,99,235,0.22)] transition hover:bg-blue-500"
          >
            <PlusIcon />
            Create Bucket
          </button>
        </div>

        {/* 4 Metric Cards */}
        <div className="mb-8 grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
          {metricCards.map((m) => (
            <div key={m.label} className={`rounded-[1.2rem] border px-6 py-4 ${cardBg}`}>
              <p className={`text-sm font-medium ${mutedText}`}>{m.label}</p>
              <p className={`mt-2 text-3xl font-semibold tracking-tight ${titleText}`}>{loading ? '—' : m.value}</p>
              <p className={`mt-1 text-sm ${mutedText}`}>{m.sub}</p>
            </div>
          ))}
        </div>

        {/* Activity Overview */}
        <div className={`mb-8 rounded-[1.2rem] border p-6 ${cardBg}`}>
          <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className={`text-base font-semibold ${titleText}`}>Activity Overview</p>
              <p className={`mt-1 text-sm ${mutedText}`}>Buckets, files and storage</p>
            </div>
            <div className="relative self-start" ref={rangePickerRef}>
              <button
                type="button"
                onClick={() => setRangePickerOpen((open) => !open)}
                className={`flex min-w-[18rem] items-center justify-between gap-3 rounded-xl border px-4 py-2.5 text-left text-sm font-medium transition ${palette.secondary}`}
              >
                <div>
                  <span className={`mb-1 block text-[11px] font-semibold uppercase tracking-[0.16em] ${mutedText}`}>Date Range</span>
                  <span className={titleText}>{rangeLabel}</span>
                </div>
                <svg viewBox="0 0 24 24" className={`h-4 w-4 shrink-0 transition ${rangePickerOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="m6 9 6 6 6-6" />
                </svg>
              </button>

              {rangePickerOpen && (
                <div className={`absolute right-0 top-[calc(100%+0.75rem)] z-20 w-[min(24rem,calc(100vw-3rem))] rounded-[1.1rem] border p-4 ${dropBg}`}>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <label className="block">
                      <span className={`mb-1.5 block text-xs font-semibold uppercase tracking-[0.16em] ${mutedText}`}>Start</span>
                      <input
                        type="month"
                        value={chartRange.startMonth}
                        max={chartRange.endMonth}
                        onChange={(event) => handleStartMonthChange(event.target.value)}
                        className={`w-full rounded-xl border px-3 py-2 text-sm outline-none transition ${palette.input}`}
                      />
                    </label>
                    <label className="block">
                      <span className={`mb-1.5 block text-xs font-semibold uppercase tracking-[0.16em] ${mutedText}`}>End</span>
                      <input
                        type="month"
                        value={chartRange.endMonth}
                        min={chartRange.startMonth}
                        max={currentMonth}
                        onChange={(event) => handleEndMonthChange(event.target.value)}
                        className={`w-full rounded-xl border px-3 py-2 text-sm outline-none transition ${palette.input}`}
                      />
                    </label>
                  </div>
                  <div className="mt-4 flex justify-end">
                    <button
                      type="button"
                      onClick={handleResetChartRange}
                      className={`rounded-xl border px-4 py-2 text-sm font-medium transition ${palette.secondary}`}
                    >
                      Reset
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
          {chartLoading ? (
            <div className="h-[250px] animate-pulse rounded-xl" style={{ background: theme === 'dark' ? 'rgba(255,255,255,0.04)' : 'rgba(15,23,42,0.04)' }} />
          ) : !monthly.length || !hasChartActivity ? (
            <p className={`py-14 text-center text-sm ${mutedText}`}>No activity data in the selected range</p>
          ) : (
            <MultiLineChart data={monthly} theme={theme} />
          )}
        </div>

        {/* Buckets */}
        <div className={`rounded-[1.2rem] border p-6 ${cardBg}`}>
          <p className={`mb-4 text-xs font-semibold uppercase tracking-widest ${mutedText}`}>Your Buckets</p>
          {loading ? (
            <div className={`overflow-hidden rounded-[1.2rem] border ${tableShell}`}>
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className={`h-16 animate-pulse border-b ${tableRow}`} />
              ))}
            </div>
          ) : buckets.length === 0 ? (
            <div className={`rounded-[1.2rem] border p-12 text-center ${cardBg}`}>
              <p className={`text-base ${mutedText}`}>Create your first bucket to get started.</p>
              <button
                type="button"
                onClick={() => setCreateOpen(true)}
                className="mt-5 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-500"
              >
                Create Bucket
              </button>
            </div>
          ) : (
            <div className={`overflow-hidden rounded-[1.2rem] border ${tableShell}`}>
              <div className="overflow-x-auto">
                <div className="min-w-[860px]">
                  <div className={`grid grid-cols-[minmax(0,2.2fr)_1.2fr_0.8fr_1fr_1.4fr] gap-4 border-b px-5 py-4 text-xs font-semibold uppercase tracking-[0.18em] ${tableHead} ${tableDivider}`}>
                    <span>Name</span>
                    <span>Created At</span>
                    <span>Files</span>
                    <span>Storage</span>
                    {/* Center the label over the visible controls cluster, not the whole column.
                        The 152px box mirrors the row's actions width (w-28 slot + gap-3 + trash button)
                        so the label tracks the cluster at any column width. */}
                    <span className="flex items-center justify-center">
                      <span className="flex w-[152px] justify-end pr-5">Actions</span>
                    </span>
                  </div>
                  {buckets.map((b) => (
                    <div
                      key={b.id}
                      className={`grid grid-cols-[minmax(0,2.2fr)_1.2fr_0.8fr_1fr_1.4fr] items-center gap-4 border-b px-5 py-4 text-sm transition ${tableRow} ${isDark ? 'text-white/88' : 'text-slate-800'}`}
                    >
                      <div className="min-w-0">
                        <button
                          type="button"
                          onClick={() => navigate(`/bucket/${b.id}`, { state: { bucket: b } })}
                          className={`truncate text-left font-semibold hover:underline ${titleText}`}
                        >
                          {b.name}
                        </button>
                        {b.description && (
                          <p className={`mt-1 truncate text-xs ${mutedText}`}>{b.description}</p>
                        )}
                      </div>
                      <span>{fmtDate(b.created_at)}</span>
                      <span>{b.file_count}</span>
                      <span>{fmtBucketStorage(b.storage_used, b.storage_gb)}</span>
                      <div className="flex items-center justify-center gap-3">
                        {/* Fixed-width slot keeps the delete button in place no matter how many members */}
                        <div className="flex w-28 justify-end">
                          {/* Current members + add new — opens the bucket access modal */}
                          <BucketMembers bucketId={b.id} bucketName={b.name} />
                        </div>
                        {/* Delete bucket */}
                        <button
                          type="button"
                          onClick={() => handleDeleteBucket(b.id, b.name)}
                          disabled={deletingBucketId === b.id}
                          title="Delete bucket"
                          aria-label="Delete bucket"
                          className={`inline-flex items-center justify-center rounded-full p-1.5 transition disabled:opacity-50 ${deletingBucketId === b.id ? 'animate-pulse' : ''} ${isDark ? 'text-red-300 hover:bg-red-500/10 hover:text-red-200' : 'text-red-600 hover:bg-red-50 hover:text-red-500'}`}
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                            <path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6" />
                            <line x1="10" y1="11" x2="10" y2="17" />
                            <line x1="14" y1="11" x2="14" y2="17" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Create Bucket Modal */}
      {createOpen && (
        <div className={`fixed inset-0 z-50 flex items-center justify-center px-4 ${theme === 'light' ? 'bg-white/45' : palette.overlay} backdrop-blur-sm`}>
          <div className={`w-full max-w-lg rounded-[1.2rem] border p-7 shadow-2xl ${theme === 'light' ? 'border-slate-200 bg-white text-slate-900 shadow-[0_24px_80px_rgba(148,163,184,0.22)]' : palette.card}`}>
            <h2 className={`mb-2 text-lg font-semibold ${titleText}`}>Create New Bucket</h2>
            <p className={`mb-5 text-sm ${bodyText}`}>Set up a new bucket with a name and description.</p>
            <form className="space-y-3" onSubmit={handleCreateBucket}>
              <Input label="Bucket Name" theme={theme} value={newBucket.name} onChange={e => setNewBucket(b => ({ ...b, name: e.target.value }))} placeholder="e.g. Company Research" disabled={creating} />
              <TextArea
                label="Description (optional)"
                theme={theme}
                value={newBucket.description}
                onChange={e => setNewBucket(b => ({ ...b, description: e.target.value }))}
                placeholder="What's in this bucket?"
                disabled={creating}
                rows={5}
              />
              <div className="flex gap-2 pt-2">
                <button type="button" onClick={() => setCreateOpen(false)} disabled={creating}
                  className={`flex-1 rounded-2xl border px-4 py-2.5 text-sm font-medium transition ${palette.secondary}`}>
                  Cancel
                </button>
                <PrimaryButton theme={theme} loading={creating}>Create</PrimaryButton>
              </div>
            </form>
          </div>
        </div>
      )}

      <ProfileDrawer
        theme={theme}
        profile={profile}
        stats={stats}
        billingPlan={billingPlan}
        open={profileOpen}
        onClose={() => setProfileOpen(false)}
        draft={profileDraft}
        onDraftChange={(key, value) => setProfileDraft((prev) => ({ ...prev, [key]: value }))}
        passwordDraft={passwordDraft}
        onPasswordChange={(key, value) => setPasswordDraft((prev) => ({ ...prev, [key]: value }))}
        onToggleTheme={onToggleTheme}
        feedback={profileFeedback}
        savingProfile={savingProfile}
        changingPassword={changingPassword}
        connectingProvider={connectingProvider}
        disconnectingProvider={disconnectingProvider}
        uploadingAvatar={uploadingAvatar}
        deletingBuckets={deletingBuckets}
        deletingAccount={deletingAccount}
        onSaveProfile={handleSaveProfile}
        onAvatarPick={() => avatarInputRef.current?.click()}
        onChangePassword={handleChangePassword}
        onConnectProvider={handleStartConnectProvider}
        onDisconnectProvider={handleDisconnectProvider}
        onRequestLimitIncrease={(planData) => window.dispatchEvent(new CustomEvent('aiveilix:limit-hit', {
          detail: {
            message: planData?.plan === 'business'
              ? 'Tell us what limits you want increased and the admin team will review it.'
              : "You've reached a plan limit on your current plan.",
            planData,
          },
        }))}
        onDeleteAllBuckets={handleDeleteAllBuckets}
        onDeleteAccount={handleDeleteAccount}
        onLogout={handleLogout}
      />
    </div>
  );
}

function Toggle({ enabled, onToggle, isDark }) {
  return (
    <button
      type="button"
      onClick={onToggle}
      className={`relative inline-flex h-5 w-9 shrink-0 items-center rounded-full transition-colors ${enabled ? 'bg-blue-500' : isDark ? 'bg-white/15' : 'bg-slate-200'}`}
    >
      <span className={`inline-block h-3.5 w-3.5 rounded-full bg-white shadow transition-transform ${enabled ? 'translate-x-4' : 'translate-x-0.5'}`} />
    </button>
  );
}

function McpTokenCard({ tok, isDark, muted, toolDescs, onRevoke, onToggleTool, onUpdateOrigins, onRename, onViewLogs }) {
  const [copied, setCopied] = useState(false);
  const [advOpen, setAdvOpen] = useState(false);
  const [originsText, setOriginsText] = useState((tok.allowed_origins || []).join('\n'));
  const [nameVal, setNameVal] = useState(tok.name);

  function copyUrl() {
    navigator.clipboard.writeText(tok.mcp_url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  const card = isDark ? 'border-white/[0.06] bg-white/[0.03]' : 'border-slate-100 bg-slate-50/50';
  const inputCls = `w-full bg-transparent text-sm font-semibold outline-none ${isDark ? 'text-white placeholder:text-white/30' : 'text-slate-900 placeholder:text-slate-400'}`;

  return (
    <div className={`rounded-xl border px-4 py-3 space-y-2.5 ${card}`}>

      {/* Row 1 — name (editable) + actions */}
      <div className="flex items-center gap-2">
        <input
          className={`flex-1 ${inputCls}`}
          value={nameVal}
          onChange={e => setNameVal(e.target.value)}
          onBlur={() => nameVal.trim() && onRename(tok.id, nameVal.trim())}
          onKeyDown={e => { if (e.key === 'Enter') { e.target.blur(); } }}
          placeholder="Token name"
        />
        <button type="button" onClick={() => onViewLogs(tok)} className={`rounded-lg px-2.5 py-1 text-xs font-medium transition ${isDark ? 'bg-white/[0.06] text-blue-400 hover:bg-blue-500/10' : 'bg-blue-50 text-blue-600 hover:bg-blue-100'}`}>Logs</button>
        <button type="button" onClick={() => onRevoke(tok.id)} className={`rounded-lg px-2.5 py-1 text-xs font-medium transition ${isDark ? 'bg-red-500/[0.08] text-red-400 hover:bg-red-500/15' : 'bg-red-50 text-red-600 hover:bg-red-100'}`}>Revoke</button>
      </div>

      {/* Row 2 — MCP URL */}
      <div className={`flex items-center gap-2 rounded-lg px-3 py-2 ${isDark ? 'bg-white/[0.05]' : 'bg-slate-100/70'}`}>
        <code className={`flex-1 truncate text-xs ${isDark ? 'text-slate-300' : 'text-slate-500'}`}>{tok.mcp_url}</code>
        <button type="button" onClick={copyUrl} className={`shrink-0 text-xs font-semibold ${isDark ? 'text-blue-400 hover:text-blue-300' : 'text-blue-600 hover:text-blue-500'}`}>
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>

      {/* Row 3 — Advanced settings toggle */}
      <button
        type="button"
        onClick={() => setAdvOpen(o => !o)}
        className={`flex items-center gap-1.5 text-xs font-medium transition ${isDark ? 'text-white/40 hover:text-white/70' : 'text-slate-400 hover:text-slate-600'}`}
      >
        <svg viewBox="0 0 16 16" className={`h-3 w-3 fill-current transition-transform ${advOpen ? 'rotate-90' : ''}`}><path d="M6 3l5 5-5 5V3z"/></svg>
        Advanced settings
      </button>

      {/* Advanced — tools list + URL restrictions */}
      {advOpen && (
        <div className="space-y-2 pt-0.5">
          {/* Tools — one row per tool */}
          <div className={`rounded-lg overflow-hidden ${isDark ? 'bg-white/[0.04]' : 'bg-white/80'}`}>
            {Object.entries(toolDescs).map(([tool, desc], i, arr) => {
              const enabled = tok.allowed_tools.includes(tool);
              return (
                <div
                  key={tool}
                  className={`flex items-center gap-3 px-3 py-2 ${i < arr.length - 1 ? isDark ? 'border-b border-white/[0.04]' : 'border-b border-slate-100/80' : ''}`}
                >
                  <div className="flex-1 min-w-0">
                    <p className={`text-xs font-semibold font-mono ${isDark ? 'text-white/80' : 'text-slate-700'}`}>{tool}</p>
                    <p className={`text-[10px] truncate ${muted}`}>{desc}</p>
                  </div>
                  <Toggle enabled={enabled} onToggle={() => onToggleTool(tok.id, tool, !enabled)} isDark={isDark} />
                </div>
              );
            })}
          </div>

          {/* URL restrictions */}
          <div className="space-y-1">
            <p className={`text-[10px] font-semibold uppercase tracking-wide ${muted}`}>Allowed Origins <span className="normal-case font-normal">(empty = allow all)</span></p>
            <textarea
              rows={2}
              className={`w-full rounded-lg px-3 py-2 text-xs font-mono resize-none outline-none ${isDark ? 'bg-white/[0.05] text-slate-200 placeholder:text-white/20' : 'bg-white/80 text-slate-700 placeholder:text-slate-400'}`}
              value={originsText}
              onChange={e => setOriginsText(e.target.value)}
              placeholder="https://yourapp.com"
            />
            <button
              type="button"
              onClick={() => onUpdateOrigins(tok.id, originsText)}
              className={`rounded-lg px-3 py-1 text-xs font-semibold ${isDark ? 'bg-white/[0.06] text-white hover:bg-white/10' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'}`}
            >
              Save
            </button>
          </div>
        </div>
      )}

      {/* Row last — meta */}
      <p className={`text-[10px] ${muted}`}>
        Created {new Date(tok.created_at).toLocaleDateString()} · {tok.last_used_at ? `Last used ${new Date(tok.last_used_at).toLocaleString()}` : 'Never used'}
      </p>

    </div>
  );
}

function BucketPage({ theme }) {
  const palette = themeOptions[theme];
  const navigate = useNavigate();
  const location = useLocation();
  const { bucketId } = useParams();
  const seedBucket = location.state?.bucket;

  // UI
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);
  const [composer, setComposer] = useState('');
  const [threadMenuOpen, setThreadMenuOpen] = useState(null);
  const [copiedId, setCopiedId] = useState(null);
  const [sourcePinpoint, setSourcePinpoint] = useState(null);
  const [editingMsgId, setEditingMsgId] = useState(null);
  const [editingContent, setEditingContent] = useState('');
  const [composerReferencedFileIds, setComposerReferencedFileIds] = useState([]);
  const [inFlightReferencedFileIds, setInFlightReferencedFileIds] = useState([]);

  // Data
  const [bucket, setBucket] = useState(seedBucket || null);
  const [threads, setThreads] = useState([]);
  const [activeThreadId, setActiveThreadId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [filesPanel, setFilesPanel] = useState([]);

  // Loading / errors
  const [loading, setLoading] = useState(true);
  const [loadingMsgs, setLoadingMsgs] = useState(false);
  const [sending, setSending] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [directUploading, setDirectUploading] = useState(false);
  const [replacingFileId, setReplacingFileId] = useState(null);
  const [error, setError] = useState(null);

  const [pendingFiles, setPendingFiles] = useState([]);
  const [expandedSourceMsgId, setExpandedSourceMsgId] = useState(null);
  const [msgFeedback, setMsgFeedback] = useState(null); // { msgId, type, reason, submitted }
  const [thinkingSteps, setThinkingSteps] = useState(null); // list of strings shown while generating
  const [currentStep, setCurrentStep] = useState(null); // { type, label } streamed live during a turn
  const [liveStepEvents, setLiveStepEvents] = useState([]);
  const [livePlan, setLivePlan] = useState([]); // [{id, task, status}] streamed from the harness
  const [livePartialText, setLivePartialText] = useState(''); // tokens streamed for the in-progress answer
  const [webOffHint, setWebOffHint] = useState(0); // bumped when agent replies with "web mode is off"
  const [workStartedAt, setWorkStartedAt] = useState(null);
  const [workElapsedMs, setWorkElapsedMs] = useState(0);
  const [pendingAction, setPendingAction] = useState(null); // { messageId, action_type, options, bucketId, convId, originalQuestion }
  const [mcpModalOpen, setMcpModalOpen] = useState(false);
  const [mcpTab, setMcpTab] = useState('tokens'); // 'tokens' | tokenId string
  const [mcpTokens, setMcpTokens] = useState([]);
  const [mcpLoading, setMcpLoading] = useState(false);
  const [mcpError, setMcpError] = useState(null);
  const [mcpToolDescs, setMcpToolDescs] = useState({});
  // mcpLogsTabs: [{ tokId, tokName, logs, total, loading, error, offset }]
  const [mcpLogsTabs, setMcpLogsTabs] = useState([]);
  const MCP_LOGS_LIMIT = 50;
  const abortCtrlRef = useRef(null);

  const composerRef = useRef(null);
  const uploadRef = useRef(null);
  const directUploadRef = useRef(null);
  const replaceRef = useRef(null);
  const msgsEndRef = useRef(null);
  const [webSearchEnabled, setWebSearchEnabled] = useState(() => {
    if (typeof window === 'undefined') return false;
    return window.localStorage.getItem('aiveilix-web-search-enabled') === '1';
  });

  useEffect(() => {
    if (!sending || !workStartedAt) return;
    const timer = setInterval(() => {
      setWorkElapsedMs(Date.now() - workStartedAt);
    }, 1000);
    return () => clearInterval(timer);
  }, [sending, workStartedAt]);

  useEffect(() => {
    window.localStorage.setItem('aiveilix-web-search-enabled', webSearchEnabled ? '1' : '0');
  }, [webSearchEnabled]);

  // Thread file scope (null = full bucket access; array = scoped to these file_ids)
  const [threadScope, setThreadScope] = useState(null);
  const [scopeModalOpen, setScopeModalOpen] = useState(false);
  const [scopeDraft, setScopeDraft] = useState([]);
  const [scopeSaving, setScopeSaving] = useState(false);
  // Out-of-scope mention prompt: { files: [...], onConfirm: fn }
  const [scopeRequest, setScopeRequest] = useState(null);

  // Load scope whenever active thread changes
  useEffect(() => {
    if (!activeThreadId || !bucketId) { setThreadScope(null); return; }
    let cancelled = false;
    (async () => {
      try {
        const data = await bucketApi.getThreadScope(bucketId, activeThreadId);
        if (!cancelled) {
          // scoped=true -> array (may be empty = "no files"); scoped=false -> null (full access)
          setThreadScope(data?.scoped ? (data.file_ids || []).map(String) : null);
        }
      } catch (_) {
        if (!cancelled) setThreadScope(null);
      }
    })();
    return () => { cancelled = true; };
  }, [activeThreadId, bucketId]);

  const openScopeModal = () => {
    // threadScope: null = full access (all eyes on); array = the visible subset
    // (may be empty = every eye off / "no files"). Default new threads to full.
    const allIds = filesPanel.map(f => String(f.id));
    setScopeDraft(threadScope !== null ? [...threadScope] : allIds);
    setScopeModalOpen(true);
  };

  const saveScope = async () => {
    if (!activeThreadId) return;
    setScopeSaving(true);
    try {
      // All eyes on => full access (scoped=false). Any eye off (incl. all off
      // => "no files") => a filter is active and we persist the visible subset.
      const allIds = filesPanel.map(f => String(f.id));
      const fullAccess = allIds.length === 0 || allIds.every(id => scopeDraft.includes(id));
      const scoped = !fullAccess;
      const data = await bucketApi.setThreadScope(bucketId, activeThreadId, scoped ? scopeDraft : [], scoped);
      setThreadScope(data?.scoped ? (data.file_ids || []).map(String) : null);
      setScopeModalOpen(false);
    } catch (e) {
      setError(e.message);
    } finally {
      setScopeSaving(false);
    }
  };

  // Speech-to-text (mic) state — full-width volume-reactive bars like ChatGPT
  const NUM_BARS = 48;
  const [isRecording, setIsRecording] = useState(false);
  const [barLevels, setBarLevels] = useState(() => new Array(NUM_BARS).fill(0.08));
  const recognitionRef = useRef(null);
  const composerBaseRef = useRef('');
  const audioCtxRef = useRef(null);
  const analyserRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const rafRef = useRef(null);

  const stopRecording = () => {
    try { recognitionRef.current?.stop(); } catch (_) {}
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    rafRef.current = null;
    try { mediaStreamRef.current?.getTracks().forEach(t => t.stop()); } catch (_) {}
    mediaStreamRef.current = null;
    try { audioCtxRef.current?.close(); } catch (_) {}
    audioCtxRef.current = null;
    analyserRef.current = null;
    setBarLevels(new Array(NUM_BARS).fill(0.08));
    setIsRecording(false);
  };

  const toggleRecording = async () => {
    if (isRecording) { stopRecording(); return; }
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      setError('Speech recognition not supported in this browser. Try Chrome or Edge.');
      return;
    }
    // 1) Get mic stream for volume analysis
    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (e) {
      setError('Microphone access denied.');
      return;
    }
    mediaStreamRef.current = stream;
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    const ctx = new AudioCtx();
    audioCtxRef.current = ctx;
    const source = ctx.createMediaStreamSource(stream);
    const analyser = ctx.createAnalyser();
    analyser.fftSize = 256;
    analyser.smoothingTimeConstant = 0.7;
    source.connect(analyser);
    analyserRef.current = analyser;
    const freqData = new Uint8Array(analyser.frequencyBinCount);

    const tick = () => {
      if (!analyserRef.current) return;
      analyser.getByteFrequencyData(freqData);
      // Map frequency bins → NUM_BARS bars
      const next = new Array(NUM_BARS);
      const binsPerBar = Math.floor(freqData.length / NUM_BARS) || 1;
      for (let i = 0; i < NUM_BARS; i++) {
        let sum = 0;
        for (let j = 0; j < binsPerBar; j++) sum += freqData[i * binsPerBar + j] || 0;
        const avg = sum / binsPerBar / 255; // 0..1
        // Boost low values so quiet speech is visible, clamp at 1
        next[i] = Math.max(0.08, Math.min(1, avg * 1.8));
      }
      setBarLevels(next);
      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);

    // 2) Start SpeechRecognition for transcription
    const rec = new SR();
    rec.continuous = true;
    rec.interimResults = true;
    rec.lang = navigator.language || 'en-US';
    composerBaseRef.current = composer ? composer.trimEnd() + ' ' : '';
    rec.onresult = (event) => {
      let finalText = '';
      let interimText = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) finalText += transcript;
        else interimText += transcript;
      }
      if (finalText) composerBaseRef.current += finalText;
      setComposer(composerBaseRef.current + interimText);
    };
    rec.onerror = (e) => {
      if (e.error && e.error !== 'no-speech' && e.error !== 'aborted') {
        setError(`Mic error: ${e.error}`);
      }
      stopRecording();
    };
    rec.onend = () => stopRecording();
    recognitionRef.current = rec;
    try {
      rec.start();
      setIsRecording(true);
    } catch (_) {
      stopRecording();
    }
  };

  // Auto-resize composer
  useEffect(() => {
    if (!composerRef.current) return;
    composerRef.current.style.height = '0px';
    composerRef.current.style.height = `${Math.min(composerRef.current.scrollHeight, 180)}px`;
  }, [composer]);

  useEffect(() => {
    const mentions = Array.from(composer.matchAll(/@([^\s]+)/g)).map((match) => match[1]);
    const nextIds = filesPanel
      .filter((file) => mentions.includes((file.name || '').replace(/\s+/g, '_')))
      .map((file) => String(file.id));
    setComposerReferencedFileIds(nextIds);
  }, [composer, filesPanel]);

  // Scroll to latest message
  useEffect(() => {
    msgsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auto-expand sources for the latest assistant message, collapse the rest
  useEffect(() => {
    const last = [...messages].reverse().find(m => m.role === 'assistant');
    if (last) {
      const { sources } = parseAssistantContent(last.content);
      if (sources.length > 0) setExpandedSourceMsgId(last.id);
    }
  }, [messages]);

  // Poll file list every 4s while any file is still processing
  useEffect(() => {
    const hasProcessing = filesPanel.some(f => f.status === 'processing' || f.status === 'uploading');
    if (!hasProcessing) return;
    const timer = setInterval(async () => {
      try {
        const data = await bucketApi.listFiles(bucketId);
        setFilesPanel(data.files || []);
      } catch (_) {}
    }, 4000);
    return () => clearInterval(timer);
  }, [filesPanel, bucketId]);

  // Load conversations + files + bucket on mount
  useEffect(() => {
    const token = sessionStorage.getItem('access_token');
    if (!token) { navigate('/login'); return; }

    async function init() {
      try {
        const [convData, fileData, bucketData] = await Promise.all([
          bucketApi.listConversations(bucketId),
          bucketApi.listFiles(bucketId),
          bucketApi.get(bucketId),
        ]);
        setBucket(bucketData);
        let convs = convData.conversations || [];
        // Auto-create a thread if bucket has none
        if (convs.length === 0) {
          const newConv = await bucketApi.createConversation(bucketId, 'New Chat');
          convs = [newConv];
        }
        setThreads(convs);
        setFilesPanel(fileData.files || []);
        setActiveThreadId(convs[0].id);
        const msgData = await bucketApi.getMessages(bucketId, convs[0].id);
        setMessages(msgData.messages || []);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, [bucketId, navigate]);

  async function loadMessages(threadId) {
    setLoadingMsgs(true);
    setMessages([]);
    try {
      const data = await bucketApi.getMessages(bucketId, threadId);
      setMessages(data.messages || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoadingMsgs(false);
    }
  }

  const handleSelectThread = async (threadId) => {
    setActiveThreadId(threadId);
    await loadMessages(threadId);
  };

  const handleCreateThread = async () => {
    if (threads.length >= 50) return;
    try {
      const conv = await bucketApi.createConversation(bucketId, 'New Chat');
      setThreads(prev => [conv, ...prev]);
      setActiveThreadId(conv.id);
      setMessages([]);
    } catch (e) {
      setError(e.message);
    }
  };

  const handleRenameThread = async (threadId) => {
    const current = threads.find(t => String(t.id) === String(threadId));
    const next = window.prompt('Rename thread', current?.title || '');
    if (!next?.trim()) return;
    try {
      const updated = await bucketApi.renameConversation(bucketId, threadId, next.trim());
      setThreads(prev => prev.map(t => String(t.id) === String(threadId) ? { ...t, title: updated.title } : t));
    } catch (e) {
      setError(e.message);
    }
    setThreadMenuOpen(null);
  };

  const handleTogglePinThread = async (threadId) => {
    const current = threads.find(t => String(t.id) === String(threadId));
    const newPinned = !current?.is_pinned;
    try {
      const updated = await bucketApi.pinConversation(bucketId, threadId, newPinned);
      setThreads(prev => {
        const mapped = prev.map(t => String(t.id) === String(threadId) ? { ...t, is_pinned: updated.is_pinned } : t);
        return [...mapped].sort((a, b) => Number(b.is_pinned) - Number(a.is_pinned));
      });
    } catch (e) {
      setError(e.message);
    }
    setThreadMenuOpen(null);
  };

  const handleDeleteThread = async (threadId) => {
    if (threads.length <= 1) return;
    try {
      await bucketApi.deleteConversation(bucketId, threadId);
      const remaining = threads.filter(t => String(t.id) !== String(threadId));
      setThreads(remaining);
      setThreadMenuOpen(null);
      if (String(activeThreadId) === String(threadId) && remaining[0]) {
        setActiveThreadId(remaining[0].id);
        await loadMessages(remaining[0].id);
      }
    } catch (e) {
      setError(e.message);
    }
  };

  // Reveal an assistant message word-by-word (typewriter effect) so the user
  // sees it stream in instead of appearing all at once.
  const typewriteAssistantMessage = (assistantMessage, wordsPerTick = 2, tickMs = 25) => {
    const fullContent = assistantMessage?.content || '';
    if (!fullContent) return;
    const tokens = fullContent.split(/(\s+)/);
    let i = 0;
    const step = Math.max(1, wordsPerTick * 2);
    const interval = setInterval(() => {
      i = Math.min(tokens.length, i + step);
      const partial = tokens.slice(0, i).join('');
      setMessages(prev => prev.map(m =>
        String(m.id) === String(assistantMessage.id) ? { ...m, content: partial } : m
      ));
      if (i >= tokens.length) clearInterval(interval);
    }, tickMs);
  };

  const copyToClipboard = (value, key) => {
    navigator.clipboard.writeText(value || '');
    setCopiedId(key);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleSend = async () => {
    const text = composer.trim();
    if ((!text && !pendingFiles.length) || sending || !activeThreadId) return;
    const ctrl = new AbortController();
    abortCtrlRef.current = ctrl;
    const filesToUpload = [...pendingFiles];
    const referencedFileIds = [...composerReferencedFileIds];

    // Scope enforcement: if thread is scoped and user @mentions a file NOT in scope,
    // pause and ask whether to add it to the thread.
    if (threadScope && referencedFileIds.length > 0) {
      const outOfScopeIds = referencedFileIds.filter(id => !threadScope.includes(String(id)));
      if (outOfScopeIds.length > 0) {
        const outOfScopeFiles = filesPanel.filter(f => outOfScopeIds.includes(String(f.id)));
        setScopeRequest({
          files: outOfScopeFiles,
          onConfirm: async () => {
            try {
              const next = Array.from(new Set([...(threadScope || []), ...outOfScopeIds.map(String)]));
              const data = await bucketApi.setThreadScope(bucketId, activeThreadId, next);
              const ids = data?.file_ids || [];
              setThreadScope(ids.length ? ids.map(String) : null);
              setScopeRequest(null);
              // Continue with the send now that scope is updated
              setTimeout(() => handleSend(), 0);
            } catch (e) {
              setError(e.message);
              setScopeRequest(null);
            }
          },
        });
        return;
      }
    }
    // Build chip-prefix for any freshly-attached files so they render as chips in the bubble.
    const attachedMentions = filesToUpload
      .map(f => '@' + (f.name || '').replace(/\s+/g, '_'))
      .filter(Boolean)
      .join(' ');
    const displayText = attachedMentions
      ? (text ? `${attachedMentions} ${text}` : attachedMentions)
      : text;
    setComposer('');
    setPendingFiles([]);
    setInFlightReferencedFileIds(referencedFileIds);
    setSending(true);
    setError(null);
    const tempId = `temp-${Date.now()}`;
    const processingId = `processing-${Date.now()}`;
    if (displayText) {
      setMessages(prev => [...prev, { id: tempId, role: 'user', content: displayText, created_at: new Date().toISOString() }]);
    }
    try {
      if (filesToUpload.length) {
        setUploading(true);
        const uploaded = await uploadFilesDirect(bucketId, filesToUpload);
        setUploading(false);
        const uploadedIds = (Array.isArray(uploaded) ? uploaded : []).map(f => String(f.id));
        // If thread is scoped, auto-add the new uploads so the user doesn't get blocked.
        if (threadScope && uploadedIds.length > 0) {
          try {
            const next = Array.from(new Set([...threadScope, ...uploadedIds]));
            const data = await bucketApi.setThreadScope(bucketId, activeThreadId, next);
            const ids = data?.file_ids || [];
            setThreadScope(ids.length ? ids.map(String) : null);
          } catch (_) {}
        }
        // If user also sent text, wait for files to be ready before sending to AI
        if (text && uploadedIds.length > 0) {
          setMessages(prev => [...prev, {
            id: processingId,
            role: 'processing',
            content: `${uploadedIds.length === 1 ? 'File is' : `${uploadedIds.length} files are`} processing — I'll respond once I've read ${uploadedIds.length === 1 ? 'it' : 'them'}…`,
          }]);
          // Poll until all uploaded files are ready or failed
          const maxAttempts = 40;
          for (let i = 0; i < maxAttempts; i++) {
            await new Promise(r => setTimeout(r, 3000));
            try {
              const data = await bucketApi.listFiles(bucketId);
              const allFiles = data.files || [];
              setFilesPanel(allFiles);
              const allDone = uploadedIds.every(id => {
                const f = allFiles.find(f => String(f.id) === id);
                return !f || f.status === 'ready' || f.status === 'failed';
              });
              if (allDone) break;
            } catch (_) {}
          }
          setMessages(prev => prev.filter(m => m.id !== processingId));
        } else {
          const data = await bucketApi.listFiles(bucketId);
          setFilesPanel(data.files || []);
        }
      }
      if (displayText) {
        const turnStartedAt = Date.now();
        const collectedStepEvents = [{ type: 'thinking', label: 'Thinking...' }];
        setWorkStartedAt(turnStartedAt);
        setWorkElapsedMs(0);
        setCurrentStep(collectedStepEvents[0]);
        setLiveStepEvents(collectedStepEvents);
        setThinkingSteps(null);
        setLivePlan([]);
        setLivePartialText('');
        const result = await bucketApi.sendMessageStream(
          bucketId,
          activeThreadId,
          displayText,
          ctrl.signal,
          { webSearch: webSearchEnabled },
          {
            onStep: (ev) => {
              collectedStepEvents.push(ev);
              setCurrentStep(ev);
              setLiveStepEvents([...collectedStepEvents]);
            },
            onPlan: (plan) => {
              setLivePlan(Array.isArray(plan) ? plan : []);
            },
            onToken: (text) => {
              setLivePartialText((prev) => prev + text);
            },
          },
        );
        const workDurationMs = Date.now() - turnStartedAt;
        setThinkingSteps(result.thinking_steps || null);
        setCurrentStep(null);
        setLiveStepEvents([]);
        setLivePlan([]);
        setLivePartialText('');
        setWorkStartedAt(null);
        setWorkElapsedMs(0);
        // Web-off polite reply → highlight the web toggle so the user can flip it on
        const replyText = result.assistant_message?.content || '';
        if (/web mode is off/i.test(replyText)) {
          setWebOffHint(Date.now());
        }
        setMessages(prev => [
          ...prev.filter(m => m.id !== tempId),
          result.user_message,
          {
            ...result.assistant_message,
            content: '',
            thinking_step_events: result.thinking_step_events || collectedStepEvents,
            thinking_steps: result.thinking_steps || collectedStepEvents.map(step => step.label),
            agent_plan: result.plan || result.assistant_message?.agent_plan || null,
            agent_steps: result.thinking_step_events || result.assistant_message?.agent_steps || null,
            work_duration_ms: workDurationMs,
          },
        ]);
        typewriteAssistantMessage(result.assistant_message);
        // If agent needs user action (e.g. web search permission), store it for button rendering
        if (result.action_required && result.action_type) {
          setPendingAction({
            messageId: result.assistant_message.id,
            action_type: result.action_type,
            options: result.action_options || [],
            bucketId,
            convId: activeThreadId,
            originalQuestion: text,
          });
        } else {
          setPendingAction(null);
        }
        setThreads(prev => prev.map(t =>
          String(t.id) === String(activeThreadId) ? { ...t, updated_at: new Date().toISOString() } : t
        ));
        const currentThread = threads.find(t => String(t.id) === String(activeThreadId));
        if (currentThread?.title === 'New Chat') {
          try {
            const updated = await bucketApi.autoTitleConversation(bucketId, activeThreadId, text);
            setThreads(prev => prev.map(t => String(t.id) === String(activeThreadId) ? { ...t, title: updated.title } : t));
          } catch (_) {
            try {
              const fallback = generateThreadTitle(text);
              const updated = await bucketApi.renameConversation(bucketId, activeThreadId, fallback);
              setThreads(prev => prev.map(t => String(t.id) === String(activeThreadId) ? { ...t, title: updated.title } : t));
            } catch (_) {}
          }
        }
      }
    } catch (e) {
      if (e.name !== 'AbortError') setError(e.message);
      setMessages(prev => prev.filter(m => m.id !== tempId && m.id !== processingId));
    } finally {
      setSending(false);
      setUploading(false);
      setCurrentStep(null);
      setLiveStepEvents([]);
      setLivePlan([]);
      setLivePartialText('');
      setWorkStartedAt(null);
      setWorkElapsedMs(0);
      setInFlightReferencedFileIds([]);
      abortCtrlRef.current = null;
    }
  };

  const handleStop = () => { abortCtrlRef.current?.abort(); };

  const handleEditSend = async (msgId) => {
    const text = editingContent.trim();
    if (!text || sending || !activeThreadId) return;
    const idx = messages.findIndex(m => String(m.id) === String(msgId));
    if (idx === -1) return;
    // Snapshot everything strictly before the edited message (does NOT include it)
    const before = messages.slice(0, idx);
    const tempId = `temp-${Date.now()}`;
    setEditingMsgId(null);
    setEditingContent('');
    setSending(true);
    setError(null);
    // Replace edited message + everything after with the new temp bubble
    setMessages([...before, { id: tempId, role: 'user', content: text, created_at: new Date().toISOString() }]);
    try {
      // Delete from DB: the edited message and everything after it
      await bucketApi.deleteMessagesFrom(bucketId, activeThreadId, msgId);
      const result = await bucketApi.sendMessage(bucketId, activeThreadId, text);
      setMessages([...before, result.user_message, { ...result.assistant_message, content: '' }]);
      typewriteAssistantMessage(result.assistant_message);
      setThreads(prev => prev.map(t =>
        String(t.id) === String(activeThreadId) ? { ...t, updated_at: new Date().toISOString() } : t
      ));
    } catch (e) {
      // Restore original messages on failure
      setMessages(prev => {
        const stillBefore = prev.filter((_, i) => i < before.length);
        return [...stillBefore, messages[idx]];
      });
      setError(e.message);
    } finally {
      setSending(false);
    }
  };

  const insertMentionIntoComposer = (file) => {
    const mention = `@${(file.name || '').replace(/\s+/g, '_')} `;
    const el = composerRef.current;
    if (el) {
      const start = el.selectionStart ?? composer.length;
      const newText = composer.slice(0, start) + mention + composer.slice(start);
      setComposer(newText);
      setTimeout(() => { el.focus(); el.setSelectionRange(start + mention.length, start + mention.length); }, 0);
    } else {
      setComposer(prev => prev + mention);
    }
  };

  const handleReferenceFile = (file) => {
    // If thread is scoped and this file isn't in scope, prompt to add it first.
    if (threadScope && !threadScope.includes(String(file.id))) {
      setScopeRequest({
        files: [file],
        onConfirm: async () => {
          try {
            const next = Array.from(new Set([...(threadScope || []), String(file.id)]));
            const data = await bucketApi.setThreadScope(bucketId, activeThreadId, next);
            const ids = data?.file_ids || [];
            setThreadScope(ids.length ? ids.map(String) : null);
            setScopeRequest(null);
            insertMentionIntoComposer(file);
          } catch (e) {
            setError(e.message);
            setScopeRequest(null);
          }
        },
      });
      return;
    }
    insertMentionIntoComposer(file);
  };

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files || []);
    event.target.value = '';
    if (!files.length) return;
    setPendingFiles(prev => [...prev, ...files]);
  };

  const handleDirectFileUpload = async (event) => {
    const files = Array.from(event.target.files || []);
    event.target.value = '';
    if (!files.length || directUploading) return;
    setError(null);
    setDirectUploading(true);
    try {
      const uploaded = await uploadFilesDirect(bucketId, files);
      const uploadedIds = (Array.isArray(uploaded) ? uploaded : []).map(f => String(f.id)).filter(Boolean);
      if (threadScope && activeThreadId && uploadedIds.length > 0) {
        try {
          const next = Array.from(new Set([...threadScope, ...uploadedIds]));
          const data = await bucketApi.setThreadScope(bucketId, activeThreadId, next);
          const ids = data?.file_ids || [];
          setThreadScope(ids.length ? ids.map(String) : null);
        } catch (_) {}
      }
      const data = await bucketApi.listFiles(bucketId);
      setFilesPanel(data.files || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setDirectUploading(false);
    }
  };

  const handleDownloadFile = async (file, event) => {
    event.stopPropagation();
    try {
      await bucketApi.downloadFile(bucketId, file.id, file.name);
    } catch (e) {
      setError(e.message);
    }
  };

  const handleDeleteFile = async (fileId) => {
    try {
      await bucketApi.deleteFile(bucketId, fileId);
      setFilesPanel(prev => prev.filter(f => String(f.id) !== String(fileId)));
    } catch (e) {
      setError(e.message);
    }
  };

  const handleReplaceFile = (fileId) => {
    setReplacingFileId(fileId);
    replaceRef.current?.click();
  };

  const handleReplaceFileInput = async (event) => {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file || !replacingFileId) return;
    setError(null);
    try {
      await bucketApi.replaceFile(bucketId, replacingFileId, file);
      const data = await bucketApi.listFiles(bucketId);
      setFilesPanel(data.files || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setReplacingFileId(null);
    }
  };

  async function openMcpModal() {
    setMcpModalOpen(true);
    setMcpLoading(true);
    setMcpError(null);
    try {
      const data = await bucketApi.listMcpTokens(bucketId);
      setMcpTokens(data.tokens || []);
      setMcpToolDescs(data.tool_descriptions || {});
    } catch (e) {
      setMcpError(e.message);
    } finally {
      setMcpLoading(false);
    }
  }

  async function handleCreateMcpToken() {
    const existingNames = new Set(mcpTokens.map(t => t.name.toLowerCase()));
    let n = mcpTokens.length + 1;
    let name = `Token ${n}`;
    while (existingNames.has(name.toLowerCase())) { n++; name = `Token ${n}`; }
    try {
      const token = await bucketApi.createMcpToken(bucketId, name, Object.keys(mcpToolDescs), []);
      setMcpTokens(prev => [...prev, token]);
    } catch (e) {
      setMcpError(e.message);
    }
  }

  async function handleRevokeMcpToken(tokenId) {
    try {
      await bucketApi.revokeMcpToken(bucketId, tokenId);
      setMcpTokens(prev => prev.filter(t => t.id !== tokenId));
      closeMcpLogsTab(tokenId);
    } catch (e) {
      setMcpError(e.message);
    }
  }

  async function handleToggleMcpTool(tokenId, tool, enabled) {
    const token = mcpTokens.find(t => t.id === tokenId);
    if (!token) return;
    const newTools = enabled
      ? [...token.allowed_tools, tool]
      : token.allowed_tools.filter(t => t !== tool);
    try {
      const updated = await bucketApi.updateMcpToken(bucketId, tokenId, { allowed_tools: newTools });
      setMcpTokens(prev => prev.map(t => t.id === tokenId ? updated : t));
    } catch (e) {
      setMcpError(e.message);
    }
  }

  async function handleUpdateMcpOrigins(tokenId, originsText) {
    const origins = originsText.split('\n').map(s => s.trim()).filter(Boolean);
    try {
      const updated = await bucketApi.updateMcpToken(bucketId, tokenId, { allowed_origins: origins });
      setMcpTokens(prev => prev.map(t => t.id === tokenId ? updated : t));
    } catch (e) {
      setMcpError(e.message);
    }
  }

  async function handleRenameMcpToken(tokenId, name) {
    const duplicate = mcpTokens.find(t => t.id !== tokenId && t.name.toLowerCase() === name.toLowerCase());
    if (duplicate) {
      setMcpError(`A token named "${name}" already exists.`);
      return;
    }
    try {
      const updated = await bucketApi.updateMcpToken(bucketId, tokenId, { name });
      setMcpTokens(prev => prev.map(t => t.id === tokenId ? updated : t));
      // Also update the tab name if it's open
      setMcpLogsTabs(prev => prev.map(t => t.tokId === tokenId ? { ...t, tokName: name } : t));
    } catch (e) {
      setMcpError(e.message);
    }
  }

  async function fetchMcpLogs(tokId, tokName, off = 0) {
    setMcpLogsTabs(prev => prev.map(t => t.tokId === tokId ? { ...t, loading: true, error: null } : t));
    try {
      const data = await bucketApi.getMcpTokenLogs(bucketId, tokId, MCP_LOGS_LIMIT, off);
      setMcpLogsTabs(prev => prev.map(t =>
        t.tokId === tokId ? { ...t, logs: data.logs || [], total: data.total || 0, offset: off, loading: false } : t
      ));
    } catch (e) {
      setMcpLogsTabs(prev => prev.map(t => t.tokId === tokId ? { ...t, error: e.message, loading: false } : t));
    }
  }

  async function handleViewLogs(tok) {
    const exists = mcpLogsTabs.find(t => t.tokId === tok.id);
    if (!exists) {
      setMcpLogsTabs(prev => [...prev, { tokId: tok.id, tokName: tok.name, logs: [], total: 0, loading: true, error: null, offset: 0 }]);
    }
    setMcpTab(tok.id);
    if (!exists) {
      await fetchMcpLogs(tok.id, tok.name, 0);
    }
  }

  function closeMcpLogsTab(tokId) {
    setMcpLogsTabs(prev => prev.filter(t => t.tokId !== tokId));
    setMcpTab(prev => prev === tokId ? 'tokens' : prev);
  }

  const bucketName = bucket?.name || seedBucket?.name || `Bucket ${bucketId?.slice(0, 8) || ''}`;
  const isDark = theme === 'dark';
  const bucketPageBg = isDark ? 'bg-[#020617] text-slate-100' : 'bg-[#f5f7fb] text-slate-900';
  const shell = isDark
    ? 'border-white/10 bg-[#020617] shadow-[0_20px_70px_rgba(0,0,0,0.55)]'
    : 'border-white/80 bg-white/78 backdrop-blur-xl shadow-[0_18px_55px_rgba(148,163,184,0.16)]';
  const subtle = isDark ? 'bg-white/[0.025]' : 'bg-slate-50/90';
  const line = isDark ? 'border-white/10' : 'border-slate-200';
  const muted = isDark ? 'text-white/55' : 'text-slate-500';
  const titleCls = isDark ? 'text-white' : 'text-slate-900';
  const bodyCls = isDark ? 'text-white/88' : 'text-slate-700';
  const modalHeaderFade = isDark
    ? 'bg-gradient-to-b from-[#020617] via-[#020617]/95 to-[#020617]/0'
    : 'bg-gradient-to-b from-white via-white/95 to-white/0';
  const modalFooterFade = isDark
    ? 'bg-gradient-to-t from-[#020617] via-[#020617]/95 to-[#020617]/0'
    : 'bg-gradient-to-t from-white via-white/95 to-white/0';
  const threadActive = isDark
    ? 'border-blue-400/55 bg-[#0e2660] shadow-[inset_0_0_0_1px_rgba(255,255,255,0.06)]'
    : 'border-blue-300 bg-blue-50';
  const threadIdle = isDark
    ? 'border-white/10 bg-[#020617] hover:bg-white/[0.04]'
    : 'border-transparent bg-transparent hover:bg-slate-100/90';
  const fileRowIdle = isDark
    ? 'border-white/10 bg-[#020617] hover:bg-white/[0.04]'
    : 'border-transparent bg-transparent hover:bg-slate-100/90';
  const fileRowActive = isDark
    ? 'border-blue-400/45 bg-[#0e2660]'
    : 'border-blue-300 bg-blue-50';
  const menuBg = isDark ? 'border-white/10 bg-[#020617] text-white' : 'border-slate-200 bg-white text-slate-900';
  const highlightedFileIds = new Set([...composerReferencedFileIds, ...inFlightReferencedFileIds]);

  return (
    <main className={`min-h-[100dvh] ${bucketPageBg}`}>
      <input ref={uploadRef} type="file" multiple className="hidden" onChange={handleFileSelect} />
      <input ref={directUploadRef} type="file" multiple className="hidden" onChange={handleDirectFileUpload} />
      <input ref={replaceRef} type="file" className="hidden" onChange={handleReplaceFileInput} />

      {error && (
        <div className="fixed left-1/2 top-4 z-50 -translate-x-1/2 rounded-xl border border-red-400/30 bg-red-500/10 px-5 py-3 text-sm text-red-400 shadow-xl backdrop-blur">
          {error}
          <button type="button" onClick={() => setError(null)} className="ml-4 font-semibold opacity-70 hover:opacity-100">✕</button>
        </div>
      )}

      <div className="mx-auto flex max-w-[1600px] gap-4 px-4 py-5 sm:px-6">

        {/* Left sidebar — threads */}
        {!leftCollapsed ? (
          <aside className={`flex h-[calc(100dvh-2.5rem)] w-[19rem] shrink-0 flex-col rounded-[1.35rem] border ${shell}`}>
            <div className="flex items-center justify-between px-4 py-4">
              <button type="button" onClick={() => navigate('/dashboard')} className={`flex items-center gap-2 text-sm font-medium ${bodyCls}`}>
                <ArrowLeftIcon />
                Dashboard
              </button>
              <button type="button" onClick={() => setLeftCollapsed(true)} className={`rounded-full p-2 ${muted} transition hover:bg-black/5`}>
                <ChevronLeftIcon />
              </button>
            </div>

            <div className="px-4 pb-3">
              <p className={`text-lg font-semibold ${titleCls}`}>{bucketName}</p>
              <p className={`mt-1 text-sm ${muted}`}>Conversation threads</p>
              <button
                type="button"
                onClick={handleCreateThread}
                disabled={threads.length >= 50 || loading}
                className={`mt-4 flex w-full items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition ${palette.primary} disabled:opacity-50`}
              >
                <PlusIcon />
                New Thread
              </button>
              {threads.length >= 50 && (
                <p className="mt-2 text-xs text-amber-400">Thread limit reached</p>
              )}
            </div>

            <div className="flex-1 overflow-y-auto px-3 pb-4">
              {loading ? (
                <div className="space-y-2">
                  {[1, 2, 3].map(i => (
                    <div key={i} className={`h-12 animate-pulse rounded-[0.9rem] border ${line} ${subtle}`} />
                  ))}
                </div>
              ) : threads.length === 0 ? (
                <p className={`px-2 py-4 text-sm ${muted}`}>No threads yet. Create one above.</p>
              ) : (
                <div className="space-y-1.5">
                  {threads.map((thread) => (
                    <div
                      key={thread.id}
                      onClick={() => handleSelectThread(thread.id)}
                      role="button"
                      tabIndex={0}
                      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleSelectThread(thread.id); } }}
                      className={`group relative w-full cursor-pointer rounded-[0.9rem] border px-2.5 py-1.5 text-left transition ${String(thread.id) === String(activeThreadId) ? threadActive : threadIdle}`}
                    >
                      <div className="flex items-center gap-2">
                        <span className={bodyCls}>
                          <img
                            src={threadChatIcon}
                            alt=""
                            aria-hidden="true"
                            className="h-[18px] w-[18px] opacity-90"
                            style={{ filter: isDark ? 'brightness(0) invert(1)' : 'none' }}
                          />
                        </span>
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            <p className={`truncate text-[14px] font-semibold ${titleCls}`}>
                              {thread.title}
                            </p>
                            <span className={`shrink-0 text-[11px] ${muted}`}>
                              {thread.updated_at ? fmtTime(thread.updated_at) : ''}
                            </span>
                          </div>
                        </div>
                        <div className="relative flex items-center gap-0.5">
                          <button
                            type="button"
                            title={thread.is_pinned ? 'Unpin chat' : 'Pin chat'}
                            onClick={(e) => { e.stopPropagation(); handleTogglePinThread(thread.id); }}
                            className={`flex h-7 w-7 items-center justify-center rounded-full transition ${thread.is_pinned ? (isDark ? 'text-white' : 'text-slate-900') : `${muted} opacity-0 group-hover:opacity-100`} hover:bg-black/5 ${thread.is_pinned ? 'opacity-100' : ''}`}
                          >
                            <PinIcon filled={thread.is_pinned} />
                          </button>
                          <button
                            type="button"
                            onClick={(e) => { e.stopPropagation(); setThreadMenuOpen(prev => String(prev) === String(thread.id) ? null : thread.id); }}
                            className={`flex h-7 w-7 items-center justify-center rounded-full opacity-0 transition group-hover:opacity-100 ${String(threadMenuOpen) === String(thread.id) ? 'opacity-100' : ''} ${muted} hover:bg-black/5`}
                          >
                            <MoreHorizontalIcon />
                          </button>
                          {String(threadMenuOpen) === String(thread.id) && (
                            <div className={`absolute right-0 top-9 z-20 min-w-[9rem] rounded-xl border p-1 shadow-lg ${menuBg}`} onClick={e => e.stopPropagation()}>
                              <button type="button" onClick={() => handleRenameThread(thread.id)} className={`block w-full rounded-lg px-3 py-2 text-left text-sm ${isDark ? 'hover:bg-white/8' : 'hover:bg-slate-50'}`}>Rename</button>
                              <button type="button" onClick={() => handleTogglePinThread(thread.id)} className={`block w-full rounded-lg px-3 py-2 text-left text-sm ${isDark ? 'hover:bg-white/8' : 'hover:bg-slate-50'}`}>{thread.is_pinned ? 'Unpin' : 'Pin'}</button>
                              <button type="button" onClick={() => handleDeleteThread(thread.id)} disabled={threads.length <= 1} className={`block w-full rounded-lg px-3 py-2 text-left text-sm ${threads.length <= 1 ? 'cursor-not-allowed opacity-40' : ''} ${isDark ? 'hover:bg-white/8 text-red-300' : 'hover:bg-slate-50 text-red-600'}`}>Delete</button>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </aside>
        ) : (
          <button type="button" onClick={() => setLeftCollapsed(false)} className={`flex h-[calc(100dvh-2.5rem)] w-12 shrink-0 items-start justify-center rounded-[1rem] border pt-4 ${shell} ${bodyCls}`}>
            <ChevronRightIcon />
          </button>
        )}

        {/* Center — chat */}
        <section className="flex h-[calc(100dvh-2.5rem)] min-w-0 flex-1 flex-col">
          <div className="flex-1 overflow-y-auto overflow-x-hidden px-5 py-5 pb-8 [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-black/10 hover:[&::-webkit-scrollbar-thumb]:bg-black/20">
            <div className="mx-auto flex min-h-full max-w-3xl flex-col">
              {loading || loadingMsgs ? (
                <div className="space-y-4">
                  {[1, 2, 3].map(i => (
                    <div key={i} className={`h-12 animate-pulse rounded-[1.2rem] ${i % 2 === 0 ? 'ml-auto w-2/3' : 'w-3/4'} ${subtle}`} />
                  ))}
                </div>
              ) : messages.length === 0 ? (
                <div className={`py-16 text-center text-sm ${muted}`}>
                  {threads.length === 0
                    ? 'Create a thread to start chatting with this bucket.'
                    : 'Send a message to start the conversation.'}
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`group relative flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      {msg.role === 'processing' ? (
                        <div className={`flex items-center gap-2.5 px-1 py-3 text-sm ${isDark ? 'text-white/60' : 'text-slate-500'}`}>
                          <svg className="h-4 w-4 shrink-0 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" strokeOpacity=".25"/><path d="M12 2a10 10 0 0 1 10 10"/></svg>
                          {msg.content}
                        </div>
                      ) : editingMsgId === msg.id ? (
                        /* ── inline editor ── */
                        <div className={`w-full max-w-[85%] rounded-[1.2rem] border px-3 py-3 ${isDark ? 'border-blue-500/60 bg-blue-600/20' : 'border-blue-400/60 bg-blue-50'}`}>
                          <textarea
                            ref={el => { if (el) { el.style.height = 'auto'; el.style.height = el.scrollHeight + 'px'; } }}
                            autoFocus
                            value={editingContent}
                            onChange={e => {
                              setEditingContent(e.target.value);
                              e.target.style.height = 'auto';
                              e.target.style.height = e.target.scrollHeight + 'px';
                            }}
                            onKeyDown={e => {
                              if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleEditSend(msg.id); }
                              if (e.key === 'Escape') { setEditingMsgId(null); setEditingContent(''); }
                            }}
                            className={`w-full resize-none overflow-hidden bg-transparent text-sm leading-7 outline-none break-words ${isDark ? 'text-white' : 'text-slate-900'}`}
                          />
                          <div className="mt-2 flex justify-end gap-2">
                            <button
                              type="button"
                              onClick={() => { setEditingMsgId(null); setEditingContent(''); }}
                              className={`rounded-lg px-3 py-1 text-xs font-medium transition ${isDark ? 'bg-white/10 text-white/70 hover:bg-white/20' : 'bg-black/8 text-slate-600 hover:bg-black/15'}`}
                            >
                              Cancel
                            </button>
                            <button
                              type="button"
                              disabled={!editingContent.trim() || sending}
                              onClick={() => handleEditSend(msg.id)}
                              className="rounded-lg bg-blue-600 px-3 py-1 text-xs font-semibold text-white transition hover:bg-blue-500 disabled:opacity-50"
                            >
                              Send
                            </button>
                          </div>
                        </div>
                      ) : (
                        <>
                          {msg.role === 'assistant' ? (() => {
                            const { text, sources } = parseAssistantContent(msg.content);
                            const isOpen = expandedSourceMsgId === msg.id;
                            return (
                              <div className={`w-full max-w-[85%] text-[15px] leading-8 ${bodyCls}`}>
                                {renderAssistantMessage(text, {
                                  onCopy: copyToClipboard,
                                  copiedKey: copiedId,
                                  copyKeyPrefix: `assistant-${msg.id}`,
                                  isDark,
                                })}
                                <SearchingGroup
                                  steps={msg.agent_steps || msg.thinking_step_events || []}
                                  plan={msg.agent_plan || []}
                                  isDark={isDark}
                                />
                                {sources.length > 0 && (
                                  <div className="mt-3">
                                    {/* Toggle row */}
                                    <button
                                      type="button"
                                      onClick={() => setExpandedSourceMsgId(isOpen ? null : msg.id)}
                                      className={`flex items-center gap-1.5 text-xs font-medium transition ${muted} hover:opacity-80`}
                                    >
                                      <svg viewBox="0 0 24 24" className={`h-3 w-3 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="m6 9 6 6 6-6"/></svg>
                                      {sources.length} source{sources.length > 1 ? 's' : ''}
                                    </button>
                                    {/* Chips — visible when open */}
                                    {isOpen && (
                                      <div className="mt-2 flex flex-wrap gap-1.5">
                                        {sources.map((s, i) => {
                                          const domain = s.kind === 'web' ? (() => { try { return new URL(s.url).hostname; } catch { return s.label; } })() : null;
                                          const iconCls = "h-3.5 w-3.5 shrink-0";
                                          if (s.kind === 'web') {
                                            return (
                                              <a key={i} href={s.url} target="_blank" rel="noopener noreferrer"
                                                className={`flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs transition hover:bg-black/5 ${line} ${bodyCls}`}>
                                                <img src={`https://www.google.com/s2/favicons?domain=${domain}&sz=16`} alt="" className="h-3.5 w-3.5 rounded-sm" onError={e => { e.target.style.display='none'; }} />
                                                <span>{domain}</span>
                                              </a>
                                            );
                                          }
                                          if (s.kind === 'memory') {
                                            return (
                                              <span key={i} className={`flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs ${line} ${muted}`}>
                                                <svg className={iconCls} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                                                <span>{s.label}</span>
                                              </span>
                                            );
                                          }
                                          if (s.kind === 'general') {
                                            return (
                                              <span key={i} className={`flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs ${line} ${muted}`}>
                                                <svg className={iconCls} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2a4 4 0 0 0-4 4 4 4 0 0 0-2 7.5A4 4 0 0 0 9 21a3 3 0 0 0 3-3 3 3 0 0 0 3 3 4 4 0 0 0 3-7.5A4 4 0 0 0 16 6a4 4 0 0 0-4-4z"/></svg>
                                                <span>{s.label}</span>
                                              </span>
                                            );
                                          }
                                          const sourceText = s.fileName
                                            ? `${s.fileName}${s.page ? ` — Page ${s.page}` : s.isOverview ? ' — Overview' : ''}`
                                            : s.label;
                                          const sourceCopyKey = `source-${msg.id}-${i}`;
                                          return (
                                            <div key={i} className={`flex max-w-full items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs ${line} ${muted}`}>
                                              <svg className={iconCls} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                                              <span className="min-w-0 max-w-[16rem] truncate">{sourceText}</span>
                                              <button
                                                type="button"
                                                title={copiedId === sourceCopyKey ? 'Copied' : 'Copy source'}
                                                onClick={() => copyToClipboard(sourceText, sourceCopyKey)}
                                                className={`ml-0.5 rounded-full p-0.5 transition ${isDark ? 'hover:bg-white/10' : 'hover:bg-black/8'} ${copiedId === sourceCopyKey ? 'text-green-500' : ''}`}
                                              >
                                                <CopyIcon />
                                              </button>
                                              {s.page && (
                                                <button
                                                  type="button"
                                                  title="Pinpoint cited page"
                                                  onClick={() => setSourcePinpoint(s)}
                                                  className={`rounded-full px-1.5 py-0.5 text-[10px] font-semibold transition ${isDark ? 'bg-blue-500/15 text-blue-300 hover:bg-blue-500/25' : 'bg-blue-50 text-blue-700 hover:bg-blue-100'}`}
                                                >
                                                  Pinpoint
                                                </button>
                                              )}
                                            </div>
                                          );
                                        })}
                                      </div>
                                    )}
                                  </div>
                                )}
                              </div>
                            );
                          })() : (() => {
                            const senderStyle = bubbleStyleForSender(msg.sender);
                            return (
                              <div className="flex max-w-[85%] flex-col items-end">
                                <SenderBadge sender={msg.sender} align="right" />
                                <div
                                  style={senderStyle || undefined}
                                  className={`w-fit max-w-full break-words rounded-[1.05rem] px-3.5 py-2 text-[15px] leading-7 shadow-none ${
                                    senderStyle ? '' : 'bg-blue-600 text-white'
                                  }`}
                                >
                                  {renderUserMessage(msg.content)}
                                </div>
                              </div>
                            );
                          })()}
                          <div className={`absolute -bottom-6 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity ${msg.role === 'user' ? 'right-0' : 'left-0'}`}>
                            {msg.role === 'user' && (
                              <button type="button" title="Edit message" onClick={() => { setEditingMsgId(msg.id); setEditingContent(msg.content); }} className={`flex h-5 w-5 items-center justify-center rounded-full ${isDark ? 'bg-white/10 text-white/60 hover:bg-white/20 hover:text-white' : 'bg-black/8 text-slate-500 hover:bg-black/15 hover:text-slate-800'} transition`}>
                                <PencilIcon />
                              </button>
                            )}
                            {msg.role === 'assistant' && (
                              <>
                                <button type="button" title="Like" onClick={() => setMsgFeedback(f => f?.msgId === msg.id && f.type === 'like' ? null : { msgId: msg.id, type: 'like', reason: '', submitted: false })}
                                  className={`flex h-5 w-5 items-center justify-center rounded-full transition ${msgFeedback?.msgId === msg.id && msgFeedback.type === 'like' ? 'text-green-500' : isDark ? 'bg-white/10 text-white/60 hover:bg-white/20 hover:text-white' : 'bg-black/8 text-slate-500 hover:bg-black/15 hover:text-slate-800'}`}>
                                  <ThumbsUpIcon />
                                </button>
                                <button type="button" title="Dislike" onClick={() => setMsgFeedback(f => f?.msgId === msg.id && f.type === 'dislike' ? null : { msgId: msg.id, type: 'dislike', reason: '', submitted: false })}
                                  className={`flex h-5 w-5 items-center justify-center rounded-full transition ${msgFeedback?.msgId === msg.id && msgFeedback.type === 'dislike' ? 'text-red-400' : isDark ? 'bg-white/10 text-white/60 hover:bg-white/20 hover:text-white' : 'bg-black/8 text-slate-500 hover:bg-black/15 hover:text-slate-800'}`}>
                                  <ThumbsDownIcon />
                                </button>
                              </>
                            )}
                            <button type="button" title={copiedId === msg.id ? 'Copied!' : 'Copy'} onClick={() => copyToClipboard(msg.content, msg.id)} className={`flex h-5 w-5 items-center justify-center rounded-full ${isDark ? 'bg-white/10 text-white/60 hover:bg-white/20 hover:text-white' : 'bg-black/8 text-slate-500 hover:bg-black/15 hover:text-slate-800'} transition ${copiedId === msg.id ? '!text-green-500' : ''}`}>
                              <CopyIcon />
                            </button>
                          </div>
                          {/* Feedback bubble */}
                          {msgFeedback?.msgId === msg.id && !msgFeedback.submitted && (
                            <div className={`absolute left-0 mt-2 w-72 rounded-2xl border p-3 shadow-lg z-10 ${isDark ? 'border-white/10 bg-[#1e2535]' : 'border-slate-200 bg-white'}`} style={{ top: 'calc(100% + 1.5rem)' }}>
                              <p className={`mb-2 text-xs font-semibold ${titleCls}`}>
                                {msgFeedback.type === 'like' ? 'Why did you like this?' : 'Why did you dislike this?'}
                              </p>
                              <div className="flex flex-wrap gap-1.5 mb-2">
                                {(msgFeedback.type === 'like'
                                  ? ['Helpful', 'Accurate', 'Well written', 'Creative']
                                  : ['Not helpful', 'Inaccurate', 'Too long', 'Too short', 'Missing info']
                                ).map(opt => (
                                  <button key={opt} type="button"
                                    onClick={() => setMsgFeedback(f => ({ ...f, reason: f.reason === opt ? '' : opt }))}
                                    className={`rounded-full border px-2.5 py-0.5 text-xs transition ${msgFeedback.reason === opt ? 'border-blue-500 bg-blue-500/10 text-blue-500' : `${line} ${muted} hover:border-blue-400`}`}>
                                    {opt}
                                  </button>
                                ))}
                              </div>
                              <textarea
                                value={msgFeedback.reason && !['Helpful','Accurate','Well written','Creative','Not helpful','Inaccurate','Too long','Too short','Missing info'].includes(msgFeedback.reason) ? msgFeedback.reason : ''}
                                onChange={e => setMsgFeedback(f => ({ ...f, reason: e.target.value }))}
                                placeholder="Add a comment (optional)…"
                                rows={2}
                                className={`w-full resize-none rounded-xl border px-3 py-2 text-xs outline-none ${line} ${isDark ? 'bg-white/5 text-white placeholder:text-white/30' : 'bg-slate-50 text-slate-800 placeholder:text-slate-400'}`}
                              />
                              <div className="mt-2 flex justify-end gap-2">
                                <button type="button" onClick={() => setMsgFeedback(null)} className={`rounded-lg px-3 py-1 text-xs ${muted} transition hover:opacity-80`}>Cancel</button>
                                <button type="button" onClick={async () => {
                                    try {
                                      await bucketApi.submitFeedback(
                                        bucketId,
                                        activeThreadId,
                                        msgFeedback.msgId,
                                        msgFeedback.type === 'like' ? 'like' : 'dislike',
                                        msgFeedback.reason || null,
                                      );
                                    } catch (_) {}
                                    setMsgFeedback(f => ({ ...f, submitted: true }));
                                  }}
                                  className="rounded-lg bg-blue-600 px-3 py-1 text-xs font-semibold text-white transition hover:bg-blue-500">
                                  Submit
                                </button>
                              </div>
                            </div>
                          )}
                          {msgFeedback?.msgId === msg.id && msgFeedback.submitted && (
                            <div className={`absolute left-0 mt-2 rounded-2xl border px-4 py-2.5 text-xs font-medium shadow-md z-10 ${isDark ? 'border-white/10 bg-[#1e2535] text-white/70' : 'border-slate-200 bg-white text-slate-600'}`} style={{ top: 'calc(100% + 1.5rem)' }}>
                              Thanks for your feedback!
                              <button type="button" onClick={() => setMsgFeedback(null)} className="ml-3 opacity-50 hover:opacity-100">✕</button>
                            </div>
                          )}
                        </>
                      )}
                    </div>
                  ))}
                  {sending && !messages.some(m => m.role === 'processing') && (
                    <div className="flex w-full max-w-[85%] justify-start">
                      <AgentWorkPanel
                        steps={liveStepEvents}
                        currentStep={currentStep}
                        plan={livePlan}
                        isDark={isDark}
                      />
                    </div>
                  )}
                  {/* Action buttons — shown when agent needs user permission */}
                  {pendingAction && !sending && (
                    <div className="flex justify-start">
                      <div className={`rounded-[1.2rem] border px-4 py-3 ${subtle} ${line}`}>
                        <div className="flex flex-wrap gap-2">
                          {pendingAction.options.map((opt) => (
                            <button
                              key={opt}
                              type="button"
                              onClick={async () => {
                                const isAllow = opt.toLowerCase().includes('allow') || opt.toLowerCase().includes('save') || opt.toLowerCase().includes('yes');
                                setPendingAction(null);
                                if (!isAllow) return;

                                if (pendingAction.action_type === 'web_search_permission') {
                                  // Re-send with explicit web search instruction
                                  const webQuery = pendingAction.originalQuestion + ' — please search online';
                                  setSending(true);
                                  try {
                                    const result = await bucketApi.sendMessage(pendingAction.bucketId, pendingAction.convId, webQuery);
                                    setMessages(prev => [...prev, result.user_message, { ...result.assistant_message, content: '' }]);
                                    typewriteAssistantMessage(result.assistant_message);
                                  } catch (e) { setError(e.message); }
                                  finally { setSending(false); }
                                } else if (pendingAction.action_type === 'save_file') {
                                  // Find the assistant message content and save it
                                  const assistantMsg = messages.find(m => String(m.id) === String(pendingAction.messageId));
                                  if (assistantMsg) {
                                    try {
                                      const fileName = (pendingAction.originalQuestion.slice(0, 40).replace(/[^a-zA-Z0-9\s]/g, '').trim().replace(/\s+/g, '_') || 'agent_note') + '.md';
                                      await bucketApi.saveMessageAsFile(pendingAction.bucketId, pendingAction.convId, pendingAction.messageId, fileName, assistantMsg.content);
                                      const updatedFiles = await bucketApi.listFiles(pendingAction.bucketId);
                                      setFilesPanel(updatedFiles.files || []);
                                    } catch (e) { setError(e.message); }
                                  }
                                }
                              }}
                              className={`rounded-full border px-3 py-1.5 text-xs font-medium transition ${
                                opt.toLowerCase().includes('allow') || opt.toLowerCase().includes('save') || opt.toLowerCase().includes('yes')
                                  ? 'border-blue-500 bg-blue-500/10 text-blue-500 hover:bg-blue-500/20'
                                  : `${line} ${muted} hover:opacity-80`
                              }`}
                            >
                              {opt}
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={msgsEndRef} />
                </div>
              )}
            </div>
          </div>

          <div className="px-4 pb-4 pt-1">
            <div className={`mx-auto max-w-3xl overflow-hidden rounded-[1.25rem] border ${subtle} ${line}`}>
              {/* Pending upload chips */}
              {pendingFiles.length > 0 && (
                <div className="flex flex-wrap gap-1.5 px-4 pt-3">
                  {pendingFiles.map((file, i) => (
                    <span key={i} className={`flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium ${line} ${bodyCls}`}>
                      <AttachmentIcon />
                      <span className="max-w-[120px] truncate">{file.name}</span>
                      <button type="button" onClick={() => setPendingFiles(prev => prev.filter((_, j) => j !== i))} className="ml-0.5 opacity-60 hover:opacity-100">
                        <CloseIcon />
                      </button>
                    </span>
                  ))}
                </div>
              )}
              {/* Textarea — always visible (shows live transcript while recording) */}
              <textarea
                ref={composerRef}
                rows={1}
                value={composer}
                onChange={(e) => setComposer(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
                placeholder={isRecording ? 'Listening…' : (activeThreadId ? 'Message…' : 'Select or create a thread first')}
                disabled={!activeThreadId}
                className={`w-full max-h-[200px] resize-none bg-transparent px-4 pt-3 pb-1 text-sm leading-6 outline-none ${titleCls} disabled:opacity-40`}
              />
              {/* Recording — full-width volume-reactive bars (ChatGPT-style) */}
              {isRecording && (
                <div className="flex items-center justify-center gap-[3px] w-full px-4 pt-4 pb-3 h-14">
                  {barLevels.map((lvl, i) => (
                    <span
                      key={i}
                      className={`flex-1 rounded-full transition-[height] duration-75 ease-out ${isDark ? 'bg-slate-200' : 'bg-blue-500'}`}
                      style={{
                        height: `${Math.max(8, lvl * 100)}%`,
                        minWidth: '2px',
                        maxWidth: '6px',
                        opacity: 0.55 + lvl * 0.45,
                      }}
                    />
                  ))}
                </div>
              )}
              {/* Bottom toolbar row */}
              <div className="flex items-center justify-between px-3 pb-2 pt-1">
                <div className="flex items-center gap-1">
                  <button
                    type="button"
                    onClick={() => uploadRef.current?.click()}
                    title="Attach file"
                    className={`flex h-7 w-7 items-center justify-center rounded-full transition ${muted} hover:bg-black/8`}
                  >
                    <AttachmentIcon />
                  </button>
                  <button
                    type="button"
                    onClick={() => { setWebSearchEnabled(v => !v); setWebOffHint(0); }}
                    title={webSearchEnabled ? 'Web search ON — click to disable' : 'Web search OFF — click to enable'}
                    className={`flex h-7 items-center gap-1 rounded-full px-2 text-xs font-medium transition ${
                      webSearchEnabled
                        ? (isDark ? 'bg-blue-500/20 text-blue-300 ring-1 ring-blue-400/40' : 'bg-blue-100 text-blue-700 ring-1 ring-blue-400/50')
                        : (webOffHint
                          ? 'bg-amber-500/15 text-amber-400 ring-1 ring-amber-500/60 animate-pulse'
                          : `${muted} hover:bg-black/8`)
                    }`}
                  >
                    <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
                    {webSearchEnabled && <span>Web</span>}
                  </button>
                  <button
                    type="button"
                    onClick={openScopeModal}
                    disabled={!activeThreadId}
                    title={threadScope ? `Filtered: ${threadScope.length} file(s)` : 'Filter files for this thread'}
                    className={`flex h-7 items-center gap-1 rounded-full px-2 text-xs font-medium transition disabled:opacity-40 ${
                      threadScope
                        ? (isDark ? 'bg-blue-500/20 text-blue-300 ring-1 ring-blue-400/40' : 'bg-blue-100 text-blue-700 ring-1 ring-blue-400/50')
                        : `${muted} hover:bg-black/8`
                    }`}
                  >
                    <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
                    </svg>
                    {threadScope && <span>{threadScope.length}</span>}
                  </button>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    type="button"
                    onClick={toggleRecording}
                    disabled={!activeThreadId}
                    title={isRecording ? 'Stop recording' : 'Voice input'}
                    className={`flex h-8 w-8 items-center justify-center rounded-full transition disabled:opacity-40 ${
                      isRecording
                        ? (isDark ? 'bg-slate-200 text-slate-900 animate-pulse' : 'bg-blue-500 text-white animate-pulse')
                        : `${muted} hover:bg-black/8`
                    }`}
                  >
                    <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <rect x="9" y="2" width="6" height="12" rx="3"/>
                      <path d="M5 11a7 7 0 0 0 14 0"/>
                      <line x1="12" y1="18" x2="12" y2="22"/>
                      <line x1="8" y1="22" x2="16" y2="22"/>
                    </svg>
                  </button>
                  <button
                    type="button"
                    onClick={sending ? handleStop : handleSend}
                    disabled={!activeThreadId || (!sending && !composer.trim() && !pendingFiles.length)}
                    className={`flex h-8 w-8 items-center justify-center rounded-full transition disabled:opacity-40 ${sending ? 'bg-red-500 text-white hover:bg-red-400' : palette.primary}`}
                  >
                    {sending ? <StopIcon /> : <SendIcon />}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Right sidebar — files */}
        {!rightCollapsed ? (
          <aside className={`flex h-[calc(100dvh-2.5rem)] w-[19rem] shrink-0 flex-col rounded-[1.35rem] border ${isDark ? 'border-white/10 bg-[#020617]' : 'border-white/80'} overflow-hidden`}>
            <div className="flex items-center justify-between px-4 py-4 bg-transparent">
              <div>
                <p className={`text-base font-semibold ${titleCls}`}>Files</p>
                <p className={`mt-0.5 text-sm ${muted}`}>{filesPanel.length} uploaded</p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => directUploadRef.current?.click()}
                  disabled={directUploading}
                  title="Upload directly to bucket"
                  className={`rounded-full p-2 transition disabled:opacity-50 ${isDark ? 'text-emerald-400 hover:bg-emerald-500/10' : 'text-emerald-600 hover:bg-emerald-50'}`}
                >
                  {directUploading ? (
                    <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" strokeOpacity=".25"/><path d="M12 2a10 10 0 0 1 10 10"/></svg>
                  ) : (
                    <PlusIcon />
                  )}
                </button>
                <button
                  type="button"
                  onClick={openMcpModal}
                  title="MCP Access Tokens"
                  className={`rounded-full p-2 transition hover:bg-black/5 ${isDark ? 'text-blue-400 hover:bg-blue-500/10' : 'text-blue-600 hover:bg-blue-50'}`}
                >
                  <svg viewBox="0 0 24 24" className="h-4 w-4 fill-current" aria-hidden="true"><path d="M15.688 2.343a2.588 2.588 0 0 0-3.61 0l-9.626 9.44a.863.863 0 0 1-1.203 0 .823.823 0 0 1 0-1.18l9.626-9.44a4.313 4.313 0 0 1 6.016 0 4.116 4.116 0 0 1 1.204 3.54 4.3 4.3 0 0 1 3.609 1.18l.05.05a4.115 4.115 0 0 1 0 5.9l-8.706 8.537a.274.274 0 0 0 0 .393l1.788 1.754a.823.823 0 0 1 0 1.18.863.863 0 0 1-1.203 0l-1.788-1.753a1.92 1.92 0 0 1 0-2.754l8.706-8.538a2.47 2.47 0 0 0 0-3.54l-.05-.049a2.588 2.588 0 0 0-3.607-.003l-7.172 7.034-.002.002-.098.097a.863.863 0 0 1-1.204 0 .823.823 0 0 1 0-1.18l7.273-7.133a2.47 2.47 0 0 0-.003-3.537Z"/></svg>
                </button>
                <button type="button" onClick={() => setRightCollapsed(true)} className={`rounded-full p-2 ${muted} transition hover:bg-black/5`}>
                  <ChevronRightIcon />
                </button>
              </div>
            </div>

            <div className={`flex-1 overflow-y-auto px-3 pb-4 pt-2 ${shell}`}>
              {loading ? (
                <div className="space-y-2">
                  {[1, 2, 3].map(i => <div key={i} className={`h-12 animate-pulse rounded-[0.9rem] border ${line} ${subtle}`} />)}
                </div>
              ) : filesPanel.length === 0 ? (
                <div className="px-2 py-6 text-center">
                  <p className={`text-sm ${muted}`}>No files yet.</p>
                  <button
                    type="button"
                    onClick={() => directUploadRef.current?.click()}
                    disabled={directUploading}
                    className={`mt-3 text-sm font-semibold disabled:opacity-50 ${isDark ? 'text-blue-400' : 'text-blue-600'}`}
                  >
                    {directUploading ? 'Uploading...' : 'Upload a file'}
                  </button>
                </div>
              ) : (
                <div className="space-y-1.5">
                  {filesPanel.map((file) => {
                    const fidStr = String(file.id);
                    const inScope = threadScope ? threadScope.includes(fidStr) : false;
                    const outOfScope = threadScope ? !inScope : false;
                    const scopeRing = inScope
                      ? (isDark ? 'ring-2 ring-blue-400/60 bg-blue-500/10' : 'ring-2 ring-blue-500 bg-blue-50')
                      : '';
                    const scopeDim = outOfScope ? 'opacity-50' : '';
                    return (
                    <div key={file.id}
                      className={`group cursor-pointer rounded-[0.9rem] border px-2.5 py-2 transition active:scale-[0.98] ${highlightedFileIds.has(String(file.id)) ? fileRowActive : fileRowIdle} ${scopeRing} ${scopeDim}`}
                      onClick={() => handleReferenceFile(file)}
                      title={inScope ? 'In this thread’s scope' : (outOfScope ? 'Not in this thread’s scope' : 'Click to reference in message')}
                    >
                      <div className="flex items-start gap-2.5">
                        <span className={`mt-0.5 ${bodyCls}`}><FileStackIcon /></span>
                        <div className="min-w-0 flex-1">
                          <p className={`truncate text-[13px] font-semibold ${titleCls}`}>{file.name}</p>
                          <p className={`mt-0.5 text-xs ${muted}`}>
                            {fmtMimeType(file.type, file.name)} · {fmtFileSize(file.size)}
                            {file.status && file.status !== 'ready' && (
                              <span className={`ml-2 rounded-full px-1.5 py-0.5 text-[10px] font-medium ${file.status === 'processing' ? 'bg-yellow-400/15 text-yellow-500' : file.status === 'failed' ? 'bg-red-400/15 text-red-400' : 'bg-green-400/15 text-green-500'}`}>
                                {file.status}
                              </span>
                            )}
                          </p>
                        </div>
                        <button
                          type="button"
                          onClick={(event) => handleDownloadFile(file, event)}
                          className={`shrink-0 rounded-full p-1 opacity-0 transition group-hover:opacity-100 ${isDark ? 'hover:bg-white/10 text-zinc-300' : 'hover:bg-black/5 text-zinc-600'}`}
                          title="Download original file"
                        >
                          <svg viewBox="0 0 16 16" className="h-3.5 w-3.5 fill-current" aria-hidden="true"><path d="M8 1.5a.75.75 0 0 1 .75.75v6.19l2.22-2.22a.75.75 0 1 1 1.06 1.06l-3.5 3.5a.75.75 0 0 1-1.06 0l-3.5-3.5a.75.75 0 1 1 1.06-1.06l2.22 2.22V2.25A.75.75 0 0 1 8 1.5ZM3.25 11a.75.75 0 0 0 0 1.5h9.5a.75.75 0 0 0 0-1.5h-9.5Z" /></svg>
                        </button>
                        <button
                          type="button"
                          onClick={(event) => { event.stopPropagation(); handleReplaceFile(file.id); }}
                          className={`shrink-0 rounded-full p-1 opacity-0 transition group-hover:opacity-100 ${isDark ? 'hover:bg-blue-500/15 text-blue-400' : 'hover:bg-blue-50 text-blue-500'}`}
                          title="Replace file"
                        >
                          <svg viewBox="0 0 16 16" className="h-3.5 w-3.5 fill-current"><path d="M2 8a6 6 0 1 1 6 6v-1.5a4.5 4.5 0 1 0-4.5-4.5H5L2.5 10.5 0 8h2ZM9 4v4.5l3 1.5-.7 1.4L8 9.5V4h1Z" /></svg>
                        </button>
                        <button
                          type="button"
                          onClick={(event) => { event.stopPropagation(); handleDeleteFile(file.id); }}
                          className={`shrink-0 rounded-full p-1 opacity-0 transition group-hover:opacity-100 ${isDark ? 'hover:bg-red-500/15 text-red-400' : 'hover:bg-red-50 text-red-500'}`}
                          title="Delete file"
                        >
                          <svg viewBox="0 0 16 16" className="h-3.5 w-3.5 fill-current"><path d="M6 2h4a1 1 0 0 1 1 1H5a1 1 0 0 1 1-1ZM2 4h12v1H3.5l.9 9h7.2l.9-9H14v-1H2v1Zm4 3h1l.3 5H6.3L6 7Zm3 0h1l-.3 5H8.7L9 7Z" /></svg>
                        </button>
                      </div>
                    </div>
                    );
                  })}
                </div>
              )}
            </div>
          </aside>
        ) : (
          <button type="button" onClick={() => setRightCollapsed(false)} className={`flex h-[calc(100dvh-2.5rem)] w-12 shrink-0 items-start justify-center rounded-[1rem] border pt-4 ${shell} ${bodyCls}`}>
            <ChevronLeftIcon />
          </button>
        )}
      </div>

      {/* Cited page pinpoint */}
      {sourcePinpoint && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={() => setSourcePinpoint(null)}>
          <div className={`absolute inset-0 ${isDark ? 'bg-black/65' : 'bg-slate-900/35'} backdrop-blur-sm`} />
          <div
            className={`relative z-10 grid w-full max-w-3xl overflow-hidden rounded-2xl border shadow-2xl md:grid-cols-[0.95fr_1.05fr] ${isDark ? 'border-white/10 bg-slate-950 text-white' : 'border-slate-200 bg-white text-slate-950'}`}
            onClick={e => e.stopPropagation()}
          >
            <div className={`flex min-h-[22rem] items-center justify-center border-b p-6 md:border-b-0 md:border-r ${isDark ? 'border-white/10 bg-slate-900' : 'border-slate-200 bg-slate-50'}`}>
              <div className={`relative aspect-[0.72] w-52 rounded-lg border shadow-sm ${isDark ? 'border-white/15 bg-slate-800' : 'border-slate-300 bg-white'}`}>
                <div className={`absolute left-5 right-5 top-7 h-2 rounded ${isDark ? 'bg-white/25' : 'bg-slate-300'}`} />
                <div className={`absolute left-5 right-12 top-12 h-2 rounded ${isDark ? 'bg-white/15' : 'bg-slate-200'}`} />
                <div className={`absolute left-5 right-8 top-20 h-16 rounded border ${isDark ? 'border-white/10 bg-white/5' : 'border-slate-200 bg-slate-50'}`} />
                <div className={`absolute left-5 right-5 top-40 space-y-2`}>
                  {[0, 1, 2, 3].map(i => (
                    <div key={i} className={`h-2 rounded ${isDark ? 'bg-white/12' : 'bg-slate-200'}`} style={{ width: `${92 - i * 9}%` }} />
                  ))}
                </div>
                <div className="absolute left-1/2 top-[44%] h-20 w-24 -translate-x-1/2 -translate-y-1/2 rounded-xl border-2 border-blue-500 bg-blue-500/10 shadow-[0_0_0_6px_rgba(59,130,246,0.12)]" />
                <div className="absolute left-1/2 top-[44%] h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-blue-500 ring-4 ring-blue-500/25" />
                <svg className="absolute left-[calc(50%+0.5rem)] top-[calc(44%-3.25rem)] h-16 w-20 text-blue-500" viewBox="0 0 80 64" fill="none" aria-hidden="true">
                  <path d="M6 56 C30 54 42 38 47 8" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeDasharray="6 6" />
                  <path d="M39 15 L48 6 L57 16" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                <span className="absolute bottom-3 right-3 rounded-full bg-blue-600 px-2 py-0.5 text-[10px] font-semibold text-white">
                  p.{sourcePinpoint.page}
                </span>
              </div>
            </div>
            <div className="p-5">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <p className={`text-xs font-semibold uppercase ${muted}`}>Cited page</p>
                  <h3 className={`mt-1 truncate text-lg font-semibold ${titleCls}`}>
                    {sourcePinpoint.fileName || sourcePinpoint.label}
                  </h3>
                  <p className={`mt-1 text-sm ${muted}`}>Page {sourcePinpoint.page}</p>
                </div>
                <button
                  type="button"
                  onClick={() => setSourcePinpoint(null)}
                  className={`rounded-full p-2 transition ${muted} ${isDark ? 'hover:bg-white/10' : 'hover:bg-black/5'}`}
                  title="Close"
                >
                  <CloseIcon />
                </button>
              </div>
              <div className={`mt-5 rounded-xl border p-4 ${line} ${subtle}`}>
                <p className={`text-sm font-medium ${titleCls}`}>{sourcePinpoint.label}</p>
                <p className={`mt-2 text-xs leading-5 ${muted}`}>
                  Page-level pinpoint from the answer citation. Exact box-level highlighting needs bounding-box data from the backend.
                </p>
              </div>
              <div className="mt-5 flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => copyToClipboard(`${sourcePinpoint.fileName || sourcePinpoint.label} — Page ${sourcePinpoint.page}`, 'pinpoint-copy')}
                  className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition ${line} ${bodyCls} ${isDark ? 'hover:bg-white/10' : 'hover:bg-slate-50'}`}
                >
                  <CopyIcon />
                  {copiedId === 'pinpoint-copy' ? 'Copied' : 'Copy reference'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setComposer(prev => `${prev}${prev ? ' ' : ''}Show me more detail on ${sourcePinpoint.fileName || sourcePinpoint.label} page ${sourcePinpoint.page}.`);
                    setSourcePinpoint(null);
                    setTimeout(() => composerRef.current?.focus(), 0);
                  }}
                  className={`rounded-full px-3 py-1.5 text-xs font-semibold text-white transition ${isDark ? 'bg-blue-500 hover:bg-blue-400' : 'bg-blue-600 hover:bg-blue-500'}`}
                >
                  Ask about this page
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Out-of-scope mention prompt */}
      {scopeRequest && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={() => setScopeRequest(null)}>
          <div className={`absolute inset-0 ${isDark ? 'bg-black/60' : 'bg-slate-900/40'} backdrop-blur-sm`} />
          <div
            className={`relative z-10 flex flex-col w-[26rem] rounded-2xl shadow-2xl overflow-hidden ${isDark ? 'bg-slate-900 text-slate-100' : 'bg-white text-slate-900'}`}
            onClick={e => e.stopPropagation()}
          >
            <div className="px-5 py-4">
              <p className="text-base font-semibold">File not in this thread</p>
              <p className={`mt-1 text-sm ${muted}`}>
                {scopeRequest.files.length === 1
                  ? 'This file isn’t in this thread’s scope. Add it to continue?'
                  : `These ${scopeRequest.files.length} files aren’t in this thread’s scope. Add them to continue?`}
              </p>
              <ul className={`mt-3 space-y-1 max-h-40 overflow-y-auto rounded-lg p-2 text-sm ${isDark ? 'bg-slate-800' : 'bg-slate-100'}`}>
                {scopeRequest.files.map(f => (
                  <li key={f.id} className="flex items-center gap-2 truncate">
                    <svg className="h-3.5 w-3.5 shrink-0 opacity-70" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                    <span className="truncate">{f.name}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className={`flex items-center justify-end gap-2 px-5 py-3 border-t ${isDark ? 'border-slate-800' : 'border-slate-200'}`}>
              <button
                type="button"
                onClick={() => setScopeRequest(null)}
                className={`rounded-lg px-3 py-1.5 text-sm font-medium ${isDark ? 'bg-slate-800 hover:bg-slate-700' : 'bg-slate-100 hover:bg-slate-200'}`}
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={scopeRequest.onConfirm}
                className={`rounded-lg px-4 py-1.5 text-sm font-semibold text-white transition ${isDark ? 'bg-blue-500 hover:bg-blue-400' : 'bg-blue-600 hover:bg-blue-500'}`}
              >
                Add &amp; send
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Thread file-scope modal */}
      {scopeModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={() => setScopeModalOpen(false)}>
          <div className={`absolute inset-0 ${isDark ? 'bg-black/60' : 'bg-slate-900/40'} backdrop-blur-sm`} />
          <div
            className={`relative z-10 flex flex-col w-[32rem] h-[32rem] rounded-2xl shadow-2xl overflow-hidden ${isDark ? 'bg-slate-900 text-slate-100' : 'bg-white text-slate-900'}`}
            onClick={e => e.stopPropagation()}
          >
            <div className="flex items-center justify-between px-5 pt-4 pb-3">
              <div>
                <p className="text-base font-semibold">Thread file access</p>
                <p className={`mt-0.5 text-xs ${muted}`}>All files are visible by default. Turn off the eye to hide a file from this thread.</p>
              </div>
              <button type="button" onClick={() => setScopeModalOpen(false)} className={`rounded-full p-1.5 ${muted} hover:bg-black/5`}>
                <CloseIcon />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto px-3 py-2">
              {filesPanel.length === 0 ? (
                <p className={`px-3 py-6 text-sm ${muted}`}>No files in this bucket yet.</p>
              ) : (
                <ul className="space-y-1">
                  {filesPanel.map(f => {
                    const fid = String(f.id);
                    const visible = scopeDraft.includes(fid);
                    return (
                      <li key={fid}>
                        <div className={`flex items-center gap-3 rounded-lg px-3 py-2 transition ${isDark ? 'hover:bg-slate-800' : 'hover:bg-slate-100'}`}>
                          <span className={`flex-1 truncate text-sm ${visible ? '' : muted}`}>{f.name}</span>
                          <button
                            type="button"
                            aria-pressed={visible}
                            title={visible ? 'Visible to this thread' : 'Hidden from this thread'}
                            onClick={() => {
                              setScopeDraft(prev =>
                                visible ? prev.filter(x => x !== fid) : [...prev, fid]
                              );
                            }}
                            className={`rounded-lg p-1.5 transition ${visible
                              ? 'text-blue-500 hover:bg-blue-500/10'
                              : `${muted} hover:bg-black/5`}`}
                          >
                            {visible ? <EyeIcon /> : <EyeOffIcon />}
                          </button>
                        </div>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>
            <div className={`flex items-center justify-between gap-3 px-5 py-3 border-t ${isDark ? 'border-slate-800' : 'border-slate-200'}`}>
              <button
                type="button"
                onClick={() => setScopeDraft(filesPanel.map(f => String(f.id)))}
                className={`text-xs font-medium ${muted} hover:opacity-80`}
              >
                Show all (full access)
              </button>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setScopeModalOpen(false)}
                  className={`rounded-lg px-3 py-1.5 text-sm font-medium ${isDark ? 'bg-slate-800 hover:bg-slate-700' : 'bg-slate-100 hover:bg-slate-200'}`}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={saveScope}
                  disabled={scopeSaving}
                  className={`rounded-lg px-4 py-1.5 text-sm font-semibold text-white transition disabled:opacity-50 ${isDark ? 'bg-blue-500 hover:bg-blue-400' : 'bg-blue-600 hover:bg-blue-500'}`}
                >
                  {scopeSaving ? 'Saving…' : 'Save'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* MCP Modal */}
      {mcpModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={() => { setMcpModalOpen(false); setMcpTab('tokens'); setMcpLogsTabs([]); }}>
          <div className={`absolute inset-0 ${isDark ? 'bg-black/60' : 'bg-slate-900/40'} backdrop-blur-sm`} />
          <div
            className={`relative z-10 flex flex-col w-[36rem] rounded-2xl shadow-2xl overflow-hidden ${isDark ? 'bg-slate-900 text-slate-100' : 'bg-white text-slate-900'}`}
            style={{ height: '560px' }}
            onClick={e => e.stopPropagation()}
          >
            {/* Header with tabs */}
            <div className={`flex shrink-0 items-center justify-between px-5 pt-3 pb-0 border-b ${isDark ? 'border-white/[0.06]' : 'border-slate-100'}`}>
              <div className="flex items-end gap-1">
                <button
                  type="button"
                  onClick={() => setMcpTab('tokens')}
                  className={`px-3 pb-2.5 pt-1 text-sm font-medium border-b-2 transition-colors ${mcpTab === 'tokens' ? 'border-blue-500 text-blue-500' : `border-transparent ${muted} hover:text-current`}`}
                >
                  Tokens <span className={`text-xs ${muted}`}>({mcpTokens.length}/10)</span>
                </button>
                {mcpLogsTabs.map(tab => (
                  <div key={tab.tokId} className={`group flex items-center gap-1 border-b-2 transition-colors ${mcpTab === tab.tokId ? 'border-blue-500' : 'border-transparent'}`}>
                    <button
                      type="button"
                      onClick={() => setMcpTab(tab.tokId)}
                      className={`pb-2.5 pt-1 pl-3 pr-1 text-sm font-medium transition-colors ${mcpTab === tab.tokId ? 'text-blue-500' : `${muted} hover:text-current`}`}
                    >
                      {tab.tokName}
                    </button>
                    <button
                      type="button"
                      onClick={() => closeMcpLogsTab(tab.tokId)}
                      className={`mb-1 mr-1 rounded p-0.5 transition opacity-0 group-hover:opacity-100 hover:bg-black/10 ${muted}`}
                      title="Close tab"
                    >
                      <svg viewBox="0 0 12 12" className="h-2.5 w-2.5 fill-current"><path d="M2.293 2.293a1 1 0 0 1 1.414 0L6 4.586l2.293-2.293a1 1 0 1 1 1.414 1.414L7.414 6l2.293 2.293a1 1 0 0 1-1.414 1.414L6 7.414 3.707 9.707a1 1 0 0 1-1.414-1.414L4.586 6 2.293 3.707a1 1 0 0 1 0-1.414Z"/></svg>
                    </button>
                  </div>
                ))}
              </div>
              <button type="button" onClick={() => { setMcpModalOpen(false); setMcpTab('tokens'); setMcpLogsTabs([]); }} className={`mb-1 rounded-full p-1.5 ${muted} hover:bg-black/5`}>
                <svg viewBox="0 0 16 16" className="h-4 w-4 fill-current"><path d="M4.293 4.293a1 1 0 0 1 1.414 0L8 6.586l2.293-2.293a1 1 0 1 1 1.414 1.414L9.414 8l2.293 2.293a1 1 0 0 1-1.414 1.414L8 9.414l-2.293 2.293a1 1 0 0 1-1.414-1.414L6.586 8 4.293 5.707a1 1 0 0 1 0-1.414Z"/></svg>
              </button>
            </div>

            {/* Header fade */}
            <div className={`h-3 shrink-0 pointer-events-none ${isDark ? 'bg-gradient-to-b from-slate-900 to-transparent' : 'bg-gradient-to-b from-white to-transparent'}`} />

            {/* Body — Tokens tab */}
            {mcpTab === 'tokens' && (
              <div className="flex-1 overflow-y-auto px-5 space-y-3">
                {mcpError && (
                  <div className={`rounded-xl border px-4 py-3 text-sm ${isDark ? 'border-red-400/20 bg-red-500/10 text-red-400' : 'border-red-200 bg-red-50 text-red-600'}`}>
                    {mcpError}
                  </div>
                )}
                {mcpLoading ? (
                  <div className="space-y-3">
                    {[1,2].map(i => <div key={i} className={`h-28 animate-pulse rounded-xl border ${line} ${subtle}`} />)}
                  </div>
                ) : mcpTokens.length === 0 ? (
                  <div className="py-8 text-center">
                    <p className={`text-sm ${muted}`}>No tokens yet. Create your first MCP token below.</p>
                  </div>
                ) : (
                  mcpTokens.map((tok) => (
                    <McpTokenCard
                      key={tok.id}
                      tok={tok}
                      isDark={isDark}
                      muted={muted}
                      toolDescs={mcpToolDescs}
                      onRevoke={handleRevokeMcpToken}
                      onToggleTool={handleToggleMcpTool}
                      onUpdateOrigins={handleUpdateMcpOrigins}
                      onRename={handleRenameMcpToken}
                      onViewLogs={handleViewLogs}
                    />
                  ))
                )}
              </div>
            )}

            {/* Body — Logs tabs */}
            {mcpTab !== 'tokens' && (() => {
              const tab = mcpLogsTabs.find(t => t.tokId === mcpTab);
              if (!tab) return null;
              return (
                <div className="flex flex-col flex-1 overflow-hidden">
                  <div className="flex-1 overflow-y-auto">
                    {tab.error && <div className={`m-4 rounded-xl border px-4 py-3 text-sm ${isDark ? 'border-red-400/20 bg-red-500/10 text-red-400' : 'border-red-200 bg-red-50 text-red-600'}`}>{tab.error}</div>}
                    <div className={`grid grid-cols-[100px_80px_50px_1fr_130px] px-5 py-2 text-[10px] font-semibold uppercase tracking-wide border-b ${muted} ${isDark ? 'border-white/[0.06]' : 'border-slate-100'}`}>
                      <span>Tool</span><span>Status</span><span>Code</span><span>Origin / Error</span><span>Time</span>
                    </div>
                    {tab.loading ? (
                      <div className="space-y-px p-3">{[...Array(6)].map((_, i) => <div key={i} className={`h-9 animate-pulse rounded-lg ${isDark ? 'bg-white/[0.03]' : 'bg-slate-50'}`} />)}</div>
                    ) : tab.logs.length === 0 ? (
                      <p className={`px-5 py-10 text-center text-sm ${muted}`}>No requests yet.</p>
                    ) : tab.logs.map(log => {
                      const sc = log.status === 'success' ? isDark ? 'text-green-400 bg-green-400/10' : 'text-green-700 bg-green-50'
                               : log.status === 'forbidden' ? isDark ? 'text-yellow-400 bg-yellow-400/10' : 'text-yellow-700 bg-yellow-50'
                               : isDark ? 'text-red-400 bg-red-400/10' : 'text-red-700 bg-red-50';
                      return (
                        <div key={log.id} className={`grid grid-cols-[100px_80px_50px_1fr_130px] border-b px-5 py-2 text-xs ${isDark ? 'border-white/[0.04] hover:bg-white/[0.02]' : 'border-slate-50 hover:bg-slate-50'}`}>
                          <span className="font-mono font-medium">{log.tool}</span>
                          <span><span className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${sc}`}>{log.status}</span></span>
                          <span className={muted}>{log.status_code}</span>
                          <span className={`truncate ${muted}`}>{log.error_message || log.origin || '—'}</span>
                          <span className={muted}>{new Date(log.created_at).toLocaleString()}</span>
                        </div>
                      );
                    })}
                  </div>
                  {tab.total > MCP_LOGS_LIMIT && (
                    <div className={`flex shrink-0 items-center justify-between px-5 py-2.5 text-xs border-t ${isDark ? 'border-white/[0.06]' : 'border-slate-100'}`}>
                      <button type="button" disabled={tab.offset === 0} onClick={() => fetchMcpLogs(tab.tokId, tab.tokName, Math.max(0, tab.offset - MCP_LOGS_LIMIT))} className={`rounded-lg px-3 py-1.5 disabled:opacity-30 ${isDark ? 'bg-white/[0.05] hover:bg-white/10' : 'bg-slate-100 hover:bg-slate-200'}`}>← Prev</button>
                      <span className={muted}>{tab.offset + 1}–{Math.min(tab.offset + MCP_LOGS_LIMIT, tab.total)} of {tab.total}</span>
                      <button type="button" disabled={tab.offset + MCP_LOGS_LIMIT >= tab.total} onClick={() => fetchMcpLogs(tab.tokId, tab.tokName, tab.offset + MCP_LOGS_LIMIT)} className={`rounded-lg px-3 py-1.5 disabled:opacity-30 ${isDark ? 'bg-white/[0.05] hover:bg-white/10' : 'bg-slate-100 hover:bg-slate-200'}`}>Next →</button>
                    </div>
                  )}
                </div>
              );
            })()}

            {/* Footer fade */}
            <div className={`h-3 shrink-0 pointer-events-none ${isDark ? 'bg-gradient-to-t from-slate-900 to-transparent' : 'bg-gradient-to-t from-white to-transparent'}`} />

            {/* Footer */}
            {mcpTab === 'tokens' && (
              <div className="flex shrink-0 items-center justify-end px-5 py-3">
                <button
                  type="button"
                  onClick={handleCreateMcpToken}
                  disabled={mcpTokens.length >= 10}
                  className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:opacity-40"
                >
                  + Create Token
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </main>
  );
}

const PIPELINE_FLOW_STEPS = [
  {
    step: '1',
    title: 'User uploads file',
    service: 'Frontend -> POST /v1/buckets/{bucket_id}/files',
    detail: 'The browser sends multipart file data to the backend.',
    output: 'UploadFile payload arrives at FastAPI.',
  },
  {
    step: '2',
    title: 'Backend saves raw file to R2',
    service: 'app.services.pipeline.upload + app.services.storage.r2',
    detail: 'Raw bytes are stored first at a versioned object key in Cloudflare R2.',
    output: 'raw/{file_id}/v1/{filename}',
  },
  {
    step: '3',
    title: 'Postgres creates file row',
    service: 'files + file_versions tables',
    detail: 'The backend creates the file metadata row and version history row after raw storage succeeds.',
    output: 'files.id + file_versions.version_number=1',
  },
  {
    step: '4',
    title: 'Status = processing',
    service: 'files.status',
    detail: 'The file becomes processing before background orchestration starts.',
    output: 'status=processing',
  },
  {
    step: '5',
    title: 'Docling extracts text/layout',
    service: 'app.services.processing.docling_service',
    detail: 'Docling reads the raw document and returns structured blocks and page count.',
    output: 'DoclingResult(blocks, page_count)',
  },
  {
    step: '6',
    title: 'Gemini reads images/visual parts',
    service: 'app.services.processing.gemini_service',
    detail: 'Every extracted image is described and OCR text is pulled out. If Gemini is required and fails, the file fails.',
    output: 'GeminiImageResult[]',
  },
  {
    step: '7',
    title: 'Layout JSON is built',
    service: 'app.services.processing.layout_builder',
    detail: 'Docling blocks and Gemini visual results are merged into one layout map.',
    output: 'layout.json object',
  },
  {
    step: '8',
    title: 'Layout JSON saved to R2',
    service: 'app.services.storage.r2.upload_json',
    detail: 'The canonical layout artifact is stored in R2.',
    output: 'layouts/{file_id}/layout.json',
  },
  {
    step: '9',
    title: 'Content is chunked',
    service: 'app.services.processing.chunker',
    detail: 'Text, tables, headings, and image-adjacent metadata are turned into chunk records. Image-only files get fallback searchable chunks.',
    output: 'ChunkRecord[]',
  },
  {
    step: '10',
    title: 'Text embeddings are created',
    service: 'BGE-M3',
    detail: 'Each searchable text chunk is embedded into dense + sparse vectors.',
    output: 'dense + sparse vectors',
  },
  {
    step: '11',
    title: 'Image embeddings are created',
    service: 'CLIP',
    detail: 'Each extracted image gets its own image vector.',
    output: '512-d image vectors',
  },
  {
    step: '12',
    title: 'Vectors saved to Qdrant',
    service: 'text_chunks + image_chunks collections',
    detail: 'Text and image vectors are upserted before Postgres chunk rows are finalized.',
    output: 'Qdrant points with status=active',
  },
  {
    step: '13',
    title: 'Postgres chunks updated',
    service: 'chunks table',
    detail: 'Embedded chunk rows are written after Qdrant succeeds.',
    output: 'chunks.status=embedded',
  },
  {
    step: '14',
    title: 'Status = ready',
    service: 'files.status',
    detail: 'The file flips to ready only after the full indexing pipeline succeeds.',
    output: 'status=ready',
  },
  {
    step: '15',
    title: 'Agent can use the file',
    service: 'app.services.agent.retrieval',
    detail: 'The agent only retrieves files whose DB status is ready.',
    output: 'search_bucket_documents() returns ready chunks only',
  },
];

const PIPELINE_NODE_POSITIONS = [
  { x: 40, y: 30 },
  { x: 380, y: 30 },
  { x: 720, y: 30 },
  { x: 1060, y: 30 },
  { x: 1060, y: 220 },
  { x: 720, y: 220 },
  { x: 380, y: 220 },
  { x: 40, y: 220 },
  { x: 40, y: 410 },
  { x: 380, y: 410 },
  { x: 720, y: 410 },
  { x: 1060, y: 410 },
  { x: 1060, y: 600 },
  { x: 720, y: 600 },
  { x: 380, y: 600 },
];

function buildPipelineNodes(theme) {
  const isDark = theme === 'dark';
  return PIPELINE_FLOW_STEPS.map((item, index) => ({
    id: item.step,
    position: PIPELINE_NODE_POSITIONS[index],
    draggable: false,
    selectable: false,
    data: {
      label: (
        <div className="min-w-[220px]">
          <div className={`mb-2 inline-flex h-7 w-7 items-center justify-center rounded-full text-[11px] font-semibold ${isDark ? 'bg-cyan-500/12 text-cyan-300' : 'bg-cyan-50 text-cyan-700'}`}>
            {item.step}
          </div>
          <div className={`text-sm font-semibold ${isDark ? 'text-white' : 'text-slate-900'}`}>{item.title}</div>
          <div className={`mt-2 text-[11px] uppercase tracking-[0.18em] ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>{item.service}</div>
        </div>
      ),
    },
    style: {
      width: 260,
      borderRadius: 22,
      border: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(148,163,184,0.25)',
      background: isDark ? 'rgba(15,23,42,0.9)' : 'rgba(255,255,255,0.95)',
      boxShadow: isDark ? '0 18px 50px rgba(2,6,23,0.45)' : '0 18px 50px rgba(148,163,184,0.18)',
      padding: '14px 16px',
    },
  }));
}

function buildPipelineStatusNodes(theme, statuses) {
  const isDark = theme === 'dark';
  const statusStyles = {
    pending: {
      border: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(148,163,184,0.25)',
      background: isDark ? 'rgba(15,23,42,0.9)' : 'rgba(255,255,255,0.95)',
      badge: isDark ? 'bg-slate-800 text-slate-300' : 'bg-slate-100 text-slate-600',
    },
    active: {
      border: '1px solid rgba(14,165,233,0.75)',
      background: isDark ? 'rgba(8,47,73,0.72)' : 'rgba(224,242,254,0.98)',
      badge: isDark ? 'bg-cyan-500/15 text-cyan-300' : 'bg-cyan-50 text-cyan-700',
    },
    completed: {
      border: '1px solid rgba(16,185,129,0.7)',
      background: isDark ? 'rgba(6,78,59,0.65)' : 'rgba(236,253,245,0.98)',
      badge: isDark ? 'bg-emerald-500/15 text-emerald-300' : 'bg-emerald-50 text-emerald-700',
    },
    failed: {
      border: '1px solid rgba(248,113,113,0.75)',
      background: isDark ? 'rgba(127,29,29,0.58)' : 'rgba(254,242,242,0.98)',
      badge: isDark ? 'bg-red-500/15 text-red-300' : 'bg-red-50 text-red-700',
    },
    skipped: {
      border: isDark ? '1px solid rgba(250,204,21,0.45)' : '1px solid rgba(234,179,8,0.45)',
      background: isDark ? 'rgba(113,63,18,0.38)' : 'rgba(254,249,195,0.98)',
      badge: isDark ? 'bg-amber-500/15 text-amber-300' : 'bg-amber-50 text-amber-700',
    },
  };

  return PIPELINE_FLOW_STEPS.map((item, index) => {
    const state = statuses[item.step] || { status: 'pending', note: 'Waiting' };
    const style = statusStyles[state.status] || statusStyles.pending;
    return {
      id: item.step,
      position: PIPELINE_NODE_POSITIONS[index],
      draggable: false,
      selectable: false,
      data: {
        label: (
          <div className="min-w-[220px]">
            <div className="flex items-start justify-between gap-3">
              <div className={`inline-flex h-7 w-7 items-center justify-center rounded-full text-[11px] font-semibold ${isDark ? 'bg-white/10 text-white' : 'bg-slate-100 text-slate-700'}`}>
                {item.step}
              </div>
              <span className={`rounded-full px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] ${style.badge}`}>
                {state.status}
              </span>
            </div>
            <div className={`mt-3 text-sm font-semibold ${isDark ? 'text-white' : 'text-slate-900'}`}>{item.title}</div>
            <div className={`mt-2 text-[11px] uppercase tracking-[0.18em] ${isDark ? 'text-slate-300/85' : 'text-slate-500'}`}>{item.service}</div>
            <div className={`mt-3 text-xs leading-5 ${isDark ? 'text-slate-200/85' : 'text-slate-600'}`}>{state.note}</div>
          </div>
        ),
      },
      style: {
        width: 260,
        borderRadius: 22,
        border: style.border,
        background: style.background,
        boxShadow: isDark ? '0 18px 50px rgba(2,6,23,0.45)' : '0 18px 50px rgba(148,163,184,0.18)',
        padding: '14px 16px',
      },
    };
  });
}

const PIPELINE_EDGES = PIPELINE_FLOW_STEPS.slice(0, -1).map((item, index) => ({
  id: `e-${item.step}-${PIPELINE_FLOW_STEPS[index + 1].step}`,
  source: item.step,
  target: PIPELINE_FLOW_STEPS[index + 1].step,
  type: 'smoothstep',
  animated: true,
  markerEnd: { type: MarkerType.ArrowClosed },
  style: { strokeWidth: 2.5, stroke: '#0ea5e9' },
}));

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function hasImageBlocks(layout) {
  return Boolean(
    layout?.pages?.some((page) => page.blocks?.some((block) => block.type === 'image'))
  );
}

function getLatestFailedEvent(events) {
  for (let index = events.length - 1; index >= 0; index -= 1) {
    if (events[index]?.status === 'failed') return events[index];
  }
  return null;
}

function buildTraceStepStatuses(file, events, layout, chunks) {
  const failedEvent = getLatestFailedEvent(events);
  const failureStage = failedEvent?.event_metadata?.stage || null;
  const failureError = failedEvent?.event_metadata?.error || null;
  const failureNote = failureError
    ? `${failureStage || failedEvent?.event || 'pipeline_failed'}: ${failureError}`
    : 'Pipeline failed before completion.';
  const fileReady = file?.status === 'ready';
  const fileFailed = file?.status === 'failed' || Boolean(failedEvent);
  const hasLayout = Boolean(layout?.layout_json_path && layout?.layout);
  const chunkCount = Array.isArray(chunks) ? chunks.length : 0;
  const imageBlocksPresent = hasImageBlocks(layout?.layout || layout);

  const hasEvent = (eventName, status) =>
    events.some((event) => event.event === eventName && (!status || event.status === status));

  const started = (eventName) => hasEvent(eventName, 'started');
  const completed = (eventName) => hasEvent(eventName, 'completed');

  const statusFor = (status, note) => ({ status, note });
  const statuses = {
    '1': file ? statusFor('completed', 'File reached the backend upload endpoint.') : statusFor('pending', 'Waiting for a file upload.'),
    '2': failureStage === 'download'
      ? statusFor('failed', failureNote)
      : file?.r2_path
        ? statusFor('completed', file.r2_path)
        : statusFor(fileFailed ? 'failed' : 'pending', 'Raw object not stored yet.'),
    '3': file?.id ? statusFor('completed', `File row ${String(file.id).slice(0, 8)} created.`) : statusFor(fileFailed ? 'failed' : 'pending', 'Database row not created yet.'),
    '4': file?.status === 'processing'
      ? statusFor('active', 'File is currently processing.')
      : file?.status
        ? statusFor(fileReady ? 'completed' : fileFailed ? 'failed' : 'completed', fileFailed ? failureNote : `Current status: ${file.status}`)
        : statusFor('pending', 'Not processing yet.'),
    '5': failureStage === 'docling'
      ? statusFor('failed', failureNote)
      : completed('docling_completed')
      ? statusFor('completed', 'Docling extracted document blocks.')
      : started('docling_started')
        ? statusFor(fileFailed ? 'failed' : 'active', 'Docling is running.')
        : statusFor(fileFailed ? 'failed' : 'pending', 'Docling has not started yet.'),
    '6': failureStage === 'gemini'
      ? statusFor('failed', failureNote)
      : completed('gemini_completed')
      ? statusFor('completed', 'Gemini finished visual extraction.')
      : imageBlocksPresent && started('gemini_started')
        ? statusFor(fileFailed ? 'failed' : 'active', 'Gemini is reading image blocks.')
        : imageBlocksPresent && fileReady
          ? statusFor('completed', 'Gemini results are present in the final layout.')
          : !imageBlocksPresent && hasLayout
            ? statusFor('skipped', 'No image blocks were present in this file.')
            : statusFor(fileFailed ? 'failed' : 'pending', 'Waiting for visual extraction.'),
    '7': failureStage === 'layout_build'
      ? statusFor('failed', failureNote)
      : hasLayout
      ? statusFor('completed', `Layout has ${layout.layout.page_count || 0} pages.`)
      : fileFailed
        ? statusFor('failed', 'Layout was not built.')
        : statusFor('pending', 'Layout JSON not available yet.'),
    '8': failureStage === 'layout_upload'
      ? statusFor('failed', failureNote)
      : file?.layout_json_path
      ? statusFor('completed', file.layout_json_path)
      : fileFailed
        ? statusFor('failed', 'Layout path was never written.')
        : statusFor('pending', 'Layout JSON path pending.'),
    '9': failureStage === 'chunking'
      ? statusFor('failed', failureNote)
      : completed('chunking_completed') || chunkCount > 0
      ? statusFor('completed', `${chunkCount} chunk${chunkCount === 1 ? '' : 's'} prepared.`)
      : started('chunking_started')
        ? statusFor(fileFailed ? 'failed' : 'active', 'Chunker is building chunk records.')
        : statusFor(fileFailed ? 'failed' : 'pending', 'Chunking has not started yet.'),
    '10': failureStage === 'text_embeddings'
      ? statusFor('failed', failureNote)
      : completed('embedding_completed') && chunkCount > 0
      ? statusFor('completed', 'Text embeddings completed.')
      : started('embedding_started')
        ? statusFor(fileFailed ? 'failed' : 'active', 'Embedding stage is running.')
        : statusFor(fileFailed ? 'failed' : 'pending', 'Text embeddings pending.'),
    '11': imageBlocksPresent
      ? failureStage === 'image_embeddings'
        ? statusFor('failed', failureNote)
        : completed('embedding_completed')
        ? statusFor('completed', 'Image embeddings completed.')
        : started('embedding_started')
          ? statusFor(fileFailed ? 'failed' : 'active', 'Image embedding stage is running.')
          : statusFor(fileFailed ? 'failed' : 'pending', 'Image embeddings pending.')
      : statusFor(hasLayout ? 'skipped' : 'pending', hasLayout ? 'No image vectors needed for this file.' : 'Waiting for layout.'),
    '12': failureStage === 'qdrant_text_upsert' || failureStage === 'qdrant_image_upsert' || failureStage === 'vector_cleanup'
      ? statusFor('failed', failureNote)
      : completed('embedding_completed')
      ? statusFor('completed', 'Vector payloads were sent to Qdrant.')
      : started('embedding_started')
        ? statusFor(fileFailed ? 'failed' : 'active', 'Waiting for vector writes to finish.')
        : statusFor(fileFailed ? 'failed' : 'pending', 'Qdrant write not reached yet.'),
    '13': failureStage === 'chunk_persist'
      ? statusFor('failed', failureNote)
      : chunkCount > 0
      ? statusFor('completed', `${chunkCount} embedded chunk row${chunkCount === 1 ? '' : 's'} available.`)
      : fileReady
        ? statusFor('completed', 'File finished with no text chunks.')
        : statusFor(fileFailed ? 'failed' : 'pending', 'Postgres chunk rows not available yet.'),
    '14': fileReady
      ? statusFor('completed', 'File is ready.')
      : fileFailed
        ? statusFor('failed', 'File ended in failed state.')
        : file?.status === 'processing'
          ? statusFor('active', 'Waiting for ready state.')
          : statusFor('pending', 'Ready state not reached yet.'),
    '15': fileReady
      ? statusFor('completed', 'Agent can retrieve this file now.')
      : fileFailed
        ? statusFor('failed', 'Agent cannot use a failed file.')
        : statusFor('pending', 'Agent access is blocked until ready.'),
  };

  return statuses;
}

function JsonPreview({ theme, title, data }) {
  const isDark = theme === 'dark';
  return (
    <section className={`overflow-hidden rounded-[1.35rem] border ${isDark ? 'border-white/10 bg-slate-950/70' : 'border-slate-200 bg-white'}`}>
      <div className={`border-b px-4 py-3 text-xs font-semibold uppercase tracking-[0.24em] ${isDark ? 'border-white/10 bg-white/[0.03] text-cyan-300' : 'border-slate-200 bg-slate-50 text-cyan-700'}`}>
        {title}
      </div>
      <pre className={`max-h-[28rem] overflow-auto p-4 text-xs leading-6 ${isDark ? 'text-slate-200' : 'text-slate-800'}`}>
        <code>{JSON.stringify(data, null, 2)}</code>
      </pre>
    </section>
  );
}

function slugifyFilenamePart(value, fallback = 'file') {
  const text = String(value || fallback)
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
  return text || fallback;
}

function downloadJsonFile(filename, data) {
  if (typeof window === 'undefined') return;
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  window.URL.revokeObjectURL(url);
}

function TempPipelinePage({ theme, onToggleTheme }) {
  const palette = themeOptions[theme];
  const isDark = theme === 'dark';
  const navigate = useNavigate();
  const uploadRef = useRef(null);
  const [buckets, setBuckets] = useState([]);
  const [bucketFiles, setBucketFiles] = useState([]);
  const [selectedBucketId, setSelectedBucketId] = useState('');
  const [selectedFileId, setSelectedFileId] = useState('');
  const [loadingBuckets, setLoadingBuckets] = useState(true);
  const [loadingFiles, setLoadingFiles] = useState(false);
  const [creatingBucket, setCreatingBucket] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(false);
  const [polling, setPolling] = useState(false);
  const [copyingBundle, setCopyingBundle] = useState(false);
  const [downloadingBundle, setDownloadingBundle] = useState(false);
  const [downloadingSeparate, setDownloadingSeparate] = useState(false);
  const [traceError, setTraceError] = useState(null);
  const [traceFile, setTraceFile] = useState(null);
  const [traceEvents, setTraceEvents] = useState([]);
  const [traceLayout, setTraceLayout] = useState(null);
  const [traceChunks, setTraceChunks] = useState([]);

  useEffect(() => {
    const token = sessionStorage.getItem('access_token');
    if (!token) {
      navigate('/login');
      return;
    }

    let cancelled = false;

    async function loadBuckets() {
      try {
        const data = await dashboardApi.listBuckets();
        if (cancelled) return;
        const rows = Array.isArray(data) ? data : (data.buckets || []);
        setBuckets(rows);
        if (!selectedBucketId && rows[0]?.id) setSelectedBucketId(String(rows[0].id));
      } catch (error) {
        if (!cancelled) setTraceError(error.message);
      } finally {
        if (!cancelled) setLoadingBuckets(false);
      }
    }

    loadBuckets();
    return () => { cancelled = true; };
  }, [navigate, selectedBucketId]);

  useEffect(() => {
    if (!selectedBucketId) {
      setBucketFiles([]);
      setSelectedFileId('');
      return;
    }

    let cancelled = false;

    async function loadBucketFiles(preferredFileId = null) {
      setLoadingFiles(true);
      try {
        const data = await bucketApi.listFiles(selectedBucketId);
        if (cancelled) return;
        const rows = Array.isArray(data) ? data : (data.files || []);
        setBucketFiles(rows);

        const preferred =
          rows.find((file) => String(file.id) === String(preferredFileId))
          || rows.find((file) => String(file.id) === String(selectedFileId))
          || rows[0]
          || null;

        setSelectedFileId(preferred ? String(preferred.id) : '');
      } catch (error) {
        if (!cancelled) setTraceError(error.message);
      } finally {
        if (!cancelled) setLoadingFiles(false);
      }
    }

    loadBucketFiles();
    return () => { cancelled = true; };
  }, [selectedBucketId]);

  async function createDemoBucket() {
    setCreatingBucket(true);
    setTraceError(null);
    try {
      const existing = buckets.find((bucket) => bucket.name === 'Pipeline Demo');
      if (existing) {
        setSelectedBucketId(String(existing.id));
        return;
      }
      const bucket = await dashboardApi.createBucket(
        'Pipeline Demo',
        'Temporary bucket for upload tracing',
        '#0ea5e9',
        'folder',
      );
      setBuckets((prev) => [bucket, ...prev]);
      setSelectedBucketId(String(bucket.id));
    } catch (error) {
      if (error.message === 'A bucket with this name already exists.') {
        const refreshed = await dashboardApi.listBuckets();
        const rows = Array.isArray(refreshed) ? refreshed : (refreshed.buckets || []);
        setBuckets(rows);
        const existing = rows.find((bucket) => bucket.name === 'Pipeline Demo');
        if (existing) {
          setSelectedBucketId(String(existing.id));
          return;
        }
      }
      setTraceError(error.message);
    } finally {
      setCreatingBucket(false);
    }
  }

  async function refreshTrace(bucketId, fileId) {
    const [file, events] = await Promise.all([
      bucketApi.getFile(bucketId, fileId),
      bucketApi.listFileEvents(bucketId, fileId),
    ]);

    setTraceFile(file);
    const eventRows = events.events || [];
    setTraceEvents(eventRows);

    let layoutData = null;
    if (file.layout_json_path || file.status === 'ready') {
      try {
        layoutData = await bucketApi.getFileLayout(bucketId, fileId);
      } catch (_) {
        layoutData = null;
      }
    }

    let chunkRows = [];
    if (file.status === 'ready' || file.status === 'failed') {
      try {
        const chunks = await bucketApi.listFileChunks(bucketId, fileId);
        chunkRows = chunks.chunks || [];
      } catch (_) {
        chunkRows = [];
      }
    }

    setTraceLayout(layoutData);
    setTraceChunks(chunkRows);
    return { file, events: eventRows };
  }

  async function pollTrace(bucketId, fileId) {
    setPolling(true);
    try {
      for (let attempt = 0; attempt < 60; attempt += 1) {
        const { file, events } = await refreshTrace(bucketId, fileId);
        if (file.status === 'ready' || file.status === 'failed' || events.some((event) => event.status === 'failed')) break;
        await sleep(2500);
      }
    } finally {
      setPolling(false);
    }
  }

  async function handleUploadInput(event) {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file || !selectedBucketId) return;

    setTraceError(null);
    setTraceFile(null);
    setTraceEvents([]);
    setTraceLayout(null);
    setTraceChunks([]);
    setUploadingFile(true);

    try {
      const uploaded = await uploadFilesDirect(selectedBucketId, [file]);
      const uploadedFile = Array.isArray(uploaded) ? uploaded[0] : null;
      if (!uploadedFile?.id) throw new Error('Upload succeeded but no file id was returned.');
      const uploadedFileId = String(uploadedFile.id);
      setSelectedFileId(uploadedFileId);
      setBucketFiles((prev) => [uploadedFile, ...prev.filter((row) => String(row.id) !== uploadedFileId)]);
      await pollTrace(selectedBucketId, String(uploadedFile.id));
      const refreshedFiles = await bucketApi.listFiles(selectedBucketId);
      const rows = Array.isArray(refreshedFiles) ? refreshedFiles : (refreshedFiles.files || []);
      setBucketFiles(rows);
    } catch (error) {
      setTraceError(error.message);
    } finally {
      setUploadingFile(false);
    }
  }

  useEffect(() => {
    if (!selectedBucketId || !selectedFileId) {
      setTraceFile(null);
      setTraceEvents([]);
      setTraceLayout(null);
      setTraceChunks([]);
      return;
    }

    if (uploadingFile) return;

    let cancelled = false;

    async function loadSelectedFile() {
      setTraceError(null);
      try {
        const { file, events } = await refreshTrace(selectedBucketId, selectedFileId);
        if (cancelled) return;
        if (file.status === 'processing' && !events.some((event) => event.status === 'failed')) {
          await pollTrace(selectedBucketId, selectedFileId);
        }
      } catch (error) {
        if (!cancelled) setTraceError(error.message);
      }
    }

    loadSelectedFile();
    return () => { cancelled = true; };
  }, [selectedBucketId, selectedFileId, uploadingFile]);

  const stepStatuses = buildTraceStepStatuses(traceFile, traceEvents, traceLayout, traceChunks);
  const nodes = buildPipelineStatusNodes(theme, stepStatuses);
  const activeBucket = buckets.find((bucket) => String(bucket.id) === String(selectedBucketId));
  const activeBucketFile = bucketFiles.find((file) => String(file.id) === String(selectedFileId));
  const failedEvent = getLatestFailedEvent(traceEvents);
  const failedStage = failedEvent?.event_metadata?.stage || 'unknown';
  const failedMessage = failedEvent?.event_metadata?.error || 'Pipeline failed without an error message.';
  const latestTraceRunId = [...traceEvents].reverse().find((event) => event?.event_metadata?.trace_run_id)?.event_metadata?.trace_run_id || null;
  const processingSummary = traceFile ? {
    file: traceFile,
    current_trace_run_id: latestTraceRunId,
    event_count: traceEvents.length,
    chunk_count: traceChunks.length,
    has_layout: Boolean(traceLayout?.layout),
    last_failure: failedEvent ? failedEvent.event_metadata : null,
  } : null;
  const exportBaseName = traceFile
    ? `${slugifyFilenamePart(traceFile.name, 'file')}-${String(traceFile.id).slice(0, 8)}`
    : 'pipeline-file';
  const bundleData = traceFile ? {
    exported_at: new Date().toISOString(),
    bucket: activeBucket || null,
    file: traceFile,
    summary: processingSummary,
    events: traceEvents,
    layout: traceLayout,
    chunks: traceChunks,
  } : null;

  async function handleCopyBundle() {
    if (!bundleData || !navigator?.clipboard) return;
    setTraceError(null);
    setCopyingBundle(true);
    try {
      await navigator.clipboard.writeText(JSON.stringify(bundleData, null, 2));
    } catch (error) {
      setTraceError(error.message || 'Could not copy bundle JSON.');
    } finally {
      setCopyingBundle(false);
    }
  }

  function handleDownloadBundle() {
    if (!bundleData) return;
    setTraceError(null);
    setDownloadingBundle(true);
    try {
      downloadJsonFile(`${exportBaseName}-bundle.json`, bundleData);
    } catch (error) {
      setTraceError(error.message || 'Could not download bundle JSON.');
    } finally {
      setDownloadingBundle(false);
    }
  }

  function handleDownloadSeparate() {
    if (!traceFile) return;
    setTraceError(null);
    setDownloadingSeparate(true);
    try {
      downloadJsonFile(`${exportBaseName}-file.json`, traceFile);
      downloadJsonFile(`${exportBaseName}-summary.json`, processingSummary);
      downloadJsonFile(`${exportBaseName}-events.json`, traceEvents);
      downloadJsonFile(`${exportBaseName}-layout.json`, traceLayout || { status: 'not_ready_yet' });
      downloadJsonFile(`${exportBaseName}-chunks.json`, traceChunks);
    } catch (error) {
      setTraceError(error.message || 'Could not download separate JSON files.');
    } finally {
      setDownloadingSeparate(false);
    }
  }

  return (
    <main className={`min-h-[100dvh] transition-colors duration-300 ${palette.app}`}>
      <div className="mx-auto flex max-w-7xl flex-col gap-8 px-4 py-6 sm:px-6 lg:px-8">
        <input ref={uploadRef} type="file" className="hidden" onChange={handleUploadInput} />
        <header className={`overflow-hidden rounded-[2rem] border px-6 py-6 sm:px-8 ${palette.card}`}>
          <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-3xl">
              <p className={`text-xs font-semibold uppercase tracking-[0.35em] ${palette.accent}`}>Temporary Pipeline View</p>
              <h1 className={`mt-3 text-3xl font-semibold tracking-tight sm:text-4xl ${palette.title}`}>
                {'Upload -> RAG -> Ready -> Agent'}
              </h1>
              <p className={`mt-3 max-w-2xl text-sm leading-7 ${palette.text}`}>
                Upload one real file here, watch the pipeline progress, and inspect the actual backend output: file metadata, event timeline, layout JSON, and chunks.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <button
                type="button"
                onClick={onToggleTheme}
                className={`rounded-full border px-4 py-2 text-sm font-medium transition ${palette.toggle}`}
              >
                {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
              </button>
              <Link
                to="/login"
                className={`rounded-full border px-4 py-2 text-sm font-medium transition ${palette.secondary}`}
              >
                Back
              </Link>
            </div>
          </div>
        </header>

        <section className={`rounded-[2rem] border px-5 py-6 sm:px-6 ${palette.card}`}>
          <div className="mb-5">
            <p className={`text-xs font-semibold uppercase tracking-[0.3em] ${palette.accent}`}>Upload</p>
            <h2 className={`mt-2 text-2xl font-semibold ${palette.title}`}>Upload a file and trace its flow</h2>
          </div>
          <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_auto_auto] lg:items-end">
            <label className="block">
              <span className={`mb-2 block text-sm font-medium ${palette.title}`}>Bucket</span>
              <select
                value={selectedBucketId}
                onChange={(event) => {
                  setSelectedBucketId(event.target.value);
                  setSelectedFileId('');
                }}
                disabled={loadingBuckets || creatingBucket || uploadingFile || polling}
                className={`w-full rounded-2xl border px-4 py-3 text-sm outline-none transition ${palette.input}`}
              >
                {buckets.length === 0 ? <option value="">No buckets yet</option> : null}
                {buckets.map((bucket) => (
                  <option key={bucket.id} value={bucket.id}>
                    {bucket.name}
                  </option>
                ))}
              </select>
            </label>
            <button
              type="button"
              onClick={createDemoBucket}
              disabled={creatingBucket || uploadingFile || polling}
              className={`rounded-2xl border px-4 py-3 text-sm font-semibold transition ${palette.secondary}`}
            >
              {creatingBucket ? 'Creating bucket...' : 'Create Demo Bucket'}
            </button>
            <button
              type="button"
              onClick={() => uploadRef.current?.click()}
              disabled={!selectedBucketId || loadingBuckets || uploadingFile || polling}
              className={`rounded-2xl px-4 py-3 text-sm font-semibold transition ${palette.primary}`}
            >
              {uploadingFile || polling ? 'Processing file...' : 'Upload File'}
            </button>
          </div>
          <div className="mt-4 grid gap-4 lg:grid-cols-[minmax(0,1fr)_auto_auto_auto] lg:items-end">
            <label className="block">
              <span className={`mb-2 block text-sm font-medium ${palette.title}`}>Existing file in bucket</span>
              <select
                value={selectedFileId}
                onChange={(event) => setSelectedFileId(event.target.value)}
                disabled={!selectedBucketId || loadingFiles || uploadingFile}
                className={`w-full rounded-2xl border px-4 py-3 text-sm outline-none transition ${palette.input}`}
              >
                {bucketFiles.length === 0 ? <option value="">No files in this bucket</option> : null}
                {bucketFiles.map((file) => (
                  <option key={file.id} value={file.id}>
                    {file.name} [{file.status}]
                  </option>
                ))}
              </select>
            </label>
            <button
              type="button"
              onClick={handleCopyBundle}
              disabled={!bundleData || copyingBundle}
              className={`rounded-2xl border px-4 py-3 text-sm font-semibold transition ${palette.secondary}`}
            >
              {copyingBundle ? 'Copying...' : 'Copy Bundle JSON'}
            </button>
            <button
              type="button"
              onClick={handleDownloadBundle}
              disabled={!bundleData || downloadingBundle}
              className={`rounded-2xl border px-4 py-3 text-sm font-semibold transition ${palette.secondary}`}
            >
              {downloadingBundle ? 'Downloading...' : 'Download One JSON'}
            </button>
            <button
              type="button"
              onClick={handleDownloadSeparate}
              disabled={!traceFile || downloadingSeparate}
              className={`rounded-2xl border px-4 py-3 text-sm font-semibold transition ${palette.secondary}`}
            >
              {downloadingSeparate ? 'Downloading...' : 'Download Separate JSONs'}
            </button>
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-3">
            <div className={`rounded-[1.2rem] border p-4 ${isDark ? 'border-white/10 bg-white/[0.03]' : 'border-slate-200 bg-white'}`}>
              <p className={`text-xs font-semibold uppercase tracking-[0.22em] ${palette.accent}`}>Active bucket</p>
              <p className={`mt-2 text-sm font-semibold ${palette.title}`}>{activeBucket?.name || 'None selected'}</p>
            </div>
            <div className={`rounded-[1.2rem] border p-4 ${isDark ? 'border-white/10 bg-white/[0.03]' : 'border-slate-200 bg-white'}`}>
              <p className={`text-xs font-semibold uppercase tracking-[0.22em] ${palette.accent}`}>Selected file</p>
              <p className={`mt-2 text-sm font-semibold ${palette.title}`}>{traceFile?.name || activeBucketFile?.name || 'No file selected'}</p>
            </div>
            <div className={`rounded-[1.2rem] border p-4 ${isDark ? 'border-white/10 bg-white/[0.03]' : 'border-slate-200 bg-white'}`}>
              <p className={`text-xs font-semibold uppercase tracking-[0.22em] ${palette.accent}`}>State</p>
              <p className={`mt-2 text-sm font-semibold ${palette.title}`}>
                {traceFile?.status || (uploadingFile || polling ? 'processing' : 'idle')}
              </p>
            </div>
          </div>
          <div className="mt-3 grid gap-3 md:grid-cols-2">
            <div className={`rounded-[1.2rem] border p-4 ${isDark ? 'border-white/10 bg-white/[0.03]' : 'border-slate-200 bg-white'}`}>
              <p className={`text-xs font-semibold uppercase tracking-[0.22em] ${palette.accent}`}>Files in bucket</p>
              <p className={`mt-2 text-sm font-semibold ${palette.title}`}>{bucketFiles.length}</p>
            </div>
            <div className={`rounded-[1.2rem] border p-4 ${isDark ? 'border-white/10 bg-white/[0.03]' : 'border-slate-200 bg-white'}`}>
              <p className={`text-xs font-semibold uppercase tracking-[0.22em] ${palette.accent}`}>Export name</p>
              <p className={`mt-2 break-all text-sm font-semibold ${palette.title}`}>{traceFile ? exportBaseName : 'No file selected'}</p>
            </div>
          </div>
          {traceError ? (
            <div className={`mt-4 rounded-2xl border px-4 py-3 text-sm ${palette.error}`}>
              {traceError}
            </div>
          ) : null}
          {failedEvent ? (
            <div className={`mt-4 rounded-2xl border px-4 py-3 text-sm ${palette.error}`}>
              <div className="font-semibold">Pipeline failed at `{failedStage}`</div>
              <div className="mt-1 break-words">{failedMessage}</div>
            </div>
          ) : null}
        </section>

        <section className={`rounded-[2rem] border px-5 py-6 sm:px-6 ${palette.card}`}>
          <div className="mb-5">
            <p className={`text-xs font-semibold uppercase tracking-[0.3em] ${palette.accent}`}>Diagram</p>
            <h2 className={`mt-2 text-2xl font-semibold ${palette.title}`}>Live pipeline status</h2>
          </div>
          <div className={`overflow-hidden rounded-[1.6rem] border ${isDark ? 'border-white/10 bg-slate-950/60' : 'border-slate-200 bg-white'}`}>
            <div style={{ height: '780px', width: '100%' }}>
              <ReactFlow
                nodes={nodes}
                edges={PIPELINE_EDGES}
                fitView
                fitViewOptions={{ padding: 0.12 }}
                proOptions={{ hideAttribution: true }}
                nodesDraggable={false}
                nodesConnectable={false}
                elementsSelectable={false}
                panOnDrag
              >
                <Background gap={24} size={1} color={isDark ? 'rgba(148,163,184,0.18)' : 'rgba(148,163,184,0.28)'} />
                <MiniMap
                  pannable
                  zoomable
                  nodeColor={isDark ? '#0ea5e9' : '#0284c7'}
                  maskColor={isDark ? 'rgba(2,6,23,0.55)' : 'rgba(255,255,255,0.7)'}
                  className={isDark ? '!bg-slate-900 !border !border-white/10' : '!bg-white !border !border-slate-200'}
                />
                <Controls className={isDark ? '!bg-slate-900 !border !border-white/10' : '!bg-white !border !border-slate-200'} />
              </ReactFlow>
            </div>
          </div>
        </section>

        <section className={`rounded-[2rem] border px-5 py-6 sm:px-6 ${palette.card}`}>
          <div className="mb-5">
            <p className={`text-xs font-semibold uppercase tracking-[0.3em] ${palette.accent}`}>Timeline</p>
            <h2 className={`mt-2 text-2xl font-semibold ${palette.title}`}>Real backend events</h2>
          </div>
          {traceEvents.length === 0 ? (
            <div className={`rounded-[1.2rem] border p-4 text-sm ${isDark ? 'border-white/10 bg-white/[0.03] text-slate-300' : 'border-slate-200 bg-white text-slate-600'}`}>
              Select a file from the bucket or upload a new one to see the actual event timeline from `investigation_events`.
            </div>
          ) : (
            <div className="space-y-3">
              {traceEvents.map((event, index) => (
                <div
                  key={`${event.id}-${index}`}
                  className={`rounded-[1.2rem] border p-4 ${isDark ? 'border-white/10 bg-white/[0.03]' : 'border-slate-200 bg-white'}`}
                >
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                    <div className="flex items-center gap-3">
                      <span className={`inline-flex h-8 items-center rounded-full px-3 text-[10px] font-semibold uppercase tracking-[0.18em] ${
                        event.status === 'completed'
                          ? isDark ? 'bg-emerald-500/15 text-emerald-300' : 'bg-emerald-50 text-emerald-700'
                          : event.status === 'failed'
                            ? isDark ? 'bg-red-500/15 text-red-300' : 'bg-red-50 text-red-700'
                            : isDark ? 'bg-cyan-500/15 text-cyan-300' : 'bg-cyan-50 text-cyan-700'
                      }`}>
                        {event.status}
                      </span>
                      <p className={`text-sm font-semibold ${palette.title}`}>{event.event}</p>
                    </div>
                    <p className={`text-xs ${palette.text}`}>{fmtTime(event.created_at)}</p>
                  </div>
                  <div className={`mt-3 flex flex-wrap gap-2 text-[11px] ${palette.text}`}>
                    {event.event_metadata?.stage ? (
                      <span className={`rounded-full border px-2.5 py-1 ${isDark ? 'border-white/10 bg-white/[0.03]' : 'border-slate-200 bg-slate-50'}`}>
                        stage: {event.event_metadata.stage}
                      </span>
                    ) : null}
                    {event.event_metadata?.trace_run_id ? (
                      <span className={`rounded-full border px-2.5 py-1 ${isDark ? 'border-white/10 bg-white/[0.03]' : 'border-slate-200 bg-slate-50'}`}>
                        trace: {String(event.event_metadata.trace_run_id).slice(0, 8)}
                      </span>
                    ) : null}
                    {typeof event.event_metadata?.duration_ms === 'number' ? (
                      <span className={`rounded-full border px-2.5 py-1 ${isDark ? 'border-white/10 bg-white/[0.03]' : 'border-slate-200 bg-slate-50'}`}>
                        duration: {event.event_metadata.duration_ms}ms
                      </span>
                    ) : null}
                  </div>
                  {event.event_metadata && Object.keys(event.event_metadata).length > 0 ? (
                    <pre className={`mt-3 overflow-x-auto rounded-xl border p-3 text-xs leading-6 ${isDark ? 'border-white/10 bg-slate-950/65 text-slate-200' : 'border-slate-200 bg-slate-50 text-slate-800'}`}>
                      <code>{JSON.stringify(event.event_metadata, null, 2)}</code>
                    </pre>
                  ) : null}
                </div>
              ))}
            </div>
          )}
        </section>

        <section className={`rounded-[2rem] border px-5 py-6 sm:px-6 ${palette.card}`}>
          <div className="mb-5">
            <p className={`text-xs font-semibold uppercase tracking-[0.3em] ${palette.accent}`}>Output</p>
            <h2 className={`mt-2 text-2xl font-semibold ${palette.title}`}>File output artifacts</h2>
          </div>
          {traceFile ? (
            <div className="grid gap-5 xl:grid-cols-2">
              <JsonPreview theme={theme} title="File Metadata" data={traceFile} />
              <JsonPreview theme={theme} title="Processing Summary" data={processingSummary} />
              {failedEvent ? <JsonPreview theme={theme} title="Latest Failure" data={failedEvent} /> : null}
              <JsonPreview theme={theme} title="Layout JSON" data={traceLayout || { status: 'not_ready_yet' }} />
              <JsonPreview theme={theme} title="Chunks" data={traceChunks.length > 0 ? traceChunks : { status: 'no_chunks_or_not_ready_yet' }} />
            </div>
          ) : (
            <div className={`rounded-[1.2rem] border p-4 text-sm ${isDark ? 'border-white/10 bg-white/[0.03] text-slate-300' : 'border-slate-200 bg-white text-slate-600'}`}>
              Select a file from the bucket or upload a new one to see its metadata, layout JSON, and chunk output here.
            </div>
          )}
        </section>

        <section className={`rounded-[2rem] border px-5 py-6 sm:px-6 ${palette.card}`}>
          <div className="mb-5">
            <p className={`text-xs font-semibold uppercase tracking-[0.3em] ${palette.accent}`}>Step Order</p>
            <h2 className={`mt-2 text-2xl font-semibold ${palette.title}`}>Full pipeline list</h2>
          </div>
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {PIPELINE_FLOW_STEPS.map((item) => (
              <div
                key={item.step}
                className={`rounded-[1.2rem] border p-4 ${isDark ? 'border-white/10 bg-white/[0.03]' : 'border-slate-200 bg-white'}`}
              >
                <div className="flex items-center gap-3">
                  <span className={`inline-flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold ${isDark ? 'bg-blue-500/14 text-blue-300' : 'bg-blue-50 text-blue-700'}`}>
                    {item.step}
                  </span>
                  <div>
                    <p className={`text-sm font-semibold ${palette.title}`}>{item.title}</p>
                    <p className={`mt-1 text-xs ${palette.text}`}>{item.output}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}

// ---------- MCP Logs Page ----------

// ---------- Dashboard router: dispatches member vs owner dashboard ----------

function DashboardRouter({ theme, onToggleTheme }) {
  const { ctx, isMember, loading } = useTeamContext();
  const palette = themeOptions[theme];

  if (loading || !ctx) {
    return (
      <div className={`min-h-[100dvh] flex items-center justify-center ${palette.app}`}>
        <div className={`text-sm ${palette.muted}`}>Loading workspace...</div>
      </div>
    );
  }

  if (isMember) {
    return <MemberDashboard theme={theme} onToggleTheme={onToggleTheme} />;
  }

  return <DashboardPage theme={theme} onToggleTheme={onToggleTheme} workspaces={ctx?.workspaces} activeWorkspace={ctx?.active_workspace} />;
}

// ---------- Admin panel (private /admin; set per-account Enterprise limits) ----------

const ADMIN_FIELD_LABELS = {
  ...LIMIT_FIELD_LABELS,
  max_users: 'Seats (users)',
  max_storage_bytes: 'Storage (bytes)',
  max_file_size_bytes: 'Max file size (bytes)',
};

function AdminPage({ theme }) {
  const dark = theme === 'dark';
  const [phase, setPhase] = useState('creds'); // 'creds' | 'code' | 'panel'
  const [adminEmail, setAdminEmail] = useState('');
  const [adminKey, setAdminKey] = useState('');
  const [code, setCode] = useState('');
  const [session, setSession] = useState('');
  const [secondsLeft, setSecondsLeft] = useState(0);

  const [custEmail, setCustEmail] = useState('');
  const [account, setAccount] = useState(null);
  const [fields, setFields] = useState({});
  const [plan, setPlan] = useState('business');
  const [subscriptionStatus, setSubscriptionStatus] = useState('active');
  const [limitRequests, setLimitRequests] = useState([]);
  const [enterpriseInquiries, setEnterpriseInquiries] = useState([]);
  const [requestEdits, setRequestEdits] = useState({});
  const [requestStatus, setRequestStatus] = useState('pending');
  const [enterpriseStatus, setEnterpriseStatus] = useState('new');
  const [loading, setLoading] = useState(false);
  const [requestLoading, setRequestLoading] = useState(false);
  const [enterpriseLoading, setEnterpriseLoading] = useState(false);
  const [error, setError] = useState('');
  const [okMsg, setOkMsg] = useState('');

  const page = dark ? 'bg-[#020617] text-slate-100' : 'bg-[#eff5ff] text-slate-900';
  const card = dark ? 'bg-[#0F172A] ring-1 ring-white/10' : 'bg-white ring-1 ring-slate-200';
  const label = dark ? 'text-slate-400' : 'text-slate-500';
  const ghost = dark ? 'text-slate-300 hover:bg-white/5' : 'text-slate-600 hover:bg-slate-100';
  const inputCls = `w-full rounded-lg px-3 py-2 text-sm outline-none ${dark ? 'bg-slate-800 text-slate-100 ring-1 ring-white/10 focus:ring-2 focus:ring-blue-500' : 'bg-slate-50 text-slate-900 ring-1 ring-slate-200 focus:ring-2 focus:ring-blue-500'}`;
  const disabledInputCls = dark ? 'disabled:bg-slate-900 disabled:text-slate-500 disabled:cursor-not-allowed' : 'disabled:bg-slate-100 disabled:text-slate-500 disabled:cursor-not-allowed';
  const customLimitsAllowed = plan === 'business';

  useEffect(() => {
    if (phase !== 'code' || secondsLeft <= 0) return;
    const t = setInterval(() => setSecondsLeft((s) => (s <= 1 ? 0 : s - 1)), 1000);
    return () => clearInterval(t);
  }, [phase, secondsLeft]);

  const buildLimitFields = (data, selectedPlan) => {
    const limitFields = data?.overridable_fields?.length ? data.overridable_fields : Object.keys(ADMIN_FIELD_LABELS);
    const baseLimits = data?.base_plan_limits?.[selectedPlan] || data?.effective_limits || {};
    const override = selectedPlan === 'business' ? (data?.limits_override || {}) : {};
    const init = {};
    limitFields.forEach((f) => {
      const value = override[f] != null ? override[f] : baseLimits[f];
      init[f] = String(value != null ? value : 0);
    });
    return init;
  };

  const selectAccountPlan = (nextPlan, data = account) => {
    setPlan(nextPlan);
    setFields(buildLimitFields(data, nextPlan));
  };

  const hydrateRequestEdits = (items) => {
    const next = {};
    (items || []).forEach((req) => {
      next[req.id] = {
        plan: 'business',
        adminNote: '',
        limits: Object.fromEntries(
          Object.entries(req.requested_limits || {}).map(([key, value]) => [key, String(value)])
        ),
      };
    });
    setRequestEdits(next);
  };

  const loadLimitRequests = async (status = requestStatus) => {
    if (!session) return;
    setRequestLoading(true);
    try {
      const data = await adminApi.listLimitRequests(session, status);
      const items = data.items || [];
      setLimitRequests(items);
      hydrateRequestEdits(items);
    } catch (e) {
      setError(e.message || 'Could not load limit requests.');
      if ((e.message || '').toLowerCase().includes('session')) backToLogin();
    } finally {
      setRequestLoading(false);
    }
  };

  const loadEnterpriseInquiries = async (status = enterpriseStatus) => {
    if (!session) return;
    setEnterpriseLoading(true);
    try {
      const data = await adminApi.listEnterpriseInquiries(session, status);
      setEnterpriseInquiries(data.items || []);
    } catch (e) {
      setError(e.message || 'Could not load Enterprise requests.');
      if ((e.message || '').toLowerCase().includes('session')) backToLogin();
    } finally {
      setEnterpriseLoading(false);
    }
  };

  useEffect(() => {
    if (phase === 'panel' && session) {
      loadLimitRequests(requestStatus);
      loadEnterpriseInquiries(enterpriseStatus);
    }
  }, [phase, session, requestStatus, enterpriseStatus]);

  const sendCode = async () => {
    setError(''); setOkMsg(''); setLoading(true);
    try {
      const data = await adminApi.requestCode(adminEmail.trim(), adminKey);
      setPhase('code');
      setCode('');
      setAdminKey('');
      setSecondsLeft(data.expires_in || 60);
      setOkMsg('Code sent to ' + (data.sent_to || 'your email') + ' — expires in 60s.');
    } catch (e) {
      setError(e.message || 'Could not send code.');
    } finally {
      setLoading(false);
    }
  };

  const verifyCode = async () => {
    setError(''); setOkMsg(''); setLoading(true);
    try {
      const data = await adminApi.verifyCode(code.trim());
      setSession(data.admin_session);
      setPhase('panel');
    } catch (e) {
      setError(e.message || 'Verification failed.');
    } finally {
      setLoading(false);
    }
  };

  const backToLogin = () => {
    setPhase('creds'); setSession(''); setCode(''); setAdminKey(''); setAccount(null); setLimitRequests([]); setEnterpriseInquiries([]); setRequestEdits({}); setError('');
  };

  const lookup = async () => {
    setError(''); setOkMsg(''); setAccount(null); setLoading(true);
    try {
      const data = await adminApi.lookup(custEmail.trim(), session);
      const nextPlan = data.plan || data.effective_plan || 'business';
      setAccount(data);
      setPlan(nextPlan);
      setSubscriptionStatus(data.subscription_status || (data.locked ? 'cancelled' : 'active'));
      setFields(buildLimitFields(data, nextPlan));
    } catch (e) {
      setError(e.message || 'Lookup failed.');
      if ((e.message || '').toLowerCase().includes('session')) backToLogin();
    } finally {
      setLoading(false);
    }
  };

  const apply = async () => {
    setError(''); setOkMsg(''); setLoading(true);
    try {
      const override = {};
      if (customLimitsAllowed) {
        Object.entries(fields).forEach(([k, v]) => {
          const n = parseInt(v, 10);
          if (!Number.isNaN(n) && n >= 0) override[k] = n;
        });
      }
      const data = await adminApi.setPlan(custEmail.trim(), plan, subscriptionStatus, override, session);
      const nextPlan = data.plan || plan;
      setAccount(data);
      setPlan(nextPlan);
      setSubscriptionStatus(data.subscription_status || (data.locked ? 'cancelled' : 'active'));
      setFields(buildLimitFields(data, nextPlan));
      setOkMsg('Saved — plan/status applied to ' + data.email + '.');
    } catch (e) {
      setError(e.message || 'Apply failed.');
      if ((e.message || '').toLowerCase().includes('session')) backToLogin();
    } finally {
      setLoading(false);
    }
  };

  const updateRequestLimit = (requestId, key, value) => {
    setRequestEdits((prev) => ({
      ...prev,
      [requestId]: {
        ...(prev[requestId] || {}),
        limits: {
          ...((prev[requestId] || {}).limits || {}),
          [key]: value,
        },
      },
    }));
  };

  const updateRequestMeta = (requestId, key, value) => {
    setRequestEdits((prev) => ({
      ...prev,
      [requestId]: {
        ...(prev[requestId] || {}),
        [key]: value,
      },
    }));
  };

  const applyLimitRequest = async (req) => {
    const edit = requestEdits[req.id] || {};
    const override = {};
    Object.entries(edit.limits || {}).forEach(([k, v]) => {
      const n = parseInt(v, 10);
      if (!Number.isNaN(n) && n >= 0) override[k] = n;
    });
    setError(''); setOkMsg(''); setRequestLoading(true);
    try {
      await adminApi.applyLimitRequest(req.id, edit.plan || 'business', override, edit.adminNote || '', session);
      setOkMsg('Request approved and limits applied.');
      await loadLimitRequests(requestStatus);
    } catch (e) {
      setError(e.message || 'Could not apply request.');
      if ((e.message || '').toLowerCase().includes('session')) backToLogin();
    } finally {
      setRequestLoading(false);
    }
  };

  const rejectLimitRequest = async (req) => {
    const edit = requestEdits[req.id] || {};
    setError(''); setOkMsg(''); setRequestLoading(true);
    try {
      await adminApi.rejectLimitRequest(req.id, edit.adminNote || '', session);
      setOkMsg('Request marked reviewed.');
      await loadLimitRequests(requestStatus);
    } catch (e) {
      setError(e.message || 'Could not reject request.');
      if ((e.message || '').toLowerCase().includes('session')) backToLogin();
    } finally {
      setRequestLoading(false);
    }
  };

  return (
    <div className={`min-h-[100dvh] ${page}`}>
      <div className="mx-auto max-w-3xl px-6 py-12">
        <h1 className="text-xl font-semibold">Admin — account limits</h1>
        <p className={`mt-1 text-sm ${label}`}>Secure access: admin email + key, then a 6-digit code sent to you.</p>

        {error && <p className="mt-4 rounded-lg bg-red-500/10 px-4 py-2 text-sm text-red-500">{error}</p>}
        {okMsg && <p className="mt-4 rounded-lg bg-emerald-500/10 px-4 py-2 text-sm text-emerald-500">{okMsg}</p>}

        {phase === 'creds' && (
          <div className={`mt-6 rounded-2xl p-5 ${card}`}>
            <label className={`text-xs font-medium ${label}`}>Admin email</label>
            <input value={adminEmail} onChange={(e) => setAdminEmail(e.target.value)} placeholder="you@youremail.com" className={`mt-1 ${inputCls}`} />
            <label className={`mt-4 block text-xs font-medium ${label}`}>Admin key</label>
            <input type="password" value={adminKey} onChange={(e) => setAdminKey(e.target.value)} placeholder="Admin key" className={`mt-1 ${inputCls}`} onKeyDown={(e) => e.key === 'Enter' && adminEmail && adminKey && sendCode()} />
            <button onClick={sendCode} disabled={loading || !adminEmail || !adminKey} className="mt-5 w-full rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-500 disabled:opacity-50">
              {loading ? 'Sending…' : 'Send 6-digit code'}
            </button>
          </div>
        )}

        {phase === 'code' && (
          <div className={`mt-6 rounded-2xl p-5 ${card}`}>
            <label className={`text-xs font-medium ${label}`}>Enter the 6-digit code {secondsLeft > 0 ? `(${secondsLeft}s left)` : '(expired — resend)'}</label>
            <input value={code} onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))} placeholder="000000" inputMode="numeric" className={`mt-1 text-center text-lg tracking-[0.5em] ${inputCls}`} onKeyDown={(e) => e.key === 'Enter' && code.length === 6 && verifyCode()} />
            <div className="mt-5 flex gap-2">
              <button onClick={verifyCode} disabled={loading || code.length !== 6 || secondsLeft <= 0} className="flex-1 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-500 disabled:opacity-50">
                {loading ? 'Verifying…' : 'Verify'}
              </button>
              <button onClick={sendCode} disabled={loading} className={`flex-none rounded-lg px-4 py-2.5 text-sm font-medium ${ghost}`}>
                Resend
              </button>
            </div>
            <button onClick={backToLogin} className={`mt-3 text-xs ${label} hover:underline`}>← back</button>
          </div>
        )}

        {phase === 'panel' && (
          <>
            <DemoAdminPanel session={session} dark={dark} />

            <div className={`mt-6 rounded-2xl p-5 ${card}`}>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm font-semibold">Enterprise requests</p>
                  <p className={`mt-1 text-xs ${label}`}>Contact-sales forms submitted by logged-in users.</p>
                </div>
                <div className="flex gap-2">
                  {['new', 'all'].map((status) => (
                    <button
                      key={status}
                      type="button"
                      onClick={() => setEnterpriseStatus(status)}
                      className={`rounded-lg px-3 py-1.5 text-xs font-semibold ${enterpriseStatus === status ? 'bg-blue-600 text-white' : ghost}`}
                    >
                      {status === 'new' ? 'New' : 'All'}
                    </button>
                  ))}
                  <button type="button" onClick={() => loadEnterpriseInquiries(enterpriseStatus)} disabled={enterpriseLoading} className={`rounded-lg px-3 py-1.5 text-xs font-semibold ${ghost}`}>
                    Refresh
                  </button>
                </div>
              </div>

              <div className="mt-4 space-y-3">
                {enterpriseLoading && enterpriseInquiries.length === 0 ? (
                  <p className={`py-4 text-center text-sm ${label}`}>Loading Enterprise requests...</p>
                ) : enterpriseInquiries.length === 0 ? (
                  <p className={`py-4 text-center text-sm ${label}`}>No Enterprise requests.</p>
                ) : (
                  enterpriseInquiries.map((req) => {
                    const detailRows = [
                      ['Request ID', req.id],
                      ['User ID', req.requester?.user_id],
                      ['Company', req.company],
                      ['Role', req.role],
                      ['Team size', req.team_size],
                      ['Document volume', req.doc_volume],
                      ['Use case', req.use_case],
                      ['Meeting link', req.meeting_url],
                    ];
                    return (
                      <div key={req.id} className={`rounded-xl border p-4 ${dark ? 'border-white/10 bg-slate-900/60' : 'border-slate-200 bg-slate-50'}`}>
                        <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                          <div>
                            <p className="text-sm font-semibold">{req.requester?.name || req.requester_email || 'Unknown user'}</p>
                            <p className={`mt-1 text-xs ${label}`}>
                              {req.requester_email || 'no email'} · {req.created_at ? new Date(req.created_at).toLocaleString() : 'unknown time'}
                            </p>
                          </div>
                          <span className={`w-fit rounded-full px-2.5 py-1 text-xs font-medium ${req.status === 'new' ? 'bg-blue-500/10 text-blue-500' : 'bg-slate-500/10 text-slate-500'}`}>
                            {req.status}
                          </span>
                        </div>

                        <div className="mt-3 grid gap-2 sm:grid-cols-2">
                          {detailRows.map(([name, value]) => (
                            <div key={name} className={`rounded-lg px-3 py-2 ${dark ? 'bg-white/5' : 'bg-white'}`}>
                              <p className={`text-xs ${label}`}>{name}</p>
                              {name === 'Meeting link' && value ? (
                                <a href={value} target="_blank" rel="noreferrer" className="mt-1 block break-words text-sm font-semibold text-blue-500 hover:underline">
                                  {value}
                                </a>
                              ) : (
                                <p className="mt-1 whitespace-pre-wrap break-words text-sm font-semibold">{value || '—'}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>

            <div className={`mt-6 rounded-2xl p-5 ${card}`}>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm font-semibold">Limit increase requests</p>
                  <p className={`mt-1 text-xs ${label}`}>Requests from users who hit plan limits.</p>
                </div>
                <div className="flex gap-2">
                  {['pending', 'all'].map((status) => (
                    <button
                      key={status}
                      type="button"
                      onClick={() => setRequestStatus(status)}
                      className={`rounded-lg px-3 py-1.5 text-xs font-semibold ${requestStatus === status ? 'bg-blue-600 text-white' : ghost}`}
                    >
                      {status === 'pending' ? 'Pending' : 'All'}
                    </button>
                  ))}
                  <button type="button" onClick={() => loadLimitRequests(requestStatus)} disabled={requestLoading} className={`rounded-lg px-3 py-1.5 text-xs font-semibold ${ghost}`}>
                    Refresh
                  </button>
                </div>
              </div>

              <div className="mt-4 space-y-3">
                {requestLoading && limitRequests.length === 0 ? (
                  <p className={`py-4 text-center text-sm ${label}`}>Loading requests...</p>
                ) : limitRequests.length === 0 ? (
                  <p className={`py-4 text-center text-sm ${label}`}>No requests.</p>
                ) : (
                  limitRequests.map((req) => {
                    const edit = requestEdits[req.id] || { limits: {}, plan: 'business', adminNote: '' };
                    const requestedEntries = Object.entries(req.requested_limits || {});
                    return (
                      <div key={req.id} className={`rounded-xl border p-4 ${dark ? 'border-white/10 bg-slate-900/60' : 'border-slate-200 bg-slate-50'}`}>
                        <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                          <div>
                            <p className="text-sm font-semibold">{req.requester?.name || req.requester_email}</p>
                            <p className={`mt-1 text-xs ${label}`}>
                              {req.requester_email} · workspace {req.owner?.email || 'unknown'} · {req.status}
                            </p>
                          </div>
                          <span className={`w-fit rounded-full px-2.5 py-1 text-xs font-medium ${req.status === 'pending' ? 'bg-amber-500/10 text-amber-500' : req.status === 'approved' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-slate-500/10 text-slate-500'}`}>
                            {req.status}
                          </span>
                        </div>

                        {req.trigger_message && <p className={`mt-3 text-xs ${label}`}>{req.trigger_message}</p>}
                        {req.user_note && <p className={`mt-2 rounded-lg px-3 py-2 text-xs ${dark ? 'bg-white/5 text-slate-300' : 'bg-white text-slate-600'}`}>User note: {req.user_note}</p>}

                        <div className="mt-3 grid gap-2 sm:grid-cols-2">
                          {requestedEntries.map(([key, value]) => (
                            <div key={key} className={`rounded-lg px-3 py-2 ${dark ? 'bg-white/5' : 'bg-white'}`}>
                              <p className={`text-xs ${label}`}>{ADMIN_FIELD_LABELS[key] || key}</p>
                              <p className="mt-1 text-sm font-semibold">
                                Requested {fmtLimitValue(key, value)}
                                {req.current_usage?.[key] != null && (
                                  <span className={`ml-2 text-xs font-normal ${label}`}>
                                    used {fmtLimitValue(key, req.current_usage[key])}
                                  </span>
                                )}
                              </p>
                            </div>
                          ))}
                        </div>

                        {req.status === 'pending' ? (
                          <>
                            <label className={`mt-4 block text-xs font-medium ${label}`}>Plan to apply</label>
                            <select value={edit.plan || 'business'} onChange={(e) => updateRequestMeta(req.id, 'plan', e.target.value)} className={`mt-1 ${inputCls}`}>
                              <option value="individual">Individual</option>
                              <option value="team">Team</option>
                              <option value="business">Enterprise (custom)</option>
                            </select>

                            <p className={`mt-4 text-xs font-medium ${label}`}>Limits to apply</p>
                            <div className="mt-2 grid grid-cols-2 gap-3">
                              {requestedEntries.map(([key]) => (
                                <div key={key}>
                                  <label className={`text-xs ${label}`}>{ADMIN_FIELD_LABELS[key] || key}</label>
                                  <input
                                    type="number"
                                    min="0"
                                    value={(edit.limits || {})[key] || ''}
                                    onChange={(e) => updateRequestLimit(req.id, key, e.target.value)}
                                    className={`mt-1 ${inputCls}`}
                                  />
                                </div>
                              ))}
                            </div>

                            <label className={`mt-4 block text-xs font-medium ${label}`}>Admin note</label>
                            <textarea
                              value={edit.adminNote || ''}
                              onChange={(e) => updateRequestMeta(req.id, 'adminNote', e.target.value)}
                              rows={3}
                              placeholder="Optional note shown to the user"
                              className={`mt-1 ${inputCls}`}
                            />
                            <div className="mt-4 flex justify-end gap-2">
                              <button onClick={() => rejectLimitRequest(req)} disabled={requestLoading} className={`rounded-lg px-4 py-2 text-sm font-semibold ${ghost}`}>
                                Reject
                              </button>
                              <button onClick={() => applyLimitRequest(req)} disabled={requestLoading} className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-500 disabled:opacity-50">
                                Apply limits
                              </button>
                            </div>
                          </>
                        ) : req.admin_note ? (
                          <p className={`mt-3 rounded-lg px-3 py-2 text-xs ${dark ? 'bg-white/5 text-slate-300' : 'bg-white text-slate-600'}`}>Admin note: {req.admin_note}</p>
                        ) : null}
                      </div>
                    );
                  })
                )}
              </div>
            </div>

            <div className={`mt-6 rounded-2xl p-5 ${card}`}>
              <label className={`text-xs font-medium ${label}`}>Customer email</label>
              <div className="mt-1 flex gap-2">
                <input value={custEmail} onChange={(e) => setCustEmail(e.target.value)} placeholder="customer@company.com" className={inputCls} onKeyDown={(e) => e.key === 'Enter' && lookup()} />
                <button onClick={lookup} disabled={loading || !custEmail} className="flex-none rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-500 disabled:opacity-50">
                  {loading ? '…' : 'Look up'}
                </button>
              </div>
            </div>

            {account && (
              <div className={`mt-6 rounded-2xl p-5 ${card}`}>
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-sm font-semibold">{account.name || account.email}</p>
                    <p className={`text-xs ${label}`}>{account.email}</p>
                  </div>
                  <span className={`flex-none rounded-full px-2.5 py-1 text-xs font-medium ${dark ? 'bg-slate-800 text-slate-300' : 'bg-slate-100 text-slate-600'}`}>
                    {account.effective_plan}{account.subscription_status ? ` · ${account.subscription_status}` : ''}{account.is_trial ? ' · trial' : ''}{account.locked ? ' · locked' : ''}
                  </span>
                </div>

                <p className={`mt-4 text-xs ${label}`}>
                  Usage: {account.usage.documents} docs · {account.usage.images} visuals · {account.usage.pages} pages · {account.usage.buckets} buckets
                </p>

                <div className="mt-5 grid gap-3 sm:grid-cols-2">
                  <label className="block">
                    <span className={`text-xs font-medium ${label}`}>Plan</span>
                    <select value={plan} onChange={(e) => selectAccountPlan(e.target.value)} className={`mt-1 ${inputCls}`}>
                      <option value="individual">Individual</option>
                      <option value="team">Team</option>
                      <option value="business">Enterprise (custom)</option>
                    </select>
                  </label>
                  <label className="block">
                    <span className={`text-xs font-medium ${label}`}>Status</span>
                    <select value={subscriptionStatus} onChange={(e) => setSubscriptionStatus(e.target.value)} className={`mt-1 ${inputCls}`}>
                      <option value="active">Active</option>
                      <option value="cancelled">Cancelled / locked</option>
                      <option value="past_due">Past due / locked</option>
                    </select>
                  </label>
                </div>

                <p className={`mt-5 text-xs font-medium ${label}`}>
                  {customLimitsAllowed ? 'Limits: edit and apply custom Enterprise values' : 'Limits: fixed for the selected Individual/Team plan'}
                </p>
                <div className="mt-2 grid grid-cols-2 gap-3">
                  {Object.keys(fields).map((f) => (
                    <div key={f}>
                      <label className={`text-xs ${label}`}>{ADMIN_FIELD_LABELS[f] || f}</label>
                      <input
                        type="number"
                        min="0"
                        value={fields[f]}
                        disabled={!customLimitsAllowed}
                        onChange={(e) => setFields((s) => ({ ...s, [f]: e.target.value }))}
                        className={`mt-1 ${inputCls} ${disabledInputCls}`}
                      />
                    </div>
                  ))}
                </div>

                <button onClick={apply} disabled={loading} className="mt-6 w-full rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-500 disabled:opacity-50">
                  {loading ? 'Applying…' : 'Apply to account'}
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

// ---------- Enterprise contact page (login-gated; 5 questions + meeting link) ----------

function EnterpriseContactPage({ theme }) {
  const dark = theme === 'dark';
  const loggedIn = typeof window !== 'undefined' && !!sessionStorage.getItem('access_token');
  const [form, setForm] = useState({ company: '', role: '', team_size: '', doc_volume: '', use_case: '', meeting_url: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [done, setDone] = useState(false);

  const page = dark ? 'bg-[#020617] text-slate-100' : 'bg-[#eff5ff] text-slate-900';
  const card = dark ? 'bg-[#0F172A] ring-1 ring-white/10' : 'bg-white ring-1 ring-slate-200';
  const muted = dark ? 'text-slate-400' : 'text-slate-500';
  const inputCls = `mt-1 w-full rounded-lg px-3 py-2 text-sm outline-none ${dark ? 'bg-slate-800 text-slate-100 ring-1 ring-white/10 focus:ring-2 focus:ring-blue-500' : 'bg-slate-50 text-slate-900 ring-1 ring-slate-200 focus:ring-2 focus:ring-blue-500'}`;
  const set = (k) => (e) => setForm((s) => ({ ...s, [k]: e.target.value }));
  const canSubmit = form.company.trim() && form.use_case.trim();

  const submit = async () => {
    setError(''); setLoading(true);
    try {
      await enterpriseApi.contact(form);
      setDone(true);
    } catch (e) {
      setError(e.message || 'Could not send. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`min-h-[100dvh] ${page}`}>
      <div className="mx-auto max-w-xl px-6 py-14">
        <a href="/" className={`text-sm ${muted} hover:underline`}>← Back to home</a>
        <h1 className="mt-4 text-2xl font-semibold">Talk to us about Enterprise</h1>
        <p className={`mt-2 text-sm ${muted}`}>Custom limits, onboarding, and pricing for your team. Tell us about your needs and we'll be in touch.</p>

        {!loggedIn ? (
          <div className={`mt-8 rounded-2xl p-6 text-center ${card}`}>
            <p className="text-sm">Please log in to contact our team.</p>
            <a href="/login" className="mt-4 inline-block rounded-full bg-blue-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-blue-500">Log in to continue</a>
          </div>
        ) : done ? (
          <div className={`mt-8 rounded-2xl p-8 text-center ${card}`}>
            <div className="text-3xl">✅</div>
            <h2 className="mt-3 text-lg font-semibold">We'll be in contact shortly</h2>
            <p className={`mt-2 text-sm ${muted}`}>Thanks — our team will reach out by email as soon as possible.{form.meeting_url.trim() ? " We'll use your booking link to schedule a call." : ''}</p>
            <a href="/dashboard" className="mt-5 inline-block rounded-full bg-blue-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-blue-500">Back to dashboard</a>
          </div>
        ) : (
          <div className={`mt-8 rounded-2xl p-6 ${card}`}>
            {error && <p className="mb-4 rounded-lg bg-red-500/10 px-4 py-2 text-sm text-red-500">{error}</p>}
            <div className="space-y-4">
              <div>
                <label className={`text-xs font-medium ${muted}`}>Company or website <span className="text-red-400">*</span></label>
                <input value={form.company} onChange={set('company')} placeholder="Acme Inc. / acme.com" className={inputCls} />
              </div>
              <div>
                <label className={`text-xs font-medium ${muted}`}>Your role</label>
                <input value={form.role} onChange={set('role')} placeholder="e.g. Head of Operations" className={inputCls} />
              </div>
              <div>
                <label className={`text-xs font-medium ${muted}`}>How many people will use it?</label>
                <input value={form.team_size} onChange={set('team_size')} placeholder="e.g. 25 users" className={inputCls} />
              </div>
              <div>
                <label className={`text-xs font-medium ${muted}`}>Roughly how many documents?</label>
                <input value={form.doc_volume} onChange={set('doc_volume')} placeholder="e.g. 10,000 PDFs" className={inputCls} />
              </div>
              <div>
                <label className={`text-xs font-medium ${muted}`}>What do you want to use AIveilix for? <span className="text-red-400">*</span></label>
                <textarea value={form.use_case} onChange={set('use_case')} rows={3} placeholder="Your use case and why you need it." className={inputCls} />
              </div>
              <div>
                <label className={`text-xs font-medium ${muted}`}>Google Calendar / meeting link (optional)</label>
                <input value={form.meeting_url} onChange={set('meeting_url')} placeholder="https://calendar.app.google/… or Calendly link" className={inputCls} />
                <p className={`mt-1 text-xs ${muted}`}>Share a booking link and we'll grab a slot to call you.</p>
              </div>
            </div>
            <button onClick={submit} disabled={loading || !canSubmit} className="mt-6 w-full rounded-full bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-500 disabled:opacity-50">
              {loading ? 'Sending…' : 'Send & request contact'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// ---------- Upgrade modal (global; fires on any HTTP 402 limit hit) ----------

function UpgradeModal({ theme }) {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [step, setStep] = useState('ask');
  const [planData, setPlanData] = useState(null);
  const [planLoading, setPlanLoading] = useState(false);
  const [limitDraft, setLimitDraft] = useState({});
  const [note, setNote] = useState('');
  const [requesting, setRequesting] = useState(false);
  const [requested, setRequested] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const handler = async (e) => {
      const eventPlan = e.detail?.planData || null;
      setMessage((e.detail && e.detail.message) || "You've reached a plan limit on your current plan.");
      setStep('ask');
      setPlanData(eventPlan);
      setLimitDraft({});
      setNote('');
      setError('');
      setRequested(false);
      setOpen(true);
      setPlanLoading(true);
      try {
        const data = await billingApi.getPlan();
        setPlanData(data);
      } catch (err) {
        setError(err.message || 'Could not load your billing plan.');
      } finally {
        setPlanLoading(false);
      }
    };
    window.addEventListener('aiveilix:limit-hit', handler);
    return () => window.removeEventListener('aiveilix:limit-hit', handler);
  }, []);

  if (!open) return null;

  const dark = theme === 'dark';
  const card = dark ? 'bg-[#0F172A] text-slate-100 ring-1 ring-white/10' : 'bg-white text-slate-900 ring-1 ring-slate-200';
  const muted = dark ? 'text-slate-400' : 'text-slate-500';
  const ghost = dark ? 'text-slate-300 hover:bg-white/5' : 'text-slate-600 hover:bg-slate-100';
  const inputCls = `w-full rounded-lg px-3 py-2 text-sm outline-none ${dark ? 'bg-slate-800 text-slate-100 ring-1 ring-white/10 focus:ring-2 focus:ring-blue-500' : 'bg-slate-50 text-slate-900 ring-1 ring-slate-200 focus:ring-2 focus:ring-blue-500'}`;
  const planKey = planData?.plan;
  const isEnterprise = planKey === 'business';
  const isTeam = planKey === 'team';
  const isIndividual = planKey === 'individual' || planKey === 'pro' || planKey === 'locked' || (!planKey && !isEnterprise);
  const modalFields = [
    { key: 'max_documents', label: 'Documents', placeholder: '500' },
    { key: 'max_pages', label: 'Pages', placeholder: '10000' },
    { key: 'max_storage_bytes', label: 'Storage (GB)', placeholder: '50' },
    { key: 'max_chat_messages', label: 'AI chats / month', placeholder: '5000' },
  ];

  const requestUpgrade = async () => {
    setError('');
    const requestedLimits = {};
    modalFields.forEach((field) => {
      const raw = String(limitDraft[field.key] || '').trim();
      if (!raw) return;
      const parsed = field.key === 'max_storage_bytes' ? Number.parseFloat(raw) : Number.parseInt(raw, 10);
      if (Number.isNaN(parsed) || parsed <= 0) return;
      requestedLimits[field.key] = field.key === 'max_storage_bytes'
        ? Math.round(parsed * 1024 * 1024 * 1024)
        : parsed;
    });
    if (Object.keys(requestedLimits).length === 0) {
      setError('Enter at least one requested limit.');
      return;
    }
    setRequesting(true);
    try {
      await billingApi.requestLimitIncrease(requestedLimits, note, message);
      setRequested(true);
    } catch (e) {
      setError(e.message || 'Could not send request.');
    } finally {
      setRequesting(false);
    }
  };

  const startCheckout = async (targetPlan) => {
    setError('');
    setRequesting(true);
    try {
      const { url } = await billingApi.createCheckout(targetPlan);
      if (url) window.location.href = url;
      else setError('Could not start checkout.');
    } catch (e) {
      setError(e.message || 'Could not start checkout.');
    } finally {
      setRequesting(false);
    }
  };

  const goEnterprise = () => {
    window.location.href = '/enterprise-contact';
  };

  return (
    <div
      className="fixed inset-0 z-[200] flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
      onClick={() => setOpen(false)}
    >
      <div className={`w-full max-w-md rounded-2xl p-6 shadow-2xl ${card}`} onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center gap-2">
          <span className="text-xl">!</span>
          <h3 className="text-lg font-semibold">You've hit a plan limit</h3>
        </div>
        <p className="mt-3 text-sm">{message}</p>
        {error && <p className="mt-3 rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-500">{error}</p>}
        {planLoading ? (
          <p className={`mt-4 text-sm ${muted}`}>Checking your current plan...</p>
        ) : !isEnterprise ? (
          <>
            <p className={`mt-3 text-sm ${muted}`}>
              {isTeam
                ? 'Team has fixed limits. Move to Enterprise for custom limits and higher capacity.'
                : 'Individual has fixed limits. Upgrade to Team for higher limits, or choose Enterprise for custom limits.'}
            </p>
            <div className="mt-5 flex flex-wrap justify-end gap-3">
              <button onClick={() => setOpen(false)} disabled={requesting} className={`rounded-full px-4 py-2 text-sm font-medium ${ghost}`}>
                Not now
              </button>
              {isIndividual && (
                <button
                  onClick={() => startCheckout('team')}
                  disabled={requesting}
                  className="rounded-full bg-blue-600 px-5 py-2 text-sm font-semibold text-white hover:bg-blue-500 disabled:opacity-60"
                >
                  {requesting ? 'Opening...' : 'Upgrade to Team'}
                </button>
              )}
              <button
                onClick={goEnterprise}
                disabled={requesting}
                className={`rounded-full px-5 py-2 text-sm font-semibold ${dark ? 'bg-white/10 text-slate-100 hover:bg-white/15' : 'bg-slate-100 text-slate-800 hover:bg-slate-200'}`}
              >
                Enterprise
              </button>
            </div>
          </>
        ) : requested ? (
          <>
            <p className={`mt-4 text-sm ${muted}`}>Request sent. The admin team was notified and will review the requested limits.</p>
            <div className="mt-5 flex justify-end gap-3">
              <button
                onClick={() => setOpen(false)}
                className="rounded-full bg-blue-600 px-5 py-2 text-sm font-semibold text-white hover:bg-blue-500 disabled:opacity-60"
              >
                Done
              </button>
            </div>
          </>
        ) : step === 'ask' ? (
          <>
            <p className={`mt-3 text-sm ${muted}`}>Do you want to request higher limits from the admin team?</p>
            <div className="mt-5 flex justify-end gap-3">
              <button onClick={() => setOpen(false)} className={`rounded-full px-4 py-2 text-sm font-medium ${ghost}`}>
                Not now
              </button>
              <button
                onClick={() => setStep('form')}
                className="rounded-full bg-blue-600 px-5 py-2 text-sm font-semibold text-white hover:bg-blue-500"
              >
                Yes, request more
              </button>
            </div>
          </>
        ) : (
          <>
            <div className="mt-4 grid grid-cols-2 gap-3">
              {modalFields.map((field) => (
                <label key={field.key} className="block">
                  <span className={`mb-1 block text-xs font-medium ${muted}`}>{field.label}</span>
                  <input
                    type="number"
                    min="0"
                    value={limitDraft[field.key] || ''}
                    onChange={(e) => setLimitDraft((prev) => ({ ...prev, [field.key]: e.target.value }))}
                    placeholder={field.placeholder}
                    className={inputCls}
                  />
                </label>
              ))}
            </div>
            <label className="mt-4 block">
              <span className={`mb-1 block text-xs font-medium ${muted}`}>Note for admin</span>
              <textarea
                value={note}
                onChange={(e) => setNote(e.target.value)}
                rows={3}
                placeholder="Why do you need more capacity?"
                className={inputCls}
              />
            </label>
            <div className="mt-5 flex justify-end gap-3">
              <button onClick={() => setStep('ask')} disabled={requesting} className={`rounded-full px-4 py-2 text-sm font-medium ${ghost}`}>
                Back
              </button>
              <button
                onClick={requestUpgrade}
                disabled={requesting}
                className="rounded-full bg-blue-600 px-5 py-2 text-sm font-semibold text-white hover:bg-blue-500 disabled:opacity-60"
              >
                {requesting ? 'Sending...' : 'Send request'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

// ---------- App ----------

export default function App() {
  const [theme, setTheme] = useState(getInitialTheme);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.documentElement.style.backgroundColor = theme === 'dark' ? '#020617' : '#eff5ff';
    window.localStorage.setItem('aiveilix-theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme((t) => (t === 'dark' ? 'light' : 'dark'));
  const publicTheme = 'light';

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage theme={publicTheme} />} />
        <Route path="/v2" element={<LandingPageV2 theme={publicTheme} />} />
        <Route path="/connect/:tool" element={<ConnectGuide theme={theme} onToggleTheme={toggleTheme} />} />
        <Route path="/login" element={<LoginPage theme={publicTheme} />} />
        <Route path="/signup" element={<SignupPage theme={publicTheme} />} />
        <Route path="/oauth/callback" element={<OAuthCallbackPage theme={publicTheme} />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage theme={publicTheme} />} />
        <Route path="/confirm-email" element={<ConfirmEmailPage theme={publicTheme} />} />
        <Route path="/verify-email" element={<VerifyEmailPage theme={publicTheme} />} />
        <Route path="/onboarding" element={<OnboardingPage theme={theme} onToggleTheme={toggleTheme} />} />
        <Route path="/dashboard" element={<DashboardRouter theme={theme} onToggleTheme={toggleTheme} />} />
        <Route path="/bucket/:bucketId" element={<BucketPage theme={theme} onToggleTheme={toggleTheme} />} />
        <Route path="/temp-pipeline" element={<TempPipelinePage theme={theme} onToggleTheme={toggleTheme} />} />
        <Route path="/privacy-policy" element={<PrivacyPolicyPage theme={theme} onToggleTheme={toggleTheme} />} />
        <Route path="/terms" element={<TermsPage theme={theme} onToggleTheme={toggleTheme} />} />
        <Route path="/tokusho" element={<TokushoPage theme={theme} onToggleTheme={toggleTheme} />} />
        <Route path="/docs" element={<DocsPage theme={theme} onToggleTheme={toggleTheme} />} />
        <Route path="/admin" element={<AdminPage theme={theme} />} />
        <Route path="/enterprise-contact" element={<EnterpriseContactPage theme={theme} />} />
        <Route path="/invite/:token" element={<InviteAcceptPage />} />
        <Route path="/try/invite/:token" element={<DemoInvitePage />} />
        <Route path="/try/:slug" element={<DemoPage />} />
        <Route path="*" element={<NotFoundPage theme={theme} onToggleTheme={toggleTheme} />} />
      </Routes>
      <TeamRoleBanner />
      <UpgradeModal theme={theme} />
    </BrowserRouter>
  );
}
