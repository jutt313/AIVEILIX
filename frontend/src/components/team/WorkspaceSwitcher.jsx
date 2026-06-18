import React, { useEffect, useRef, useState } from 'react';
import { setActiveWorkspace } from '../../api/auth';
import { useAppTheme } from './theme';

/**
 * Compact dashboard control to switch the active workspace for a user who can
 * act in more than one — their own account ('self') plus any team they belong
 * to. Renders nothing when there's only a single workspace, so pure owners and
 * pure members never see it.
 *
 * Selecting a workspace persists it (X-Workspace header) and hard-reloads to
 * /dashboard so the backend re-resolves context and the router swaps the
 * owner/member view cleanly.
 */
export default function WorkspaceSwitcher({ workspaces, active }) {
  const { theme, palette } = useAppTheme();
  const [open, setOpen] = useState(false);
  const ref = useRef(null);
  const isDark = theme === 'dark';

  useEffect(() => {
    function onDocClick(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener('mousedown', onDocClick);
    return () => document.removeEventListener('mousedown', onDocClick);
  }, []);

  if (!Array.isArray(workspaces) || workspaces.length <= 1) return null;

  const current = workspaces.find((w) => w.id === active) || workspaces[0];

  function choose(ws) {
    setOpen(false);
    if (ws.id === active) return;
    setActiveWorkspace(ws.id);
    window.location.assign('/dashboard');
  }

  const btn = `inline-flex items-center gap-2 rounded-xl border px-3 py-2 text-sm font-medium transition ${
    isDark ? 'border-white/10 bg-white/[0.04] text-slate-100 hover:bg-white/[0.08]' : 'border-slate-200 bg-white text-slate-800 hover:bg-slate-50'
  }`;
  const menu = `absolute right-0 z-50 mt-2 w-64 overflow-hidden rounded-2xl border shadow-xl ${
    isDark ? 'border-white/10 bg-[#0b1220]' : 'border-slate-200 bg-white'
  }`;

  return (
    <div className="relative" ref={ref}>
      <button type="button" className={btn} onClick={() => setOpen((o) => !o)} aria-haspopup="listbox" aria-expanded={open}>
        <Dot color={current.color} type={current.type} />
        <span className="max-w-[10rem] truncate">{current.label}</span>
        <svg width="14" height="14" viewBox="0 0 20 20" fill="none" className="opacity-60">
          <path d="M6 8l4 4 4-4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>

      {open && (
        <div className={menu} role="listbox">
          <div className={`px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.18em] ${palette.muted}`}>
            Switch workspace
          </div>
          {workspaces.map((ws) => (
            <button
              key={ws.id}
              type="button"
              role="option"
              aria-selected={ws.id === active}
              onClick={() => choose(ws)}
              className={`flex w-full items-center gap-2.5 px-3 py-2.5 text-left text-sm transition ${
                isDark ? 'hover:bg-white/[0.06]' : 'hover:bg-slate-50'
              } ${ws.id === active ? (isDark ? 'bg-white/[0.04]' : 'bg-slate-50') : ''}`}
            >
              <Dot color={ws.color} type={ws.type} />
              <span className="min-w-0 flex-1 truncate">
                <span className={palette.title}>{ws.label}</span>
                <span className={`ml-1 text-xs ${palette.muted}`}>{ws.type === 'owner' ? '· You' : '· Team'}</span>
              </span>
              {ws.id === active && (
                <svg width="16" height="16" viewBox="0 0 20 20" fill="none" className="shrink-0 text-blue-500">
                  <path d="M5 10l3.5 3.5L15 7" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function Dot({ color, type }) {
  const bg = color || (type === 'owner' ? '#3B82F6' : '#10B981');
  return <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ backgroundColor: bg }} />;
}
