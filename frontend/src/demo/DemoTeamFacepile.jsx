// Slack-style team facepile for the demo workspace header — mirrors the
// dashboard's TeamFacepile (avatars + "+" affordance + click opens the team
// modal). Themed to the demo palette (light/dark).
import React, { useEffect, useState } from 'react';
import { demoApi, DemoLimitError } from './demoApi';
import { themeOptions } from './demoTheme';
import { DemoModal, DemoButton, DemoField, DemoInput, ErrorNote } from './DemoShell';
import { cn } from '../lib/utils';

const MAX_FACES = 4;
const TEAM_COLORS = ['#2563EB', '#0EA5E9', '#6366F1', '#10B981', '#F59E0B', '#EC4899', '#EF4444', '#14B8A6'];

function timeAgo(iso) {
  if (!iso) return '';
  const ms = Date.now() - new Date(iso).getTime();
  if (ms < 60_000) return 'just now';
  const m = Math.floor(ms / 60_000);
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24);
  if (d < 7) return `${d}d ago`;
  return new Date(iso).toLocaleDateString();
}

export default function DemoTeamFacepile({ theme = 'light', members, capTeamMembers, onChange, onLimit }) {
  const isDark = theme === 'dark';
  const ring = isDark ? 'ring-[#020617]' : 'ring-white';
  const [open, setOpen] = useState(false);
  const list = members || [];
  const shown = list.slice(0, MAX_FACES);
  const overflow = list.length - shown.length;
  const has = list.length > 0;
  const names = list.map((m) => m.name || m.email || 'Member').join(', ');

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        title={has ? `Team · ${names}` : 'Add team members'}
        aria-label={has ? 'Team members — view and add' : 'Add team members'}
        data-tour="team"
        className="group inline-flex shrink-0 items-center transition hover:opacity-95"
      >
        <div className="flex items-center -space-x-2">
          {shown.map((m) => (
            <div key={m.id} className="relative">
              <div
                className={cn('flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold text-white ring-2 transition group-hover:translate-y-[-1px]', ring)}
                style={{ backgroundColor: m.color || '#64748b' }}
              >
                {(m.name || m.email || '?').charAt(0).toUpperCase()}
              </div>
              {m.is_online && (
                <span className={cn('absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-emerald-400 ring-2', ring)} />
              )}
            </div>
          ))}
          {overflow > 0 && (
            <div className={cn('flex h-8 w-8 items-center justify-center rounded-full text-[11px] font-semibold ring-2', ring, isDark ? 'bg-white/[0.08] text-white/80' : 'bg-slate-200 text-slate-600')}>
              +{overflow}
            </div>
          )}
          {/* Add-member affordance — merged into the same bubble row */}
          <div className={cn('relative z-10 flex h-8 w-8 items-center justify-center rounded-full ring-2 transition group-hover:translate-y-[-1px]', ring,
            isDark ? 'bg-white/[0.08] text-white/75 group-hover:bg-white/[0.16] group-hover:text-white' : 'bg-slate-200 text-slate-600 group-hover:bg-slate-300 group-hover:text-slate-900')}>
            <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M12 5v14M5 12h14" />
            </svg>
          </div>
        </div>
      </button>
      <DemoTeamManageModal
        open={open}
        onClose={() => { setOpen(false); onChange?.(); }}
        theme={theme}
        members={list}
        capTeamMembers={capTeamMembers}
        onChange={onChange}
        onLimit={onLimit}
      />
    </>
  );
}

