'use client';

import { Task, TaskStatus } from '@/types';
import TaskCard from './TaskCard';

interface TaskColumnProps {
  status: TaskStatus;
  title: string;
  tasks: Task[];
}

export default function TaskColumn({ status, title, tasks }: TaskColumnProps) {
  const bgColors: Record<TaskStatus, string> = {
    todo: 'bg-gray-100',
    in_progress: 'bg-blue-50',
    review: 'bg-yellow-50',
    done: 'bg-green-50',
  };

  return (
    <div className="flex-shrink-0 w-80">
      <div className={`rounded-lg ${bgColors[status]} p-4`}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-gray-900 text-base">{title}</h3>
          <span className="px-3 py-1 text-xs bg-white rounded-full font-medium shadow-sm">{tasks.length}</span>
        </div>
        <div className="space-y-3 min-h-[200px] max-h-[calc(100vh-250px)] overflow-y-auto pr-1">
          {tasks.length === 0 ? (
            <div className="text-center py-12 text-gray-400 text-sm">No tasks</div>
          ) : (
            tasks.map((task) => <TaskCard key={task.id} task={task} />)
          )}
        </div>
      </div>
    </div>
  );
}
