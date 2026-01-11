import { motion } from 'framer-motion';
import { Message } from '../types';
import { User, Sparkles } from 'lucide-react';
import MarkdownContent from './MarkdownContent';
import { useState, useEffect } from 'react';

interface ClaudeMessageBubbleProps {
  message: Message;
  isFirst?: boolean;
}

// 打字机效果组件
const TypewriterText = ({ content, speed = 20 }: { content: string; speed?: number }) => {
  const [displayedContent, setDisplayedContent] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (currentIndex < content.length) {
      const timeout = setTimeout(() => {
        setDisplayedContent(prev => prev + content[currentIndex]);
        setCurrentIndex(prev => prev + 1);
      }, speed);

      return () => clearTimeout(timeout);
    }
  }, [currentIndex, content, speed]);

  return <MarkdownContent content={displayedContent} />;
};

export default function ClaudeMessageBubble({ message, isFirst }: ClaudeMessageBubbleProps) {
  const isUser = message.role === 'user';
  const isTyping = message.isTyping;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{
        duration: 0.4,
        type: 'spring',
        stiffness: 300,
        damping: 30
      }}
      className={`mb-8 ${isFirst ? 'mt-8' : ''}`}
    >
      <div className={`flex gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start`}>
        {/* 头像 */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', delay: 0.1 }}
          className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center shadow-lg ${
            isUser
              ? 'bg-gradient-to-br from-blue-500 to-blue-600'
              : 'bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500'
          }`}
        >
          {isUser ? (
            <User className="w-5 h-5 text-white" />
          ) : (
            <Sparkles className="w-5 h-5 text-white" />
          )}
        </motion.div>

        {/* 消息内容 */}
        <div className={`flex-1 ${isUser ? 'text-right' : 'text-left'} max-w-[85%]`}>
          {/* 发送者名称 */}
          <div className={`text-xs font-semibold mb-2 ${isUser ? 'text-blue-600' : 'text-indigo-600'}`}>
            {isUser ? '你' : 'Stock Agent'}
          </div>

          {/* 消息气泡 */}
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.1 }}
            className={`relative inline-block max-w-full ${
              isUser
                ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-3xl rounded-tr-md'
                : 'bg-white/90 backdrop-blur-sm text-slate-800 rounded-3xl rounded-tl-md border border-slate-200/50 shadow-lg'
            } px-6 py-4`}
          >
            {/* 用户消息 - 普通文本 */}
            {isUser ? (
              <div className="leading-relaxed whitespace-pre-wrap break-words">
                {message.content}
              </div>
            ) : (
              // AI 消息 - Markdown 渲染 + 打字机效果
              <div className="prose prose-slate max-w-none">
                {isTyping ? (
                  <TypewriterText content={message.content} speed={15} />
                ) : (
                  <MarkdownContent content={message.content} />
                )}
              </div>
            )}

            {/* 加载中的闪烁光标 */}
            {!isUser && isTyping && (
              <motion.span
                animate={{ opacity: [1, 0, 1] }}
                transition={{ duration: 1, repeat: Infinity }}
                className="inline-block w-1 h-4 bg-indigo-500 ml-1"
              />
            )}

            {/* 时间戳 */}
            <div
              className={`text-xs mt-2 ${
                isUser ? 'text-blue-100' : 'text-slate-400'
              }`}
            >
              {message.timestamp}
            </div>

            {/* AI 消息的装饰性渐变边框 */}
            {!isUser && (
              <motion.div
                className="absolute inset-0 rounded-3xl rounded-tl-md bg-gradient-to-r from-indigo-500/20 via-purple-500/20 to-pink-500/20 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"
                initial={false}
              />
            )}
          </motion.div>

          {/* AI 思考中动画 */}
          {!isUser && isTyping && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center gap-2 mt-2 text-xs text-indigo-500"
            >
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
              >
                <Sparkles className="w-3 h-3" />
              </motion.div>
              <span>正在思考...</span>
            </motion.div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
