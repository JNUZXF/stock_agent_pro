/**
 * 历史会话面板组件 - AETHER UI 风格
 */

import { Layers, MoreHorizontal, Home } from 'lucide-react';
import { Link } from 'react-router-dom';
import { cn } from '../../../lib/cn';
import { ChatSession } from '../../../types';
import { typographyStyles } from '../../../styles/typography';

export interface HistoryPanelProps {
  /**
   * 会话列表
   */
  sessions: ChatSession[];
  /**
   * 当前激活的会话ID
   */
  activeSessionId?: string | null;
  /**
   * 选择会话回调
   */
  onSelectSession: (session: ChatSession) => void;
  /**
   * 新建会话回调
   */
  onNewConversation: () => void;
  /**
   * 是否为深度思考模式
   */
  isDeepThinking?: boolean;
  /**
   * 自定义类名
   */
  className?: string;
}

export const HistoryPanel = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewConversation,
  isDeepThinking = false,
  className,
}: HistoryPanelProps) => {
  return (
    <div
      className={cn(
        'flex flex-col w-64 backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl overflow-hidden shadow-2xl transition-all hover:bg-white/10 group',
        className
      )}
    >
      {/* 头部 */}
      <div className="p-5 border-b border-white/5 flex items-center gap-3 justify-between">
        <div className="flex items-center gap-3">
          <Layers size={18} className="text-cyan-400" />
          <span className={cn('text-sm font-bold tracking-widest uppercase', typographyStyles.textSecondary)}>
            Memory Log
          </span>
        </div>
        {/* 回到首页按钮 - 在侧边栏头部 */}
        <Link
          to="/"
          className={cn(
            'p-2 rounded-lg transition-all duration-300 hover:bg-white/10',
            'text-cyan-400 hover:text-cyan-300'
          )}
          title="回到首页"
        >
          <Home size={16} />
        </Link>
      </div>

      {/* 会话列表 */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2 custom-scrollbar">
        {sessions.length === 0 ? (
          <div className={cn('text-center text-sm mt-8', typographyStyles.textTertiary)}>
            No sessions yet
          </div>
        ) : (
          sessions.map((session) => (
            <div
              key={session.id}
              onClick={() => onSelectSession(session)}
              className={cn(
                'p-3 rounded-xl hover:bg-white/5 cursor-pointer transition-all duration-300 group/item border border-transparent hover:border-white/10',
                activeSessionId === session.id && 'bg-white/10 border-white/20'
              )}
            >
              <div className={cn('text-xs mb-1 flex items-center gap-2', typographyStyles.textMain)}>
                <div
                  className={cn(
                    'w-1.5 h-1.5 rounded-full transition-all',
                    isDeepThinking
                      ? 'bg-yellow-500 group-hover/item:shadow-[0_0_8px_rgba(255,215,0,0.8)]'
                      : 'bg-cyan-500 group-hover/item:shadow-[0_0_8px_rgba(0,255,255,0.8)]'
                  )}
                />
                Session #{session.id.slice(-6)}
              </div>
              <div className="text-sm truncate group-hover/item:opacity-100 group-hover/item:translate-x-1 transition-transform" style={{opacity: 0.8}}>
                {session.title || 'Untitled Session'}
              </div>
            </div>
          ))
        )}
      </div>

      {/* 底部操作 */}
      <div className="p-4 border-t border-white/5 bg-black/20">
        <button
          type="button"
          onClick={onNewConversation}
          className={cn('flex items-center gap-2 text-xs transition-opacity w-full', typographyStyles.textTertiary, 'hover:text-white/80')}
        >
          <MoreHorizontal size={14} />
          <span>New Session</span>
        </button>
      </div>
    </div>
  );
};
