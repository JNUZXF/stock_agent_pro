// frontend/src/components/AuroraLoader.tsx
// 极光风格的加载指示器

import { motion } from 'framer-motion';

const AuroraLoader = () => (
  <div className="flex items-center gap-1 h-6 px-2">
    {[0, 1, 2].map((i) => (
      <motion.div
        key={i}
        className="w-1.5 h-1.5 rounded-full bg-gradient-to-tr from-blue-400 to-emerald-300"
        animate={{
          y: [-2, 4, -2],
          opacity: [0.4, 1, 0.4],
          scale: [0.8, 1.2, 0.8]
        }}
        transition={{
          duration: 1.2,
          repeat: Infinity,
          delay: i * 0.2,
          ease: "easeInOut"
        }}
      />
    ))}
  </div>
);

export default AuroraLoader;

