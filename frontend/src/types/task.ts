export type TaskStatus = 'todo' | 'in_progress' | 'review' | 'done';
export type TaskPriority = 'low' | 'medium' | 'high' | 'critical';

export interface Task {
  id: string;
  project_id: string;
  parent_task_id: string | null;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  assignee: string | null;
  due_date: string | null;
  tags: string[] | null;
  created_at: string;
  updated_at: string | null;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: TaskPriority;
  assignee?: string;
  due_date?: string;
  tags?: string[];
  parent_task_id?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  assignee?: string;
  due_date?: string;
  tags?: string[];
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
}

export interface BulkTaskCreate {
  tasks: TaskCreate[];
}

export interface BulkTaskResponse {
  created: Task[];
  count: number;
}
