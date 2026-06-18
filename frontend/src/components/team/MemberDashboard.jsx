import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { dashboardApi, signOut } from '../../api/auth';
import { teamApi } from '../../api/team';
import { useAppTheme } from './theme';
import MemberProfileDrawer from './MemberProfileDrawer';

/**
 * Dedicated dashboard for accepted team members.
 *
 * Intentionally minimal: just the buckets the member can access, a welcome
 * header tied to the workspace owner's name, theme toggle, notifications,
 * and the slim profile drawer. No stats charts, no create-bucket button,
 * no billing / MCP / danger zone.
 */
export default function MemberDashboard({ theme, onToggleTheme }) {
  const navigate = useNavigate();
  const { palette } = useAppTheme();
  const isDark = theme === 'dark';

  const [me, setMe] = useState(null);
  const [buckets, setBuckets] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [notifOpen, setNotifOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    const token = sessionStorage.getItem('access_token');
    if (!token) {
      navigate('/login');
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        const [meRes, b, n, p] = await Promise.all([
          teamApi.getMe(),
          dashboardApi.listBuckets(),
          dashboardApi.listNotifications(),
          dashboardApi.getProfile(),
        ]);
        if (cancelled) return;
        setMe(meRes);
        setBuckets(b || []);
        setNotifications(n || []);
        setProfile(p);
      } catch (e) {
        // If token's bad, bounce
        if ((e.message || '').toLowerCase().includes('token')) navigate('/login');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [navigate]);

  async function refreshNotifications() {
    try {
      const n = await dashboardApi.listNotifications();
      setNotifications(n || []);
    } catch (_) {}
  }

  async function handleMarkAllRead() {
    await dashboardApi.markAllRead();
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
  }

  async function handleSignOut() {
    await signOut();
    navigate('/login');
  }

  const unreadCount = notifications.filter((n) => !n.is_read).length;
  const workspaceName = me?.workspace_owner_name || 'your workspace';
  const ownerEmailHint = me?.workspace_owner_email ? ` (${me.workspace_owner_email})` : '';
  const memberName = me?.display_name || profile?.full_name || me?.email?.split('@')[0] || 'there';
  const memberColor = me?.display_color || '#3B82F6';

  const cardBg = isDark
    ? 'bg-white/[0.03] hover:bg-white/[0.06]'
    : 'bg-white/80 hover:bg-white';

  return (
    <div className={`min-h-[100dvh] ${palette.app}`}>
      {/* Subtle gradient backdrop */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute left-1/2 top-[-12rem] h-80 w-80 -translate-x-1/2 rounded-full bg-blue-500/8 blur-3xl" />
        <div className="absolute bottom-[-8rem] right-[-4rem] h-72 w-72 rounded-full bg-cyan-400/6 blur-3xl" />
      </div>

      {/* Top bar */}
      <nav className="relative sticky top-0 z-30 px-4 py-4 sm:px-6">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div
              className="h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: memberColor }}
            />
            <span className={`text-xs font-semibold uppercase tracking-[0.18em] ${palette.muted}`}>
              {workspaceName}
            </span>
          </div>

          <div className="flex items-center gap-1">
            {/* Theme toggle */}
            <button
              type="button"
              onClick={onToggleTheme}
              aria-label="Toggle theme"
              className={`inline-flex h-10 w-10 items-center justify-center rounded-full transition ${
                isDark ? 'text-white/80 hover:bg-white/[0.05] hover:text-white' : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              {isDark ? (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="4" />
                  <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
                </svg>
              ) : (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
                </svg>
              )}
            </button>

            {/* Notifications */}
            <div className="relative">
              <button
                type="button"
                onClick={() => { setNotifOpen((v) => !v); if (!notifOpen) refreshNotifications(); }}
                aria-label="Notifications"
                className={`relative inline-flex h-10 w-10 items-center justify-center rounded-full transition ${
                  isDark ? 'text-white/80 hover:bg-white/[0.05] hover:text-white' : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                  <path d="M13.73 21a2 2 0 0 1-3.46 0" />
                </svg>
                {unreadCount > 0 && (
                  <span className="pointer-events-none absolute right-1 top-1 flex h-[16px] min-w-[16px] items-center justify-center rounded-full bg-blue-500 px-1 text-[9px] font-bold text-white">
                    {unreadCount > 99 ? '99+' : unreadCount}
                  </span>
                )}
              </button>
              {notifOpen && (
                <div
                  className={`absolute right-0 top-12 z-40 w-[22rem] max-w-[92vw] rounded-2xl p-3 ${
                    isDark ? 'bg-[#0b1220] shadow-[0_24px_80px_rgba(2,6,23,0.6)]' : 'bg-white shadow-[0_24px_80px_rgba(148,163,184,0.22)]'
                  }`}
                >
                  <div className="mb-2 flex items-center justify-between px-1">
                    <p className={`text-[10px] font-semibold uppercase tracking-[0.18em] ${palette.muted}`}>
                      Notifications
                    </p>
                    {unreadCount > 0 && (
                      <button onClick={handleMarkAllRead} className="text-[10px] font-medium text-blue-500 hover:underline">
                        Mark all read
                      </button>
                    )}
                  </div>
                  {notifications.length === 0 ? (
                    <p className={`px-2 py-6 text-center text-xs ${palette.muted}`}>
                      Nothing here yet.
                    </p>
                  ) : (
                    <ul className="max-h-72 space-y-1 overflow-y-auto">
                      {notifications.slice(0, 20).map((n) => (
                        <li
                          key={n.id}
                          className={`rounded-xl px-3 py-2 text-xs ${
                            n.is_read ? '' : isDark ? 'bg-white/[0.03]' : 'bg-blue-50'
                          }`}
                        >
                          <div className={`font-medium ${palette.title}`}>{n.title}</div>
                          {n.body && (
                            <div className={`mt-0.5 ${palette.muted}`}>{n.body}</div>
                          )}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </div>

            {/* Profile button */}
            <button
              type="button"
              onClick={() => setProfileOpen(true)}
              aria-label="Open profile"
              className="ml-1 inline-flex h-10 w-10 items-center justify-center rounded-full transition hover:opacity-90"
            >
              {profile?.avatar_url ? (
                <img src={profile.avatar_url} alt="" className="h-9 w-9 rounded-full object-cover" />
              ) : (
                <div
                  className="h-9 w-9 rounded-full flex items-center justify-center text-white font-semibold text-sm"
                  style={{ backgroundColor: memberColor }}
                >
                  {(memberName || '?').charAt(0).toUpperCase()}
                </div>
              )}
            </button>
          </div>
        </div>
      </nav>

      {/* Welcome banner */}
      <header className="relative mx-auto max-w-6xl px-4 sm:px-6 pt-2 pb-8">
        <div className="flex items-end justify-between gap-6">
          <div>
            <h1 className={`text-3xl sm:text-4xl font-semibold tracking-tight ${palette.title}`}>
              Welcome back to {workspaceName}
            </h1>
            <p className={`mt-2 text-sm ${palette.muted}`}>
              {me?.workspace_owner_name
                ? `You're collaborating in ${me.workspace_owner_name}${ownerEmailHint}'s workspace as ${memberName}.`
                : `You're collaborating as ${memberName}.`}
            </p>
          </div>
          <div className={`hidden sm:flex items-center gap-2 rounded-full px-3 py-1.5 text-xs ${
            isDark ? 'bg-white/[0.04] text-slate-300' : 'bg-slate-100 text-slate-700'
          }`}>
            <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: memberColor }} />
            {memberName}
            <span className={palette.subtle}>·</span>
            <span className={palette.subtle}>Team member</span>
          </div>
        </div>
      </header>

      {/* Buckets grid */}
      <main className="relative mx-auto max-w-6xl px-4 sm:px-6 pb-12">
        <div className="mb-3 flex items-center justify-between">
          <h2 className={`text-sm font-semibold uppercase tracking-[0.18em] ${palette.muted}`}>
            Your buckets
          </h2>
          <span className={`text-xs ${palette.subtle}`}>
            {buckets.length} bucket{buckets.length === 1 ? '' : 's'}
          </span>
        </div>

        {loading && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className={`h-32 rounded-2xl animate-pulse ${
                  isDark ? 'bg-white/[0.03]' : 'bg-slate-100'
                }`}
              />
            ))}
          </div>
        )}

        {!loading && buckets.length === 0 && (
          <div
            className={`rounded-2xl py-16 text-center ${
              isDark ? 'bg-white/[0.02]' : 'bg-white/70'
            }`}
          >
            <svg
              className={`mx-auto mb-3 ${palette.muted}`}
              width="36"
              height="36"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.4"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
            </svg>
            <p className={`text-sm font-medium ${palette.title}`}>No bucket access yet</p>
            <p className={`mt-1 text-xs ${palette.muted}`}>
              {me?.workspace_owner_name || 'The workspace owner'} hasn't shared any buckets with you. Reach out to them to get access.
            </p>
          </div>
        )}

        {!loading && buckets.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {buckets.map((b) => (
              <button
                key={b.id}
                onClick={() => navigate(`/bucket/${b.id}`, { state: { bucket: b } })}
                className={`group rounded-2xl p-5 text-left transition ${cardBg}`}
              >
                <div className="flex items-center gap-2.5 mb-3">
                  <span
                    className="h-3 w-3 rounded-full"
                    style={{ backgroundColor: b.color || '#3B82F6' }}
                  />
                  <h3 className={`text-base font-semibold truncate ${palette.title}`}>
                    {b.name}
                  </h3>
                </div>
                {b.description && (
                  <p className={`mb-4 text-xs line-clamp-2 ${palette.muted}`}>
                    {b.description}
                  </p>
                )}
                <div className="flex items-center justify-between">
                  <div className={`flex items-center gap-3 text-[11px] ${palette.subtle}`}>
                    <span>{b.file_count} file{b.file_count === 1 ? '' : 's'}</span>
                    <span>·</span>
                    <span>{(b.storage_gb || 0).toFixed(2)} GB</span>
                  </div>
                  <span
                    className={`text-[11px] font-medium opacity-0 transition group-hover:opacity-100 ${palette.accent}`}
                  >
                    Open →
                  </span>
                </div>
              </button>
            ))}
          </div>
        )}
      </main>

      <MemberProfileDrawer
        open={profileOpen}
        onClose={() => setProfileOpen(false)}
        me={me}
        profile={profile}
        onProfileUpdated={setProfile}
        onSignOut={handleSignOut}
        theme={theme}
        onToggleTheme={onToggleTheme}
      />
    </div>
  );
}
