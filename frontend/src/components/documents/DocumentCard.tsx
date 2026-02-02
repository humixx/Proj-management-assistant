'use client';

import { useEffect, useState } from 'react';
import { Document } from '@/types';
import { useDocumentStore } from '@/lib/stores';

interface DocumentCardProps {
  document: Document;
}

export default function DocumentCard({ document }: DocumentCardProps) {
  const { deleteDocument, refreshDocument } = useDocumentStore();
  const [isDeleting, setIsDeleting] = useState(false);

  // Poll for processing status
  useEffect(() => {
    if (!document.processed) {
      const interval = setInterval(() => refreshDocument(document.id), 3000);
      return () => clearInterval(interval);
    }
  }, [document.id, document.processed, refreshDocument]);

  const handleDelete = async () => {
    if (!confirm('Delete this document?')) return;
    setIsDeleting(true);
    await deleteDocument(document.id);
  };

  const formatSize = (bytes: number | null) => {
    if (!bytes) return 'Unknown';
    const kb = bytes / 1024;
    return kb < 1024 ? `${kb.toFixed(1)} KB` : `${(kb / 1024).toFixed(1)} MB`;
  };

  return (
    <div className="bg-white border rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3">
        <div className="p-2 bg-gray-100 rounded-lg">📄</div>
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-gray-900 truncate">{document.filename}</h3>
          <p className="text-sm text-gray-500">{formatSize(document.file_size)} • {document.file_type?.toUpperCase()}</p>
          <div className="flex items-center gap-1 mt-2 text-xs">
            {document.processed ? (
              <span className="text-green-600">✓ Processed ({document.chunk_count} chunks)</span>
            ) : (
              <span className="text-yellow-600">⏳ Processing...</span>
            )}
          </div>
        </div>
        <button
          onClick={handleDelete}
          disabled={isDeleting}
          className="p-1 text-gray-400 hover:text-red-500 disabled:opacity-50"
        >
          🗑️
        </button>
      </div>
    </div>
  );
}
