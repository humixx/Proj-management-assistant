import { useState, useCallback } from 'react';
import { Document } from '@/types/document';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function useDocuments(projectId?: string) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({});

  const fetchDocuments = useCallback(async () => {
    if (!projectId) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/documents`, {
        headers: {
          'X-Project-ID': projectId,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch documents');
      
      const data = await response.json();
      setDocuments(data.documents || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  const uploadDocument = useCallback(async (file: File) => {
    if (!projectId) {
      setError('No project selected');
      return null;
    }

    setError(null);
    setUploadProgress(prev => ({ ...prev, [file.name]: 0 }));

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_URL}/documents/upload`, {
        method: 'POST',
        headers: {
          'X-Project-ID': projectId,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload document');
      }

      const document = await response.json();
      
      setUploadProgress(prev => ({ ...prev, [file.name]: 100 }));
      
      // Remove progress after a short delay
      setTimeout(() => {
        setUploadProgress(prev => {
          const { [file.name]: _, ...rest } = prev;
          return rest;
        });
      }, 2000);

      // Refresh documents list
      await fetchDocuments();

      return document;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
      setUploadProgress(prev => {
        const { [file.name]: _, ...rest } = prev;
        return rest;
      });
      return null;
    }
  }, [projectId, fetchDocuments]);

  const deleteDocument = useCallback(async (documentId: string) => {
    setError(null);

    try {
      const response = await fetch(`${API_URL}/documents/${documentId}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Failed to delete document');

      // Refresh documents list
      await fetchDocuments();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed');
    }
  }, [fetchDocuments]);

  return {
    documents,
    isLoading,
    error,
    uploadProgress,
    fetchDocuments,
    uploadDocument,
    deleteDocument,
  };
}
