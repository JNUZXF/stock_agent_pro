import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Archive, Plus, Menu, X } from 'lucide-react';
import { useChat } from '../hooks/useChat';
import { Message, ChatSession } from '../types';
import ClaudeMessageBubble from '../components/ClaudeMessageBubble';
import ClaudeInputArea from '../components/ClaudeInputArea';
import ArcticBackground from '../components/Background';

const WELCOME_MESSAGE: Message = {
  id: 'welcome',
  role: 'ai',
  content: '你好！我是你的专业股票分析助手。我可以帮你分析股票数据、生成详细的分析报告。\n\n你可以这样问我：\n- 分析一下 SZ000001 这只股票\n- 帮我查看特斯拉的最新走势\n- 对比一下苹果和微软的表现',
  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
};

export default function ChatPage() {
  const [inputText, setInputText] = useState('');
  const [activeSession, setActiveSession] = useState<ChatSession | null>(null);
  // 桌面端默认显示侧边栏，移动端默认隐藏
  const [showSidebar, setShowSidebar] = useState(() => {
    // 使用媒体查询判断是否为桌面端
    if (typeof window !== 'undefined') {
      return window.innerWidth >= 1024; // lg断点
    }
    return false;
  });
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

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

  // 判断是否为首次使用（无消息状态）
  const isEmptyState = chatMessages.length === 0 && !conversationId;

  // 显示的消息列表
  const messages = isEmptyState ? [WELCOME_MESSAGE] : chatMessages;

  // 加载会话列表
  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  // 同步 activeSession
  useEffect(() => {
    if (conversationId) {
      const session = sessions.find(s => s.id === conversationId);
      setActiveSession(session || null);
    } else {
      setActiveSession(null);
    }
  }, [conversationId, sessions]);

  // 监听窗口大小变化，自动调整侧边栏显示状态
  useEffect(() => {
    const handleResize = () => {
      // 桌面端（lg及以上）默认显示，移动端默认隐藏
      if (window.innerWidth >= 1024) {
        setShowSidebar(true);
      } else {
        setShowSidebar(false);
      }
    };

    window.addEventListener('resize', handleResize);
    // 初始化时也检查一次
    handleResize();

    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // 自动滚动到底部（平滑滚动）
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isSending]);

  const handleSend = () => {
    if (!inputText.trim() || isSending) return;
    sendMessage(inputText);
    setInputText('');
  };

  const handleSelectSession = async (session: ChatSession) => {
    setActiveSession(session);
    setShowSidebar(false);
    await loadConversation(session);
  };

  const handleNewConversation = () => {
    setActiveSession(null);
    setShowSidebar(false);
    createNewConversation();
  };

  return (
    <div className="relative w-full h-screen bg-gradient-to-br from-slate-50 to-blue-50 overflow-hidden flex">
      <ArcticBackground />

      {/* 侧边栏 - 历史记录 */}
      {/* 桌面端：始终显示；移动端：通过showSidebar控制 */}
      <AnimatePresence mode="wait">
        {showSidebar && (
          <>
            {/* 遮罩层 - 仅移动端显示 */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowSidebar(false)}
              className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 lg:hidden"
            />

            {/* 侧边栏内容 */}
            <motion.div
              initial={{ x: -320 }}
              animate={{ x: 0 }}
              exit={{ x: -320 }}
              transition={{ type: 'spring', damping: 30, stiffness: 300 }}
              className="fixed left-0 top-0 h-full w-80 bg-white/80 backdrop-blur-xl border-r border-slate-200/50 shadow-2xl z-50 lg:relative lg:z-0 lg:shadow-none lg:border-r lg:border-slate-200/50"
            >
              <div className="flex flex-col h-full p-6">
                {/* 头部 */}
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-2">
                    <Archive className="w-5 h-5 text-indigo-600" />
                    <h2 className="text-lg font-bold text-slate-800">历史会话</h2>
                  </div>
                  <button
                    onClick={() => setShowSidebar(false)}
                    className="lg:hidden p-2 hover:bg-slate-200/50 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5 text-slate-600" />
                  </button>
                </div>

                {/* 新建会话按钮 */}
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleNewConversation}
                  className="flex items-center gap-3 w-full px-4 py-3 bg-gradient-to-r from-indigo-500 to-purple-500 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all mb-4"
                >
                  <Plus className="w-5 h-5" />
                  新建会话
                </motion.button>

                {/* 会话列表 */}
                <div className="flex-1 overflow-y-auto space-y-2 scrollbar-thin scrollbar-thumb-slate-300 scrollbar-track-transparent">
                  {sessions.length === 0 ? (
                    <div className="text-center text-slate-400 text-sm mt-8">
                      暂无历史会话
                    </div>
                  ) : (
                    sessions.map((session) => (
                      <motion.button
                        key={session.id}
                        whileHover={{ scale: 1.02, x: 4 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => handleSelectSession(session)}
                        className={`w-full text-left p-4 rounded-xl transition-all ${
                          activeSession?.id === session.id
                            ? 'bg-indigo-100 border-2 border-indigo-300'
                            : 'bg-white/50 hover:bg-white/80 border-2 border-transparent'
                        }`}
                      >
                        <div className="font-semibold text-slate-800 mb-1 truncate">
                          {session.title}
                        </div>
                        <div className="text-xs text-slate-500 mb-2">{session.date}</div>
                        <div className="text-sm text-slate-600 line-clamp-2">
                          {session.summary}
                        </div>
                      </motion.button>
                    ))
                  )}
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* 主聊天区域 */}
      <div className="flex-1 flex flex-col relative z-10">
        {/* 顶部工具栏 */}
        <div className="flex items-center justify-between px-6 py-4 bg-white/60 backdrop-blur-xl border-b border-slate-200/50">
          <div className="flex items-center gap-3">
            {/* 移动端菜单按钮 */}
            <button
              onClick={() => setShowSidebar(!showSidebar)}
              className="lg:hidden p-2 hover:bg-slate-200/50 rounded-lg transition-colors"
            >
              {showSidebar ? <X className="w-5 h-5 text-slate-600" /> : <Menu className="w-5 h-5 text-slate-600" />}
            </button>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-500 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <div className="font-bold text-slate-800">Stock Agent Pro</div>
                <div className="text-xs text-slate-500">AI 股票分析助手</div>
              </div>
            </div>
          </div>
        </div>

        {/* 聊天内容区域 */}
        <div
          ref={chatContainerRef}
          className="flex-1 overflow-y-auto"
        >
          {/* 空状态 - 欢迎界面（中心化显示） */}
          {isEmptyState ? (
            <div className="h-full flex items-center justify-center px-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="max-w-2xl text-center"
              >
                {/* Logo */}
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: 'spring', duration: 0.8, delay: 0.2 }}
                  className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-r from-indigo-500 to-purple-500 flex items-center justify-center shadow-2xl"
                >
                  <Sparkles className="w-10 h-10 text-white" />
                </motion.div>

                {/* 欢迎文字 */}
                <h1 className="text-4xl font-black text-slate-800 mb-4">
                  你好，我是
                  <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 to-purple-500">
                    {' '}Stock Agent{' '}
                  </span>
                </h1>
                <p className="text-lg text-slate-600 mb-8 leading-relaxed">
                  {WELCOME_MESSAGE.content}
                </p>

                {/* 示例问题卡片 */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
                  {[
                    '分析 SZ000001',
                    '贵州茅台怎么样',
                    '给出立讯精密的报告',
                    '分析歌尔股份',
                  ].map((example, idx) => (
                    <motion.button
                      key={idx}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.4 + idx * 0.1 }}
                      whileHover={{ scale: 1.05, y: -2 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setInputText(example)}
                      className="p-4 bg-white/80 backdrop-blur-sm rounded-xl border-2 border-slate-200 hover:border-indigo-300 hover:bg-indigo-50/50 transition-all text-left"
                    >
                      <div className="text-sm font-medium text-slate-700">{example}</div>
                    </motion.button>
                  ))}
                </div>
              </motion.div>
            </div>
          ) : (
            // 有消息时 - Claude 风格布局（消息从中心开始）
            <div className="max-w-3xl mx-auto px-6 py-8">
              <AnimatePresence mode="popLayout">
                {messages.map((msg, index) => (
                  <ClaudeMessageBubble
                    key={msg.id}
                    message={msg}
                    isFirst={index === 0}
                  />
                ))}
              </AnimatePresence>
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* 输入区域 */}
        <ClaudeInputArea
          inputText={inputText}
          onInputChange={setInputText}
          onSend={handleSend}
          isSending={isSending}
        />
      </div>
    </div>
  );
}
