import { create } from "zustand";
import type {
  Document,
  Tag,
  SearchResponse,
  DocumentFilter,
  AdvancedSearchRequest,
  DocumentProcessingJob,
  KnowledgeStats,
} from "../services/knowledge";
import {
  getDocuments,
  getTags,
  searchDocuments,
  advancedSearch,
  getSearchHistory,
  getProcessingJobs,
  getKnowledgeStats,
  uploadDocumentWithProgress,
  bulkUploadWithProgress,
  uploadDocument,
  updateDocument,
  deleteDocument,
} from "../services/knowledge";
import api from "../services/api";

interface UploadItem {
  id: string;
  file: File;
  progress: number;
  status: "pending" | "uploading" | "completed" | "error";
  error?: string;
  document?: Document;
}

interface KnowledgeState {
  // Documents
  documents: Document[];
  documentsLoading: boolean;
  documentsError: string | null;

  // Tags
  tags: Tag[];
  tagsLoading: boolean;
  tagsError: string | null;
  documentTypes: string[];

  // Search
  searchResults: SearchResponse | null;
  searchLoading: boolean;
  searchError: string | null;
  searchHistory: SearchResponse[];

  // Filters
  currentFilters: DocumentFilter;
  appliedFilters: DocumentFilter;

  // Upload
  uploadQueue: UploadItem[];
  uploadProgress: number;

  // Processing Jobs
  processingJobs: DocumentProcessingJob[];
  jobsLoading: boolean;

  // Statistics
  stats: KnowledgeStats | null;
  statsLoading: boolean;

  // Actions
  fetchDocuments: (filters?: DocumentFilter) => Promise<void>;
  fetchTags: () => Promise<void>;
  search: (query: string, searchType?: string) => Promise<void>;
  advancedSearch: (request: AdvancedSearchRequest) => Promise<void>;
  fetchSearchHistory: () => Promise<void>;
  fetchProcessingJobs: () => Promise<void>;
  fetchStats: () => Promise<void>;
  getTags: () => Promise<void>;
  getDocuments: () => Promise<void>;
  
  // Document actions
  uploadDocument: (file: File, metadata?: Partial<Document>) => Promise<Document>;
  updateDocument: (documentId: string, updates: Partial<Document>) => Promise<Document>;
  deleteDocument: (documentId: string) => Promise<void>;
  downloadDocument: (documentId: string) => Promise<void>;
  reprocessDocument: (documentId: string) => Promise<void>;
  bulkUpdateDocuments: (documentIds: string[], updates: Partial<Document>) => Promise<void>;

  // Upload actions
  addToUploadQueue: (files: File[]) => void;
  removeFromUploadQueue: (id: string) => void;
  uploadFile: (item: UploadItem) => Promise<void>;
  uploadFiles: (files: File[]) => Promise<void>;
  clearUploadQueue: () => void;

  // Filter actions
  setFilters: (filters: DocumentFilter) => void;
  applyFilters: () => Promise<void>;
  clearFilters: () => void;

  // Utility actions
  refreshDocuments: () => Promise<void>;
  refreshTags: () => Promise<void>;
  clearSearchResults: () => void;
  clearErrors: () => void;
}

