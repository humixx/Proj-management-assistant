'use client';

import { useParams } from 'next/navigation';
import Header from '@/components/layout/Header';
import ProjectNav from '@/components/layout/ProjectNav';
import DocumentManager from '@/components/documents/DocumentManager';

export default function ProjectDocumentsPage() {
  const params = useParams();
  const projectId = params.id as string;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />
      <ProjectNav projectId={projectId} activeTab="documents" />
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Documents</h2>
          <p className="text-gray-600">Manage and organize your project documents</p>
        </div>
        <DocumentManager projectId={projectId} />
      </main>
    </div>
  );
}
