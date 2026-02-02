export interface Document {
  id: string;
  project_id: string;
  filename: string;
  file_type: string | null;
  file_size: number | null;
  processed: boolean;
  chunk_count: number;
  created_at: string;
}

export interface DocumentListResponse {
  documents: Document[];
  total: number;
}

export interface SearchResult {
  chunk_text: string;
  document_id: string;
  document_name: string;
  page_number: number | null;
  score: number;
}

export interface SearchResponse {
  results: SearchResult[];
  query: string;
  total: number;
}
