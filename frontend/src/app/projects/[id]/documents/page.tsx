'use client';

import { useParams } from 'next/navigation';
import FileUploader from '@/components/documents/FileUploader';
import DocumentList from '@/components/documents/DocumentList';

export default function DocumentsPage() {
  const params = useParams();
  const projectId = params.id as string;

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Documents</h1>
        <p className="text-gray-600">Upload PDF and DOCX files for AI analysis</p>
      </div>

      <div className="bg-white rounded-lg border p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Upload Documents</h2>
        <FileUploader />
      </div>

      <div>
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Uploaded Documents</h2>
        <DocumentList projectId={projectId} />
      </div>
    </div>
  );
}
