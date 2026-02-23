import apiClient from './client';
import { Project, ProjectCreate, ProjectUpdate, ProjectListResponse } from '@/types';

export const projectsApi = {
  create: async (data: ProjectCreate): Promise<Project> => {
    const response = await apiClient.post<Project>('/projects', data);
    return response.data;
  },
  list: async (): Promise<ProjectListResponse> => {
    const response = await apiClient.get<ProjectListResponse>('/projects');
    return response.data;
  },
  get: async (projectId: string): Promise<Project> => {
    const response = await apiClient.get<Project>(`/projects/${projectId}`);
    return response.data;
  },
  update: async (projectId: string, data: ProjectUpdate): Promise<Project> => {
    const response = await apiClient.put<Project>(`/projects/${projectId}`, data);
    return response.data;
  },
  delete: async (projectId: string): Promise<void> => {
    await apiClient.delete(`/projects/${projectId}`);
  },
  validateLLMKey: async (
    projectId: string,
    provider: string,
    apiKey: string,
  ): Promise<{ valid: boolean; message: string }> => {
    const response = await apiClient.post<{ valid: boolean; message: string }>(
      `/projects/${projectId}/validate-llm`,
      { provider, api_key: apiKey },
    );
    return response.data;
  },
};
