'use client';

import { useState } from 'react';
import FileUploader from './FileUploader';
import DocumentList, { Document } from './DocumentList';

interface DocumentManagerProps {
  projectId: string;
  initialDocuments?: Document[];
}

export default function DocumentManager({
  projectId,
  initialDocuments = [],
}: DocumentManagerProps) {
  const [documents, setDocuments] = useState<Document[]>(initialDocuments);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileSelect = async (files: File[]) => {
    setIsUploading(true);

    // Create document entries for each file
    const newDocuments: Document[] = files.map((file) => ({
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      name: file.name,
      type: file.type || 'application/octet-stream',
      size: file.size,
      uploadedAt: new Date(),
      status: 'processing' as const,
    }));

    setDocuments((prev) => [...newDocuments, ...prev]);

    try {
      // TODO: Upload files to backend API
      // const formData = new FormData();
      // files.forEach((file) => formData.append('files', file));
      // formData.append('projectId', projectId);
      
      // const response = await fetch(`/api/projects/${projectId}/documents`, {
      //   method: 'POST',
      //   body: formData,
      // });
      // const data = await response.json();

      // Simulate upload delay
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // Update document status to completed
      setDocuments((prev) =>
        prev.map((doc) =>
          newDocuments.some((newDoc) => newDoc.id === doc.id)
            ? { ...doc, status: 'completed' as const }
            : doc
        )
      );
    } catch (error) {
      console.error('Error uploading files:', error);
      // Update document status to failed
      setDocuments((prev) =>
        prev.map((doc) =>
          newDocuments.some((newDoc) => newDoc.id === doc.id)
            ? { ...doc, status: 'failed' as const }
            : doc
        )
      );
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      // TODO: Delete from backend API
      // await fetch(`/api/projects/${projectId}/documents/${id}`, {
      //   method: 'DELETE',
      // });

      setDocuments((prev) => prev.filter((doc) => doc.id !== id));
    } catch (error) {
      console.error('Error deleting document:', error);
      // TODO: Show error message to user
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Documents</h3>
        <FileUploader
          onFileSelect={handleFileSelect}
          disabled={isUploading}
        />
      </div>

      {/* Documents List */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            Documents ({documents.length})
          </h3>
        </div>
        <DocumentList documents={documents} onDelete={handleDelete} />
      </div>
    </div>
  );
}

