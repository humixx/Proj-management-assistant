import { create } from 'zustand';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}

interface UIState {
  toasts: Toast[];
  addToast: (type: ToastType, message: string, duration?: number) => void;
  removeToast: (id: string) => void;
  // Modal states
  isCreateTaskModalOpen: boolean;
  setCreateTaskModalOpen: (open: boolean) => void;
}

const generateId = () => `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

export const useUIStore = create<UIState>((set, get) => ({
  toasts: [],
  
  addToast: (type, message, duration = 5000) => {
    const id = generateId();
    const toast: Toast = { id, type, message, duration };
    
    set((state) => ({ toasts: [...state.toasts, toast] }));
    
    // Auto-remove after duration
    if (duration > 0) {
      setTimeout(() => {
        get().removeToast(id);
      }, duration);
    }
  },
  
  removeToast: (id) => {
    set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) }));
  },

  isCreateTaskModalOpen: false,
  setCreateTaskModalOpen: (open) => set({ isCreateTaskModalOpen: open }),
}));

// Helper hooks for common toast types
export const useToast = () => {
  const addToast = useUIStore((state) => state.addToast);
  
  return {
    success: (message: string) => addToast('success', message),
    error: (message: string) => addToast('error', message),
    warning: (message: string) => addToast('warning', message),
    info: (message: string) => addToast('info', message),
  };
};
