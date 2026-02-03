'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useProjectStore } from '@/lib/stores';

export default function ProjectsPage() {
  const router = useRouter();
  const { currentProject, projects, fetchProjects } = useProjectStore();

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  useEffect(() => {
    // Redirect to current project if exists, otherwise to first project
    if (currentProject) {
      router.push(`/projects/${currentProject.id}/chat`);
    } else if (projects.length > 0) {
      router.push(`/projects/${projects[0].id}/chat`);
    }
  }, [currentProject, projects, router]);

  return (
    <div className="flex items-center justify-center h-full p-4">
      <div className="text-center max-w-md mx-auto">
        <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-4">Welcome to Project Management Assistant</h2>
        <p className="text-sm sm:text-base text-gray-600 mb-8">Create a new project using the sidebar to get started</p>
        <div className="text-gray-400">
          <svg className="mx-auto h-12 w-12 sm:h-16 sm:w-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
      </div>
    </div>
  );
}
