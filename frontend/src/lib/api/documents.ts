import apiClient from './client';
import { Document, DocumentListResponse, SearchResponse } from '@/types';

export const documentsApi = {
  upload: async (file: File, onProgress?: (progress: number) => void): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post<Document>('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (onProgress && e.total) onProgress(Math.round((e.loaded * 100) / e.total));
      },
    });
    return response.data;
  },
  list: async (): Promise<DocumentListResponse> => {
    const response = await apiClient.get<DocumentListResponse>('/documents');
    return response.data;
  },
  get: async (documentId: string): Promise<Document> => {
    const response = await apiClient.get<Document>(`/documents/${documentId}`);
    return response.data;
  },
  delete: async (documentId: string): Promise<void> => {
    await apiClient.delete(`/documents/${documentId}`);
  },
  search: async (query: string, topK = 5): Promise<SearchResponse> => {
    const response = await apiClient.post<SearchResponse>('/documents/search', null, {
      params: { query, top_k: topK },
    });
    return response.data;
  },
};
