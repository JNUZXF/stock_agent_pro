// frontend/src/components/MessageBubble.tsx
// 消息气泡组件

import { motion } from 'framer-motion';
import { Message } from '../types';
import AuroraLoader from './AuroraLoader';
import MarkdownContent from './MarkdownContent';

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble = ({ message }: MessageBubbleProps) => {
  const isAi = message.role === 'ai';
  
  return (
    <motion.div
      // 不再动画 filter，避免 Framer Motion 在插值时产生负的 blur 半径
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: "spring", stiffness: 100, damping: 15 }}
      className={`relative flex w-full mb-8 ${isAi ? 'justify-start' : 'justify-end'}`}
    >
      <motion.div 
        whileHover={{ scale: 1.01 }}
        className={`
          relative px-6 py-4 max-w-[85%] rounded-2xl backdrop-blur-xl border transition-all duration-300
          ${isAi 
            ? 'bg-white/60 text-white rounded-tl-none border-white/60' 
            : 'bg-gradient-to-br from-[#E0F2FE]/80 to-[#F0F9FF]/80 text-white rounded-tr-none border-blue-100/50'
          }
        `}
        style={{
          boxShadow: isAi 
            ? '0 8px 32px -4px rgba(148, 163, 184, 0.1)' 
            : '0 8px 32px -4px rgba(56, 189, 248, 0.15)',
        }}
      >
        {/* AI消息使用Markdown渲染，用户消息使用纯文本 */}
        {isAi ? (
          <div className="text-sm font-light leading-relaxed tracking-wide">
            <MarkdownContent content={message.content} />
          </div>
        ) : (
          <div className="text-sm font-light leading-relaxed tracking-wide whitespace-pre-wrap">
            {message.content}
          </div>
        )}
        
        {message.isTyping && (
           <div className="mt-2">
             <AuroraLoader />
           </div>
        )}

        <div className="absolute bottom-1 right-3 text-[10px] text-white font-mono opacity-60 flex items-center gap-1">
          {message.timestamp}
          {!isAi && <span className="block w-1 h-1 rounded-full bg-blue-400" />}
        </div>
      </motion.div>
    </motion.div>
  );
};

export default MessageBubble;

