// Standalone route for /try/invite/:token — a teammate joins directly (no code).
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { demoApi } from './demoApi';
import DemoWorkspace from './DemoWorkspace';
import { DemoBackdrop, DemoLogo, DemoButton, Spinner, Avatar, ErrorNote } from './DemoShell';

export default function DemoInvitePage() {
  const { token } = useParams();
  const [phase, setPhase] = useState('checking'); // checking | invite | workspace | invalid
  const [info, setInfo] = useState(null);
  const [me, setMe] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    demoApi.inviteInfo(token)
      .then((data) => {
        if (cancelled) return;
        if (data?.valid) { setInfo(data); setPhase('invite'); }
        else { setInfo(data); setPhase('invalid'); }
      })
      .catch(() => !cancelled && setPhase('invalid'));
    return () => { cancelled = true; };
  }, [token]);

  const accept = async () => {
    setLoading(true); setError('');
    try {
      const data = await demoApi.inviteAccept(token);
      setMe(data.me);
      setPhase('workspace');
    } catch (e) {
      setError(e.message || 'This invite could not be opened.');
    } finally {
      setLoading(false);
    }
  };

  if (phase === 'checking') {
    return (
      <DemoBackdrop className="grid place-items-center">
        <div className="flex flex-col items-center gap-4"><DemoLogo size="lg" /><Spinner className="h-6 w-6 text-indigo-400" /></div>
      </DemoBackdrop>
    );
  }

  if (phase === 'workspace' && me) {
    return <DemoWorkspace initialMe={me} onExpired={() => setPhase('invalid')} />;
  }

  if (phase === 'invalid') {
    return (
      <DemoBackdrop className="grid place-items-center p-4">
        <div className="w-full max-w-md text-center">
          <div className="mb-6 flex justify-center"><DemoLogo size="lg" /></div>
          <div className="rounded-3xl bg-[#0B1220]/80 p-8 ring-1 ring-white/10">
            <h1 className="text-lg font-bold">This invite isn’t available</h1>
            <p className="mt-2 text-sm text-slate-400">
              {info?.expired ? 'It looks like this invite has expired.' : 'This invite link is invalid or has been removed.'} Ask whoever invited you to send a new one.
            </p>
          </div>
        </div>
      </DemoBackdrop>
    );
  }

  return (
    <DemoBackdrop className="grid place-items-center p-4">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md">
        <div className="mb-6 flex justify-center"><DemoLogo size="lg" /></div>
        <div className="rounded-3xl bg-[#0B1220]/80 p-8 text-center ring-1 ring-white/10 shadow-2xl">
          <div className="mb-4 flex justify-center"><Avatar name={info?.name} color={info?.color} size="lg" /></div>
          <h1 className="text-xl font-bold">Hi {info?.name?.split(' ')[0] || 'there'} 👋</h1>
          <p className="mt-2 text-sm text-slate-400">
            You’ve been invited to explore an AIveilix demo built on{' '}
            <span className="font-semibold text-slate-200">{info?.company_name || 'their'}</span> documents. Jump right in — no code needed.
          </p>
          <div className="mt-4"><ErrorNote>{error}</ErrorNote></div>
          <DemoButton className="mx-auto mt-5 w-full" onClick={accept} loading={loading}>Open the demo →</DemoButton>
        </div>
      </motion.div>
    </DemoBackdrop>
  );
}
