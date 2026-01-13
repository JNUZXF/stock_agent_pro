/**
 * 输入区域组件 - AETHER UI 风格
 * 支持深度思考模式切换
 */

import { KeyboardEvent } from 'react';
import { Send, UploadCloud } from 'lucide-react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../../lib/cn';
import { typographyStyles } from '../../../styles/typography';

const inputAreaVariants = cva(
  'relative flex items-end gap-3 p-2 pr-3 rounded-2xl border transition-all duration-300',
  {
    variants: {
      mode: {
        normal: 'bg-white/5 border-white/10 focus-within:border-cyan-500/50 focus-within:bg-white/10 focus-within:shadow-[0_0_20px_rgba(6,182,212,0.1)]',
        deep: 'bg-yellow-900/10 border-yellow-500/30 shadow-[0_0_30px_rgba(234,179,8,0.1)]',
      },
    },
    defaultVariants: {
      mode: 'normal',
    },
  }
);

const sendButtonVariants = cva(
  'p-3 rounded-xl transition-all duration-300 flex items-center justify-center',
  {
    variants: {
      enabled: {
        true: '',
        false: 'bg-white/5 text-white cursor-not-allowed',
      },
      mode: {
        normal: 'bg-cyan-500 text-black shadow-[0_0_15px_rgba(6,182,212,0.5)] hover:scale-105',
        deep: 'bg-yellow-500 text-black shadow-[0_0_15px_rgba(234,179,8,0.5)] hover:scale-105',
      },
    },
    compoundVariants: [
      {
        enabled: false,
        className: 'bg-white/5 text-white cursor-not-allowed',
      },
    ],
    defaultVariants: {
      enabled: true,
      mode: 'normal',
    },
  }
);

export interface InputAreaProps extends VariantProps<typeof inputAreaVariants> {
  /**
   * 输入框值
   */
  inputText: string;
  /**
   * 输入变化回调
   */
  onInputChange: (text: string) => void;
  /**
   * 发送回调
   */
  onSend: () => void;
  /**
   * 是否正在发送
   */
  isSending?: boolean;
  /**
   * 是否为深度思考模式
   */
  isDeepThinking?: boolean;
  /**
   * 自定义类名
   */
  className?: string;
}

export const InputArea = ({
  inputText,
  onInputChange,
  onSend,
  isSending = false,
  isDeepThinking = false,
  className,
}: InputAreaProps) => {
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isSending && inputText.trim()) {
        onSend();
      }
    }
  };

  const isEnabled = !isSending && !!inputText.trim();

  return (
    <div className={cn('px-0 py-0 bg-gradient-to-t from-black/90 to-black/50', className)}>
      <div className={cn(inputAreaVariants({ mode: isDeepThinking ? 'deep' : 'normal' }), 'mx-2 sm:mx-4 mt-2 sm:mt-3 mb-0')}>
        {/* 上传按钮 */}
        <button
          type="button"
          className="p-2 sm:p-2.5 text-white hover:text-white hover:bg-white/10 rounded-lg sm:rounded-xl transition-colors flex-shrink-0"
          aria-label="上传文件"
        >
          <UploadCloud size={16} className="sm:size-[18px]" />
        </button>

        {/* 文本输入框 */}
        <textarea
          value={inputText}
          onChange={(e) => onInputChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            isDeepThinking
              ? 'Entering complex query into neural cortex...'
              : 'Input command or query...'
          }
          disabled={isSending}
          className={cn('flex-1 bg-transparent border-none outline-none text-white resize-none py-1 sm:py-1.5 min-h-[38px] sm:min-h-[42px] max-h-[100px] custom-scrollbar text-sm sm:text-base', typographyStyles.inputPlaceholder)}
          rows={1}
        />

        {/* 发送按钮 */}
        <button
          type="button"
          onClick={onSend}
          disabled={!isEnabled}
          className={cn(
            sendButtonVariants({
              enabled: isEnabled,
              mode: isDeepThinking ? 'deep' : 'normal',
            }),
            'p-2 sm:p-2.5 flex-shrink-0'
          )}
          aria-label="发送消息"
        >
          <Send
            size={16}
            className={cn('sm:size-[18px]', isEnabled && '-translate-y-0.5 translate-x-0.5')}
          />
        </button>
      </div>
    </div>
  );
};
