import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  motion, AnimatePresence, useInView, useScroll, useTransform, animate,
} from 'framer-motion';

/* ════════════════════════════════════════════════════════════════════
   AIveilix — Landing v2
   A self-contained, premium marketing page with built-in light/dark.
   Inspired by Stripe · Apple · OpenAI · Mistral · 21st.dev
   Lives at /v2 — does NOT touch the existing landing page.
   ════════════════════════════════════════════════════════════════════ */

/* ─────────────────────────── design tokens ──────────────────────── */
const TOKENS = {
  dark: {
    page:     'bg-[#05070e] text-slate-300',
    heading:  'text-white',
    body:     'text-slate-300',
    muted:    'text-slate-400',
    faint:    'text-slate-500',
    border:   'border-white/10',
    hair:     'border-white/[0.07]',
    card:     'bg-white/[0.025] border border-white/10',
    cardHover:'hover:border-white/25 hover:bg-white/[0.04]',
    chip:     'bg-white/5 border border-white/10 text-slate-300',
    pill:     'bg-blue-500/10 border border-blue-400/30 text-blue-300',
    glass:    'bg-[#070a14]/70 border-white/10',
    inset:    'bg-white/[0.02]',
    window:   'bg-[#0a0e1a] border-white/10',
    windowBar:'bg-white/[0.03] border-white/10',
    sectionAlt:'bg-white/[0.012]',
    ghost:    'border border-white/15 bg-white/[0.03] text-white hover:bg-white/[0.07]',
    footer:   'bg-[#04060c] border-white/10',
  },
  light: {
    page:     'bg-[#fbfcfe] text-slate-600',
    heading:  'text-slate-900',
    body:     'text-slate-600',
    muted:    'text-slate-500',
    faint:    'text-slate-400',
    border:   'border-slate-200',
    hair:     'border-slate-200/70',
    card:     'bg-white border border-slate-200',
    cardHover:'hover:border-slate-300 hover:shadow-[0_18px_50px_-20px_rgba(15,23,42,0.18)]',
    chip:     'bg-white border border-slate-200 text-slate-600',
    pill:     'bg-blue-50 border border-blue-200 text-blue-700',
    glass:    'bg-white/80 border-slate-200',
    inset:    'bg-slate-50',
    window:   'bg-white border-slate-200',
    windowBar:'bg-slate-50 border-slate-200',
    sectionAlt:'bg-slate-50/60',
    ghost:    'border border-slate-300 bg-white text-slate-900 hover:bg-slate-50',
    footer:   'bg-white border-slate-200',
  },
};

/* ─────────────────────────── global effects ─────────────────────── */
function GlobalFx() {
  return (
    <style>{`
      @keyframes aivAurora {
        0%   { transform: translate(0,0) scale(1); }
        33%  { transform: translate(4%,-5%) scale(1.12); }
        66%  { transform: translate(-4%,4%) scale(0.94); }
        100% { transform: translate(0,0) scale(1); }
      }
      @keyframes aivFloat { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-12px); } }
      @keyframes aivGrad  { 0% { background-position: 0% 50%; } 100% { background-position: 200% 50%; } }
      @keyframes aivDash  { to { stroke-dashoffset: -24; } }
      @keyframes aivMarquee { from { transform: translateX(0); } to { transform: translateX(calc(-50% - 1.25rem)); } }
      @keyframes aivPulse { 0%,100% { opacity: .35; } 50% { opacity: 1; } }
      @keyframes aivSheen { 0% { transform: translateX(-120%); } 60%,100% { transform: translateX(220%); } }

      .aiv-grad-text {
        background-image: linear-gradient(100deg,#2563eb,#6366f1,#22d3ee,#6366f1,#2563eb);
        background-size: 200% auto;
        -webkit-background-clip: text; background-clip: text;
        -webkit-text-fill-color: transparent; color: transparent;
        animation: aivGrad 7s linear infinite;
      }
      .aiv-marquee-track { display: flex; width: max-content; animation: aivMarquee 38s linear infinite; }
      .aiv-marquee:hover .aiv-marquee-track { animation-play-state: paused; }
      .aiv-beam { stroke-dasharray: 6 10; animation: aivDash 1.1s linear infinite; }
      .aiv-float { animation: aivFloat 7s ease-in-out infinite; }
      .aiv-sheen::after {
        content: ''; position: absolute; inset: 0; border-radius: inherit; overflow: hidden;
        background: linear-gradient(110deg, transparent 30%, rgba(255,255,255,.55) 50%, transparent 70%);
        transform: translateX(-120%); pointer-events: none;
      }
      .aiv-sheen:hover::after { animation: aivSheen 1.1s ease; }
      @media (prefers-reduced-motion: reduce) {
        .aiv-grad-text, .aiv-marquee-track, .aiv-beam, .aiv-float { animation: none !important; }
      }
    `}</style>
  );
}

/* ─────────────────────────── primitives ─────────────────────────── */
const EASE = [0.22, 1, 0.36, 1];

function Reveal({ children, delay = 0, y = 26, className }) {
  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-80px' }}
      transition={{ duration: 0.75, delay, ease: EASE }}
    >
      {children}
    </motion.div>
  );
}

function Stagger({ children, className, delay = 0 }) {
  return (
    <motion.div
      className={className}
      initial="hide"
      whileInView="show"
      viewport={{ once: true, margin: '-70px' }}
      transition={{ staggerChildren: 0.09, delayChildren: delay }}
    >
      {children}
    </motion.div>
  );
}
const itemV = {
  hide: { opacity: 0, y: 22 },
  show: { opacity: 1, y: 0, transition: { duration: 0.7, ease: EASE } },
};

function GradientText({ children }) {
  return <span className="aiv-grad-text">{children}</span>;
}

function CountUp({ to, suffix = '', prefix = '', duration = 1.7, decimals = 0 }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-60px' });
  const [val, setVal] = useState(0);
  useEffect(() => {
    if (!inView) return;
    const controls = animate(0, to, { duration, ease: EASE, onUpdate: (v) => setVal(v) });
    return () => controls.stop();
  }, [inView, to, duration]);
  const formatted = decimals ? val.toFixed(decimals) : Math.round(val).toLocaleString();
  return <span ref={ref}>{prefix}{formatted}{suffix}</span>;
}

function PrimaryButton({ children, onClick, className = '' }) {
  return (
    <button
      onClick={onClick}
      className={`group relative inline-flex items-center justify-center gap-2 overflow-hidden rounded-full bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-600 bg-[length:200%_auto] px-7 py-3.5 text-base font-semibold text-white shadow-[0_10px_30px_-8px_rgba(37,99,235,0.6)] transition-[background-position,transform,box-shadow] duration-500 hover:bg-[position:100%] hover:shadow-[0_16px_40px_-10px_rgba(37,99,235,0.7)] active:scale-[0.98] aiv-sheen ${className}`}
    >
      {children}
    </button>
  );
}

