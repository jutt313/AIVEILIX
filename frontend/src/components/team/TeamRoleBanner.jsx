import React from 'react';
import { useTeamContext } from './useTeamContext';
import { useAppTheme } from './theme';

export default function TeamRoleBanner() {
  const { ctx, isMember } = useTeamContext();
  const { theme } = useAppTheme();
  if (!isMember || !ctx) return null;

  const shellCls = theme === 'dark'
    ? 'border-white/10 bg-slate-900/85 text-slate-100'
    : 'border-slate-200 bg-white/95 text-slate-800';

  return (
    <div className={`fixed bottom-4 left-1/2 -translate-x-1/2 z-30 flex items-center gap-2.5 rounded-full border px-4 py-1.5 shadow-lg backdrop-blur ${shellCls}`}>
      <span
        className="inline-block h-2.5 w-2.5 rounded-full"
        style={{ backgroundColor: ctx.display_color || '#64748b' }}
      />
      <span className="text-xs font-semibold">
        {ctx.display_name || ctx.email}
      </span>
      <span className="text-[10px] uppercase tracking-[0.18em] opacity-60">
        Team member
      </span>
    </div>
  );
}
