/**
 * 主聊天页面 - AETHER UI 风格
 * 集成所有组件，支持深度思考模式和 3D 倾斜效果
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { Box, Cpu, Sparkles, Maximize2, Code, FileText, Menu, X } from 'lucide-react';
import { useChat } from '../hooks/useChat';
import { ChatSession } from '../types';
import { ParticleBackground } from '../components/ui/ParticleBackground';
import { ChatBubble } from '../components/ui/ChatBubble';
import { InputArea } from '../components/composite/InputArea';
import { HistoryPanel } from '../components/composite/HistoryPanel';
import { cn } from '../lib/cn';
import { typographyStyles } from '../styles/typography';

const WELCOME_MESSAGE = {
  id: 'welcome',
  role: 'ai' as const,
  content: '系统在线。神经连接已建立。请问我们今天探索什么领域的知识？',
  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
};

export default function ChatPage() {
  const [inputValue, setInputValue] = useState('');
  const [isDeepThinking, setIsDeepThinking] = useState(false);
  const [activeArtifact, setActiveArtifact] = useState<{
    title: string;
    type: 'code' | 'text';
    content: string;
  } | null>(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [isMobile, setIsMobile] = useState(false);
  // 侧边栏状态：桌面端默认显示，移动端默认隐藏
  const [showSidebar, setShowSidebar] = useState(() => {
    if (typeof window !== 'undefined') {
      return window.innerWidth >= 1024; // lg 断点
    }
    return false;
  });
  const containerRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatAreaRef = useRef<HTMLDivElement>(null);
  const [shouldAutoScroll, setShouldAutoScroll] = useState(true);
  const isUserScrollingRef = useRef(false);

  const {
    messages: chatMessages,
    isSending,
    conversationId,
    sessions,
    sendMessage,
    loadSessions,
    loadConversation,
    createNewConversation,
  } = useChat();

  // 判断是否为空状态
  const isEmptyState = chatMessages.length === 0 && !conversationId;
  const messages = isEmptyState ? [WELCOME_MESSAGE] : chatMessages;

  // 加载会话列表
  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  // 监听窗口大小变化
  useEffect(() => {
    const handleResize = () => {
      const isMobileView = window.innerWidth < 1024;
      setIsMobile(isMobileView);
      // 桌面端默认显示侧边栏，移动端默认隐藏
      if (!isMobileView) {
        setShowSidebar(true);
      } else {
        setShowSidebar(false);
      }
    };

    handleResize(); // 初始化
    window.addEventListener('resize', handleResize);

    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // 3D 倾斜效果
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current) return;
      const { innerWidth, innerHeight } = window;
      const x = (e.clientX - innerWidth / 2) / innerWidth;
      const y = (e.clientY - innerHeight / 2) / innerHeight;
      setMousePos({ x, y });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // 检测用户是否在底部附近（阈值：50px）
  const isNearBottom = useCallback(() => {
    if (!chatAreaRef.current) return true;
    const { scrollTop, scrollHeight, clientHeight } = chatAreaRef.current;
    return scrollHeight - scrollTop - clientHeight < 50;
  }, []);

  // 监听滚动事件，检测用户手动滚动
  useEffect(() => {
    const chatArea = chatAreaRef.current;
    if (!chatArea) return;

    let scrollTimeout: ReturnType<typeof setTimeout>;

    const handleScroll = () => {
      // 清除之前的定时器
      clearTimeout(scrollTimeout);
      
      // 标记用户正在滚动
      isUserScrollingRef.current = true;
      
      // 检查是否接近底部
      const nearBottom = isNearBottom();
      setShouldAutoScroll(nearBottom);

      // 如果用户停止滚动一段时间（300ms），重置滚动标记
      scrollTimeout = setTimeout(() => {
        isUserScrollingRef.current = false;
      }, 300);
    };

    chatArea.addEventListener('scroll', handleScroll, { passive: true });

    return () => {
      chatArea.removeEventListener('scroll', handleScroll);
      clearTimeout(scrollTimeout);
    };
  }, [isNearBottom]);

  // 自动滚动到底部（仅在应该自动滚动时执行）
  useEffect(() => {
    if (shouldAutoScroll && !isUserScrollingRef.current) {
      // 使用 requestAnimationFrame 确保在下一帧执行，避免与滚动事件冲突
      requestAnimationFrame(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      });
    }
  }, [messages, isSending, shouldAutoScroll]);

  // 当发送新消息时，重置自动滚动状态
  useEffect(() => {
    if (isSending) {
      setShouldAutoScroll(true);
    }
  }, [isSending]);

  const handleSend = () => {
    if (!inputValue.trim() || isSending) return;

    sendMessage(inputValue);
    setInputValue('');

    // 模拟生成 Artifact（深度思考模式）
    if (isDeepThinking) {
      setTimeout(() => {
        setActiveArtifact({
          title: 'Analysis_Report.md',
          type: 'text',
          content: `# Analysis Report\n\nGenerated analysis for: "${inputValue}"\n\n## Summary\n\nDetailed analysis content...`,
        });
      }, 1500);
    }
  };

  const handleSelectSession = async (session: ChatSession) => {
    // 只在移动端隐藏侧边栏，桌面端保持显示
    if (isMobile) {
      setShowSidebar(false);
    }
    await loadConversation(session);
  };

  const handleNewConversation = () => {
    // 只在移动端隐藏侧边栏，桌面端保持显示
    if (isMobile) {
      setShowSidebar(false);
    }
    createNewConversation();
    setActiveArtifact(null);
  };

  // 3D 倾斜样式
  const tiltStyle = {
    transform: `perspective(1000px) rotateY(${mousePos.x * 2}deg) rotateX(${mousePos.y * -2}deg)`,
  };

  return (
    <div className="relative w-full h-screen overflow-hidden bg-black text-white font-sans selection:bg-cyan-500/30 flex flex-col">
      {/* 背景层 */}
      <div
        className={cn(
          'absolute inset-0 transition-colors duration-1000',
          isDeepThinking ? 'bg-[#0a0510]' : 'bg-[#020610]'
        )}
      >
        {/* 径向渐变 */}
        <div
          className="absolute w-[800px] h-[800px] rounded-full blur-[120px] opacity-20 transition-all duration-1000"
          style={{
            background: isDeepThinking
              ? 'radial-gradient(circle, #ffd700, #4b0082)'
              : 'radial-gradient(circle, #00ffff, #0000ff)',
            top: '50%',
            left: '50%',
            transform: `translate(-50%, -50%) translate(${mousePos.x * -30}px, ${mousePos.y * -30}px)`,
          }}
        />
      </div>

      {/* 粒子背景 */}
      <ParticleBackground isDeepThinking={isDeepThinking} />

      {/* 主玻璃容器 */}
      <div
        ref={containerRef}
        className="relative z-10 flex flex-1 w-full min-h-0 pt-4 sm:pt-6 px-0 pb-0 gap-2 sm:gap-3 transition-transform duration-100 ease-out overflow-hidden"
        style={tiltStyle}
      >
        {/* 左侧：历史会话面板 */}
        {/* 桌面端：始终显示；移动端：通过 showSidebar 控制 */}
        {!isMobile && (
          <div className="hidden md:block">
            <HistoryPanel
              sessions={sessions}
              activeSessionId={conversationId}
              onSelectSession={handleSelectSession}
              onNewConversation={handleNewConversation}
              isDeepThinking={isDeepThinking}
            />
          </div>
        )}

            {/* 移动端侧边栏遮罩和面板 */}
        {showSidebar && isMobile && (
          <>
            {/* 遮罩层 */}
            <div
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 md:hidden"
              onClick={() => setShowSidebar(false)}
            />
            {/* 侧边栏 - 从右侧滑出，不挡住聊天内容 */}
            <div className="fixed right-0 top-0 h-screen w-72 sm:w-80 bg-black/95 backdrop-blur-xl border-l border-white/10 z-50 md:hidden overflow-y-auto shadow-2xl">
              {/* 关闭按钮 */}
              <div className="sticky top-0 p-4 border-b border-white/10 bg-black/50 backdrop-blur-sm flex items-center justify-between">
                <span className={cn('text-xs sm:text-sm font-bold tracking-widest uppercase', typographyStyles.textSecondary)}>
                  Memory Log
                </span>
                <button
                  onClick={() => setShowSidebar(false)}
                  className="p-1.5 hover:bg-white/10 rounded-lg transition-colors"
                >
                  <X size={18} />
                </button>
              </div>
              {/* 聊天记录列表 */}
              <div className="p-4">
                <HistoryPanel
                  sessions={sessions}
                  activeSessionId={conversationId}
                  onSelectSession={handleSelectSession}
                  onNewConversation={handleNewConversation}
                  isDeepThinking={isDeepThinking}
                />
              </div>
            </div>
          </>
        )}

        {/* 移动端侧边栏切换按钮 */}
        <button
          onClick={() => setShowSidebar(!showSidebar)}
          className={cn(
            'fixed right-4 top-4 z-30 p-2.5 sm:p-3 rounded-lg backdrop-blur-xl border transition-all duration-300',
            isDeepThinking
              ? 'bg-yellow-500/20 border-yellow-500/30 text-yellow-400 hover:bg-yellow-500/30'
              : 'bg-cyan-500/20 border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/30',
            'md:hidden'
          )}
          aria-label="切换聊天记录"
          title="聊天记录"
        >
          <Menu size={18} className="sm:size-[20px]" />
        </button>

        {/* 中间：主界面 */}
        <div className="flex-1 flex flex-col backdrop-blur-2xl bg-black/40 border border-white/10 rounded-xl sm:rounded-3xl shadow-2xl relative overflow-hidden">
          {/* 聊天区域 - flex-1 填满所有可用空间 */}
          <div ref={chatAreaRef} className="flex-1 overflow-y-auto px-3 sm:px-6 pt-3 sm:pt-6 pb-0 custom-scrollbar relative">
            {/* 装饰性网格线 */}
            <div
              className="absolute inset-0 pointer-events-none opacity-[0.03]"
              style={{
                backgroundImage:
                  'linear-gradient(rgba(255,255,255,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.5) 1px, transparent 1px)',
                backgroundSize: '40px 40px',
              }}
            />

            {messages.map((msg) => (
              <ChatBubble
                key={msg.id}
                message={msg}
                isDeepThinking={isDeepThinking}
              />
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* 输入区域 - 与 Deep Think 按钮同一行 */}
          <div className="flex-shrink-0 border-t border-white/5 flex items-center gap-2 sm:gap-4 px-2 sm:px-4 pt-2 sm:pt-3 pb-0 m-0">
            {/* 深度思考切换 - 移到输入框同一行 */}
            <div
              onClick={() => setIsDeepThinking(!isDeepThinking)}
              className={cn(
                'cursor-pointer group flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-1.5 sm:py-2 rounded-full border transition-all duration-500 text-xs sm:text-sm flex-shrink-0',
                isDeepThinking
                  ? 'border-yellow-500/50 bg-yellow-500/10 shadow-[0_0_20px_rgba(234,179,8,0.2)]'
                  : 'border-white/10 hover:border-cyan-500/50 bg-transparent'
              )}
            >
              <Cpu
                size={14}
                className={cn(
                  'transition-all duration-500 sm:size-[16px]',
                  isDeepThinking ? 'text-yellow-400 rotate-180' : 'text-white group-hover:text-cyan-400'
                )}
              />
              <span
                className={cn(
                  'hidden sm:inline font-semibold uppercase tracking-wider transition-colors duration-500 text-[10px]',
                  isDeepThinking ? 'text-yellow-400' : 'text-white group-hover:text-cyan-400'
                )}
              >
                Deep Think
              </span>
            </div>
            
            {/* 输入框 */}
            <div className="flex-1 relative">
              <InputArea
                inputText={inputValue}
                onInputChange={setInputValue}
                onSend={handleSend}
                isSending={isSending}
                isDeepThinking={isDeepThinking}
              />
            </div>
          </div>
        </div>

        {/* 右侧：Artifact 面板 */}
        <div
          className={cn(
            'hidden xl:flex flex-col w-60 xl:w-80 backdrop-blur-xl border border-white/10 rounded-2xl xl:rounded-3xl overflow-hidden shadow-2xl transition-all duration-500',
            activeArtifact
              ? 'translate-x-0 opacity-100'
              : 'translate-x-10 opacity-50 grayscale',
            isDeepThinking ? 'bg-yellow-900/5' : 'bg-cyan-900/5'
          )}
        >
          <div className="p-3 sm:p-5 border-b border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles
                size={14}
                className={cn('sm:size-[16px]', isDeepThinking ? 'text-yellow-400' : 'text-cyan-400')}
              />
              <span className="text-xs sm:text-sm font-bold tracking-widest uppercase">Artifact</span>
            </div>
                  <Maximize2 size={12} className={cn('sm:size-[14px] cursor-pointer transition-opacity', typographyStyles.textTertiary, 'hover:text-white/80')} />
          </div>

          <div className="flex-1 p-3 sm:p-5 overflow-y-auto custom-scrollbar relative">
            {!activeArtifact ? (
              <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-4 sm:p-6 opacity-30">
                <Box size={36} className="sm:size-[48px] mb-4 animate-bounce-slow" />
                <p className="text-xs sm:text-sm">Waiting for output generation...</p>
              </div>
            ) : (
              <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
                <div className="flex items-center gap-2 mb-4">
                  {activeArtifact.type === 'code' ? (
                    <Code size={14} className="sm:size-[16px] text-pink-400" />
                  ) : (
                    <FileText size={14} className="sm:size-[16px]" />
                  )}
                  <span className="text-xs font-mono text-pink-300 bg-pink-500/10 px-2 py-0.5 rounded break-words">
                    {activeArtifact.title}
                  </span>
                </div>
                <div className="bg-black/40 rounded-lg p-3 sm:p-4 font-mono text-xs border border-white/5 shadow-inner text-white overflow-x-auto">
                  <pre className="break-words whitespace-pre-wrap">{activeArtifact.content}</pre>
                </div>

                <div className="mt-6 space-y-3">
                  <div className="h-1 w-full bg-white/10 rounded-full overflow-hidden">
                    <div
                      className={cn(
                        'h-full w-2/3 rounded-full animate-pulse',
                        isDeepThinking ? 'bg-yellow-500' : 'bg-cyan-500'
                      )}
                    />
                  </div>
                  <div className="flex justify-between text-[8px] sm:text-[10px] uppercase tracking-widest" style={{color: 'rgba(255, 255, 255, 0.6)'}}>
                    <span>Stability: 98%</span>
                    <span>Complexity: High</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* 底部按钮 */}
          <div className="p-3 sm:p-5 border-t border-white/5">
            <button
              type="button"
              className={cn(
                'w-full py-2 sm:py-3 rounded-xl font-bold text-xs sm:text-sm uppercase tracking-wider transition-all duration-300 relative overflow-hidden group',
                isDeepThinking
                  ? 'bg-yellow-500/10 text-yellow-400 hover:bg-yellow-500 hover:text-black'
                  : 'bg-cyan-500/10 text-cyan-400 hover:bg-cyan-500 hover:text-black'
              )}
            >
              <span className="relative z-10">Export Artifact</span>
              <div className="absolute inset-0 translate-y-full group-hover:translate-y-0 transition-transform duration-300 bg-current opacity-20" />
            </button>
          </div>
        </div>
      </div>

      {/* 全局样式 */}
      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
          height: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.02);
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.2);
        }
        
        @keyframes bounce-slow {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-10px); }
        }
        .animate-bounce-slow {
          animation: bounce-slow 3s infinite ease-in-out;
        }
      `}</style>
    </div>
  );
}
