/**
 * 样式系统主入口
 * 导出所有设计令牌和样式系统
 */

export { tokens } from './tokens';
export { 
  typographyStyles, 
  getTextColorByMode, 
  textVariants 
} from './typography';
export { globalStyles } from './globals';

// 便利导出：常用的颜色组合
export const colorSchemes = {
  // 正常模式 - Cyan
  normal: {
    text: 'text-white',
    textSecondary: 'text-white/80',
    textTertiary: 'text-white/60',
    accent: 'text-cyan-400',
    accentDim: 'text-cyan-500/70',
    bg: 'bg-cyan-500/10',
    border: 'border-cyan-500/50',
    shadow: 'shadow-cyan-500/20',
  },
  
  // 深度模式 - Gold
  deep: {
    text: 'text-white',
    textSecondary: 'text-white/80',
    textTertiary: 'text-white/60',
    accent: 'text-yellow-400',
    accentDim: 'text-yellow-500/70',
    bg: 'bg-yellow-500/10',
    border: 'border-yellow-500/50',
    shadow: 'shadow-yellow-500/20',
  },
} as const;
