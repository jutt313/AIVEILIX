import React, { useCallback, useEffect, useState } from 'react';
import ColorPicker from './ColorPicker';
import { RadioCard, Switch } from './Switch';
import {
  DEFAULT_BUCKET_PERMISSIONS,
  HISTORY_SCOPE_OPTIONS,
  PERMISSION_LABELS,
  teamApi,
} from '../../api/team';
import { dashboardApi } from '../../api/auth';
import { useAppTheme } from './theme';

function fmtWhen(value) {
  if (!value) return null;
  const d = new Date(value);
  const mins = Math.floor((Date.now() - d.getTime()) / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins} min ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs} hr${hrs === 1 ? '' : 's'} ago`;
  const days = Math.floor(hrs / 24);
  if (days < 7) return `${days} day${days === 1 ? '' : 's'} ago`;
  return d.toLocaleDateString();
}

export default function EditMemberForm({
  memberId,
  onBack,
  onChanged,
  onRemoved,
  hideBackButton = false,
}) {
  const { theme, palette } = useAppTheme();
  const isDark = theme === 'dark';

  const [member, setMember] = useState(null);
  const [allBuckets, setAllBuckets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [displayName, setDisplayName] = useState('');
  const [color, setColor] = useState('#3B82F6');
  const [savingProfile, setSavingProfile] = useState(false);

  const [editPerms, setEditPerms] = useState({}); // bucket_id -> perms
  const [savingBucket, setSavingBucket] = useState({});
  const [expanded, setExpanded] = useState({}); // bucket_id -> bool
  const [addingBucketId, setAddingBucketId] = useState('');

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [m, list] = await Promise.all([
        teamApi.getMember(memberId),
        dashboardApi.listBuckets(),
      ]);
      setMember(m);
      setAllBuckets(list || []);
      setDisplayName(m.display_name || '');
      setColor(m.display_color || '#3B82F6');
      const next = {};
      for (const b of (m.buckets || [])) {
        next[b.bucket_id] = { ...DEFAULT_BUCKET_PERMISSIONS, ...b.permissions };
      }
      setEditPerms(next);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [memberId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function handleSaveProfile() {
    setSavingProfile(true);
    setError(null);
    try {
      await teamApi.updateMember(memberId, {
        display_name: displayName.trim() || null,
        display_color: color,
      });
      onChanged?.();
      await refresh();
    } catch (e) {
      setError(e.message);
    } finally {
      setSavingProfile(false);
    }
  }

  async function handleSaveBucket(bucketId) {
    setSavingBucket((s) => ({ ...s, [bucketId]: true }));
    setError(null);
    try {
      await teamApi.updateBucketAccess(bucketId, memberId, editPerms[bucketId]);
      onChanged?.();
      await refresh();
    } catch (e) {
      setError(e.message);
    } finally {
      setSavingBucket((s) => ({ ...s, [bucketId]: false }));
    }
  }

  async function handleRevokeBucket(bucketId) {
    if (!confirm("Revoke this member's access to this bucket? Their old messages stay.")) return;
    try {
      await teamApi.revokeBucketAccess(bucketId, memberId);
      onChanged?.();
      await refresh();
    } catch (e) {
      alert(e.message);
    }
  }

  async function handleAddBucket() {
    if (!addingBucketId) return;
    try {
      await teamApi.grantBucketAccess(addingBucketId, {
        team_member_id: memberId,
        permissions: DEFAULT_BUCKET_PERMISSIONS,
      });
      const newId = addingBucketId;
      setAddingBucketId('');
      setExpanded((s) => ({ ...s, [newId]: true }));
      onChanged?.();
      await refresh();
    } catch (e) {
      alert(e.message);
    }
  }

  async function handleResend() {
    try {
      await teamApi.resendInvite(memberId);
      alert('Invite resent.');
    } catch (e) {
      alert(e.message);
    }
  }

  async function handleRemove() {
    if (!confirm('Remove this team member? Their old messages stay; they lose all bucket access.')) return;
    try {
      await teamApi.deleteMember(memberId);
      onRemoved?.();
    } catch (e) {
      alert(e.message);
    }
  }

  function setPermission(bucketId, perm, value) {
    setEditPerms((prev) => ({
      ...prev,
      [bucketId]: { ...(prev[bucketId] || DEFAULT_BUCKET_PERMISSIONS), [perm]: value },
    }));
  }

  function toggleExpanded(bucketId) {
    setExpanded((s) => ({ ...s, [bucketId]: !s[bucketId] }));
  }

  function permsSummary(perms) {
    if (!perms) return '';
    const enabled = Object.keys(PERMISSION_LABELS).filter((k) => perms[k]);
    const scopeLabel = perms.history_scope === 'all' ? 'all history' : 'from now';
    const count = enabled.length;
    return `${scopeLabel} · ${count} permission${count === 1 ? '' : 's'}`;
  }

  const inputCls = `w-full rounded-2xl px-4 py-2.5 text-sm outline-none transition focus:ring-2 ${
    isDark
      ? 'bg-white/[0.04] text-slate-100 placeholder:text-slate-500 focus:ring-blue-400/30'
      : 'bg-white text-slate-900 placeholder:text-slate-400 focus:ring-blue-500/20'
  }`;
  const labelCls = `mb-2 block text-xs font-semibold uppercase tracking-[0.18em] ${palette.muted}`;
  const btnPrimary = `rounded-2xl px-5 py-2.5 text-sm font-semibold transition ${palette.primary} disabled:opacity-50`;
  const btnSmallPrimary = `rounded-xl px-3 py-1.5 text-xs font-semibold transition ${palette.primary} disabled:opacity-50`;
  const btnSmallSubtle = `rounded-xl px-3 py-1.5 text-xs font-medium transition ${
    isDark ? 'text-slate-300 hover:bg-white/[0.05]' : 'text-slate-600 hover:bg-slate-100'
  }`;
  const btnSmallDanger = `rounded-xl px-3 py-1.5 text-xs font-medium transition ${palette.danger}`;
  const cardBg = isDark ? 'bg-white/[0.025]' : 'bg-white/80';

  if (loading) {
    return <div className={`text-sm ${palette.muted}`}>Loading member...</div>;
  }
  if (!member) {
    return (
      <div className="space-y-4">
        <div className={`text-sm rounded-2xl px-4 py-3 ${palette.error}`}>
          Could not load this member.
        </div>
        {!hideBackButton && <button onClick={onBack} className={btnSmallSubtle}>Back</button>}
      </div>
    );
  }

  const grantedIds = new Set((member.buckets || []).map((b) => b.bucket_id));
  const availableToAdd = allBuckets.filter((b) => !grantedIds.has(b.id));

  return (
    <div className="space-y-5">
      {error && (
        <div className={`text-sm rounded-2xl px-4 py-3 ${palette.error}`}>{error}</div>
      )}

      {/* Profile hero */}
      <section className={`rounded-2xl p-5 ${cardBg}`}>
        <div className="flex items-start gap-4 mb-4">
          {member.avatar_url ? (
            <img
              src={member.avatar_url}
              alt=""
              className="h-16 w-16 shrink-0 rounded-full object-cover ring-2"
              style={{ outlineColor: color, boxShadow: `0 0 0 2px ${color}` }}
            />
          ) : (
            <div
              className="h-16 w-16 shrink-0 rounded-full flex items-center justify-center text-white font-bold text-xl shadow-sm"
              style={{ backgroundColor: color }}
            >
              {(displayName || member.invite_email || '?').charAt(0).toUpperCase()}
            </div>
          )}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <div className={`text-lg font-semibold truncate ${palette.title}`}>
                {displayName || '(unnamed)'}
              </div>
              {member.status === 'accepted' && (
                <span className={`inline-flex shrink-0 items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium ${
                  member.is_online
                    ? 'bg-emerald-500/15 text-emerald-500'
                    : (isDark ? 'bg-white/[0.06] text-slate-400' : 'bg-slate-100 text-slate-500')
                }`}>
                  <span className={`h-1.5 w-1.5 rounded-full ${member.is_online ? 'bg-emerald-400' : 'bg-slate-400'}`} />
                  {member.is_online ? 'Online' : 'Offline'}
                </span>
              )}
            </div>
            <div className={`text-xs truncate ${palette.muted}`}>{member.invite_email}</div>
            <div className={`mt-1 space-y-0.5 text-[11px] ${palette.subtle}`}>
              <div>Status: <span className="font-medium">{member.status}</span></div>
              {member.status === 'accepted' && (
                <>
                  <div>
                    {member.is_online
                      ? 'Active now'
                      : member.last_active_at
                        ? `Last active ${fmtWhen(member.last_active_at)}`
                        : 'No activity yet'}
                  </div>
                  <div>
                    {member.last_login_at
                      ? `Last login ${fmtWhen(member.last_login_at)}`
                      : 'Never signed in'}
                  </div>
                </>
              )}
            </div>
          </div>
          <div className="flex flex-col gap-1.5 shrink-0">
            {member.status === 'pending' && (
              <button onClick={handleResend} className={btnSmallSubtle}>Resend invite</button>
            )}
            <button onClick={handleRemove} className={btnSmallDanger}>Remove</button>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Display name</label>
            <input
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Color</label>
            <ColorPicker value={color} onChange={setColor} />
          </div>
        </div>

        <div className="mt-4 flex justify-end">
          <button onClick={handleSaveProfile} disabled={savingProfile} className={btnPrimary}>
            {savingProfile ? 'Saving...' : 'Save profile'}
          </button>
        </div>
      </section>

      {/* Bucket access */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <div className={`text-[10px] font-semibold uppercase tracking-[0.18em] ${palette.muted}`}>
            Bucket access
          </div>
          {availableToAdd.length > 0 && (
            <div className="flex items-center gap-2">
              <select
                value={addingBucketId}
                onChange={(e) => setAddingBucketId(e.target.value)}
                className={`rounded-xl px-3 py-1.5 text-xs ${inputCls}`}
              >
                <option value="">+ Add bucket</option>
                {availableToAdd.map((b) => (
                  <option key={b.id} value={b.id}>{b.name}</option>
                ))}
              </select>
              <button
                onClick={handleAddBucket}
                disabled={!addingBucketId}
                className={btnSmallPrimary}
              >
                Add
              </button>
            </div>
          )}
        </div>

        {(member.buckets || []).length === 0 && (
          <div className={`text-center py-10 rounded-2xl ${cardBg}`}>
            <p className={`text-sm ${palette.muted}`}>This member has no bucket access yet.</p>
          </div>
        )}

        {(member.buckets || []).map((bAccess) => {
          const bucketMeta = allBuckets.find((b) => b.id === bAccess.bucket_id);
          const perms = editPerms[bAccess.bucket_id] || DEFAULT_BUCKET_PERMISSIONS;
          const isOpen = !!expanded[bAccess.bucket_id];
          return (
            <div key={bAccess.bucket_id} className={`rounded-2xl overflow-hidden ${cardBg}`}>
              <button
                onClick={() => toggleExpanded(bAccess.bucket_id)}
                className={`w-full flex items-center gap-3 px-5 py-3.5 text-left transition ${
                  isDark ? 'hover:bg-white/[0.02]' : 'hover:bg-slate-50'
                }`}
              >
                <span
                  className="inline-block h-3 w-3 rounded-full shrink-0"
                  style={{ backgroundColor: bucketMeta?.color }}
                />
                <div className="flex-1 min-w-0">
                  <div className={`text-sm font-semibold truncate ${palette.title}`}>
                    {bucketMeta?.name || bAccess.bucket_id}
                  </div>
                  <div className={`text-[11px] ${palette.subtle} truncate`}>
                    {permsSummary(perms)}
                  </div>
                </div>
                <svg
                  className={`shrink-0 transition-transform ${isOpen ? 'rotate-180' : ''} ${palette.muted}`}
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <polyline points="6 9 12 15 18 9" />
                </svg>
              </button>

              {isOpen && (
                <div className="px-5 pb-5 space-y-4">
                  <div>
                    <div className={`mb-2 text-[10px] font-semibold uppercase tracking-[0.18em] ${palette.muted}`}>
                      Chat history visibility
                    </div>
                    <div className="space-y-2">
                      {HISTORY_SCOPE_OPTIONS.map((opt) => (
                        <RadioCard
                          key={opt.value}
                          checked={perms.history_scope === opt.value}
                          onChange={() => setPermission(bAccess.bucket_id, 'history_scope', opt.value)}
                          label={opt.label}
                          hint={opt.description}
                        />
                      ))}
                    </div>
                  </div>

                  <div>
                    <div className={`mb-2 text-[10px] font-semibold uppercase tracking-[0.18em] ${palette.muted}`}>
                      Extra actions
                    </div>
                    <div className="space-y-2">
                      {Object.entries(PERMISSION_LABELS).map(([perm, label]) => (
                        <Switch
                          key={perm}
                          checked={!!perms[perm]}
                          onChange={(v) => setPermission(bAccess.bucket_id, perm, v)}
                          label={label}
                        />
                      ))}
                    </div>
                  </div>

                  <div className="flex justify-end gap-2 pt-1">
                    <button
                      onClick={() => handleRevokeBucket(bAccess.bucket_id)}
                      className={btnSmallDanger}
                    >
                      Revoke
                    </button>
                    <button
                      onClick={() => handleSaveBucket(bAccess.bucket_id)}
                      disabled={savingBucket[bAccess.bucket_id]}
                      className={btnSmallPrimary}
                    >
                      {savingBucket[bAccess.bucket_id] ? 'Saving...' : 'Save changes'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </section>

      {!hideBackButton && (
        <div className="flex justify-start pt-2">
          <button onClick={onBack} className={btnSmallSubtle}>Back to list</button>
        </div>
      )}
    </div>
  );
}
