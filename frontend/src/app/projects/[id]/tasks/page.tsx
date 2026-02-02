'use client';

import { useParams } from 'next/navigation';
import TaskBoard from '@/components/tasks/TaskBoard';

export default function TasksPage() {
  const params = useParams();
  const projectId = params.id as string;

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Tasks</h1>
        <p className="text-gray-600 mt-1">Manage your project tasks</p>
      </div>
      <TaskBoard projectId={projectId} />
    </div>
  );
}
