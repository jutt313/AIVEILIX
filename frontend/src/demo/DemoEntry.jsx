// Entry flow for /try/:slug — 4-digit CodeGate → Name/Email/Role. Branded to the
// app's AuthShell look (logo, blue/cyan glow, themed card).
import React, { useRef, useState } from 'react';
import { demoApi } from './demoApi';
import { themeOptions } from './demoTheme';
import { DemoBackdrop, DemoLogo, DemoButton, DemoField, DemoInput, ErrorNote, ThemeToggle } from './DemoShell';
import { cn } from '../lib/utils';

function CodeBoxes({ value, onChange, onComplete, disabled, theme }) {
  const p = themeOptions[theme];
  const refs = useRef([]);
  const digits = value.padEnd(4, ' ').slice(0, 4).split('');
  const setDigit = (i, d) => {
    const next = value.split('');
    next[i] = d;
    const joined = next.join('').replace(/\s/g, '').slice(0, 4);
    onChange(joined);
    if (d && i < 3) refs.current[i + 1]?.focus();
    if (joined.length === 4) onComplete?.(joined);
  };
  return (
    <div className="flex justify-center gap-3" onPaste={(e) => {
      const text = (e.clipboardData.getData('text') || '').replace(/\D/g, '').slice(0, 4);
      if (text) { e.preventDefault(); onChange(text); if (text.length === 4) onComplete?.(text); else refs.current[text.length]?.focus(); }
    }}>
      {[0, 1, 2, 3].map((i) => (
        <input key={i} ref={(el) => (refs.current[i] = el)} value={digits[i].trim()} disabled={disabled} inputMode="numeric" maxLength={1} aria-label={`Digit ${i + 1}`}
          onChange={(e) => setDigit(i, e.target.value.replace(/\D/g, '').slice(-1))}
          onKeyDown={(e) => { if (e.key === 'Backspace' && !digits[i].trim() && i > 0) refs.current[i - 1]?.focus(); }}
          className={cn('h-16 w-14 rounded-2xl border text-center text-2xl font-bold outline-none transition focus:ring-2 focus:ring-blue-500/30 disabled:opacity-50', p.input)} />
      ))}
    </div>
  );
}

export default function DemoEntry({ slug, onEntered, theme = 'light', onToggleTheme }) {
  const p = themeOptions[theme];
  const [step, setStep] = useState('code');
  const [code, setCode] = useState('');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const verify = async (value) => {
    const c = value || code;
    if (c.length !== 4) return;
    setError(''); setLoading(true);
    try {
      const res = await demoApi.verifyCode(slug, c);
      if (res.ok) setStep('identity');
      else { setError('That code isn’t right. Check the code in your invite.'); setCode(''); }
    } catch (e) { setError(e.message || 'Could not verify the code.'); }
    finally { setLoading(false); }
  };

  const submitIdentity = async (e) => {
    e?.preventDefault();
    if (!name.trim() || !email.trim()) { setError('Please enter your name and email.'); return; }
    setError(''); setLoading(true);
    try {
      const data = await demoApi.enter(slug, { code, name: name.trim(), email: email.trim(), role: role.trim() || null });
      onEntered(data.me);
    } catch (e) { if (e.status === 403) { setStep('code'); setCode(''); } setError(e.message || 'Could not enter the demo.'); }
    finally { setLoading(false); }
  };

  return (
    <DemoBackdrop theme={theme}>
      <div className="absolute right-4 top-4"><ThemeToggle theme={theme} onToggle={onToggleTheme} /></div>
      <div className="flex min-h-[100dvh] items-center justify-center px-4 py-12">
        <div className="w-full max-w-[28rem]">
          <div className="mb-6 flex justify-center"><DemoLogo theme={theme} size="lg" /></div>
          <section className={cn('rounded-[2rem] border px-5 py-6 transition-all duration-300 sm:px-7', p.card.split(' hover:')[0])}>
            {step === 'code' ? (
              <>
                <div className="text-center">
                  <p className={cn('text-xs font-semibold uppercase tracking-[0.35em]', p.accent)}>Private demo</p>
                  <h1 className={cn('mt-3 text-2xl font-semibold tracking-tight', p.title)}>Welcome</h1>
                  <p className={cn('mt-2 text-sm leading-6', p.text)}>Enter the 4-digit access code from your invite to explore an AI built on your own documents.</p>
                </div>
                <div className="mt-7"><CodeBoxes value={code} onChange={setCode} onComplete={verify} disabled={loading} theme={theme} /></div>
                <div className="mt-5"><ErrorNote theme={theme}>{error}</ErrorNote></div>
                <DemoButton theme={theme} className="mt-5 w-full" onClick={() => verify()} loading={loading} disabled={code.length !== 4}>Continue</DemoButton>
              </>
            ) : (
              <form onSubmit={submitIdentity}>
                <div className="text-center">
                  <p className={cn('text-xs font-semibold uppercase tracking-[0.35em]', p.accent)}>One more step</p>
                  <h1 className={cn('mt-3 text-2xl font-semibold tracking-tight', p.title)}>Tell us who you are</h1>
                  <p className={cn('mt-2 text-sm leading-6', p.text)}>So we can personalize your demo and follow up if you’d like.</p>
                </div>
                <div className="mt-6 space-y-3.5">
                  <DemoField theme={theme} label="Your name"><DemoInput theme={theme} value={name} onChange={(e) => setName(e.target.value)} placeholder="Jane Smith" autoFocus /></DemoField>
                  <DemoField theme={theme} label="Work email"><DemoInput theme={theme} type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="jane@company.com" /></DemoField>
                  <DemoField theme={theme} label="Your role" hint="Optional — helps us tailor the conversation."><DemoInput theme={theme} value={role} onChange={(e) => setRole(e.target.value)} placeholder="Head of Operations" /></DemoField>
                </div>
                <div className="mt-4"><ErrorNote theme={theme}>{error}</ErrorNote></div>
                <DemoButton theme={theme} className="mt-5 w-full" type="submit" loading={loading}>Enter the demo →</DemoButton>
                <button type="button" onClick={() => { setStep('code'); setError(''); }} className={cn('mt-3 w-full text-center text-xs', p.muted, 'hover:opacity-80')}>← Use a different code</button>
              </form>
            )}
          </section>
          <p className={cn('mt-5 text-center text-[11px]', p.muted)}>Powered by AIveilix · Your data stays private to this demo.</p>
        </div>
      </div>
    </DemoBackdrop>
  );
}
