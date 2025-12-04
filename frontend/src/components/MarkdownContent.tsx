// frontend/src/components/MarkdownContent.tsx
// Markdown内容渲染组件，支持代码高亮和GFM语法

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import rehypeRaw from 'rehype-raw';
import 'highlight.js/styles/github-dark.css';

interface MarkdownContentProps {
  content: string;
}

const MarkdownContent = ({ content }: MarkdownContentProps) => {
  return (
    <div className="markdown-content prose prose-slate max-w-none prose-headings:font-semibold prose-headings:text-slate-800 prose-h1:text-2xl prose-h2:text-xl prose-h3:text-lg prose-h4:text-base prose-p:text-slate-700 prose-p:leading-relaxed prose-a:text-blue-600 prose-a:no-underline hover:prose-a:underline prose-strong:text-slate-900 prose-strong:font-semibold prose-em:text-slate-700 prose-code:text-sm prose-code:bg-slate-100 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:font-mono prose-code:text-blue-700 prose-pre:bg-slate-900 prose-pre:border prose-pre:border-slate-700 prose-pre:rounded-lg prose-pre:p-4 prose-pre:overflow-x-auto prose-ul:list-disc prose-ul:pl-6 prose-ol:list-decimal prose-ol:pl-6 prose-li:text-slate-700 prose-li:my-1 prose-blockquote:border-l-4 prose-blockquote:border-blue-300 prose-blockquote:pl-4 prose-blockquote:italic prose-blockquote:text-slate-600 prose-table:w-full prose-table:border-collapse prose-th:bg-slate-100 prose-th:border prose-th:border-slate-300 prose-th:px-4 prose-th:py-2 prose-th:text-left prose-th:font-semibold prose-td:border prose-td:border-slate-300 prose-td:px-4 prose-td:py-2 prose-hr:border-slate-300">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeRaw, rehypeHighlight]}
        components={{
          // 自定义代码块样式
          code({ className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || '');
            const isInline = !match;
            return isInline ? (
              <code className="bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded text-sm font-mono" {...props}>
                {children}
              </code>
            ) : (
              <div className="relative group my-4">
                <div className="absolute top-2 right-2 text-xs text-slate-400 font-mono opacity-0 group-hover:opacity-100 transition-opacity z-10">
                  {match[1]}
                </div>
                <code className={`${className} block bg-slate-900 text-slate-100 rounded-lg p-4 overflow-x-auto text-sm`} {...props}>
                  {children}
                </code>
              </div>
            );
          },
          // 自定义表格样式
          table({ children }: any) {
            return (
              <div className="overflow-x-auto my-4">
                <table className="min-w-full border-collapse border border-slate-300 rounded-lg overflow-hidden">
                  {children}
                </table>
              </div>
            );
          },
          // 自定义链接样式
          a({ href, children }: any) {
            return (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-700 underline transition-colors"
              >
                {children}
              </a>
            );
          },
          // 自定义引用块样式
          blockquote({ children }: any) {
            return (
              <blockquote className="border-l-4 border-blue-400 pl-4 my-4 italic text-slate-600 bg-blue-50/50 py-2 rounded-r">
                {children}
              </blockquote>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownContent;

