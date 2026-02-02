import apiClient from './client';
import { ChatRequest, ChatResponse, ChatHistoryResponse } from '@/types';

export const chatApi = {
  sendMessage: async (message: string): Promise<ChatResponse> => {
    const data: ChatRequest = { message, include_context: true };
    const response = await apiClient.post<ChatResponse>('/chat', data);
    return response.data;
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
