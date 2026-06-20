// Feedback + Let's-Talk modal (2 steps), MCP panel, Team invite, Upload.
import React, { useEffect, useState } from 'react';
import { demoApi, DemoLimitError } from './demoApi';
import {
  DemoModal, DemoButton, DemoField, DemoInput, DemoTextarea, ErrorNote, Spinner, Avatar,
} from './DemoShell';
import { cn } from '../lib/utils';

const LIMIT_COPY = {
  threads: 'You’ve reached the demo’s chat limit',
  messages: 'You’ve reached the demo’s message limit',
  files: 'You’ve reached the demo’s upload limit',
  team_members: 'You’ve reached the demo’s teammate limit',
  comebacks: 'You’ve used all your demo visits',
};

function Stars({ value, onChange }) {
  return (
    <div className="flex justify-center gap-1.5">
      {[1, 2, 3, 4, 5].map((n) => (
        <button
          key={n}
          type="button"
          onClick={() => onChange(n)}
          className="transition hover:scale-110"
          aria-label={`${n} star${n > 1 ? 's' : ''}`}
        >
          <svg viewBox="0 0 24 24" className={cn('h-8 w-8', n <= value ? 'text-amber-400' : 'text-slate-700')} fill="currentColor">
            <path d="M12 2l2.9 6.3 6.9.6-5.2 4.6 1.6 6.8L12 17.3 5.8 20.9l1.6-6.8L2.2 9.5l6.9-.6L12 2z" />
          </svg>
        </button>
      ))}
    </div>
  );
}

function Select({ label, value, onChange, options }) {
  return (
    <DemoField label={label}>
      <div className="relative">
        <select
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
          className="w-full appearance-none rounded-xl bg-slate-800/70 px-3.5 py-2.5 text-sm text-slate-100 outline-none ring-1 ring-white/10 focus:ring-2 focus:ring-indigo-500"
        >
          <option value="" disabled>Select…</option>
          {options.map((o) => <option key={o} value={o}>{o}</option>)}
        </select>
        <svg viewBox="0 0 24 24" className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 9l6 6 6-6" /></svg>
      </div>
    </DemoField>
  );
}

