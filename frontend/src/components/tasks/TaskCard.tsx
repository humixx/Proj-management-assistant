export interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'todo' | 'in_progress' | 'done' | 'blocked';
  priority?: 'low' | 'medium' | 'high';
  assignee?: string;
  dueDate?: Date;
  createdAt: Date;
  updatedAt: Date;
}

interface TaskCardProps {
  task: Task;
  onClick: (task: Task) => void;
}

export default function TaskCard({ task, onClick }: TaskCardProps) {
  const getPriorityColor = (priority?: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div
      onClick={() => onClick(task)}
      className="bg-white border border-gray-200 rounded-lg p-4 cursor-pointer hover:shadow-md transition-shadow"
    >
      <div className="flex items-start justify-between mb-2">
        <h3 className="text-sm font-medium text-gray-900 flex-1">{task.title}</h3>
        {task.priority && (
          <span
            className={`ml-2 px-2 py-1 text-xs font-medium rounded border ${getPriorityColor(
              task.priority
            )}`}
          >
            {task.priority}
          </span>
        )}
      </div>
      {task.description && (
        <p className="text-xs text-gray-600 mb-3 line-clamp-2">{task.description}</p>
      )}
      <div className="flex items-center justify-between text-xs text-gray-500">
        {task.dueDate && (
          <div className="flex items-center space-x-1">
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            <span>{formatDate(task.dueDate)}</span>
          </div>
        )}
        {task.assignee && (
          <div className="flex items-center space-x-1">
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
            <span>{task.assignee}</span>
          </div>
        )}
      </div>
    </div>
  );
}
