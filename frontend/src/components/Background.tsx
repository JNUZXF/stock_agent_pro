// frontend/src/components/Background.tsx
// 动态背景组件，包含极光效果和视差动画

import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';
import { useEffect } from 'react';
import SnowParticles from './SnowParticles';

const useParallax = (sensitivity: number = 0.05) => {
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const smoothX = useSpring(x, { stiffness: 50, damping: 20 });
  const smoothY = useSpring(y, { stiffness: 50, damping: 20 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const { innerWidth, innerHeight } = window;
      const xPos = (e.clientX - innerWidth / 2) * sensitivity;
      const yPos = (e.clientY - innerHeight / 2) * sensitivity;
      x.set(xPos);
      y.set(yPos);
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [x, y, sensitivity]);

  return { x: smoothX, y: smoothY };
};

const ArcticBackground = () => {
  const { x, y } = useParallax(0.02);
  
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden bg-slate-50">
      {/* Base Sky Gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#F0F4F8] via-[#E6EEF5] to-[#DCE6F0]" />
      
      {/* Dynamic Aurora Curtains (SVG Animation) */}
      <motion.div style={{ x, y }} className="absolute inset-0 opacity-60">
        <svg className="absolute w-full h-full" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="aurora-gradient-1" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="rgba(56, 189, 248, 0)" />
              <stop offset="50%" stopColor="rgba(56, 189, 248, 0.3)" />
              <stop offset="100%" stopColor="rgba(167, 243, 208, 0)" />
            </linearGradient>
            <filter id="blur-filter" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur in="SourceGraphic" stdDeviation="40" />
            </filter>
          </defs>
          
          {/* Wave 1 */}
          <motion.path
            d="M-100,200 Q400,0 900,300 T2000,100 V-200 H-100 Z"
            fill="url(#aurora-gradient-1)"
            filter="url(#blur-filter)"
            animate={{
              d: [
                "M-100,200 Q400,0 900,300 T2000,100 V-200 H-100 Z",
                "M-100,200 Q400,100 900,200 T2000,300 V-200 H-100 Z",
                "M-100,200 Q400,0 900,300 T2000,100 V-200 H-100 Z"
              ]
            }}
            transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
          />
        </svg>
      </motion.div>

      {/* Secondary Aurora Layer */}
      <motion.div 
        style={{ x: useTransform(x, v => v * 1.5), y: useTransform(y, v => v * 1.5) }} 
        className="absolute inset-0 opacity-40"
      >
        <div className="absolute top-[-10%] right-[-20%] w-[80vw] h-[80vw] rounded-full bg-indigo-200/20 blur-[150px] mix-blend-multiply" />
      </motion.div>

      {/* Floating Ice Particles */}
      <SnowParticles />
      
      {/* Texture Overlay */}
      <div className="absolute inset-0 opacity-[0.04] mix-blend-overlay" style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=\'0 0 200 200\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'noiseFilter\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.8\' numOctaves=\'3\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23noiseFilter)\'/%3E%3C/svg%3E")' }}></div>
    </div>
  );
};

export default ArcticBackground;

