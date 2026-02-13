import apiClient from './client';
import { ChatRequest, ChatResponse, ChatHistoryResponse } from '@/types';

export interface StreamEvent {
  type: 'thinking' | 'tool_start' | 'tool_end' | 'task_created' | 'text_delta' | 'composing' | 'response' | 'error' | 'done' | 'plan_started' | 'plan_step_created';
  stage?: string;
  iteration?: number;
  has_tool_calls?: boolean;
  last_tool?: string;
  tool_name?: string;
  arguments?: Record<string, any>;
  result?: any;
  message?: string;
  text?: string;
  tool_calls?: any[];
  task?: { id: string; title: string; priority: string; status: string };
  progress?: { current: number; total: number };
  plan_goal?: string;
  parent_task_id?: string;
  total_steps?: number;
  step_number?: number;
}

export const chatApi = {
  sendMessage: async (message: string): Promise<ChatResponse> => {
    const data: ChatRequest = { message, include_context: true };
    const response = await apiClient.post<ChatResponse>('/chat', data, {
      timeout: 120000, // 2 minutes for complex operations like creating multiple tasks
    });
    return response.data;
  },

  sendMessageStreaming: async function* (message: string): AsyncGenerator<StreamEvent> {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const projectId = localStorage.getItem('currentProjectId');

    // Get auth token from persisted store
    let token: string | null = null;
    try {
      const authStore = localStorage.getItem('auth-store');
      if (authStore) {
        const parsed = JSON.parse(authStore);
        token = parsed?.state?.token || null;
      }
    } catch {
      // ignore parse errors
    }

    const response = await fetch(`${baseUrl}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(projectId ? { 'X-Project-ID': projectId } : {}),
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ message, include_context: true }),
    });

    if (!response.ok) {
      throw new Error(`Stream request failed: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error('No response body');

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith('data: ')) {
          try {
            const event: StreamEvent = JSON.parse(trimmed.slice(6));
            yield event;
          } catch {
            // skip malformed lines
          }
        }
      }
    }
  },

  getHistory: async (limit = 50): Promise<ChatHistoryResponse> => {
    const response = await apiClient.get<ChatHistoryResponse>('/chat/history', { params: { limit } });
    return response.data;
  },
  clearHistory: async (): Promise<{ deleted: number }> => {
    const response = await apiClient.delete<{ deleted: number }>('/chat/history');
    return response.data;
  },
};
