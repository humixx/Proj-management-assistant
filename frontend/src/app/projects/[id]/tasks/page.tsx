'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import TaskBoard from '@/components/tasks/TaskBoard';
import TaskModal from '@/components/tasks/TaskModal';
import ChatBubble from '@/components/chat/ChatBubble';
import { useTaskStore } from '@/lib/stores';
import { TaskCreate } from '@/types';

export default function TasksPage() {
  const params = useParams();
  const projectId = params.id as string;
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { createTask } = useTaskStore();

  const handleCreateTask = async (taskData: any) => {
    const payload: TaskCreate = {
      title: taskData.title,
      description: taskData.description || undefined,
      priority: taskData.priority,
      assignee: taskData.assignee || undefined,
      due_date: taskData.due_date || undefined,
    };
    await createTask(payload);
  };

  return (
    <div className="p-4 sm:p-6">
      <div className="mb-4 sm:mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Tasks</h1>
          <p className="text-sm sm:text-base text-gray-600 mt-1">Manage your project tasks</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Create Task
        </button>
      </div>

      <TaskBoard projectId={projectId} />

      <TaskModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleCreateTask}
        projectId={projectId}
      />

      <ChatBubble projectId={projectId} />
    </div>
  );
}
