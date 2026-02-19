'use client';

import { useMemo } from 'react';
import { Task, TaskStatus } from '@/types';
import TaskCard from './TaskCard';
import { useTaskStore } from '@/lib/stores';

interface TaskColumnProps {
  status: TaskStatus;
  title: string;
  tasks: Task[];
}

export default function TaskColumn({ status, title, tasks }: TaskColumnProps) {
  const allTasks = useTaskStore((s) => s.tasks);

  const bgColors: Record<TaskStatus, string> = {
    todo: 'bg-gray-100 dark:bg-slate-900/60',
    in_progress: 'bg-blue-50 dark:bg-blue-900/30',
    review: 'bg-yellow-50 dark:bg-yellow-900/25',
    done: 'bg-green-50 dark:bg-green-900/25',
  };

  // Build parent→children map.
  // Subtasks are shown nested under their parent card (in whatever column
  // the PARENT lives in), regardless of the subtask's own status.
  const { topLevel, childrenMap } = useMemo(() => {
    // Build children map from ALL tasks: parent_id → subtask[]
    const cMap = new Map<string, Task[]>();
    for (const t of allTasks) {
      if (t.parent_task_id) {
        const existing = cMap.get(t.parent_task_id) || [];
        existing.push(t);
        cMap.set(t.parent_task_id, existing);
      }
    }

    // Top-level tasks in this column = tasks that have no parent
    // (subtasks are excluded — they render inside their parent's card)
    const top = tasks.filter((t) => !t.parent_task_id);

    return { topLevel: top, childrenMap: cMap };
  }, [tasks, allTasks]);

  const displayCount = topLevel.length;

  return (
    <div className="flex-shrink-0 w-full lg:w-72">
      <div className={`rounded-xl ${bgColors[status]} p-4 shadow-sm`}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-base">{title}</h3>
          <span className="px-3 py-1 text-xs bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 rounded-full font-medium shadow-sm">
            {displayCount}
          </span>
        </div>
        <div className="space-y-3 min-h-[220px] max-h-[calc(100vh-260px)] overflow-y-auto pr-1">
          {topLevel.length === 0 && tasks.length === 0 ? (
            <div className="text-center py-10 text-gray-400 dark:text-gray-500 text-sm">No tasks</div>
          ) : (
            topLevel.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                subtasks={childrenMap.get(task.id)}
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
}