/* ─────────────────────────── icons ──────────────────────────────── */
function Ico({ name, className }) {
  const c = { className: className || 'h-5 w-5', viewBox: '0 0 24 24', fill: 'none', strokeWidth: 1.7, stroke: 'currentColor', strokeLinecap: 'round', strokeLinejoin: 'round' };
  switch (name) {
    case 'arrow':   return <svg {...c}><path d="M5 12h14M13 6l6 6-6 6" /></svg>;
    case 'check':   return <svg {...c}><path d="M5 12l4 4 10-10" /></svg>;
    case 'sun':     return <svg {...c}><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5L19 19M19 5l-1.5 1.5M6.5 17.5L5 19" /></svg>;
    case 'moon':    return <svg {...c}><path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5Z" /></svg>;
    case 'spark':   return <svg {...c}><path d="M12 3l1.7 5L19 9.7l-5.3 1.7L12 16l-1.7-4.6L5 9.7 10.3 8 12 3Z" /></svg>;
    case 'upload':  return <svg {...c}><path d="M12 16V4m0 0L8 8m4-4 4 4" /><path d="M4 16v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" /></svg>;
    case 'link':    return <svg {...c}><path d="M10 14a4 4 0 0 0 5.66 0l3-3a4 4 0 1 0-5.66-5.66l-1.5 1.5" /><path d="M14 10a4 4 0 0 0-5.66 0l-3 3a4 4 0 1 0 5.66 5.66l1.5-1.5" /></svg>;
    case 'chat':    return <svg {...c}><path d="M4 5h16v11H8l-4 4V5Z" /><path d="M8 10h8M8 13h5" /></svg>;
    case 'quote':   return <svg {...c}><path d="M7 7h4v6H7zM13 7h4v6h-4z" /><path d="M7 13c0 2-1 3-2 4M13 13c0 2-1 3-2 4" /></svg>;
    case 'eye':     return <svg {...c}><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z" /><circle cx="12" cy="12" r="3" /></svg>;
    case 'lock':    return <svg {...c}><rect x="4" y="11" width="16" height="9" rx="2" /><path d="M8 11V8a4 4 0 1 1 8 0v3" /></svg>;
    case 'search':  return <svg {...c}><circle cx="11" cy="11" r="7" /><path d="m20 20-3.2-3.2" /></svg>;
    case 'branch':  return <svg {...c}><circle cx="6" cy="6" r="2.5" /><circle cx="6" cy="18" r="2.5" /><circle cx="18" cy="9" r="2.5" /><path d="M6 8.5v7M6 12h6a4 4 0 0 0 4-4" /></svg>;
    case 'cpu':     return <svg {...c}><rect x="7" y="7" width="10" height="10" rx="2" /><path d="M9 1v3M15 1v3M9 20v3M15 20v3M1 9h3M1 15h3M20 9h3M20 15h3" /></svg>;
    case 'globe':   return <svg {...c}><circle cx="12" cy="12" r="9" /><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18" /></svg>;
    case 'bolt':    return <svg {...c}><path d="M13 2 4 14h7l-1 8 9-12h-7l1-8Z" /></svg>;
    case 'shield':  return <svg {...c}><path d="M12 3l8 4v5c0 5-3.5 8.5-8 9-4.5-.5-8-4-8-9V7l8-4Z" /></svg>;
    case 'doc':     return <svg {...c}><path d="M6 2h8l4 4v16H6z" /><path d="M14 2v4h4M9 13h6M9 17h6M9 9h2" /></svg>;
    case 'folder':  return <svg {...c}><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z" /></svg>;
    case 'plus':    return <svg {...c}><path d="M12 5v14M5 12h14" /></svg>;
    case 'minus':   return <svg {...c}><path d="M5 12h14" /></svg>;
    case 'x':       return <svg {...c}><path d="M6 6l12 12M18 6 6 18" /></svg>;
    case 'menu':    return <svg {...c}><path d="M4 7h16M4 12h16M4 17h16" /></svg>;
    default:        return null;
  }
}

/* ─────────────────────────── theme toggle ───────────────────────── */
function ThemeToggle({ theme, onToggle, t }) {
  const isDark = theme === 'dark';
  return (
    <button
      onClick={onToggle}
      aria-label="Toggle theme"
      className={`relative flex h-9 w-[4.4rem] items-center rounded-full border px-1 transition ${t.ghost}`}
    >
      <motion.span
        layout
        transition={{ type: 'spring', stiffness: 500, damping: 34 }}
        className={`absolute flex h-7 w-7 items-center justify-center rounded-full ${isDark ? 'left-1 bg-blue-500/20 text-blue-300' : 'left-[calc(100%-2rem)] bg-amber-100 text-amber-600'}`}
      >
        <Ico name={isDark ? 'moon' : 'sun'} className="h-4 w-4" />
      </motion.span>
    </button>
  );
}

/* ════════════════════════════════ NAV ═══════════════════════════════ */
function Nav({ t, theme, onToggle }) {
  const navigate = useNavigate();
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 16);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const links = [['Product', '#features'], ['How it works', '#how'], ['Pricing', '#pricing']];

  return (
    <header className={`fixed inset-x-0 top-0 z-50 transition-all duration-300 ${scrolled ? `backdrop-blur-xl border-b ${t.glass}` : 'border-b border-transparent'}`}>
      <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-3.5 sm:px-6">
        <Link to="/v2" className="flex items-center gap-2.5">
          <img src="/logo-tight.png" alt="AIveilix" className="h-8 w-8 rounded-lg" />
          <span className={`text-[1.05rem] font-bold tracking-tight ${t.heading}`}>AIveilix</span>
        </Link>

        <nav className="hidden items-center gap-8 md:flex">
          {links.map(([l, h]) => (
            <a key={l} href={h} className={`text-sm font-medium transition hover:opacity-100 ${t.muted} hover:${t.heading.replace('text-', 'text-')}`}>{l}</a>
          ))}
          <Link to="/docs" className={`text-sm font-medium ${t.muted}`}>Docs</Link>
        </nav>

        <div className="flex items-center gap-2.5">
          <ThemeToggle theme={theme} onToggle={onToggle} t={t} />
          <Link to="/login" className={`hidden rounded-full px-3.5 py-1.5 text-sm font-medium transition sm:inline-flex ${t.ghost}`}>Sign in</Link>
          <button onClick={() => navigate('/signup')} className="hidden rounded-full bg-blue-600 px-4 py-1.5 text-sm font-semibold text-white transition hover:bg-blue-500 sm:inline-flex">Start free</button>
          <button onClick={() => setOpen((v) => !v)} className={`md:hidden rounded-full border p-2 ${t.ghost}`} aria-label="Menu">
            <Ico name={open ? 'x' : 'menu'} className="h-5 w-5" />
          </button>
        </div>
      </div>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className={`overflow-hidden border-t backdrop-blur-xl md:hidden ${t.glass}`}
          >
            <div className="flex flex-col gap-1 px-6 py-4">
              {[...links, ['Docs', '/docs']].map(([l, h]) => (
                <a key={l} href={h} onClick={() => setOpen(false)} className={`rounded-lg px-2 py-2.5 text-sm font-medium ${t.body}`}>{l}</a>
              ))}
              <div className="mt-2 flex gap-2">
                <Link to="/login" className={`flex-1 rounded-full border px-4 py-2 text-center text-sm font-medium ${t.ghost}`}>Sign in</Link>
                <button onClick={() => navigate('/signup')} className="flex-1 rounded-full bg-blue-600 px-4 py-2 text-sm font-semibold text-white">Start free</button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}

