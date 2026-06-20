// First-run spotlight tour. Dims the page and highlights each feature using the
// big-box-shadow "hole" trick. Themed to the app palette.
import React, { useEffect, useLayoutEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { DemoButton } from './DemoShell';
import { themeOptions } from './demoTheme';
import { cn } from '../lib/utils';

export default function DemoTour({ steps, onDone, theme = 'light' }) {
  const isDark = theme === 'dark';
  const p = themeOptions[theme];
  const [i, setI] = useState(0);
  const [rect, setRect] = useState(null);
  const step = steps[i];

  const measure = useCallback(() => {
    if (!step) return;
    const el = document.querySelector(step.selector);
    if (!el) { setRect(null); return; }
    el.scrollIntoView({ block: 'center', behavior: 'smooth' });
    const r = el.getBoundingClientRect();
    setRect({ top: r.top, left: r.left, width: r.width, height: r.height });
  }, [step]);

  useLayoutEffect(() => { measure(); }, [measure]);
  useEffect(() => {
    const onChange = () => measure();
    window.addEventListener('resize', onChange);
    window.addEventListener('scroll', onChange, true);
    const tmo = setTimeout(measure, 250);
    return () => { window.removeEventListener('resize', onChange); window.removeEventListener('scroll', onChange, true); clearTimeout(tmo); };
  }, [measure]);

  const next = () => { if (i < steps.length - 1) setI(i + 1); else onDone?.(true); };
  const skip = () => onDone?.(false);

  if (!step) return null;

  const pad = 8;
  const box = rect ? { top: rect.top - pad, left: rect.left - pad, width: rect.width + pad * 2, height: rect.height + pad * 2 } : null;
  const dim = isDark ? 'rgba(2,6,23,0.82)' : 'rgba(15,23,42,0.45)';

  let tipStyle = { top: '50%', left: '50%', transform: 'translate(-50%, -50%)' };
  if (box) {
    const below = box.top + box.height + 14;
    if (window.innerHeight - below > 180) tipStyle = { top: below, left: Math.min(Math.max(box.left, 16), window.innerWidth - 340) };
    else tipStyle = { top: Math.max(box.top - 190, 16), left: Math.min(Math.max(box.left, 16), window.innerWidth - 340) };
  }

  return (
    <div className="fixed inset-0 z-[200]">
      {box ? (
        <motion.div layout transition={{ type: 'spring', stiffness: 300, damping: 30 }} className="pointer-events-none absolute rounded-2xl ring-2 ring-blue-400/80"
          style={{ top: box.top, left: box.left, width: box.width, height: box.height, boxShadow: `0 0 0 9999px ${dim}` }} />
      ) : (
        <div className="absolute inset-0" style={{ background: dim }} />
      )}
      <AnimatePresence mode="wait">
        <motion.div key={i} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}
          className={cn('absolute w-[320px] rounded-2xl border p-5 shadow-2xl', isDark ? 'border-white/15 bg-[#0b1424]' : 'border-slate-200 bg-white')} style={tipStyle}>
          <div className="mb-2 flex items-center gap-2">
            <span className="grid h-6 w-6 place-items-center rounded-full bg-blue-500/15 text-xs font-bold text-blue-500">{i + 1}</span>
            <span className={cn('text-[11px] font-medium uppercase tracking-wide', p.muted)}>{i + 1} of {steps.length}</span>
          </div>
          <h3 className={cn('text-base font-bold', p.title)}>{step.title}</h3>
          <p className={cn('mt-1.5 text-sm', p.text)}>{step.body}</p>
          <div className="mt-4 flex items-center justify-between">
            <button onClick={skip} className={cn('text-xs', p.muted, 'hover:opacity-80')}>Skip tour</button>
            <DemoButton theme={theme} onClick={next}>{i < steps.length - 1 ? 'Next' : 'Got it'}</DemoButton>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
