import { create } from 'zustand';
import { LocalMessage, ChatResponse } from '@/types';
import { chatApi } from '@/lib/api';

const generateId = () => `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

interface ChatState {
  messages: LocalMessage[];
  isLoading: boolean;
  isSending: boolean;
  error: string | null;
  fetchHistory: () => Promise<void>;
  sendMessage: (content: string) => Promise<ChatResponse | null>;
  clearHistory: () => Promise<void>;
  clearError: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isLoading: false,
  isSending: false,
  error: null,

  fetchHistory: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await chatApi.getHistory();
      set({ messages: response.messages.map((m) => ({ ...m, pending: false })), isLoading: false });
    } catch (error: any) {
      set({ error: error.response?.data?.detail || 'Failed to fetch history', isLoading: false });
    }
  },

  sendMessage: async (content: string) => {
    const userMessage: LocalMessage = {
      id: generateId(),
      role: 'user',
      content,
      created_at: new Date().toISOString(),
      pending: false,
    };

    set((state) => ({ messages: [...state.messages, userMessage], isSending: true, error: null }));

    try {
      const response = await chatApi.sendMessage(content);
      const assistantMessage: LocalMessage = {
        id: generateId(),
        role: 'assistant',
        content: response.message,
        tool_calls: response.tool_calls,
        created_at: new Date().toISOString(),
        pending: false,
      };
      set((state) => ({ messages: [...state.messages, assistantMessage], isSending: false }));
      return response;
    } catch (error: any) {
      set({ error: error.response?.data?.detail || 'Failed to send message', isSending: false });
      return null;
    }
  },

  clearHistory: async () => {
    try {
      await chatApi.clearHistory();
      set({ messages: [] });
    } catch (error: any) {
      set({ error: error.response?.data?.detail || 'Failed to clear history' });
    }
  },

  clearError: () => set({ error: null }),
}));
