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
}

export interface ChatChunkResponse {
  type: 'chunk' | 'done' | 'error';
  content?: string;
  conversation_id?: string;
  error?: string;
}

