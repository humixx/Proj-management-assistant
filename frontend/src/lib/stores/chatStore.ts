import { create } from 'zustand';
import { LocalMessage, ChatResponse } from '@/types';
import { chatApi, getCurrentProjectId } from '@/lib/api';
import { useUIStore } from './uiStore';

// Helper to get addToast outside of React
const getAddToast = () => useUIStore.getState().addToast;

const generateId = () => `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

interface ChatState {
  messages: LocalMessage[];
  isLoading: boolean;
  isSending: boolean;
  error: string | null;
  currentProjectId: string | null;
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
  currentProjectId: null,

  fetchHistory: async () => {
    const projectId = getCurrentProjectId();
    if (!projectId) {
      set({ error: 'No project selected', isLoading: false });
      return;
    }

    // Clear messages if project changed
    const currentState = get();
    if (currentState.currentProjectId !== projectId) {
      set({ messages: [], currentProjectId: projectId });
    }

    set({ isLoading: true, error: null });
    try {
      const response = await chatApi.getHistory();
      set({ messages: response.messages.map((m) => ({ ...m, pending: false })), isLoading: false, currentProjectId: projectId });
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
      set((state) => ({ messages: [...state.messages, assistantMessage], isSending: false, error: null }));
      return response;
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || 'Failed to send message';
      console.error('Chat error:', message, error);
      set({ error: message, isSending: false });
      getAddToast()('error', message);
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
