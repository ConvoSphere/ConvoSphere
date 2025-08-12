import { config } from "../config";
import type {
  AIModel,
  ModelCreate,
  ModelUpdate,
  ModelTest,
} from "../store/aiModelsStore";

export interface ModelPerformance {
  latencyMsAvg: number;
  tokensPerSecond: number;
  successRate: number;
  timeframe: string;
}

export interface ModelUsage {
  totalRequests: number;
  totalTokens: number;
  averageTokensPerRequest: number;
  timeframe: string;
}

export interface ModelCosts {
  totalCostUsd: number;
  inputCostUsd: number;
  outputCostUsd: number;
  timeframe: string;
}

export interface ProviderInfo {
  id: string;
  name: string;
  supportedModels: string[];
}

export interface CompareModelsResult {
  differences: Array<{ key: string; a?: unknown; b?: unknown }>;
}

export interface ModelAnalytics {
  byProvider: Record<string, number>;
  byModel: Record<string, number>;
  timeframe: string;
}

class AIModelsService {
  private baseUrl = config.apiUrl;
  private endpoints = config.apiEndpoints;

  /**
   * Fetch all AI models
   */
  async getModels(): Promise<AIModel[]> {
    const response = await fetch(
      `${this.baseUrl}${this.endpoints.assistants}/models`,
    );

    if (!response.ok) {
      throw new Error("Failed to fetch models");
    }

    return response.json();
  }

  /**
   * Get a specific model by ID
   */
  async getModel(modelId: string): Promise<AIModel> {
    const response = await fetch(
      `${this.baseUrl}${this.endpoints.assistants}/models/${modelId}`,
    );

    if (!response.ok) {
      throw new Error("Failed to fetch model");
    }

    return response.json();
  }

  /**
   * Create a new AI model
   */
  async createModel(modelData: ModelCreate): Promise<AIModel> {
    const response = await fetch(
      `${this.baseUrl}${this.endpoints.assistants}/models`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(modelData),
      },
    );

    if (!response.ok) {
      throw new Error("Failed to create model");
    }

