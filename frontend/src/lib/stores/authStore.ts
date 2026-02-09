'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, LoginRequest, RegisterRequest } from '@/types/auth';
import { authApi } from '@/lib/api/auth';
import { useUIStore } from './uiStore';
import { useNotesStore } from './notesStore';
import { useProjectStore } from './projectStore';

const getAddToast = () => useUIStore.getState().addToast;

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  setToken: (token: string) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      setToken: (token: string) => {
        set({ token });
        // Also set cookie for middleware access
        document.cookie = `auth-token=${token}; path=/; SameSite=Lax`;
      },

      login: async (data: LoginRequest) => {
        set({ isLoading: true });
        try {
          const response = await authApi.login(data);
          set({
            user: response.user,
            token: response.access_token,
            isAuthenticated: true,
            isLoading: false,
          });
          // Set cookie for middleware
          document.cookie = `auth-token=${response.access_token}; path=/; SameSite=Lax`;
          getAddToast()('success', `Welcome back, ${response.user.name}!`);
        } catch (error: any) {
          set({ isLoading: false });
          const message = error.response?.data?.detail || 'Login failed';
          getAddToast()('error', message);
          throw error;
        }
      },

      register: async (data: RegisterRequest) => {
        set({ isLoading: true });
        try {
          const response = await authApi.register(data);
          set({
            user: response.user,
            token: response.access_token,
            isAuthenticated: true,
            isLoading: false,
          });
          // Set cookie for middleware
          document.cookie = `auth-token=${response.access_token}; path=/; SameSite=Lax`;
          getAddToast()('success', `Welcome, ${response.user.name}!`);
        } catch (error: any) {
          set({ isLoading: false });
          const message = error.response?.data?.detail || 'Registration failed';
          getAddToast()('error', message);
          throw error;
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        });
        // Clear cookie
        document.cookie = 'auth-token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
        // Clear other stores (both in-memory Zustand state and persisted storage)
        useProjectStore.getState().selectProject(null);
        useProjectStore.setState({ projects: [] });
        localStorage.removeItem('currentProjectId');
        localStorage.removeItem('project-store');
        // Clear session notes
        useNotesStore.getState().clearNotes();
      },

      checkAuth: async () => {
        const { token } = get();
        if (!token) {
          set({ isAuthenticated: false, user: null });
          return;
        }
        try {
          const user = await authApi.getMe();
          set({ user, isAuthenticated: true });
        } catch {
          // Token invalid/expired
          get().logout();
        }
      },
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
