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
    return <div className="text-center py-12 text-gray-500 dark:text-gray-400">Loading tasks...</div>;
  }

  const totalTasks = tasks.length;

  // Show empty state for completely empty board
  if (!isLoading && totalTasks === 0) {
    return (
      <div className="flex flex-col lg:flex-row gap-4 overflow-x-auto pb-4">
        {columns.map((col) => (
          <div key={col.status} className="w-full lg:w-72 lg:flex-shrink-0">
            <div className="rounded-lg bg-gray-50 dark:bg-gray-900 p-3 border-2 border-dashed border-gray-200 dark:border-gray-700">
              <h3 className="font-medium text-gray-400 dark:text-gray-500 mb-3">{col.title}</h3>
              <div className="text-center py-8 text-gray-400 dark:text-gray-500 text-sm">
                No tasks
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="flex flex-col lg:flex-row gap-6 lg:gap-8 overflow-x-auto pb-6 pt-2 px-4">
      {columns.map((col) => (
        <div key={col.status} className="w-full lg:w-72 lg:flex-shrink-0">
          <TaskColumn status={col.status} title={col.title} tasks={getTasksByStatus(col.status)} />
        </div>
      ))}
    </div>
  );
}