    return response.json();
  }

  /**
   * Update an existing AI model
   */
  async updateModel(modelId: string, modelData: ModelUpdate): Promise<AIModel> {
    const response = await fetch(
      `${this.baseUrl}${this.endpoints.assistants}/models/${modelId}`,
      {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(modelData),
      },
    );

    if (!response.ok) {
      throw new Error("Failed to update model");
    }

    return response.json();
  }

  /**
   * Delete an AI model
   */
  async deleteModel(modelId: string): Promise<void> {
    const response = await fetch(
      `${this.baseUrl}${this.endpoints.assistants}/models/${modelId}`,
      {
        method: "DELETE",
      },
    );

    if (!response.ok) {
      throw new Error("Failed to delete model");
    }
  }

  /**
   * Toggle model active status
   */
  async toggleModelActive(
    modelId: string,
    isActive: boolean,
  ): Promise<AIModel> {
    const response = await fetch(
      `${this.baseUrl}${this.endpoints.assistants}/models/${modelId}/toggle`,
      {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ isActive }),
      },
    );

    if (!response.ok) {
      throw new Error("Failed to toggle model status");
    }

    return response.json();
  }

  /**
   * Set model as default
   */
  async setDefaultModel(modelId: string): Promise<AIModel> {
    const response = await fetch(
      `${this.baseUrl}${this.endpoints.assistants}/models/${modelId}/default`,
      {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
      },
    );

    if (!response.ok) {
      throw new Error("Failed to set default model");
    }

    return response.json();
  }

  /**
   * Test a model with a prompt
   */
  async testModel(modelId: string, prompt: string): Promise<ModelTest> {
    const response = await fetch(
      `${this.baseUrl}${this.endpoints.assistants}/models/${modelId}/test`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      },
    );

    if (!response.ok) {
      throw new Error("Failed to test model");
    }

    return response.json();
  }

  /**
   * Get model performance statistics
   */
  async getModelPerformance(modelId: string, timeRange?: string): Promise<ModelPerformance> {
    const params = timeRange ? `?timeRange=${timeRange}` : "";
    const response = await fetch(
      `${this.baseUrl}${this.endpoints.assistants}/models/${modelId}/performance${params}`,
    );

    if (!response.ok) {
      throw new Error("Failed to fetch model performance");
    }

    return response.json();
  }

  /**
   * Get model usage statistics
   */
  async getModelUsage(modelId: string, timeRange?: string): Promise<ModelUsage> {
    const params = timeRange ? `?timeRange=${timeRange}` : "";
    const response = await fetch(
      `${this.baseUrl}${this.endpoints.assistants}/models/${modelId}/usage${params}`,
    );

    if (!response.ok) {
      throw new Error("Failed to fetch model usage");
    }

    return response.json();
  }

  /**
   * Get model cost statistics
   */
  async getModelCosts(modelId: string, timeRange?: string): Promise<ModelCosts> {
    const params = timeRange ? `?timeRange=${timeRange}` : "";
    const response = await fetch(
      `${this.baseUrl}${this.endpoints.assistants}/models/${modelId}/costs${params}`,
    );

    if (!response.ok) {
      throw new Error("Failed to fetch model costs");
    }

    return response.json();
  }

  /**
   * Get available providers
   */
  async getProviders(): Promise<ProviderInfo[]> {
    const response = await fetch(
      `${this.baseUrl}${this.endpoints.assistants}/providers`,
    );

    if (!response.ok) {
      throw new Error("Failed to fetch providers");
    }

    return response.json();
  }

  /**
   * Get provider models
   */
  async getProviderModels(provider: string): Promise<string[]> {
    const response = await fetch(
      `${this.baseUrl}${this.endpoints.assistants}/providers/${provider}/models`,
    );

    if (!response.ok) {
      throw new Error("Failed to fetch provider models");
    }

    return response.json();
  }

  /**
   * Validate model configuration
   */
  async validateModel(
    modelData: ModelCreate,
  ): Promise<{ valid: boolean; errors?: string[] }> {
    const response = await fetch(
      `${this.baseUrl}${this.endpoints.assistants}/models/validate`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(modelData),
      },
    );

    if (!response.ok) {
      throw new Error("Failed to validate model");
    }

    return response.json();
  }

  /**
   * Get model comparison data
   */
  async compareModels(modelIds: string[]): Promise<CompareModelsResult> {
    const response = await fetch(
      `${this.baseUrl}${this.endpoints.assistants}/models/compare`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ modelIds }),
      },
    );

    if (!response.ok) {
      throw new Error("Failed to compare models");
    }

    return response.json();
  }

  /**
   * Get model recommendations based on use case
   */
  async getModelRecommendations(
    useCase: string,
    requirements?: Partial<Record<string, unknown>>,
  ): Promise<AIModel[]> {
    const response = await fetch(
      `${this.baseUrl}${this.endpoints.assistants}/models/recommendations`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ useCase, requirements }),
      },
    );

    if (!response.ok) {
      throw new Error("Failed to get model recommendations");
    }

    return response.json();
  }

  /**
   * Get model analytics
   */
  async getModelAnalytics(timeRange?: string, filters?: Partial<Record<string, unknown>>): Promise<ModelAnalytics> {
    const params = new URLSearchParams();
    if (timeRange) params.append("timeRange", timeRange);
    if (filters) params.append("filters", JSON.stringify(filters));

    const response = await fetch(
      `${this.baseUrl}${this.endpoints.assistants}/models/analytics?${params}`,
    );

    if (!response.ok) {
      throw new Error("Failed to fetch model analytics");
    }

    return response.json();
  }
}

export const aiModelsService = new AIModelsService();
export default aiModelsService;
