/**
 * Markdown 内容渲染组件
 * 封装 react-markdown 和相关插件
 */

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import rehypeRaw from 'rehype-raw';
import 'highlight.js/styles/github-dark.css';
import { cn } from '../../../lib/cn';
import { typographyStyles } from '../../../styles/typography';

export interface MarkdownContentProps {
  /**
   * Markdown 内容
   */
  content: string;
  /**
   * 自定义类名
   */
  className?: string;
}

export const MarkdownContent = ({ content, className }: MarkdownContentProps) => {
  return (
    <div className={cn('markdown-content prose prose-slate max-w-none prose-headings:text-white prose-p:text-white/90 prose-a:text-cyan-400 prose-strong:text-white prose-code:text-cyan-300 prose-pre:bg-gray-900/50 prose-pre:border prose-pre:border-white/10 prose-pre:p-0 prose-pre:overflow-x-auto overflow-x-hidden', className)}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight, rehypeRaw]}
        components={{
          code({ className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || '');
            const isInline = !match;
            return isInline ? (
              <code className={cn('bg-cyan-500/20 rounded text-xs sm:text-sm font-mono px-1.5 py-0.5 break-words', typographyStyles.textCode)} {...props}>
                {children}
              </code>
            ) : (
              <code className={cn(className, 'block bg-gray-900/50 text-white rounded-lg p-3 sm:p-4 overflow-x-auto text-xs sm:text-sm border border-white/10')} {...props}>
                {children}
              </code>
            );
          },
          // 自定义列表项样式
          li({ children }: any) {
            return (
              <li className="text-white/85 ml-0 mb-2 text-sm sm:text-base">
                {children}
              </li>
            );
          },
          // 自定义表格容器
          table({ children }: any) {
            return (
              <div className="overflow-x-auto my-3 sm:my-4 rounded-lg border border-white/10">
                <table className="min-w-full border-collapse">
                  {children}
                </table>
              </div>
            );
          },
          // 自定义表格单元格
          td({ children }: any) {
            return (
              <td className="text-white/85 border border-white/10 px-2 sm:px-4 py-2 bg-black/20 text-xs sm:text-sm break-words">
                {children}
              </td>
            );
          },
          // 自定义表格头
          th({ children }: any) {
            return (
              <th className="bg-cyan-500/10 text-white font-semibold border border-white/10 px-2 sm:px-4 py-2 text-left text-xs sm:text-sm">
                {children}
              </th>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};
