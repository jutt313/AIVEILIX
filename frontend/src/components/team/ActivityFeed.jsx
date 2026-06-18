import React, { useEffect, useRef, useState } from 'react';
import { teamApi } from '../../api/team';
import { useAppTheme } from './theme';

const POLL_INTERVAL_MS = 8000;

function relativeTime(iso) {
  if (!iso) return '';
  const then = new Date(iso).getTime();
  const now = Date.now();
  const diffSec = Math.max(0, Math.floor((now - then) / 1000));
  if (diffSec < 10) return 'just now';
  if (diffSec < 60) return `${diffSec}s ago`;
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
  if (diffSec < 604800) return `${Math.floor(diffSec / 86400)}d ago`;
  return new Date(iso).toLocaleDateString();
}

function actionVerb(kind) {
  switch (kind) {
    case 'joined': return 'joined the workspace';
    case 'invited': return 'was invited';
    case 'created_thread': return 'started a thread';
    case 'sent_message': return 'sent a message';
    default: return 'did something';
  }
}

function actionTint(kind, isDark) {
  switch (kind) {
    case 'joined': return isDark ? 'text-emerald-400' : 'text-emerald-600';
    case 'invited': return isDark ? 'text-amber-400' : 'text-amber-600';
    case 'created_thread': return isDark ? 'text-violet-400' : 'text-violet-600';
    case 'sent_message': return isDark ? 'text-blue-400' : 'text-blue-600';
    default: return isDark ? 'text-slate-400' : 'text-slate-500';
  }
}

function MemberAvatar({ avatar_url, display_color, display_name, size = 32, online = false, ringBg }) {
  const initial = (display_name || '?').charAt(0).toUpperCase();
  return (
    <div className="relative shrink-0">
      {avatar_url ? (
        <img src={avatar_url} alt="" className="rounded-full object-cover" style={{ height: size, width: size }} />
      ) : (
        <div
          className="rounded-full flex items-center justify-center text-white font-semibold"
          style={{
            height: size,
            width: size,
            backgroundColor: display_color || '#64748b',
            fontSize: size <= 24 ? 10 : size <= 32 ? 12 : 14,
          }}
        >
          {initial}
        </div>
      )}
      {online && (
        <span
          className={`absolute -bottom-0.5 -right-0.5 rounded-full bg-emerald-400 ${ringBg}`}
          style={{
            height: size <= 24 ? 8 : 10,
            width: size <= 24 ? 8 : 10,
            boxShadow: '0 0 0 2px var(--ring-bg, transparent), 0 0 10px rgba(52,211,153,0.5)',
          }}
        />
      )}
    </div>
  );
}

