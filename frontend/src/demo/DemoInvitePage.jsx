// Standalone route for /try/invite/:token — a teammate joins directly (no code).
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { demoApi, getDemoToken, clearDemoToken } from './demoApi';
import { getInitialTheme, saveTheme, themeOptions } from './demoTheme';
import DemoWorkspace from './DemoWorkspace';
import { DemoBackdrop, DemoLogo, DemoButton, Spinner, Avatar, ErrorNote, ThemeToggle } from './DemoShell';
import { cn } from '../lib/utils';

export default function DemoInvitePage() {
  const { token } = useParams();
  const [phase, setPhase] = useState('checking');
  const [info, setInfo] = useState(null);
  const [me, setMe] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [theme, setTheme] = useState(getInitialTheme());
  const p = themeOptions[theme];
  const onToggleTheme = () => setTheme((prev) => { const next = prev === 'dark' ? 'light' : 'dark'; saveTheme(next); return next; });

  useEffect(() => {
    let cancelled = false;
    async function resume() {
      // If we already have a demo token in this tab, jump straight back to the
      // workspace instead of forcing the teammate through the invite page again.
      if (getDemoToken()) {
        try {
          const data = await demoApi.me();
          if (cancelled) return;
          setMe(data);
          setPhase('workspace');
          return;
        } catch {
          clearDemoToken();
          if (cancelled) return;
        }
      }
      try {
        const data = await demoApi.inviteInfo(token);
        if (cancelled) return;
        if (data?.valid) { setInfo(data); setPhase('invite'); }
        else { setInfo(data); setPhase('invalid'); }
      } catch {
        if (!cancelled) setPhase('invalid');
      }
    }
    resume();
    return () => { cancelled = true; };
  }, [token]);

  const accept = async () => {
    setLoading(true); setError('');
    try { const data = await demoApi.inviteAccept(token); setMe(data.me); setPhase('workspace'); }
    catch (e) { setError(e.message || 'This invite could not be opened.'); }
    finally { setLoading(false); }
  };

  if (phase === 'checking') {
    return <DemoBackdrop theme={theme}><div className="grid min-h-[100dvh] place-items-center"><div className="flex flex-col items-center gap-4"><DemoLogo theme={theme} size="lg" /><Spinner className="h-6 w-6 text-blue-500" /></div></div></DemoBackdrop>;
  }
  if (phase === 'workspace' && me) {
    return <DemoWorkspace initialMe={me} theme={theme} onToggleTheme={onToggleTheme} onExpired={() => { clearDemoToken(); setMe(null); setPhase('invalid'); }} />;
  }
  if (phase === 'invalid') {
    return (
      <DemoBackdrop theme={theme}>
        <div className="absolute right-4 top-4"><ThemeToggle theme={theme} onToggle={onToggleTheme} /></div>
        <div className="grid min-h-[100dvh] place-items-center px-4">
          <div className="w-full max-w-md text-center">
            <div className="mb-6 flex justify-center"><DemoLogo theme={theme} size="lg" /></div>
            <div className={cn('rounded-[2rem] border p-8', p.card.split(' hover:')[0])}>
              <h1 className={cn('text-lg font-bold', p.title)}>This invite isn’t available</h1>
              <p className={cn('mt-2 text-sm', p.text)}>{info?.expired ? 'It looks like this invite has expired.' : 'This invite link is invalid or has been removed.'} Ask whoever invited you to send a new one.</p>
            </div>
          </div>
        </div>
      </DemoBackdrop>
    );
  }
  const firstName = (info?.name || '').split(' ')[0] || 'there';
  const inviter = (info?.inviter_name || '').trim();
  const company = info?.company_name || '';

  return (
    <DemoBackdrop theme={theme}>
      <div className="absolute right-4 top-4"><ThemeToggle theme={theme} onToggle={onToggleTheme} /></div>
      <div className="grid min-h-[100dvh] place-items-center px-4 py-10">
        <div className="w-full max-w-md">
          <div className="mb-6 flex justify-center"><DemoLogo theme={theme} size="lg" /></div>
          <div className={cn('rounded-[2rem] border p-7 text-center', p.card.split(' hover:')[0])}>
            <div className="mb-4 flex justify-center"><Avatar name={info?.name} color={info?.color} size="lg" /></div>
            <h1 className={cn('text-xl font-bold', p.title)}>Hi {firstName} 👋</h1>
            <p className={cn('mt-2 text-sm leading-6', p.text)}>
              {inviter
                ? <><span className={cn('font-semibold', p.title)}>{inviter}</span> invited you to a private <span className={cn('font-semibold', p.title)}>AIveilix</span> demo</>
                : <>You’ve been invited to a private <span className={cn('font-semibold', p.title)}>AIveilix</span> demo</>}
              {company && <> built on <span className={cn('font-semibold', p.title)}>{company}</span>’s own documents.</>}
            </p>
            <div className={cn('mt-4 rounded-2xl border p-4 text-left text-[13px] leading-6', theme === 'dark' ? 'border-white/10 bg-white/[0.03]' : 'border-slate-200 bg-slate-50')}>
              <p className={cn('font-semibold', p.title)}>What is AIveilix?</p>
              <p className={cn('mt-1', p.text)}>
                AIveilix is a document intelligence tool. Upload your files and get cited answers from an AI built on
                your own content — no more digging through PDFs. In this demo, the AI has already been built on
                {company ? ` ${company}'s` : ' the inviter’s'} public documents so you can try it instantly.
              </p>
            </div>
            <div className="mt-4"><ErrorNote theme={theme}>{error}</ErrorNote></div>
            <DemoButton theme={theme} className="mx-auto mt-5 w-full" onClick={accept} loading={loading}>Open the demo →</DemoButton>
            <p className={cn('mt-3 text-[11px]', p.muted)}>No account or code needed — your spot is reserved by this private link.</p>
          </div>
        </div>
      </div>
    </DemoBackdrop>
  );
}
