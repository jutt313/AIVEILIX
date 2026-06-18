/* Modern landing-page primitives — sourced from Aceternity UI + Magic UI
   patterns. All pure JSX, depend only on framer-motion + clsx + tailwind-merge.
*/
import React, {
  useCallback, useEffect, useId, useMemo, useRef, useState,
} from 'react';
import {
  AnimatePresence, motion, useInView, useMotionTemplate,
  useMotionValue, useScroll, useSpring, useTransform,
} from 'framer-motion';
import { cn } from './lib/utils';

/* ─────────────────────────── Spotlight ─────────────────────────── */
export const Spotlight = ({ className, fill = 'white' }) => (
  <svg
    className={cn(
      'animate-spotlight pointer-events-none absolute z-[1] h-[169%] w-[138%] lg:w-[84%] opacity-0',
      className,
    )}
    xmlns="http://www.w3.org/2000/svg" viewBox="0 0 3787 2842" fill="none"
  >
    <g filter="url(#filter)">
      <ellipse
        cx="1924.71" cy="273.501" rx="1924.71" ry="273.501"
        transform="matrix(-0.822377 -0.568943 -0.568943 0.822377 3631.88 2291.09)"
        fill={fill} fillOpacity="0.21"
      />
    </g>
    <defs>
      <filter id="filter" x="0.86" y="0.84" width="3785.16" height="2840.26" filterUnits="userSpaceOnUse" colorInterpolationFilters="sRGB">
        <feFlood floodOpacity="0" result="BackgroundImageFix" />
        <feBlend mode="normal" in="SourceGraphic" in2="BackgroundImageFix" result="shape" />
        <feGaussianBlur stdDeviation="151" result="effect1_foregroundBlur_1065_8" />
      </filter>
    </defs>
  </svg>
);

/* ───────────────────────── Background Beams ─────────────────────── */
export const BackgroundBeams = React.memo(({ className }) => {
  const paths = useMemo(() => Array.from({ length: 50 }, (_, i) => {
    const k = i * 7;
    return `M-${380 - k} -${189 + k}C-${380 - k} -${189 + k} -${312 - k} ${216 - k} ${152 + k} ${343 - k}C${616 + k} ${470 - k} ${684 + k} ${875 - k} ${684 + k} ${875 - k}`;
  }), []);
  return (
    <div className={cn(
      'absolute inset-0 h-full w-full flex items-center justify-center [mask-image:radial-gradient(50%_50%_at_50%_50%,white,transparent)]',
      className,
    )}>
      <svg className="z-0 h-full w-full pointer-events-none absolute" width="100%" height="100%" viewBox="0 0 696 316" fill="none">
        {paths.map((d, idx) => (
          <motion.path
            key={`p-${idx}`} d={d}
            stroke={`url(#bb-grad-${idx})`} strokeOpacity="0.4" strokeWidth="0.5"
          />
        ))}
        <defs>
          {paths.map((_, idx) => (
            <motion.linearGradient
              id={`bb-grad-${idx}`} key={`g-${idx}`}
              initial={{ x1: '0%', x2: '0%', y1: '0%', y2: '0%' }}
              animate={{
                x1: ['0%', '100%'], x2: ['0%', '95%'],
                y1: ['0%', '100%'], y2: ['0%', `${93 + Math.random() * 8}%`],
              }}
              transition={{
                duration: Math.random() * 10 + 10, ease: 'easeInOut',
                repeat: Infinity, delay: Math.random() * 10,
              }}
            >
              <stop stopColor="#18CCFC" stopOpacity="0" />
              <stop stopColor="#18CCFC" />
              <stop offset="32.5%" stopColor="#6344F5" />
              <stop offset="100%" stopColor="#AE48FF" stopOpacity="0" />
            </motion.linearGradient>
          ))}
        </defs>
      </svg>
    </div>
  );
});
BackgroundBeams.displayName = 'BackgroundBeams';

