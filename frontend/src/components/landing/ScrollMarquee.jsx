import { useRef } from 'react';
import {
  motion,
  useAnimationFrame,
  useMotionValue,
  useScroll,
  useSpring,
  useTransform,
  useVelocity,
} from 'framer-motion';

function wrap(min, max, v) {
  const range = max - min;
  return ((((v - min) % range) + range) % range) + min;
}

const ScrollMarquee = ({
  children,
  baseVelocity = -2,
  scrollDependent = true,
  className = '',
}) => {
  const baseX = useMotionValue(0);
  const { scrollY } = useScroll();
  const scrollVelocity = useVelocity(scrollY);
  const smoothVelocity = useSpring(scrollVelocity, { damping: 50, stiffness: 400 });
  const velocityFactor = useTransform(smoothVelocity, [0, 1000], [0, 5], { clamp: false });

  const directionFactor = useRef(1);

  useAnimationFrame((_, delta) => {
    let moveBy = directionFactor.current * baseVelocity * (delta / 1000);

    if (scrollDependent) {
      if (velocityFactor.get() < 0) {
        directionFactor.current = -1;
      } else if (velocityFactor.get() > 0) {
        directionFactor.current = 1;
      }
      moveBy += directionFactor.current * moveBy * velocityFactor.get();
    }

    baseX.set(baseX.get() + moveBy);
  });

  const x = useTransform(baseX, (v) => `${wrap(-25, 0, v)}%`);

  return (
    <div className={`marquee-wrapper ${className}`} style={{ overflow: 'hidden' }}>
      <motion.div
        style={{ x, display: 'flex', whiteSpace: 'nowrap', gap: '2rem' }}
      >
        {/* Repeat content 4 times for seamless loop */}
        {[0, 1, 2, 3].map((i) => (
          <span key={i} style={{ display: 'flex', gap: '2rem', flexShrink: 0 }}>
            {children}
          </span>
        ))}
      </motion.div>
    </div>
  );
};

export default ScrollMarquee;
