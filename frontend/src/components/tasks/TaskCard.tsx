'use client';

import { useState } from 'react';
import { Task, TaskStatus, TaskPriority } from '@/types';
import { useTaskStore } from '@/lib/stores';
import ConfirmDialog from '@/components/ui/ConfirmDialog';

const priorityColors: Record<TaskPriority, string> = {
  low: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-200',
  medium: 'bg-blue-100 text-blue-600 dark:bg-blue-900/40 dark:text-blue-300',
  high: 'bg-orange-100 text-orange-600 dark:bg-orange-900/40 dark:text-orange-300',
  critical: 'bg-red-100 text-red-600 dark:bg-red-900/40 dark:text-red-300',
};

interface TaskCardProps {
  task: Task;
  subtasks?: Task[];
}

export default function TaskCard({ task, subtasks }: TaskCardProps) {
  const { updateTask, deleteTask } = useTaskStore();
  const [isUpdating, setIsUpdating] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [subtasksExpanded, setSubtasksExpanded] = useState(true);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const hasSubtasks = subtasks && subtasks.length > 0;

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

  // Parent task with subtasks — grouped card
  if (hasSubtasks) {
    const doneCount = subtasks.filter((s) => s.status === 'done').length;

    return (
      <div className="rounded-lg border-2 border-indigo-200 dark:border-indigo-700 overflow-hidden shadow-sm">
        {/* Parent task header */}
        <div
          className={`bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/40 dark:to-purple-900/40 p-3 cursor-pointer ${isUpdating ? 'opacity-50' : ''}`}
          onClick={toggleExpand}
        >
          <div className="flex items-start gap-2">
            <div className="flex-shrink-0 mt-0.5">
              <svg className="w-4 h-4 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <div className="flex-1 min-w-0">
              <h4 className={`font-semibold text-sm ${isExpanded ? '' : 'line-clamp-2'}`}>
                {task.title}
              </h4>
              {task.description && isExpanded && (
                <p className="text-xs text-gray-600 dark:text-gray-300 mt-1 whitespace-pre-wrap">{task.description}</p>
              )}
            </div>
          </div>

          <div className="flex items-center justify-between mt-2">
            <div className="flex items-center gap-2">
              <span className={`px-2 py-0.5 text-xs rounded-full font-medium ${priorityColors[task.priority]}`}>
                {task.priority}
              </span>
              <span className="text-xs text-indigo-600 font-medium">
                {doneCount}/{subtasks.length} done
              </span>
            </div>
            <div className="flex items-center gap-2">
              <select
                value={task.status}
                onChange={(e) => {
                  e.stopPropagation();
                  handleStatusChange(e.target.value as TaskStatus);
                }}
                disabled={isUpdating}
                className="text-xs border border-gray-300 dark:border-gray-600 rounded px-2 py-1 bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-medium hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                onClick={(e) => e.stopPropagation()}
              >
                <option value="todo">To Do</option>
                <option value="in_progress">In Progress</option>
                <option value="review">Review</option>
                <option value="done">Done</option>
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

          {/* Progress bar */}
          <div className="mt-2 h-1.5 bg-indigo-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-indigo-500 rounded-full transition-all duration-300"
              style={{ width: `${(doneCount / subtasks.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Subtasks toggle + list */}
        <div className="bg-white dark:bg-gray-900">
          <button
            onClick={() => setSubtasksExpanded(!subtasksExpanded)}
            className="w-full flex items-center gap-1.5 px-3 py-1.5 text-xs text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors border-t border-indigo-100 dark:border-indigo-800"
          >
            <svg className={`w-3 h-3 transition-transform ${subtasksExpanded ? 'rotate-90' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
            </svg>
            <span className="font-medium">Subtasks ({subtasks.length})</span>
          </button>

          {subtasksExpanded && (
            <div className="px-2 pb-2 space-y-1.5">
              {subtasks.map((sub, i) => (
                <SubtaskRow key={sub.id} task={sub} index={i + 1} />
              ))}
            </div>
          )}
        </div>

        <ConfirmDialog
          isOpen={showDeleteConfirm}
          title="Delete Plan"
          message={`Are you sure you want to delete "${task.title}" and all its subtasks? This action cannot be undone.`}
          confirmLabel="Delete"
          variant="danger"
          onConfirm={handleDelete}
          onCancel={() => setShowDeleteConfirm(false)}
          isLoading={isDeleting}
        />
      </div>
    );
  }

  // Regular standalone task card (no subtasks)
  return (
    <div
      className={`bg-white dark:bg-gray-900 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-all cursor-pointer ${isUpdating ? 'opacity-50' : ''}`}
      onClick={toggleExpand}
    >
      <h4 className={`font-medium text-sm mb-2 ${isExpanded ? '' : 'line-clamp-2'}`}>
        {task.title}
      </h4>

      {task.description && (
        <p className={`text-xs text-gray-600 dark:text-gray-300 mb-3 whitespace-pre-wrap ${isExpanded ? '' : 'line-clamp-3'}`}>
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
            className="text-xs border border-gray-300 dark:border-gray-600 rounded px-2 py-1 bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-medium hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
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
        <div className="flex flex-wrap gap-2 text-xs text-gray-500 dark:text-gray-400 border-t border-gray-200 dark:border-gray-700 pt-2">
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
        <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700 text-xs text-gray-400 dark:text-gray-500">
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


/** Compact subtask row inside a parent card */
function SubtaskRow({ task, index }: { task: Task; index: number }) {
  const { updateTask } = useTaskStore();
  const [isUpdating, setIsUpdating] = useState(false);

  const handleStatusChange = async (newStatus: TaskStatus) => {
    if (newStatus === task.status) return;
    setIsUpdating(true);
    await updateTask(task.id, { status: newStatus });
    setIsUpdating(false);
  };

  const isDone = task.status === 'done';

  return (
    <div className={`flex items-center gap-2 rounded-md border px-2.5 py-2 transition-colors ${
      isDone
        ? 'bg-green-50/50 dark:bg-green-900/30 border-green-100 dark:border-green-700'
        : 'bg-gray-50/50 dark:bg-gray-800 border-gray-100 dark:border-gray-700 hover:border-indigo-200 dark:hover:border-indigo-500'
    } ${isUpdating ? 'opacity-50' : ''}`}>
      {/* Step number */}
      <span className={`flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold ${
        isDone ? 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300' : 'bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300'
      }`}>
        {isDone ? (
          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        ) : (
          index
        )}
      </span>

      {/* Title */}
      <span className={`flex-1 text-xs font-medium min-w-0 truncate ${isDone ? 'text-gray-400 dark:text-gray-500 line-through' : 'text-gray-800 dark:text-gray-100'}`}>
        {task.title}
      </span>

      {/* Priority dot */}
      <span className={`w-2 h-2 rounded-full flex-shrink-0 ${
        task.priority === 'critical' ? 'bg-red-400' :
        task.priority === 'high' ? 'bg-orange-400' :
        task.priority === 'medium' ? 'bg-blue-400' : 'bg-gray-300'
      }`} title={task.priority} />

      {/* Status select */}
      <select
        value={task.status}
        onChange={(e) => handleStatusChange(e.target.value as TaskStatus)}
        disabled={isUpdating}
        className="text-[10px] border border-gray-200 dark:border-gray-600 rounded px-1 py-0.5 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 font-medium focus:outline-none focus:ring-1 focus:ring-indigo-400"
      >
        <option value="todo">To Do</option>
        <option value="in_progress">In Progress</option>
        <option value="review">Review</option>
        <option value="done">Done</option>
      </select>
    </div>
  );
}
