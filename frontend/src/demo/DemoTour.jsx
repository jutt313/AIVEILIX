// First-run spotlight tour. Dims the page and highlights each feature in turn
// using the classic big-box-shadow "hole" trick. Logs tour_completed when done.
import React, { useEffect, useLayoutEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { DemoButton } from './DemoShell';

export default function DemoTour({ steps, onDone }) {
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
    const t = setTimeout(measure, 250); // settle after scroll
    return () => {
      window.removeEventListener('resize', onChange);
      window.removeEventListener('scroll', onChange, true);
      clearTimeout(t);
    };
  }, [measure]);

  const next = () => {
    if (i < steps.length - 1) setI(i + 1);
    else onDone?.(true);
  };
  const skip = () => onDone?.(false);

  if (!step) return null;

  const pad = 8;
  const box = rect
    ? { top: rect.top - pad, left: rect.left - pad, width: rect.width + pad * 2, height: rect.height + pad * 2 }
    : null;

  // tooltip placement: below the target if room, else above, else center
  let tipStyle = { top: '50%', left: '50%', transform: 'translate(-50%, -50%)' };
  if (box) {
    const below = box.top + box.height + 14;
    const spaceBelow = window.innerHeight - below;
    if (spaceBelow > 180) {
      tipStyle = { top: below, left: Math.min(Math.max(box.left, 16), window.innerWidth - 340) };
    } else {
      tipStyle = { top: Math.max(box.top - 190, 16), left: Math.min(Math.max(box.left, 16), window.innerWidth - 340) };
    }
  }

  return (
    <div className="fixed inset-0 z-[200]">
      {/* dim + spotlight hole */}
      {box ? (
        <motion.div
          layout
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          className="pointer-events-none absolute rounded-2xl ring-2 ring-indigo-400/80"
          style={{
            top: box.top, left: box.left, width: box.width, height: box.height,
            boxShadow: '0 0 0 9999px rgba(2,6,23,0.82)',
          }}
        />
      ) : (
        <div className="absolute inset-0 bg-[#020617]/82" />
      )}

      {/* tooltip */}
      <AnimatePresence mode="wait">
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          className="absolute w-[320px] rounded-2xl bg-[#0B1220] p-5 ring-1 ring-white/15 shadow-2xl"
          style={tipStyle}
        >
          <div className="mb-2 flex items-center gap-2">
            <span className="grid h-6 w-6 place-items-center rounded-full bg-indigo-500/20 text-xs font-bold text-indigo-300">{i + 1}</span>
            <span className="text-[11px] font-medium uppercase tracking-wide text-slate-500">{i + 1} of {steps.length}</span>
          </div>
          <h3 className="text-base font-bold">{step.title}</h3>
          <p className="mt-1.5 text-sm text-slate-400">{step.body}</p>
          <div className="mt-4 flex items-center justify-between">
            <button onClick={skip} className="text-xs text-slate-500 hover:text-slate-300">Skip tour</button>
            <DemoButton onClick={next}>{i < steps.length - 1 ? 'Next' : 'Got it'}</DemoButton>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
