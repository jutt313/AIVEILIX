import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  AnimatedBeam, AnimatedGridPattern, BackgroundBeams, BentoGrid, BentoGridItem,
  BlurFade, BorderBeam, CardHoverSpotlight, ContainerScroll, GradientText,
  Marquee, ShimmerButton, Spotlight,
} from './landing-components';
import { TOOLS } from './brand-logos';
import { motion, AnimatePresence } from 'framer-motion';
import { billingApi, dashboardApi } from './api/auth';

/* ─────────────────────────── Inline SVG icons ──────────────────── */
function Icon({ name, className }) {
  const c = { className: className || 'h-5 w-5', viewBox: '0 0 24 24', fill: 'none', strokeWidth: 1.6, stroke: 'currentColor', strokeLinecap: 'round', strokeLinejoin: 'round' };
  switch (name) {
    case 'folder':    return <svg {...c}><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z"/></svg>;
    case 'chat':      return <svg {...c}><path d="M4 5h16v11H7l-3 3V5Z"/><path d="M8 10h8M8 13h5"/></svg>;
    case 'link':      return <svg {...c}><path d="M10 14a4 4 0 0 0 5.66 0l3-3a4 4 0 1 0-5.66-5.66l-1.5 1.5"/><path d="M14 10a4 4 0 0 0-5.66 0l-3 3a4 4 0 1 0 5.66 5.66l1.5-1.5"/></svg>;
    case 'web':       return <svg {...c}><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/></svg>;
    case 'mic':       return <svg {...c}><rect x="9" y="3" width="6" height="12" rx="3"/><path d="M5 12a7 7 0 0 0 14 0M12 19v3"/></svg>;
    case 'lock':      return <svg {...c}><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V8a4 4 0 1 1 8 0v3"/></svg>;
    case 'arrow':     return <svg {...c}><path d="M5 12h14M13 6l6 6-6 6"/></svg>;
    case 'check':     return <svg {...c}><path d="M5 12l4 4 10-10"/></svg>;
    case 'sparkle':   return <svg {...c}><path d="M12 3l1.6 4.8L18 9.4l-4.4 1.6L12 16l-1.6-5L6 9.4l4.4-1.6L12 3Z"/></svg>;
    case 'at':        return <svg {...c}><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3.5"/><path d="M15.5 12V14a2.5 2.5 0 0 0 5 0v-2a9 9 0 1 0-4 7"/></svg>;
    case 'paperclip': return <svg {...c}><path d="M21 12.5l-9 9a5.5 5.5 0 0 1-7.78-7.78l9.55-9.55a3.5 3.5 0 0 1 4.95 4.95L9.16 18.7a1.5 1.5 0 0 1-2.12-2.12L15 8.5"/></svg>;
    case 'flash':     return <svg {...c}><path d="M13 2L4 14h7l-1 8 9-12h-7l1-8Z"/></svg>;
    case 'shield':    return <svg {...c}><path d="M12 3l8 4v5c0 5-3.5 8.5-8 9-4.5-.5-8-4-8-9V7l8-4Z"/></svg>;
    case 'tag':       return <svg {...c}><path d="M3 12V4h8l9 9-8 8-9-9Z"/><circle cx="7.5" cy="7.5" r="1.5"/></svg>;
    default: return null;
  }
}

/* ───────────────────────── theme palette ────────────────────────── */
const palettes = {
  dark: {
    page:       'bg-[#020617] text-slate-200',
    title:      'text-white',
    text:       'text-slate-300',
    muted:      'text-slate-400',
    accent:     'text-blue-400',
    soft:       'bg-white/[0.025] border border-white/10',
    softer:     'bg-white/[0.04] border border-white/10',
    card:       'border border-white/10 bg-white/[0.03] hover:border-white/25',
    chip:       'border border-white/15 bg-white/5 text-slate-200',
    pillBlue:   'border border-blue-400/40 bg-blue-500/10 text-blue-300',
    primary:    'bg-white text-slate-950 hover:bg-slate-100',
    secondary:  'border border-white/20 bg-white/5 text-white hover:bg-white/10',
    divider:    'border-white/10',
    inputBar:   'bg-slate-900/85 border-white/10',
    sectionAlt: 'bg-white/[0.015]',
    navBg:      'bg-transparent',
  },
  light: {
    page:       'bg-white text-slate-800',
    title:      'text-slate-900',
    text:       'text-slate-700',
    muted:      'text-slate-500',
    accent:     'text-blue-600',
    soft:       'bg-slate-50 border border-slate-200',
    softer:     'bg-slate-100 border border-slate-200',
    card:       'border border-slate-200 bg-white hover:border-slate-300 hover:shadow-md',
    chip:       'border border-slate-300 bg-white text-slate-700',
    pillBlue:   'border border-blue-300 bg-blue-50 text-blue-700',
    primary:    'bg-slate-900 text-white hover:bg-slate-800',
    secondary:  'border border-slate-300 bg-white text-slate-900 hover:bg-slate-50',
    divider:    'border-slate-200',
    inputBar:   'bg-white border-slate-200',
    sectionAlt: 'bg-slate-50',
    navBg:      'bg-transparent',
  },
};

