interface TaskFiltersProps {
  filters: {
    status?: string;
    priority?: string;
    assignee?: string;
  };
  onFilterChange: (filters: {
    status?: string;
    priority?: string;
    assignee?: string;
  }) => void;
  assignees?: string[];
}

export default function TaskFilters({ filters, onFilterChange, assignees = [] }: TaskFiltersProps) {
  return (
    <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4 mb-4">
      <div className="flex flex-wrap items-center gap-4">
        <div>
          <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Status</label>
          <select
            value={filters.status || ''}
            onChange={(e) =>
              onFilterChange({ ...filters, status: e.target.value || undefined })
            }
            className="text-sm text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All Statuses</option>
            <option value="todo">To Do</option>
            <option value="in_progress">In Progress</option>
            <option value="done">Done</option>
            <option value="blocked">Blocked</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Priority</label>
          <select
            value={filters.priority || ''}
            onChange={(e) =>
              onFilterChange({ ...filters, priority: e.target.value || undefined })
            }
            className="text-sm text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All Priorities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Assignee</label>
          <select
            value={filters.assignee || ''}
            onChange={(e) =>
              onFilterChange({ ...filters, assignee: e.target.value || undefined })
            }
            className="text-sm text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All Assignees</option>
            {assignees.map((assignee) => (
              <option key={assignee} value={assignee}>
                {assignee}
              </option>
            ))}
          </select>
        </div>

        <div className="flex-1"></div>

        <button
          onClick={() => onFilterChange({})}
          className="px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:text-gray-900 dark:hover:text-white border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
        >
          Clear Filters
        </button>
      </div>
    </div>
  );
}
