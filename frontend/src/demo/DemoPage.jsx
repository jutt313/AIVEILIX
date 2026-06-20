// Standalone route for /try/:slug — own shell, no dashboard chrome. Owns theme
// (light default, persisted) and resumes an existing per-tab demo session.
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { demoApi, getDemoToken, clearDemoToken } from './demoApi';
import { getInitialTheme, saveTheme } from './demoTheme';
import DemoEntry from './DemoEntry';
import DemoWorkspace from './DemoWorkspace';
import { DemoBackdrop, DemoLogo, Spinner } from './DemoShell';

export default function DemoPage() {
  const { slug } = useParams();
  const [phase, setPhase] = useState('checking');
  const [me, setMe] = useState(null);
  const [theme, setTheme] = useState(getInitialTheme());
  const onToggleTheme = () => setTheme((prev) => { const next = prev === 'dark' ? 'light' : 'dark'; saveTheme(next); return next; });

  useEffect(() => {
    let cancelled = false;
    async function resume() {
      if (!getDemoToken()) { if (!cancelled) setPhase('entry'); return; }
      try {
        const data = await demoApi.me();
        if (data?.slug && data.slug !== slug) { clearDemoToken(); if (!cancelled) setPhase('entry'); return; }
        if (!cancelled) { setMe(data); setPhase('workspace'); }
      } catch { clearDemoToken(); if (!cancelled) setPhase('entry'); }
    }
    resume();
    return () => { cancelled = true; };
  }, [slug]);

  if (phase === 'checking') {
    return (
      <DemoBackdrop theme={theme}>
        <div className="grid min-h-[100dvh] place-items-center">
          <div className="flex flex-col items-center gap-4"><DemoLogo theme={theme} size="lg" /><Spinner className="h-6 w-6 text-blue-500" /></div>
        </div>
      </DemoBackdrop>
    );
  }

  if (phase === 'workspace' && me) {
    return <DemoWorkspace initialMe={me} theme={theme} onToggleTheme={onToggleTheme} onExpired={() => { clearDemoToken(); setMe(null); setPhase('entry'); }} />;
  }

  return <DemoEntry slug={slug} theme={theme} onToggleTheme={onToggleTheme} onEntered={(m) => { setMe(m); setPhase('workspace'); }} />;
}
