export interface Project {
  id: string;
  name: string;
  description: string | null;
  settings: Record<string, any> | null;
  created_at: string;
  updated_at: string | null;
}

export interface ProjectSettings {
  chunk_size?: number;
  chunk_overlap?: number;
  top_k?: number;
  similarity_threshold?: number;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  settings?: ProjectSettings;
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
  settings?: ProjectSettings;
}

export interface ProjectListResponse {
  projects: Project[];
  total: number;
}
