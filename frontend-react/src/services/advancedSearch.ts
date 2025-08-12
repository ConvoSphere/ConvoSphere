import api from "./api";
import config from "../config";

export interface SearchFilter {
  field: string;
  operator: "equals" | "contains" | "in" | "range" | "exists" | "not_exists";
  value: any;
}

export interface SearchQuery {
  query: string;
  filters?: SearchFilter[];
  searchType?: "keyword" | "semantic" | "hybrid" | "vector";
  limit?: number;
  offset?: number;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
  includeMetadata?: boolean;
  includeVectors?: boolean;
}

export interface SearchResult {
  id: string;
  title: string;
  content: string;
  type: "document" | "conversation" | "knowledge" | "assistant";
  score: number;
  metadata: Record<string, any>;
  highlights?: string[];
  vector?: number[];
  createdAt: string;
  updatedAt: string;
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  query: string;
  searchType: string;
  processingTime: number;
  facets?: Record<string, any>;
}

export interface SavedSearch {
  id: string;
  name: string;
  description?: string;
  query: SearchQuery;
  createdAt: string;
  updatedAt: string;
  isPublic: boolean;
  createdBy: string;
}

export interface SearchHistory {
  id: string;
  query: string;
  searchType: string;
  resultsCount: number;
  timestamp: string;
  userId: string;
}

export interface RAGConfig {
  embeddingModel: string;
  chunkSize: number;
  chunkOverlap: number;
  similarityThreshold: number;
  maxResults: number;
  rerankEnabled: boolean;
  rerankModel?: string;
}

export const advancedSearchService = {
  // Perform advanced search
  search: async (searchQuery: SearchQuery): Promise<SearchResponse> => {
    const response = await api.post(
      `${config.apiEndpoints.search}/advanced`,
      searchQuery,
    );
    return response.data;
  },

  // Semantic search
  semanticSearch: async (
    query: string,
    filters?: SearchFilter[],
  ): Promise<SearchResponse> => {
    const response = await api.post(`${config.apiEndpoints.search}/semantic`, {
      query,
      filters,
    });
    return response.data;
  },

  // Vector search
  vectorSearch: async (
    query: string,
    filters?: SearchFilter[],
  ): Promise<SearchResponse> => {
    const response = await api.post(`${config.apiEndpoints.search}/vector`, {
      query,
      filters,
    });
    return response.data;
  },

  // Hybrid search (keyword + semantic)
  hybridSearch: async (
    query: string,
    filters?: SearchFilter[],
  ): Promise<SearchResponse> => {
    const response = await api.post(`${config.apiEndpoints.search}/hybrid`, {
      query,
      filters,
    });
    return response.data;
  },

  // Get search suggestions
  getSuggestions: async (
    query: string,
    limit: number = 10,
  ): Promise<string[]> => {
    const response = await api.get(
      `${config.apiEndpoints.search}/suggestions`,
      {
        params: { q: query, limit },
      },
    );
    return response.data;
  },

  // Get search facets
  getFacets: async (query?: string): Promise<Record<string, any>> => {
    const response = await api.get(`${config.apiEndpoints.search}/facets`, {
      params: { q: query },
    });
    return response.data;
  },

  // Save search
  saveSearch: async (
    savedSearch: Omit<SavedSearch, "id" | "createdAt" | "updatedAt">,
  ): Promise<SavedSearch> => {
    const response = await api.post(
      `${config.apiEndpoints.search}/saved`,
      savedSearch,
    );
    return response.data;
  },

  // Get saved searches
  getSavedSearches: async (): Promise<SavedSearch[]> => {
    const response = await api.get(`${config.apiEndpoints.search}/saved`);
    return response.data;
  },

  // Update saved search
  updateSavedSearch: async (
    id: string,
    updates: Partial<SavedSearch>,
  ): Promise<SavedSearch> => {
    const response = await api.put(
      `${config.apiEndpoints.search}/saved/${id}`,
      updates,
    );
    return response.data;
  },

  // Delete saved search
  deleteSavedSearch: async (id: string): Promise<void> => {
    await api.delete(`${config.apiEndpoints.search}/saved/${id}`);
  },

  // Get search history
  getSearchHistory: async (limit: number = 50): Promise<SearchHistory[]> => {
    const response = await api.get(`${config.apiEndpoints.search}/history`, {
      params: { limit },
    });
    return response.data;
  },

  // Clear search history
  clearSearchHistory: async (): Promise<void> => {
    await api.delete(`${config.apiEndpoints.search}/history`);
  },

  // RAG Configuration
  getRAGConfig: async (): Promise<RAGConfig> => {
    const response = await api.get(`${config.apiEndpoints.rag}/config`);
    return response.data;
  },

  updateRAGConfig: async (config: Partial<RAGConfig>): Promise<RAGConfig> => {
    const response = await api.put(`${config.apiEndpoints.rag}/config`, config);
    return response.data;
  },

  // RAG Search
  ragSearch: async (
    query: string,
    context?: string,
  ): Promise<SearchResponse> => {
    const response = await api.post(`${config.apiEndpoints.rag}/search`, {
      query,
      context,
    });
    return response.data;
  },

  // Get RAG embeddings
  getEmbeddings: async (text: string): Promise<number[]> => {
    const response = await api.post(`${config.apiEndpoints.rag}/embeddings`, {
      text,
    });
    return response.data;
  },

  // Batch embeddings
  getBatchEmbeddings: async (texts: string[]): Promise<number[][]> => {
    const response = await api.post(
      `${config.apiEndpoints.rag}/embeddings/batch`,
      {
        texts,
      },
    );
    return response.data;
  },

  // RAG Index management
  createIndex: async (name: string, config: any): Promise<any> => {
    const response = await api.post(`${config.apiEndpoints.rag}/index`, {
      name,
      config,
    });
    return response.data;
  },

  deleteIndex: async (name: string): Promise<void> => {
    await api.delete(`${config.apiEndpoints.rag}/index/${name}`);
  },

  listIndices: async (): Promise<any[]> => {
    const response = await api.get(`${config.apiEndpoints.rag}/index`);
    return response.data;
  },

  // Index documents
  indexDocuments: async (documents: any[]): Promise<any> => {
    const response = await api.post(
      `${config.apiEndpoints.rag}/index/documents`,
      {
        documents,
      },
    );
    return response.data;
  },

  // Search within specific index
  searchIndex: async (
    indexName: string,
    query: SearchQuery,
  ): Promise<SearchResponse> => {
    const response = await api.post(
      `${config.apiEndpoints.rag}/index/${indexName}/search`,
      query,
    );
    return response.data;
  },

  // Get search statistics
  getSearchStats: async (timeRange?: string): Promise<any> => {
    const response = await api.get(`${config.apiEndpoints.search}/stats`, {
      params: { timeRange },
    });
    return response.data;
  },

  // Export search results
  exportSearchResults: async (
    searchQuery: SearchQuery,
    format: "csv" | "json" = "csv",
  ): Promise<Blob> => {
    const response = await api.post(
      `${config.apiEndpoints.search}/export`,
      {
        ...searchQuery,
        format,
      },
      {
        responseType: "blob",
      },
    );
    return response.data;
  },
};
