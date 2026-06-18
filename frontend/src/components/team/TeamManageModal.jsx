import React, { useCallback, useEffect, useState } from 'react';
import ActivityFeed from './ActivityFeed';
import InviteWizard from './InviteWizard';
import EditMemberForm from './EditMemberForm';
import Modal from './Modal';
import { teamApi } from '../../api/team';
import { useAppTheme } from './theme';

const VIEW_FEED = 'feed';
const VIEW_INVITE = 'invite';
const VIEW_EDIT = 'edit';

export default function TeamManageModal({ open, onClose }) {
  const { theme, palette } = useAppTheme();
  const isDark = theme === 'dark';

  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [onlineIds, setOnlineIds] = useState(new Set());

  const [view, setView] = useState(VIEW_FEED);
  const [selectedId, setSelectedId] = useState(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await teamApi.listMembers();
      setMembers(data.members || []);
      // Best-effort online status sync — ignore failure
      try {
        const activity = await teamApi.getActivity();
        setOnlineIds(new Set(activity.online_member_ids || []));
      } catch (_) { /* ignore */ }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (open) {
      setView(VIEW_FEED);
      setSelectedId(null);
      refresh();
    }
  }, [open, refresh]);

  function openInvite() {
    setView(VIEW_INVITE);
    setSelectedId(null);
  }

  function openMember(memberId) {
    setSelectedId(memberId);
    setView(VIEW_EDIT);
  }

  const sidebarBg = isDark ? 'bg-transparent' : 'bg-transparent';

  return (
    <Modal open={open} onClose={onClose} fixedSize bare>
      <header className="flex items-center justify-between gap-4 px-7 pt-6 pb-4">
        <div className="min-w-0">
          <h2 className={`text-base font-semibold tracking-tight ${palette.title}`}>Team workspace</h2>
          <p className={`mt-0.5 text-xs ${palette.muted}`}>Activity feed, members and access.</p>
        </div>
        <button
          onClick={onClose}
          aria-label="Close"
          className={`shrink-0 rounded-full p-1.5 transition ${
            isDark ? 'text-slate-400 hover:bg-white/[0.05] hover:text-white' : 'text-slate-500 hover:bg-slate-100'
          }`}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </header>

      {/* Split layout — no dividers, just spacing */}
      <div className="flex flex-1 min-h-0 px-2 pb-2 gap-2">
        {/* Left: member list */}
        <aside className={`flex w-[15rem] shrink-0 flex-col overflow-hidden rounded-2xl ${sidebarBg}`}>
          {/* Top navigation buttons */}
          <div className="px-2 pt-3 pb-2 space-y-0.5">
            <NavButton
              active={view === VIEW_FEED}
              onClick={() => {
                setView(VIEW_FEED);
                setSelectedId(null);
              }}
              icon={
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                </svg>
              }
              label="Activity log"
              palette={palette}
              isDark={isDark}
            />
            <NavButton
              active={view === VIEW_INVITE}
              onClick={openInvite}
              icon={
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="12" y1="5" x2="12" y2="19" />
                  <line x1="5" y1="12" x2="19" y2="12" />
                </svg>
              }
              label="Invite member"
              palette={palette}
              isDark={isDark}
            />
          </div>

          {/* Members section label */}
          <div className={`px-4 pt-2 pb-1 text-[10px] font-semibold uppercase tracking-[0.18em] ${palette.subtle}`}>
            Members
          </div>

          <div className="flex-1 overflow-y-auto px-2 pb-3">
            {loading && (
              <div className={`px-3 text-xs ${palette.muted}`}>Loading...</div>
            )}

            {!loading && members.length === 0 && (
              <div className={`px-3 py-6 text-center text-xs ${palette.muted}`}>
                No members yet.
              </div>
            )}

            <ul className="space-y-0.5">
              {members.map((m) => {
                const isSelected = selectedId === m.id && view === VIEW_EDIT;
                const isOnline = onlineIds.has(m.id);
                const rowBase = isDark ? 'hover:bg-white/[0.04]' : 'hover:bg-slate-100';
                const rowSelected = isDark ? 'bg-white/[0.06]' : 'bg-slate-100';
                return (
                  <li key={m.id}>
                    <button
                      onClick={() => openMember(m.id)}
                      className={`flex w-full items-center gap-2.5 rounded-xl px-2.5 py-2 text-left transition ${
                        isSelected ? rowSelected : rowBase
                      }`}
                    >
                      <div className="relative shrink-0">
                        {m.avatar_url ? (
                          <img
                            src={m.avatar_url}
                            alt=""
                            className="h-8 w-8 rounded-full object-cover"
                          />
                        ) : (
                          <div
                            className="h-8 w-8 rounded-full flex items-center justify-center text-white text-xs font-semibold"
                            style={{ backgroundColor: m.display_color || '#64748b' }}
                          >
                            {(m.display_name || m.invite_email || '?').charAt(0).toUpperCase()}
                          </div>
                        )}
                        {isOnline && (
                          <span className={`absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-emerald-400 ${
                            isDark ? 'ring-2 ring-[#0b1220]' : 'ring-2 ring-[#f8fafc]'
                          }`} />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className={`text-xs font-semibold truncate ${palette.title}`}>
                          {m.display_name || '(no name)'}
                        </div>
                        <div className={`text-[10px] truncate ${palette.muted}`}>
                          {m.status === 'pending' ? 'Pending invite' : m.invite_email}
                        </div>
                      </div>
                    </button>
                  </li>
                );
              })}
            </ul>
          </div>

          <div className={`px-4 py-2 text-[10px] uppercase tracking-[0.18em] ${palette.subtle}`}>
            {members.length} member{members.length === 1 ? '' : 's'}
          </div>
        </aside>

        {/* Right: detail pane (own rounded container, no shared border) */}
        <main className={`flex-1 min-w-0 overflow-y-auto rounded-2xl px-6 py-5 ${
          isDark ? 'bg-white/[0.015]' : 'bg-white/60'
        }`}>
          {error && (
            <div className={`mb-4 text-sm rounded-2xl px-4 py-3 ${palette.error}`}>{error}</div>
          )}

          {view === VIEW_FEED && (
            <ActivityFeed
              onInvite={openInvite}
              onPickMember={openMember}
            />
          )}

          {view === VIEW_INVITE && (
            <InviteWizard
              onCancel={() => setView(VIEW_FEED)}
              onSuccess={async () => {
                setView(VIEW_FEED);
                await refresh();
              }}
            />
          )}

          {view === VIEW_EDIT && selectedId && (
            <EditMemberForm
              key={selectedId}
              memberId={selectedId}
              onBack={() => {
                setSelectedId(null);
                setView(VIEW_FEED);
              }}
              onChanged={refresh}
              onRemoved={async () => {
                setSelectedId(null);
                setView(VIEW_FEED);
                await refresh();
              }}
              hideBackButton
            />
          )}
        </main>
      </div>
    </Modal>
  );
}

function NavButton({ active, onClick, icon, label, palette, isDark }) {
  const activeCls = isDark ? 'bg-white/[0.06] text-white' : 'bg-slate-100 text-slate-900';
  const idleCls = isDark
    ? 'text-slate-300 hover:bg-white/[0.04] hover:text-white'
    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900';
  return (
    <button
      onClick={onClick}
      className={`flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-medium transition ${
        active ? activeCls : idleCls
      }`}
    >
      <span className="opacity-80">{icon}</span>
      <span>{label}</span>
    </button>
  );
}
