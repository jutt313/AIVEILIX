import React, { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { dashboardApi } from '../../api/auth';
import { useAppTheme } from './theme';

/**
 * Slim profile drawer for team members.
 *
 * Lets them edit: avatar + display name + password + theme.
 * Email is read-only. Color is read-only (owner controls it).
 * No connected accounts, no billing, no MCP, no danger zone.
 */
export default function MemberProfileDrawer({
  open,
  onClose,
  me,
  profile,
  onProfileUpdated,
  onSignOut,
  theme,
  onToggleTheme,
}) {
  const { palette } = useAppTheme();
  const isDark = theme === 'dark';

  const avatarInputRef = useRef(null);
  const [savingName, setSavingName] = useState(false);
  const [savingAvatar, setSavingAvatar] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [name, setName] = useState('');
  const [currentPw, setCurrentPw] = useState('');
  const [newPw, setNewPw] = useState('');
  const [confirmPw, setConfirmPw] = useState('');

  useEffect(() => {
    if (open) {
      setName(profile?.full_name || '');
      setFeedback(null);
      setErrorMsg(null);
      setCurrentPw('');
      setNewPw('');
      setConfirmPw('');
    }
  }, [open, profile]);

  useEffect(() => {
    if (!open) return;
    function onKey(e) {
      if (e.key === 'Escape') onClose?.();
    }
    document.addEventListener('keydown', onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = prev;
    };
  }, [open, onClose]);

  async function handleSaveName() {
    setSavingName(true);
    setFeedback(null);
    setErrorMsg(null);
    try {
      const updated = await dashboardApi.updateProfile({
        full_name: name.trim() || 'Member',
        bio: profile?.bio || null,
        theme: profile?.theme || theme,
        language: profile?.language || 'en',
        timezone: profile?.timezone || 'UTC',
      });
      onProfileUpdated?.({ ...profile, full_name: updated?.full_name || name });
      setFeedback('Profile updated.');
    } catch (e) {
      setErrorMsg(e.message);
    } finally {
      setSavingName(false);
    }
  }

  async function handleAvatarPick(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setSavingAvatar(true);
    setErrorMsg(null);
    try {
      const result = await dashboardApi.uploadAvatar(file);
      onProfileUpdated?.({ ...profile, avatar_url: result?.avatar_url });
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setSavingAvatar(false);
      e.target.value = '';
    }
  }

  async function handleChangePassword() {
    if (newPw.length < 8) {
      setErrorMsg('New password must be at least 8 characters.');
      return;
    }
    if (newPw !== confirmPw) {
      setErrorMsg('Passwords do not match.');
      return;
    }
    setSavingPassword(true);
    setErrorMsg(null);
    setFeedback(null);
    try {
      await dashboardApi.changePassword(currentPw, newPw);
      setFeedback('Password changed.');
      setCurrentPw('');
      setNewPw('');
      setConfirmPw('');
    } catch (e) {
      setErrorMsg(e.message);
    } finally {
      setSavingPassword(false);
    }
  }

  if (!open) return null;
  if (typeof document === 'undefined') return null;

  const memberName = me?.display_name || name || 'Member';
  const memberColor = me?.display_color || '#3B82F6';
  const initial = memberName.charAt(0).toUpperCase();

  const overlayCls = isDark ? 'bg-slate-950/80' : 'bg-white/55';
  const panelCls = isDark
    ? 'border-white/10 bg-[#0b1220] text-white shadow-[0_30px_100px_rgba(2,6,23,0.62)]'
    : 'border-slate-300 bg-[#f8fafc] text-slate-900 shadow-[0_24px_80px_rgba(148,163,184,0.22)]';
  const inputCls = `w-full rounded-2xl px-4 py-2.5 text-sm outline-none transition focus:ring-2 ${
    isDark
      ? 'bg-white/[0.04] text-white placeholder:text-slate-500 focus:ring-blue-400/30'
      : 'bg-white text-slate-900 placeholder:text-slate-400 focus:ring-blue-500/20'
  }`;
  const labelCls = `mb-2 block text-[10px] font-semibold uppercase tracking-[0.18em] ${palette.muted}`;
  const cardBg = isDark ? 'bg-white/[0.03]' : 'bg-white/80';
  const btnPrimary = `rounded-2xl px-5 py-2.5 text-sm font-semibold transition ${palette.primary} disabled:opacity-50`;
  const btnSubtle = `rounded-2xl px-5 py-2.5 text-sm font-medium transition ${
    isDark ? 'text-slate-300 hover:bg-white/[0.05]' : 'text-slate-700 hover:bg-slate-100'
  }`;

  return createPortal(
    <div
      className={`fixed inset-0 z-[100] flex items-center justify-center px-4 py-6 backdrop-blur-sm ${overlayCls}`}
      onClick={onClose}
      role="dialog"
      aria-modal="true"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className={`w-full max-w-[40rem] max-h-[88vh] flex flex-col overflow-hidden rounded-[1.6rem] border ${panelCls}`}
      >
        <input
          ref={avatarInputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={handleAvatarPick}
        />

        <header className="px-7 pt-6 pb-4 flex items-start justify-between gap-4">
          <div>
            <h2 className={`text-lg font-semibold tracking-tight ${palette.title}`}>Your profile</h2>
            <p className={`mt-0.5 text-xs ${palette.muted}`}>
              Update your name, password, or avatar.
            </p>
          </div>
          <button
            onClick={onClose}
            className={`rounded-full p-1.5 transition ${
              isDark ? 'text-slate-400 hover:bg-white/[0.05] hover:text-white' : 'text-slate-500 hover:bg-slate-100'
            }`}
            aria-label="Close"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </header>

        <div className="flex-1 overflow-y-auto px-7 pb-7 space-y-5">
          {feedback && (
            <div className={`text-sm rounded-2xl px-4 py-3 ${
              isDark ? 'bg-emerald-500/10 text-emerald-300' : 'bg-emerald-50 text-emerald-700'
            }`}>
              {feedback}
            </div>
          )}
          {errorMsg && (
            <div className={`text-sm rounded-2xl px-4 py-3 ${palette.error}`}>
              {errorMsg}
            </div>
          )}

          {/* Avatar + name + email + color */}
          <section className={`rounded-2xl p-5 ${cardBg}`}>
            <div className="flex items-center gap-4 mb-5">
              <div className="relative">
                {profile?.avatar_url ? (
                  <img src={profile.avatar_url} alt="" className="h-16 w-16 rounded-full object-cover" />
                ) : (
                  <div
                    className="h-16 w-16 rounded-full flex items-center justify-center text-white font-bold text-xl"
                    style={{ backgroundColor: memberColor }}
                  >
                    {initial}
                  </div>
                )}
                <button
                  type="button"
                  disabled={savingAvatar}
                  onClick={() => avatarInputRef.current?.click()}
                  className={`absolute -bottom-1 -right-1 inline-flex h-7 w-7 items-center justify-center rounded-full shadow ${
                    isDark ? 'bg-blue-500 text-white' : 'bg-blue-600 text-white'
                  } disabled:opacity-50`}
                  aria-label="Change avatar"
                >
                  {savingAvatar ? (
                    <svg className="animate-spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 12a9 9 0 1 1-6.219-8.56" strokeLinecap="round" />
                    </svg>
                  ) : (
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
                      <circle cx="12" cy="13" r="4" />
                    </svg>
                  )}
                </button>
              </div>
              <div className="flex-1 min-w-0">
                <div className={`text-base font-semibold truncate ${palette.title}`}>
                  {memberName}
                </div>
                <div className={`text-xs truncate ${palette.muted}`}>{me?.email}</div>
                <div className={`mt-1 inline-flex items-center gap-1.5 text-[10px] font-medium uppercase tracking-[0.18em] ${palette.subtle}`}>
                  <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: memberColor }} />
                  Color set by your workspace owner
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className={labelCls}>Display name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Your name"
                  className={inputCls}
                />
              </div>
              <div>
                <label className={labelCls}>Email (read-only)</label>
                <input
                  type="email"
                  value={me?.email || ''}
                  readOnly
                  className={`${inputCls} opacity-60 cursor-not-allowed`}
                />
              </div>
            </div>

            <div className="mt-4 flex justify-end">
              <button onClick={handleSaveName} disabled={savingName} className={btnPrimary}>
                {savingName ? 'Saving...' : 'Save profile'}
              </button>
            </div>
          </section>

          {/* Change password */}
          <section className={`rounded-2xl p-5 ${cardBg}`}>
            <div className="mb-4">
              <h3 className={`text-sm font-semibold ${palette.title}`}>Change password</h3>
              <p className={`mt-0.5 text-xs ${palette.muted}`}>
                You'll be signed out of other sessions after changing.
              </p>
            </div>
            <div className="space-y-3">
              <div>
                <label className={labelCls}>Current password</label>
                <input
                  type="password"
                  value={currentPw}
                  onChange={(e) => setCurrentPw(e.target.value)}
                  className={inputCls}
                />
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className={labelCls}>New password</label>
                  <input
                    type="password"
                    value={newPw}
                    onChange={(e) => setNewPw(e.target.value)}
                    className={inputCls}
                  />
                </div>
                <div>
                  <label className={labelCls}>Confirm new password</label>
                  <input
                    type="password"
                    value={confirmPw}
                    onChange={(e) => setConfirmPw(e.target.value)}
                    className={inputCls}
                  />
                </div>
              </div>
            </div>
            <div className="mt-4 flex justify-end">
              <button
                onClick={handleChangePassword}
                disabled={savingPassword || !currentPw || !newPw || !confirmPw}
                className={btnPrimary}
              >
                {savingPassword ? 'Updating...' : 'Update password'}
              </button>
            </div>
          </section>

          {/* Theme */}
          <section className={`rounded-2xl p-5 ${cardBg}`}>
            <div className="flex items-center justify-between">
              <div>
                <h3 className={`text-sm font-semibold ${palette.title}`}>Appearance</h3>
                <p className={`mt-0.5 text-xs ${palette.muted}`}>Light or dark theme.</p>
              </div>
              <button
                onClick={onToggleTheme}
                className={`rounded-2xl px-4 py-2 text-xs font-semibold transition ${
                  isDark ? 'bg-white/[0.06] text-white hover:bg-white/[0.10]' : 'bg-slate-100 text-slate-900 hover:bg-slate-200'
                }`}
              >
                {isDark ? '🌙 Dark mode' : '☀️ Light mode'} → switch
              </button>
            </div>
          </section>

          {/* Sign out */}
          <section className="flex justify-end gap-2">
            <button onClick={onClose} className={btnSubtle}>Close</button>
            <button
              onClick={onSignOut}
              className={`rounded-2xl px-5 py-2.5 text-sm font-semibold transition ${
                isDark ? 'bg-red-500/15 text-red-300 hover:bg-red-500/25' : 'bg-red-50 text-red-700 hover:bg-red-100'
              }`}
            >
              Sign out
            </button>
          </section>
        </div>
      </div>
    </div>,
    document.body,
  );
}
