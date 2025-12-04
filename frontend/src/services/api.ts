// frontend/src/services/api.ts
// API调用服务，处理与后端的通信

import { ChatChunkResponse, ChatSession } from '../types';

const API_BASE_URL = '/api';

/**
 * 发送聊天消息，返回EventSource用于接收流式响应
 */
export function sendChatMessage(
  message: string,
  conversationId: string | null,
  onChunk: (chunk: string) => void,
  onDone: (conversationId: string) => void,
  onError: (error: string) => void
): () => void {
  // 使用fetch + ReadableStream实现SSE流式接收
  const controller = new AbortController();
  
  fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
    }),
    signal: controller.signal,
  })
    .then(async (response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('Response body is null');
      }

      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          // 处理剩余的buffer
          if (buffer.trim()) {
            const lines = buffer.split('\n');
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data: ChatChunkResponse = JSON.parse(line.slice(6));
                  if (data.type === 'done' && data.conversation_id) {
                    onDone(data.conversation_id);
                  }
                } catch (e) {
                  console.error('Failed to parse SSE data:', e);
                }
              }
            }
          }
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        // 保留最后一个不完整的行
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim() === '') continue; // 跳过空行
          
          if (line.startsWith('data: ')) {
            try {
              const data: ChatChunkResponse = JSON.parse(line.slice(6));
              
              if (data.type === 'chunk' && data.content) {
                onChunk(data.content);
              } else if (data.type === 'done' && data.conversation_id) {
                onDone(data.conversation_id);
                return;
              } else if (data.type === 'error') {
                onError(data.error || '未知错误');
                return;
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e, line);
            }
          }
        }
      }
    })
    .catch((error) => {
      if (error.name !== 'AbortError') {
        onError(error.message || '请求失败');
      }
    });

  // 返回取消函数
  return () => {
    controller.abort();
  };
}

/**
 * 获取会话列表
 */
export async function getConversations(): Promise<ChatSession[]> {
  const response = await fetch(`${API_BASE_URL}/conversations`);
  if (!response.ok) {
    throw new Error('获取会话列表失败');
  }
  const data = await response.json();
  return data.conversations || [];
}

/**
 * 获取会话详情
 */
export async function getConversationDetail(conversationId: string) {
  const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}`);
  if (!response.ok) {
    throw new Error('获取会话详情失败');
  }
  return await response.json();
}

