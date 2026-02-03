'use client';

import { useEffect } from 'react';
import { useParams } from 'next/navigation';
import { useProjectStore } from '@/lib/stores';
import FileUploader from '@/components/documents/FileUploader';
import DocumentList from '@/components/documents/DocumentList';

export default function DocumentsPage() {
  const params = useParams();
  const projectId = params.id as string;
  const { projects, selectProject, currentProject } = useProjectStore();

  useEffect(() => {
    // Ensure the current project is selected
    if (projectId && (!currentProject || currentProject.id !== projectId)) {
      const project = projects.find(p => p.id === projectId);
      if (project) {
        selectProject(project);
      }
    }
  }, [projectId, currentProject, projects, selectProject]);

  return (
    <div className="p-4 sm:p-6 space-y-4 sm:space-y-6">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">Documents</h1>
        <p className="text-sm sm:text-base text-gray-600">Upload PDF and DOCX files for AI analysis</p>
      </div>

      <div className="bg-white rounded-lg border p-4 sm:p-6">
        <h2 className="text-lg sm:text-xl font-semibold text-gray-800 mb-4">Upload Documents</h2>
        <FileUploader />
      </div>

      <div>
        <h2 className="text-lg sm:text-xl font-semibold text-gray-800 mb-4">Uploaded Documents</h2>
        <DocumentList projectId={projectId} />
      </div>
    </div>
  );
}
