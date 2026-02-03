'use client';

import FileUploader from './FileUploader';
import DocumentList from './DocumentList';

interface DocumentManagerProps {
  projectId: string;
}

export default function DocumentManager({
  projectId,
}: DocumentManagerProps) {
  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Documents</h3>
        <FileUploader />
      </div>

      {/* Documents List */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Uploaded Documents</h3>
        <DocumentList projectId={projectId} />
      </div>
    </div>
  );
}
