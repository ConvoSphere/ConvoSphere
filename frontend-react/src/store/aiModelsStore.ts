import { create } from "zustand";
import { config } from "../config";

export interface AIModel {
  id: string;
  name: string;
  provider: string;
  modelId: string;
  displayName: string;
  description: string;
  maxTokens: number;
  costPer1kTokens: number;
  isActive: boolean;
  isDefault: boolean;
  isFavorite: boolean;
  performance: {
    responseTime: number;
    errorRate: number;
    successRate: number;
    totalRequests: number;
  };
  capabilities: string[];
  lastUsed: string;
  createdAt: string;
  updatedAt: string;
}

export interface ModelTest {
  id: string;
  modelId: string;
  prompt: string;
  response: string;
  responseTime: number;
  tokensUsed: number;
  cost: number;
  timestamp: string;
}

export interface ModelCreate {
  name: string;
  provider: string;
  modelId: string;
  displayName: string;
  description?: string;
  maxTokens: number;
  costPer1kTokens: number;
  capabilities?: string[];
  isActive?: boolean;
}

export interface ModelUpdate {
  name?: string;
  provider?: string;
  modelId?: string;
  displayName?: string;
  description?: string;
  maxTokens?: number;
  costPer1kTokens?: number;
  capabilities?: string[];
  isActive?: boolean;
}

interface AIModelsState {
  models: AIModel[];
  selectedModel: AIModel | null;
  testResults: ModelTest[];
  loading: boolean;
  error: string | null;

  // Actions
  fetchModels: () => Promise<void>;
  createModel: (modelData: ModelCreate) => Promise<AIModel>;
  updateModel: (modelId: string, modelData: ModelUpdate) => Promise<AIModel>;
  deleteModel: (modelId: string) => Promise<void>;
  toggleModelActive: (modelId: string) => Promise<void>;
  testModel: (modelId: string, prompt: string) => Promise<ModelTest>;
  setSelectedModel: (model: AIModel | null) => void;
  clearError: () => void;
}

export const useAIModelsStore = create<AIModelsState>((set, get) => ({
  models: [],
  selectedModel: null,
  testResults: [],
  loading: false,
  error: null,

  fetchModels: async () => {
    try {
      set({ loading: true, error: null });
      const response = await fetch(
        `${config.apiUrl}${config.apiEndpoints.assistants}/models`,
      );

      if (!response.ok) {
        throw new Error("Failed to fetch models");
      }

      const models = await response.json();
      set({ models, loading: false });
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : "Failed to fetch models",
        loading: false,
      });
    }
  },

  createModel: async (modelData: ModelCreate) => {
    try {
      set({ loading: true, error: null });
      const response = await fetch(
        `${config.apiUrl}${config.apiEndpoints.assistants}/models`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(modelData),
        },
      );

      if (!response.ok) {
        throw new Error("Failed to create model");
      }

      const newModel = await response.json();
      set((state) => ({
        models: [...state.models, newModel],
        loading: false,
      }));

      return newModel;
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : "Failed to create model",
        loading: false,
      });
      throw error;
    }
  },

  updateModel: async (modelId: string, modelData: ModelUpdate) => {
    try {
      set({ loading: true, error: null });
      const response = await fetch(
        `${config.apiUrl}${config.apiEndpoints.assistants}/models/${modelId}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(modelData),
        },
      );

      if (!response.ok) {
        throw new Error("Failed to update model");
      }

      const updatedModel = await response.json();
      set((state) => ({
        models: state.models.map((model) =>
          model.id === modelId ? updatedModel : model,
        ),
        loading: false,
      }));

      return updatedModel;
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : "Failed to update model",
        loading: false,
      });
      throw error;
    }
  },

  deleteModel: async (modelId: string) => {
    try {
      set({ loading: true, error: null });
      const response = await fetch(
        `${config.apiUrl}${config.apiEndpoints.assistants}/models/${modelId}`,
        {
          method: "DELETE",
        },
      );

      if (!response.ok) {
        throw new Error("Failed to delete model");
      }

      set((state) => ({
        models: state.models.filter((model) => model.id !== modelId),
        loading: false,
      }));
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : "Failed to delete model",
        loading: false,
      });
      throw error;
    }
  },

  toggleModelActive: async (modelId: string) => {
    try {
      set({ loading: true, error: null });
      const currentModel = get().models.find((model) => model.id === modelId);
      if (!currentModel) {
        throw new Error("Model not found");
      }

      const response = await fetch(
        `${config.apiUrl}${config.apiEndpoints.assistants}/models/${modelId}/toggle`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ isActive: !currentModel.isActive }),
        },
      );

      if (!response.ok) {
        throw new Error("Failed to toggle model status");
      }

      const updatedModel = await response.json();
      set((state) => ({
        models: state.models.map((model) =>
          model.id === modelId ? updatedModel : model,
        ),
        loading: false,
      }));
    } catch (error) {
      set({
        error:
          error instanceof Error
            ? error.message
            : "Failed to toggle model status",
        loading: false,
      });
      throw error;
    }
  },

  testModel: async (modelId: string, prompt: string) => {
    try {
      set({ loading: true, error: null });
      const response = await fetch(
        `${config.apiUrl}${config.apiEndpoints.assistants}/models/${modelId}/test`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt }),
        },
      );

      if (!response.ok) {
        throw new Error("Failed to test model");
      }

      const testResult = await response.json();
      set((state) => ({
        testResults: [testResult, ...state.testResults],
        loading: false,
      }));

      return testResult;
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Failed to test model",
        loading: false,
      });
      throw error;
    }
  },

  setSelectedModel: (model: AIModel | null) => {
    set({ selectedModel: model });
  },

  clearError: () => {
    set({ error: null });
  },
}));
