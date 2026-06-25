// Admin UI for the Demo Bucket layer — mounted inside the existing AdminPage
// panel. Create per-company demo buckets, load prebuild docs, watch activity,
// and work the "let's talk" meeting queue. Uses the verified admin session.
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { adminApi } from '../api/auth';

const CAP_FIELDS = [
  { key: 'cap_team_members', label: 'Team members', min: 0, max: 1000 },
  { key: 'cap_threads', label: 'Chats', min: 0, max: 10000 },
  { key: 'cap_messages', label: 'Messages', min: 0, max: 100000 },
  { key: 'cap_files', label: 'Visitor files', min: 0, max: 1000 },
  { key: 'cap_file_size_mb', label: 'File size (MB)', min: 1, max: 1024 },
  { key: 'cap_file_pages', label: 'Pages / file', min: 1, max: 10000 },
  { key: 'cap_file_visuals', label: 'Visuals / file', min: 0, max: 10000 },
  { key: 'cap_comebacks', label: 'Visits / lead', min: 1, max: 1000 },
];
const DEFAULT_CAPS = {
  cap_team_members: 3,
  cap_threads: 10,
  cap_messages: 100,
  cap_files: 1,
  cap_file_size_mb: 50,
  cap_file_pages: 100,
  cap_file_visuals: 100,
  cap_comebacks: 3,
};

function slugify(s) {
  return (s || '').toLowerCase().trim().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 60);
}

function parseCapValue(value, min, max) {
  const parsed = parseInt(value, 10);
  if (!Number.isFinite(parsed)) return min;
  return Math.min(max, Math.max(min, parsed));
}

const STATE_PILL = {
  ready: ['bg-emerald-500/10 text-emerald-400', 'Ready'],
  processing: ['bg-amber-500/10 text-amber-400', 'Processing'],
  partial: ['bg-amber-500/10 text-amber-400', 'Partial'],
  empty: ['bg-slate-500/10 text-slate-400', 'No docs'],
  failed: ['bg-rose-500/10 text-rose-400', 'Failed'],
};

