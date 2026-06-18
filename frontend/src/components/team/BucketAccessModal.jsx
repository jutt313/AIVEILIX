import React, { useCallback, useEffect, useState } from 'react';
import Modal from './Modal';
import { RadioCard, Switch } from './Switch';
import {
  DEFAULT_BUCKET_PERMISSIONS,
  HISTORY_SCOPE_OPTIONS,
  PERMISSION_LABELS,
  teamApi,
} from '../../api/team';
import { useAppTheme } from './theme';

export default function BucketAccessModal({ open, bucketId, bucketName, onClose }) {
  const { palette } = useAppTheme();
  const [members, setMembers] = useState([]);
  const [allMembers, setAllMembers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [editing, setEditing] = useState(null);
  const [editPerms, setEditPerms] = useState(DEFAULT_BUCKET_PERMISSIONS);
  const [addingMemberId, setAddingMemberId] = useState('');

  const refresh = useCallback(async () => {
    if (!bucketId) return;
    setLoading(true);
    setError(null);
    try {
      const [access, allTeam] = await Promise.all([
        teamApi.listBucketAccess(bucketId),
        teamApi.listMembers(),
      ]);
      setMembers(access.members || []);
      setAllMembers(allTeam.members || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [bucketId]);

  useEffect(() => {
    if (open) {
      setEditing(null);
      setAddingMemberId('');
      refresh();
    }
  }, [open, refresh]);

  function startEdit(memberInfo) {
    setEditing(memberInfo.team_member_id);
    setEditPerms({ ...DEFAULT_BUCKET_PERMISSIONS, ...memberInfo.permissions });
  }

  async function saveEdit() {
    try {
      await teamApi.updateBucketAccess(bucketId, editing, editPerms);
      setEditing(null);
      await refresh();
    } catch (e) {
      alert(e.message);
    }
  }

  async function handleRevoke(memberId) {
    if (!confirm("Revoke this member's access to this bucket? Their old messages stay.")) return;
    try {
      await teamApi.revokeBucketAccess(bucketId, memberId);
      await refresh();
    } catch (e) {
      alert(e.message);
    }
  }

  async function handleAdd() {
    if (!addingMemberId) return;
    try {
      await teamApi.grantBucketAccess(bucketId, {
        team_member_id: addingMemberId,
        permissions: DEFAULT_BUCKET_PERMISSIONS,
      });
      setAddingMemberId('');
      await refresh();
    } catch (e) {
      alert(e.message);
    }
  }

  const grantedIds = new Set(members.map((m) => m.team_member_id));
  const availableToAdd = allMembers.filter((m) => !grantedIds.has(m.id));

  const inputCls = `w-full rounded-2xl border px-4 py-2.5 text-sm outline-none transition focus:ring-2 ${palette.input}`;
  const btnPrimary = `rounded-2xl px-5 py-2.5 text-sm font-semibold transition ${palette.primary} disabled:opacity-50`;
  const btnSecondary = `rounded-xl border px-3 py-1.5 text-xs font-medium transition ${palette.secondary}`;
  const btnDanger = `rounded-xl px-3 py-1.5 text-xs font-medium transition ${palette.danger}`;

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Bucket access"
      subtitle={bucketName || bucketId}
      maxWidth="2xl"
    >
      <div className="space-y-5">
        {error && (
          <div className={`text-sm rounded-2xl px-4 py-3 ${palette.error}`}>{error}</div>
        )}

        {availableToAdd.length > 0 && (
          <div className={`flex items-end gap-3 rounded-2xl border p-4 ${palette.card}`}>
            <div className="flex-1">
              <label className={`mb-1.5 block text-xs font-semibold uppercase tracking-[0.18em] ${palette.muted}`}>
                Add team member
              </label>
              <select
                value={addingMemberId}
                onChange={(e) => setAddingMemberId(e.target.value)}
                className={inputCls}
              >
                <option value="">— Pick member —</option>
                {availableToAdd.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.display_name} ({m.invite_email})
                  </option>
                ))}
              </select>
            </div>
            <button onClick={handleAdd} disabled={!addingMemberId} className={btnPrimary}>
              Grant access
            </button>
          </div>
        )}

        {loading && <div className={`text-sm ${palette.muted}`}>Loading...</div>}

        {!loading && members.length === 0 && (
          <div className={`text-center py-12 rounded-2xl border ${palette.card}`}>
            <p className={`text-sm ${palette.muted}`}>No members have access to this bucket yet.</p>
          </div>
        )}

        <div className="space-y-3">
          {members.map((m) => (
            <div key={m.team_member_id} className={`rounded-2xl border p-5 ${palette.card}`}>
              <div className="flex items-center gap-3 mb-4">
                <div
                  className="h-10 w-10 rounded-full flex items-center justify-center text-white font-semibold text-sm shadow-sm"
                  style={{ backgroundColor: m.display_color || '#64748b' }}
                >
                  {(m.display_name || m.invite_email || '?').charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <div className={`text-sm font-semibold ${palette.title}`}>{m.display_name}</div>
                  <div className={`text-xs truncate ${palette.muted}`}>{m.invite_email}</div>
                </div>
                <div className="flex gap-1.5">
                  {editing !== m.team_member_id ? (
                    <>
                      <button onClick={() => startEdit(m)} className={btnSecondary}>Edit</button>
                      <button onClick={() => handleRevoke(m.team_member_id)} className={btnDanger}>Revoke</button>
                    </>
                  ) : (
                    <>
                      <button onClick={saveEdit} className={`rounded-xl px-3 py-1.5 text-xs font-semibold ${palette.primary}`}>Save</button>
                      <button onClick={() => setEditing(null)} className={btnSecondary}>Cancel</button>
                    </>
                  )}
                </div>
              </div>
              <div className="mb-5">
                <div className={`mb-2 text-[10px] font-semibold uppercase tracking-[0.18em] ${palette.muted}`}>
                  Chat history visibility
                </div>
                <div className="space-y-2">
                  {HISTORY_SCOPE_OPTIONS.map((opt) => (
                    <RadioCard
                      key={opt.value}
                      disabled={editing !== m.team_member_id}
                      checked={
                        editing === m.team_member_id
                          ? editPerms.history_scope === opt.value
                          : m.permissions.history_scope === opt.value
                      }
                      onChange={() => setEditPerms((p) => ({ ...p, history_scope: opt.value }))}
                      label={opt.label}
                      hint={opt.description}
                    />
                  ))}
                </div>
              </div>

              <div className={`mb-2 text-[10px] font-semibold uppercase tracking-[0.18em] ${palette.muted}`}>
                Extra actions
              </div>
              <div className="space-y-2">
                {Object.entries(PERMISSION_LABELS).map(([perm, label]) => (
                  <Switch
                    key={perm}
                    disabled={editing !== m.team_member_id}
                    checked={
                      editing === m.team_member_id
                        ? !!editPerms[perm]
                        : !!m.permissions[perm]
                    }
                    onChange={(v) => setEditPerms((p) => ({ ...p, [perm]: v }))}
                    label={label}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </Modal>
  );
}