/* ──────────────────────────── NAV ───────────────────────────────── */
function Nav({ p, theme }) {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (!sessionStorage.getItem('access_token')) return;
    let active = true;
    dashboardApi.getProfile()
      .then((prof) => { if (active) setUser(prof); })
      .catch(() => { if (active) setUser(null); });
    return () => { active = false; };
  }, []);

  const displayName = user ? (user.full_name || user.email || 'Account') : null;
  const initial = (displayName || 'U').trim()[0]?.toUpperCase() || 'U';

  return (
    <header className={`sticky top-0 z-40 backdrop-blur-md ${p.navBg}`}>
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link to="/" className="flex items-center gap-2.5">
          <img src="/logo-tight.png" alt="AIveilix" className="h-8 w-8 rounded-md" />
          <span className={`text-base font-semibold tracking-tight ${p.title}`}>AIveilix</span>
        </Link>
        <nav className="hidden items-center gap-7 md:flex">
          {[['How it works', '#how'], ['Features', '#features'], ['Pricing', '#pricing']].map(([l, h]) => (
            <a key={l} href={h} className={`text-sm ${p.text} transition hover:${p.title}`}>{l}</a>
          ))}
          <Link to="/docs" className={`text-sm ${p.text} transition hover:${p.title}`}>Docs</Link>
        </nav>
        <div className="flex items-center gap-2">
          {displayName ? (
            <button
              onClick={() => navigate('/dashboard')}
              title="Go to dashboard"
              className={`flex items-center gap-2 rounded-full py-1.5 pl-1.5 pr-4 text-sm font-semibold transition ${p.secondary}`}
            >
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-blue-600 text-xs font-bold text-white">{initial}</span>
              <span className="max-w-[12rem] truncate">{displayName}</span>
            </button>
          ) : (
            <>
              <Link to="/login" className={`rounded-full px-3 py-1.5 text-sm font-medium transition ${p.secondary}`}>Sign in</Link>
              <button onClick={() => navigate('/signup')} className={`rounded-full px-4 py-1.5 text-sm font-semibold transition ${theme === 'dark' ? 'bg-blue-600 text-white hover:bg-blue-500' : 'bg-blue-600 text-white hover:bg-blue-500'}`}>
                Start free
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

/* ──────────────────────────── HERO ──────────────────────────────── */
function Hero({ p, theme }) {
  const navigate = useNavigate();
  const isDark = theme === 'dark';
  return (
    <section className={`relative overflow-hidden ${isDark ? 'bg-[#020617]' : 'bg-white'}`}>
      {/* layered background */}
      {isDark && <>
        <BackgroundBeams />
        <Spotlight className="-top-40 left-0 md:-top-20 md:left-60" fill="white" />
      </>}
      {!isDark && (
        <AnimatedGridPattern
          numSquares={30} maxOpacity={0.08} duration={3} repeatDelay={1}
          className="[mask-image:radial-gradient(500px_circle_at_center,white,transparent)] inset-x-0 inset-y-[-30%] h-[200%] skew-y-12"
        />
      )}
      {/* soft blue glow */}
      <div className="pointer-events-none absolute -top-32 left-1/2 -translate-x-1/2 h-[40rem] w-[40rem] rounded-full bg-blue-500/20 blur-3xl" />

      <div className="relative mx-auto max-w-7xl px-6 pt-32 pb-40 text-center sm:pt-40">
        <BlurFade delay={0.12}>
          <h1 className={`mx-auto max-w-4xl text-5xl font-semibold leading-[1.04] tracking-tight sm:text-7xl ${p.title}`}>
            Anchor your docs.<br />
            Use them in <GradientText>every AI</GradientText>.
          </h1>
        </BlurFade>

        <BlurFade delay={0.22}>
          <p className={`mx-auto mt-8 max-w-2xl text-lg leading-relaxed sm:text-xl ${p.text}`}>
            Upload once. Get a single link Claude, ChatGPT, and any modern AI can read on demand.
            <strong className={p.title}> Stop re-uploading the same files to every chat.</strong>
          </p>
        </BlurFade>

        <BlurFade delay={0.32}>
          <div className="mt-10 flex flex-wrap items-center justify-center gap-3">
            <ShimmerButton
              background={isDark ? 'rgba(255,255,255,1)' : 'rgba(15,23,42,1)'}
              shimmerColor={isDark ? '#60a5fa' : '#ffffff'}
              onClick={() => navigate('/signup')}
              className={isDark ? '!text-slate-950 font-semibold px-7 py-3.5 text-base' : '!text-white font-semibold px-7 py-3.5 text-base'}
            >
              Start free — no card
              <Icon name="arrow" className="ml-2 h-4 w-4" />
            </ShimmerButton>
            <a href="#how" className={`inline-flex items-center gap-2 rounded-full px-6 py-3.5 text-base font-medium transition ${p.secondary}`}>
              See how it works
            </a>
          </div>
        </BlurFade>

        <BlurFade delay={0.42}>
          <div className={`mt-14 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-sm ${p.muted}`}>
            <span className="flex items-center gap-1.5"><Icon name="check" className={`h-4 w-4 ${p.accent}`} /> Cite every answer</span>
            <span className="flex items-center gap-1.5"><Icon name="check" className={`h-4 w-4 ${p.accent}`} /> Private buckets</span>
            <span className="flex items-center gap-1.5"><Icon name="check" className={`h-4 w-4 ${p.accent}`} /> Works with Claude &amp; ChatGPT</span>
            <span className="flex items-center gap-1.5"><Icon name="check" className={`h-4 w-4 ${p.accent}`} /> No re-uploading</span>
          </div>
        </BlurFade>
      </div>
      {/* bottom fade */}
      <div className={`pointer-events-none absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-b ${isDark ? 'from-transparent to-[#020617]' : 'from-transparent to-white'}`} />
    </section>
  );
}

/* ───────────────────────── TRUST STRIP ──────────────────────────── */
function TrustStrip({ p, theme }) {
  const isDark = theme === 'dark';
  const tools = ['Claude', 'ChatGPT', 'Claude Desktop', 'MCP Inspector', 'Continue', 'Goose', 'Zed', 'Cline'];
  return (
    <section className={`relative border-y ${p.divider} overflow-hidden`}>
      <div className="mx-auto max-w-7xl px-6 py-10">
        <BlurFade>
          <p className={`mb-6 text-center text-xs font-semibold uppercase tracking-[0.22em] ${p.muted}`}>
            Plug into the AI you already use
          </p>
        </BlurFade>
        <Marquee pauseOnHover className="[--duration:35s]">
          {tools.map((t) => (
            <div key={t} className={`mx-6 flex items-center gap-2 text-2xl font-semibold ${isDark ? 'text-white/80' : 'text-slate-700'}`}>
              <Icon name="sparkle" className={`h-5 w-5 ${p.accent}`} />
              {t}
            </div>
          ))}
        </Marquee>
        {/* left + right fade gradient */}
        <div className={`pointer-events-none absolute inset-y-0 left-0 w-24 bg-gradient-to-r ${isDark ? 'from-[#020617]' : 'from-white'} to-transparent`} />
        <div className={`pointer-events-none absolute inset-y-0 right-0 w-24 bg-gradient-to-l ${isDark ? 'from-[#020617]' : 'from-white'} to-transparent`} />
      </div>
    </section>
  );
}

/* ───────────────────────── PROBLEM / SOLUTION ───────────────────── */
const PAIN_POINTS = [
  { icon: 'clock', title: '5+ minutes lost every chat',          body: 'Dragging the same 30 PDFs into every new Claude or ChatGPT window. Every. Single. Time.' },
  { icon: 'coins', title: 'Pay for the same tokens twice',       body: 'Each session reprocesses the entire context from scratch. Your wallet feels it.' },
  { icon: 'block', title: 'Context window keeps cutting you off', body: 'Big PDFs get truncated. Answers come back shallow. You never know what the AI missed.' },
  { icon: 'question', title: 'Answers without citations',         body: 'Was it from the contract? The annual report? A hallucination? You can\'t verify anything.' },
  { icon: 'restart', title: 'Switch tools = start over',          body: 'Move from ChatGPT to Claude and that\'s another 30-minute upload session. Lock-in by friction.' },
];
const WIN_POINTS = [
  { icon: 'flash',  title: 'Upload once. Forever.',          body: 'Files stay indexed across every AI tool you use. Zero re-uploading, ever.' },
  { icon: 'tag',    title: 'Pay tokens once',                body: 'Your AI fetches only the exact chunks it needs — never the whole 200-page PDF.' },
  { icon: 'infin',  title: '5,000 files per bucket',         body: 'No context window pressure. Drop your entire research library in and ask away.' },
  { icon: 'check',  title: 'Every answer cited',             body: 'Exact file + exact page number on every response. Click to verify in one tap.' },
  { icon: 'link',   title: 'One link, every AI',             body: 'Claude today, ChatGPT tomorrow, the next great AI next year. Same link. No migration.' },
];

function PainPointIcon({ name, className }) {
  const c = { className: className || 'h-4 w-4', viewBox: '0 0 24 24', fill: 'none', strokeWidth: 1.8, stroke: 'currentColor', strokeLinecap: 'round', strokeLinejoin: 'round' };
  switch (name) {
    case 'clock':    return <svg {...c}><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>;
    case 'coins':    return <svg {...c}><circle cx="9" cy="9" r="6"/><path d="M19.5 15a6 6 0 0 1-6 6m1.5-4.5a6 6 0 1 0-6-6"/></svg>;
    case 'block':    return <svg {...c}><circle cx="12" cy="12" r="9"/><path d="M5.6 5.6l12.8 12.8"/></svg>;
    case 'question': return <svg {...c}><circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 0 1 5 0c0 1.5-2.5 2-2.5 3.5M12 17v.01"/></svg>;
    case 'restart':  return <svg {...c}><path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/></svg>;
    case 'flash':    return <svg {...c}><path d="M13 2L4 14h7l-1 8 9-12h-7l1-8Z"/></svg>;
    case 'tag':      return <svg {...c}><path d="M3 12V4h8l9 9-8 8-9-9Z"/><circle cx="7.5" cy="7.5" r="1.5"/></svg>;
    case 'infin':    return <svg {...c}><path d="M5.5 12a4 4 0 0 1 6.5-3.1c0.7 0.6 1.6 1.6 3 3.1 1.4 1.5 2.3 2.5 3 3.1A4 4 0 1 0 18.5 12a4 4 0 0 1-6.5 3.1c-0.7-0.6-1.6-1.6-3-3.1-1.4-1.5-2.3-2.5-3-3.1A4 4 0 1 0 5.5 12Z"/></svg>;
    case 'check':    return <svg {...c}><path d="M5 12l4 4 10-10"/></svg>;
    case 'link':     return <svg {...c}><path d="M10 14a4 4 0 0 0 5.66 0l3-3a4 4 0 1 0-5.66-5.66l-1.5 1.5"/><path d="M14 10a4 4 0 0 0-5.66 0l-3 3a4 4 0 1 0 5.66 5.66l1.5-1.5"/></svg>;
    default: return null;
  }
}

function ProblemSolution({ p, theme }) {
  const isDark = theme === 'dark';
  return (
    <section className={`relative overflow-hidden border-b ${p.divider} ${p.sectionAlt}`}>
      {/* faint background patterning to make the section pop */}
      <div className="pointer-events-none absolute inset-0">
        <div className={`absolute left-1/4 top-1/4 h-72 w-72 rounded-full ${isDark ? 'bg-red-500/8' : 'bg-red-500/5'} blur-3xl`} />
        <div className={`absolute right-1/4 bottom-1/4 h-80 w-80 rounded-full ${isDark ? 'bg-blue-500/12' : 'bg-blue-500/8'} blur-3xl`} />
      </div>

      <div className="relative mx-auto max-w-7xl px-6 py-28">
        <BlurFade>
          <p className={`text-center text-xs font-semibold uppercase tracking-[0.22em] ${p.accent}`}>The honest comparison</p>
          <h2 className={`mx-auto mt-3 max-w-3xl text-center text-4xl font-semibold tracking-tight sm:text-6xl ${p.title}`}>
            Stop the doc-upload<br/>
            <span className="bg-gradient-to-r from-red-400 via-red-500 to-rose-500 bg-clip-text text-transparent">tax</span>.
          </h2>
          <p className={`mx-auto mt-6 max-w-2xl text-center text-lg ${p.text}`}>
            Every minute you spend re-uploading is a minute not spent reading. Here's exactly what you lose — and what you get back with AIveilix.
          </p>
        </BlurFade>

        <div className="relative mt-20 grid items-stretch gap-6 lg:grid-cols-[1fr_auto_1fr]">

          {/* WITHOUT AIveilix — desaturated, red accent */}
          <BlurFade delay={0.05}>
            <CardHoverSpotlight className={`h-full ${p.card} p-7 sm:p-8`} color="#ef4444">
              <div className="mb-6 flex items-center gap-3">
                <span className={`inline-flex h-9 items-center gap-2 rounded-full px-3 text-[11px] font-semibold uppercase tracking-wider ${isDark ? 'bg-red-500/15 text-red-300 ring-1 ring-red-500/30' : 'bg-red-50 text-red-700 ring-1 ring-red-200'}`}>
                  <span className="h-1.5 w-1.5 rounded-full bg-red-400" />
                  Without AIveilix
                </span>
              </div>
              <h3 className={`text-2xl font-semibold tracking-tight ${p.title} sm:text-3xl`}>
                What you're losing
                <span className={isDark ? 'text-red-400' : 'text-red-600'}> today.</span>
              </h3>
              <ul className={`mt-8 space-y-5`}>
                {PAIN_POINTS.map((pt, i) => (
                  <li key={pt.title} className="group flex gap-4">
                    <span className={`mt-0.5 inline-flex h-9 w-9 flex-none items-center justify-center rounded-lg ring-1 transition group-hover:scale-110 ${isDark ? 'bg-red-500/10 text-red-300 ring-red-500/25' : 'bg-red-50 text-red-700 ring-red-200'}`}>
                      <PainPointIcon name={pt.icon} className="h-4 w-4" />
                    </span>
                    <div className="flex-1">
                      <p className={`text-base font-semibold ${p.title}`}>{pt.title}</p>
                      <p className={`mt-1 text-sm leading-relaxed ${p.text}`}>{pt.body}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </CardHoverSpotlight>
          </BlurFade>

          {/* VS divider */}
          <div className="hidden flex-col items-center justify-center lg:flex">
            <div className={`h-32 w-px ${isDark ? 'bg-white/15' : 'bg-slate-300'}`} />
            <div className={`my-4 flex h-14 w-14 items-center justify-center rounded-full text-sm font-bold tracking-wider ${isDark ? 'bg-white/5 text-white ring-1 ring-white/15' : 'bg-white text-slate-700 ring-1 ring-slate-200 shadow-md'}`}>
              VS
            </div>
            <div className={`h-32 w-px ${isDark ? 'bg-white/15' : 'bg-slate-300'}`} />
          </div>

          {/* WITH AIveilix — highlighted, blue glow */}
          <BlurFade delay={0.15}>
            <div className="relative h-full">
              {/* subtle blue glow halo behind the winning card */}
              <div className={`pointer-events-none absolute -inset-0.5 rounded-2xl bg-gradient-to-br ${isDark ? 'from-blue-500/40 via-cyan-400/20 to-purple-500/30' : 'from-blue-400/30 via-cyan-300/20 to-purple-400/20'} opacity-60 blur-md`} />
              <CardHoverSpotlight className={`relative h-full ${p.card} p-7 sm:p-8 ${isDark ? 'ring-1 ring-blue-400/30' : 'ring-1 ring-blue-300'}`} color="#60a5fa">
                <div className="mb-6 flex items-center gap-3">
                  <span className={`inline-flex h-9 items-center gap-2 rounded-full px-3 text-[11px] font-semibold uppercase tracking-wider ${isDark ? 'bg-blue-500/15 text-blue-300 ring-1 ring-blue-400/30' : 'bg-blue-50 text-blue-700 ring-1 ring-blue-200'}`}>
                    <span className="h-1.5 w-1.5 rounded-full bg-blue-400" />
                    With AIveilix
                  </span>
                  <span className={`hidden rounded-full px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider sm:inline ${isDark ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white' : 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'}`}>
                    The fix
                  </span>
                </div>
                <h3 className={`text-2xl font-semibold tracking-tight ${p.title} sm:text-3xl`}>
                  What you get
                  <span className={isDark ? 'text-blue-400' : 'text-blue-600'}> instead.</span>
                </h3>
                <ul className="mt-8 space-y-5">
                  {WIN_POINTS.map((pt, i) => (
                    <li key={pt.title} className="group flex gap-4">
                      <span className={`mt-0.5 inline-flex h-9 w-9 flex-none items-center justify-center rounded-lg ring-1 transition group-hover:scale-110 ${isDark ? 'bg-blue-500/15 text-blue-300 ring-blue-400/30' : 'bg-blue-50 text-blue-700 ring-blue-200'}`}>
                        <PainPointIcon name={pt.icon} className="h-4 w-4" />
                      </span>
                      <div className="flex-1">
                        <p className={`text-base font-semibold ${p.title}`}>{pt.title}</p>
                        <p className={`mt-1 text-sm leading-relaxed ${p.text}`}>{pt.body}</p>
                      </div>
                    </li>
                  ))}
                </ul>
              </CardHoverSpotlight>
            </div>
          </BlurFade>
        </div>

        {/* Outcome strip */}
        <BlurFade delay={0.25}>
          <div className={`relative mx-auto mt-16 max-w-4xl overflow-hidden rounded-2xl px-6 py-6 text-center sm:px-10 sm:py-8 ${p.card}`}>
            <p className={`text-base sm:text-lg ${p.text}`}>
              <strong className={p.title}>The math:</strong> If you do 5 AI chats a day at 5 minutes of re-upload each, AIveilix saves you <strong className={p.title}>~10 hours every month</strong>. That's a working day, back.
            </p>
          </div>
        </BlurFade>
      </div>
    </section>
  );
}

/* ─────────────── HOW IT WORKS — tool workflow ─────────────── */
function HowItWorks({ p, theme }) {
  const isDark = theme === 'dark';
  return (
    <section id="how" className={`border-b ${p.divider}`}>
      <div className="mx-auto max-w-7xl px-6 py-28">
        <BlurFade>
          <p className={`text-center text-xs font-semibold uppercase tracking-[0.22em] ${p.accent}`}>How it works</p>
          <h2 className={`mx-auto mt-3 max-w-2xl text-center text-3xl font-semibold tracking-tight sm:text-5xl ${p.title}`}>
            Upload once.<br/>Ask anything, anytime.
          </h2>
          <p className={`mx-auto mt-5 max-w-xl text-center text-base ${p.text}`}>
            Three steps. No setup. Your documents become a chatroom you can come back to whenever.
          </p>
        </BlurFade>

        <div className="mt-16 grid gap-6 md:grid-cols-3">
          {/* Step 1: Upload */}
          <BlurFade delay={0.05}>
            <div className={`group relative h-full overflow-hidden rounded-2xl p-7 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl ${p.card}`}>
              <div className="absolute -right-6 -top-6 text-[8rem] font-black leading-none tracking-tighter opacity-[0.04]">1</div>
              <div className={`relative flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 text-white shadow-lg shadow-blue-500/30`}>
                <Icon name="folder" className="h-6 w-6" />
              </div>
              <h3 className={`relative mt-5 text-lg font-semibold ${p.title}`}>Drop in your docs</h3>
              <p className={`relative mt-2 text-sm leading-relaxed ${p.text}`}>
                Drag PDFs, spreadsheets, images, and notes into a bucket. We index everything in the background — searchable in seconds.
              </p>
              {/* tiny visual: stacked file pills */}
              <div className="relative mt-5 space-y-1.5">
                {['Q3-strategy.pdf', 'market-research.pdf', 'metrics.csv'].map((f, i) => (
                  <div key={f} className={`flex items-center gap-2 rounded-md px-2.5 py-1.5 text-xs ${isDark ? 'bg-white/[0.04] text-slate-300' : 'bg-slate-50 text-slate-600'}`}>
                    <Icon name="folder" className="h-3.5 w-3.5 opacity-50" /> {f}
                  </div>
                ))}
              </div>
            </div>
          </BlurFade>

          {/* Step 2: Ask */}
          <BlurFade delay={0.15}>
            <div className={`group relative h-full overflow-hidden rounded-2xl p-7 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl ${p.card}`}>
              <div className="absolute -right-6 -top-6 text-[8rem] font-black leading-none tracking-tighter opacity-[0.04]">2</div>
              <div className="relative flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 text-white shadow-lg shadow-purple-500/30">
                <Icon name="chat" className="h-6 w-6" />
              </div>
              <h3 className={`relative mt-5 text-lg font-semibold ${p.title}`}>Ask in plain language</h3>
              <p className={`relative mt-2 text-sm leading-relaxed ${p.text}`}>
                Open the bucket, type your question. AIveilix pulls the relevant chunks and answers — with the exact page cited.
              </p>
              {/* tiny visual: chat bubble */}
              <div className="relative mt-5 space-y-2">
                <div className={`max-w-[85%] rounded-2xl px-3 py-1.5 text-xs ${isDark ? 'bg-blue-600 text-white' : 'bg-blue-600 text-white'} ml-auto`}>What are the Q3 risks?</div>
                <div className={`max-w-[90%] rounded-2xl px-3 py-1.5 text-xs ${isDark ? 'bg-white/[0.06] text-slate-200' : 'bg-slate-100 text-slate-700'}`}>Three: EMEA pressure, vendor lock-in, APAC compliance.</div>
                <div className="flex flex-wrap gap-1.5">
                  <span className={`rounded-full px-2 py-0.5 text-[10px] ${isDark ? 'bg-white/[0.06] text-slate-300' : 'bg-blue-50 text-blue-700'}`}>📎 p.4-5</span>
                </div>
              </div>
            </div>
          </BlurFade>

          {/* Step 3: Branch into many threads */}
          <BlurFade delay={0.25}>
            <div className={`group relative h-full overflow-hidden rounded-2xl p-7 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl ${p.card}`}>
              <div className="absolute -right-6 -top-6 text-[8rem] font-black leading-none tracking-tighter opacity-[0.04]">3</div>
              <div className="relative flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/30">
                <Icon name="chat" className="h-6 w-6" />
              </div>
              <h3 className={`relative mt-5 text-lg font-semibold ${p.title}`}>Branch into many threads</h3>
              <p className={`relative mt-2 text-sm leading-relaxed ${p.text}`}>
                One bucket can host dozens of conversations. Keep risks, market sizing, and vendor talks in their own threads. Come back any time.
              </p>
              {/* tiny visual: thread list */}
              <div className="relative mt-5 space-y-1.5">
                {[
                  { t: 'Q3 risks deep-dive', meta: '16 msgs · 2h ago' },
                  { t: 'Market sizing',      meta: '11 msgs · 4h ago' },
                  { t: 'Vendor compare',     meta: '9 msgs · 1d ago' },
                ].map((th) => (
                  <div key={th.t} className={`flex items-center justify-between rounded-md px-2.5 py-1.5 text-xs ${isDark ? 'bg-white/[0.04]' : 'bg-slate-50'}`}>
                    <span className={`font-medium ${p.title}`}>{th.t}</span>
                    <span className={p.muted + ' text-[10px]'}>{th.meta}</span>
                  </div>
                ))}
              </div>
            </div>
          </BlurFade>
        </div>
      </div>
    </section>
  );
}

/* ───────── HOW MCP WORKS — separate section, beam diagram ─────── */
function HowMcpWorks({ p, theme }) {
  const navigate = useNavigate();
  const containerRef = useRef(null);
  const bucketRef = useRef(null);
  const aiRefs = [useRef(null), useRef(null), useRef(null), useRef(null)];
  const isDark = theme === 'dark';

  return (
    <section id="mcp" className={`${p.sectionAlt} border-b ${p.divider}`}>
      <div className="mx-auto max-w-7xl px-6 py-28">
        <BlurFade>
          {/* AIveilix-branded badge with the real logo */}
          <span className={`mx-auto flex w-fit items-center gap-2 rounded-full pl-1 pr-3 py-1 text-xs font-semibold uppercase tracking-wider ${p.pillBlue}`}>
            <img src="/logo-tight.png" alt="" className="h-5 w-5 rounded-full" />
            The AIveilix MCP superpower
          </span>
          <h2 className={`mx-auto mt-5 max-w-3xl text-center text-3xl font-semibold tracking-tight sm:text-5xl ${p.title}`}>
            One bucket, <span className="bg-gradient-to-r from-blue-400 via-cyan-300 to-purple-400 bg-clip-text text-transparent">every AI you use</span>.
          </h2>
          <p className={`mx-auto mt-5 max-w-2xl text-center text-base ${p.text}`}>
            MCP is just a smart link. AIveilix generates one for each bucket. Paste it into Claude, ChatGPT, or any modern AI — they all read the same documents in real time. No re-uploading anywhere, ever.
          </p>
          <p className={`mx-auto mt-3 max-w-2xl text-center text-xs ${p.muted}`}>
            Click any tile below for a step-by-step setup guide.
          </p>
        </BlurFade>

        {/* Animated beam diagram with REAL logos */}
        <BlurFade delay={0.15}>
          <div ref={containerRef} className={`relative mx-auto mt-14 grid h-[340px] max-w-3xl grid-cols-2 items-center justify-items-center gap-y-8 rounded-2xl p-8 sm:h-[400px] ${p.soft}`}>
            {/* AIveilix bucket node — using real logo */}
            <div className="row-span-4 flex flex-col items-center">
              <div ref={bucketRef} className="relative flex h-24 w-24 items-center justify-center rounded-2xl bg-white p-2 shadow-xl shadow-blue-500/30 ring-1 ring-blue-400/40 sm:h-28 sm:w-28">
                <img src="/logo-tight.png" alt="AIveilix" className="h-full w-full rounded-xl object-contain" />
              </div>
              <p className={`mt-3 text-sm font-semibold ${p.title}`}>AIveilix bucket</p>
              <p className={`text-xs ${p.muted}`}>via MCP link</p>
            </div>

            {/* AI tool tiles — real logos, clickable to /connect/<id> */}
            {TOOLS.map((t, i) => {
              const Logo = t.Logo;
              return (
                <button
                  key={t.id}
                  ref={aiRefs[i]}
                  onClick={() => navigate(`/connect/${t.id}`)}
                  className={`group flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg ${p.card} ${p.title} ${isDark ? 'hover:border-white/40 hover:shadow-blue-500/20' : 'hover:border-slate-400 hover:shadow-slate-400/30'}`}
                  style={{ ['--brand']: t.brand }}
                >
                  <span className="flex items-center gap-2.5">
                    <Logo className="h-7 w-7 flex-none transition group-hover:scale-110" />
                    <span>{t.label}</span>
                  </span>
                  <span className={`inline-flex items-center gap-1 text-xs font-medium opacity-0 transition group-hover:opacity-100 ${p.accent}`}>
                    Setup
                    <Icon name="arrow" className="h-3 w-3" />
                  </span>
                </button>
              );
            })}

            <AnimatedBeam containerRef={containerRef} fromRef={bucketRef} toRef={aiRefs[0]} curvature={-60} duration={3.5} />
            <AnimatedBeam containerRef={containerRef} fromRef={bucketRef} toRef={aiRefs[1]} curvature={-20} duration={4}   delay={0.6} />
            <AnimatedBeam containerRef={containerRef} fromRef={bucketRef} toRef={aiRefs[2]} curvature={20}  duration={4.5} delay={1.2} />
            <AnimatedBeam containerRef={containerRef} fromRef={bucketRef} toRef={aiRefs[3]} curvature={60}  duration={5}   delay={1.8} />
          </div>
        </BlurFade>

        {/* 3-step row explaining MCP for non-devs */}
        <div className="mt-14 grid gap-6 md:grid-cols-3">
          {[
            { n: 1, t: 'Open your bucket',  b: 'Hit the MCP button. AIveilix generates a single secure link tied to that bucket.' },
            { n: 2, t: 'Copy the link',     b: 'Treat it like a password — anyone with it can read that bucket. Revoke any time.' },
            { n: 3, t: 'Paste into your AI', b: 'Add it as a custom connector in Claude, ChatGPT, or any MCP-ready tool. Done.' },
          ].map((s, i) => (
            <BlurFade key={s.n} delay={i * 0.08}>
              <div className={`group relative h-full overflow-hidden rounded-2xl p-7 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg ${p.card}`}>
                <span className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-sm font-semibold text-white">{s.n}</span>
                <h3 className={`mt-5 text-lg font-semibold ${p.title}`}>{s.t}</h3>
                <p className={`mt-2 text-sm leading-relaxed ${p.text}`}>{s.b}</p>
              </div>
            </BlurFade>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ────────────── BUCKET SHOWCASE — Container Scroll ─────────────── */
function BucketShowcase({ p, theme }) {
  return (
    <section id="features" className={`relative overflow-hidden ${p.sectionAlt}`}>
      <ContainerScroll
        titleComponent={
          <>
            <BlurFade>
              <p className={`text-xs font-semibold uppercase tracking-[0.22em] ${p.accent}`}>The bucket workspace</p>
              <h2 className={`mx-auto mt-3 max-w-2xl text-3xl font-semibold tracking-tight sm:text-5xl ${p.title}`}>
                Built for people who read things.
              </h2>
            </BlurFade>
          </>
        }
      >
        <BucketMockup p={p} theme={theme} />
      </ContainerScroll>
    </section>
  );
}

function BucketMockup({ p, theme }) {
  const isDark = theme === 'dark';
  const sub = isDark ? 'text-slate-500' : 'text-slate-400';
  const tone = isDark ? 'text-slate-200' : 'text-slate-700';
  return (
    <div className={`h-full w-full overflow-hidden ${isDark ? 'bg-slate-950' : 'bg-white'} flex flex-col`}>
      {/* top bar */}
      <div className={`flex items-center gap-2 border-b px-4 py-3 ${p.divider} ${isDark ? 'bg-slate-900' : 'bg-slate-50'}`}>
        <span className="h-3 w-3 rounded-full bg-red-400" />
        <span className="h-3 w-3 rounded-full bg-amber-400" />
        <span className="h-3 w-3 rounded-full bg-emerald-400" />
        <span className={`ml-3 text-xs ${sub}`}>aiveilix.com / bucket / research-papers</span>
      </div>

      <div className="grid flex-1 grid-cols-[180px_1fr_240px] min-h-0">
        {/* Files */}
        <div className={`border-r p-4 overflow-y-auto ${p.divider}`}>
          <p className={`mb-3 text-[10px] font-semibold uppercase tracking-wider ${sub}`}>Files</p>
          <ul className="space-y-1.5">
            {['Q3-strategy.pdf', 'market-research.pdf', 'team-notes.md', 'metrics.csv', 'whitepaper.pdf', 'investor-deck.pdf'].map((f, i) => (
              <li key={f} className={`flex items-center gap-2 rounded-md px-2 py-1.5 text-xs ${i === 0 ? (isDark ? 'bg-blue-500/15 text-blue-200' : 'bg-blue-50 text-blue-700') : tone}`}>
                <Icon name="folder" className="h-3.5 w-3.5 opacity-60" />
                <span className="truncate">{f}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Chat */}
        <div className="flex flex-col">
          <div className="flex-1 space-y-3 overflow-y-auto p-5">
            <ChatBubble side="user" text="What were the main risks called out in Q3-strategy.pdf?" theme={theme} />
            <ChatBubble side="ai" text="Three primary risks: (1) competitive pressure in EMEA, (2) supply-chain dependency on a single vendor, and (3) regulatory uncertainty around data residency in APAC." theme={theme} />
            <div className="flex flex-wrap gap-1.5">
              {['Q3-strategy.pdf · pp.4-5', 'Q3-strategy.pdf · p.11'].map((c) => (
                <span key={c} className={`rounded-full px-2 py-1 text-[10px] ${isDark ? 'bg-white/[0.06] text-slate-300' : 'bg-blue-50 text-blue-700'}`}>📎 {c}</span>
              ))}
            </div>
          </div>

          {/* Input bar */}
          <div className={`border-t p-3 ${p.divider}`}>
            <div className={`flex items-center gap-1.5 rounded-2xl border px-3 py-1.5 ${p.inputBar} shadow-sm`}>
              <button className={`flex h-7 w-7 items-center justify-center rounded-lg ${isDark ? 'text-slate-400 hover:bg-white/10' : 'text-slate-500 hover:bg-slate-100'}`}><Icon name="paperclip" className="h-4 w-4" /></button>
              <button className={`flex h-7 w-7 items-center justify-center rounded-lg ${isDark ? 'text-blue-400 bg-blue-500/15' : 'text-blue-600 bg-blue-50'}`}><Icon name="at" className="h-4 w-4" /></button>
              <button className={`flex h-7 w-7 items-center justify-center rounded-lg ${isDark ? 'text-slate-400 hover:bg-white/10' : 'text-slate-500 hover:bg-slate-100'}`}><Icon name="web" className="h-4 w-4" /></button>
              <input readOnly value="@whitepaper.pdf  Summarize the key findings"
                className={`flex-1 bg-transparent text-sm focus:outline-none ${tone}`} />
              <button className={`flex h-7 w-7 items-center justify-center rounded-lg ${isDark ? 'text-slate-400 hover:bg-white/10' : 'text-slate-500 hover:bg-slate-100'}`}><Icon name="mic" className="h-4 w-4" /></button>
              <button className="flex h-7 items-center gap-1 rounded-lg bg-blue-600 px-2.5 text-xs font-semibold text-white hover:bg-blue-500">Ask <Icon name="arrow" className="h-3 w-3" /></button>
            </div>
          </div>
        </div>

        {/* Threads */}
        <div className={`border-l p-4 overflow-y-auto ${p.divider}`}>
          <p className={`mb-3 text-[10px] font-semibold uppercase tracking-wider ${sub}`}>Threads</p>
          <ul className="space-y-2">
            {['Q3 risks deep-dive', 'Market sizing', 'Vendor compare', 'Notes recap'].map((t, i) => (
              <li key={t} className={`rounded-md p-2 text-xs ${i === 0 ? (isDark ? 'bg-white/[0.07]' : 'bg-slate-100') : ''} ${tone}`}>
                <p className={`font-medium ${p.title}`}>{t}</p>
                <p className={`mt-0.5 ${sub}`}>{i + 2}h ago · {(i + 1) * 4} msgs</p>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

function ChatBubble({ side, text, theme }) {
  const isUser = side === 'user';
  const isDark = theme === 'dark';
  const wrap = isUser ? 'justify-end' : 'justify-start';
  const bubble = isUser
    ? 'bg-blue-600 text-white'
    : (isDark ? 'bg-white/[0.06] text-slate-100' : 'bg-slate-100 text-slate-800');
  return (
    <div className={`flex ${wrap}`}>
      <div className={`max-w-[80%] rounded-2xl px-3.5 py-2 text-sm ${bubble}`}>{text}</div>
    </div>
  );
}

/* ──────────────────────── FEATURES — Bento ─────────────────────── */
function Features({ p, theme }) {
  const isDark = theme === 'dark';

  /* === Reusable real UI fragments — pixel-matched to BucketPage in App.jsx === */
  const fMuted = isDark ? 'text-slate-400' : 'text-slate-500';
  const fLine  = isDark ? 'border-white/10' : 'border-slate-200';
  const fBody  = isDark ? 'text-slate-200' : 'text-slate-700';

  const GlobeSVG = ({ className = 'h-4 w-4' }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
    </svg>
  );
  const MicSVG = ({ className = 'h-4 w-4' }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 11a7 7 0 0 0 14 0"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="8" y1="22" x2="16" y2="22"/>
    </svg>
  );
  const AttachSVG = ({ className = 'h-4 w-4' }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="m21 12-9 9a5 5 0 0 1-7-7l9-9a3 3 0 0 1 5 5L11 18a1.4 1.4 0 0 1-2-2l8-8"/>
    </svg>
  );
  const ScopeSVG = ({ className = 'h-4 w-4' }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
    </svg>
  );
  const SendSVG = ({ className = 'h-4 w-4' }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 19V5"/><path d="m5 12 7-7 7 7"/>
    </svg>
  );
  const DocSVG = ({ className = 'h-3.5 w-3.5' }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
    </svg>
  );
  const ChevronSVG = ({ className = 'h-3 w-3' }) => (
    <svg viewBox="0 0 24 24" className={className} fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="m6 9 6 6 6-6"/></svg>
  );

  /* RealInputBar — replicates the bottom-of-bucket composer.
     variant: 'idle' | 'web' | 'voice' */
  const RealInputBar = ({ variant = 'idle' }) => {
    const passive = `${fMuted} hover:bg-black/10`;
    const webOn   = isDark ? 'bg-blue-500/20 text-blue-300 ring-1 ring-blue-400/40' : 'bg-blue-100 text-blue-700 ring-1 ring-blue-400/50';
    const micOn   = isDark ? 'bg-slate-200 text-slate-900 animate-pulse' : 'bg-blue-500 text-white animate-pulse';
    const placeholder =
      variant === 'voice' ? 'Listening…'
      : variant === 'web' ? "What's the latest on EU's AI Act vs our Q3 plan?"
      : 'Message…';
    return (
      <div className={`overflow-hidden rounded-2xl border shadow-sm ${isDark ? 'bg-slate-900/85 border-white/10' : 'bg-white border-slate-200'}`}>
        <div className="px-3 pt-2.5">
          <p className={`text-[11px] leading-5 ${variant === 'voice' ? p.title : fMuted}`}>{placeholder}</p>
        </div>
        <div className="flex items-center justify-between px-2 pb-2 pt-2">
          <div className="flex items-center gap-1">
            <button className={`flex h-7 w-7 items-center justify-center rounded-full transition ${passive}`}><AttachSVG className="h-3.5 w-3.5" /></button>
            <button className={`flex h-7 items-center gap-1 rounded-full px-2 text-[11px] font-medium transition ${variant === 'web' ? webOn : passive}`}>
              <GlobeSVG className="h-3.5 w-3.5" />
              {variant === 'web' && <span>Web</span>}
            </button>
            <button className={`flex h-7 items-center gap-1 rounded-full px-2 text-[11px] font-medium transition ${passive}`}>
              <ScopeSVG className="h-3.5 w-3.5" />
            </button>
          </div>
          <div className="flex items-center gap-1">
            <button className={`flex h-7 w-7 items-center justify-center rounded-full transition ${variant === 'voice' ? micOn : passive}`}>
              <MicSVG className="h-3.5 w-3.5" />
            </button>
            <button className="flex h-7 w-7 items-center justify-center rounded-full bg-blue-600 text-white transition hover:bg-blue-500">
              <SendSVG className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>
    );
  };

  /* PRIVATE BUCKETS — mimics the REAL dashboard table at App.jsx:3702
     5-column grid: Name | Created | Files | Storage | Actions */
  const PrivateBucketsDemo = () => {
    const headCls   = isDark ? 'text-white/54' : 'text-slate-500';
    const rowCls    = isDark ? 'border-white/10 hover:bg-white/[0.03]' : 'border-slate-200 hover:bg-slate-50';
    const bodyText  = isDark ? 'text-white/88' : 'text-slate-800';
    const rows = [
      { name: 'Research papers', desc: 'arXiv + meta studies', created: 'Mar 12',  files: 47, storage: '186 MB', tone: 'blue' },
      { name: 'Client Acme Corp', desc: 'engagement files',    created: 'Apr 03',  files: 23, storage: '94 MB',  tone: 'purple' },
      { name: 'Personal notes',   desc: 'journal & references', created: 'Apr 21', files: 12, storage: '8 MB',   tone: 'emerald' },
    ];
    return (
      <div className="relative h-full w-full overflow-hidden rounded-xl p-3">
        <div className={`absolute inset-0 bg-gradient-to-br ${isDark ? 'from-blue-500/8 to-purple-600/8' : 'from-blue-50/80 to-purple-50/80'}`} />
        <div className={`relative h-full overflow-hidden rounded-[0.9rem] border ${isDark ? 'border-white/10 bg-white/[0.03]' : 'border-slate-200 bg-white/72'} backdrop-blur-xl`}>
          {/* Header row — matches real "grid-cols-... text-xs font-semibold uppercase tracking-[0.18em]" */}
          <div className={`grid grid-cols-[minmax(0,2.2fr)_1fr_0.7fr_0.9fr_0.7fr] gap-2 border-b px-3 py-2 text-[9px] font-semibold uppercase tracking-[0.18em] ${headCls} ${isDark ? 'border-white/10' : 'border-slate-200'}`}>
            <span>Name</span>
            <span>Created</span>
            <span>Files</span>
            <span>Storage</span>
            <span>Actions</span>
          </div>
          {rows.map((r) => (
            <div key={r.name} className={`grid grid-cols-[minmax(0,2.2fr)_1fr_0.7fr_0.9fr_0.7fr] items-center gap-2 border-b px-3 py-2 text-[10px] transition ${rowCls} ${bodyText}`}>
              <div className="min-w-0">
                <p className={`truncate font-semibold ${p.title}`}>{r.name}</p>
                <p className={`mt-0.5 truncate text-[9px] ${p.muted}`}>{r.desc}</p>
              </div>
              <span className={p.text}>{r.created}</span>
              <span className={p.text}>{r.files}</span>
              <span className={p.text}>{r.storage}</span>
              <span className={`text-[10px] font-semibold ${isDark ? 'text-red-300' : 'text-red-600'}`}>Delete</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  /* CITED ANSWERS — mirrors the real chat: blue user bubble + assistant text + "N sources" toggle + doc chip rows */
  const CitedAnswersDemo = () => (
    <div className="relative h-full w-full overflow-hidden rounded-xl p-3">
      <div className={`absolute inset-0 bg-gradient-to-br ${isDark ? 'from-emerald-500/10 to-cyan-500/8' : 'from-emerald-50 to-cyan-50'}`} />
      <div className="relative space-y-3">
        {/* user bubble — exact rounded-[1.05rem] bg-blue-600 from real BucketPage */}
        <div className="flex justify-end">
          <div className="w-fit max-w-[80%] break-words rounded-[1.05rem] bg-blue-600 px-3 py-1.5 text-[11px] leading-snug text-white">
            What were the Q3 risks?
          </div>
        </div>
        {/* assistant body text — same line-height as real chat */}
        <div className={`text-[11px] leading-relaxed ${fBody}`}>
          Three risks: <strong className={p.title}>EMEA pressure</strong>, vendor lock-in, and APAC compliance.
        </div>
        {/* Sources toggle — exact pattern from BucketPage */}
        <button className={`flex items-center gap-1.5 text-[11px] font-medium ${fMuted}`}>
          <ChevronSVG className="h-3 w-3 rotate-180" /> 2 sources
        </button>
        <div className="flex flex-wrap gap-1.5">
          {['Q3-strategy.pdf', 'market-research.pdf'].map(c => (
            <span key={c} className={`flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[10px] ${fLine} ${fBody}`}>
              <DocSVG className="h-3 w-3" /> {c}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
  /* ONE LINK, EVERY AI — replicates the REAL McpTokenCard panel at App.jsx:3823.
     A name + Logs/Revoke buttons, the URL pill with a Copy button, then brand logos as recipients. */
  const OneLinkDemo = () => {
    const pillBg  = isDark ? 'bg-white/[0.05]' : 'bg-slate-100/70';
    const codeCol = isDark ? 'text-slate-300' : 'text-slate-500';
    const copyCol = isDark ? 'text-blue-400 hover:text-blue-300' : 'text-blue-600 hover:text-blue-500';
    const logsBtn = isDark ? 'bg-white/[0.06] text-blue-400 hover:bg-blue-500/10' : 'bg-blue-50 text-blue-600 hover:bg-blue-100';
    const revBtn  = isDark ? 'bg-red-500/[0.08] text-red-400 hover:bg-red-500/15' : 'bg-red-50 text-red-600 hover:bg-red-100';
    return (
      <div className="relative h-full w-full overflow-hidden rounded-xl p-3">
        <div className={`absolute inset-0 bg-gradient-to-br ${isDark ? 'from-fuchsia-500/10 to-pink-500/8' : 'from-fuchsia-50 to-pink-50'}`} />
        <div className={`relative h-full space-y-2 rounded-[0.9rem] border p-3 ${isDark ? 'border-white/10 bg-white/[0.03]' : 'border-slate-200 bg-white/82'} backdrop-blur-xl`}>
          {/* Row 1 — token name + Logs + Revoke */}
          <div className="flex items-center gap-2">
            <span className={`flex-1 truncate text-[11px] font-semibold ${p.title}`}>My research bucket</span>
            <button className={`rounded-md px-1.5 py-0.5 text-[10px] font-medium ${logsBtn}`}>Logs</button>
            <button className={`rounded-md px-1.5 py-0.5 text-[10px] font-medium ${revBtn}`}>Revoke</button>
          </div>
          {/* Row 2 — URL pill with Copy button (matches real BucketPage exactly) */}
          <div className={`flex items-center gap-2 rounded-lg px-2.5 py-1.5 ${pillBg}`}>
            <code className={`flex-1 truncate text-[10px] ${codeCol}`}>mcp.aiveilix.com/bucket/mcp_2eSxir…</code>
            <button className={`shrink-0 text-[10px] font-semibold ${copyCol}`}>Copy</button>
          </div>
          {/* Recipient AIs — using real brand logos */}
          <div className={`flex items-center justify-between gap-1.5 rounded-lg border-2 border-dashed px-2.5 py-2 ${isDark ? 'border-white/10' : 'border-slate-300'}`}>
            <div className="flex items-center gap-1.5">
              {TOOLS.slice(0,4).map(t => {
                const Logo = t.Logo;
                return (
                  <div key={t.id} className="flex h-6 w-6 items-center justify-center transition hover:scale-110">
                    <Logo className="h-5 w-5" />
                  </div>
                );
              })}
            </div>
            <span className={`text-[10px] ${p.muted}`}>4 connected</span>
          </div>
          <p className={`text-[9px] ${p.muted}`}>Created Mar 12 · Last used 3m ago</p>
        </div>
      </div>
    );
  };

  /* WEB MODE — shows the real input bar with the Web pill ACTIVE, plus the real source-chip row that appears under the answer */
  const WebModeDemo = () => (
    <div className="relative h-full w-full overflow-hidden rounded-xl p-3">
      <div className={`absolute inset-0 bg-gradient-to-br ${isDark ? 'from-cyan-500/10 to-blue-500/8' : 'from-cyan-50 to-blue-50'}`} />
      <div className="relative space-y-2.5">
        <RealInputBar variant="web" />
        <button className={`flex items-center gap-1.5 text-[11px] font-medium ${fMuted}`}>
          <ChevronSVG className="h-3 w-3 rotate-180" /> 3 sources
        </button>
        <div className="flex flex-wrap gap-1.5">
          <span className={`flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[10px] ${fLine} ${fBody}`}>
            <DocSVG className="h-3 w-3" /> Q3-strategy.pdf
          </span>
          <span className={`flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[10px] ${fLine} ${fBody}`}>
            <span className="inline-block h-3 w-3 rounded-sm bg-orange-500" /> reuters.com
          </span>
          <span className={`flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[10px] ${fLine} ${fBody}`}>
            <span className="inline-block h-3 w-3 rounded-sm bg-black" /> bloomberg.com
          </span>
        </div>
      </div>
    </div>
  );

  /* VOICE INPUT — shows live waveform above + the real input bar in recording state below */
  const VoiceDemo = () => (
    <div className="relative flex h-full w-full flex-col justify-center overflow-hidden rounded-xl p-3">
      <div className={`absolute inset-0 bg-gradient-to-br ${isDark ? 'from-orange-500/10 to-red-500/8' : 'from-orange-50 to-red-50'}`} />
      <div className="relative space-y-3">
        <div className="flex h-10 items-end justify-center gap-[3px] px-2">
          {[8,18,30,16,34,22,40,28,20,36,26,12,22,32,18,10,24,30,16,28].map((h,i) => (
            <span key={i} className={`w-[3px] rounded-full ${isDark ? 'bg-orange-400' : 'bg-orange-500'}`}
              style={{ height: `${h}px`, animation: `lp-pulse 1.4s ease-in-out ${i * 0.05}s infinite` }} />
          ))}
        </div>
        <RealInputBar variant="voice" />
      </div>
    </div>
  );

  /* Layout the user asked for:
     Row 1 (3 cards, equal width): Web mode | Voice input | Cited answers
     Row 2 (2 cards, equal width): Private buckets | One link, every AI    */
  const row1 = [
    { title: 'Web mode',      body: 'Mix fresh internet results with your private docs for time-sensitive questions.', Demo: WebModeDemo,        glow: 'hover:shadow-cyan-500/20' },
    { title: 'Voice input',   body: 'Dictate your question instead of typing. Great for long research sessions.',     Demo: VoiceDemo,          glow: 'hover:shadow-orange-500/20' },
    { title: 'Cited answers', body: 'Every answer points to the exact page. Verify in one click.',                    Demo: CitedAnswersDemo,   glow: 'hover:shadow-emerald-500/20' },
  ];
  const row2 = [
    { title: 'Private buckets',    body: 'Group docs by project or client. Each bucket is isolated — files never leak across.', Demo: PrivateBucketsDemo, glow: 'hover:shadow-blue-500/20' },
    { title: 'One link, every AI', body: 'Paste your MCP link into Claude or ChatGPT once. Your docs follow you everywhere.',   Demo: OneLinkDemo,        glow: 'hover:shadow-fuchsia-500/20' },
  ];

  const Card = ({ f, i }) => {
    const Demo = f.Demo;
    return (
      <BlurFade delay={i * 0.06}>
        <div className={`group flex h-full flex-col gap-3 rounded-2xl border p-4 transition-all duration-300 ease-out hover:-translate-y-1 hover:shadow-2xl ${f.glow} ${isDark ? 'border-white/10 bg-white/[0.025] hover:border-white/30' : 'border-slate-200 bg-white hover:border-slate-300'}`}>
          <div className="flex-1 overflow-hidden">
            <Demo />
          </div>
          <div>
            <h3 className={`text-base font-semibold ${p.title}`}>{f.title}</h3>
            <p className={`mt-1 text-sm leading-relaxed ${p.text}`}>{f.body}</p>
          </div>
        </div>
      </BlurFade>
    );
  };

  return (
    <section className={`border-b ${p.divider}`}>
      <div className="mx-auto max-w-7xl px-6 py-28">
        <BlurFade>
          <p className={`text-center text-xs font-semibold uppercase tracking-[0.22em] ${p.accent}`}>What you get</p>
          <h2 className={`mx-auto mt-3 max-w-2xl text-center text-3xl font-semibold tracking-tight sm:text-5xl ${p.title}`}>
            Built for doc handlers,<br/>not devs.
          </h2>
        </BlurFade>

        {/* Row 1: 3 equal columns at md+, stack on mobile */}
        <div className="mt-16 grid grid-cols-1 gap-4 md:grid-cols-3 md:auto-rows-[22rem]">
          {row1.map((f, i) => <Card key={f.title} f={f} i={i} />)}
        </div>

        {/* Row 2: 2 equal columns */}
        <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2 md:auto-rows-[22rem]">
          {row2.map((f, i) => <Card key={f.title} f={f} i={i + 3} />)}
        </div>
      </div>

      {/* keyframe for the voice waveform */}
      <style>{`
        @keyframes lp-pulse {
          0%, 100% { transform: scaleY(0.6); opacity: 0.6; }
          50%      { transform: scaleY(1);   opacity: 1;   }
        }
      `}</style>
    </section>
  );
}

/* ────────────────────── USE CASES TABS ──────────────────────── */
const USE_CASES = [
  {
    id: 'researchers',
    label: 'Researchers',
    line: 'For literature reviews that span 200 PDFs.',
    body: 'Trace a claim across every paper that ever touched it. Pull verbatim methodology details. Citations stay anchored to the page — no re-skimming.',
    query: 'Compare the sample sizes across the three 2024 RCTs on GLP-1 + cognition.',
  },
  {
    id: 'lawyers',
    label: 'Lawyers',
    line: 'For case files measured in boxes, not pages.',
    body: 'Find the precedent, pull the exact deposition line, ground every answer in a page reference you can cite directly in your filings.',
    query: 'Where did the witness contradict their 2019 deposition?',
  },
  {
    id: 'consultants',
    label: 'Consultants',
    line: 'For engagements buried in 40 client docs.',
    body: 'Onboard a new engagement in an hour. Synthesize interviews, prior decks, and source data side by side — without ever pasting a brief into a chat window.',
    query: 'Summarize the cost drivers the CFO raised across the discovery interviews.',
  },
  {
    id: 'analysts',
    label: 'Analysts',
    line: 'For 10-Ks, transcripts, and board decks.',
    body: 'Extract segment numbers, flag tone shifts across quarters, compare guidance against actuals. Cross-document answers in a single response.',
    query: "How did management's gross-margin commentary change Q2 to Q4?",
  },
];

function UseCases({ p, theme }) {
  const [active, setActive] = useState(USE_CASES[0]);
  const isDark = theme === 'dark';

  return (
    <section className={`border-b ${p.divider}`}>
      <div className="mx-auto max-w-6xl px-6 py-28">
        <BlurFade>
          <p className={`font-mono text-xs uppercase tracking-widest ${isDark ? 'text-slate-300' : 'text-slate-500'}`}>Who it's for</p>
          <h2 className={`mt-3 max-w-2xl text-3xl font-semibold tracking-tight ${p.title} sm:text-5xl`}>
            Built for people who<br/>read for a living.
          </h2>
        </BlurFade>

        <div className="mt-20 grid gap-12 md:grid-cols-[14rem_1fr] md:gap-20">
          {/* LEFT RAIL — persona switcher */}
          <ul className="flex flex-row gap-2 overflow-x-auto pb-2 md:flex-col md:gap-0 md:overflow-visible md:pb-0">
            {USE_CASES.map((u) => {
              const on = u.id === active.id;
              return (
                <li key={u.id}>
                  <button
                    onClick={() => setActive(u)}
                    className={`group flex w-full items-center gap-3 whitespace-nowrap border-l-2 py-2.5 pl-4 text-left text-[15px] font-medium transition ${
                      on
                        ? (isDark ? 'border-blue-400 text-white' : 'border-blue-600 text-slate-900')
                        : (isDark ? 'border-transparent text-slate-300 hover:text-white' : 'border-transparent text-slate-500 hover:text-slate-900')
                    }`}
                  >
                    {u.label}
                  </button>
                </li>
              );
            })}
          </ul>

          {/* DETAIL PANE — swaps with crossfade */}
          <div className="min-h-[20rem]">
            <AnimatePresence mode="wait">
              <motion.div
                key={active.id}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -6 }}
                transition={{ duration: 0.22, ease: 'easeOut' }}
              >
                <p className={`text-sm font-medium ${p.accent}`}>{active.line}</p>
                <p className={`mt-4 text-lg leading-relaxed ${isDark ? 'text-slate-100' : 'text-slate-800'}`}>
                  {active.body}
                </p>

                <div className={`mt-10 rounded-lg border p-5 ${isDark ? 'border-white/15 bg-white/[0.04]' : 'border-slate-200 bg-slate-50/60'}`}>
                  <p className={`font-mono text-[11px] uppercase tracking-widest ${isDark ? 'text-slate-300' : 'text-slate-500'}`}>Example question</p>
                  <p className={`mt-2 font-mono text-[14px] leading-relaxed ${isDark ? 'text-slate-100' : 'text-slate-800'}`}>
                    &gt; {active.query}
                  </p>
                </div>
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ─────────────────────────── PRICING ───────────────────────────── */
const PRICING = [
  {
    name: 'Individual', price: '$15', cadence: '/month', tagline: 'For solo users',
    trial: '15-day free trial',
    star: 'Visual understanding — reads charts, diagrams & images',
    features: ['1 user', '5 buckets', '100 documents', 'Up to 1,800 pages', '5 GB storage', '500 AI chats / month', 'Cited answers — exact page', 'Connect any AI (MCP) — 30 req/min', 'Email support'],
    cta: 'Start 15-day free trial', highlight: true,
  },
  {
    name: 'Team', price: '$49', cadence: '/month', tagline: 'For small teams',
    star: 'Visual understanding — reads charts, diagrams & images',
    features: ['9 users', '20 buckets', '300 documents', 'Up to 4,000 pages', '15 GB storage', '1,800 AI chats / month', 'Cited answers — exact page', 'Team sharing & permissions', 'Connect any AI (MCP) — 60 req/min', 'Priority support'],
    cta: 'Start Team',
  },
  {
    name: 'Enterprise', price: 'Custom', cadence: '', tagline: 'For large teams',
    star: 'Custom limits — documents, visuals, seats & MCP rate',
    features: ['Custom documents & visuals', 'Custom pages & storage', 'More user seats', 'Higher MCP rate limits', 'Priority support & onboarding', 'Invoice billing'],
    cta: 'Contact sales', enterprise: true,
  },
];
function Pricing({ p, theme }) {
  const navigate = useNavigate();
  const [busy, setBusy] = useState('');

  const handlePlan = async (t) => {
    // Enterprise is always a sales conversation.
    if (t.enterprise) { navigate('/enterprise-contact'); return; }
    const plan = t.name.toLowerCase(); // 'individual' | 'team'
    // Not logged in → create an account first.
    if (!sessionStorage.getItem('access_token')) { navigate('/signup'); return; }
    // Logged in → go straight to Stripe Checkout.
    setBusy(plan);
    try {
      const { url } = await billingApi.createCheckout(plan);
      if (url) { window.location.href = url; return; }
      setBusy('');
      window.alert('Could not start checkout. Please try again.');
    } catch (e) {
      // Don't bounce a logged-in user to auth — surface the reason instead.
      setBusy('');
      window.alert(e.message || 'Could not start checkout. Please try again.');
    }
  };

  return (
    <section id="pricing" className={`${p.sectionAlt} border-b ${p.divider}`}>
      <div className="mx-auto max-w-7xl px-6 py-28">
        <BlurFade>
          <p className={`text-center text-xs font-semibold uppercase tracking-[0.22em] ${p.accent}`}>Pricing</p>
          <h2 className={`mx-auto mt-3 max-w-2xl text-center text-3xl font-semibold tracking-tight sm:text-5xl ${p.title}`}>
            Try it free for 15 days. Keep what works.
          </h2>
        </BlurFade>

        <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3 max-w-6xl mx-auto">
          {PRICING.map((t, i) => (
            <BlurFade key={t.name} delay={i * 0.08}>
              <div className={`group relative flex h-full flex-col rounded-2xl p-7 transition-all duration-300 ease-out hover:-translate-y-1 ${p.card} ${
                t.highlight
                  ? 'ring-2 ring-blue-500/50 ' + (theme === 'dark' ? 'hover:shadow-xl hover:shadow-blue-500/20' : 'hover:shadow-xl hover:shadow-blue-500/15')
                  : (theme === 'dark' ? 'hover:shadow-lg hover:shadow-white/5' : 'hover:shadow-lg hover:shadow-slate-300/40')
              }`}>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className={`text-base font-semibold ${p.title}`}>{t.name}</h3>
                    {t.tagline && <p className={`mt-1 text-xs ${p.muted}`}>{t.tagline}</p>}
                  </div>
                  {t.highlight && (
                    <span className="flex-none rounded-full bg-blue-600 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide text-white">Most popular</span>
                  )}
                </div>

                <div className="mt-5 flex items-baseline gap-1">
                  <span className={`text-4xl font-semibold tracking-tight ${p.title}`}>{t.price}</span>
                  <span className={`text-sm ${p.muted}`}>{t.cadence}</span>
                </div>

                {t.trial && (
                  <span className={`mt-3 inline-flex w-fit items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${theme === 'dark' ? 'bg-emerald-500/15 text-emerald-300' : 'bg-emerald-50 text-emerald-700'}`}>
                    <Icon name="check" className="h-3.5 w-3.5" /> {t.trial}
                  </span>
                )}

                {t.star && (
                  <div className={`mt-5 flex items-start gap-2.5 rounded-xl px-3.5 py-3 text-[13px] font-medium ${theme === 'dark' ? 'bg-blue-500/10 text-blue-200 ring-1 ring-inset ring-blue-500/25' : 'bg-blue-50 text-blue-700 ring-1 ring-inset ring-blue-100'}`}>
                    <span aria-hidden className="mt-px text-sm leading-none">⭐</span>
                    <span>{t.star}</span>
                  </div>
                )}

                <ul className={`mt-6 space-y-3 text-sm ${p.text}`}>
                  {t.features.map((f) => (
                    <li key={f} className="flex items-start gap-2.5">
                      <span className={`mt-0.5 flex h-4 w-4 flex-none items-center justify-center rounded-full ${theme === 'dark' ? 'bg-blue-500/15 text-blue-300' : 'bg-blue-50 text-blue-600'}`}>
                        <Icon name="check" className="h-3 w-3" />
                      </span>
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>

                <div className="grow" />

                <button onClick={() => handlePlan(t)} disabled={busy === t.name.toLowerCase()}
                  className={`mt-8 w-full rounded-full px-4 py-2.5 text-sm font-semibold transition disabled:opacity-60 ${
                    t.highlight ? 'bg-blue-600 text-white shadow-sm hover:bg-blue-500' : p.secondary
                  }`}>
                  {busy === t.name.toLowerCase() ? 'Redirecting…' : t.cta}
                </button>
              </div>
            </BlurFade>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ─────────────────────────── FAQ ────────────────────────────── */
const FAQ = [
  { q: 'Who is AIveilix for?', a: 'Anyone who works with documents — researchers, lawyers, consultants, analysts, students. If you read a lot of PDFs and ask AI about them, AIveilix is for you.' },
  { q: 'Do I need to know what MCP is?', a: 'No. Think of MCP as a one-click link that lets Claude, ChatGPT, and other AI tools read your docs. You copy a link, paste it into your AI, done.' },
  { q: 'Are my documents private?', a: 'Yes. Files in a bucket are private to your account, never shared with other users, never used to train public AI models.' },
  { q: 'What file types are supported?', a: 'PDFs (including scanned), Word docs, plain text, CSV, Markdown, and common image formats.' },
  { q: 'Can I cancel anytime?', a: 'Yes. Paid plans are month-to-month. Cancel from your account settings. Your data stays put even after you downgrade.' },
];
function FaqSection({ p }) {
  return (
    <section className={`border-b ${p.divider}`}>
      <div className="mx-auto max-w-3xl px-6 py-28">
        <BlurFade>
          <p className={`text-center text-xs font-semibold uppercase tracking-[0.22em] ${p.accent}`}>FAQ</p>
          <h2 className={`mt-3 text-center text-3xl font-semibold tracking-tight sm:text-5xl ${p.title}`}>Questions, answered.</h2>
        </BlurFade>
        <div className={`mt-10 divide-y rounded-2xl ${p.divider} ${p.soft}`}>
          {FAQ.map((q, i) => (
            <BlurFade key={q.q} delay={i * 0.04}>
              <details className="group px-6 py-5">
                <summary className={`flex cursor-pointer list-none items-center justify-between gap-4 text-base font-medium ${p.title}`}>
                  <span>{q.q}</span>
                  <span className={`flex h-6 w-6 flex-none items-center justify-center rounded-full text-lg font-bold transition group-open:rotate-45 ${p.accent}`}>+</span>
                </summary>
                <p className={`mt-3 text-sm leading-relaxed ${p.text}`}>{q.a}</p>
              </details>
            </BlurFade>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ─────────────────────────── FINAL CTA ──────────────────────────── */
function FinalCta({ p, theme }) {
  const navigate = useNavigate();
  const isDark = theme === 'dark';
  return (
    <section className="relative overflow-hidden">
      <AnimatedGridPattern
        numSquares={40} maxOpacity={isDark ? 0.15 : 0.08} duration={4} repeatDelay={1}
        className="[mask-image:radial-gradient(600px_circle_at_center,white,transparent)] inset-x-0 inset-y-[-20%] h-[140%]"
      />
      <div className="relative mx-auto max-w-7xl px-6 py-28 text-center">
        <BlurFade>
          <div className={`relative mx-auto inline-block overflow-hidden rounded-2xl px-8 py-3 ${p.pillBlue}`}>
            <span className="text-sm font-semibold">Ready when you are</span>
          </div>
        </BlurFade>
        <BlurFade delay={0.1}>
          <h2 className={`mx-auto mt-7 max-w-3xl text-4xl font-semibold tracking-tight sm:text-6xl ${p.title}`}>
            Anchor your docs. <GradientText>Today.</GradientText>
          </h2>
        </BlurFade>
        <BlurFade delay={0.18}>
          <p className={`mx-auto mt-5 max-w-xl text-base ${p.text}`}>
            Free forever for your first bucket. Set up in under a minute. Cancel anytime.
          </p>
        </BlurFade>
        <BlurFade delay={0.26}>
          <div className="mt-10 flex flex-wrap justify-center gap-3">
            <ShimmerButton
              background={isDark ? 'rgba(255,255,255,1)' : 'rgba(15,23,42,1)'}
              shimmerColor={isDark ? '#60a5fa' : '#ffffff'}
              onClick={() => navigate('/signup')}
              className={isDark ? '!text-slate-950 font-semibold px-8 py-3.5 text-base' : '!text-white font-semibold px-8 py-3.5 text-base'}
            >
              Start free <Icon name="arrow" className="ml-2 h-4 w-4" />
            </ShimmerButton>
            <Link to="/docs" className={`inline-flex items-center gap-2 rounded-full px-8 py-3.5 text-base font-medium transition ${p.secondary}`}>
              Read the docs
            </Link>
          </div>
        </BlurFade>
      </div>
    </section>
  );
}

/* ─────────────────────────── FOOTER ────────────────────────────── */
function Footer({ p }) {
  return (
    <footer className={`border-t ${p.divider}`}>
      <div className="mx-auto max-w-7xl px-6 py-12">
        <div className="flex flex-wrap items-center justify-between gap-6">
          <div className="flex items-center gap-2.5">
            <img src="/logo-tight.png" alt="AIveilix" className="h-7 w-7 rounded-md" />
            <span className={`text-sm font-semibold ${p.title}`}>AIveilix</span>
            <span className={`text-xs ${p.muted}`}>© {new Date().getFullYear()}</span>
          </div>
          <nav className="flex flex-wrap gap-x-6 gap-y-2 text-sm">
            <Link to="/docs"           className={`${p.text} transition hover:${p.title}`}>Docs</Link>
            <Link to="/privacy-policy" className={`${p.text} transition hover:${p.title}`}>Privacy</Link>
            <Link to="/terms"          className={`${p.text} transition hover:${p.title}`}>Terms</Link>
            <a   href="mailto:info@aiveilix.com" className={`${p.text} transition hover:${p.title}`}>info@aiveilix.com</a>
          </nav>
        </div>
      </div>
    </footer>
  );
}

/* ────────────────────────── ROOT ─────────────────────────────── */
export default function LandingPage({ theme }) {
  // Sync Tailwind `dark:` class so dark variants kick in on bento etc.
  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') root.classList.add('dark'); else root.classList.remove('dark');
  }, [theme]);

  const p = palettes[theme] || palettes.dark;
  return (
    <main className={p.page}>
      <Nav p={p} theme={theme} />
      <Hero p={p} theme={theme} />
      <TrustStrip p={p} theme={theme} />
      <ProblemSolution p={p} theme={theme} />
      <HowItWorks p={p} theme={theme} />
      <HowMcpWorks p={p} theme={theme} />
      <BucketShowcase p={p} theme={theme} />
      <Features p={p} theme={theme} />
      <UseCases p={p} />
      <Pricing p={p} theme={theme} />
      <FaqSection p={p} />
      <FinalCta p={p} theme={theme} />
      <Footer p={p} />
    </main>
  );
}
