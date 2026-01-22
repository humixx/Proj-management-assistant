'use client';

import { useParams } from 'next/navigation';
import Header from '@/components/layout/Header';
import ProjectNav from '@/components/layout/ProjectNav';
import ChatWindow from '@/components/chat/ChatWindow';

export default function ProjectChatPage() {
  const params = useParams();
  const projectId = params.id as string;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />
      <ProjectNav projectId={projectId} activeTab="chat" />
      <ChatWindow projectId={projectId} />
    </div>
  );
}
