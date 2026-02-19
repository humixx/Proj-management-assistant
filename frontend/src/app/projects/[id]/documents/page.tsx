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
    <div className="p-4 sm:p-6 space-y-4 sm:space-y-6 text-foreground">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold mb-2">Documents</h1>
        <p className="text-sm sm:text-base text-gray-600 dark:text-gray-300">Upload PDF and DOCX files for AI analysis</p>
      </div>

      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4 sm:p-6">
        <h2 className="text-lg sm:text-xl font-semibold mb-4">Upload Documents</h2>
        <FileUploader />
      </div>

      <div>
        <h2 className="text-lg sm:text-xl font-semibold mb-4">Uploaded Documents</h2>
        <DocumentList projectId={projectId} />
      </div>
    </div>
  );
}
