import TaskColumn, { Task } from './TaskColumn';

interface TaskBoardProps {
  tasks: Task[];
  onTaskClick: (task: Task) => void;
  onAddTask?: (status: Task['status']) => void;
}

export default function TaskBoard({ tasks, onTaskClick, onAddTask }: TaskBoardProps) {
  const columns = [
    { title: 'To Do', status: 'todo' as const },
    { title: 'In Progress', status: 'in_progress' as const },
    { title: 'Done', status: 'done' as const },
    { title: 'Blocked', status: 'blocked' as const },
  ];

  const getTasksByStatus = (status: Task['status']) => {
    return tasks.filter((task) => task.status === status);
  };

  return (
    <div className="flex space-x-4 overflow-x-auto pb-4">
      {columns.map((column) => (
        <TaskColumn
          key={column.status}
          title={column.title}
          status={column.status}
          tasks={getTasksByStatus(column.status)}
          onTaskClick={onTaskClick}
          onAddTask={onAddTask ? () => onAddTask(column.status) : undefined}
        />
      ))}
    </div>
  );
}
