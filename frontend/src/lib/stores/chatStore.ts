import { create } from 'zustand';
import { LocalMessage, ChatResponse } from '@/types';
import { chatApi, StreamEvent } from '@/lib/api/chat';
import { getCurrentProjectId } from '@/lib/api';
import { useUIStore } from './uiStore';
import { useTaskStore } from './taskStore';

// Helper to get addToast outside of React
const getAddToast = () => useUIStore.getState().addToast;

// Tools that change task data — trigger live refresh on tool_end
const TASK_MUTATING_TOOLS = ['create_task', 'bulk_create_tasks', 'confirm_proposed_tasks', 'update_task', 'delete_task'];

const generateId = () => `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

// Human-readable labels for agent stages
const TOOL_LABELS: Record<string, string> = {
  create_task: 'Creating task',
  bulk_create_tasks: 'Creating tasks',
  list_tasks: 'Fetching tasks',
  search_documents: 'Searching documents',
  propose_tasks: 'Proposing tasks',
  confirm_proposed_tasks: 'Creating approved tasks',
  update_task: 'Updating task',
  delete_task: 'Deleting task',
};

export interface AgentStatus {
  stage: 'idle' | 'analyzing' | 'calling_llm' | 'tool_running' | 'tool_done' | 'composing' | 'responding';
  label: string;
  toolName?: string;
  toolArgs?: Record<string, any>;
  toolResult?: any;
}

interface ChatState {
  messages: LocalMessage[];
  isLoading: boolean;
  isSending: boolean;
  error: string | null;
  currentProjectId: string | null;
  agentStatus: AgentStatus;
  fetchHistory: () => Promise<void>;
  sendMessage: (content: string) => Promise<ChatResponse | null>;
  sendMessageStreaming: (content: string) => Promise<ChatResponse | null>;
  clearHistory: () => Promise<void>;
  clearError: () => void;
}

const IDLE_STATUS: AgentStatus = { stage: 'idle', label: '' };

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isLoading: false,
  isSending: false,
  error: null,
  currentProjectId: null,
  agentStatus: IDLE_STATUS,

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
      set({ messages: response.messages.map((m) => ({ ...m, pending: false })) as LocalMessage[], isLoading: false, currentProjectId: projectId });
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

  sendMessageStreaming: async (content: string) => {
    const userMessage: LocalMessage = {
      id: generateId(),
      role: 'user',
      content,
      created_at: new Date().toISOString(),
      pending: false,
    };

    set((state) => ({
      messages: [...state.messages, userMessage],
      isSending: true,
      error: null,
      agentStatus: { stage: 'analyzing', label: 'Analyzing your request...' },
    }));

    let finalResponse: ChatResponse | null = null;

    try {
      for await (const event of chatApi.sendMessageStreaming(content)) {
        switch (event.type) {
          case 'thinking': {
            let label: string;
            if (event.iteration && event.iteration > 1) {
              // After a tool ran — describe what the agent is doing next
              const lastTool = event.last_tool;
              if (lastTool === 'list_tasks') {
                label = 'Reviewing task list...';
              } else if (lastTool === 'search_documents') {
                label = 'Analyzing search results...';
              } else if (lastTool === 'propose_tasks') {
                label = 'Preparing proposal...';
              } else if (lastTool === 'confirm_proposed_tasks') {
                label = 'Summarizing created tasks...';
              } else if (lastTool === 'update_task') {
                label = 'Confirming changes...';
              } else if (lastTool === 'delete_task') {
                label = 'Confirming deletion...';
              } else {
                label = 'Processing next step...';
              }
            } else {
              label = 'Thinking...';
            }
            set({
              agentStatus: { stage: 'calling_llm', label },
            });
            break;
          }

          case 'tool_start':
            set({
              agentStatus: {
                stage: 'tool_running',
                label: TOOL_LABELS[event.tool_name || ''] || `Running ${event.tool_name}`,
                toolName: event.tool_name,
                toolArgs: event.arguments,
              },
            });
            break;

          case 'task_created':
            // Live-refresh after each individual task is created
            set({
              agentStatus: {
                stage: 'tool_running',
                label: event.progress
                  ? `Creating tasks (${event.progress.current}/${event.progress.total})...`
                  : `Created "${event.task?.title}"`,
                toolName: event.tool_name,
              },
            });
            useTaskStore.getState().fetchTasks();
            break;

          case 'tool_end':
            set({
              agentStatus: {
                stage: 'tool_done',
                label: `${TOOL_LABELS[event.tool_name || ''] || event.tool_name} complete`,
                toolName: event.tool_name,
                toolResult: event.result,
              },
            });
            // Live-refresh task board when a task-mutating tool completes
            if (event.tool_name && TASK_MUTATING_TOOLS.includes(event.tool_name)) {
              useTaskStore.getState().fetchTasks();
            }
            break;

          case 'composing':
            set({
              agentStatus: {
                stage: 'composing',
                label: 'Writing response...',
              },
            });
            break;

          case 'response':
            finalResponse = {
              message: event.message || '',
              tool_calls: event.tool_calls?.map((tc: any) => ({
                tool_name: tc.tool_name,
                arguments: tc.arguments,
                result: tc.result,
              })) || null,
            };

            const assistantMessage: LocalMessage = {
              id: generateId(),
              role: 'assistant',
              content: event.message || '',
              tool_calls: finalResponse.tool_calls,
              created_at: new Date().toISOString(),
              pending: false,
            };

            set((state) => ({
              messages: [...state.messages, assistantMessage],
              isSending: false,
              agentStatus: IDLE_STATUS,
            }));
            break;

          case 'error':
            set({
              error: event.message || 'Agent error',
              isSending: false,
              agentStatus: IDLE_STATUS,
            });
            getAddToast()('error', event.message || 'Agent error');
            break;

          case 'done':
            // Stream complete — if no response event was received, reset
            if (!finalResponse) {
              set({ isSending: false, agentStatus: IDLE_STATUS });
            }
            break;
        }
      }

      return finalResponse;
    } catch (error: any) {
      const message = error.message || 'Failed to send message';
      console.error('Streaming chat error:', message, error);
      set({ error: message, isSending: false, agentStatus: IDLE_STATUS });
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