// Team management modal — view current demo team + invite a new one. Mirrors
// the dashboard TeamManageModal shape: avatar row, list of members with details,
// inline invite form when there's capacity.
function DemoTeamManageModal({ open, onClose, theme, members, capTeamMembers, onChange, onLimit }) {
  const p = themeOptions[theme];
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [color, setColor] = useState(TEAM_COLORS[0]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [okMsg, setOkMsg] = useState('');
  const usedColors = new Set((members || []).map((m) => m.color).filter(Boolean));
  const remaining = Math.max(0, (capTeamMembers ?? 0) - (members || []).length);

  useEffect(() => {
    if (!open) return;
    setError(''); setOkMsg('');
    setName(''); setEmail('');
    setColor(TEAM_COLORS.find((c) => !usedColors.has(c)) || TEAM_COLORS[0]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  const invite = async (e) => {
    e?.preventDefault();
    if (!name.trim() || !email.trim()) { setError('Enter a name and email.'); return; }
    setError(''); setOkMsg(''); setLoading(true);
    try {
      await demoApi.teamInvite({ name: name.trim(), email: email.trim(), color });
      setOkMsg(`Invite sent to ${email}.`);
      setName(''); setEmail('');
      onChange?.();
    } catch (e) {
      if (e instanceof DemoLimitError) { onClose?.(); onLimit?.(e.limit); return; }
      setError(e.message || 'Could not send the invite.');
    } finally { setLoading(false); }
  };

  return (
    <DemoModal open={open} onClose={onClose} theme={theme} widthClass="max-w-lg">
      <div className="max-h-[88vh] overflow-y-auto p-6 sm:p-7">
        <div className="flex items-start justify-between">
          <div>
            <h2 className={cn('text-lg font-bold', p.title)}>Team</h2>
            <p className={cn('mt-1 text-sm', p.text)}>
              People exploring this demo with you. They get an email link and join directly — no code.
            </p>
          </div>
          <button onClick={onClose} className={cn('rounded-lg p-1.5 transition', p.muted, theme === 'dark' ? 'hover:bg-white/5' : 'hover:bg-slate-100')}>
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 6l12 12M18 6L6 18" /></svg>
          </button>
        </div>

        <p className={cn('mt-4 text-[11px] font-semibold uppercase tracking-wide', p.muted)}>
          Current ({(members || []).length}{capTeamMembers != null ? `/${capTeamMembers}` : ''})
        </p>
        <div className="mt-2 space-y-1.5">
          {(members || []).length === 0 ? (
            <p className={cn('rounded-xl border px-3 py-3 text-sm', theme === 'dark' ? 'border-white/10' : 'border-slate-200', p.muted)}>
              No teammates yet. Invite someone below.
            </p>
          ) : (
            (members || []).map((m) => (
              <div key={m.id} className={cn('flex items-center gap-3 rounded-xl border px-3 py-2.5', theme === 'dark' ? 'border-white/10 bg-white/[0.025]' : 'border-slate-200 bg-slate-50/80')}>
                <div className="relative">
                  <div className="flex h-9 w-9 items-center justify-center rounded-full text-sm font-semibold text-white" style={{ backgroundColor: m.color || '#64748b' }}>
                    {(m.name || m.email || '?').charAt(0).toUpperCase()}
                  </div>
                  {m.is_online && <span className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-emerald-400 ring-2 ring-white" />}
                </div>
                <div className="min-w-0 flex-1">
                  <p className={cn('truncate text-sm font-semibold', p.title)}>
                    {m.name}
                    {m.role && <span className={cn('ml-1.5 text-[11px] font-medium', p.muted)}>· {m.role}</span>}
                  </p>
                  <p className={cn('truncate text-xs', p.muted)}>{m.email}</p>
                </div>
                <div className="shrink-0 text-right">
                  {m.is_online ? (
                    <span className="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[11px] font-semibold text-emerald-500">Online</span>
                  ) : m.joined ? (
                    <span className={cn('text-[11px]', p.muted)}>Last seen {timeAgo(m.last_seen_at)}</span>
                  ) : (
                    <span className="rounded-full bg-amber-500/10 px-2 py-0.5 text-[11px] font-semibold text-amber-600">Invited</span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Invite form — only when there's capacity */}
        {remaining > 0 ? (
          <form onSubmit={invite} className={cn('mt-6 rounded-2xl border p-4', theme === 'dark' ? 'border-white/10 bg-white/[0.02]' : 'border-slate-200 bg-white')}>
            <p className={cn('text-sm font-semibold', p.title)}>Invite a teammate</p>
            <p className={cn('mt-0.5 text-xs', p.muted)}>{remaining} seat{remaining === 1 ? '' : 's'} left in this demo.</p>
            <div className="mt-3 grid gap-3 sm:grid-cols-2">
              <DemoField theme={theme} label="Name"><DemoInput theme={theme} value={name} onChange={(e) => setName(e.target.value)} placeholder="Alex Doe" /></DemoField>
              <DemoField theme={theme} label="Email"><DemoInput theme={theme} type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="alex@company.com" /></DemoField>
            </div>
            <DemoField theme={theme} label="Avatar color">
              <div className="flex flex-wrap gap-2">
                {TEAM_COLORS.map((c) => (
                  <button key={c} type="button" onClick={() => setColor(c)} className={cn('h-7 w-7 rounded-full ring-2 ring-offset-2 transition', theme === 'dark' ? 'ring-offset-[#0b1424]' : 'ring-offset-white', color === c ? 'ring-blue-500' : 'ring-transparent')} style={{ background: c }} aria-label={`Color ${c}`} />
                ))}
              </div>
            </DemoField>
            <ErrorNote theme={theme}>{error}</ErrorNote>
            {okMsg && <p className="mt-2 rounded-lg bg-emerald-500/10 px-3 py-2 text-xs font-medium text-emerald-600">{okMsg}</p>}
            <DemoButton theme={theme} type="submit" className="mt-3 w-full" loading={loading}>Send invite</DemoButton>
          </form>
        ) : (
          <div className={cn('mt-6 rounded-2xl border px-4 py-3 text-sm', theme === 'dark' ? 'border-amber-500/20 bg-amber-500/5 text-amber-300' : 'border-amber-300 bg-amber-50 text-amber-700')}>
            You’ve used all {capTeamMembers} teammate seats in this demo. There’s no limit on the real thing — open Feedback to talk.
          </div>
        )}
      </div>
    </DemoModal>
  );
}
