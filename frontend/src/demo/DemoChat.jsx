// Demo chat — same look as the BucketPage chat: blue user bubbles, markdown
// assistant answers (same component map), source chips, and the same composer.
import React, { useEffect, useRef, useState, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { demoApi, DemoLimitError } from './demoApi';
import { bucketClasses } from './demoTheme';
import { Spinner } from './DemoShell';
import { cn } from '../lib/utils';

// Copied from App.jsx buildMarkdownComponents so assistant answers render identically.
const buildMarkdownComponents = (isDark) => {
  const inlineCode = isDark ? 'bg-white/10 text-blue-200' : 'bg-slate-100 text-blue-700';
  const blockCode = isDark ? 'bg-black/30 text-slate-100' : 'bg-slate-100 text-slate-800';
  const linkCls = isDark ? 'text-blue-400 decoration-blue-400/40 hover:decoration-blue-400' : 'text-blue-600 decoration-blue-600/40 hover:decoration-blue-600';
  const tableBorder = isDark ? 'border-white/10' : 'border-slate-200';
  const theadBg = isDark ? 'bg-white/[0.04]' : 'bg-slate-50';
  const thText = isDark ? 'text-white/90' : 'text-slate-700';
  const tdText = isDark ? 'text-white/85' : 'text-slate-700';
  const bqBorder = isDark ? 'border-white/25' : 'border-slate-300';
  return {
    h1: (p) => <h1 className="mt-2 text-lg font-semibold" {...p} />,
    h2: (p) => <h2 className="mt-2 text-lg font-semibold" {...p} />,
    h3: (p) => <h3 className="mt-2 text-base font-semibold" {...p} />,
    h4: (p) => <h4 className="mt-2 text-base font-semibold" {...p} />,
    p: (p) => <p className="whitespace-pre-wrap break-words leading-7" {...p} />,
    ul: (p) => <ul className="my-1 list-disc space-y-1 pl-5" {...p} />,
    ol: (p) => <ol className="my-1 list-decimal space-y-1 pl-5" {...p} />,
    li: (p) => <li className="leading-7" {...p} />,
    hr: (p) => <hr className={`my-3 ${tableBorder}`} {...p} />,
    a: (p) => <a className={`underline underline-offset-2 ${linkCls}`} target="_blank" rel="noopener noreferrer" {...p} />,
    strong: (p) => <strong className="font-semibold" {...p} />,
    em: (p) => <em className="italic" {...p} />,
    blockquote: (p) => <blockquote className={`my-2 border-l-2 pl-3 italic opacity-90 ${bqBorder}`} {...p} />,
    code: ({ inline, className, children, ...rest }) =>
      inline === false
        ? <code className={`block whitespace-pre overflow-x-auto rounded-md px-3 py-2 font-mono text-[13px] ${blockCode} ${className || ''}`} {...rest}>{children}</code>
        : <code className={`rounded px-1 py-0.5 font-mono text-[0.9em] ${inlineCode}`} {...rest}>{children}</code>,
    table: (p) => <div className={`my-2 overflow-x-auto rounded-lg border ${tableBorder}`}><table className="w-full border-collapse text-sm" {...p} /></div>,
    thead: (p) => <thead className={theadBg} {...p} />,
    tr: (p) => <tr className={`border-b last:border-b-0 ${tableBorder}`} {...p} />,
    th: ({ style, ...p }) => <th style={style} className={`px-3 py-2 text-left font-semibold border-r last:border-r-0 ${thText} ${tableBorder}`} {...p} />,
    td: ({ style, ...p }) => <td style={style} className={`px-3 py-2 align-top border-r last:border-r-0 ${tdText} ${tableBorder}`} {...p} />,
  };
};

function sourceLabel(s) {
  if (!s) return null;
  if (s.file_name || s.fileName) {
    const name = s.file_name || s.fileName;
    const page = s.page || s.page_number;
    return `${name}${page ? ` — Page ${page}` : ''}`;
  }
  return s.label || s.title || s.source || (s.file_id ? `Document ${String(s.file_id).slice(0, 6)}` : null);
}

function Sources({ sources, t }) {
  if (!sources || sources.length === 0) return null;
  const seen = new Set();
  const items = [];
  for (const s of sources) {
    const label = sourceLabel(s);
    if (!label || seen.has(label)) continue;
    seen.add(label);
    items.push(label);
    if (items.length >= 8) break;
  }
  if (items.length === 0) return null;
  return (
    <div className="mt-2 flex flex-wrap gap-1.5">
      {items.map((label, i) => (
        <div key={i} className={`flex max-w-full items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs ${t.line} ${t.muted}`}>
          <svg className="h-3.5 w-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /></svg>
          <span className="min-w-0 max-w-[16rem] truncate">{label}</span>
        </div>
      ))}
    </div>
  );
}

const STARTERS = [
  'What is this about?',
  'Summarize the key documents',
  'What are the main points?',
  'What should I know first?',
];

export default function DemoChat({ theme, activeConversationId, onEnsureConversation, onBusyChange, onAfterTurn, onLimit, hasThread, onComposerFocus }) {
  const t = bucketClasses(theme === 'dark');
  const md = buildMarkdownComponents(t.isDark);
  const [messages, setMessages] = useState([]);
  const [streaming, setStreaming] = useState(null);
  const [thinking, setThinking] = useState(false);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const scrollRef = useRef(null);
  const composerRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    requestAnimationFrame(() => { const el = scrollRef.current; if (el) el.scrollTop = el.scrollHeight; });
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (!activeConversationId) { setMessages([]); return; }
      setLoadingHistory(true);
      try {
        const data = await demoApi.getMessages(activeConversationId);
        if (!cancelled) { setMessages(data.messages || []); scrollToBottom(); }
      } catch { /* ignore */ } finally { if (!cancelled) setLoadingHistory(false); }
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
        onToken: (tok) => { setThinking(false); setStreaming((s) => (s || '') + tok); },
      });
      setMessages((m) => [...m.filter((x) => x.id !== tempUser.id), result.user_message, result.assistant_message]);
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
    <section className="flex h-[calc(100dvh-2.5rem)] min-w-0 flex-1 flex-col">
      <div ref={scrollRef} className="flex-1 overflow-y-auto overflow-x-hidden px-5 py-5 pb-8 [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-black/10 hover:[&::-webkit-scrollbar-thumb]:bg-black/20">
        <div className="mx-auto flex min-h-full max-w-3xl flex-col">
          {loadingHistory ? (
            <div className="space-y-4">{[1, 2, 3].map((i) => <div key={i} className={`h-12 animate-pulse rounded-[1.2rem] ${i % 2 === 0 ? 'ml-auto w-2/3' : 'w-3/4'} ${t.subtle}`} />)}</div>
          ) : empty ? (
            <div className="flex flex-1 flex-col items-center justify-center py-16 text-center">
              <p className={`text-[15px] ${t.muted}`}>Ask anything about these documents — answers are grounded and cited.</p>
              <div className="mt-6 grid w-full max-w-xl gap-2 sm:grid-cols-2">
                {STARTERS.map((s) => (
                  <button key={s} onClick={() => send(s)} className={`rounded-[0.9rem] border px-4 py-3 text-left text-sm transition ${t.line} ${t.threadIdle} ${t.bodyCls}`}>{s}</button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((msg) => (
                <div key={msg.id} className={`group relative flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {msg.role === 'assistant' ? (
                    <div className={`w-full max-w-[85%] text-[15px] leading-8 ${t.bodyCls}`}>
                      <ReactMarkdown remarkPlugins={[remarkGfm]} components={md}>{msg.content || ''}</ReactMarkdown>
                      <Sources sources={msg.sources} t={t} />
                    </div>
                  ) : (
                    <div className="flex max-w-[85%] flex-col items-end">
                      <div className="w-fit max-w-full break-words rounded-[1.05rem] bg-blue-600 px-3.5 py-2 text-[15px] leading-7 text-white">
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                      </div>
                    </div>
                  )}
                </div>
              ))}
              {thinking && (
                <div className="flex justify-start">
                  <div className={`flex items-center gap-2.5 px-1 py-3 text-sm ${t.muted}`}>
                    <svg className="h-4 w-4 shrink-0 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" strokeOpacity=".25" /><path d="M12 2a10 10 0 0 1 10 10" /></svg>
                    Reading the documents…
                  </div>
                </div>
              )}
              {streaming != null && (
                <div className="flex justify-start">
                  <div className={`w-full max-w-[85%] text-[15px] leading-8 ${t.bodyCls}`}>
                    <ReactMarkdown remarkPlugins={[remarkGfm]} components={md}>{streaming}</ReactMarkdown>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Composer — same shell as BucketPage */}
      <div className="px-4 pb-4 pt-1">
        <div className={`mx-auto max-w-3xl overflow-hidden rounded-[1.25rem] border ${t.subtle} ${t.line}`}>
          <textarea
            ref={composerRef}
            rows={1}
            value={input}
            onFocus={onComposerFocus}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
            placeholder="Message…"
            className={`w-full max-h-[200px] resize-none bg-transparent px-4 pt-3 pb-1 text-sm leading-6 outline-none ${t.titleCls}`}
          />
          <div className="flex items-center justify-end px-3 pb-2 pt-1">
            <button
              type="button"
              data-tour="send"
              onClick={() => send()}
              disabled={!input.trim() || sending}
              className={`flex h-8 w-8 items-center justify-center rounded-full transition disabled:opacity-40 ${t.primary}`}
            >
              {sending ? <Spinner className="h-4 w-4" /> : (
                <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" /></svg>
              )}
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
