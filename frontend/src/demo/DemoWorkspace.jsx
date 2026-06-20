// Demo workspace — the real BucketPage layout (threads · chat · files) with a
// top header of counters. Standalone shell, no dashboard chrome. Themed + branded
// to match the rest of the tool exactly.
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { demoApi, DemoLimitError } from './demoApi';
import { bucketClasses, LOGO_SRC } from './demoTheme';
import { Spinner, Avatar, ThemeToggle } from './DemoShell';
import DemoChat from './DemoChat';
import DemoTour from './DemoTour';
import { FeedbackTalkModal, McpPanelModal, TeamInviteModal, UploadModal } from './DemoModals';
import { cn } from '../lib/utils';

const IDLE_MS = 60_000;

const TOUR_STEPS = [
  { selector: '[data-tour="send"]', title: 'Ask anything', body: 'Type a question — answers are grounded in the documents and cited.' },
  { selector: '[data-tour="new-chat"]', title: 'Start fresh chats', body: 'Open a new thread anytime to explore a different topic.' },
  { selector: '[data-tour="files"]', title: 'The source documents', body: 'This AI was built on these real documents. Add your own with the + button.' },
  { selector: '[data-tour="mcp"]', title: 'Use it in ChatGPT & Claude', body: 'Connect these documents to any AI client over MCP.' },
  { selector: '[data-tour="team"]', title: 'Bring your team', body: 'Invite a teammate — they join with one click, no code.' },
  { selector: '[data-tour="feedback"]', title: 'Feedback & a quick call', body: 'Share what you think or book a call with us whenever you’re ready.' },
];

function Counter({ label, value, max, t }) {
  return (
    <div className={cn('hidden items-center gap-1.5 rounded-full border px-2.5 py-1 md:flex', t.line)}>
      <span className={cn('text-[10px] uppercase tracking-wide', t.muted)}>{label}</span>
      <span className={cn('text-xs font-bold', t.titleCls)}>{value}{max != null ? `/${max}` : ''}</span>
    </div>
  );
}

function fmtCountdown(ms) {
  const s = Math.max(0, Math.ceil(ms / 1000));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
}

function fileStatusDot(status) {
  if (status === 'ready') return <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" title="Ready" />;
  if (status === 'failed') return <span className="h-1.5 w-1.5 rounded-full bg-red-400" title="Failed" />;
  return <span className="h-3 w-3 animate-spin rounded-full border-2 border-slate-400/40 border-t-blue-500" title="Processing" />;
}

