import DocumentCard from './DocumentCard';

export interface Document {
  id: string;
  name: string;
  type: string;
  size: number;
  uploadedAt: Date;
  status: 'processing' | 'completed' | 'failed';
}

interface DocumentListProps {
  documents: Document[];
  onDelete: (id: string) => void;
}

export default function DocumentList({ documents, onDelete }: DocumentListProps) {
  if (documents.length === 0) {
    return (
      <div className="text-center py-12">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
        <h3 className="mt-4 text-lg font-medium text-gray-900">No documents yet</h3>
        <p className="mt-2 text-sm text-gray-500">
          Upload documents to get started with document management
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {documents.map((document) => (
        <DocumentCard
          key={document.id}
          id={document.id}
          name={document.name}
          type={document.type}
          size={document.size}
          uploadedAt={document.uploadedAt}
          status={document.status}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
