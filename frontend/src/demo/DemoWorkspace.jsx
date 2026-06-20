// The demo workspace — standalone shell (no dashboard chrome): header counters,
// thread + document sidebar, chat, idle pop-up, spotlight tour, and every panel.
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { demoApi, DemoLimitError } from './demoApi';
import { DemoBackdrop, DemoLogo, Avatar, BRAND } from './DemoShell';
import DemoChat from './DemoChat';
import DemoTour from './DemoTour';
import { FeedbackTalkModal, McpPanelModal, TeamInviteModal, UploadModal } from './DemoModals';
import { cn } from '../lib/utils';

const IDLE_MS = 60_000; // first auto pop-up after ~1 min idle

const TOUR_STEPS = [
  { selector: '[data-tour="send"]', title: 'Ask anything', body: 'Type a question — every answer is grounded in the documents and shows its sources.' },
  { selector: '[data-tour="new-chat"]', title: 'Start fresh chats', body: 'Open a new thread anytime to explore a different topic.' },
  { selector: '[data-tour="documents"]', title: 'The source documents', body: 'This AI was built on these real documents. Click one to see it processed.' },
  { selector: '[data-tour="upload"]', title: 'Add your own file', body: 'Upload a document and chat with it instantly — see how it works on your content.' },
  { selector: '[data-tour="mcp"]', title: 'Use it in ChatGPT & Claude', body: 'Connect these documents to any AI client over MCP.' },
  { selector: '[data-tour="team"]', title: 'Bring your team', body: 'Invite a teammate to explore alongside you — they join with one click.' },
  { selector: '[data-tour="feedback"]', title: 'Feedback & a quick call', body: 'Share what you think or book a call with us whenever you’re ready.' },
];

function Counter({ label, value, max, tone = 'indigo' }) {
  const tones = {
    indigo: 'text-indigo-300',
    amber: 'text-amber-300',
    emerald: 'text-emerald-300',
  };
  return (
    <div className="rounded-lg bg-white/[0.04] px-2.5 py-1 ring-1 ring-white/10">
      <span className="text-[10px] uppercase tracking-wide text-slate-500">{label}</span>
      <span className={cn('ml-1.5 text-xs font-bold', tones[tone])}>{value}{max != null ? `/${max}` : ''}</span>
    </div>
  );
}

function fmtCountdown(ms) {
  const s = Math.max(0, Math.ceil(ms / 1000));
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return `${m}:${String(sec).padStart(2, '0')}`;
}

