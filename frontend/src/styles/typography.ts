/**
 * 排版和文字颜色系统 - AETHER UI
 * 中心化管理所有文字样式，确保一致的可读性和美观性
 * 
 * 使用指南：
 * - 主文本：textMain（默认白色，完全不透明）
 * - 次级文本：textSecondary（略降低的对比度）
 * - 辅助文本：textTertiary（更低的对比度）
 * - 禁用文本：textDisabled（最低对比度）
 * - 强调文本：textHighlight（带颜色强调）
 */

export const typographyStyles = {
  // ============ 文字颜色类 ============
  
  // 主文本 - 清晰可读的主内容
  textMain: 'text-white',
  textMainOpacity: 'text-white', // 透明度 100%
  
  // 次级文本 - UI标签、说明文字
  textSecondary: 'text-white/80',
  textSecondaryClass: 'opacity-80',
  
  // 辅助文本 - 时间戳、元数据
  textTertiary: 'text-white/60',
  tertiaryClass: 'opacity-60',
  
  // 禁用文本 - 不可交互的元素
  textDisabled: 'text-white/40',
  disabledClass: 'opacity-40',
  
  // 非常淡 - 装饰性文本
  textFaint: 'text-white/30',
  faintClass: 'opacity-30',
  
  // ============ 彩色文本 ============
  
  // Cyan 主题色（正常模式）
  textCyan: 'text-cyan-400',
  textCyanDim: 'text-cyan-500/70',
  textCyanBright: 'text-cyan-300',
  
  // Yellow/Gold 主题色（深度思考模式）
  textGold: 'text-yellow-400',
  textGoldDim: 'text-yellow-500/70',
  textGoldBright: 'text-yellow-300',
  
  // 功能性颜色
  textSuccess: 'text-green-400',
  textWarning: 'text-amber-400',
  textError: 'text-red-400',
  textInfo: 'text-blue-400',
  
  // ============ 特殊用途 ============
  
  // 代码文本
  textCode: 'text-cyan-300',
  textCodeBg: 'bg-cyan-500/20',
  
  // 链接
  textLink: 'text-cyan-400 hover:text-cyan-300',
  
  // 标签/徽章
  textLabel: 'text-pink-300',
  
  // ============ 组合样式 ============
  
  // 消息时间戳
  messageTimestamp: 'text-xs text-white/60 opacity-60',
  
  // 聊天气泡中的消息
  chatMessage: 'text-sm md:text-base font-light tracking-wide leading-relaxed text-white',
  
  // 输入框占位符
  inputPlaceholder: 'placeholder-white/30',
  
  // 按钮文字
  buttonText: 'text-xs font-semibold uppercase tracking-wider',
  
  // 页面标题
  pageTitle: 'text-lg font-bold tracking-wider text-white',
  
  // 小标题/标签
  label: 'text-sm font-bold tracking-widest uppercase text-white/80',
  
  // 描述文本
  description: 'text-sm text-white/70',
  
  // ============ Tailwind 类名辅助 ============
  
  // 用于需要动态应用的场景
  baseTextClasses: 'text-white font-light tracking-wide',
  
  // 可访问性增强
  highContrast: 'text-white font-medium',
  
} as const;

/**
 * 获取基于模式的文本颜色
 */
export function getTextColorByMode(mode: 'normal' | 'deep', intensity: 'main' | 'secondary' | 'tertiary' = 'main'): string {
  if (mode === 'normal') {
    if (intensity === 'main') return typographyStyles.textCyan;
    if (intensity === 'secondary') return typographyStyles.textCyanDim;
    return typographyStyles.textCyanBright;
  } else {
    if (intensity === 'main') return typographyStyles.textGold;
    if (intensity === 'secondary') return typographyStyles.textGoldDim;
    return typographyStyles.textGoldBright;
  }
}

/**
 * 预定义的文本样式组合
 */
export const textVariants = {
  // 主标题
  h1: 'text-4xl font-bold tracking-tight text-white',
  // 副标题
  h2: 'text-2xl font-semibold tracking-wide text-white',
  // 小标题
  h3: 'text-lg font-semibold text-white',
  // 正文
  body: 'text-base font-light leading-relaxed text-white',
  // 小字
  small: 'text-sm text-white/80',
  // 超小字
  tiny: 'text-xs text-white/60',
  // 代码块
  code: 'text-sm font-mono text-cyan-300',
} as const;
