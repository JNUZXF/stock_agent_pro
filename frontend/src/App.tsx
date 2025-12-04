// frontend/src/App.tsx
// 主应用组件

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ArcticBackground from './components/Background';
import MessageBubble from './components/MessageBubble';
import InputArea from './components/InputArea';
import HistoryPanel from './components/HistoryPanel';
import { useChat } from './hooks/useChat';
import { Message, ChatSession } from './types';

const INITIAL_MESSAGES: Message[] = [
  { 
    id: 'm1', 
    role: 'ai', 
    content: '欢迎来到股票分析智能体。我是您的专业股票分析助手，可以帮您分析股票数据并生成详细的分析报告。请输入股票代码或问题，例如："分析一下SZ000001这只股票"。', 
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) 
  },
];

function App() {
  const [inputText, setInputText] = useState('');
  const [activeSession, setActiveSession] = useState<ChatSession | null>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  
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

  // 当conversationId变化时，同步activeSession
  useEffect(() => {
    if (conversationId) {
      const session = sessions.find(s => s.id === conversationId);
      setActiveSession(session || null);
    } else {
      setActiveSession(null);
    }
  }, [conversationId, sessions]);

  // 如果有聊天消息则使用，否则显示初始欢迎消息（仅在无会话时）
  const messages = chatMessages.length > 0 ? chatMessages : (conversationId ? [] : INITIAL_MESSAGES);

  // 加载会话列表
  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  // 自动滚动到底部
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages, isSending]);

  const handleSend = () => {
    if (!inputText.trim() || isSending) return;
    sendMessage(inputText);
    setInputText('');
  };

  const handleSelectSession = async (session: ChatSession) => {
    setActiveSession(session);
    await loadConversation(session);
  };

  const handleNewConversation = () => {
    setActiveSession(null);
    createNewConversation();
  };

  return (
    <div className="relative w-full h-screen font-sans text-slate-700 overflow-hidden flex items-center justify-center perspective-[2000px] selection:bg-blue-100 selection:text-blue-900">
      <ArcticBackground />

      {/* 历史记录面板 */}
      <HistoryPanel
        sessions={sessions}
        activeSession={activeSession}
        onSelectSession={handleSelectSession}
        onNewConversation={handleNewConversation}
      />

      {/* 主聊天区域：尽量利用垂直空间显示更多聊天内容 */}
      <motion.div 
        className="relative w-full max-w-3xl h-[100vh] flex flex-col z-20"
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.8 }}
      >
        {/* Chat Area */}
        <div 
          ref={chatContainerRef}
          className="flex-1 overflow-y-auto px-4 md:px-8 pb-24 scrollbar-none"
          style={{ 
            maskImage: 'linear-gradient(to bottom, transparent 0%, black 5%, black 90%, transparent 100%)',
            WebkitMaskImage: 'linear-gradient(to bottom, transparent 0%, black 5%, black 90%, transparent 100%)'
          }}
        >
          {/* 去掉顶部多余的内边距，让消息更贴近顶部显示 */}
          <div className="min-h-full flex flex-col justify-end pt-2">
            <AnimatePresence>
              {messages.map((msg) => (
                <MessageBubble key={msg.id} message={msg} />
              ))}
            </AnimatePresence>
            <div className="h-4" /> 
          </div>
        </div>

        {/* Input Area */}
        <InputArea
          inputText={inputText}
          onInputChange={setInputText}
          onSend={handleSend}
          isSending={isSending}
        />
      </motion.div>
    </div>
  );
}

export default App;

