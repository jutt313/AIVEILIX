// Demo chat panel — message list, streaming reply, citations, composer.
import React, { useEffect, useRef, useState, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { motion, AnimatePresence } from 'framer-motion';
import { demoApi, DemoLimitError } from './demoApi';
import { Spinner, Avatar, BRAND } from './DemoShell';
import { cn } from '../lib/utils';

const MD_COMPONENTS = {
  p: ({ children }) => <p className="mb-3 leading-relaxed last:mb-0">{children}</p>,
  ul: ({ children }) => <ul className="mb-3 list-disc space-y-1 pl-5 last:mb-0">{children}</ul>,
  ol: ({ children }) => <ol className="mb-3 list-decimal space-y-1 pl-5 last:mb-0">{children}</ol>,
  li: ({ children }) => <li className="leading-relaxed">{children}</li>,
  h1: ({ children }) => <h1 className="mb-2 mt-1 text-lg font-bold">{children}</h1>,
  h2: ({ children }) => <h2 className="mb-2 mt-1 text-base font-bold">{children}</h2>,
  h3: ({ children }) => <h3 className="mb-1.5 mt-1 text-sm font-bold">{children}</h3>,
  strong: ({ children }) => <strong className="font-semibold text-white">{children}</strong>,
  a: ({ children, href }) => (
    <a href={href} target="_blank" rel="noreferrer" className="text-indigo-400 underline decoration-indigo-400/40 hover:text-indigo-300">{children}</a>
  ),
  code: ({ inline, children }) =>
    inline ? (
      <code className="rounded bg-white/10 px-1.5 py-0.5 text-[0.85em] text-indigo-200">{children}</code>
    ) : (
      <code className="block overflow-x-auto rounded-xl bg-black/40 p-3 text-[0.85em] text-slate-200 ring-1 ring-white/10">{children}</code>
    ),
  blockquote: ({ children }) => (
    <blockquote className="mb-3 border-l-2 border-indigo-500/50 pl-3 text-slate-300">{children}</blockquote>
  ),
  table: ({ children }) => (
    <div className="mb-3 overflow-x-auto"><table className="w-full border-collapse text-sm">{children}</table></div>
  ),
  th: ({ children }) => <th className="border border-white/10 bg-white/5 px-2.5 py-1.5 text-left font-semibold">{children}</th>,
  td: ({ children }) => <td className="border border-white/10 px-2.5 py-1.5">{children}</td>,
};

function Sources({ sources }) {
  if (!sources || sources.length === 0) return null;
  // De-dupe by file name; show up to 6 citation chips.
  const seen = new Set();
  const chips = [];
  for (const s of sources) {
    const label = s.file_name || s.name || s.title || s.source || (s.file_id ? `Doc ${String(s.file_id).slice(0, 6)}` : null);
    if (!label || seen.has(label)) continue;
    seen.add(label);
    const page = s.page || s.page_number || (s.pages && s.pages[0]);
    chips.push({ label, page });
    if (chips.length >= 6) break;
  }
  if (chips.length === 0) return null;
  return (
    <div className="mt-2.5 flex flex-wrap gap-1.5">
      <span className="text-[11px] font-medium uppercase tracking-wide text-slate-500">Sources</span>
      {chips.map((c, i) => (
        <span key={i} className="inline-flex items-center gap-1 rounded-full bg-indigo-500/10 px-2.5 py-0.5 text-[11px] font-medium text-indigo-300 ring-1 ring-indigo-500/20">
          <svg viewBox="0 0 24 24" className="h-3 w-3" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 3v4a1 1 0 001 1h4M5 3h9l5 5v11a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2z" /></svg>
          {c.label}{c.page ? ` · p.${c.page}` : ''}
        </span>
      ))}
    </div>
  );
}

function Bubble({ msg, lead }) {
  const isUser = msg.role === 'user';
  return (
    <div className={cn('flex gap-3', isUser ? 'flex-row-reverse' : 'flex-row')}>
      {isUser ? (
        <Avatar name={lead?.name} color={lead?.color || BRAND} size="md" />
      ) : (
        <div className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-gradient-to-br from-indigo-500 to-fuchsia-500 ring-2 ring-[#020617]">
          <svg viewBox="0 0 24 24" className="h-4 w-4 text-white" fill="currentColor"><path d="M12 2l2.4 6.3L21 11l-6.6 2.7L12 20l-2.4-6.3L3 11l6.6-2.7L12 2z" /></svg>
        </div>
      )}
      <div className={cn('min-w-0 max-w-[80%]', isUser ? 'text-right' : 'text-left')}>
        <div
          className={cn(
            'inline-block rounded-2xl px-4 py-2.5 text-left text-[14px]',
            isUser ? 'bg-indigo-600 text-white' : 'bg-white/[0.06] text-slate-100 ring-1 ring-white/10',
          )}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
          ) : (
            <div className="prose-demo"><ReactMarkdown remarkPlugins={[remarkGfm]} components={MD_COMPONENTS}>{msg.content || ''}</ReactMarkdown></div>
          )}
        </div>
        {!isUser && <Sources sources={msg.sources} />}
      </div>
    </div>
  );
}

