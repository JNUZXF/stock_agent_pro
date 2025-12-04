// frontend/src/hooks/useChat.ts
// 聊天逻辑Hook，处理消息发送和接收

import { useState, useRef, useCallback, useEffect } from 'react';
import { Message, ChatSession } from '../types';
import { sendChatMessage, getConversations, getConversationDetail } from '../services/api';

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
      // 按照会话ID倒序排序（会话ID格式：YYYYMMDD-HHMMSS+随机数，最新的ID更大）
      // 确保最新的会话显示在最上面
      const sortedData = [...data].sort((a, b) => {
        // 按会话ID倒序排序（字符串比较，因为ID格式固定，可以直接比较）
        return b.id.localeCompare(a.id);
      });
      setSessions(sortedData);
    } catch (error) {
      console.error('Failed to load sessions:', error);
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
          const formattedMessages: Message[] = detail.messages.map((msg, index) => ({
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
  const createNewConversation = useCallback(() => {
    setConversationId(null);
    setMessages([]);
    localStorage.removeItem(STORAGE_KEY_CURRENT_CONVERSATION);
  }, []);

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
                const formattedMessages: Message[] = detail.messages.map((msg, index) => ({
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

