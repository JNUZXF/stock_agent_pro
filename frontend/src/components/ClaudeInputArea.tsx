import { motion } from 'framer-motion';
import { Send, Loader2 } from 'lucide-react';
import { KeyboardEvent } from 'react';

interface ClaudeInputAreaProps {
  inputText: string;
  onInputChange: (text: string) => void;
  onSend: () => void;
  isSending: boolean;
}

export default function ClaudeInputArea({
  inputText,
  onInputChange,
  onSend,
  isSending,
}: ClaudeInputAreaProps) {
  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isSending && inputText.trim()) {
        onSend();
      }
    }
  };

  return (
    <div className="border-t border-slate-200/50 bg-white/60 backdrop-blur-xl">
      <div className="max-w-3xl mx-auto px-6 py-4">
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="relative"
        >
          {/* 输入框容器 */}
          <div className="relative flex items-end gap-3 p-3 bg-white rounded-2xl border-2 border-slate-200 focus-within:border-indigo-400 focus-within:shadow-lg focus-within:shadow-indigo-500/20 transition-all">
            {/* 文本输入框 */}
            <textarea
              value={inputText}
              onChange={(e) => onInputChange(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="输入你的问题... (Shift + Enter 换行)"
              disabled={isSending}
              rows={1}
              className="flex-1 resize-none bg-transparent text-slate-800 placeholder-slate-400 focus:outline-none min-h-[24px] max-h-[200px] leading-6 py-1"
              style={{
                scrollbarWidth: 'thin',
              }}
              onInput={(e) => {
                const target = e.target as HTMLTextAreaElement;
                target.style.height = 'auto';
                target.style.height = Math.min(target.scrollHeight, 200) + 'px';
              }}
            />

            {/* 发送按钮 */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={onSend}
              disabled={!inputText.trim() || isSending}
              className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center transition-all ${
                inputText.trim() && !isSending
                  ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg hover:shadow-xl hover:shadow-indigo-500/50'
                  : 'bg-slate-200 text-slate-400 cursor-not-allowed'
              }`}
            >
              {isSending ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                >
                  <Loader2 className="w-5 h-5" />
                </motion.div>
              ) : (
                <Send className="w-5 h-5" />
              )}
            </motion.button>
          </div>

          {/* 提示文字 */}
          <div className="flex items-center justify-between mt-2 px-1">
            <div className="text-xs text-slate-400">
              {isSending ? (
                <span className="flex items-center gap-2">
                  <motion.span
                    animate={{ opacity: [1, 0.5, 1] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  >
                    AI 正在思考...
                  </motion.span>
                </span>
              ) : (
                <span>按 Enter 发送，Shift + Enter 换行</span>
              )}
            </div>
            <div className="text-xs text-slate-400">
              {inputText.length > 0 && `${inputText.length} 字符`}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