const STARTERS = [
  'What is this company about?',
  'Summarize the key documents',
  'What are the main products or services?',
  'What should I know before a meeting?',
];

export default function DemoChat({
  activeConversationId,
  onEnsureConversation,
  onBusyChange,
  onAfterTurn,
  onLimit,
  companyName,
  readyFiles,
  composerId,
}) {
  const [messages, setMessages] = useState([]);
  const [streaming, setStreaming] = useState(null); // live assistant text
  const [thinking, setThinking] = useState(false);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const scrollRef = useRef(null);
  const lead = (() => { try { return JSON.parse(sessionStorage.getItem('aiveilix-demo-lead') || 'null'); } catch { return null; } })();

  const scrollToBottom = useCallback(() => {
    requestAnimationFrame(() => {
      const el = scrollRef.current;
      if (el) el.scrollTop = el.scrollHeight;
    });
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (!activeConversationId) { setMessages([]); return; }
      setLoadingHistory(true);
      try {
        const data = await demoApi.getMessages(activeConversationId);
        if (!cancelled) { setMessages(data.messages || []); scrollToBottom(); }
      } catch { /* ignore */ }
      finally { if (!cancelled) setLoadingHistory(false); }
    }
    load();
    return () => { cancelled = true; };
  }, [activeConversationId, scrollToBottom]);

  useEffect(() => { scrollToBottom(); }, [messages, streaming, thinking, scrollToBottom]);

  const send = async (text) => {
    const content = (text ?? input).trim();
    if (!content || sending) return;
    setInput('');
    setSending(true);
    setThinking(true);
    onBusyChange?.(true);

    // optimistic user bubble
    const tempUser = { id: `tmp-${Date.now()}`, role: 'user', content };
    setMessages((m) => [...m, tempUser]);

    let convId = activeConversationId;
    try {
      if (!convId) convId = await onEnsureConversation();
    } catch (e) {
      setMessages((m) => m.filter((x) => x.id !== tempUser.id));
      setSending(false); setThinking(false); onBusyChange?.(false);
      if (e instanceof DemoLimitError) onLimit?.(e.limit);
      return;
    }

    setStreaming('');
    try {
      const result = await demoApi.sendMessageStream(convId, content, {
        onToken: (t) => { setThinking(false); setStreaming((s) => (s || '') + t); },
      });
      setMessages((m) => {
        const withoutTemp = m.filter((x) => x.id !== tempUser.id);
        return [...withoutTemp, result.user_message, result.assistant_message];
      });
      setStreaming(null);
      onAfterTurn?.();
    } catch (e) {
      setMessages((m) => m.filter((x) => x.id !== tempUser.id));
      setStreaming(null);
      if (e instanceof DemoLimitError) onLimit?.(e.limit);
      else setMessages((m) => [...m, { id: `err-${Date.now()}`, role: 'assistant', content: `⚠️ ${e.message || 'Something went wrong.'}` }]);
    } finally {
      setSending(false); setThinking(false); onBusyChange?.(false);
    }
  };

  const empty = messages.length === 0 && !streaming && !thinking;

  return (
    <div className="flex h-full flex-col">
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-6 sm:px-8">
        <div className="mx-auto max-w-3xl space-y-5">
          {empty && !loadingHistory && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="pt-6 text-center">
              <div className="mx-auto mb-4 grid h-14 w-14 place-items-center rounded-2xl bg-gradient-to-br from-indigo-500 to-fuchsia-500 shadow-lg shadow-indigo-900/40">
                <svg viewBox="0 0 24 24" className="h-7 w-7 text-white" fill="currentColor"><path d="M12 2l2.4 6.3L21 11l-6.6 2.7L12 20l-2.4-6.3L3 11l6.6-2.7L12 2z" /></svg>
              </div>
              <h2 className="text-lg font-bold">Ask anything about {companyName || 'these documents'}</h2>
              <p className="mt-1.5 text-sm text-slate-400">
                This AI is built on {readyFiles ? `${readyFiles} ` : ''}real document{readyFiles === 1 ? '' : 's'}. Every answer is grounded and cited.
              </p>
              <div data-tour="starters" className="mx-auto mt-6 grid max-w-xl gap-2 sm:grid-cols-2">
                {STARTERS.map((s) => (
                  <button
                    key={s}
                    onClick={() => send(s)}
                    className="rounded-xl bg-white/[0.04] px-4 py-3 text-left text-sm text-slate-200 ring-1 ring-white/10 transition hover:bg-white/[0.08] hover:ring-indigo-500/40"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </motion.div>
          )}

          {loadingHistory && <div className="flex justify-center py-10"><Spinner className="h-6 w-6 text-indigo-400" /></div>}

          {messages.map((m) => <Bubble key={m.id} msg={m} lead={lead} />)}

          <AnimatePresence>
            {thinking && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex gap-3">
                <div className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-gradient-to-br from-indigo-500 to-fuchsia-500">
                  <svg viewBox="0 0 24 24" className="h-4 w-4 text-white" fill="currentColor"><path d="M12 2l2.4 6.3L21 11l-6.6 2.7L12 20l-2.4-6.3L3 11l6.6-2.7L12 2z" /></svg>
                </div>
                <div className="flex items-center gap-1.5 rounded-2xl bg-white/[0.06] px-4 py-3 ring-1 ring-white/10">
                  {[0, 1, 2].map((i) => (
                    <span key={i} className="h-1.5 w-1.5 animate-bounce rounded-full bg-indigo-400" style={{ animationDelay: `${i * 120}ms` }} />
                  ))}
                  <span className="ml-1 text-xs text-slate-400">Reading the documents…</span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {streaming != null && (
            <Bubble msg={{ id: 'streaming', role: 'assistant', content: streaming }} lead={lead} />
          )}
        </div>
      </div>

      {/* composer */}
      <div className="border-t border-white/10 bg-[#070C18]/80 px-4 py-3 backdrop-blur sm:px-8">
        <form
          id={composerId}
          onSubmit={(e) => { e.preventDefault(); send(); }}
          className="mx-auto flex max-w-3xl items-end gap-2"
        >
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
            }}
            rows={1}
            placeholder="Ask about the documents…"
            className="max-h-40 min-h-[48px] flex-1 resize-none rounded-2xl bg-slate-800/70 px-4 py-3 text-sm text-slate-100 outline-none ring-1 ring-white/10 placeholder:text-slate-500 focus:ring-2 focus:ring-indigo-500"
          />
          <button
            type="submit"
            disabled={!input.trim() || sending}
            data-tour="send"
            className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-gradient-to-br from-indigo-500 to-indigo-600 text-white shadow-lg shadow-indigo-900/30 transition hover:from-indigo-400 hover:to-indigo-500 disabled:opacity-40"
          >
            {sending ? <Spinner className="h-5 w-5" /> : (
              <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
            )}
          </button>
        </form>
        <p className="mx-auto mt-1.5 max-w-3xl text-center text-[11px] text-slate-600">
          AIveilix can make mistakes. Answers are grounded in the provided documents.
        </p>
      </div>
    </div>
  );
}