export const useKnowledgeStore = create<KnowledgeState>((set, get) => ({
  // Initial state
  documents: [],
  documentsLoading: false,
  documentsError: null,

  tags: [],
  documentTypes: [],
  tagsLoading: false,
  tagsError: null,

  searchResults: null,
  searchLoading: false,
  searchError: null,
  searchHistory: [],

  currentFilters: {},
  appliedFilters: {},

  uploadQueue: [],
  uploadProgress: 0,

  processingJobs: [],
  jobsLoading: false,

  stats: null,
  statsLoading: false,

  // Document actions
  fetchDocuments: async (filters?: DocumentFilter) => {
    set({ documentsLoading: true, documentsError: null });
    try {
      const documents = await getDocuments(filters);
      set({ documents, documentsLoading: false });
    } catch (error) {
      set({
        documentsError:
          error instanceof Error ? error.message : "Failed to fetch documents",
        documentsLoading: false,
      });
    }
  },

  fetchTags: async () => {
    set({ tagsLoading: true, tagsError: null });
    try {
      const tags = await getTags();
      set({ tags, tagsLoading: false });
    } catch (error) {
      set({
        tagsError:
          error instanceof Error ? error.message : "Failed to fetch tags",
        tagsLoading: false,
      });
    }
  },

  // Search actions
  search: async (query: string, searchType: string = "semantic") => {
    set({ searchLoading: true, searchError: null });
    try {
      const results = await searchDocuments(query, searchType);
      set({ searchResults: results, searchLoading: false });
    } catch (error) {
      set({
        searchError: error instanceof Error ? error.message : "Search failed",
        searchLoading: false,
      });
    }
  },

  advancedSearch: async (request: AdvancedSearchRequest) => {
    set({ searchLoading: true, searchError: null });
    try {
      const results = await advancedSearch(request);
      set({ searchResults: results, searchLoading: false });
    } catch (error) {
      set({
        searchError:
          error instanceof Error ? error.message : "Advanced search failed",
        searchLoading: false,
      });
    }
  },

  fetchSearchHistory: async () => {
    try {
      const history = await getSearchHistory();
      set({ searchHistory: history });
    } catch (error) {
      console.error("Failed to fetch search history:", error);
    }
  },

  fetchProcessingJobs: async () => {
    set({ jobsLoading: true });
    try {
      const jobs = await getProcessingJobs();
      set({ processingJobs: jobs, jobsLoading: false });
    } catch (error) {
      console.error("Failed to fetch processing jobs:", error);
      set({ jobsLoading: false });
    }
  },

  fetchStats: async () => {
    set({ statsLoading: true });
    try {
      const stats = await getKnowledgeStats();
      set({ stats, statsLoading: false });
    } catch (error) {
      console.error("Failed to fetch stats:", error);
      set({ statsLoading: false });
    }
  },

  getTags: async () => {
    await get().fetchTags();
  },

  getDocuments: async () => {
    await get().fetchDocuments();
  },

  // Document actions
  uploadDocument: async (file: File, metadata?: Partial<Document>) => {
    try {
      const document = await uploadDocument(file, metadata);
      // Refresh documents list
      await get().fetchDocuments();
      return document;
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : "Upload failed");
    }
  },

  updateDocument: async (documentId: string, updates: Partial<Document>) => {
    try {
      const document = await updateDocument(documentId, updates);
      // Update document in list
      const { documents } = get();
      const updatedDocuments = documents.map(doc =>
        doc.id === documentId ? document : doc
      );
      set({ documents: updatedDocuments });
      return document;
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : "Update failed");
    }
  },

  deleteDocument: async (documentId: string) => {
    try {
      await deleteDocument(documentId);
      // Remove document from list
      const { documents } = get();
      const updatedDocuments = documents.filter(doc => doc.id !== documentId);
      set({ documents: updatedDocuments });
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : "Delete failed");
    }
  },

  downloadDocument: async (documentId: string) => {
    try {
      const response = await api.get(`/knowledge/documents/${documentId}/download`, {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `document-${documentId}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : "Download failed");
    }
  },

  reprocessDocument: async (documentId: string) => {
    try {
      await api.post(`/knowledge/documents/${documentId}/reprocess`);
      // Refresh documents to get updated status
      await get().fetchDocuments();
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : "Reprocess failed");
    }
  },

  bulkUpdateDocuments: async (documentIds: string[], updates: Partial<Document>) => {
    try {
      // Update each document individually
      const updatePromises = documentIds.map(id => updateDocument(id, updates));
      await Promise.all(updatePromises);
      
      // Refresh documents to get updated data
      await get().fetchDocuments();
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : "Bulk update failed");
    }
  },

  // Upload actions
  addToUploadQueue: (files: File[]) => {
    const newItems: UploadItem[] = files.map((file) => ({
      id: `${Date.now()}-${Math.random()}`,
      file,
      progress: 0,
      status: "pending",
    }));

    set((state) => ({
      uploadQueue: [...state.uploadQueue, ...newItems],
    }));
  },

  removeFromUploadQueue: (id: string) => {
    set((state) => ({
      uploadQueue: state.uploadQueue.filter((item) => item.id !== id),
    }));
  },

  uploadFile: async (item: UploadItem) => {
    set((state) => ({
      uploadQueue: state.uploadQueue.map((queueItem) =>
        queueItem.id === item.id
          ? { ...queueItem, status: "uploading" }
          : queueItem,
      ),
    }));

    try {
      const document = await uploadDocumentWithProgress(
        item.file,
        undefined,
        (progress) => {
          set((state) => ({
            uploadQueue: state.uploadQueue.map((queueItem) =>
              queueItem.id === item.id ? { ...queueItem, progress } : queueItem,
            ),
          }));
        },
      );

      set((state) => ({
        uploadQueue: state.uploadQueue.map((queueItem) =>
          queueItem.id === item.id
            ? { ...queueItem, status: "completed", document }
            : queueItem,
        ),
        documents: [document, ...state.documents],
      }));
    } catch (error) {
      set((state) => ({
        uploadQueue: state.uploadQueue.map((queueItem) =>
          queueItem.id === item.id
            ? {
                ...queueItem,
                status: "error",
                error: error instanceof Error ? error.message : "Upload failed",
              }
            : queueItem,
        ),
      }));
    }
  },

  uploadFiles: async (files: File[]) => {
    const { addToUploadQueue, uploadQueue } = get();
    addToUploadQueue(files);

    const newItems = uploadQueue.filter((item) =>
      files.some((file) => file === item.file),
    );

    for (const item of newItems) {
      await get().uploadFile(item);
    }
  },

  clearUploadQueue: () => {
    set({ uploadQueue: [] });
  },

  // Filter actions
  setFilters: (filters: DocumentFilter) => {
    set({ currentFilters: filters });
  },

  applyFilters: async () => {
    const { currentFilters, fetchDocuments } = get();
    set({ appliedFilters: currentFilters });
    await fetchDocuments(currentFilters);
  },

  clearFilters: () => {
    set({ currentFilters: {}, appliedFilters: {} });
    get().fetchDocuments();
  },

  // Utility actions
  refreshDocuments: async () => {
    const { appliedFilters, fetchDocuments } = get();
    await fetchDocuments(appliedFilters);
  },

  refreshTags: async () => {
    await get().fetchTags();
  },

  clearSearchResults: () => {
    set({ searchResults: null, searchError: null });
  },

  clearErrors: () => {
    set({
      documentsError: null,
      tagsError: null,
      searchError: null,
    });
  },

  getTags: async () => {
    // Placeholder: fetch tags and set state
    try {
      const tags = await getTags();
      set({ tags });
    } catch (error) {
      set({ tags: [] });
    }
  },
  getDocuments: async () => {
    // Placeholder: fetch documents and set state
    try {
      const documents = await getDocuments();
      set({ documents });
    } catch (error) {
      set({ documents: [] });
    }
  },
}));

// Selectors for better performance
export const useDocuments = () =>
  useKnowledgeStore((state) => ({
    documents: state.documents,
    loading: state.documentsLoading,
    error: state.documentsError,
  }));

export const useTags = () =>
  useKnowledgeStore((state) => ({
    tags: state.tags,
    loading: state.tagsLoading,
    error: state.tagsError,
  }));

export const useSearch = () =>
  useKnowledgeStore((state) => ({
    results: state.searchResults,
    loading: state.searchLoading,
    error: state.searchError,
    history: state.searchHistory,
  }));

export const useUpload = () =>
  useKnowledgeStore((state) => ({
    queue: state.uploadQueue,
    progress: state.uploadProgress,
  }));

export const useFilters = () =>
  useKnowledgeStore((state) => ({
    current: state.currentFilters,
    applied: state.appliedFilters,
  }));

export const useStats = () =>
  useKnowledgeStore((state) => ({
    stats: state.stats,
    loading: state.statsLoading,
    fetchStats: state.fetchStats,
  }));
