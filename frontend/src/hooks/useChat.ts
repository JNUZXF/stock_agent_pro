// frontend/src/hooks/useChat.ts
// 聊天逻辑Hook，处理消息发送和接收

import { useState, useRef, useCallback, useEffect } from 'react';
import { Message, ChatSession, ApiMessage } from '../types';
import { sendChatMessage, getConversations, getConversationDetail, createConversation } from '../services/api';

// localStorage键名
const STORAGE_KEY_CURRENT_CONVERSATION = 'stock_agent_current_conversation';
const STORAGE_KEY_MESSAGES_PREFIX = 'stock_agent_messages_';

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const abortControllerRef = useRef<(() => void) | null>(null);

  // 保存消息到localStorage
  const saveMessagesToStorage = useCallback((convId: string | null, msgs: Message[]) => {
    if (convId) {
      try {
        localStorage.setItem(`${STORAGE_KEY_MESSAGES_PREFIX}${convId}`, JSON.stringify(msgs));
        localStorage.setItem(STORAGE_KEY_CURRENT_CONVERSATION, convId);
      } catch (e) {
        console.error('Failed to save messages to localStorage:', e);
      }
    }
  }, []);

  // 从localStorage加载消息
  const loadMessagesFromStorage = useCallback((convId: string | null): Message[] => {
    if (!convId) return [];
    try {
      const stored = localStorage.getItem(`${STORAGE_KEY_MESSAGES_PREFIX}${convId}`);
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (e) {
      console.error('Failed to load messages from localStorage:', e);
    }
    return [];
  }, []);

  // 当消息变化时保存到localStorage
  useEffect(() => {
    if (conversationId && messages.length > 0) {
      saveMessagesToStorage(conversationId, messages);
    }
  }, [messages, conversationId, saveMessagesToStorage]);

  // 当conversationId变化时保存
  useEffect(() => {
    if (conversationId) {
      localStorage.setItem(STORAGE_KEY_CURRENT_CONVERSATION, conversationId);
    }
  }, [conversationId]);

  // 加载会话列表
  const loadSessions = useCallback(async () => {
    try {
      const data = await getConversations();
      // 按照更新时间倒序排序，确保最新的会话显示在最上面
      const sortedData = [...data].sort((a, b) => {
        if (a.updated_at && b.updated_at) {
          return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
        }
        // 如果没有更新时间，按会话ID倒序排序
        return b.id.localeCompare(a.id);
      });
      setSessions(sortedData);
    } catch (error) {
      console.error('Failed to load sessions:', error);
      // 如果加载失败，至少保持空数组
      setSessions([]);
    }
  }, []);

  // 发送消息
  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isSending) return;

    // 添加用户消息
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    setIsSending(true);

    // 创建AI消息占位符
    const aiMessageId = (Date.now() + 1).toString();
    const aiMessage: Message = {
      id: aiMessageId,
      role: 'ai',
      content: '',
      timestamp: '',
      isTyping: true
    };
    setMessages(prev => [...prev, aiMessage]);

    // 取消之前的请求
    if (abortControllerRef.current) {
      abortControllerRef.current();
    }

    // 发送请求并接收流式响应
    const cancel = sendChatMessage(
      content.trim(),
      conversationId,
      (chunk: string) => {
        // 更新AI消息内容
        setMessages(prev => prev.map(msg => 
          msg.id === aiMessageId 
            ? { ...msg, content: msg.content + chunk, isTyping: false }
            : msg
        ));
      },
      (newConversationId: string) => {
        // 完成
        setIsSending(false);
        setConversationId(newConversationId);
        setMessages(prev => {
          const updated = prev.map(msg => 
            msg.id === aiMessageId 
              ? { ...msg, isTyping: false, timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
              : msg
          );
          // 保存到localStorage
          saveMessagesToStorage(newConversationId, updated);
          return updated;
        });
        // 重新加载会话列表
        loadSessions();
        abortControllerRef.current = null;
      },
      (error: string) => {
        // 错误处理
        setIsSending(false);
        setMessages(prev => prev.map(msg => 
          msg.id === aiMessageId 
            ? { ...msg, content: `错误: ${error}`, isTyping: false, timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
            : msg
        ));
        abortControllerRef.current = null;
      }
    );

    abortControllerRef.current = cancel;
  }, [conversationId, isSending, loadSessions, saveMessagesToStorage]);

  // 加载会话
  const loadConversation = useCallback(async (session: ChatSession) => {
    try {
      setConversationId(session.id);
      
      // 先从localStorage尝试加载
      const cachedMessages = loadMessagesFromStorage(session.id);
      if (cachedMessages.length > 0) {
        setMessages(cachedMessages);
      }

      // 从后端加载最新消息（确保同步）
      try {
        const detail = await getConversationDetail(session.id);
        if (detail.messages && detail.messages.length > 0) {
          // 转换为前端Message格式
          const formattedMessages: Message[] = detail.messages.map((msg: ApiMessage, index: number) => ({
            id: `${session.id}_${index}_${msg.role}`,
            role: msg.role === 'user' ? 'user' : 'ai',
            content: msg.content,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }));
          
          setMessages(formattedMessages);
          // 保存到localStorage
          saveMessagesToStorage(session.id, formattedMessages);
        } else if (cachedMessages.length === 0) {
          // 如果后端和缓存都没有消息，保持空数组
          setMessages([]);
        }
      } catch (apiError) {
        console.error('Failed to load conversation from API:', apiError);
        // 如果API失败但缓存有数据，使用缓存
        if (cachedMessages.length > 0) {
          setMessages(cachedMessages);
        }
      }
    } catch (error) {
      console.error('Failed to load conversation:', error);
    }
  }, [loadMessagesFromStorage, saveMessagesToStorage]);

  // 创建新会话
  const createNewConversation = useCallback(async () => {
    try {
      // 生成新的会话ID（格式：YYYYMMDD-HHMMSS-随机数）
      const now = new Date();
      const dateStr = now.toISOString().slice(0, 10).replace(/-/g, '');
      const timeStr = now.toTimeString().slice(0, 8).replace(/:/g, '');
      const randomNum = Math.floor(Math.random() * 10000).toString().padStart(4, '0');
      const newConversationId = `${dateStr}-${timeStr}-${randomNum}`;
      
      // 调用后端API创建对话
      const newSession = await createConversation(newConversationId);
      
      // 更新状态
      setConversationId(newConversationId);
      setMessages([]);
      localStorage.setItem(STORAGE_KEY_CURRENT_CONVERSATION, newConversationId);
      
      // 重新加载会话列表
      await loadSessions();
      
      return newSession;
    } catch (error) {
      console.error('Failed to create conversation:', error);
      // 如果创建失败，至少清空本地状态
      setConversationId(null);
      setMessages([]);
      localStorage.removeItem(STORAGE_KEY_CURRENT_CONVERSATION);
      throw error;
    }
  }, [loadSessions]);

  // 初始化：恢复上次的会话（仅执行一次）
  useEffect(() => {
    const savedConversationId = localStorage.getItem(STORAGE_KEY_CURRENT_CONVERSATION);
    if (savedConversationId) {
      const cachedMessages = loadMessagesFromStorage(savedConversationId);
      setConversationId(savedConversationId);
      if (cachedMessages.length > 0) {
        setMessages(cachedMessages);
      } else {
        // 即使缓存为空，也尝试从后端加载
        loadSessions().then(() => {
          // 会话列表加载后，尝试从后端加载消息
          getConversationDetail(savedConversationId)
            .then(detail => {
              if (detail.messages && detail.messages.length > 0) {
                const formattedMessages: Message[] = detail.messages.map((msg: ApiMessage, index: number) => ({
                  id: `${savedConversationId}_${index}_${msg.role}`,
                  role: msg.role === 'user' ? 'user' : 'ai',
                  content: msg.content,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                }));
                setMessages(formattedMessages);
                saveMessagesToStorage(savedConversationId, formattedMessages);
              }
            })
            .catch(() => {
              // 如果加载失败，保持空消息列表
            });
        });
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // 仅在组件挂载时执行一次

  return {
    messages,
    isSending,
    conversationId,
    sessions,
    sendMessage,
    loadSessions,
    loadConversation,
    createNewConversation,
  };
};

