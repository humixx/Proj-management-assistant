import { create } from 'zustand';
import { Document } from '@/types';
import { documentsApi, getCurrentProjectId } from '@/lib/api';
import { useUIStore } from './uiStore';

// Helper to get addToast outside of React
const getAddToast = () => useUIStore.getState().addToast;

interface DocumentState {
  documents: Document[];
  uploadProgress: Record<string, number>;
  isLoading: boolean;
  isUploading: boolean;
  error: string | null;
  currentProjectId: string | null;
  fetchDocuments: () => Promise<void>;
  uploadDocument: (file: File) => Promise<Document | null>;
  deleteDocument: (documentId: string) => Promise<void>;
  refreshDocument: (documentId: string) => Promise<void>;
  clearError: () => void;
}

export const useDocumentStore = create<DocumentState>((set, get) => ({
  documents: [],
  uploadProgress: {},
  isLoading: false,
  isUploading: false,
  error: null,
  currentProjectId: null,

  fetchDocuments: async () => {
    const projectId = getCurrentProjectId();
    if (!projectId) {
      set({ error: 'No project selected', isLoading: false });
      return;
    }

    // Clear documents if project changed
    const currentState = get();
    if (currentState.currentProjectId !== projectId) {
      set({ documents: [], currentProjectId: projectId });
    }

    set({ isLoading: true, error: null });
    try {
      const response = await documentsApi.list();
      set({ documents: response.documents, isLoading: false, currentProjectId: projectId });
    } catch (error: any) {
      set({ error: error.response?.data?.detail || 'Failed to fetch documents', isLoading: false });
    }
  },

  uploadDocument: async (file: File) => {
    set({ isUploading: true, error: null });
    try {
      const document = await documentsApi.upload(file, (progress) => {
        set((state) => ({ uploadProgress: { ...state.uploadProgress, [file.name]: progress } }));
      });
      set((state) => ({
        documents: [document, ...state.documents],
        isUploading: false,
        uploadProgress: {},
      }));
      getAddToast()('success', `"${file.name}" uploaded successfully`);
      return document;
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to upload document';
      set({ error: message, isUploading: false, uploadProgress: {} });
      getAddToast()('error', message);
      return null;
    }
  },

  deleteDocument: async (documentId: string) => {
    try {
      await documentsApi.delete(documentId);
      set((state) => ({ documents: state.documents.filter((d) => d.id !== documentId) }));
      getAddToast()('success', 'Document deleted');
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to delete document';
      set({ error: message });
      getAddToast()('error', message);
    }
  },

  refreshDocument: async (documentId: string) => {
    try {
      const document = await documentsApi.get(documentId);
      set((state) => ({ documents: state.documents.map((d) => (d.id === documentId ? document : d)) }));
    } catch (error) {
      console.error('Failed to refresh document');
    }
  },

  clearError: () => set({ error: null }),
}));
