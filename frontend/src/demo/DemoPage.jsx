// Standalone route for /try/:slug — its own shell, no dashboard chrome.
// Resumes an existing demo session (per-tab token) or runs the entry flow.
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { demoApi, getDemoToken, clearDemoToken } from './demoApi';
import DemoEntry from './DemoEntry';
import DemoWorkspace from './DemoWorkspace';
import { DemoBackdrop, DemoLogo, Spinner } from './DemoShell';

export default function DemoPage() {
  const { slug } = useParams();
  const [phase, setPhase] = useState('checking'); // checking | entry | workspace
  const [me, setMe] = useState(null);

  useEffect(() => {
    let cancelled = false;
    async function resume() {
      if (!getDemoToken()) { if (!cancelled) setPhase('entry'); return; }
      try {
        const data = await demoApi.me();
        // Token could belong to a different slug — only resume if it matches.
        if (data?.slug && data.slug !== slug) { clearDemoToken(); if (!cancelled) setPhase('entry'); return; }
        if (!cancelled) { setMe(data); setPhase('workspace'); }
      } catch {
        clearDemoToken();
        if (!cancelled) setPhase('entry');
      }
    }
    resume();
    return () => { cancelled = true; };
  }, [slug]);

  if (phase === 'checking') {
    return (
      <DemoBackdrop className="grid place-items-center">
        <div className="flex flex-col items-center gap-4">
          <DemoLogo size="lg" />
          <Spinner className="h-6 w-6 text-indigo-400" />
        </div>
      </DemoBackdrop>
    );
  }

  if (phase === 'workspace' && me) {
    return (
      <DemoWorkspace
        initialMe={me}
        onExpired={() => { clearDemoToken(); setMe(null); setPhase('entry'); }}
      />
    );
  }

  return <DemoEntry slug={slug} onEntered={(m) => { setMe(m); setPhase('workspace'); }} />;
}