export default function DemoWorkspace({ initialMe, onExpired, theme, onToggleTheme }) {
  const t = bucketClasses(theme === 'dark');
  const isDark = theme === 'dark';

  const [me, setMe] = useState(initialMe);
  const [conversations, setConversations] = useState([]);
  const [activeConvId, setActiveConvId] = useState(null);
  const [files, setFiles] = useState([]);
  const [team, setTeam] = useState([]);
  const [chatBusy, setChatBusy] = useState(false);
  const [loadingLists, setLoadingLists] = useState(true);

  const [feedback, setFeedback] = useState({ open: false, limit: null, auto: false });
  const [mcpOpen, setMcpOpen] = useState(false);
  const [teamOpen, setTeamOpen] = useState(false);
  const [uploadOpen, setUploadOpen] = useState(false);

  const lastActivity = useRef(Date.now());
  const shownThisIdle = useRef(false);
  const [snoozeUntil, setSnoozeUntil] = useState(0);
  const [nowTick, setNowTick] = useState(Date.now());

  const tourKey = `aiveilix-demo-tour-${me?.slug || 'x'}`;
  const [showTour, setShowTour] = useState(false);

  const anyModalOpen = feedback.open || mcpOpen || teamOpen || uploadOpen;

  const persistLead = useCallback((m) => {
    try { sessionStorage.setItem('aiveilix-demo-lead', JSON.stringify(m?.lead || null)); } catch { /* ignore */ }
  }, []);

  const refreshMe = useCallback(async () => {
    try { const m = await demoApi.me(); setMe(m); persistLead(m); }
    catch (e) { if (e.status === 401 || e.status === 403) onExpired?.(); }
  }, [onExpired, persistLead]);

  const loadConversations = useCallback(async () => {
    try {
      const data = await demoApi.listConversations();
      setConversations(data.conversations || []);
      setActiveConvId((cur) => cur || (data.conversations?.[0]?.id ?? null));
    } catch { /* ignore */ }
  }, []);
  const loadFiles = useCallback(async () => {
    try { const data = await demoApi.files(); setFiles(data.files || []); } catch { /* ignore */ }
  }, []);
  const loadTeam = useCallback(async () => {
    try { const data = await demoApi.team(); setTeam(data.members || []); } catch { /* ignore */ }
  }, []);

  useEffect(() => {
    persistLead(me);
    (async () => { await Promise.all([loadConversations(), loadFiles(), loadTeam()]); setLoadingLists(false); })();
    if (!localStorage.getItem(tourKey)) { const t = setTimeout(() => setShowTour(true), 900); return () => clearTimeout(t); }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const processing = files.some((f) => f.status === 'processing' || f.status === 'uploading');
    if (!processing) return;
    const id = setInterval(loadFiles, 5000);
    return () => clearInterval(id);
  }, [files, loadFiles]);

  useEffect(() => {
    const mark = () => { lastActivity.current = Date.now(); shownThisIdle.current = false; };
    const evts = ['mousemove', 'mousedown', 'keydown', 'scroll', 'touchstart'];
    evts.forEach((e) => window.addEventListener(e, mark, { passive: true }));
    return () => evts.forEach((e) => window.removeEventListener(e, mark));
  }, []);

  useEffect(() => {
    const id = setInterval(() => {
      setNowTick(Date.now());
      const now = Date.now();
      if (chatBusy || anyModalOpen || showTour || snoozeUntil > now) return;
      if (!shownThisIdle.current && now - lastActivity.current >= IDLE_MS) {
        shownThisIdle.current = true;
        setFeedback({ open: true, limit: null, auto: true });
        demoApi.logEvent('popup_shown', { trigger: 'idle' });
      }
    }, 1000);
    return () => clearInterval(id);
  }, [chatBusy, anyModalOpen, showTour, snoozeUntil]);

  const ensureConversation = useCallback(async () => {
    if (activeConvId) return activeConvId;
    const conv = await demoApi.createConversation('New chat');
    setConversations((c) => [conv, ...c]);
    setActiveConvId(conv.id);
    return conv.id;
  }, [activeConvId]);

  const newChat = async () => {
    try {
      const conv = await demoApi.createConversation('New chat');
      setConversations((c) => [conv, ...c]);
      setActiveConvId(conv.id);
    } catch (e) { if (e instanceof DemoLimitError) openLimit(e.limit); }
  };

  const openLimit = useCallback((limit) => {
    demoApi.logEvent('limit_hit', { limit });
    setFeedback({ open: true, limit, auto: false });
  }, []);

  const handleSnooze = (minutes) => {
    setSnoozeUntil(Date.now() + minutes * 60_000);
    setFeedback({ open: false, limit: null, auto: false });
    lastActivity.current = Date.now();
    shownThisIdle.current = false;
    demoApi.logEvent('popup_snoozed', { minutes });
  };

  const caps = me?.caps || {};
  const usage = me?.usage || {};
  const lead = me?.lead || {};
  const snoozeRemaining = snoozeUntil - nowTick;
  const bucketName = me?.company_name || 'Demo';

  return (
    <main className={cn('min-h-[100dvh]', t.bg)}>
      {/* ── top header ── */}
      <header className={cn('sticky top-0 z-30 border-b backdrop-blur', t.line, isDark ? 'bg-[#020617]/80' : 'bg-white/70')}>
        <div className="mx-auto flex max-w-[1600px] items-center justify-between gap-3 px-4 py-2.5 sm:px-6">
          <div className="flex min-w-0 items-center gap-2.5">
            <img src={LOGO_SRC} alt="AIveilix" className="h-7 w-7 rounded-md object-contain" />
            <span className={cn('text-base font-semibold tracking-tight', t.titleCls)}>AIveilix</span>
            <span className={cn('ml-1 hidden truncate text-sm sm:inline', t.muted)}>· {bucketName}</span>
            <span className="rounded-full bg-blue-500/15 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-blue-500">Demo</span>
          </div>

          <div className="flex items-center gap-1.5 sm:gap-2">
            {snoozeRemaining > 0 && (
              <div className={cn('hidden items-center gap-1 rounded-full border px-2.5 py-1 text-xs font-semibold text-amber-500 sm:flex', t.line)}>
                <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></svg>
                {fmtCountdown(snoozeRemaining)}
              </div>
            )}
            <Counter label="Visit" value={lead.comeback_count} max={caps.comebacks} t={t} />
            <Counter label="Msgs" value={usage.messages} max={caps.messages} t={t} />
            <button data-tour="team" onClick={() => setTeamOpen(true)} title="Invite teammates" className={cn('relative flex h-8 items-center gap-1.5 rounded-full border px-2.5 text-xs font-semibold transition', t.line, t.bodyCls, isDark ? 'hover:bg-white/5' : 'hover:bg-slate-100')}>
              <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2M9 7a4 4 0 1 0 0 8 4 4 0 0 0 0-8zM23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" /></svg>
              <span className="hidden sm:inline">{team.length}/{caps.team_members ?? '—'}</span>
            </button>
            <button data-tour="mcp" onClick={() => setMcpOpen(true)} title="Use in ChatGPT / Claude" className={cn('hidden h-8 items-center rounded-full border px-3 text-xs font-semibold transition sm:flex', t.line, t.accent || '', isDark ? 'text-blue-400 hover:bg-blue-500/10' : 'text-blue-600 hover:bg-blue-50')}>MCP</button>
            <ThemeToggle theme={theme} onToggle={onToggleTheme} />
            <button data-tour="feedback" onClick={() => setFeedback({ open: true, limit: null, auto: false })} className="rounded-full bg-blue-600 px-3.5 py-1.5 text-xs font-semibold text-white transition hover:bg-blue-500">Feedback</button>
          </div>
        </div>
        {/* nudge strip */}
        <div className={cn('flex items-center justify-center gap-2 border-t px-4 py-1 text-center text-[12px]', t.line, isDark ? 'bg-blue-500/[0.06] text-blue-200/90' : 'bg-blue-50 text-blue-700')}>
          <svg viewBox="0 0 24 24" className="h-3.5 w-3.5 shrink-0" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /><path d="M12 8v5M12 16h.01" /></svg>
          Don’t forget to leave feedback — it helps us improve and understand you better.
        </div>
      </header>

      {/* ── 3-column body ── */}
      <div className="mx-auto flex max-w-[1600px] gap-4 px-4 py-5 sm:px-6">
        {/* threads */}
        <aside className={cn('hidden h-[calc(100dvh-7rem)] w-[19rem] shrink-0 flex-col rounded-[1.35rem] border lg:flex', t.shell)}>
          <div className="px-4 pb-3 pt-4">
            <p className={cn('text-lg font-semibold', t.titleCls)}>{bucketName}</p>
            <p className={cn('mt-1 text-sm', t.muted)}>Conversation threads</p>
            <button data-tour="new-chat" type="button" onClick={newChat} className={cn('mt-4 flex w-full items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition disabled:opacity-50', t.primary)}>
              <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 5v14M5 12h14" /></svg>
              New chat
            </button>
          </div>
          <div className="flex-1 overflow-y-auto px-3 pb-4">
            {loadingLists ? (
              <div className="space-y-2">{[1, 2, 3].map((i) => <div key={i} className={cn('h-12 animate-pulse rounded-[0.9rem] border', t.line, t.subtle)} />)}</div>
            ) : conversations.length === 0 ? (
              <p className={cn('px-2 py-4 text-sm', t.muted)}>No threads yet. Create one above.</p>
            ) : (
              <div className="space-y-1.5">
                {conversations.map((c) => (
                  <div
                    key={c.id}
                    onClick={() => setActiveConvId(c.id)}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setActiveConvId(c.id); } }}
                    className={cn('group relative w-full cursor-pointer rounded-[0.9rem] border px-2.5 py-1.5 text-left transition', String(c.id) === String(activeConvId) ? t.threadActive : t.threadIdle)}
                  >
                    <div className="flex items-center gap-2">
                      <svg viewBox="0 0 24 24" className={cn('h-[18px] w-[18px] shrink-0', t.muted)} fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" /></svg>
                      <p className={cn('min-w-0 flex-1 truncate text-[14px] font-semibold', t.titleCls)}>{c.title}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </aside>

        {/* chat */}
        <DemoChat
          theme={theme}
          activeConversationId={activeConvId}
          onEnsureConversation={ensureConversation}
          onBusyChange={setChatBusy}
          onAfterTurn={() => { refreshMe(); loadConversations(); }}
          onLimit={openLimit}
        />

        {/* files */}
        <aside data-tour="files" className={cn('hidden h-[calc(100dvh-7rem)] w-[19rem] shrink-0 flex-col overflow-hidden rounded-[1.35rem] border lg:flex', t.rightAside)}>
          <div className="flex items-center justify-between px-4 py-4">
            <div>
              <p className={cn('text-base font-semibold', t.titleCls)}>Files</p>
              <p className={cn('mt-0.5 text-sm', t.muted)}>{files.length} document{files.length === 1 ? '' : 's'}</p>
            </div>
            <div className="flex items-center gap-1">
              <button type="button" onClick={() => setUploadOpen(true)} title="Add your own document" className={cn('rounded-full p-2 transition', isDark ? 'text-emerald-400 hover:bg-emerald-500/10' : 'text-emerald-600 hover:bg-emerald-50')}>
                <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 5v14M5 12h14" /></svg>
              </button>
              <button type="button" onClick={() => setMcpOpen(true)} title="MCP access" className={cn('rounded-full p-2 transition', isDark ? 'text-blue-400 hover:bg-blue-500/10' : 'text-blue-600 hover:bg-blue-50')}>
                <svg viewBox="0 0 24 24" className="h-4 w-4 fill-current"><path d="M15.688 2.343a2.588 2.588 0 0 0-3.61 0l-9.626 9.44a.863.863 0 0 1-1.203 0 .823.823 0 0 1 0-1.18l9.626-9.44a4.313 4.313 0 0 1 6.016 0 4.116 4.116 0 0 1 1.204 3.54 4.3 4.3 0 0 1 3.609 1.18l.05.05a4.115 4.115 0 0 1 0 5.9l-8.706 8.537a.274.274 0 0 0 0 .393l1.788 1.754a.823.823 0 0 1 0 1.18.863.863 0 0 1-1.203 0l-1.788-1.753a1.92 1.92 0 0 1 0-2.754l8.706-8.538a2.47 2.47 0 0 0 0-3.54l-.05-.049a2.588 2.588 0 0 0-3.607-.003l-7.172 7.034-.002.002-.098.097a.863.863 0 0 1-1.204 0 .823.823 0 0 1 0-1.18l7.273-7.133a2.47 2.47 0 0 0-.003-3.537Z" /></svg>
              </button>
            </div>
          </div>
          <div className={cn('flex-1 overflow-y-auto px-3 pb-4 pt-2', t.shell)}>
            {loadingLists ? (
              <div className="space-y-2">{[1, 2, 3].map((i) => <div key={i} className={cn('h-12 animate-pulse rounded-[0.9rem] border', t.line, t.subtle)} />)}</div>
            ) : files.length === 0 ? (
              <div className="px-2 py-6 text-center"><p className={cn('text-sm', t.muted)}>No documents yet.</p></div>
            ) : (
              <div className="space-y-1.5">
                {files.map((f) => (
                  <div key={f.id} className={cn('flex items-center gap-2 rounded-[0.9rem] border px-2.5 py-2 text-sm', t.line, t.fileRowIdle)}>
                    <svg viewBox="0 0 24 24" className={cn('h-4 w-4 shrink-0', t.muted)} fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /></svg>
                    <span className={cn('min-w-0 flex-1 truncate', t.bodyCls)}>{f.name}</span>
                    {fileStatusDot(f.status)}
                  </div>
                ))}
              </div>
            )}
          </div>
        </aside>
      </div>

      {/* ── modals ── */}
      <FeedbackTalkModal
        theme={theme}
        open={feedback.open}
        limit={feedback.limit}
        onSnooze={feedback.auto ? handleSnooze : null}
        onClose={() => setFeedback({ open: false, limit: null, auto: false })}
        onSubmitted={refreshMe}
      />
      <McpPanelModal theme={theme} open={mcpOpen} onClose={() => setMcpOpen(false)} />
      <TeamInviteModal theme={theme} open={teamOpen} onClose={() => setTeamOpen(false)} onInvited={(err) => { if (err instanceof DemoLimitError) openLimit(err.limit); else { loadTeam(); refreshMe(); } }} />
      <UploadModal theme={theme} open={uploadOpen} fileSizeMb={caps.file_size_mb || 50} onClose={() => setUploadOpen(false)} onUploaded={(err) => { if (err instanceof DemoLimitError) openLimit(err.limit); else { loadFiles(); refreshMe(); } }} />

      {showTour && (
        <DemoTour theme={theme} steps={TOUR_STEPS} onDone={(done) => { setShowTour(false); try { localStorage.setItem(tourKey, '1'); } catch { /* ignore */ } if (done) demoApi.logEvent('tour_completed'); }} />
      )}
    </main>
  );
}
