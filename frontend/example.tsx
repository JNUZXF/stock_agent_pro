import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence, useScroll, useTransform, useSpring, useMotionValue } from 'framer-motion';
import { 
  Send, 
  Paperclip, 
  Cpu, 
  Sparkles, 
  History, 
  Maximize2, 
  MoreHorizontal, 
  X,
  Aperture,
  Wind,
  Waves
} from 'lucide-react';

// --- Types & Mock Data ---

interface Message {
  id: string;
  role: 'user' | 'ai';
  content: string;
  timestamp: string;
  isTyping?: boolean;
}

interface ChatSession {
  id: string;
  title: string;
  date: string;
  summary: string;
}

const MOCK_HISTORY: ChatSession[] = [
  { id: '1', title: '极光摄影参数分析', date: '2023-10-24', summary: '讨论了ISO设置与快门速度的平衡，建议使用f/2.8光圈。' },
  { id: '2', title: '特罗姆瑟建筑美学', date: '2023-10-22', summary: '分析了北极大教堂的三角形结构与冰山的隐喻关系。' },
  { id: '3', title: '北欧极简主义设计', date: '2023-10-20', summary: '探讨了留白在UI设计中的重要性。' },
];

const INITIAL_MESSAGES: Message[] = [
  { id: 'm1', role: 'ai', content: '欢迎来到 Arctic Echo。这里的空气很冷，但思维很清晰。我们需要探索什么？', timestamp: '10:00' },
];

// --- Hooks ---

// Hook for mouse parallax effect
const useParallax = (sensitivity: number = 0.05) => {
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const smoothX = useSpring(x, { stiffness: 50, damping: 20 });
  const smoothY = useSpring(y, { stiffness: 50, damping: 20 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const { innerWidth, innerHeight } = window;
      const xPos = (e.clientX - innerWidth / 2) * sensitivity;
      const yPos = (e.clientY - innerHeight / 2) * sensitivity;
      x.set(xPos);
      y.set(yPos);
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [x, y, sensitivity]);

  return { x: smoothX, y: smoothY };
};

// --- Components ---

// 1. Dynamic Background: Aurora Curtains & Parallax
const ArcticBackground = () => {
  const { x, y } = useParallax(0.02); // Slow background movement
  
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden bg-slate-50">
      {/* Base Sky Gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#F0F4F8] via-[#E6EEF5] to-[#DCE6F0]" />
      
      {/* Dynamic Aurora Curtains (SVG Animation) */}
      <motion.div style={{ x, y }} className="absolute inset-0 opacity-60">
        <svg className="absolute w-full h-full" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="aurora-gradient-1" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="rgba(56, 189, 248, 0)" />
              <stop offset="50%" stopColor="rgba(56, 189, 248, 0.3)" />
              <stop offset="100%" stopColor="rgba(167, 243, 208, 0)" />
            </linearGradient>
            <filter id="blur-filter" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur in="SourceGraphic" stdDeviation="40" />
            </filter>
          </defs>
          
          {/* Wave 1 */}
          <motion.path
            d="M-100,200 Q400,0 900,300 T2000,100 V-200 H-100 Z"
            fill="url(#aurora-gradient-1)"
            filter="url(#blur-filter)"
            animate={{
              d: [
                "M-100,200 Q400,0 900,300 T2000,100 V-200 H-100 Z",
                "M-100,200 Q400,100 900,200 T2000,300 V-200 H-100 Z",
                "M-100,200 Q400,0 900,300 T2000,100 V-200 H-100 Z"
              ]
            }}
            transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
          />
        </svg>
      </motion.div>

      {/* Secondary Aurora Layer (Purple/Pink hint) */}
      <motion.div 
        style={{ x: useTransform(x, v => v * 1.5), y: useTransform(y, v => v * 1.5) }} 
        className="absolute inset-0 opacity-40"
      >
        <div className="absolute top-[-10%] right-[-20%] w-[80vw] h-[80vw] rounded-full bg-indigo-200/20 blur-[150px] mix-blend-multiply" />
      </motion.div>

      {/* Floating Ice Particles (More dynamic) */}
      <SnowParticles />
      
      {/* Texture Overlay */}
      <div className="absolute inset-0 opacity-[0.04] mix-blend-overlay" style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=\'0 0 200 200\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'noiseFilter\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.8\' numOctaves=\'3\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23noiseFilter)\'/%3E%3C/svg%3E")' }}></div>
    </div>
  );
};

