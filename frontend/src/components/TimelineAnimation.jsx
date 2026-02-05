import { motion, useInView } from 'framer-motion';
import { useRef } from 'react';

const TimelineAnimation = ({
  children,
  animationNum,
  timelineRef,
  className = '',
  customVariants,
  once = true,
  ...props
}) => {
  const defaultSequenceVariants = {
    visible: (i) => ({
      filter: 'blur(0px)',
      y: 0,
      opacity: 1,
      transition: {
        delay: i * 0.3,
        duration: 0.6,
        ease: 'easeOut'
      },
    }),
    hidden: {
      filter: 'blur(10px)',
      y: 30,
      opacity: 0,
    },
  };

  const sequenceVariants = customVariants || defaultSequenceVariants;

  const isInView = useInView(timelineRef, { once });

  return (
    <motion.div
      initial="hidden"
      animate={isInView ? 'visible' : 'hidden'}
      custom={animationNum}
      variants={sequenceVariants}
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  );
};

export default TimelineAnimation;