/* ─────────────────────── Animated Grid Pattern ──────────────────── */
export function AnimatedGridPattern({
  width = 40, height = 40, x = -1, y = -1, strokeDasharray = 0,
  numSquares = 50, className, maxOpacity = 0.5, duration = 4, repeatDelay = 0.5, ...props
}) {
  const id = useId();
  const containerRef = useRef(null);
  const [dims, setDims] = useState({ width: 0, height: 0 });
  const [squares, setSquares] = useState([]);

  const getPos = useCallback(() => [
    Math.floor((Math.random() * dims.width) / width),
    Math.floor((Math.random() * dims.height) / height),
  ], [dims, width, height]);

  const generate = useCallback((count) =>
    Array.from({ length: count }, (_, i) => ({ id: i, pos: getPos(), iteration: 0 })),
  [getPos]);

  const update = useCallback((sid) => {
    setSquares((cur) => {
      const c = cur[sid]; if (!c) return cur;
      const next = cur.slice();
      next[sid] = { ...c, pos: getPos(), iteration: c.iteration + 1 };
      return next;
    });
  }, [getPos]);

  useEffect(() => { if (dims.width && dims.height) setSquares(generate(numSquares)); }, [dims, generate, numSquares]);
  useEffect(() => {
    const el = containerRef.current; if (!el) return;
    const ro = new ResizeObserver((entries) => {
      for (const e of entries) setDims({ width: e.contentRect.width, height: e.contentRect.height });
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  return (
    <svg ref={containerRef} aria-hidden="true"
      className={cn('pointer-events-none absolute inset-0 h-full w-full fill-gray-400/30 stroke-gray-400/30', className)}
      {...props}
    >
      <defs>
        <pattern id={id} width={width} height={height} patternUnits="userSpaceOnUse" x={x} y={y}>
          <path d={`M.5 ${height}V.5H${width}`} fill="none" strokeDasharray={strokeDasharray} />
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill={`url(#${id})`} />
      <svg x={x} y={y} className="overflow-visible">
        {squares.map(({ pos: [sx, sy], id: sid, iteration }, index) => (
          <motion.rect
            key={`${sid}-${iteration}`}
            initial={{ opacity: 0 }} animate={{ opacity: maxOpacity }}
            transition={{ duration, repeat: 1, delay: index * 0.1, repeatType: 'reverse', repeatDelay }}
            onAnimationComplete={() => update(sid)}
            width={width - 1} height={height - 1}
            x={sx * width + 1} y={sy * height + 1}
            fill="currentColor" strokeWidth="0"
          />
        ))}
      </svg>
    </svg>
  );
}

/* ───────────────────────────── Marquee ──────────────────────────── */
export function Marquee({ className, reverse = false, pauseOnHover = false, children, vertical = false, repeat = 4, ...rest }) {
  return (
    <div {...rest} className={cn(
      'group flex overflow-hidden p-2 [--duration:40s] [--gap:1rem] gap-[var(--gap)]',
      vertical ? 'flex-col' : 'flex-row', className,
    )}>
      {Array(repeat).fill(0).map((_, i) => (
        <div key={i} className={cn(
          'flex shrink-0 justify-around gap-[var(--gap)]',
          vertical ? 'animate-marquee-vertical flex-col' : 'animate-marquee flex-row',
          pauseOnHover && 'group-hover:[animation-play-state:paused]',
          reverse && '[animation-direction:reverse]',
        )}>
          {children}
        </div>
      ))}
    </div>
  );
}

/* ───────────────────────────── BlurFade ─────────────────────────── */
export function BlurFade({
  children, className, variant, duration = 0.55, delay = 0,
  offset = 12, direction = 'down', inView = true, inViewMargin = '-80px', blur = '6px', ...props
}) {
  const ref = useRef(null);
  const seen = useInView(ref, { once: true, margin: inViewMargin });
  const visible = !inView || seen;
  const v = variant ?? {
    hidden: {
      [direction === 'left' || direction === 'right' ? 'x' : 'y']:
        direction === 'right' || direction === 'down' ? -offset : offset,
      opacity: 0, filter: `blur(${blur})`,
    },
    visible: { x: 0, y: 0, opacity: 1, filter: 'blur(0px)' },
  };
  return (
    <AnimatePresence>
      <motion.div
        ref={ref} initial="hidden" animate={visible ? 'visible' : 'hidden'}
        exit="hidden" variants={v}
        transition={{ delay: 0.04 + delay, duration, ease: 'easeOut', filter: { duration } }}
        className={className} {...props}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}

/* ─────────────────────────── BorderBeam ─────────────────────────── */
export const BorderBeam = ({
  className, size = 200, duration = 6, delay = 0,
  colorFrom = '#60a5fa', colorTo = '#a855f7', reverse = false,
  initialOffset = 0, borderWidth = 1.5,
}) => (
  <div
    className="pointer-events-none absolute inset-0 rounded-[inherit] border border-transparent"
    style={{
      WebkitMask: 'linear-gradient(transparent,transparent), linear-gradient(#000,#000)',
      WebkitMaskClip: 'padding-box, border-box',
      WebkitMaskComposite: 'destination-out',
      maskComposite: 'exclude',
      borderWidth: `${borderWidth}px`,
    }}
  >
    <motion.div
      className={cn('absolute aspect-square', className)}
      style={{
        width: size,
        offsetPath: `rect(0 auto auto 0 round ${size}px)`,
        background: `linear-gradient(to left, ${colorFrom}, ${colorTo}, transparent)`,
      }}
      initial={{ offsetDistance: `${initialOffset}%` }}
      animate={{
        offsetDistance: reverse
          ? [`${100 - initialOffset}%`, `${-initialOffset}%`]
          : [`${initialOffset}%`, `${100 + initialOffset}%`],
      }}
      transition={{ repeat: Infinity, ease: 'linear', duration, delay: -delay }}
    />
  </div>
);

/* ─────────────────────────── NumberTicker ───────────────────────── */
export function NumberTicker({ value, startValue = 0, direction = 'up', delay = 0, className, decimalPlaces = 0, suffix = '', ...props }) {
  const ref = useRef(null);
  const motionValue = useMotionValue(direction === 'down' ? value : startValue);
  const spring = useSpring(motionValue, { damping: 60, stiffness: 100 });
  const isInView = useInView(ref, { once: true, margin: '0px' });

  useEffect(() => {
    if (!isInView) return;
    const t = setTimeout(() => motionValue.set(direction === 'down' ? startValue : value), delay * 1000);
    return () => clearTimeout(t);
  }, [motionValue, isInView, delay, value, direction, startValue]);

  useEffect(() => spring.on('change', (latest) => {
    if (ref.current) {
      ref.current.textContent = Intl.NumberFormat('en-US', {
        minimumFractionDigits: decimalPlaces,
        maximumFractionDigits: decimalPlaces,
      }).format(Number(latest.toFixed(decimalPlaces))) + suffix;
    }
  }), [spring, decimalPlaces, suffix]);

  return <span ref={ref} className={cn('inline-block tracking-wider tabular-nums', className)} {...props}>{startValue}{suffix}</span>;
}

/* ─────────────────────────── ShimmerButton ──────────────────────── */
export const ShimmerButton = React.forwardRef(({
  shimmerColor = '#ffffff', shimmerSize = '0.05em', shimmerDuration = '3s',
  borderRadius = '100px', background = 'rgba(0, 0, 0, 1)', className, children, ...props
}, ref) => (
  <button
    ref={ref}
    style={{
      '--spread': '90deg', '--shimmer-color': shimmerColor, '--radius': borderRadius,
      '--speed': shimmerDuration, '--cut': shimmerSize, '--bg': background,
      borderRadius, background,
    }}
    className={cn(
      'group relative z-0 flex cursor-pointer items-center justify-center overflow-hidden border border-white/10 px-6 py-3 whitespace-nowrap text-white',
      'transform-gpu transition-transform duration-300 ease-in-out active:translate-y-px',
      className,
    )}
    {...props}
  >
    <div className="-z-30 blur-[2px] absolute inset-0 overflow-visible [container-type:size]">
      <div className="animate-shimmer-slide absolute inset-0 h-[100cqh] aspect-square">
        <div className="animate-spin-around absolute -inset-full w-auto rotate-0"
          style={{ background: 'conic-gradient(from calc(270deg - (var(--spread) * 0.5)), transparent 0, var(--shimmer-color) var(--spread), transparent var(--spread))' }} />
      </div>
    </div>
    {children}
    <div className={cn(
      'absolute inset-0 size-full rounded-2xl px-4 py-1.5 text-sm font-medium',
      'shadow-[inset_0_-8px_10px_#ffffff1f]',
      'transform-gpu transition-all duration-300 ease-in-out',
      'group-hover:shadow-[inset_0_-6px_10px_#ffffff3f]',
      'group-active:shadow-[inset_0_-10px_10px_#ffffff3f]',
    )} />
    <div className="absolute -z-20" style={{ inset: 'var(--cut)', borderRadius, background }} />
  </button>
));
ShimmerButton.displayName = 'ShimmerButton';

/* ─────────────────────── CardHoverSpotlight ─────────────────────── */
export const CardHoverSpotlight = ({ children, className, radius = 350, color = '#60a5fa' }) => {
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const onMove = ({ currentTarget, clientX, clientY }) => {
    const { left, top } = currentTarget.getBoundingClientRect();
    mouseX.set(clientX - left); mouseY.set(clientY - top);
  };
  return (
    <div onMouseMove={onMove} className={cn('group/spot relative overflow-hidden rounded-xl', className)}>
      <motion.div
        className="pointer-events-none absolute -inset-px rounded-xl opacity-0 transition duration-300 group-hover/spot:opacity-100"
        style={{ background: useMotionTemplate`radial-gradient(${radius}px circle at ${mouseX}px ${mouseY}px, ${color}33, transparent 80%)` }}
      />
      <div className="relative z-10">{children}</div>
    </div>
  );
};

/* ─────────────────────────── BentoGrid ──────────────────────────── */
export const BentoGrid = ({ className, children }) => (
  <div className={cn('mx-auto grid max-w-7xl grid-cols-1 gap-4 md:auto-rows-[18rem] md:grid-cols-3', className)}>
    {children}
  </div>
);
export const BentoGridItem = ({ className, title, description, header, icon }) => (
  <div className={cn(
    'group/bento row-span-1 flex flex-col justify-between space-y-4 rounded-xl border p-5 transition duration-200',
    'border-neutral-200 bg-white hover:shadow-lg',
    'dark:border-white/10 dark:bg-white/[0.03] dark:hover:border-white/25',
    className,
  )}>
    {header}
    <div className="transition duration-200 group-hover/bento:translate-x-1">
      {icon}
      <div className="mt-2 mb-1 font-semibold text-neutral-800 dark:text-white">{title}</div>
      <div className="text-sm leading-relaxed text-neutral-600 dark:text-neutral-300">{description}</div>
    </div>
  </div>
);

/* ─────────────────────── ContainerScroll ─────────────────────── */
export const ContainerScroll = ({ titleComponent, children }) => {
  const containerRef = useRef(null);
  // Scroll progress: 0 when section bottom enters viewport, 1 when section is centered.
  // This way the frame is fully flat & at rest while the user is actually looking at it.
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'center center'],
  });
  const [isMobile, setIsMobile] = useState(false);
  useEffect(() => {
    const c = () => setIsMobile(window.innerWidth <= 768);
    c(); window.addEventListener('resize', c);
    return () => window.removeEventListener('resize', c);
  }, []);
  const rotate = useTransform(scrollYProgress, [0, 1], [25, 0]);
  const scale  = useTransform(scrollYProgress, [0, 1], isMobile ? [0.75, 0.95] : [0.92, 1]);
  const translate = useTransform(scrollYProgress, [0, 1], [40, 0]);
  return (
    <div className="relative flex items-center justify-center p-2 md:p-10 h-[40rem] md:h-[52rem]" ref={containerRef}>
      <div className="py-8 md:py-16 w-full relative" style={{ perspective: '1000px' }}>
        <motion.div style={{ translateY: translate }} className="max-w-5xl mx-auto text-center">
          {titleComponent}
        </motion.div>
        <motion.div
          style={{
            rotateX: rotate, scale,
            boxShadow: '0 0 #0000004d, 0 9px 20px #0000004a, 0 37px 37px #00000042, 0 84px 50px #00000026, 0 149px 60px #0000000a',
          }}
          className="max-w-5xl mt-6 mx-auto h-[26rem] md:h-[36rem] w-full border-[6px] border-neutral-800 dark:border-[#3a3a3a] p-2 md:p-4 bg-neutral-900 dark:bg-[#222] rounded-[28px] shadow-2xl"
        >
          <div className="h-full w-full overflow-hidden rounded-2xl bg-gray-100 dark:bg-zinc-900 md:rounded-2xl">
            {children}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

/* ────────────────────────── AnimatedBeam ────────────────────────── */
export const AnimatedBeam = ({
  className, containerRef, fromRef, toRef,
  curvature = 0, reverse = false, duration = 4, delay = 0,
  pathColor = 'gray', pathWidth = 2, pathOpacity = 0.2,
  gradientStartColor = '#60a5fa', gradientStopColor = '#a855f7',
  startXOffset = 0, startYOffset = 0, endXOffset = 0, endYOffset = 0,
}) => {
  const id = useId();
  const [pathD, setPathD] = useState('');
  const [dims, setDims] = useState({ width: 0, height: 0 });
  const gradient = reverse
    ? { x1: ['90%', '-10%'], x2: ['100%', '0%'], y1: ['0%', '0%'], y2: ['0%', '0%'] }
    : { x1: ['10%', '110%'], x2: ['0%', '100%'],  y1: ['0%', '0%'], y2: ['0%', '0%'] };

  useEffect(() => {
    const update = () => {
      if (!containerRef.current || !fromRef.current || !toRef.current) return;
      const c = containerRef.current.getBoundingClientRect();
      const a = fromRef.current.getBoundingClientRect();
      const b = toRef.current.getBoundingClientRect();
      setDims({ width: c.width, height: c.height });
      const sx = a.left - c.left + a.width / 2 + startXOffset;
      const sy = a.top - c.top + a.height / 2 + startYOffset;
      const ex = b.left - c.left + b.width / 2 + endXOffset;
      const ey = b.top - c.top + b.height / 2 + endYOffset;
      const cy = sy - curvature;
      setPathD(`M ${sx},${sy} Q ${(sx + ex) / 2},${cy} ${ex},${ey}`);
    };
    const ro = new ResizeObserver(update);
    if (containerRef.current) ro.observe(containerRef.current);
    update();
    return () => ro.disconnect();
  }, [containerRef, fromRef, toRef, curvature, startXOffset, startYOffset, endXOffset, endYOffset]);

  return (
    <svg fill="none" width={dims.width} height={dims.height}
      className={cn('pointer-events-none absolute top-0 left-0 transform-gpu stroke-2', className)}
      viewBox={`0 0 ${dims.width} ${dims.height}`}
    >
      <path d={pathD} stroke={pathColor} strokeWidth={pathWidth} strokeOpacity={pathOpacity} strokeLinecap="round" />
      <path d={pathD} strokeWidth={pathWidth} stroke={`url(#${id})`} strokeOpacity="1" strokeLinecap="round" />
      <defs>
        <motion.linearGradient className="transform-gpu" id={id} gradientUnits="userSpaceOnUse"
          initial={{ x1: '0%', x2: '0%', y1: '0%', y2: '0%' }}
          animate={{ x1: gradient.x1, x2: gradient.x2, y1: gradient.y1, y2: gradient.y2 }}
          transition={{ delay, duration, ease: [0.16, 1, 0.3, 1], repeat: Infinity, repeatDelay: 0 }}
        >
          <stop stopColor={gradientStartColor} stopOpacity="0" />
          <stop stopColor={gradientStartColor} />
          <stop offset="32.5%" stopColor={gradientStopColor} />
          <stop offset="100%" stopColor={gradientStopColor} stopOpacity="0" />
        </motion.linearGradient>
      </defs>
    </svg>
  );
};

/* ─────────────────── GradientText (utility) ────────────────────── */
export const GradientText = ({ children, className }) => (
  <span className={cn('bg-gradient-to-br from-blue-400 via-cyan-300 to-purple-400 bg-clip-text text-transparent', className)}>
    {children}
  </span>
);