/* ════════════════════════════════ HERO ══════════════════════════════ */
function Aurora({ isDark }) {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      <div
        className="absolute -top-40 left-1/2 h-[42rem] w-[42rem] -translate-x-1/2 rounded-full blur-[120px]"
        style={{ background: isDark ? 'radial-gradient(circle, rgba(37,99,235,0.34), transparent 65%)' : 'radial-gradient(circle, rgba(59,130,246,0.20), transparent 65%)', animation: 'aivAurora 18s ease-in-out infinite' }}
      />
      <div
        className="absolute top-20 -left-24 h-[26rem] w-[26rem] rounded-full blur-[110px]"
        style={{ background: isDark ? 'radial-gradient(circle, rgba(99,102,241,0.28), transparent 65%)' : 'radial-gradient(circle, rgba(99,102,241,0.16), transparent 65%)', animation: 'aivAurora 22s ease-in-out infinite reverse' }}
      />
      <div
        className="absolute top-10 -right-24 h-[28rem] w-[28rem] rounded-full blur-[120px]"
        style={{ background: isDark ? 'radial-gradient(circle, rgba(34,211,238,0.20), transparent 65%)' : 'radial-gradient(circle, rgba(34,211,238,0.12), transparent 65%)', animation: 'aivAurora 26s ease-in-out infinite' }}
      />
    </div>
  );
}

function GridBg({ isDark }) {
  const stroke = isDark ? 'rgba(255,255,255,0.05)' : 'rgba(15,23,42,0.05)';
  return (
    <div
      className="pointer-events-none absolute inset-0 [mask-image:radial-gradient(70%_55%_at_50%_30%,black,transparent)]"
      style={{ backgroundImage: `linear-gradient(${stroke} 1px,transparent 1px),linear-gradient(90deg,${stroke} 1px,transparent 1px)`, backgroundSize: '54px 54px' }}
    />
  );
}

function Hero({ t, theme }) {
  const navigate = useNavigate();
  const isDark = theme === 'dark';
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start start', 'end start'] });
  const rotateX = useTransform(scrollYProgress, [0, 0.5], [16, 0]);
  const scale = useTransform(scrollYProgress, [0, 0.5], [0.94, 1]);
  const yShift = useTransform(scrollYProgress, [0, 1], [0, -60]);

  return (
    <section ref={ref} className="relative overflow-hidden pt-32 sm:pt-40">
      <Aurora isDark={isDark} />
      <GridBg isDark={isDark} />

      <div className="relative mx-auto max-w-5xl px-5 text-center sm:px-6">
        <Reveal delay={0.02}>
          <span className={`inline-flex items-center gap-2 rounded-full px-3.5 py-1.5 text-xs font-semibold ${t.pill}`}>
            <Ico name="spark" className="h-3.5 w-3.5" />
            Persistent knowledge for every AI
          </span>
        </Reveal>

        <Reveal delay={0.1}>
          <h1 className={`mx-auto mt-7 max-w-4xl text-[2.6rem] font-bold leading-[1.05] tracking-tight sm:text-6xl md:text-7xl ${t.heading}`}>
            Anchor your docs.
            <br />
            Use them in <GradientText>every AI</GradientText>.
          </h1>
        </Reveal>

        <Reveal delay={0.2}>
          <p className={`mx-auto mt-7 max-w-2xl text-lg leading-relaxed sm:text-xl ${t.body}`}>
            Upload once into a private bucket. Get a single link Claude, ChatGPT, Cursor — any modern AI — can read on demand.{' '}
            <span className={`font-semibold ${t.heading}`}>Stop re-uploading the same files to every chat.</span>
          </p>
        </Reveal>

        <Reveal delay={0.3}>
          <div className="mt-9 flex flex-wrap items-center justify-center gap-3">
            <PrimaryButton onClick={() => navigate('/signup')}>
              Start free — no card
              <Ico name="arrow" className="h-4 w-4 transition group-hover:translate-x-0.5" />
            </PrimaryButton>
            <a href="#how" className={`inline-flex items-center gap-2 rounded-full border px-6 py-3.5 text-base font-medium transition ${t.ghost}`}>
              See how it works
            </a>
          </div>
        </Reveal>

        <Reveal delay={0.4}>
          <div className={`mt-9 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-sm ${t.muted}`}>
            {['Cited to the page', 'Private buckets', 'Works with Claude & ChatGPT', 'No re-uploading'].map((x) => (
              <span key={x} className="flex items-center gap-1.5">
                <Ico name="check" className={`h-4 w-4 ${isDark ? 'text-blue-400' : 'text-blue-600'}`} /> {x}
              </span>
            ))}
          </div>
        </Reveal>
      </div>

      {/* floating product window */}
      <motion.div style={{ y: yShift }} className="relative mx-auto mt-16 max-w-5xl px-5 sm:mt-20 sm:px-6" >
        <div style={{ perspective: 1400 }}>
          <motion.div style={{ rotateX, scale, transformStyle: 'preserve-3d' }}>
            <AppMockup t={t} isDark={isDark} />
          </motion.div>
        </div>
        <div className={`pointer-events-none absolute inset-x-0 bottom-0 h-40 bg-gradient-to-b from-transparent ${isDark ? 'to-[#05070e]' : 'to-[#fbfcfe]'}`} />
      </motion.div>
    </section>
  );
}

