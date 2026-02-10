'use client';

import { useState } from 'react';
import { ProposedTask } from '@/types';

const PRIORITY_STYLES: Record<string, string> = {
  low: 'bg-gray-100 text-gray-700',
  medium: 'bg-blue-100 text-blue-700',
  high: 'bg-orange-100 text-orange-700',
  critical: 'bg-red-100 text-red-700',
};

interface TaskProposalCardProps {
  tasks: ProposedTask[];
  onApprove: (message: string) => void;
  disabled?: boolean;
}

export default function TaskProposalCard({ tasks, onApprove, disabled = false }: TaskProposalCardProps) {
  const [selected, setSelected] = useState<Set<string>>(new Set(tasks.map((t) => t.temp_id)));
  const [acted, setActed] = useState(false);

  const isDisabled = disabled || acted;

  const toggleTask = (tempId: string) => {
    if (isDisabled) return;
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(tempId)) {
        next.delete(tempId);
      } else {
        next.add(tempId);
      }
      return next;
    });
  };

  const toggleAll = () => {
    if (isDisabled) return;
    if (selected.size === tasks.length) {
      setSelected(new Set());
    } else {
      setSelected(new Set(tasks.map((t) => t.temp_id)));
    }
  };

  const handleApprove = () => {
    if (isDisabled || selected.size === 0) return;
    setActed(true);

    const selectedTasks = tasks.filter((t) => selected.has(t.temp_id));
    // Include the full task data in the approval message so the agent
    // can pass it directly to confirm_proposed_tasks without calling list_tasks.
    const taskJson = JSON.stringify(
      selectedTasks.map(({ temp_id, ...rest }) => rest),
    );

    if (selected.size === tasks.length) {
      onApprove(
        `APPROVED. Call confirm_proposed_tasks now with these tasks: ${taskJson}`,
      );
    } else {
      onApprove(
        `APPROVED. Create only the selected tasks. Call confirm_proposed_tasks now with these tasks: ${taskJson}`,
      );
    }
  };

  const handleReject = () => {
    if (isDisabled) return;
    setActed(true);
    onApprove('Rejected. Do not create these tasks.');
  };

  return (
    <div className="mt-3 bg-white border border-gray-200 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 bg-gradient-to-r from-yellow-50 to-orange-50 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-lg">📋</span>
          <span className="font-semibold text-gray-800">
            Proposed Tasks ({tasks.length})
          </span>
        </div>
        {!isDisabled && (
          <button
            onClick={toggleAll}
            className="text-xs text-blue-600 hover:text-blue-800 font-medium"
          >
            {selected.size === tasks.length ? 'Deselect All' : 'Select All'}
          </button>
        )}
      </div>

      {/* Task list */}
      <div className="divide-y divide-gray-100">
        {tasks.map((task) => (
          <div
            key={task.temp_id}
            className={`px-4 py-3 flex items-start gap-3 transition-colors ${
              !isDisabled ? 'hover:bg-gray-50 cursor-pointer' : ''
            } ${!selected.has(task.temp_id) ? 'opacity-50' : ''}`}
            onClick={() => toggleTask(task.temp_id)}
          >
            {/* Checkbox */}
            <div className="flex-shrink-0 mt-0.5">
              <div
                className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                  selected.has(task.temp_id)
                    ? 'bg-blue-600 border-blue-600'
                    : 'border-gray-300 bg-white'
                }`}
              >
                {selected.has(task.temp_id) && (
                  <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                )}
              </div>
            </div>

            {/* Task content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="font-medium text-sm text-gray-900">{task.title}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${PRIORITY_STYLES[task.priority] || PRIORITY_STYLES.medium}`}>
                  {task.priority}
                </span>
              </div>
              {task.description && (
                <p className="text-xs text-gray-500 mt-1 line-clamp-2">{task.description}</p>
              )}
              {(task.assignee || task.due_date) && (
                <div className="flex items-center gap-3 mt-1">
                  {task.assignee && (
                    <span className="text-xs text-gray-400">👤 {task.assignee}</span>
                  )}
                  {task.due_date && (
                    <span className="text-xs text-gray-400">📅 {task.due_date}</span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Action buttons */}
      <div className="px-4 py-3 bg-gray-50 border-t border-gray-200 flex items-center gap-2">
        {acted ? (
          <span className="text-sm text-gray-500 italic">
            {selected.size > 0 ? '✅ Approved' : '❌ Rejected'}
          </span>
        ) : (
          <>
            <button
              onClick={handleApprove}
              disabled={isDisabled || selected.size === 0}
              className="px-4 py-1.5 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {selected.size === tasks.length
                ? 'Approve All'
                : `Approve ${selected.size} Selected`}
            </button>
            <button
              onClick={handleReject}
              disabled={isDisabled}
              className="px-4 py-1.5 bg-white text-red-600 text-sm font-medium rounded-md border border-red-200 hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Reject All
            </button>
            <span className="text-xs text-gray-400 ml-auto">
              Click tasks to select/deselect
            </span>
          </>
        )}
      </div>
    </div>
  );
}