// 2. Aurora Typing Indicator
const AuroraLoader = () => (
  <div className="flex items-center gap-1 h-6 px-2">
    {[0, 1, 2].map((i) => (
      <motion.div
        key={i}
        className="w-1.5 h-1.5 rounded-full bg-gradient-to-tr from-blue-400 to-emerald-300"
        animate={{
          y: [-2, 4, -2],
          opacity: [0.4, 1, 0.4],
          scale: [0.8, 1.2, 0.8]
        }}
        transition={{
          duration: 1.2,
          repeat: Infinity,
          delay: i * 0.2,
          ease: "easeInOut"
        }}
      />
    ))}
  </div>
);

// 3. Enhanced Message Bubble
const MessageBubble = ({ message }: { message: Message }) => {
  const isAi = message.role === 'ai';
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20, filter: 'blur(10px)' }}
      animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
      transition={{ type: "spring", stiffness: 100, damping: 15 }}
      className={`relative flex w-full mb-8 ${isAi ? 'justify-start' : 'justify-end'}`}
    >
      <motion.div 
        whileHover={{ scale: 1.01 }}
        className={`
          relative px-6 py-4 max-w-[75%] rounded-2xl backdrop-blur-xl border transition-all duration-300
          ${isAi 
            ? 'bg-white/60 text-slate-700 rounded-tl-none border-white/60' 
            : 'bg-gradient-to-br from-[#E0F2FE]/80 to-[#F0F9FF]/80 text-slate-800 rounded-tr-none border-blue-100/50'
          }
        `}
        style={{
          boxShadow: isAi 
            ? '0 8px 32px -4px rgba(148, 163, 184, 0.1)' 
            : '0 8px 32px -4px rgba(56, 189, 248, 0.15)',
        }}
      >
        <div className="text-sm font-light leading-relaxed tracking-wide">
          {message.content}
        </div>
        
        {message.isTyping && (
           <div className="mt-2">
             <AuroraLoader />
           </div>
        )}

        <div className="absolute bottom-1 right-3 text-[10px] text-slate-400 font-mono opacity-60 flex items-center gap-1">
          {message.timestamp}
          {!isAi && <span className="block w-1 h-1 rounded-full bg-blue-400" />}
        </div>
        
        {/* Shimmer Effect on Hover (Frost melting) */}
        <motion.div 
          className="absolute inset-0 rounded-2xl overflow-hidden pointer-events-none opacity-0 group-hover:opacity-100"
          initial={false}
          whileHover={{ opacity: 1 }}
        >
          <div className="absolute top-0 left-[-100%] w-[50%] h-full bg-gradient-to-r from-transparent via-white/40 to-transparent skew-x-[-25deg] hover:animate-shimmer" />
        </motion.div>
      </motion.div>
    </motion.div>
  );
};

