/**
 * Markdown内容黑色系主题样式系统 - AETHER UI
 * 为深色背景优化，确保所有元素在黑色主题下的高可读性
 * 包含响应式设计支持
 */

export const markdownStyles = {
  // ============ 标题样式 ============
  h1: 'text-xl sm:text-2xl font-bold mb-3 sm:mb-4 text-white tracking-wide',
  h2: 'text-lg sm:text-xl font-bold mb-2 sm:mb-3 text-white/95 mt-3 sm:mt-4',
  h3: 'text-base sm:text-lg font-semibold mb-2 text-white/90 mt-2 sm:mt-3',
  h4: 'text-sm sm:text-base font-semibold mb-1 sm:mb-2 text-white/85 mt-2',
  h5: 'text-xs sm:text-sm font-semibold mb-1 text-white/80 mt-2',
  h6: 'text-xs sm:text-sm font-medium mb-1 text-white/75 mt-2',

  // ============ 段落和文本 ============
  paragraph: 'text-white/90 mb-3 sm:mb-4 leading-relaxed text-sm sm:text-base',
  text: 'text-white/90 text-sm sm:text-base',
  
  // ============ 列表样式（最重要的部分）============
  // 有序列表项
  ol_item: 'text-white/85 ml-4 sm:ml-6 mb-2 list-decimal list-inside text-sm sm:text-base',
  // 无序列表项
  ul_item: 'text-white/85 ml-4 sm:ml-6 mb-2 list-disc list-inside text-sm sm:text-base',
  // 列表项文本
  list_text: 'text-white/85 inline-block ml-1 sm:ml-2 text-sm sm:text-base',
  
  // ============ 强调和引用 ============
  strong: 'font-bold text-white',
  em: 'italic text-white/90',
  code_inline: 'text-cyan-300 bg-cyan-500/15 px-1.5 py-0.5 rounded font-mono text-xs sm:text-sm break-words',
  blockquote: 'border-l-4 border-cyan-500/50 pl-3 sm:pl-4 py-2 text-white/75 italic bg-cyan-500/5 my-3 sm:my-4 text-sm sm:text-base',

  // ============ 代码块 ============
  code_block: 'bg-gray-900/50 border border-white/10 rounded-lg p-3 sm:p-4 overflow-x-auto my-3 sm:my-4 text-xs sm:text-sm',
  code_block_text: 'text-white/90 font-mono text-xs sm:text-sm',

  // ============ 表格 ============
  table: 'border-collapse w-full my-3 sm:my-4 text-xs sm:text-sm overflow-x-auto block',
  table_header: 'bg-cyan-500/10 border border-white/10',
  table_header_cell: 'px-2 sm:px-4 py-2 text-white font-semibold text-left border border-white/10 text-xs sm:text-sm',
  table_row: 'border-b border-white/5',
  table_cell: 'px-2 sm:px-4 py-2 text-white/85 border border-white/10 bg-black/20 text-xs sm:text-sm',
  
  // ============ 水平线 ============
  hr: 'border-t border-white/20 my-4 sm:my-6',

  // ============ 链接 ============
  link: 'text-cyan-400 hover:text-cyan-300 hover:underline transition-colors break-words',
  link_visited: 'text-cyan-500/70',

  // ============ 图片 ============
  image: 'max-w-full h-auto rounded-lg my-3 sm:my-4 border border-white/10',
  image_caption: 'text-center text-white/60 text-xs sm:text-sm mt-2 italic',

} as const;

/**
 * 获取基于模式的Markdown样式
 */
export function getMarkdownStylesByMode(): typeof markdownStyles {
  // 如果需要根据模式返回不同的样式，可以在这里扩展
  // 目前两种模式使用相同的样式系统
  return markdownStyles;
}

/**
 * 列表项CSS类生成器
 * @param depth 列表嵌套深度 (0-3)
 * @param isOrdered 是否为有序列表
 */
export function getListItemClass(depth: number = 0, isOrdered: boolean = false): string {
  const baseMargin = 24; // 每层6px * 4
  const currentMargin = depth * 6;
  const marginLeft = baseMargin + currentMargin;
  
  const listType = isOrdered ? 'list-decimal' : 'list-disc';
  const colorClass = depth > 1 ? 'text-white/75' : 'text-white/85';
  
  return `${listType} list-inside ml-${marginLeft/4} mb-2 ${colorClass}`;
}
