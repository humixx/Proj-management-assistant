'use client';

import { useEffect, useState } from 'react';
import { Document } from '@/types';
import { useDocumentStore } from '@/lib/stores';
import ConfirmDialog from '@/components/ui/ConfirmDialog';

interface DocumentCardProps {
  document: Document;
}

export default function DocumentCard({ document }: DocumentCardProps) {
  const { deleteDocument, refreshDocument } = useDocumentStore();
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Poll for processing status
  useEffect(() => {
    if (!document.processed) {
      const interval = setInterval(() => refreshDocument(document.id), 3000);
      return () => clearInterval(interval);
    }
  }, [document.id, document.processed, refreshDocument]);

  const handleDelete = async () => {
    setIsDeleting(true);
    await deleteDocument(document.id);
    setIsDeleting(false);
    setShowDeleteConfirm(false);
  };

  const formatSize = (bytes: number | null) => {
    if (!bytes) return 'Unknown';
    const kb = bytes / 1024;
    return kb < 1024 ? `${kb.toFixed(1)} KB` : `${(kb / 1024).toFixed(1)} MB`;
  };

  return (
    <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3">
        <div className="p-2 bg-gray-100 dark:bg-gray-800 rounded-lg">📄</div>
        <div className="flex-1 min-w-0">
          <h3 className="font-medium truncate">{document.filename}</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {formatSize(document.file_size)} • {document.file_type?.toUpperCase()}
          </p>
          <div className="flex items-center gap-1 mt-2 text-xs">
            {document.processed ? (
              <span className="text-green-600 dark:text-green-400">
                ✓ Processed ({document.chunk_count} chunks)
              </span>
            ) : (
              <span className="text-yellow-600 dark:text-yellow-400">⏳ Processing...</span>
            )}
          </div>
        </div>
        <button
          onClick={() => setShowDeleteConfirm(true)}
          disabled={isDeleting}
          className="p-1 text-gray-400 hover:text-red-500 disabled:opacity-50"
        >
          🗑️
        </button>
      </div>

      <ConfirmDialog
        isOpen={showDeleteConfirm}
        title="Delete Document"
        message={`Are you sure you want to delete "${document.filename}"? This will also remove all processed chunks.`}
        confirmLabel="Delete"
        variant="danger"
        onConfirm={handleDelete}
        onCancel={() => setShowDeleteConfirm(false)}
        isLoading={isDeleting}
      />
    </div>
  );
}
