'use client';

import { useState } from 'react';
import { Task, TaskStatus, TaskPriority } from '@/types';
import { useTaskStore } from '@/lib/stores';
import ConfirmDialog from '@/components/ui/ConfirmDialog';

const priorityColors: Record<TaskPriority, string> = {
  low: 'bg-gray-100 text-gray-600',
  medium: 'bg-blue-100 text-blue-600',
  high: 'bg-orange-100 text-orange-600',
  critical: 'bg-red-100 text-red-600',
};

interface TaskCardProps {
  task: Task;
}

export default function TaskCard({ task }: TaskCardProps) {
  const { updateTask, deleteTask } = useTaskStore();
  const [isUpdating, setIsUpdating] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleStatusChange = async (newStatus: TaskStatus) => {
    if (newStatus === task.status) return;
    setIsUpdating(true);
    await updateTask(task.id, { status: newStatus });
    setIsUpdating(false);
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    await deleteTask(task.id);
    setIsDeleting(false);
    setShowDeleteConfirm(false);
  };

  const toggleExpand = () => setIsExpanded(!isExpanded);

  return (
    <div 
      className={`bg-white rounded-lg p-4 shadow-sm border hover:shadow-md transition-all cursor-pointer ${isUpdating ? 'opacity-50' : ''}`}
      onClick={toggleExpand}
    >
      <h4 className={`font-medium text-gray-900 text-sm mb-2 ${isExpanded ? '' : 'line-clamp-2'}`}>
        {task.title}
      </h4>
      
      {task.description && (
        <p className={`text-xs text-gray-600 mb-3 whitespace-pre-wrap ${isExpanded ? '' : 'line-clamp-3'}`}>
          {task.description}
        </p>
      )}

      <div className="flex items-center justify-between mb-2">
        <span className={`px-2 py-1 text-xs rounded-full font-medium ${priorityColors[task.priority]}`}>
          {task.priority}
        </span>
        <div className="flex items-center gap-2">
          <select
            value={task.status}
            onChange={(e) => {
              e.stopPropagation();
              handleStatusChange(e.target.value as TaskStatus);
            }}
            disabled={isUpdating}
            className="text-xs border border-gray-300 rounded px-2 py-1 bg-white text-gray-900 font-medium hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            onClick={(e) => e.stopPropagation()}
          >
            <option value="todo" className="text-gray-900">To Do</option>
            <option value="in_progress" className="text-gray-900">In Progress</option>
            <option value="review" className="text-gray-900">Review</option>
            <option value="done" className="text-gray-900">Done</option>
          </select>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowDeleteConfirm(true);
            }}
            disabled={isDeleting}
            className="p-1 text-gray-400 hover:text-red-500 disabled:opacity-50 text-sm"
          >
            🗑️
          </button>
        </div>
      </div>

      {(task.assignee || task.due_date) && (
        <div className="flex flex-wrap gap-2 text-xs text-gray-500 border-t pt-2">
          {task.assignee && (
            <span className="flex items-center gap-1">
              <span className="font-medium">👤</span>
              {task.assignee}
            </span>
          )}
          {task.due_date && (
            <span className="flex items-center gap-1">
              <span className="font-medium">📅</span>
              {new Date(task.due_date).toLocaleDateString()}
            </span>
          )}
        </div>
      )}

      {isExpanded && (
        <div className="mt-2 pt-2 border-t text-xs text-gray-400">
          Click to collapse
        </div>
      )}

      <ConfirmDialog
        isOpen={showDeleteConfirm}
        title="Delete Task"
        message={`Are you sure you want to delete "${task.title}"? This action cannot be undone.`}
        confirmLabel="Delete"
        variant="danger"
        onConfirm={handleDelete}
        onCancel={() => setShowDeleteConfirm(false)}
        isLoading={isDeleting}
      />
    </div>
  );
}
