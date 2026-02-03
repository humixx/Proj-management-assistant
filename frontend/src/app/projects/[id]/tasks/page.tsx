'use client';

import { useParams } from 'next/navigation';
import TaskBoard from '@/components/tasks/TaskBoard';

export default function TasksPage() {
  const params = useParams();
  const projectId = params.id as string;

  return (
    <div className="p-4 sm:p-6">
      <div className="mb-4 sm:mb-6">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Tasks</h1>
        <p className="text-sm sm:text-base text-gray-600 mt-1">Manage your project tasks</p>
      </div>
      <TaskBoard projectId={projectId} />
    </div>
  );
}
