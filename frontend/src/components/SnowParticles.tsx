// frontend/src/components/SnowParticles.tsx
// 雪花粒子效果组件

import { motion } from 'framer-motion';

const SnowFlake = () => {
  const randomDuration = Math.random() * 10 + 20;
  const randomDelay = Math.random() * 20;
  
  return (
    <motion.div
      className="absolute bg-white rounded-full opacity-60 blur-[0.5px]"
      initial={{
        x: Math.random() * window.innerWidth,
        y: -20,
        scale: Math.random() * 0.4 + 0.2,
      }}
      animate={{
        y: window.innerHeight + 50,
        x: `calc(${Math.random() * 100}vw + ${Math.random() * 200 - 100}px)`,
        opacity: [0, 0.6, 0]
      }}
      transition={{
        duration: randomDuration,
        repeat: Infinity,
        ease: "linear",
        delay: randomDelay,
      }}
      style={{
        width: Math.random() * 4 + 2,
        height: Math.random() * 4 + 2,
      }}
    />
  );
};

const SnowParticles = () => {
  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden z-[5]">
      {[...Array(30)].map((_, i) => (
        <SnowFlake key={i} />
      ))}
    </div>
  );
};

export default SnowParticles;

