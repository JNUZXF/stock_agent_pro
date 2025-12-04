// frontend/src/components/HistoryPanel.tsx
// 历史记录面板组件

import { motion } from 'framer-motion';
import { Wind } from 'lucide-react';
import { ChatSession } from '../types';

interface HistoryPanelProps {
  sessions: ChatSession[];
  activeSession: ChatSession | null;
  onSelectSession: (session: ChatSession) => void;
  onNewConversation?: () => void;
}

const HistoryPanel = ({ sessions, activeSession, onSelectSession, onNewConversation }: HistoryPanelProps) => {
  return (
    <motion.div 
      className="hidden md:flex flex-col absolute left-[4%] top-[12%] bottom-[18%] w-64 z-10"
      initial={{ opacity: 0, x: -50, rotateY: 15 }}
      animate={{ 
        opacity: 1, 
        x: 0, 
        rotateY: 15,
        y: [0, -8, 0]
      }}
      transition={{ 
        opacity: { duration: 0.8 },
        y: { duration: 6, repeat: Infinity, ease: "easeInOut" }
      }}
      style={{ transformStyle: 'preserve-3d' }}
    >
      <div className="flex items-center gap-3 mb-4 pl-4 group">
        <div className="p-2 bg-white/40 backdrop-blur-md rounded-lg shadow-sm border border-white/50 group-hover:rotate-180 transition-transform duration-700">
          <Wind size={20} className="text-slate-600" />
        </div>
        <span className="text-lg font-light tracking-widest text-slate-600 uppercase group-hover:text-blue-500 transition-colors">Archive</span>
      </div>

      {/* 新建会话按钮 */}
      {onNewConversation && (
        <motion.button
          onClick={onNewConversation}
          className="mx-4 mb-4 px-4 py-2 bg-white/40 backdrop-blur-md rounded-xl border border-white/50 text-sm font-medium text-slate-700 hover:bg-white/60 hover:border-blue-200 transition-all duration-300"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          + 新建会话
        </motion.button>
      )}

      <div className="flex-1 space-y-4 overflow-y-auto scrollbar-none pr-4 py-2 mask-image-b-fade">
        {sessions.map((session, idx) => (
          <motion.div
            key={session.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 * idx }}
            onClick={() => onSelectSession(session)}
            className={`
              group relative p-4 rounded-xl cursor-pointer transition-all duration-500
              border backdrop-blur-md overflow-hidden
              ${activeSession?.id === session.id 
                ? 'bg-white/60 border-blue-200 shadow-lg shadow-blue-100/50 translate-x-4' 
                : 'bg-white/10 border-white/20 hover:bg-white/30 hover:border-white/40 hover:translate-x-1'
              }
            `}
          >
            <div className="relative z-10">
              <div className="text-[10px] text-slate-400 mb-1 font-mono tracking-tighter uppercase">{session.date}</div>
              <div className="text-sm font-medium text-slate-700 group-hover:text-blue-600 transition-colors line-clamp-1">
                {session.title}
              </div>
            </div>
            
            {activeSession?.id === session.id && (
              <motion.div 
                layoutId="active-glow"
                className="absolute inset-0 bg-gradient-to-r from-blue-50 to-transparent opacity-50 z-0"
              />
            )}
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

export default HistoryPanel;

