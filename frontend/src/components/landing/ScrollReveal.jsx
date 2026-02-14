import { motion } from 'framer-motion';

const directionOffset = {
  up: { y: 40 },
  down: { y: -40 },
  left: { x: 40 },
  right: { x: -40 },
};

const ScrollReveal = ({
  children,
  direction = 'up',
  delay = 0,
  duration = 0.7,
  viewport = 0.15,
  once = true,
  className = '',
}) => {
  const offset = directionOffset[direction] || directionOffset.up;

  return (
    <motion.div
      initial={{ opacity: 0, filter: 'blur(8px)', ...offset }}
      whileInView={{ opacity: 1, filter: 'blur(0px)', x: 0, y: 0 }}
      viewport={{ once, amount: viewport }}
      transition={{
        duration,
        delay,
        ease: [0.25, 0.1, 0.25, 1],
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
};

export default ScrollReveal;
