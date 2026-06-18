import React, { useEffect, useState } from 'react';
import ColorPicker from './ColorPicker';
import { RadioCard, Switch } from './Switch';
import {
  DEFAULT_BUCKET_PERMISSIONS,
  HISTORY_SCOPE_OPTIONS,
  PERMISSION_LABELS,
  teamApi,
} from '../../api/team';
import { dashboardApi } from '../../api/auth';
import { TEAM_COLOR_PALETTE } from './colorPalette';
import { useAppTheme } from './theme';

const STEP_INFO = 1;
const STEP_BUCKETS = 2;
const STEP_PERMS = 3;

export default function InviteWizard({ onCancel, onSuccess }) {
  const { theme, palette } = useAppTheme();
  const [step, setStep] = useState(STEP_INFO);
  const [email, setEmail] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [color, setColor] = useState(TEAM_COLOR_PALETTE[0]);
  const [note, setNote] = useState('');
  const [buckets, setBuckets] = useState([]);
  const [bucketsLoading, setBucketsLoading] = useState(false);
  const [bucketSearch, setBucketSearch] = useState('');
  const [selected, setSelected] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    setBucketsLoading(true);
    dashboardApi
      .listBuckets()
      .then((list) => setBuckets(list || []))
      .catch((e) => setError(e.message))
      .finally(() => setBucketsLoading(false));
  }, []);

  function toggleBucket(bucketId) {
    setSelected((prev) => {
      const next = { ...prev };
      if (next[bucketId]) {
        delete next[bucketId];
      } else {
        next[bucketId] = { ...DEFAULT_BUCKET_PERMISSIONS };
      }
      return next;
    });
  }

  function setPermission(bucketId, perm, val) {
    setSelected((prev) => ({
      ...prev,
      [bucketId]: { ...(prev[bucketId] || DEFAULT_BUCKET_PERMISSIONS), [perm]: val },
    }));
  }

  function infoValid() {
    return /\S+@\S+\.\S+/.test(email.trim()) && displayName.trim().length > 0;
  }

  async function handleSubmit() {
    setSubmitting(true);
    setError(null);
    try {
      const payload = {
        email: email.trim(),
        display_name: displayName.trim(),
        display_color: color,
        note: note.trim() || null,
        buckets: Object.entries(selected).map(([bucket_id, permissions]) => ({
          bucket_id,
          permissions,
        })),
      };
      await teamApi.inviteMember(payload);
      onSuccess?.();
    } catch (e) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  }

  const filteredBuckets = buckets.filter((b) =>
    !bucketSearch.trim() || b.name.toLowerCase().includes(bucketSearch.toLowerCase()),
  );

  const labelCls = `mb-2 block text-xs font-semibold uppercase tracking-[0.18em] ${palette.muted}`;
  const inputCls = `w-full rounded-2xl border px-4 py-2.5 text-sm outline-none transition focus:ring-2 ${palette.input}`;
  const btnPrimary = `rounded-2xl px-5 py-2.5 text-sm font-semibold transition ${palette.primary} disabled:opacity-50 disabled:cursor-not-allowed`;
  const btnSecondary = `rounded-2xl border px-5 py-2.5 text-sm font-medium transition ${palette.secondary}`;

  return (
    <div className="space-y-6">
      {/* Progress bar */}
      <div className="flex items-center gap-2">
        {[1, 2, 3].map((n) => (
          <div
            key={n}
            className={`flex-1 h-1 rounded-full transition-colors ${
              step >= n
                ? 'bg-blue-500'
                : theme === 'dark'
                  ? 'bg-white/10'
                  : 'bg-slate-200'
            }`}
          />
        ))}
      </div>

      {error && (
        <div className={`text-sm rounded-2xl px-4 py-3 ${palette.error}`}>{error}</div>
      )}

      {step === STEP_INFO && (
        <div className="space-y-5">
          <div>
            <label className={labelCls}>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="teammate@example.com"
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Display name</label>
            <input
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="Their name (shown on chat bubbles)"
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Color</label>
            <ColorPicker value={color} onChange={setColor} />
          </div>
          <div>
            <label className={labelCls}>Note (optional)</label>
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              rows={3}
              placeholder="Personal message included in the invite email"
              className={inputCls}
            />
          </div>
          <div className="flex justify-between pt-2">
            <button onClick={onCancel} className={btnSecondary}>Cancel</button>
            <button
              onClick={() => setStep(STEP_BUCKETS)}
              disabled={!infoValid()}
              className={btnPrimary}
            >
              Next: Buckets
            </button>
          </div>
        </div>
      )}

      {step === STEP_BUCKETS && (
        <div className="space-y-5">
          <input
            type="text"
            value={bucketSearch}
            onChange={(e) => setBucketSearch(e.target.value)}
            placeholder="Search buckets..."
            className={inputCls}
          />
          <div className={`max-h-72 overflow-y-auto rounded-2xl border ${palette.card} p-2`}>
            {bucketsLoading && <div className={`text-sm p-3 ${palette.muted}`}>Loading buckets...</div>}
            {!bucketsLoading && filteredBuckets.length === 0 && (
              <div className={`text-sm p-3 ${palette.muted}`}>No buckets found.</div>
            )}
            {filteredBuckets.map((b) => (
              <label
                key={b.id}
                className={`flex items-center gap-3 p-3 rounded-xl cursor-pointer transition ${palette.rowHover}`}
              >
                <input
                  type="checkbox"
                  checked={!!selected[b.id]}
                  onChange={() => toggleBucket(b.id)}
                  className={`h-4 w-4 ${palette.checkbox}`}
                />
                <span
                  className="inline-block h-3 w-3 rounded-full"
                  style={{ backgroundColor: b.color }}
                />
                <span className={`text-sm ${palette.title}`}>{b.name}</span>
              </label>
            ))}
          </div>
          <div className="flex justify-between">
            <button onClick={() => setStep(STEP_INFO)} className={btnSecondary}>Back</button>
            <button
              onClick={() => setStep(STEP_PERMS)}
              disabled={Object.keys(selected).length === 0}
              className={btnPrimary}
            >
              Next: Permissions
            </button>
          </div>
        </div>
      )}

      {step === STEP_PERMS && (
        <div className="space-y-5">
          <p className={`text-xs ${palette.muted}`}>
            Bucket access lets the member view + chat. Set history visibility and tick what extra actions they can take.
          </p>
          <div className="max-h-[24rem] overflow-y-auto space-y-3 pr-1">
            {Object.keys(selected).map((bid) => {
              const bucket = buckets.find((b) => b.id === bid);
              const perms = selected[bid] || DEFAULT_BUCKET_PERMISSIONS;
              return (
                <div key={bid} className={`rounded-2xl border p-5 ${palette.card}`}>
                  <div className="flex items-center gap-2 mb-4">
                    <span className="inline-block h-3 w-3 rounded-full" style={{ backgroundColor: bucket?.color }} />
                    <h4 className={`text-sm font-semibold ${palette.title}`}>{bucket?.name || bid}</h4>
                  </div>

                  <div className="mb-5">
                    <div className={`mb-2 text-[10px] font-semibold uppercase tracking-[0.18em] ${palette.muted}`}>
                      Chat history visibility
                    </div>
                    <div className="space-y-2">
                      {HISTORY_SCOPE_OPTIONS.map((opt) => (
                        <RadioCard
                          key={opt.value}
                          checked={perms.history_scope === opt.value}
                          onChange={() => setPermission(bid, 'history_scope', opt.value)}
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
                        checked={!!perms[perm]}
                        onChange={(v) => setPermission(bid, perm, v)}
                        label={label}
                      />
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
          <div className="flex justify-between">
            <button onClick={() => setStep(STEP_BUCKETS)} className={btnSecondary}>Back</button>
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className={btnPrimary}
            >
              {submitting ? 'Sending...' : 'Send invite'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