/* polished faux app UI — bucket + cited chat */
function AppMockup({ t, isDark }) {
  const files = [
    { n: 'Q4-financials.pdf', s: '2.4 MB' },
    { n: 'product-spec.docx', s: '880 KB' },
    { n: 'market-research.pdf', s: '5.1 MB' },
    { n: 'board-deck.pptx', s: '12 MB' },
  ];
  return (
    <div className={`relative overflow-hidden rounded-2xl border shadow-2xl ${t.window}`}>
      {/* glow border */}
      <div className="pointer-events-none absolute -inset-px rounded-2xl" style={{ background: 'linear-gradient(120deg, rgba(37,99,235,0.4), transparent 30%, transparent 70%, rgba(34,211,238,0.35))', WebkitMask: 'linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0)', WebkitMaskComposite: 'xor', maskComposite: 'exclude', padding: 1 }} />
      {/* title bar */}
      <div className={`flex items-center gap-2 border-b px-4 py-3 ${t.windowBar}`}>
        <span className="h-3 w-3 rounded-full bg-[#ff5f57]" />
        <span className="h-3 w-3 rounded-full bg-[#febc2e]" />
        <span className="h-3 w-3 rounded-full bg-[#28c840]" />
        <div className={`ml-3 flex items-center gap-2 rounded-md px-2.5 py-1 text-xs ${t.chip}`}>
          <Ico name="lock" className="h-3 w-3" /> mcp.aiveilix.com/bucket/•••
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-[200px_1fr]">
        {/* sidebar */}
        <div className={`hidden border-r p-3 sm:block ${t.hair} ${t.inset}`}>
          <div className="flex items-center gap-2 px-2 py-1.5">
            <span className="flex h-6 w-6 items-center justify-center rounded-md bg-blue-600 text-white"><Ico name="folder" className="h-3.5 w-3.5" /></span>
            <span className={`text-sm font-semibold ${t.heading}`}>Research</span>
          </div>
          <div className="mt-2 space-y-0.5">
            {files.map((f, i) => (
              <div key={f.n} className={`flex items-center gap-2 rounded-md px-2 py-1.5 text-xs ${i === 0 ? (isDark ? 'bg-white/5' : 'bg-blue-50') : ''} ${t.muted}`}>
                <Ico name="doc" className="h-3.5 w-3.5 flex-none" />
                <span className="truncate">{f.n}</span>
              </div>
            ))}
          </div>
          <div className={`mt-3 flex items-center gap-1.5 rounded-md border border-dashed px-2 py-2 text-[11px] ${t.hair} ${t.faint}`}>
            <Ico name="plus" className="h-3.5 w-3.5" /> Drop files
          </div>
        </div>

        {/* chat */}
        <div className="flex flex-col gap-3 p-4 sm:p-5">
          <div className="flex justify-end">
            <div className={`max-w-[80%] rounded-2xl rounded-br-md px-3.5 py-2.5 text-sm ${isDark ? 'bg-blue-600 text-white' : 'bg-blue-600 text-white'}`}>
              What was our Q4 net revenue, and how did it compare to forecast?
            </div>
          </div>
          <div className="flex justify-start">
            <div className={`max-w-[88%] rounded-2xl rounded-bl-md border px-3.5 py-3 text-sm ${t.card} ${t.body}`}>
              <p>Q4 net revenue was <span className={`font-semibold ${t.heading}`}>$48.2M</span>, beating the forecast of $44.0M by <span className={`font-semibold ${isDark ? 'text-emerald-400' : 'text-emerald-600'}`}>+9.5%</span>. Growth was driven mainly by the enterprise segment.</p>
              <div className="mt-2.5 flex flex-wrap gap-1.5">
                <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium ${t.pill}`}>
                  <Ico name="doc" className="h-3 w-3" /> Q4-financials.pdf · p.12
                </span>
                <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium ${t.pill}`}>
                  <Ico name="doc" className="h-3 w-3" /> board-deck.pptx · slide 7
                </span>
              </div>
            </div>
          </div>
          <div className={`mt-1 flex items-center gap-2 rounded-xl border px-3 py-2.5 ${t.card}`}>
            <Ico name="chat" className={`h-4 w-4 ${t.faint}`} />
            <span className={`text-sm ${t.faint}`}>Ask anything about your docs…</span>
            <span className="ml-auto flex h-7 w-7 items-center justify-center rounded-lg bg-blue-600 text-white"><Ico name="arrow" className="h-3.5 w-3.5" /></span>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ════════════════════════════ LOGO CLOUD ═══════════════════════════ */
function LogoCloud({ t, isDark }) {
  const tools = ['Claude', 'ChatGPT', 'Cursor', 'Claude Desktop', 'Zed', 'Continue', 'Goose', 'Cline', 'MCP Inspector'];
  const row = [...tools, ...tools];
  return (
    <section className="relative py-14">
      <Reveal>
        <p className={`mb-7 text-center text-xs font-semibold uppercase tracking-[0.24em] ${t.faint}`}>
          Plug into the AI you already use
        </p>
      </Reveal>
      <div className="aiv-marquee relative overflow-hidden">
        <div className="aiv-marquee-track gap-10">
          {row.map((tool, i) => (
            <div key={i} className={`flex flex-none items-center gap-2 text-xl font-semibold ${isDark ? 'text-white/55' : 'text-slate-500'}`}>
              <Ico name="spark" className={`h-4 w-4 ${isDark ? 'text-blue-400/70' : 'text-blue-500/70'}`} />
              {tool}
            </div>
          ))}
        </div>
        <div className={`pointer-events-none absolute inset-y-0 left-0 w-28 bg-gradient-to-r ${isDark ? 'from-[#05070e]' : 'from-[#fbfcfe]'} to-transparent`} />
        <div className={`pointer-events-none absolute inset-y-0 right-0 w-28 bg-gradient-to-l ${isDark ? 'from-[#05070e]' : 'from-[#fbfcfe]'} to-transparent`} />
      </div>
    </section>
  );
}

/* ════════════════════════ PROBLEM / SHIFT ══════════════════════════ */
function Section({ id, eyebrow, title, sub, t, children, className = '' }) {
  return (
    <section id={id} className={`relative py-24 sm:py-28 ${className}`}>
      <div className="mx-auto max-w-7xl px-5 sm:px-6">
        <Reveal>
          <div className="mx-auto max-w-2xl text-center">
            {eyebrow && <p className="mb-3 text-sm font-semibold uppercase tracking-[0.18em] text-blue-500">{eyebrow}</p>}
            <h2 className={`text-3xl font-bold tracking-tight sm:text-[2.6rem] sm:leading-[1.1] ${t.heading}`}>{title}</h2>
            {sub && <p className={`mx-auto mt-4 max-w-xl text-lg ${t.body}`}>{sub}</p>}
          </div>
        </Reveal>
        {children}
      </div>
    </section>
  );
}

function ProblemShift({ t, isDark }) {
  const before = [
    'Drag the same 30 PDFs into every new chat',
    'Pay to reprocess the entire context, every time',
    'Big files get truncated — answers come back shallow',
    'No citations — you can’t verify anything',
    'Switch tools and start the upload over',
  ];
  const after = [
    'Upload once — files stay indexed forever',
    'Your AI fetches only the exact chunks it needs',
    'Up to 5,000 files per bucket, no context pressure',
    'Every answer cited to the exact page',
    'One link works across every AI you use',
  ];
  return (
    <Section
      id="problem"
      eyebrow="The shift"
      title="The blank-slate tax is real"
      sub="Every AI session forgets what you uploaded. AIveilix gives your knowledge a permanent home."
      t={t}
    >
      <div className="mx-auto mt-14 grid max-w-4xl gap-5 md:grid-cols-2">
        <Reveal delay={0.05}>
          <div className={`h-full rounded-2xl border p-6 sm:p-7 ${isDark ? 'border-red-500/20 bg-red-500/[0.04]' : 'border-red-200 bg-red-50/50'}`}>
            <span className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold ${isDark ? 'bg-red-500/15 text-red-300' : 'bg-red-100 text-red-700'}`}>
              <Ico name="x" className="h-3.5 w-3.5" /> Without AIveilix
            </span>
            <ul className="mt-5 space-y-3.5">
              {before.map((x) => (
                <li key={x} className="flex items-start gap-3">
                  <span className={`mt-0.5 flex h-5 w-5 flex-none items-center justify-center rounded-full ${isDark ? 'bg-red-500/15 text-red-300' : 'bg-red-100 text-red-600'}`}><Ico name="x" className="h-3 w-3" /></span>
                  <span className={`text-[0.95rem] ${t.body}`}>{x}</span>
                </li>
              ))}
            </ul>
          </div>
        </Reveal>
        <Reveal delay={0.12}>
          <div className={`relative h-full overflow-hidden rounded-2xl border p-6 sm:p-7 ${isDark ? 'border-blue-400/25 bg-blue-500/[0.05]' : 'border-blue-200 bg-blue-50/50'}`}>
            <span className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold ${isDark ? 'bg-blue-500/15 text-blue-300' : 'bg-blue-100 text-blue-700'}`}>
              <Ico name="check" className="h-3.5 w-3.5" /> With AIveilix
            </span>
            <ul className="mt-5 space-y-3.5">
              {after.map((x) => (
                <li key={x} className="flex items-start gap-3">
                  <span className={`mt-0.5 flex h-5 w-5 flex-none items-center justify-center rounded-full ${isDark ? 'bg-blue-500/20 text-blue-300' : 'bg-blue-100 text-blue-600'}`}><Ico name="check" className="h-3 w-3" /></span>
                  <span className={`text-[0.95rem] ${t.body}`}>{x}</span>
                </li>
              ))}
            </ul>
          </div>
        </Reveal>
      </div>
      <Reveal delay={0.18}>
        <p className={`mx-auto mt-10 max-w-2xl text-center text-base ${t.muted}`}>
          <span className={`font-semibold ${t.heading}`}>The math:</span> 5 chats a day × 5 minutes of re-uploading ≈{' '}
          <span className={`font-semibold ${t.heading}`}>10 hours saved every month</span>. That’s a working day, back.
        </p>
      </Reveal>
    </Section>
  );
}

