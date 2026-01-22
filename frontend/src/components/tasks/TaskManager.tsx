'use client';

import { useState, useMemo } from 'react';
import TaskBoard from './TaskBoard';
import TaskFilters from './TaskFilters';
import TaskModal from './TaskModal';
import { Task } from './TaskCard';

interface TaskManagerProps {
  projectId: string;
  initialTasks?: Task[];
}

export default function TaskManager({
  projectId,
  initialTasks = [],
}: TaskManagerProps) {
  const [tasks, setTasks] = useState<Task[]>(initialTasks);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | undefined>(undefined);
  const [filters, setFilters] = useState<{
    status?: string;
    priority?: string;
    assignee?: string;
  }>({});

  const filteredTasks = useMemo(() => {
    return tasks.filter((task) => {
      if (filters.status && task.status !== filters.status) return false;
      if (filters.priority && task.priority !== filters.priority) return false;
      if (filters.assignee && task.assignee !== filters.assignee) return false;
      return true;
    });
  }, [tasks, filters]);

  const assignees = useMemo(() => {
    const uniqueAssignees = new Set(
      tasks.map((task) => task.assignee).filter(Boolean) as string[]
    );
    return Array.from(uniqueAssignees);
  }, [tasks]);

  const handleTaskClick = (task: Task) => {
    setSelectedTask(task);
    setIsModalOpen(true);
  };

  const handleAddTask = (status: Task['status']) => {
    setSelectedTask(undefined);
    setIsModalOpen(true);
    // Set default status if creating from a column
    if (status) {
      // This will be handled in the modal's useEffect
    }
  };

  const handleSaveTask = async (taskData: Omit<Task, 'id' | 'createdAt' | 'updatedAt'>) => {
    try {
      if (selectedTask) {
        // Update existing task
        // TODO: Call backend API
        // await fetch(`/api/projects/${projectId}/tasks/${selectedTask.id}`, {
        //   method: 'PUT',
        //   headers: { 'Content-Type': 'application/json' },
        //   body: JSON.stringify(taskData),
        // });

        setTasks((prev) =>
          prev.map((task) =>
            task.id === selectedTask.id
              ? {
                  ...task,
                  ...taskData,
                  updatedAt: new Date(),
                }
              : task
          )
        );
      } else {
        // Create new task
        // TODO: Call backend API
        // const response = await fetch(`/api/projects/${projectId}/tasks`, {
        //   method: 'POST',
        //   headers: { 'Content-Type': 'application/json' },
        //   body: JSON.stringify(taskData),
        // });
        // const newTask = await response.json();

        const newTask: Task = {
          id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
          ...taskData,
          createdAt: new Date(),
          updatedAt: new Date(),
        };

        setTasks((prev) => [...prev, newTask]);
      }
    } catch (error) {
      console.error('Error saving task:', error);
      // TODO: Show error message to user
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    if (!confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      // TODO: Call backend API
      // await fetch(`/api/projects/${projectId}/tasks/${taskId}`, {
      //   method: 'DELETE',
      // });

      setTasks((prev) => prev.filter((task) => task.id !== taskId));
    } catch (error) {
      console.error('Error deleting task:', error);
      // TODO: Show error message to user
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Tasks ({filteredTasks.length})
          </h3>
        </div>
        <button
          onClick={() => handleAddTask('todo')}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm"
        >
          + New Task
        </button>
      </div>

      <TaskFilters
        filters={filters}
        onFilterChange={setFilters}
        assignees={assignees}
      />

      <TaskBoard
        tasks={filteredTasks}
        onTaskClick={handleTaskClick}
        onAddTask={handleAddTask}
      />

      <TaskModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedTask(undefined);
        }}
        onSave={handleSaveTask}
        task={selectedTask}
        projectId={projectId}
      />
    </div>
  );
}

