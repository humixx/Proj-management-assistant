'use client';

import { useEffect } from 'react';
import { useTaskStore } from '@/lib/stores';
import TaskColumn from './TaskColumn';
import { TaskStatus } from '@/types';

const columns: { status: TaskStatus; title: string }[] = [
  { status: 'todo', title: 'To Do' },
  { status: 'in_progress', title: 'In Progress' },
  { status: 'review', title: 'Review' },
  { status: 'done', title: 'Done' },
];

interface TaskBoardProps {
  projectId: string;
}

export default function TaskBoard({ projectId }: TaskBoardProps) {
  const { tasks, isLoading, fetchTasks, getTasksByStatus } = useTaskStore();

  useEffect(() => {
    fetchTasks();
  }, [projectId, fetchTasks]);

  if (isLoading && tasks.length === 0) {
    return <div className="text-center py-12 text-gray-500">Loading tasks...</div>;
  }

  return (
    <div className="flex gap-6 overflow-x-auto pb-6 px-2">
      {columns.map((col) => (
        <TaskColumn key={col.status} status={col.status} title={col.title} tasks={getTasksByStatus(col.status)} />
      ))}
    </div>
  );
}
