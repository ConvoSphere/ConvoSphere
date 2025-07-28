import api from "./api";

// Types
export interface Document {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  file_name: string;
  file_path: string;
  file_type: string;
  file_size: number;
  mime_type: string;
  status: "UPLOADED" | "PROCESSING" | "PROCESSED" | "ERROR" | "REPROCESSING";
  author?: string;
  source?: string;
  language?: string;
  year?: number;
  version?: string;
  keywords?: string[];
  document_type?: string;
  processing_engine?: string;
  processing_options?: Record<string, any>;
  page_count?: number;
  word_count?: number;
  character_count?: number;
  error_message?: string;
  tag_names?: string[];
  created_at: string;
  updated_at: string;
  tags?: Tag[]; // <-- added for frontend compatibility
}

export interface DocumentChunk {
  id: string;
  document_id: string;
  content: string;
  chunk_index: number;
  chunk_size: number;
  token_count: number;
  chunk_type?: string;
  page_number?: number;
  section_title?: string;
  table_id?: string;
  figure_id?: string;
  chunk_metadata?: Record<string, any>;
  created_at: string;
}

export interface Tag {
  id: string;
  name: string;
  description?: string;
  color?: string;
  is_system: boolean;
  usage_count: number;
  created_at: string;
  updated_at: string;
}

export interface SearchResult {
  document: Document;
  chunk: DocumentChunk;
  score: number;
  snippet: string;
}

export interface SearchResponse {
  query: string;
  search_type: string;
  results: SearchResult[];
  total: number;
}

export interface DocumentFilter {
  document_type?: string;
  author?: string;
  year?: number;
  language?: string;
  tag_names?: string[];
  status?: string;
  date_from?: string;
  date_to?: string;
  file_size_min?: number;
  file_size_max?: number;
}

export interface AdvancedSearchRequest {
  query?: string;
  filters?: DocumentFilter;
  sort_by?: string;
  sort_order?: "asc" | "desc";
  page?: number;
  page_size?: number;
}

export interface DocumentProcessingJob {
  id: string;
  document_id: string;
  user_id: string;
  job_type: string;
  status: string;
  priority: number;
  processing_engine?: string;
  processing_options?: Record<string, any>;
  progress: number;
  current_step?: string;
  total_steps?: number;
  error_message?: string;
  retry_count: number;
  max_retries: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

export interface KnowledgeStats {
  total_documents: number;
  total_chunks: number;
  total_tokens: number;
  documents_by_status: Record<string, number>;
  documents_by_type: Record<string, number>;
  storage_used: number;
  last_processed: string;
}

// API Functions
export async function getDocuments(
  filters?: DocumentFilter,
): Promise<Document[]> {
  const params = new URLSearchParams();
  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (Array.isArray(value)) {
          value.forEach((v) => params.append(key, v.toString()));
        } else {
          params.append(key, value.toString());
        }
      }
    });
  }

  const response = await api.get(`/knowledge/documents?${params.toString()}`);
  return response.data.documents || response.data;
}

export async function getDocument(documentId: string): Promise<Document> {
  const response = await api.get(`/knowledge/documents/${documentId}`);
  return response.data;
}

export async function uploadDocument(
  file: File,
  metadata?: Partial<Document>,
): Promise<Document> {
  const formData = new FormData();
  formData.append("file", file);

  // Add required fields
  formData.append("title", metadata?.title || file.name);
  if (metadata?.description) {
    formData.append("description", metadata.description);
  }
  if (metadata?.tags) {
    formData.append("tags", JSON.stringify(metadata.tags));
  }

  const response = await api.post("/knowledge/documents", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function updateDocument(
  documentId: string,
  updates: Partial<Document>,
): Promise<Document> {
  const response = await api.put(`/knowledge/documents/${documentId}`, updates);
  return response.data;
}

export async function deleteDocument(documentId: string): Promise<void> {
  await api.delete(`/knowledge/documents/${documentId}`);
}

export async function searchDocuments(
  query: string,
  searchType: string = "semantic",
): Promise<SearchResponse> {
  const response = await api.post("/knowledge/search", {
    query,
    search_type: searchType,
  });
  return response.data;
}

export async function advancedSearch(
  request: AdvancedSearchRequest,
): Promise<SearchResponse> {
  const response = await api.post("/knowledge/search/advanced", request);
  return response.data;
}

export async function getSearchHistory(): Promise<SearchResponse[]> {
  const response = await api.get("/knowledge/search/history");
  return response.data;
}

export async function getTags(): Promise<Tag[]> {
  const response = await api.get("/knowledge/tags");
  return response.data;
}

export async function searchTags(query: string): Promise<Tag[]> {
  const response = await api.get(
    `/knowledge/tags/search?q=${encodeURIComponent(query)}`,
  );
  return response.data;
}

export async function createTag(tag: Partial<Tag>): Promise<Tag> {
  const response = await api.post("/knowledge/tags", tag);
  return response.data;
}

export async function deleteTag(tagId: string): Promise<void> {
  await api.delete(`/knowledge/tags/${tagId}`);
}

export async function getProcessingJobs(): Promise<DocumentProcessingJob[]> {
  const response = await api.get("/knowledge/processing/jobs");
  return response.data;
}

export async function createProcessingJob(
  job: Partial<DocumentProcessingJob>,
): Promise<DocumentProcessingJob> {
  const response = await api.post("/knowledge/processing/jobs", job);
  return response.data;
}

export async function bulkImport(
  files: File[],
): Promise<DocumentProcessingJob> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append("files", file);
  });

  const response = await api.post("/knowledge/bulk-import", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function getKnowledgeStats(): Promise<KnowledgeStats> {
  const response = await api.get("/knowledge/stats");
  return response.data;
}

// Upload with progress tracking
export async function uploadDocumentWithProgress(
  file: File,
  metadata?: Partial<Document>,
  onProgress?: (progress: number) => void,
): Promise<Document> {
  const formData = new FormData();
  formData.append("file", file);

  if (metadata) {
    formData.append("metadata", JSON.stringify(metadata));
  }

  const response = await api.post("/knowledge/documents", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const progress = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total,
        );
        onProgress(progress);
      }
    },
  });
  return response.data;
}

// Bulk upload with progress tracking
export async function bulkUploadWithProgress(
  files: File[],
  onProgress?: (fileIndex: number, progress: number) => void,
): Promise<Document[]> {
  const results: Document[] = [];

  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    try {
      const document = await uploadDocumentWithProgress(
        file,
        undefined,
        (progress) => onProgress?.(i, progress),
      );
      results.push(document);
    } catch (_error) {
      console.error(`Failed to upload ${file.name}:`, _error);
      throw _error;
    }
  }

  return results;
}
