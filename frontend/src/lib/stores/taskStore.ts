import { create } from 'zustand';
import { Task, TaskCreate, TaskUpdate, TaskStatus } from '@/types';
import { tasksApi, getCurrentProjectId } from '@/lib/api';
import { useUIStore } from './uiStore';

// Helper to get addToast outside of React
const getAddToast = () => useUIStore.getState().addToast;

interface TaskState {
  tasks: Task[];
  isLoading: boolean;
  error: string | null;
  currentProjectId: string | null;
  fetchTasks: () => Promise<void>;
  createTask: (data: TaskCreate) => Promise<Task>;
  updateTask: (taskId: string, data: TaskUpdate) => Promise<void>;
  deleteTask: (taskId: string) => Promise<void>;
  getTasksByStatus: (status: TaskStatus) => Task[];
  clearError: () => void;
}

export const useTaskStore = create<TaskState>((set, get) => ({
  tasks: [],
  isLoading: false,
  error: null,
  currentProjectId: null,

  fetchTasks: async () => {
    const projectId = getCurrentProjectId();
    if (!projectId) {
      set({ error: 'No project selected', isLoading: false });
      return;
    }

    // Clear tasks if project changed
    const currentState = get();
    if (currentState.currentProjectId !== projectId) {
      set({ tasks: [], currentProjectId: projectId });
    }

    set({ isLoading: true, error: null });
    try {
      const response = await tasksApi.list();
      set({ tasks: response.tasks, isLoading: false, currentProjectId: projectId });
    } catch (error: any) {
      set({ error: error.response?.data?.detail || 'Failed to fetch tasks', isLoading: false });
    }
  },

  createTask: async (data: TaskCreate) => {
    set({ isLoading: true });
    try {
      const task = await tasksApi.create(data);
      set((state) => ({ tasks: [task, ...state.tasks], isLoading: false }));
      getAddToast()('success', `Task "${task.title}" created`);
      return task;
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to create task';
      set({ error: message, isLoading: false });
      getAddToast()('error', message);
      throw error;
    }
  },

  updateTask: async (taskId: string, data: TaskUpdate) => {
    try {
      const updated = await tasksApi.update(taskId, data);
      set((state) => ({ tasks: state.tasks.map((t) => (t.id === taskId ? updated : t)) }));
      getAddToast()('success', 'Task updated');
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to update task';
      set({ error: message });
      getAddToast()('error', message);
    }
  },

  deleteTask: async (taskId: string) => {
    try {
      await tasksApi.delete(taskId);
      set((state) => ({ tasks: state.tasks.filter((t) => t.id !== taskId) }));
      getAddToast()('success', 'Task deleted');
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to delete task';
      set({ error: message });
      getAddToast()('error', message);
    }
  },

  getTasksByStatus: (status: TaskStatus) => get().tasks.filter((t) => t.status === status),
  clearError: () => set({ error: null }),
}));