/* ════════════════════════════ HOW IT WORKS ═════════════════════════ */
function HowItWorks({ t, isDark }) {
  const steps = [
    { ico: 'upload', n: '01', title: 'Create a bucket, drop your docs', body: 'Upload PDFs, slides, spreadsheets, images. We parse text and visuals into one searchable knowledge base.' },
    { ico: 'link', n: '02', title: 'Copy your private MCP link', body: 'Every bucket gets a unique link. Paste it into Claude, ChatGPT, Cursor — any MCP-ready AI.' },
    { ico: 'chat', n: '03', title: 'Ask anything, anywhere', body: 'Your AI fetches the exact chunks it needs and answers with citations down to the page.' },
  ];
  return (
    <Section id="how" eyebrow="How it works" title="Live in under a minute" sub="Three steps from a pile of files to knowledge your AI can use on demand." t={t} className={isDark ? '' : t.sectionAlt}>
      <Stagger className="mt-14 grid gap-6 md:grid-cols-3" delay={0.05}>
        {steps.map((s, i) => (
          <motion.div key={s.n} variants={itemV} className="relative">
            {i < steps.length - 1 && (
              <div className="absolute right-[-1.6rem] top-12 hidden h-px w-12 md:block" style={{ background: isDark ? 'linear-gradient(90deg,rgba(59,130,246,0.5),transparent)' : 'linear-gradient(90deg,rgba(59,130,246,0.4),transparent)' }} />
            )}
            <div className={`h-full rounded-2xl border p-7 transition ${t.card} ${t.cardHover}`}>
              <div className="flex items-center justify-between">
                <span className={`flex h-12 w-12 items-center justify-center rounded-xl ${isDark ? 'bg-blue-500/15 text-blue-300' : 'bg-blue-50 text-blue-600'}`}>
                  <Ico name={s.ico} className="h-6 w-6" />
                </span>
                <span className={`text-3xl font-bold ${t.faint}`}>{s.n}</span>
              </div>
              <h3 className={`mt-5 text-lg font-semibold ${t.heading}`}>{s.title}</h3>
              <p className={`mt-2 text-[0.95rem] leading-relaxed ${t.body}`}>{s.body}</p>
            </div>
          </motion.div>
        ))}
      </Stagger>
    </Section>
  );
}