export function FeedbackTalkModal({ open, onClose, limit, onSubmitted, onSnooze }) {
  const [step, setStep] = useState(1);
  const [rating, setRating] = useState(0);
  const [exp, setExp] = useState({});
  const [product, setProduct] = useState({});
  const [notes, setNotes] = useState('');
  const [wantsToTalk, setWantsToTalk] = useState(null);
  const [talkReason, setTalkReason] = useState('');
  const [when, setWhen] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [done, setDone] = useState(false);

  useEffect(() => {
    if (open) {
      setStep(1); setRating(0); setExp({}); setProduct({}); setNotes('');
      setWantsToTalk(null); setTalkReason(''); setWhen(''); setError(''); setDone(false);
    }
  }, [open]);

  const tz = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';

  const submit = async () => {
    setError(''); setLoading(true);
    try {
      await demoApi.survey({
        rating: rating || null,
        experience: exp,
        product_answers: product,
        notes: notes || null,
        wants_to_talk: wantsToTalk,
        talk_reason: talkReason || null,
      });
      if (wantsToTalk && when) {
        await demoApi.meeting({ preferred_time: new Date(when).toISOString(), timezone: tz });
      }
      setDone(true);
      onSubmitted?.();
    } catch (e) {
      setError(e.message || 'Could not submit. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <DemoModal open={open} onClose={onClose} widthClass="max-w-xl">
      <div className="max-h-[88vh] overflow-y-auto p-6 sm:p-7">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-lg font-bold">
              {done ? 'Thank you!' : step === 1 ? 'How was your experience?' : 'Want this in your workflow?'}
            </h2>
            {!done && (
              <p className="mt-1 text-sm text-slate-400">
                {step === 1 ? 'Your feedback helps us understand you better.' : 'Tell us if it’s a fit — we’ll set up a quick call.'}
              </p>
            )}
          </div>
          <button onClick={onClose} className="rounded-lg p-1.5 text-slate-500 hover:bg-white/5 hover:text-slate-300">
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 6l12 12M18 6L6 18" /></svg>
          </button>
        </div>

        {limit && !done && (
          <div className="mt-4 rounded-xl bg-amber-500/10 px-4 py-3 text-sm text-amber-200 ring-1 ring-amber-500/20">
            <strong className="font-semibold">{LIMIT_COPY[limit] || 'You’ve reached a demo limit'}.</strong>{' '}
            That’s all the demo allows — but there’s no limit on the real thing. Leave a note and let’s talk about using it on all your documents.
          </div>
        )}

        {done ? (
          <div className="py-8 text-center">
            <div className="mx-auto mb-3 grid h-14 w-14 place-items-center rounded-full bg-emerald-500/15 ring-1 ring-emerald-500/30">
              <svg viewBox="0 0 24 24" className="h-7 w-7 text-emerald-400" fill="none" stroke="currentColor" strokeWidth="2"><path d="M5 13l4 4L19 7" /></svg>
            </div>
            <p className="text-sm text-slate-300">
              {wantsToTalk && when
                ? 'Got it — we’ll email you a Zoom link for your preferred time.'
                : 'We appreciate your feedback. Enjoy exploring the rest of the demo!'}
            </p>
            <DemoButton className="mx-auto mt-6" onClick={onClose}>Close</DemoButton>
          </div>
        ) : step === 1 ? (
          <div className="mt-5 space-y-4">
            <div className="rounded-xl bg-white/[0.03] p-4 ring-1 ring-white/10">
              <p className="mb-2 text-center text-xs font-medium text-slate-400">Rate your experience</p>
              <Stars value={rating} onChange={setRating} />
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <Select label="Quality of answers" value={exp.answers} onChange={(v) => setExp({ ...exp, answers: v })}
                options={['Spot on', 'Mostly accurate', 'Hit or miss', 'Not useful']} />
              <Select label="How easy was it to use?" value={exp.ease} onChange={(v) => setExp({ ...exp, ease: v })}
                options={['Very easy', 'Easy', 'Okay', 'Confusing']} />
              <Select label="Does it help with your work?" value={product.helpful} onChange={(v) => setProduct({ ...product, helpful: v })}
                options={['A lot', 'Somewhat', 'A little', 'Not really']} />
              <Select label="Would you trust it on real docs?" value={product.trust} onChange={(v) => setProduct({ ...product, trust: v })}
                options={['Definitely', 'Probably', 'Maybe', 'No']} />
            </div>
            <DemoField label="Anything you wish it did?" hint="Optional">
              <DemoTextarea rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="It would be perfect if…" />
            </DemoField>
            <ErrorNote>{error}</ErrorNote>
            <div className="flex justify-between gap-2 pt-1">
              <button onClick={onClose} className="text-sm text-slate-500 hover:text-slate-300">Maybe later</button>
              <DemoButton onClick={() => setStep(2)}>Next →</DemoButton>
            </div>
            {onSnooze && (
              <div className="flex flex-wrap items-center justify-center gap-2 border-t border-white/5 pt-3 text-xs text-slate-500">
                <span>Remind me in</span>
                {[5, 10, 15, 30].map((min) => (
                  <button
                    key={min}
                    onClick={() => onSnooze(min)}
                    className="rounded-lg bg-white/[0.04] px-2.5 py-1 font-semibold text-slate-300 ring-1 ring-white/10 hover:bg-white/[0.08]"
                  >
                    {min} min
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="mt-5 space-y-4">
            <div>
              <p className="mb-2 text-sm font-medium text-slate-300">Would you use this in your workflow?</p>
              <div className="grid grid-cols-2 gap-2">
                {[['Yes, I’m interested', true], ['Not right now', false]].map(([label, val]) => (
                  <button
                    key={label}
                    onClick={() => setWantsToTalk(val)}
                    className={cn(
                      'rounded-xl px-4 py-3 text-sm font-semibold ring-1 transition',
                      wantsToTalk === val
                        ? 'bg-indigo-600 text-white ring-indigo-500'
                        : 'bg-white/[0.04] text-slate-200 ring-white/10 hover:bg-white/[0.08]',
                    )}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
            <DemoField label={wantsToTalk === false ? 'What’s holding you back?' : 'What would you use it for?'} hint="Optional">
              <DemoTextarea rows={2} value={talkReason} onChange={(e) => setTalkReason(e.target.value)}
                placeholder={wantsToTalk === false ? 'e.g. need to check with my team…' : 'e.g. answering questions across all our contracts…'} />
            </DemoField>
            {wantsToTalk && (
              <DemoField label="Pick a time for a quick call" hint={`Your timezone: ${tz}. We’ll email you a Zoom link.`}>
                <DemoInput type="datetime-local" value={when} onChange={(e) => setWhen(e.target.value)} />
              </DemoField>
            )}
            <ErrorNote>{error}</ErrorNote>
            <div className="flex justify-between gap-2 pt-1">
              <button onClick={() => setStep(1)} className="text-sm text-slate-500 hover:text-slate-300">← Back</button>
              <DemoButton onClick={submit} loading={loading} disabled={wantsToTalk === null}>
                {wantsToTalk ? 'Submit & request call' : 'Submit feedback'}
              </DemoButton>
            </div>
          </div>
        )}
      </div>
    </DemoModal>
  );
}

export function McpPanelModal({ open, onClose }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState('');

  useEffect(() => {
    if (!open) return;
    setError(''); setData(null);
    demoApi.mcp().then(setData).catch((e) => setError(e.message || 'Could not load MCP details.'));
    demoApi.logEvent('mcp_opened');
  }, [open]);

  const copy = (text, key) => {
    navigator.clipboard?.writeText(text);
    setCopied(key);
    setTimeout(() => setCopied(''), 1500);
  };

  return (
    <DemoModal open={open} onClose={onClose} widthClass="max-w-lg">
      <div className="p-6 sm:p-7">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-lg font-bold">Use this in ChatGPT &amp; Claude</h2>
            <p className="mt-1 text-sm text-slate-400">Connect these documents to any AI client over MCP.</p>
          </div>
          <button onClick={onClose} className="rounded-lg p-1.5 text-slate-500 hover:bg-white/5 hover:text-slate-300">
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 6l12 12M18 6L6 18" /></svg>
          </button>
        </div>
        {error && <div className="mt-4"><ErrorNote>{error}</ErrorNote></div>}
        {!data && !error && <div className="flex justify-center py-10"><Spinner className="h-6 w-6 text-indigo-400" /></div>}
        {data && (
          <div className="mt-5 space-y-4">
            <div>
              <p className="mb-1 text-xs font-medium text-slate-400">MCP Server URL</p>
              <div className="flex items-center gap-2 rounded-xl bg-slate-800/70 p-2.5 ring-1 ring-white/10">
                <code className="flex-1 truncate text-xs text-indigo-300">{data.mcp_url}</code>
                <button onClick={() => copy(data.mcp_url, 'url')} className="rounded-lg bg-white/5 px-2.5 py-1 text-xs font-semibold text-slate-200 hover:bg-white/10">
                  {copied === 'url' ? 'Copied' : 'Copy'}
                </button>
              </div>
            </div>
            <div className="rounded-xl bg-white/[0.03] p-4 text-sm text-slate-300 ring-1 ring-white/10">
              <p className="mb-2 font-semibold text-slate-200">How to connect</p>
              <ol className="list-decimal space-y-1.5 pl-5 text-[13px] text-slate-400">
                <li>Open ChatGPT or Claude → <span className="text-slate-300">Settings → Connectors / MCP</span>.</li>
                <li>Add a new connector and paste the URL above.</li>
                <li>Ask it about these documents — it answers with citations, right inside your AI.</li>
              </ol>
            </div>
            <p className="text-[11px] text-slate-500">Read-only access to this demo bucket. Tools: {(data.allowed_tools || []).join(', ')}.</p>
          </div>
        )}
      </div>
    </DemoModal>
  );
}

const TEAM_COLORS = ['#6366F1', '#EC4899', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6', '#EF4444', '#14B8A6'];

export function TeamInviteModal({ open, onClose, onInvited }) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [color, setColor] = useState(TEAM_COLORS[0]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [sent, setSent] = useState(false);

  useEffect(() => {
    if (open) { setName(''); setEmail(''); setColor(TEAM_COLORS[0]); setError(''); setSent(false); }
  }, [open]);

  const submit = async (e) => {
    e?.preventDefault();
    if (!name.trim() || !email.trim()) { setError('Enter a name and email.'); return; }
    setError(''); setLoading(true);
    try {
      await demoApi.teamInvite({ name: name.trim(), email: email.trim(), color });
      setSent(true);
      onInvited?.();
    } catch (e) {
      if (e instanceof DemoLimitError) { onClose?.(); onInvited?.(e); return; }
      setError(e.message || 'Could not send the invite.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <DemoModal open={open} onClose={onClose} widthClass="max-w-md">
      <div className="p-6 sm:p-7">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-lg font-bold">Invite a teammate</h2>
            <p className="mt-1 text-sm text-slate-400">They’ll get an email link and join directly — no code needed.</p>
          </div>
          <button onClick={onClose} className="rounded-lg p-1.5 text-slate-500 hover:bg-white/5 hover:text-slate-300">
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 6l12 12M18 6L6 18" /></svg>
          </button>
        </div>
        {sent ? (
          <div className="py-7 text-center">
            <div className="mx-auto mb-3 grid h-12 w-12 place-items-center rounded-full bg-emerald-500/15 ring-1 ring-emerald-500/30">
              <svg viewBox="0 0 24 24" className="h-6 w-6 text-emerald-400" fill="none" stroke="currentColor" strokeWidth="2"><path d="M5 13l4 4L19 7" /></svg>
            </div>
            <p className="text-sm text-slate-300">Invite sent to <span className="font-semibold text-white">{email}</span>.</p>
            <DemoButton className="mx-auto mt-5" onClick={onClose}>Done</DemoButton>
          </div>
        ) : (
          <form onSubmit={submit} className="mt-5 space-y-3.5">
            <DemoField label="Name"><DemoInput value={name} onChange={(e) => setName(e.target.value)} placeholder="Alex Doe" autoFocus /></DemoField>
            <DemoField label="Email"><DemoInput type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="alex@company.com" /></DemoField>
            <DemoField label="Avatar color">
              <div className="flex flex-wrap gap-2">
                {TEAM_COLORS.map((c) => (
                  <button key={c} type="button" onClick={() => setColor(c)}
                    className={cn('h-8 w-8 rounded-full ring-2 ring-offset-2 ring-offset-[#0B1220] transition', color === c ? 'ring-white' : 'ring-transparent')}
                    style={{ background: c }} aria-label={`Color ${c}`} />
                ))}
              </div>
            </DemoField>
            <ErrorNote>{error}</ErrorNote>
            <DemoButton type="submit" className="w-full" loading={loading}>Send invite</DemoButton>
          </form>
        )}
      </div>
    </DemoModal>
  );
}

export function UploadModal({ open, onClose, fileSizeMb, onUploaded }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [ok, setOk] = useState(false);

  useEffect(() => { if (open) { setFile(null); setError(''); setOk(false); } }, [open]);

  const submit = async () => {
    if (!file) return;
    if (file.size > fileSizeMb * 1024 * 1024) { setError(`That file is over the ${fileSizeMb} MB limit.`); return; }
    setError(''); setLoading(true);
    try {
      await demoApi.upload(file);
      setOk(true);
      onUploaded?.();
    } catch (e) {
      if (e instanceof DemoLimitError) { onClose?.(); onUploaded?.(e); return; }
      setError(e.message || 'Upload failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <DemoModal open={open} onClose={onClose} widthClass="max-w-md">
      <div className="p-6 sm:p-7">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-lg font-bold">Add your own document</h2>
            <p className="mt-1 text-sm text-slate-400">Upload a file (up to {fileSizeMb} MB) and chat with it instantly.</p>
          </div>
          <button onClick={onClose} className="rounded-lg p-1.5 text-slate-500 hover:bg-white/5 hover:text-slate-300">
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 6l12 12M18 6L6 18" /></svg>
          </button>
        </div>
        {ok ? (
          <div className="py-7 text-center">
            <div className="mx-auto mb-3 grid h-12 w-12 place-items-center rounded-full bg-emerald-500/15 ring-1 ring-emerald-500/30">
              <svg viewBox="0 0 24 24" className="h-6 w-6 text-emerald-400" fill="none" stroke="currentColor" strokeWidth="2"><path d="M5 13l4 4L19 7" /></svg>
            </div>
            <p className="text-sm text-slate-300">Uploaded! It’s processing now and will be ready to chat with in a moment.</p>
            <DemoButton className="mx-auto mt-5" onClick={onClose}>Done</DemoButton>
          </div>
        ) : (
          <div className="mt-5 space-y-4">
            <label className="block cursor-pointer rounded-2xl border-2 border-dashed border-white/15 bg-white/[0.02] px-4 py-8 text-center transition hover:border-indigo-500/40 hover:bg-white/[0.04]">
              <input type="file" className="hidden" onChange={(e) => setFile(e.target.files?.[0] || null)} />
              <svg viewBox="0 0 24 24" className="mx-auto h-9 w-9 text-slate-500" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M12 16V4m0 0L8 8m4-4l4 4M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2" /></svg>
              <p className="mt-2 text-sm text-slate-300">{file ? file.name : 'Click to choose a file'}</p>
              {file && <p className="mt-0.5 text-xs text-slate-500">{(file.size / (1024 * 1024)).toFixed(1)} MB</p>}
            </label>
            <ErrorNote>{error}</ErrorNote>
            <DemoButton className="w-full" onClick={submit} loading={loading} disabled={!file}>Upload &amp; process</DemoButton>
          </div>
        )}
      </div>
    </DemoModal>
  );
}
