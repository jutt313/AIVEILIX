// Standalone route for /try/invite/:token — a teammate joins directly (no code).
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { demoApi } from './demoApi';
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
    demoApi.inviteInfo(token)
      .then((data) => { if (cancelled) return; if (data?.valid) { setInfo(data); setPhase('invite'); } else { setInfo(data); setPhase('invalid'); } })
      .catch(() => !cancelled && setPhase('invalid'));
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
    return <DemoWorkspace initialMe={me} theme={theme} onToggleTheme={onToggleTheme} onExpired={() => setPhase('invalid')} />;
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
  return (
    <DemoBackdrop theme={theme}>
      <div className="absolute right-4 top-4"><ThemeToggle theme={theme} onToggle={onToggleTheme} /></div>
      <div className="grid min-h-[100dvh] place-items-center px-4">
        <div className="w-full max-w-md">
          <div className="mb-6 flex justify-center"><DemoLogo theme={theme} size="lg" /></div>
          <div className={cn('rounded-[2rem] border p-8 text-center', p.card.split(' hover:')[0])}>
            <div className="mb-4 flex justify-center"><Avatar name={info?.name} color={info?.color} size="lg" /></div>
            <h1 className={cn('text-xl font-bold', p.title)}>Hi {info?.name?.split(' ')[0] || 'there'} 👋</h1>
            <p className={cn('mt-2 text-sm', p.text)}>You’ve been invited to explore an AIveilix demo built on <span className={cn('font-semibold', p.title)}>{info?.company_name || 'their'}</span> documents. Jump right in — no code needed.</p>
            <div className="mt-4"><ErrorNote theme={theme}>{error}</ErrorNote></div>
            <DemoButton theme={theme} className="mx-auto mt-5 w-full" onClick={accept} loading={loading}>Open the demo →</DemoButton>
          </div>
        </div>
      </div>
    </DemoBackdrop>
  );
}
