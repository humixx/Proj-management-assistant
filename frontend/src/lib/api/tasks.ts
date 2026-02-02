import apiClient from './client';
import { Task, TaskCreate, TaskUpdate, TaskListResponse, BulkTaskCreate, BulkTaskResponse } from '@/types';

export const tasksApi = {
  create: async (data: TaskCreate): Promise<Task> => {
    const response = await apiClient.post<Task>('/tasks', data);
    return response.data;
  },
  bulkCreate: async (data: BulkTaskCreate): Promise<BulkTaskResponse> => {
    const response = await apiClient.post<BulkTaskResponse>('/tasks/bulk', data);
    return response.data;
  },
  list: async (filters?: { status?: string; priority?: string; assignee?: string }): Promise<TaskListResponse> => {
    const response = await apiClient.get<TaskListResponse>('/tasks', { params: filters });
    return response.data;
  },
  get: async (taskId: string): Promise<Task> => {
    const response = await apiClient.get<Task>(`/tasks/${taskId}`);
    return response.data;
  },
  update: async (taskId: string, data: TaskUpdate): Promise<Task> => {
    const response = await apiClient.put<Task>(`/tasks/${taskId}`, data);
    return response.data;
  },
  delete: async (taskId: string): Promise<void> => {
    await apiClient.delete(`/tasks/${taskId}`);
  },
};