/* ════════════════════════════ BENTO FEATURES ═══════════════════════ */
function Bento({ t, isDark }) {
  const card = `group relative overflow-hidden rounded-2xl border p-6 transition ${t.card} ${t.cardHover}`;
  const FeatIcon = ({ name }) => (
    <span className={`flex h-11 w-11 items-center justify-center rounded-xl ${isDark ? 'bg-blue-500/15 text-blue-300' : 'bg-blue-50 text-blue-600'}`}>
      <Ico name={name} className="h-5 w-5" />
    </span>
  );
  return (
    <Section id="features" eyebrow="Why AIveilix" title="Built for knowledge that lasts" sub="A managed RAG + MCP layer that turns your documents into something every AI can reason over." t={t}>
      <div className="mt-14 grid gap-5 md:grid-cols-3 md:grid-rows-2">
        {/* big feature */}
        <Reveal className="md:col-span-2 md:row-span-1" delay={0.04}>
          <div className={`${card} h-full`}>
            <div className="pointer-events-none absolute -right-16 -top-16 h-48 w-48 rounded-full bg-blue-500/20 blur-3xl opacity-60 transition group-hover:opacity-100" />
            <FeatIcon name="check" />
            <h3 className={`mt-5 text-xl font-semibold ${t.heading}`}>Cited to the page</h3>
            <p className={`mt-2 max-w-md text-[0.95rem] ${t.body}`}>Every answer comes with the exact file and page number. Click to verify in one tap — no more “did it hallucinate that?”</p>
            <div className="mt-5 flex flex-wrap gap-2">
              {['contract.pdf · p.4', 'report.pdf · p.22', 'deck.pptx · slide 9'].map((c) => (
                <span key={c} className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium ${t.pill}`}><Ico name="doc" className="h-3 w-3" />{c}</span>
              ))}
            </div>
          </div>
        </Reveal>

        <Reveal delay={0.1}>
          <div className={`${card} h-full`}>
            <FeatIcon name="eye" />
            <h3 className={`mt-5 text-lg font-semibold ${t.heading}`}>Visual understanding</h3>
            <p className={`mt-2 text-[0.95rem] ${t.body}`}>Charts, diagrams, and text inside images are read too — not just the words on the page.</p>
          </div>
        </Reveal>

        <Reveal delay={0.06}>
          <div className={`${card} h-full`}>
            <FeatIcon name="lock" />
            <h3 className={`mt-5 text-lg font-semibold ${t.heading}`}>Private buckets</h3>
            <p className={`mt-2 text-[0.95rem] ${t.body}`}>Group docs by project or client. Each bucket is isolated — files never leak across.</p>
          </div>
        </Reveal>

        <Reveal delay={0.1}>
          <div className={`${card} h-full`}>
            <FeatIcon name="search" />
            <h3 className={`mt-5 text-lg font-semibold ${t.heading}`}>Hybrid search + rerank</h3>
            <p className={`mt-2 text-[0.95rem] ${t.body}`}>Dense + sparse retrieval, then a reranker narrows to the few chunks that actually matter.</p>
          </div>
        </Reveal>

        <Reveal delay={0.14}>
          <div className={`${card} h-full`}>
            <FeatIcon name="cpu" />
            <h3 className={`mt-5 text-lg font-semibold ${t.heading}`}>Bring your own model</h3>
            <p className={`mt-2 text-[0.95rem] ${t.body}`}>Claude, Gemini, GPT-4o, Kimi — connect the model you prefer with your own key.</p>
          </div>
        </Reveal>
      </div>
    </Section>
  );
}

/* ════════════════════ ONE LINK, EVERY AI (beams) ═══════════════════ */
function MCPBeams({ t, isDark }) {
  const nodes = ['Claude', 'ChatGPT', 'Cursor', 'Zed', 'Continue', 'Goose'];
  const line = isDark ? 'rgba(59,130,246,0.55)' : 'rgba(37,99,235,0.45)';
  const faint = isDark ? 'rgba(148,163,184,0.18)' : 'rgba(148,163,184,0.3)';
  return (
    <Section id="mcp" eyebrow="The MCP layer" title="One link. Every AI." sub="No SDK, no glue code. Drop your bucket’s MCP URL into any compatible client and your docs are instantly available." t={t} className={isDark ? '' : t.sectionAlt}>
      <Reveal delay={0.06}>
        <div className={`relative mx-auto mt-14 max-w-3xl overflow-hidden rounded-3xl border p-8 sm:p-12 ${t.card}`}>
          <svg viewBox="0 0 600 360" className="mx-auto w-full max-w-2xl" role="img" aria-label="AIveilix connecting to multiple AI clients">
            {/* center node coords */}
            {(() => {
              const cx = 300, cy = 180;
              const pts = [
                [70, 70], [300, 40], [530, 70],
                [70, 290], [300, 320], [530, 290],
              ];
              return (
                <>
                  {pts.map((p, i) => (
                    <g key={i}>
                      <path d={`M${cx},${cy} L${p[0]},${p[1]}`} stroke={faint} strokeWidth="1.5" fill="none" />
                      <path d={`M${cx},${cy} L${p[0]},${p[1]}`} stroke={line} strokeWidth="2" fill="none" className="aiv-beam" style={{ animationDelay: `${i * 0.18}s` }} />
                    </g>
                  ))}
                  {pts.map((p, i) => (
                    <g key={`n${i}`}>
                      <rect x={p[0] - 52} y={p[1] - 17} width="104" height="34" rx="17" fill={isDark ? '#0a0e1a' : '#ffffff'} stroke={isDark ? 'rgba(255,255,255,0.12)' : 'rgba(15,23,42,0.12)'} strokeWidth="1" />
                      <text x={p[0]} y={p[1] + 4} textAnchor="middle" fontSize="13" fontWeight="600" fill={isDark ? '#cbd5e1' : '#475569'} fontFamily="Plus Jakarta Sans, sans-serif">{nodes[i]}</text>
                    </g>
                  ))}
                  {/* center */}
                  <circle cx={cx} cy={cy} r="46" fill="url(#aivCore)" />
                  <circle cx={cx} cy={cy} r="46" fill="none" stroke={line} strokeWidth="1.5" opacity="0.6" />
                  <text x={cx} y={cy + 5} textAnchor="middle" fontSize="14" fontWeight="700" fill="#ffffff" fontFamily="Plus Jakarta Sans, sans-serif">AIveilix</text>
                  <defs>
                    <radialGradient id="aivCore" cx="50%" cy="35%" r="75%">
                      <stop offset="0%" stopColor="#3b82f6" />
                      <stop offset="100%" stopColor="#1e3a8a" />
                    </radialGradient>
                  </defs>
                </>
              );
            })()}
          </svg>
          <div className={`mx-auto mt-6 flex max-w-md items-center gap-2 rounded-xl border px-4 py-3 font-mono text-sm ${t.inset} ${t.hair}`}>
            <Ico name="link" className={`h-4 w-4 flex-none ${isDark ? 'text-blue-400' : 'text-blue-600'}`} />
            <span className={`truncate ${t.body}`}>mcp.aiveilix.com/bucket/<span className={t.heading}>your-key</span></span>
          </div>
        </div>
      </Reveal>
    </Section>
  );
}

/* ════════════════════════════════ STATS ════════════════════════════ */
function Stats({ t, isDark }) {
  const stats = [
    { to: 5000, suffix: '+', label: 'Files per bucket' },
    { to: 1, prefix: '<', suffix: ' min', label: 'To go live' },
    { to: 100, suffix: '%', label: 'Answers cited' },
    { to: 9, prefix: '~', suffix: ' hrs', label: 'Saved / month' },
  ];
  return (
    <section className="relative py-20">
      <div className="mx-auto max-w-6xl px-5 sm:px-6">
        <Reveal>
          <div className={`grid grid-cols-2 gap-px overflow-hidden rounded-3xl border md:grid-cols-4 ${t.border} ${isDark ? 'bg-white/10' : 'bg-slate-200'}`}>
            {stats.map((s) => (
              <div key={s.label} className={`flex flex-col items-center justify-center px-4 py-10 text-center ${isDark ? 'bg-[#05070e]' : 'bg-white'}`}>
                <span className={`text-4xl font-bold tracking-tight sm:text-5xl ${t.heading}`}>
                  <CountUp to={s.to} prefix={s.prefix || ''} suffix={s.suffix || ''} />
                </span>
                <span className={`mt-2 text-sm ${t.muted}`}>{s.label}</span>
              </div>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}

/* ════════════════════════════════ PRICING ══════════════════════════ */
const PLANS = [
  {
    name: 'Individual', price: '$15', cadence: '/mo', tagline: 'For solo users', trial: '15-day free trial',
    features: ['1 user', '5 buckets', '100 documents', 'Up to 1,800 pages', '5 GB storage', '500 AI chats / month', 'Cited answers — exact page', 'Connect any AI (MCP) — 30 req/min', 'Email support'],
    cta: 'Start free trial', highlight: true,
  },
  {
    name: 'Team', price: '$49', cadence: '/mo', tagline: 'For small teams',
    features: ['9 users', '20 buckets', '300 documents', 'Up to 4,000 pages', '15 GB storage', '1,800 AI chats / month', 'Cited answers — exact page', 'Team sharing & permissions', 'Connect any AI (MCP) — 60 req/min', 'Priority support'],
    cta: 'Start free trial',
  },
  {
    name: 'Enterprise', price: 'Custom', cadence: '', tagline: 'For large teams',
    features: ['Unlimited users & buckets', 'Custom document & storage limits', 'SSO / SAML', 'Dedicated infrastructure', 'Audit logs & SLA', 'Dedicated support'],
    cta: 'Contact sales', enterprise: true,
  },
];

function Pricing({ t, isDark }) {
  const navigate = useNavigate();
  const go = (p) => (p.enterprise ? navigate('/enterprise-contact') : navigate('/signup'));
  return (
    <Section id="pricing" eyebrow="Pricing" title="Simple, honest pricing" sub="Try it free for 15 days. Keep what works, cancel anytime." t={t}>
      <Stagger className="mt-14 grid gap-6 lg:grid-cols-3" delay={0.05}>
        {PLANS.map((p) => (
          <motion.div key={p.name} variants={itemV}>
            <div className={`relative flex h-full flex-col rounded-2xl border p-7 transition ${p.highlight ? (isDark ? 'border-blue-400/40 bg-blue-500/[0.06]' : 'border-blue-300 bg-blue-50/40 shadow-[0_24px_60px_-28px_rgba(37,99,235,0.4)]') : `${t.card} ${t.cardHover}`}`}>
              {p.highlight && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-blue-600 px-3 py-1 text-xs font-semibold text-white shadow">Most popular</span>
              )}
              <div className="flex items-center justify-between">
                <h3 className={`text-lg font-semibold ${t.heading}`}>{p.name}</h3>
                <span className={`text-xs ${t.muted}`}>{p.tagline}</span>
              </div>
              <div className="mt-5 flex items-end gap-1">
                <span className={`text-4xl font-bold tracking-tight ${t.heading}`}>{p.price}</span>
                {p.cadence && <span className={`mb-1 text-sm ${t.muted}`}>{p.cadence}</span>}
              </div>
              {p.trial && <p className="mt-1 text-xs font-medium text-blue-500">{p.trial}</p>}
              <button
                onClick={() => go(p)}
                className={`mt-6 w-full rounded-full px-5 py-3 text-sm font-semibold transition ${p.highlight ? 'bg-blue-600 text-white hover:bg-blue-500' : `border ${t.ghost}`}`}
              >
                {p.cta}
              </button>
              <ul className="mt-6 space-y-3">
                {p.features.map((f) => (
                  <li key={f} className={`flex items-start gap-2.5 text-sm ${t.body}`}>
                    <Ico name="check" className={`mt-0.5 h-4 w-4 flex-none ${isDark ? 'text-blue-400' : 'text-blue-600'}`} />
                    {f}
                  </li>
                ))}
              </ul>
            </div>
          </motion.div>
        ))}
      </Stagger>
    </Section>
  );
}

/* ════════════════════════════ BUILT FOR ════════════════════════════ */
function Personas({ t, isDark }) {
  const personas = [
    { ico: 'search', title: 'Researchers', body: 'Keep an entire literature library queryable. Ask across hundreds of papers and get answers cited to the page.' },
    { ico: 'shield', title: 'Teams', body: 'A shared, permissioned knowledge base for contracts, specs, and reports — without re-uploading per person.' },
    { ico: 'cpu', title: 'Builders', body: 'Skip building your own RAG + MCP stack. Ship AI features on a managed retrieval layer in minutes.' },
  ];
  return (
    <Section id="built-for" eyebrow="Built for" title="Made for people who live in their docs" t={t} className={isDark ? '' : t.sectionAlt}>
      <Stagger className="mt-12 grid gap-6 md:grid-cols-3" delay={0.05}>
        {personas.map((p) => (
          <motion.div key={p.title} variants={itemV}>
            <div className={`h-full rounded-2xl border p-7 ${t.card} ${t.cardHover} transition`}>
              <span className={`flex h-11 w-11 items-center justify-center rounded-xl ${isDark ? 'bg-blue-500/15 text-blue-300' : 'bg-blue-50 text-blue-600'}`}><Ico name={p.ico} className="h-5 w-5" /></span>
              <h3 className={`mt-5 text-lg font-semibold ${t.heading}`}>{p.title}</h3>
              <p className={`mt-2 text-[0.95rem] ${t.body}`}>{p.body}</p>
            </div>
          </motion.div>
        ))}
      </Stagger>
    </Section>
  );
}

/* ════════════════════════════════ FAQ ══════════════════════════════ */
function FAQItem({ q, a, t, isDark, open, onToggle }) {
  return (
    <div className={`rounded-2xl border transition ${t.card}`}>
      <button onClick={onToggle} className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left">
        <span className={`text-[0.98rem] font-semibold ${t.heading}`}>{q}</span>
        <span className={`flex h-7 w-7 flex-none items-center justify-center rounded-full ${isDark ? 'bg-white/5 text-slate-300' : 'bg-slate-100 text-slate-600'}`}>
          <Ico name={open ? 'minus' : 'plus'} className="h-4 w-4" />
        </span>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.28, ease: EASE }} className="overflow-hidden">
            <p className={`px-5 pb-5 text-[0.95rem] leading-relaxed ${t.body}`}>{a}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function FAQ({ t, isDark }) {
  const faqs = [
    { q: 'How do I connect AIveilix to my AI?', a: 'Create a bucket, then copy its MCP URL into Claude, ChatGPT, Cursor, or any MCP-compatible client. Your docs become available instantly — no SDK or setup code needed.' },
    { q: 'What file types are supported?', a: 'PDFs, Word docs, slides, spreadsheets, and images. Text and visuals (charts, diagrams, text inside images) are both parsed into the searchable knowledge base.' },
    { q: 'Is my data private?', a: 'Yes. Every bucket is isolated and access is gated by a private token baked into the MCP link. Files never leak across buckets.' },
    { q: 'Which AI models can I use?', a: 'Bring your own key for Claude, Gemini, GPT-4o, or Kimi. You stay in control of the model and its cost.' },
    { q: 'Can I cancel anytime?', a: 'Yes. Paid plans are month-to-month — cancel from account settings. Your data stays put even if you downgrade.' },
    { q: 'Do answers really cite sources?', a: 'Always. Each response includes the exact file and page (or slide) it drew from, so you can verify in one click.' },
  ];
  const [open, setOpen] = useState(0);
  return (
    <Section id="faq" eyebrow="FAQ" title="Questions, answered" t={t}>
      <div className="mx-auto mt-12 max-w-3xl space-y-3">
        {faqs.map((f, i) => (
          <Reveal key={f.q} delay={i * 0.03}>
            <FAQItem {...f} t={t} isDark={isDark} open={open === i} onToggle={() => setOpen(open === i ? -1 : i)} />
          </Reveal>
        ))}
      </div>
    </Section>
  );
}

/* ════════════════════════════════ CTA ══════════════════════════════ */
function FinalCTA({ t, isDark }) {
  const navigate = useNavigate();
  return (
    <section className="relative py-24">
      <div className="mx-auto max-w-5xl px-5 sm:px-6">
        <Reveal>
          <div className="relative overflow-hidden rounded-3xl px-6 py-16 text-center sm:px-12 sm:py-20" style={{ background: isDark ? 'linear-gradient(135deg,#0b1224,#0a1a3a)' : 'linear-gradient(135deg,#1e3a8a,#2563eb)' }}>
            <div className="pointer-events-none absolute inset-0">
              <div className="absolute -top-24 left-1/4 h-64 w-64 rounded-full bg-blue-400/30 blur-3xl" />
              <div className="absolute -bottom-24 right-1/4 h-64 w-64 rounded-full bg-cyan-400/20 blur-3xl" />
            </div>
            <div className="relative">
              <h2 className="mx-auto max-w-2xl text-3xl font-bold tracking-tight text-white sm:text-5xl">Give your knowledge a permanent home.</h2>
              <p className="mx-auto mt-5 max-w-xl text-lg text-blue-100">Free for your first bucket. Set up in under a minute. No card required.</p>
              <div className="mt-9 flex flex-wrap items-center justify-center gap-3">
                <button onClick={() => navigate('/signup')} className="group inline-flex items-center gap-2 rounded-full bg-white px-7 py-3.5 text-base font-semibold text-slate-900 transition hover:bg-slate-100 active:scale-[0.98]">
                  Start free <Ico name="arrow" className="h-4 w-4 transition group-hover:translate-x-0.5" />
                </button>
                <Link to="/docs" className="inline-flex items-center gap-2 rounded-full border border-white/30 bg-white/10 px-6 py-3.5 text-base font-medium text-white transition hover:bg-white/20">Read the docs</Link>
              </div>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}

/* ════════════════════════════════ FOOTER ═══════════════════════════ */
function Footer({ t, isDark }) {
  const cols = [
    { h: 'Product', items: [['Features', '#features'], ['How it works', '#how'], ['Pricing', '#pricing'], ['Docs', '/docs']] },
    { h: 'Company', items: [['Privacy', '/privacy-policy'], ['Terms', '/terms'], ['Contact', '/enterprise-contact']] },
    { h: 'Get started', items: [['Sign up', '/signup'], ['Sign in', '/login']] },
  ];
  return (
    <footer className={`border-t ${t.footer}`}>
      <div className="mx-auto max-w-7xl px-5 py-14 sm:px-6">
        <div className="grid gap-10 md:grid-cols-[1.4fr_repeat(3,1fr)]">
          <div>
            <Link to="/v2" className="flex items-center gap-2.5">
              <img src="/logo-tight.png" alt="AIveilix" className="h-8 w-8 rounded-lg" />
              <span className={`text-base font-bold tracking-tight ${t.heading}`}>AIveilix</span>
            </Link>
            <p className={`mt-4 max-w-xs text-sm ${t.muted}`}>Persistent knowledge infrastructure for AI. Upload once, use it in every AI.</p>
          </div>
          {cols.map((c) => (
            <div key={c.h}>
              <p className={`text-sm font-semibold ${t.heading}`}>{c.h}</p>
              <ul className="mt-4 space-y-2.5">
                {c.items.map(([l, h]) => (
                  <li key={l}>
                    {h.startsWith('#') ? (
                      <a href={h} className={`text-sm transition hover:text-blue-500 ${t.muted}`}>{l}</a>
                    ) : (
                      <Link to={h} className={`text-sm transition hover:text-blue-500 ${t.muted}`}>{l}</Link>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className={`mt-12 flex flex-col items-center justify-between gap-4 border-t pt-6 sm:flex-row ${t.hair}`}>
          <p className={`text-xs ${t.faint}`}>© {new Date().getFullYear()} AIveilix. All rights reserved.</p>
          <p className={`text-xs ${t.faint}`}>AI + Veil + lix — your knowledge, protected and connected.</p>
        </div>
      </div>
    </footer>
  );
}

/* ════════════════════════════════ PAGE ═════════════════════════════ */
export default function LandingPageV2({ theme: initialTheme }) {
  const [theme, setTheme] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = window.localStorage.getItem('aiveilix-v2-theme');
      if (saved === 'dark' || saved === 'light') return saved;
    }
    return initialTheme === 'light' ? 'light' : 'dark';
  });
  const isDark = theme === 'dark';
  const t = isDark ? TOKENS.dark : TOKENS.light;

  const toggle = () => {
    setTheme((prev) => {
      const next = prev === 'dark' ? 'light' : 'dark';
      try { window.localStorage.setItem('aiveilix-v2-theme', next); } catch {}
      return next;
    });
  };

  useEffect(() => { window.scrollTo(0, 0); }, []);

  return (
    <div className={`min-h-screen w-full overflow-x-hidden antialiased transition-colors duration-500 ${t.page}`} style={{ fontFamily: '"Plus Jakarta Sans", system-ui, sans-serif' }}>
      <GlobalFx />
      <Nav t={t} theme={theme} onToggle={toggle} />
      <main>
        <Hero t={t} theme={theme} />
        <LogoCloud t={t} isDark={isDark} />
        <ProblemShift t={t} isDark={isDark} />
        <HowItWorks t={t} isDark={isDark} />
        <Bento t={t} isDark={isDark} />
        <MCPBeams t={t} isDark={isDark} />
        <Stats t={t} isDark={isDark} />
        <Pricing t={t} isDark={isDark} />
        <Personas t={t} isDark={isDark} />
        <FAQ t={t} isDark={isDark} />
        <FinalCTA t={t} isDark={isDark} />
      </main>
      <Footer t={t} isDark={isDark} />
    </div>
  );
}
