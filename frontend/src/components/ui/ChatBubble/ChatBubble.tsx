/**
 * 聊天消息气泡组件 - AETHER UI 风格
 * 使用 CVA 管理样式变体
 */

import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { Sparkles } from 'lucide-react';
import { cn } from '../../../lib/cn';
import { Message } from '../../../types';
import { MarkdownContent } from '../../composite/MarkdownContent';
import { typographyStyles } from '../../../styles/typography';

const chatBubbleVariants = cva(
  'relative max-w-[80%] p-4 rounded-2xl backdrop-blur-md transition-all duration-500 border border-white/10 shadow-lg hover:shadow-cyan-500/20 hover:scale-[1.01]',
  {
    variants: {
      variant: {
        ai: 'bg-gradient-to-br from-gray-900/80 to-gray-800/80 rounded-tl-none text-white',
        user: 'bg-gradient-to-br from-cyan-500/10 to-blue-600/10 rounded-tr-none text-white',
      },
    },
    defaultVariants: {
      variant: 'ai',
    },
  }
);

const glowDotVariants = cva(
  'absolute -left-1 -top-1 w-2 h-2 rounded-full',
  {
    variants: {
      mode: {
        normal: 'bg-cyan-400 shadow-[0_0_10px_rgba(0,255,255,0.8)]',
        deep: 'bg-yellow-400 shadow-[0_0_10px_rgba(255,215,0,0.8)]',
      },
    },
    defaultVariants: {
      mode: 'normal',
    },
  }
);

export interface ChatBubbleProps extends VariantProps<typeof chatBubbleVariants> {
  /**
   * 消息对象
   */
  message: Message;
  /**
   * 是否为深度思考模式
   */
  isDeepThinking?: boolean;
  /**
   * 自定义类名
   */
  className?: string;
}

export const ChatBubble = React.forwardRef<HTMLDivElement, ChatBubbleProps>(
  ({ message, isDeepThinking = false, className }, ref) => {
    const isAi = message.role === 'ai';

    return (
      <div
        ref={ref}
        className={cn(
          'flex w-full mb-6',
          isAi ? 'justify-start' : 'justify-end',
          'group',
          className
        )}
      >
        <div className={cn(chatBubbleVariants({ variant: isAi ? 'ai' : 'user' }))}>
          {/* AI 消息的发光点 */}
          {isAi && (
            <div
              className={cn(
                glowDotVariants({ mode: isDeepThinking ? 'deep' : 'normal' })
              )}
            />
          )}

          {/* 消息内容 */}
          <div className="font-light tracking-wide leading-relaxed text-sm md:text-base">
            {isAi ? (
              <MarkdownContent content={message.content} />
            ) : (
              <div className="whitespace-pre-wrap break-words">
                {message.content}
              </div>
            )}
          </div>

          {/* 元数据页脚 */}
          <div className={cn('flex items-center justify-end gap-2 mt-2', typographyStyles.messageTimestamp)}>
            {isAi && isDeepThinking && (
              <Sparkles size={10} className="text-yellow-400 animate-pulse" />
            )}
            <span>{message.timestamp}</span>
          </div>
        </div>
      </div>
    );
  }
);

ChatBubble.displayName = 'ChatBubble';
