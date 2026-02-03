import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Project, ProjectCreate } from '@/types';
import { projectsApi, setCurrentProjectId } from '@/lib/api';
import { useUIStore } from './uiStore';

// Helper to get addToast outside of React
const getAddToast = () => useUIStore.getState().addToast;

interface ProjectState {
  projects: Project[];
  currentProject: Project | null;
  isLoading: boolean;
  error: string | null;
  fetchProjects: () => Promise<void>;
  createProject: (data: ProjectCreate) => Promise<Project>;
  selectProject: (project: Project | null) => void;
  deleteProject: (projectId: string) => Promise<void>;
  clearError: () => void;
}

export const useProjectStore = create<ProjectState>()(
  persist(
    (set, get) => ({
      projects: [],
      currentProject: null,
      isLoading: false,
      error: null,

      fetchProjects: async () => {
        set({ isLoading: true, error: null });
        try {
          const response = await projectsApi.list();
          set({ projects: response.projects, isLoading: false });
        } catch (error: any) {
          set({ error: error.response?.data?.detail || 'Failed to fetch projects', isLoading: false });
        }
      },

      createProject: async (data: ProjectCreate) => {
        set({ isLoading: true, error: null });
        try {
          const project = await projectsApi.create(data);
          set((state) => ({ projects: [project, ...state.projects], isLoading: false }));
          getAddToast()('success', `Project "${project.name}" created`);
          return project;
        } catch (error: any) {
          const message = error.response?.data?.detail || 'Failed to create project';
          set({ error: message, isLoading: false });
          getAddToast()('error', message);
          throw error;
        }
      },

      selectProject: (project: Project | null) => {
        set({ currentProject: project });
        setCurrentProjectId(project?.id || null);
      },

      deleteProject: async (projectId: string) => {
        set({ isLoading: true });
        try {
          await projectsApi.delete(projectId);
          set((state) => ({
            projects: state.projects.filter((p) => p.id !== projectId),
            currentProject: state.currentProject?.id === projectId ? null : state.currentProject,
            isLoading: false,
          }));
          getAddToast()('success', 'Project deleted');
        } catch (error: any) {
          const message = error.response?.data?.detail || 'Failed to delete project';
          set({ error: message, isLoading: false });
          getAddToast()('error', message);
        }
      },

      clearError: () => set({ error: null }),
    }),
    { name: 'project-store', partialize: (state) => ({ currentProject: state.currentProject }) }
  )
);