export default function ActivityFeed({ onInvite, onPickMember }) {
  const { theme, palette } = useAppTheme();
  const isDark = theme === 'dark';
  const [items, setItems] = useState([]);
  const [members, setMembers] = useState([]);
  const [online, setOnline] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [refreshedAt, setRefreshedAt] = useState(Date.now());
  const pollRef = useRef(null);

  async function load(initial = false) {
    if (initial) setLoading(true);
    try {
      const [act, list] = await Promise.all([
        teamApi.getActivity(),
        teamApi.listMembers(),
      ]);
      setItems(act.items || []);
      setOnline(new Set(act.online_member_ids || []));
      setMembers(list.members || []);
      setRefreshedAt(Date.now());
    } catch (_) {
      // swallow — keep stale data
    } finally {
      if (initial) setLoading(false);
    }
  }

  useEffect(() => {
    load(true);
    pollRef.current = window.setInterval(() => load(false), POLL_INTERVAL_MS);
    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current);
    };
  }, []);

  // Repaint relative-times every 20s so "just now" → "1m ago" feels alive.
  const [, forceTick] = useState(0);
  useEffect(() => {
    const id = window.setInterval(() => forceTick((x) => x + 1), 20000);
    return () => window.clearInterval(id);
  }, []);

  const onlineMembers = members.filter((m) => online.has(m.id));
  const ringBg = isDark ? 'ring-2 ring-[#0b1220]' : 'ring-2 ring-[#f8fafc]';

  return (
    <div className="h-full flex flex-col">
      {/* Header row */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className={`text-base font-semibold ${palette.title}`}>Live activity</h3>
          <p className={`text-xs ${palette.muted}`}>
            Auto-refreshing · last update {relativeTime(new Date(refreshedAt).toISOString())}
          </p>
        </div>
        <button
          onClick={onInvite}
          className={`rounded-xl px-3 py-1.5 text-xs font-semibold ${palette.primary}`}
        >
          + Invite
        </button>
      </div>

      {/* Online now strip */}
      <div className="mb-5">
        <div className={`mb-2 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.18em] ${palette.muted}`}>
          <span className="inline-flex items-center gap-1.5">
            <span className="relative inline-flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400" />
            </span>
            Online now
          </span>
          <span className={`${palette.subtle} normal-case tracking-normal font-normal`}>
            {onlineMembers.length === 0
              ? '— nobody active in the last 15 minutes'
              : `${onlineMembers.length} active in the last 15 minutes`}
          </span>
        </div>
        {onlineMembers.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {onlineMembers.map((m) => (
              <button
                key={m.id}
                onClick={() => onPickMember?.(m.id)}
                className={`group flex items-center gap-2 rounded-full pl-1 pr-3 py-1 transition ${
                  isDark ? 'bg-white/[0.04] hover:bg-white/[0.07]' : 'bg-slate-100 hover:bg-slate-200'
                }`}
                title={`Open ${m.display_name}`}
              >
                <MemberAvatar
                  avatar_url={m.avatar_url}
                  display_color={m.display_color}
                  display_name={m.display_name}
                  size={22}
                  online
                  ringBg={ringBg}
                />
                <span className={`text-xs font-medium ${palette.title}`}>{m.display_name}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Feed */}
      {loading && <div className={`text-xs ${palette.muted}`}>Loading...</div>}
      {!loading && items.length === 0 && (
        <div className={`mt-8 text-center text-xs ${palette.muted}`}>
          No activity yet. Invite someone or send a message to start the feed.
        </div>
      )}

      <div className="flex-1 overflow-y-auto pr-1 space-y-1">
        {items.map((it) => {
          const isOnline = online.has(it.team_member_id);
          const verbCls = actionTint(it.kind, isDark);
          return (
            <button
              key={it.id}
              onClick={() => it.team_member_id && onPickMember?.(it.team_member_id)}
              className={`group flex w-full items-start gap-3 rounded-xl px-3 py-2.5 text-left transition ${
                isDark ? 'hover:bg-white/[0.03]' : 'hover:bg-slate-100'
              }`}
            >
              <MemberAvatar
                avatar_url={it.avatar_url}
                display_color={it.display_color}
                display_name={it.display_name}
                size={32}
                online={isOnline}
                ringBg={ringBg}
              />

              <div className="flex-1 min-w-0">
                {/* WHO + WHAT */}
                <div className="text-xs leading-relaxed">
                  <span className={`font-semibold ${palette.title}`}>
                    {it.display_name || 'A teammate'}
                  </span>{' '}
                  <span className={verbCls}>{actionVerb(it.kind)}</span>
                  {it.bucket_name && (
                    <>
                      {' '}
                      <span className={palette.muted}>in</span>{' '}
                      <span className={`font-medium ${palette.title}`}>{it.bucket_name}</span>
                    </>
                  )}
                  {it.conversation_title && it.kind === 'sent_message' && (
                    <>
                      {' · '}
                      <span className={`${palette.subtle}`}>{it.conversation_title}</span>
                    </>
                  )}
                  {it.conversation_title && it.kind === 'created_thread' && (
                    <>
                      {' '}
                      <span className={`font-medium ${palette.title}`}>"{it.conversation_title}"</span>
                    </>
                  )}
                </div>

                {/* SNIPPET */}
                {it.snippet && (
                  <div className={`mt-1 text-[11px] truncate italic ${palette.text}`}>
                    "{it.snippet}"
                  </div>
                )}

                {/* WHEN */}
                <div className={`mt-1 text-[10px] ${palette.subtle}`}>
                  {relativeTime(it.created_at)}
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
