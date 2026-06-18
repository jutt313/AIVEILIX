import React, { useEffect, useState } from 'react';
import TeamManageModal from './TeamManageModal';
import { useTeamContext } from './useTeamContext';
import { teamApi } from '../../api/team';
import { useAppTheme } from './theme';

const MAX_FACES = 4;

// Slack-style facepile of team member avatars for the dashboard header.
// Owner-only (mirrors TeamButton). Clicking opens the team workspace modal.
export default function TeamFacepile() {
  const { isOwner } = useTeamContext();
  const { theme } = useAppTheme();
  const isDark = theme === 'dark';

  const [members, setMembers] = useState([]);
  const [open, setOpen] = useState(false);

  const loadMembers = async () => {
    try {
      const data = await teamApi.listMembers();
      setMembers((data.members || []).filter((m) => m.status === 'accepted'));
    } catch (_) {
      setMembers([]);
    }
  };

  useEffect(() => {
    if (isOwner) loadMembers();
  }, [isOwner]);

  if (!isOwner) return null;

  // Ring color blends each avatar into the page background.
  const ring = isDark ? 'ring-[#0b1220]' : 'ring-[#f8fafc]';
  const shown = members.slice(0, MAX_FACES);
  const overflow = members.length - shown.length;
  const hasMembers = members.length > 0;
  const names = members.map((m) => m.display_name || m.invite_email || 'Member').join(', ');

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        title={hasMembers ? `Team · ${names}` : 'Add team members'}
        aria-label={hasMembers ? 'Team members — view and add' : 'Add team members'}
        className="group inline-flex shrink-0 items-center transition hover:opacity-95"
      >
        <div className="flex items-center -space-x-2">
          {shown.map((m) => (
            <div key={m.id} className="relative">
              {m.avatar_url ? (
                <img
                  src={m.avatar_url}
                  alt=""
                  className={`h-8 w-8 rounded-full object-cover ring-2 ${ring} transition group-hover:translate-y-[-1px]`}
                />
              ) : (
                <div
                  className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold text-white ring-2 ${ring} transition group-hover:translate-y-[-1px]`}
                  style={{ backgroundColor: m.display_color || '#64748b' }}
                >
                  {(m.display_name || m.invite_email || '?').charAt(0).toUpperCase()}
                </div>
              )}
              {m.is_online && (
                <span className={`absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-emerald-400 ring-2 ${ring}`} />
              )}
            </div>
          ))}
          {overflow > 0 && (
            <div
              className={`flex h-8 w-8 items-center justify-center rounded-full text-[11px] font-semibold ring-2 ${ring} ${
                isDark ? 'bg-white/[0.08] text-white/80' : 'bg-slate-200 text-slate-600'
              }`}
            >
              +{overflow}
            </div>
          )}
          {/* Add-member affordance — merged into the same bubble as current members */}
          <div
            className={`relative z-10 flex h-8 w-8 items-center justify-center rounded-full ring-2 ${ring} transition group-hover:translate-y-[-1px] ${
              isDark
                ? 'bg-white/[0.08] text-white/75 group-hover:bg-white/[0.16] group-hover:text-white'
                : 'bg-slate-200 text-slate-600 group-hover:bg-slate-300 group-hover:text-slate-900'
            }`}
          >
            <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M12 5v14M5 12h14" />
            </svg>
          </div>
        </div>
      </button>
      <TeamManageModal open={open} onClose={() => { setOpen(false); loadMembers(); }} />
    </>
  );
}