export default function DemoAdminPanel({ session, dark }) {
  const card = dark ? 'bg-[#0F172A] ring-1 ring-white/10' : 'bg-white ring-1 ring-slate-200';
  const sub = dark ? 'border-white/10 bg-slate-900/60' : 'border-slate-200 bg-slate-50';
  const label = dark ? 'text-slate-400' : 'text-slate-500';
  const ghost = dark ? 'text-slate-300 hover:bg-white/5' : 'text-slate-600 hover:bg-slate-100';
  const input = `w-full rounded-lg px-3 py-2 text-sm outline-none ${dark ? 'bg-slate-800 text-slate-100 ring-1 ring-white/10 focus:ring-2 focus:ring-blue-500' : 'bg-slate-50 text-slate-900 ring-1 ring-slate-200 focus:ring-2 focus:ring-blue-500'}`;

  const [buckets, setBuckets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [okMsg, setOkMsg] = useState('');
  const [createOpen, setCreateOpen] = useState(false);
  const [expanded, setExpanded] = useState(null); // link id
  const [meetings, setMeetings] = useState([]);
  const [meetingStatus, setMeetingStatus] = useState('pending');

  const load = async () => {
    if (!session) return;
    setLoading(true); setError('');
    try {
      const data = await adminApi.listDemoBuckets(session);
      setBuckets(data.items || []);
    } catch (e) { setError(e.message || 'Could not load demo buckets.'); }
    finally { setLoading(false); }
  };

  const loadMeetings = async (status = meetingStatus) => {
    if (!session) return;
    try {
      const data = await adminApi.listDemoMeetings(session, status);
      setMeetings(data.items || []);
    } catch (e) { setError(e.message || 'Could not load call requests.'); }
  };

  useEffect(() => { load(); /* eslint-disable-next-line */ }, [session]);
  useEffect(() => { loadMeetings(meetingStatus); /* eslint-disable-next-line */ }, [session, meetingStatus]);

  const flash = (msg) => { setOkMsg(msg); setTimeout(() => setOkMsg(''), 2500); };

  return (
    <>
      {/* ── Demo Buckets ── */}
      <div className={`mt-6 rounded-2xl p-5 ${card}`}>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-semibold">Demo buckets</p>
            <p className={`mt-1 text-xs ${label}`}>Per-company public “try-on-your-docs” demo pages.</p>
          </div>
          <div className="flex gap-2">
            <button onClick={() => setCreateOpen((v) => !v)} className="rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-blue-500">
              {createOpen ? 'Close' : '+ New demo bucket'}
            </button>
            <button onClick={load} disabled={loading} className={`rounded-lg px-3 py-1.5 text-xs font-semibold ${ghost}`}>Refresh</button>
          </div>
        </div>

        {error && <p className="mt-3 rounded-lg bg-rose-500/10 px-3 py-2 text-xs text-rose-400">{error}</p>}
        {okMsg && <p className="mt-3 rounded-lg bg-emerald-500/10 px-3 py-2 text-xs text-emerald-400">{okMsg}</p>}

        {createOpen && (
          <CreateForm
            dark={dark} input={input} sub={sub} label={label}
            onCreate={async (payload) => {
              const created = await adminApi.createDemoBucket(payload, session);
              setCreateOpen(false);
              await load();
              setExpanded(created.id);
              flash('Demo bucket created — now upload the prebuild docs.');
            }}
          />
        )}

        <div className="mt-4 space-y-3">
          {loading && buckets.length === 0 ? (
            <p className={`py-4 text-center text-sm ${label}`}>Loading…</p>
          ) : buckets.length === 0 ? (
            <p className={`py-4 text-center text-sm ${label}`}>No demo buckets yet. Create one to get started.</p>
          ) : (
            buckets.map((b) => (
              <BucketCard
                key={b.id} bucket={b} dark={dark} sub={sub} label={label} ghost={ghost} input={input}
                session={session} expanded={expanded === b.id}
                onToggle={() => setExpanded(expanded === b.id ? null : b.id)}
                onChanged={load} onFlash={flash} onError={setError}
              />
            ))
          )}
        </div>
      </div>

      {/* ── Demo call requests ── */}
      <div className={`mt-6 rounded-2xl p-5 ${card}`}>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-semibold">Demo call requests</p>
            <p className={`mt-1 text-xs ${label}`}>“Let’s talk” requests from demo visitors. Create a Zoom link, email them, then paste it here.</p>
          </div>
          <div className="flex gap-2">
            {['pending', 'scheduled', 'all'].map((s) => (
              <button key={s} onClick={() => setMeetingStatus(s)} className={`rounded-lg px-3 py-1.5 text-xs font-semibold ${meetingStatus === s ? 'bg-blue-600 text-white' : ghost}`}>
                {s[0].toUpperCase() + s.slice(1)}
              </button>
            ))}
            <button onClick={() => loadMeetings(meetingStatus)} className={`rounded-lg px-3 py-1.5 text-xs font-semibold ${ghost}`}>Refresh</button>
          </div>
        </div>
        <div className="mt-4 space-y-3">
          {meetings.length === 0 ? (
            <p className={`py-4 text-center text-sm ${label}`}>No call requests.</p>
          ) : (
            meetings.map((m) => (
              <MeetingRow key={m.id} meeting={m} dark={dark} sub={sub} label={label} input={input} session={session} onSaved={() => loadMeetings(meetingStatus)} />
            ))
          )}
        </div>
      </div>
    </>
  );
}

function CreateForm({ dark, input, sub, label, onCreate }) {
  const [company, setCompany] = useState('');
  const [slug, setSlug] = useState('');
  const [slugEdited, setSlugEdited] = useState(false);
  const [code, setCode] = useState('');
  const [caps, setCaps] = useState({ ...DEFAULT_CAPS });
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState('');

  const submit = async () => {
    setErr('');
    if (!company.trim()) return setErr('Company name is required.');
    if (!/^[a-z0-9](?:[a-z0-9-]{0,60}[a-z0-9])?$/.test(slug)) return setErr('Slug: lowercase letters, numbers, hyphens.');
    if (!/^\d{4}$/.test(code)) return setErr('Access code must be 4 digits.');
    setBusy(true);
    try {
      await onCreate({ company_name: company.trim(), slug, access_code: code, caps });
    } catch (e) { setErr(e.message || 'Could not create.'); }
    finally { setBusy(false); }
  };

  return (
    <div className={`mt-4 rounded-xl border p-4 ${sub}`}>
      <div className="grid gap-3 sm:grid-cols-2">
        <label className="block">
          <span className={`text-xs ${label}`}>Company name</span>
          <input className={`mt-1 ${input}`} value={company}
            onChange={(e) => { setCompany(e.target.value); if (!slugEdited) setSlug(slugify(e.target.value)); }}
            placeholder="Acme Corp" />
        </label>
        <label className="block">
          <span className={`text-xs ${label}`}>Slug (URL)</span>
          <input className={`mt-1 ${input}`} value={slug}
            onChange={(e) => { setSlug(slugify(e.target.value)); setSlugEdited(true); }} placeholder="acme-corp" />
          <span className={`mt-0.5 block text-[11px] ${label}`}>/try/{slug || '…'}</span>
        </label>
        <label className="block">
          <span className={`text-xs ${label}`}>4-digit access code</span>
          <input className={`mt-1 ${input}`} value={code} inputMode="numeric"
            onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 4))} placeholder="0000" />
        </label>
      </div>
      <p className={`mt-2 text-[11px] ${label}`}>The first person to enter the code fills in their name &amp; email — they become the demo owner.</p>
      <div className="mt-3">
        <span className={`text-xs ${label}`}>Caps</span>
        <div className="mt-1 grid grid-cols-2 gap-2 sm:grid-cols-3">
          {CAP_FIELDS.map(({ key, label: capLabel, min, max }) => (
            <label key={key} className="block">
              <span className={`text-[11px] ${label}`}>{capLabel}</span>
              <input type="number" min={min} max={max} className={`mt-0.5 ${input}`} value={caps[key]}
                onChange={(e) => setCaps({ ...caps, [key]: parseCapValue(e.target.value, min, max) })} />
            </label>
          ))}
        </div>
      </div>
      {err && <p className="mt-3 text-xs text-rose-400">{err}</p>}
      <button onClick={submit} disabled={busy} className="mt-4 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-500 disabled:opacity-50">
        {busy ? 'Creating…' : 'Create demo bucket'}
      </button>
    </div>
  );
}

