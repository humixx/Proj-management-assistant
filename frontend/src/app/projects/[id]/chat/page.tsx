'use client';

import { useEffect } from 'react';
import { useParams } from 'next/navigation';
import { useProjectStore } from '@/lib/stores';
import ChatWindow from '@/components/chat/ChatWindow';

export default function ChatPage() {
  const params = useParams();
  const projectId = params.id as string;
  const { currentProject, projects, selectProject, fetchProjects } = useProjectStore();

  useEffect(() => {
    if (!currentProject || currentProject.id !== projectId) {
      const project = projects.find((p) => p.id === projectId);
      if (project) selectProject(project);
      else fetchProjects();
    }
  }, [projectId, currentProject, projects, selectProject, fetchProjects]);

  if (!currentProject) {
    return <div className="flex items-center justify-center h-full text-gray-500">Loading...</div>;
  }

  return (
    <div className="h-full p-4 sm:p-6">
      <ChatWindow projectId={projectId} />
    </div>
  );
}
