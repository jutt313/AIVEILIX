import { motion } from 'framer-motion';

const containerVariants = {
  hidden: {},
  visible: (staggerDelay) => ({
    transition: {
      staggerChildren: staggerDelay,
    },
  }),
};

const wordVariants = {
  hidden: {
    opacity: 0,
    y: 20,
    filter: 'blur(6px)',
  },
  visible: {
    opacity: 1,
    y: 0,
    filter: 'blur(0px)',
    transition: {
      duration: 0.5,
      ease: [0.25, 0.1, 0.25, 1],
    },
  },
};

const letterVariants = {
  hidden: {
    opacity: 0,
    y: 12,
    filter: 'blur(4px)',
  },
  visible: {
    opacity: 1,
    y: 0,
    filter: 'blur(0px)',
    transition: {
      duration: 0.35,
      ease: [0.25, 0.1, 0.25, 1],
    },
  },
};

const TextReveal = ({
  text,
  as: Tag = 'h2',
  letterAnime = false,
  staggerDelay = 0.06,
  className = '',
  once = true,
  viewport = 0.3,
}) => {
  if (letterAnime) {
    const letters = text.split('');
    return (
      <Tag className={className}>
        <motion.span
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once, amount: viewport }}
          custom={staggerDelay}
          style={{ display: 'inline-block' }}
        >
          {letters.map((letter, i) => (
            <motion.span
              key={i}
              variants={letterVariants}
              style={{ display: 'inline-block', whiteSpace: letter === ' ' ? 'pre' : 'normal' }}
            >
              {letter}
            </motion.span>
          ))}
        </motion.span>
      </Tag>
    );
  }

  const words = text.split(' ');
  return (
    <Tag className={className}>
      <motion.span
        variants={containerVariants}
        initial="hidden"
        whileInView="visible"
        viewport={{ once, amount: viewport }}
        custom={staggerDelay}
        style={{ display: 'inline-flex', flexWrap: 'wrap', justifyContent: 'center', gap: '0 0.3em' }}
      >
        {words.map((word, i) => (
          <motion.span
            key={i}
            variants={wordVariants}
            style={{ display: 'inline-block' }}
          >
            {word}
          </motion.span>
        ))}
      </motion.span>
    </Tag>
  );
};

export default TextReveal;
