// frontend/src/types/index.ts
// TypeScript类型定义

export interface Message {
  id: string;
  role: 'user' | 'ai';
  content: string;
  timestamp: string;
  isTyping?: boolean;
}

export interface ChatSession {
  id: string;
  title: string;
  date: string;
  summary: string;
  message_count?: number;
  created_at?: string;
  updated_at?: string;
}

export interface ChatChunkResponse {
  type: 'chunk' | 'done' | 'error';
  content?: string;
  conversation_id?: string;
  error?: string;
}

// 后端API返回的消息类型
export interface ApiMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

// 后端API返回的会话详情类型
export interface ConversationDetail {
  id: number;
  conversation_id: string;
  title?: string;
  summary?: string;
  message_count: number;
  created_at: string;
  updated_at: string;
  messages: ApiMessage[];
}