export default function DemoWorkspace({ initialMe, onExpired }) {
  const [me, setMe] = useState(initialMe);
  const [conversations, setConversations] = useState([]);
  const [activeConvId, setActiveConvId] = useState(null);
  const [files, setFiles] = useState([]);
  const [team, setTeam] = useState([]);
  const [chatBusy, setChatBusy] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // modals
  const [feedback, setFeedback] = useState({ open: false, limit: null, auto: false });
  const [mcpOpen, setMcpOpen] = useState(false);
  const [teamOpen, setTeamOpen] = useState(false);
  const [uploadOpen, setUploadOpen] = useState(false);

  // idle + snooze
  const lastActivity = useRef(Date.now());
  const shownThisIdle = useRef(false);
  const [snoozeUntil, setSnoozeUntil] = useState(0);
  const [nowTick, setNowTick] = useState(Date.now());

  // tour
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
      if (!activeConvId && data.conversations?.length) setActiveConvId(data.conversations[0].id);
    } catch { /* ignore */ }
  }, [activeConvId]);

  const loadFiles = useCallback(async () => {
    try { const data = await demoApi.files(); setFiles(data.files || []); } catch { /* ignore */ }
  }, []);
  const loadTeam = useCallback(async () => {
    try { const data = await demoApi.team(); setTeam(data.members || []); } catch { /* ignore */ }
  }, []);

  useEffect(() => {
    persistLead(me);
    loadConversations();
    loadFiles();
    loadTeam();
    if (!localStorage.getItem(tourKey)) {
      const t = setTimeout(() => setShowTour(true), 900);
      return () => clearTimeout(t);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // poll processing files so visitor-uploaded docs flip to "ready"
  useEffect(() => {
    const processing = files.some((f) => f.status === 'processing' || f.status === 'uploading');
    if (!processing) return;
    const t = setInterval(loadFiles, 5000);
    return () => clearInterval(t);
  }, [files, loadFiles]);

  // activity tracking for idle pop-up
  useEffect(() => {
    const mark = () => { lastActivity.current = Date.now(); shownThisIdle.current = false; };
    const evts = ['mousemove', 'mousedown', 'keydown', 'scroll', 'touchstart'];
    evts.forEach((e) => window.addEventListener(e, mark, { passive: true }));
    return () => evts.forEach((e) => window.removeEventListener(e, mark));
  }, []);

  // idle + countdown ticker
  useEffect(() => {
    const t = setInterval(() => {
      setNowTick(Date.now());
      const now = Date.now();
      const busy = chatBusy || anyModalOpen || showTour;
      const snoozed = snoozeUntil > now;
      if (busy || snoozed) return;
      if (!shownThisIdle.current && now - lastActivity.current >= IDLE_MS) {
        shownThisIdle.current = true;
        setFeedback({ open: true, limit: null, auto: true });
        demoApi.logEvent('popup_shown', { trigger: 'idle' });
      }
    }, 1000);
    return () => clearInterval(t);
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
      setSidebarOpen(false);
    } catch (e) {
      if (e instanceof DemoLimitError) openLimit(e.limit);
    }
  };

  const openLimit = useCallback((limit) => {
    demoApi.logEvent('limit_hit', { limit });
    setFeedback({ open: true, limit, auto: false });
  }, []);

  const handleSnooze = (minutes) => {
    const until = Date.now() + minutes * 60_000;
    setSnoozeUntil(until);
    setFeedback({ open: false, limit: null, auto: false });
    lastActivity.current = Date.now();
    shownThisIdle.current = false;
    demoApi.logEvent('popup_snoozed', { minutes });
  };

  const caps = me?.caps || {};
  const usage = me?.usage || {};
  const lead = me?.lead || {};
  const snoozeRemaining = snoozeUntil - nowTick;

  const readyFiles = useMemo(() => files.filter((f) => f.status === 'ready').length, [files]);

  return (
    <DemoBackdrop>
      <div className="flex h-[100dvh] flex-col">
        {/* ── header ── */}
        <header className="flex shrink-0 items-center justify-between gap-3 border-b border-white/10 bg-[#070C18]/80 px-3 py-2.5 backdrop-blur sm:px-5">
          <div className="flex min-w-0 items-center gap-3">
            <button onClick={() => setSidebarOpen((s) => !s)} className="rounded-lg p-1.5 text-slate-400 hover:bg-white/5 lg:hidden">
              <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4 6h16M4 12h16M4 18h16" /></svg>
            </button>
            <DemoLogo size="sm" />
            <div className="hidden min-w-0 sm:block">
              <span className="truncate text-sm font-semibold text-slate-200">{me?.company_name}</span>
              <span className="ml-2 rounded-full bg-indigo-500/15 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-indigo-300">Demo</span>
            </div>
          </div>

          <div className="flex items-center gap-1.5 sm:gap-2">
            {snoozeRemaining > 0 && (
              <div className="hidden items-center gap-1 rounded-lg bg-amber-500/10 px-2.5 py-1 text-xs font-semibold text-amber-300 ring-1 ring-amber-500/20 sm:flex">
                <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></svg>
                {fmtCountdown(snoozeRemaining)}
              </div>
            )}
            <div className="hidden items-center gap-1.5 md:flex">
              <Counter label="Visit" value={lead.comeback_count} max={caps.comebacks} tone="amber" />
              <Counter label="Msgs" value={usage.messages} max={caps.messages} />
            </div>
            <button data-tour="mcp" onClick={() => setMcpOpen(true)} title="Use in ChatGPT/Claude" className="hidden rounded-lg bg-white/[0.05] px-2.5 py-1.5 text-xs font-semibold text-slate-200 ring-1 ring-white/10 hover:bg-white/10 sm:block">MCP</button>
            <button data-tour="team" onClick={() => setTeamOpen(true)} title="Invite a teammate" className="relative rounded-lg bg-white/[0.05] p-1.5 text-slate-200 ring-1 ring-white/10 hover:bg-white/10">
              <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M9 7a4 4 0 100 8 4 4 0 000-8zM23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" /></svg>
              {team.length > 0 && <span className="absolute -right-1 -top-1 grid h-4 w-4 place-items-center rounded-full bg-indigo-500 text-[9px] font-bold text-white">{team.length}</span>}
            </button>
            <button
              data-tour="feedback"
              onClick={() => setFeedback({ open: true, limit: null, auto: false })}
              className="rounded-lg bg-gradient-to-br from-indigo-500 to-indigo-600 px-3 py-1.5 text-xs font-semibold text-white shadow-lg shadow-indigo-900/30 hover:from-indigo-400 hover:to-indigo-500"
            >
              Feedback
            </button>
          </div>
        </header>

        {/* ── nudge banner ── */}
        <div className="flex shrink-0 items-center justify-center gap-2 border-b border-white/5 bg-indigo-500/[0.07] px-4 py-1.5 text-center text-[12px] text-indigo-200/90">
          <svg viewBox="0 0 24 24" className="h-3.5 w-3.5 shrink-0" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2a10 10 0 100 20 10 10 0 000-20zM12 8v5M12 16h.01" /></svg>
          Don’t forget to leave feedback — it helps us improve and understand you better.
        </div>

        <div className="flex min-h-0 flex-1">
          {/* ── sidebar ── */}
          <aside className={cn(
            'absolute z-50 h-[calc(100dvh-92px)] w-72 shrink-0 flex-col border-r border-white/10 bg-[#0A1020] transition-transform lg:static lg:z-auto lg:flex lg:h-auto lg:translate-x-0',
            sidebarOpen ? 'flex translate-x-0' : '-translate-x-full lg:translate-x-0',
          )}>
            <div className="flex flex-col gap-3 overflow-y-auto p-3">
              <button data-tour="new-chat" onClick={newChat} className="flex items-center justify-center gap-2 rounded-xl bg-white/[0.05] px-3 py-2.5 text-sm font-semibold text-slate-100 ring-1 ring-white/10 hover:bg-white/10">
                <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 5v14M5 12h14" /></svg>
                New chat
              </button>

              <div>
                <p className="px-1 pb-1.5 text-[11px] font-semibold uppercase tracking-wide text-slate-500">Chats ({conversations.length}/{caps.threads ?? '—'})</p>
                <div className="space-y-1">
                  {conversations.length === 0 && <p className="px-1 py-2 text-xs text-slate-600">No chats yet.</p>}
                  {conversations.map((c) => (
                    <button
                      key={c.id}
                      onClick={() => { setActiveConvId(c.id); setSidebarOpen(false); }}
                      className={cn(
                        'flex w-full items-center gap-2 truncate rounded-lg px-2.5 py-2 text-left text-sm transition',
                        activeConvId === c.id ? 'bg-indigo-500/15 text-indigo-200 ring-1 ring-indigo-500/30' : 'text-slate-300 hover:bg-white/5',
                      )}
                    >
                      <svg viewBox="0 0 24 24" className="h-3.5 w-3.5 shrink-0 text-slate-500" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" /></svg>
                      <span className="truncate">{c.title}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div data-tour="documents">
                <div className="flex items-center justify-between px-1 pb-1.5">
                  <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Documents ({files.length})</p>
                  <button data-tour="upload" onClick={() => setUploadOpen(true)} title="Add your own" className="rounded-md p-1 text-slate-400 hover:bg-white/10 hover:text-indigo-300">
                    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 5v14M5 12h14" /></svg>
                  </button>
                </div>
                <div className="space-y-1">
                  {files.length === 0 && <p className="px-1 py-2 text-xs text-slate-600">Loading documents…</p>}
                  {files.map((f) => (
                    <div key={f.id} className="flex items-center gap-2 rounded-lg px-2.5 py-1.5 text-sm text-slate-300">
                      <svg viewBox="0 0 24 24" className="h-4 w-4 shrink-0 text-slate-500" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 3v4a1 1 0 001 1h4M5 3h9l5 5v11a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2z" /></svg>
                      <span className="min-w-0 flex-1 truncate">{f.name}</span>
                      {f.status === 'ready' ? (
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" title="Ready" />
                      ) : f.status === 'failed' ? (
                        <span className="h-1.5 w-1.5 rounded-full bg-rose-400" title="Failed" />
                      ) : (
                        <span className="h-3 w-3 animate-spin rounded-full border-2 border-slate-600 border-t-indigo-400" title="Processing" />
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {team.length > 0 && (
                <div>
                  <p className="px-1 pb-1.5 text-[11px] font-semibold uppercase tracking-wide text-slate-500">Team ({team.length}/{caps.team_members ?? '—'})</p>
                  <div className="flex flex-wrap gap-1.5 px-1">
                    {team.map((m) => <Avatar key={m.id} name={m.name} color={m.color} size="sm" />)}
                  </div>
                </div>
              )}
            </div>
          </aside>
          {sidebarOpen && <div className="absolute inset-0 z-40 bg-black/50 lg:hidden" onClick={() => setSidebarOpen(false)} />}

          {/* ── chat ── */}
          <main className="min-w-0 flex-1">
            <DemoChat
              activeConversationId={activeConvId}
              onEnsureConversation={ensureConversation}
              onBusyChange={setChatBusy}
              onAfterTurn={() => { refreshMe(); loadConversations(); }}
              onLimit={openLimit}
              companyName={me?.company_name}
              readyFiles={readyFiles}
            />
          </main>
        </div>
      </div>

      {/* ── modals ── */}
      <FeedbackTalkModal
        open={feedback.open}
        limit={feedback.limit}
        onSnooze={feedback.auto ? handleSnooze : null}
        onClose={() => setFeedback({ open: false, limit: null, auto: false })}
        onSubmitted={refreshMe}
      />
      <McpPanelModal open={mcpOpen} onClose={() => setMcpOpen(false)} />
      <TeamInviteModal
        open={teamOpen}
        onClose={() => setTeamOpen(false)}
        onInvited={(maybeErr) => {
          if (maybeErr instanceof DemoLimitError) openLimit(maybeErr.limit);
          else { loadTeam(); refreshMe(); }
        }}
      />
      <UploadModal
        open={uploadOpen}
        fileSizeMb={caps.file_size_mb || 50}
        onClose={() => setUploadOpen(false)}
        onUploaded={(maybeErr) => {
          if (maybeErr instanceof DemoLimitError) openLimit(maybeErr.limit);
          else { loadFiles(); refreshMe(); }
        }}
      />

      {/* ── spotlight tour ── */}
      {showTour && (
        <DemoTour
          steps={TOUR_STEPS}
          onDone={(completed) => {
            setShowTour(false);
            try { localStorage.setItem(tourKey, '1'); } catch { /* ignore */ }
            if (completed) demoApi.logEvent('tour_completed');
          }}
        />
      )}
    </DemoBackdrop>
  );
}
