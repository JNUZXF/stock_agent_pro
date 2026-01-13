/**
 * 粒子背景组件 - AETHER UI 风格
 * 使用 HTML5 Canvas 实现神经网络效果
 */

import { useEffect, useRef } from 'react';
import { cn } from '../../../lib/cn';

export interface ParticleBackgroundProps {
  /**
   * 是否为深度思考模式（影响颜色和速度）
   */
  isDeepThinking?: boolean;
  /**
   * 自定义类名
   */
  className?: string;
}

export const ParticleBackground = ({ 
  isDeepThinking = false,
  className 
}: ParticleBackgroundProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let particles: Particle[] = [];

    // 配置参数
    const config = {
      particleCount: 60,
      connectionDistance: 150,
      baseSpeed: isDeepThinking ? 0.2 : 0.5,
      color: isDeepThinking ? '255, 215, 0' : '0, 255, 255', // Gold vs Cyan
    };

    // 调整画布大小
    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    // 粒子类
    class Particle {
      x: number;
      y: number;
      vx: number;
      vy: number;
      size: number;

      constructor() {
        if (!canvas) {
          // 如果 canvas 不存在，使用默认值
          this.x = 0;
          this.y = 0;
          this.vx = 0;
          this.vy = 0;
          this.size = 0;
          return;
        }
        this.x = Math.random() * (canvas as HTMLCanvasElement).width;
        this.y = Math.random() * (canvas as HTMLCanvasElement).height;
        this.vx = (Math.random() - 0.5) * config.baseSpeed;
        this.vy = (Math.random() - 0.5) * config.baseSpeed;
        this.size = Math.random() * 2 + 1;
      }

      update() {
        if (!canvas) return;
        this.x += this.vx;
        this.y += this.vy;

        // 边界反弹
        if (this.x < 0 || this.x > (canvas as HTMLCanvasElement).width) this.vx *= -1;
        if (this.y < 0 || this.y > (canvas as HTMLCanvasElement).height) this.vy *= -1;
      }

      draw() {
        if (!ctx) return;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${config.color}, ${isDeepThinking ? 0.6 : 0.4})`;
        ctx.fill();
      }
    }

    // 初始化粒子
    const init = () => {
      if (!canvas) return;
      particles = [];
      for (let i = 0; i < config.particleCount; i++) {
        particles.push(new Particle());
      }
    };

    // 动画循环
    const animate = () => {
      if (!ctx || !canvas) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // 绘制连接线
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < config.connectionDistance) {
            ctx.beginPath();
            ctx.strokeStyle = `rgba(${config.color}, ${1 - distance / config.connectionDistance})`;
            ctx.lineWidth = 0.5;
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }

      // 更新和绘制粒子
      particles.forEach(p => {
        p.update();
        p.draw();
      });

      animationFrameId = requestAnimationFrame(animate);
    };

    // 初始化
    window.addEventListener('resize', resize);
    resize();
    init();
    animate();

    // 清理
    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(animationFrameId);
    };
  }, [isDeepThinking]);

  return (
    <canvas
      ref={canvasRef}
      className={cn(
        'absolute top-0 left-0 w-full h-full pointer-events-none z-0',
        className
      )}
    />
  );
};
