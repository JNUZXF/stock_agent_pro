/**
 * 文字颜色快速参考
 * 将此文件导入到任何组件中，快速获取标准化的文字颜色类
 * 
 * 使用方式：
 * import { typographyStyles } from '@/styles/typography';
 * 
 * <div className={typographyStyles.textMain}>主文本</div>
 * <div className={typographyStyles.textSecondary}>次级文本</div>
 * <div className={typographyStyles.messageTimestamp}>时间戳</div>
 */

// ============ 导入示例 ============

// 在你的组件文件顶部添加：
// import { typographyStyles, getTextColorByMode, textVariants } from '@/styles/typography';
// import { colorSchemes } from '@/styles';

// ============ 常用场景速查表 ============

// 场景 1: 消息气泡中的时间戳
// <span className={typographyStyles.messageTimestamp}>12:34 PM</span>

// 场景 2: 聊天消息内容
// <div className={typographyStyles.chatMessage}>
//   {message.content}
// </div>

// 场景 3: 输入框占位符
// <input 
//   className={typographyStyles.inputPlaceholder}
//   placeholder="输入消息..."
// />

// 场景 4: 按钮文本
// <button className={typographyStyles.buttonText}>发送</button>

// 场景 5: 页面标题
// <h1 className={typographyStyles.pageTitle}>聊天</h1>

// 场景 6: 小标签
// <span className={typographyStyles.label}>Memory Log</span>

// 场景 7: 描述文本
// <p className={typographyStyles.description}>这是一个描述</p>

// 场景 8: 彩色强调文本（正常模式）
// <span className={typographyStyles.textCyan}>主题色文本</span>

// 场景 9: 彩色强调文本（深度模式）
// <span className={typographyStyles.textGold}>深度模式文本</span>

// 场景 10: 代码文本
// <code className={typographyStyles.textCode}>const x = 1;</code>

// ============ 动态模式选择 ============

// 根据模式获取文本颜色（在组件中使用）
// const textColor = getTextColorByMode(isDeepThinking ? 'deep' : 'normal', 'main');
// <span className={textColor}>动态颜色文本</span>

// ============ 完整的颜色方案 ============

// 正常模式配置
// const scheme = colorSchemes.normal;
// {
//   text: 'text-white',           // 主文本
//   textSecondary: 'text-white/80', // 次级文本
//   textTertiary: 'text-white/60',  // 辅助文本
//   accent: 'text-cyan-400',       // 强调色
//   accentDim: 'text-cyan-500/70',  // 淡化强调色
//   bg: 'bg-cyan-500/10',          // 背景
//   border: 'border-cyan-500/50',  // 边框
//   shadow: 'shadow-cyan-500/20',  // 阴影
// }

// 深度模式配置
// const scheme = colorSchemes.deep;
// {
//   text: 'text-white',           // 主文本
//   textSecondary: 'text-white/80', // 次级文本
//   textTertiary: 'text-white/60',  // 辅助文本
//   accent: 'text-yellow-400',     // 强调色
//   accentDim: 'text-yellow-500/70', // 淡化强调色
//   bg: 'bg-yellow-500/10',        // 背景
//   border: 'border-yellow-500/50', // 边框
//   shadow: 'shadow-yellow-500/20', // 阴影
// }

// ============ 完整颜色映射表 ============

const TYPOGRAPHY_REFERENCE = {
  // 文字透明度等级（从清晰到模糊）
  opacity_levels: {
    main: '100%',       // text-white
    secondary: '80%',   // text-white/80
    tertiary: '60%',    // text-white/60
    disabled: '40%',    // text-white/40
    faint: '30%',       // text-white/30
  },

  // 颜色变体
  color_variants: {
    white: {
      base: 'text-white',
      // 可以与透明度组合：text-white/80
    },
    cyan: {
      base: 'text-cyan-400',
      dim: 'text-cyan-500/70',
      bright: 'text-cyan-300',
    },
    gold: {
      base: 'text-yellow-400',
      dim: 'text-yellow-500/70',
      bright: 'text-yellow-300',
    },
    semantic: {
      success: 'text-green-400',
      warning: 'text-amber-400',
      error: 'text-red-400',
      info: 'text-blue-400',
    },
  },

  // 预定义组合
  predefined_combinations: {
    message_timestamp: 'text-xs text-white/60 opacity-60',
    chat_message: 'text-sm md:text-base font-light tracking-wide leading-relaxed text-white',
    button_text: 'text-xs font-semibold uppercase tracking-wider',
    page_title: 'text-lg font-bold tracking-wider text-white',
    label: 'text-sm font-bold tracking-widest uppercase text-white/80',
    description: 'text-sm text-white/70',
    code: 'text-sm font-mono text-cyan-300',
  },
};

export default TYPOGRAPHY_REFERENCE;