function BucketCard({ bucket, dark, sub, label, ghost, input, session, expanded, onToggle, onChanged, onFlash, onError }) {
  const fileRef = useRef(null);
  const [detail, setDetail] = useState(null);
  const [caps, setCaps] = useState({});
  const [code, setCode] = useState(bucket.access_code);
  const [active, setActive] = useState(bucket.is_active);
  const [savingCfg, setSavingCfg] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [activity, setActivity] = useState(null);
  const [showActivity, setShowActivity] = useState(false);

  const [statePillCls, statePillTxt] = STATE_PILL[bucket.files?.state] || STATE_PILL.empty;
  const tryUrl = `${window.location.origin}/try/${bucket.slug}`;

  useEffect(() => {
    if (!expanded) return;
    adminApi.getDemoBucket(bucket.id, session).then((d) => {
      setDetail(d); setCaps(d.caps || {}); setCode(d.access_code); setActive(d.is_active);
    }).catch((e) => onError(e.message));
  }, [expanded, bucket.id, session, onError]);

  const saveConfig = async () => {
    setSavingCfg(true);
    try {
      await adminApi.updateDemoBucket(bucket.id, { caps, access_code: code, is_active: active }, session);
      onFlash('Saved.');
      onChanged();
      const d = await adminApi.getDemoBucket(bucket.id, session); setDetail(d);
    } catch (e) { onError(e.message); }
    finally { setSavingCfg(false); }
  };

  const deleteBucket = async () => {
    const confirmed = window.confirm(`Delete demo bucket "${bucket.company_name}"?\n\nThis removes its demo link, leads, chats, files, and activity. This cannot be undone.`);
    if (!confirmed) return;
    setDeleting(true);
    try {
      await adminApi.deleteDemoBucket(bucket.id, session);
      onFlash('Demo bucket deleted.');
      onChanged();
    } catch (e) { onError(e.message); }
    finally { setDeleting(false); }
  };

  const upload = async (fileList) => {
    const files = Array.from(fileList || []);
    if (files.length === 0) return;
    setUploading(true);
    try {
      await adminApi.uploadDemoFiles(bucket.id, files, session);
      onFlash(`Uploading ${files.length} file(s) — processing now.`);
      const d = await adminApi.getDemoBucket(bucket.id, session); setDetail(d);
      onChanged();
    } catch (e) { onError(e.message); }
    finally { setUploading(false); if (fileRef.current) fileRef.current.value = ''; }
  };

  const openActivity = async () => {
    setShowActivity((v) => !v);
    if (!activity) {
      try { setActivity(await adminApi.getDemoActivity(bucket.id, session)); }
      catch (e) { onError(e.message); }
    }
  };

  return (
    <div className={`rounded-xl border p-4 ${sub}`}>
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <p className="truncate text-sm font-semibold">{bucket.company_name}</p>
            <span className={`rounded-full px-2 py-0.5 text-[11px] font-medium ${statePillCls}`}>{statePillTxt}</span>
            {!bucket.is_active && <span className="rounded-full bg-slate-500/10 px-2 py-0.5 text-[11px] text-slate-400">Inactive</span>}
          </div>
          <div className={`mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs ${label}`}>
            <button onClick={() => { navigator.clipboard?.writeText(tryUrl); onFlash('Demo link copied.'); }} className="text-blue-400 hover:underline">/try/{bucket.slug}</button>
            <span>Code <span className="font-mono font-semibold text-slate-300">{bucket.access_code}</span></span>
            <span>{bucket.counts?.leads || 0} leads</span>
            <span>{bucket.counts?.messages || 0} msgs</span>
            <span>{bucket.counts?.feedback || 0} feedback</span>
            {bucket.counts?.pending_calls > 0 && <span className="font-semibold text-amber-400">{bucket.counts.pending_calls} call req</span>}
            <span>{bucket.files?.ready || 0}/{bucket.files?.total || 0} docs ready</span>
          </div>
        </div>
        <div className="flex shrink-0 gap-2">
          <button onClick={openActivity} className={`rounded-lg px-3 py-1.5 text-xs font-semibold ${ghost}`}>Activity</button>
          <button onClick={onToggle} className={`rounded-lg px-3 py-1.5 text-xs font-semibold ${ghost}`}>{expanded ? 'Close' : 'Manage'}</button>
        </div>
      </div>

      {expanded && detail && (
        <div className="mt-4 space-y-4 border-t border-white/10 pt-4">
          {/* config */}
          <div className="grid gap-3 sm:grid-cols-3">
            <label className="block">
              <span className={`text-[11px] ${label}`}>Access code</span>
              <input className={`mt-0.5 ${input}`} value={code} inputMode="numeric" onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 4))} />
            </label>
            <label className="flex items-center gap-2 pt-5 text-sm">
              <input type="checkbox" checked={active} onChange={(e) => setActive(e.target.checked)} />
              <span className={label}>Active</span>
            </label>
          </div>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
            {CAP_FIELDS.map(({ key, label: capLabel, min, max }) => (
              <label key={key} className="block">
                <span className={`text-[11px] ${label}`}>{capLabel}</span>
                <input type="number" min={min} max={max} className={`mt-0.5 ${input}`} value={caps[key] ?? min}
                  onChange={(e) => setCaps({ ...caps, [key]: parseCapValue(e.target.value, min, max) })} />
              </label>
            ))}
          </div>
          <div className="flex flex-wrap gap-2">
            <button onClick={saveConfig} disabled={savingCfg} className="rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white hover:bg-blue-500 disabled:opacity-50">
              {savingCfg ? 'Saving…' : 'Save caps & code'}
            </button>
            <button onClick={deleteBucket} disabled={deleting} className="rounded-lg bg-rose-600 px-4 py-2 text-xs font-semibold text-white hover:bg-rose-500 disabled:opacity-50">
              {deleting ? 'Deleting…' : 'Delete demo bucket'}
            </button>
          </div>

          {/* prebuild files */}
          <div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold">Prebuild documents</span>
              <button onClick={() => fileRef.current?.click()} disabled={uploading} className="rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-blue-500 disabled:opacity-50">
                {uploading ? 'Uploading…' : '+ Upload files'}
              </button>
              <input ref={fileRef} type="file" multiple className="hidden" onChange={(e) => upload(e.target.files)} />
            </div>
            <div className="mt-2 space-y-1">
              {(detail.file_list || []).length === 0 && <p className={`text-xs ${label}`}>No docs yet. Upload the curated public docs the visitor will explore.</p>}
              {(detail.file_list || []).map((f) => (
                <div key={f.id} className="flex items-center justify-between rounded-lg bg-white/5 px-3 py-1.5 text-xs">
                  <span className="truncate text-slate-300">{f.name}</span>
                  <span className={f.status === 'ready' ? 'text-emerald-400' : f.status === 'failed' ? 'text-rose-400' : 'text-amber-400'}>{f.status}</span>
                </div>
              ))}
            </div>
          </div>

          {/* leads */}
          {(detail.leads || []).length > 0 && (
            <div>
              <span className="text-sm font-semibold">Leads ({detail.leads.length})</span>
              <div className="mt-2 space-y-1">
                {detail.leads.map((l) => (
                  <div key={l.id} className="flex items-center justify-between rounded-lg bg-white/5 px-3 py-1.5 text-xs">
                    <span className="truncate text-slate-300">
                      {l.name} · {l.email}{l.role ? ` · ${l.role}` : ''}{l.is_team_member ? ' · team' : ''}
                    </span>
                    <span className={label}>{l.comeback_count} visit{l.comeback_count === 1 ? '' : 's'}{l.last_seen_at ? ` · ${new Date(l.last_seen_at).toLocaleDateString()}` : ''}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {showActivity && activity && (
        <Activity activity={activity} label={label} />
      )}
    </div>
  );
}

function Activity({ activity, label }) {
  return (
    <div className="mt-4 space-y-3 border-t border-white/10 pt-4">
      {(activity.leads || []).length === 0 && <p className={`text-xs ${label}`}>No visitor activity yet.</p>}
      {(activity.leads || []).map((l) => (
        <div key={l.id} className="rounded-lg bg-white/5 p-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="text-sm font-semibold text-slate-200">
              {l.name} <span className="font-normal text-slate-400">· {l.email}</span>
              {l.is_team_member && <span className="ml-1 rounded bg-indigo-500/15 px-1.5 py-0.5 text-[10px] text-indigo-300">team</span>}
            </p>
            <span className={`text-xs ${label}`}>{l.comeback_count} visits · {l.message_count} msgs</span>
          </div>
          {(l.surveys || []).map((s, i) => (
            <div key={i} className="mt-2 rounded-md bg-amber-500/[0.07] px-2.5 py-1.5 text-xs text-amber-200/90">
              ⭐ {s.rating || '—'}/5 · {s.wants_to_talk ? 'wants a call' : 'no call'}{s.notes ? ` · “${s.notes}”` : ''}
            </div>
          ))}
          {(l.events || []).length > 0 && (
            <div className={`mt-2 flex flex-wrap gap-1 text-[10px] ${label}`}>
              {l.events.slice(0, 16).map((ev, i) => (
                <span key={i} className="rounded bg-white/5 px-1.5 py-0.5" title={ev.created_at ? new Date(ev.created_at).toLocaleString() : ''}>
                  {ev.type}
                </span>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function MeetingRow({ meeting, dark, sub, label, input, session, onSaved }) {
  const [zoom, setZoom] = useState(meeting.zoom_link || '');
  const [notes, setNotes] = useState(meeting.admin_notes || '');
  const [status, setStatus] = useState(meeting.status);
  const [busy, setBusy] = useState(false);

  const save = async (nextStatus) => {
    setBusy(true);
    try {
      const payload = { zoom_link: zoom || null, admin_notes: notes || null, status: nextStatus || status };
      await adminApi.updateDemoMeeting(meeting.id, payload, session);
      onSaved();
    } catch (e) { /* surfaced by parent on reload */ }
    finally { setBusy(false); }
  };

  return (
    <div className={`rounded-xl border p-4 ${sub}`}>
      <div className="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm font-semibold">{meeting.lead_name} <span className="font-normal text-slate-400">· {meeting.company_name}</span></p>
          <p className={`mt-0.5 text-xs ${label}`}>
            {meeting.lead_email}{meeting.lead_role ? ` · ${meeting.lead_role}` : ''}
          </p>
          <p className={`mt-0.5 text-xs ${label}`}>
            Preferred: {meeting.preferred_time ? new Date(meeting.preferred_time).toLocaleString() : 'no time given'}{meeting.timezone ? ` (${meeting.timezone})` : ''}
          </p>
        </div>
        <span className={`w-fit rounded-full px-2.5 py-1 text-xs font-medium ${meeting.status === 'pending' ? 'bg-amber-500/10 text-amber-400' : meeting.status === 'scheduled' ? 'bg-blue-500/10 text-blue-400' : meeting.status === 'done' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-slate-500/10 text-slate-400'}`}>
          {meeting.status}
        </span>
      </div>
      <div className="mt-3 grid gap-2 sm:grid-cols-2">
        <input className={input} placeholder="Paste Zoom link…" value={zoom} onChange={(e) => setZoom(e.target.value)} />
        <input className={input} placeholder="Notes (optional)" value={notes} onChange={(e) => setNotes(e.target.value)} />
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        <button onClick={() => save('scheduled')} disabled={busy} className="rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-blue-500 disabled:opacity-50">Save & mark scheduled</button>
        <button onClick={() => save('done')} disabled={busy} className="rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-500 disabled:opacity-50">Mark done</button>
        <button onClick={() => save('declined')} disabled={busy} className="rounded-lg bg-slate-600/40 px-3 py-1.5 text-xs font-semibold text-slate-200 hover:bg-slate-600/60 disabled:opacity-50">Decline</button>
      </div>
    </div>
  );
}
