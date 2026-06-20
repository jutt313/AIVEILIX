// Entry flow for /try/:slug — 4-digit CodeGate → Name/Email/Role capture.
import React, { useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { demoApi } from './demoApi';
import {
  DemoBackdrop, DemoLogo, DemoButton, DemoField, DemoInput, ErrorNote,
} from './DemoShell';

function CodeBoxes({ value, onChange, onComplete, disabled }) {
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
      if (text) {
        e.preventDefault();
        onChange(text);
        if (text.length === 4) onComplete?.(text);
        else refs.current[text.length]?.focus();
      }
    }}>
      {[0, 1, 2, 3].map((i) => (
        <input
          key={i}
          ref={(el) => (refs.current[i] = el)}
          value={digits[i].trim()}
          disabled={disabled}
          inputMode="numeric"
          maxLength={1}
          aria-label={`Digit ${i + 1}`}
          onChange={(e) => setDigit(i, e.target.value.replace(/\D/g, '').slice(-1))}
          onKeyDown={(e) => {
            if (e.key === 'Backspace' && !digits[i].trim() && i > 0) refs.current[i - 1]?.focus();
          }}
          className="h-16 w-14 rounded-2xl bg-slate-800/70 text-center text-2xl font-bold text-slate-100 outline-none ring-1 ring-white/10 focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
        />
      ))}
    </div>
  );
}

export default function DemoEntry({ slug, onEntered }) {
  const [step, setStep] = useState('code'); // 'code' | 'identity'
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
      if (res.ok) {
        setStep('identity');
      } else {
        setError('That code isn’t right. Check the code in your invite.');
        setCode('');
      }
    } catch (e) {
      setError(e.message || 'Could not verify the code.');
    } finally {
      setLoading(false);
    }
  };

  const submitIdentity = async (e) => {
    e?.preventDefault();
    if (!name.trim() || !email.trim()) { setError('Please enter your name and email.'); return; }
    setError(''); setLoading(true);
    try {
      const data = await demoApi.enter(slug, { code, name: name.trim(), email: email.trim(), role: role.trim() || null });
      onEntered(data.me);
    } catch (e) {
      // A wrong/expired code (admin rotated it) sends us back to the code step.
      if (e.status === 403) { setStep('code'); setCode(''); }
      setError(e.message || 'Could not enter the demo.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <DemoBackdrop className="grid place-items-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-md"
      >
        <div className="mb-6 flex justify-center"><DemoLogo size="lg" /></div>
        <div className="overflow-hidden rounded-3xl bg-[#0B1220]/80 p-7 ring-1 ring-white/10 shadow-2xl backdrop-blur">
          {step === 'code' ? (
            <>
              <h1 className="text-center text-xl font-bold">Welcome to your private demo</h1>
              <p className="mt-2 text-center text-sm text-slate-400">
                Enter the 4-digit access code from your invite to explore an AI built on your own documents.
              </p>
              <div className="mt-7">
                <CodeBoxes value={code} onChange={setCode} onComplete={verify} disabled={loading} />
              </div>
              <div className="mt-6">
                <ErrorNote>{error}</ErrorNote>
              </div>
              <DemoButton
                className="mt-5 w-full"
                onClick={() => verify()}
                loading={loading}
                disabled={code.length !== 4}
              >
                Continue
              </DemoButton>
            </>
          ) : (
            <form onSubmit={submitIdentity}>
              <h1 className="text-center text-xl font-bold">Tell us who you are</h1>
              <p className="mt-2 text-center text-sm text-slate-400">
                So we can personalize your demo and follow up if you'd like.
              </p>
              <div className="mt-6 space-y-3.5">
                <DemoField label="Your name">
                  <DemoInput value={name} onChange={(e) => setName(e.target.value)} placeholder="Jane Smith" autoFocus />
                </DemoField>
                <DemoField label="Work email">
                  <DemoInput type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="jane@company.com" />
                </DemoField>
                <DemoField label="Your role" hint="Optional — helps us tailor the conversation.">
                  <DemoInput value={role} onChange={(e) => setRole(e.target.value)} placeholder="Head of Operations" />
                </DemoField>
              </div>
              <div className="mt-4"><ErrorNote>{error}</ErrorNote></div>
              <DemoButton className="mt-5 w-full" type="submit" loading={loading}>
                Enter the demo →
              </DemoButton>
              <button
                type="button"
                onClick={() => { setStep('code'); setError(''); }}
                className="mt-3 w-full text-center text-xs text-slate-500 hover:text-slate-300"
              >
                ← Use a different code
              </button>
            </form>
          )}
        </div>
        <p className="mt-5 text-center text-[11px] text-slate-600">
          Powered by AIveilix · Your data stays private to this demo.
        </p>
      </motion.div>
    </DemoBackdrop>
  );
}