// 4. Main Application
export default function ArcticEchoApp() {
  const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [selectedModel, setSelectedModel] = useState('GPT-4o (Arctic)');
  const [activeSession, setActiveSession] = useState(MOCK_HISTORY[0]);
  const [showHistory, setShowHistory] = useState(false);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  
  // Parallax hooks for UI elements (more sensitive than background)
  const { x, y } = useParallax(0.015);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSend = () => {
    if (!inputText.trim()) return;
    
    const newMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, newMessage]);
    setInputText('');
    setIsTyping(true);

    // Simulate AI Response with Typing Animation
    setTimeout(() => {
      setIsTyping(false);
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'ai',
        content: '我看到了你思维中的闪光点。这就像极地夜晚的第一缕阳光，既寒冷又充满希望。我们继续深入这个话题吗？',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, aiResponse]);
    }, 2000);
  };

  return (
    <div className="relative w-full h-screen font-sans text-slate-700 overflow-hidden flex items-center justify-center perspective-[2000px] selection:bg-blue-100 selection:text-blue-900">
      <ArcticBackground />

      {/* --- LAYER 1: 历史回溯 (Floating Iceberg) --- */}
      <motion.div 
        className="hidden md:flex flex-col absolute left-[4%] top-[12%] bottom-[18%] w-64 z-10"
        initial={{ opacity: 0, x: -50, rotateY: 15 }}
        animate={{ 
          opacity: 1, 
          x: 0, 
          rotateY: 15,
          y: [0, -8, 0] // Gentle floating animation (Iceberg breathing)
        }}
        transition={{ 
          opacity: { duration: 0.8 },
          y: { duration: 6, repeat: Infinity, ease: "easeInOut" } // Slow bobbing
        }}
        style={{ transformStyle: 'preserve-3d' }}
      >
        <div className="flex items-center gap-3 mb-8 pl-4 group">
          <div className="p-2 bg-white/40 backdrop-blur-md rounded-lg shadow-sm border border-white/50 group-hover:rotate-180 transition-transform duration-700">
            <Wind size={20} className="text-slate-600" />
          </div>
          <span className="text-lg font-light tracking-widest text-slate-600 uppercase group-hover:text-blue-500 transition-colors">Archive</span>
        </div>

        <div className="flex-1 space-y-4 overflow-y-auto scrollbar-hide pr-4 py-2 mask-image-b-fade">
          {MOCK_HISTORY.map((session, idx) => (
            <motion.div
              key={session.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 * idx }}
              onClick={() => setActiveSession(session)}
              className={`
                group relative p-4 rounded-xl cursor-pointer transition-all duration-500
                border backdrop-blur-md overflow-hidden
                ${activeSession.id === session.id 
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
              
              {/* Icy Glow Effect on Active */}
              {activeSession.id === session.id && (
                <motion.div 
                  layoutId="active-glow"
                  className="absolute inset-0 bg-gradient-to-r from-blue-50 to-transparent opacity-50 z-0"
                />
              )}
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* --- LAYER 2: 智能棱镜 (Context Prism - Floating) --- */}
      <motion.div 
        className="hidden lg:block absolute right-[5%] top-[15%] w-72 z-10"
        initial={{ opacity: 0, y: -20, rotateY: -10 }}
        animate={{ 
          opacity: 1, 
          rotateY: -10,
          y: [0, 10, 0] // Counter-floating against the history panel
        }}
        transition={{ 
          opacity: { delay: 0.4, duration: 0.8 },
          y: { duration: 7, repeat: Infinity, ease: "easeInOut", delay: 1 } 
        }}
        style={{ x: useTransform(x, v => -v), y: useTransform(y, v => -v) }} // Inverse parallax for depth
      >
        <div className="relative p-6 rounded-3xl bg-white/20 backdrop-blur-2xl border border-white/40 shadow-2xl shadow-indigo-100/20 overflow-hidden group">
          {/* Prismatic Reflection */}
          <div className="absolute inset-0 bg-gradient-to-tr from-white/20 via-transparent to-white/10 pointer-events-none" />
          <motion.div 
            className="absolute top-0 -left-[100%] w-[100%] h-full bg-gradient-to-r from-transparent via-white/30 to-transparent skew-x-12"
            animate={{ left: ['-100%', '200%'] }}
            transition={{ duration: 8, repeat: Infinity, ease: "linear", delay: 2 }}
          />
          
          <div className="flex items-center gap-2 mb-4 text-indigo-900/60">
            <Aperture size={16} className="animate-spin-slow" />
            <span className="text-xs font-bold tracking-widest uppercase">Context Analysis</span>
          </div>

          <div className="space-y-4 relative z-10">
            <div>
              <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1 flex items-center gap-2">
                <Waves size={10} /> Current Focus
              </h4>
              <p className="text-sm text-slate-700 leading-relaxed font-light">
                {activeSession.summary}
              </p>
            </div>
            
            <div className="h-px w-full bg-gradient-to-r from-transparent via-indigo-200/50 to-transparent" />

            <div>
              <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">Compute Load</h4>
              <div className="flex items-center gap-2">
                <div className="h-1.5 flex-1 bg-slate-200/50 rounded-full overflow-hidden backdrop-blur-sm">
                  <motion.div 
                    initial={{ width: 0 }} 
                    animate={{ width: ['40%', '60%', '45%'] }} 
                    transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                    className="h-full bg-gradient-to-r from-blue-300 via-indigo-300 to-purple-300"
                  />
                </div>
                <span className="text-[10px] font-mono text-slate-400">stable</span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* --- LAYER 3: 核心交互流 (Main Flow) --- */}
      <motion.div 
        className="relative w-full max-w-2xl h-[85vh] flex flex-col z-20"
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.8 }}
      >
        
        {/* Header - Shimmering Title */}
        <div className="flex justify-between items-center px-6 py-4 mb-2">
          <motion.h1 
            className="text-3xl font-thin tracking-wide text-slate-700 drop-shadow-sm cursor-default"
            whileHover={{ scale: 1.02 }}
          >
            Arctic<span className="font-bold text-transparent bg-clip-text bg-gradient-to-r from-slate-800 to-slate-600">Echo</span>
          </motion.h1>
          <div className="md:hidden p-2 bg-white/50 rounded-full backdrop-blur-md shadow-sm active:scale-95 transition-transform" onClick={() => setShowHistory(!showHistory)}>
            <History size={20} />
          </div>
        </div>

        {/* Chat Area - The "Fjord" */}
        <div 
          ref={chatContainerRef}
          className="flex-1 overflow-y-auto px-4 md:px-8 pb-32 scrollbar-none"
          style={{ 
            maskImage: 'linear-gradient(to bottom, transparent 0%, black 5%, black 90%, transparent 100%)',
            WebkitMaskImage: 'linear-gradient(to bottom, transparent 0%, black 5%, black 90%, transparent 100%)'
          }}
        >
          <div className="min-h-full flex flex-col justify-end pt-8">
            <AnimatePresence>
              {messages.map((msg) => (
                <MessageBubble key={msg.id} message={msg} />
              ))}
              {isTyping && (
                 <MessageBubble 
                   key="typing" 
                   message={{ 
                     id: 'typing', 
                     role: 'ai', 
                     content: '', 
                     timestamp: '', 
                     isTyping: true 
                   }} 
                 />
              )}
            </AnimatePresence>
            <div className="h-4" /> 
          </div>
        </div>

        {/* --- LAYER 4: 控制台 (Control Deck) --- */}
        <div className="absolute bottom-6 left-0 right-0 px-4 md:px-0 flex justify-center perspective-[1000px]">
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
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSend())}
                placeholder="在极夜中低语..."
                className="flex-1 bg-transparent border-none outline-none resize-none py-3 text-slate-700 placeholder:text-slate-400/60 font-light text-base max-h-32 focus:placeholder:text-slate-300"
                rows={1}
                style={{ minHeight: '44px' }}
              />

              <motion.button 
                whileHover={{ scale: 1.1, rotate: 10 }}
                whileTap={{ scale: 0.9 }}
                onClick={handleSend}
                disabled={!inputText.trim()}
                className={`
                  p-3 rounded-full mb-1 shadow-lg transition-all duration-300 relative overflow-hidden
                  ${inputText.trim() 
                    ? 'bg-slate-800 text-white shadow-blue-900/20' 
                    : 'bg-slate-200 text-slate-400 cursor-not-allowed'}
                `}
              >
                <Send size={18} className="relative z-10" />
                {inputText.trim() && (
                  <motion.div 
                    className="absolute inset-0 bg-gradient-to-r from-blue-600 to-indigo-600"
                    animate={{ x: ['-100%', '100%'] }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  />
                )}
              </motion.button>
            </div>

            {/* Bottom Bar: Model Selector & Status */}
            <div className="flex items-center justify-between px-4 pb-1 pt-2 border-t border-slate-200/50">
              <div className="flex items-center gap-2 group cursor-pointer">
                <motion.div 
                  className="p-1.5 bg-indigo-50 rounded-full text-indigo-500"
                  whileHover={{ rotate: 180 }}
                  transition={{ duration: 0.5 }}
                >
                  <Cpu size={14} />
                </motion.div>
                <div className="relative group-hover:text-indigo-600 transition-colors">
                  <select 
                    value={selectedModel} 
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="appearance-none bg-transparent text-xs font-semibold text-slate-600 outline-none cursor-pointer pr-4 uppercase tracking-wider"
                  >
                    <option>GPT-4o (Arctic)</option>
                    <option>Claude 3.5 (Sonnet)</option>
                    <option>Gemini Pro (Vision)</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center gap-2 text-[10px] font-mono text-slate-400">
                <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
                <span>ONLINE</span>
              </div>
            </div>

          </motion.div>
        </div>

      </motion.div>

      {/* Interactive Snow Particles */}
      <SnowParticles />
    </div>
  );
}

// 5. Enhanced Atmospheric Effect: Drifting Snow with Mouse Interaction
const SnowParticles = () => {
  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden z-[5]">
      {[...Array(30)].map((_, i) => (
        <SnowFlake key={i} />
      ))}
    </div>
  );
};

const SnowFlake = () => {
  const randomDuration = Math.random() * 10 + 20;
  const randomDelay = Math.random() * 20;
  
  return (
    <motion.div
      className="absolute bg-white rounded-full opacity-60 blur-[0.5px]"
      initial={{
        x: Math.random() * window.innerWidth,
        y: -20,
        scale: Math.random() * 0.4 + 0.2,
      }}
      animate={{
        y: window.innerHeight + 50,
        x: `calc(${Math.random() * 100}vw + ${Math.random() * 200 - 100}px)`,
        opacity: [0, 0.6, 0]
      }}
      transition={{
        duration: randomDuration,
        repeat: Infinity,
        ease: "linear",
        delay: randomDelay,
      }}
      style={{
        width: Math.random() * 4 + 2,
        height: Math.random() * 4 + 2,
      }}
    />
  );
}