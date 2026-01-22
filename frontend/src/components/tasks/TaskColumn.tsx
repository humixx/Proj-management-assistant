import TaskCard, { Task } from './TaskCard';

interface TaskColumnProps {
  title: string;
  status: Task['status'];
  tasks: Task[];
  onTaskClick: (task: Task) => void;
  onAddTask?: () => void;
}

export default function TaskColumn({
  title,
  status,
  tasks,
  onTaskClick,
  onAddTask,
}: TaskColumnProps) {
  const getStatusColor = (status: Task['status']) => {
    switch (status) {
      case 'todo':
        return 'border-gray-300 bg-gray-50';
      case 'in_progress':
        return 'border-blue-300 bg-blue-50';
      case 'done':
        return 'border-green-300 bg-green-50';
      case 'blocked':
        return 'border-red-300 bg-red-50';
      default:
        return 'border-gray-300 bg-gray-50';
    }
  };

  return (
    <div className={`flex-1 min-w-[280px] rounded-lg border-2 ${getStatusColor(status)}`}>
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-gray-900">{title}</h3>
          <span className="text-sm text-gray-500 bg-white px-2 py-1 rounded-full">
            {tasks.length}
          </span>
        </div>
      </div>
      <div className="p-4 space-y-3 min-h-[200px] max-h-[600px] overflow-y-auto">
        {tasks.map((task) => (
          <TaskCard key={task.id} task={task} onClick={onTaskClick} />
        ))}
        {onAddTask && (
          <button
            onClick={onAddTask}
            className="w-full border-2 border-dashed border-gray-300 rounded-lg p-4 text-sm text-gray-500 hover:border-gray-400 hover:text-gray-600 transition-colors"
          >
            + Add Task
          </button>
        )}
      </div>
    </div>
  );
}
