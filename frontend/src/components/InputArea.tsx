// frontend/src/components/InputArea.tsx
// 输入区域组件

import { motion } from 'framer-motion';
import { Send, Paperclip, Cpu } from 'lucide-react';

interface InputAreaProps {
  inputText: string;
  onInputChange: (text: string) => void;
  onSend: () => void;
  isSending: boolean;
}

const InputArea = ({ inputText, onInputChange, onSend, isSending }: InputAreaProps) => {
  return (
    // 输入区域紧贴容器底部，减少多余间距
    <div className="absolute bottom-0 left-0 right-0 px-4 md:px-0 flex justify-center perspective-[1000px]">
      <motion.div 
        className="w-full max-w-xl bg-white/60 backdrop-blur-2xl rounded-[2rem] shadow-2xl shadow-blue-900/10 border border-white/50 p-2 flex flex-col gap-2 relative overflow-visible"
        initial={{ y: 100, rotateX: 20 }}
        animate={{ y: 0, rotateX: 0 }}
        transition={{ type: "spring", stiffness: 100, damping: 20, delay: 0.2 }}
        whileHover={{ 
          scale: 1.02, 
          boxShadow: "0 25px 50px -12px rgba(56, 189, 248, 0.25)",
          translateY: -5
        }}
      >
        {/* Input Area */}
        <div className="flex items-end gap-2 px-2">
          <motion.button 
            whileHover={{ scale: 1.1, backgroundColor: "rgba(255,255,255,0.8)" }}
            whileTap={{ scale: 0.95 }}
            className="p-3 rounded-full text-slate-400 hover:text-blue-500 transition-colors"
          >
            <Paperclip size={20} />
          </motion.button>

          <textarea 
            value={inputText}
            onChange={(e) => onInputChange(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (!isSending && inputText.trim()) {
                  onSend();
                }
              }
            }}
            placeholder="在极夜中低语..."
            className="flex-1 bg-transparent border-none outline-none resize-none py-3 text-slate-700 placeholder:text-slate-400/60 font-light text-base max-h-32 focus:placeholder:text-slate-300"
            rows={1}
            style={{ minHeight: '44px' }}
            disabled={isSending}
          />

          <motion.button 
            whileHover={!isSending && inputText.trim() ? { scale: 1.1, rotate: 10 } : {}}
            whileTap={!isSending && inputText.trim() ? { scale: 0.9 } : {}}
            onClick={onSend}
            disabled={!inputText.trim() || isSending}
            className={`
              p-3 rounded-full mb-1 shadow-lg transition-all duration-300 relative overflow-hidden
              ${inputText.trim() && !isSending
                ? 'bg-slate-800 text-white shadow-blue-900/20' 
                : 'bg-slate-200 text-slate-400 cursor-not-allowed'}
            `}
          >
            <Send size={18} className="relative z-10" />
            {inputText.trim() && !isSending && (
              <motion.div 
                className="absolute inset-0 bg-gradient-to-r from-blue-600 to-indigo-600"
                animate={{ x: ['-100%', '100%'] }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              />
            )}
          </motion.button>
        </div>

        {/* Bottom Bar: Status */}
        <div className="flex items-center justify-between px-4 pb-1 pt-2 border-t border-slate-200/50">
          <div className="flex items-center gap-2 group cursor-pointer">
            <motion.div 
              className="p-1.5 bg-indigo-50 rounded-full text-indigo-500"
              whileHover={{ rotate: 180 }}
              transition={{ duration: 0.5 }}
            >
              <Cpu size={14} />
            </motion.div>
          </div>

          <div className="flex items-center gap-2 text-[10px] font-mono text-slate-400">
            <span className={`w-1.5 h-1.5 rounded-full ${isSending ? 'bg-blue-400 animate-pulse' : 'bg-emerald-400'} shadow-[0_0_8px_rgba(52,211,153,0.8)]`} />
            <span>{isSending ? '思考中' : 'ONLINE'}</span>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default InputArea;

