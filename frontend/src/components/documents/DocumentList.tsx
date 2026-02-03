'use client';

import { useEffect } from 'react';
import { useDocumentStore, useProjectStore } from '@/lib/stores';
import DocumentCard from './DocumentCard';
import { NoDocumentsEmpty } from '@/components/ui/EmptyState';

interface DocumentListProps {
  projectId: string;
}

export default function DocumentList({ projectId }: DocumentListProps) {
  const { documents, isLoading, error, fetchDocuments } = useDocumentStore();
  const { currentProject } = useProjectStore();

  useEffect(() => {
    // Only fetch if we have a current project set
    if (currentProject?.id === projectId) {
      fetchDocuments();
    }
  }, [projectId, currentProject, fetchDocuments]);

  if (isLoading) return <div className="text-center py-8 text-gray-500">Loading documents...</div>;
  if (error) return <div className="text-center py-8 text-red-500">Error: {error}</div>;
  if (documents.length === 0) return <NoDocumentsEmpty />;

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {documents.map((doc) => (
        <DocumentCard key={doc.id} document={doc} />
      ))}
    </div>
  );
}
