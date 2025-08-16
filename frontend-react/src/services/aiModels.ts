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

  private get base(): string {
    return `${this.baseUrl}/api/v1/ai-models`;
  }

  async getModels(): Promise<AIModel[]> {
    const response = await fetch(`${this.base}/`);
    if (!response.ok) throw new Error("Failed to fetch models");
    return response.json();
  }

  async getModel(modelId: string): Promise<AIModel> {
    const response = await fetch(`${this.base}/${modelId}`);
    if (!response.ok) throw new Error("Failed to fetch model");
    return response.json();
  }

  async createModel(modelData: ModelCreate): Promise<AIModel> {
    const response = await fetch(`${this.base}/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(modelData),
    });
    if (!response.ok) throw new Error("Failed to create model");
    return response.json();
  }

  async updateModel(modelId: string, modelData: ModelUpdate): Promise<AIModel> {
    const response = await fetch(`${this.base}/${modelId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(modelData),
    });
    if (!response.ok) throw new Error("Failed to update model");
    return response.json();
  }

  async deleteModel(modelId: string): Promise<void> {
    const response = await fetch(`${this.base}/${modelId}`, { method: "DELETE" });
    if (!response.ok) throw new Error("Failed to delete model");
  }

  async toggleModelActive(modelId: string, isActive: boolean): Promise<AIModel> {
    const response = await fetch(`${this.base}/${modelId}/toggle`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ isActive }),
    });
    if (!response.ok) throw new Error("Failed to toggle model status");
    return response.json();
  }

  async setDefaultModel(modelId: string): Promise<AIModel> {
    const response = await fetch(`${this.base}/${modelId}/default`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
    });
    if (!response.ok) throw new Error("Failed to set default model");
    return response.json();
  }

  async testModel(modelId: string, prompt: string): Promise<ModelTest> {
    const response = await fetch(`${this.base}/${modelId}/test`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });
    if (!response.ok) throw new Error("Failed to test model");
    return response.json();
  }

  async getModelPerformance(modelId: string, timeRange?: string): Promise<ModelPerformance> {
    const params = timeRange ? `?timeRange=${timeRange}` : "";
    const response = await fetch(`${this.base}/${modelId}/performance${params}`);
    if (!response.ok) throw new Error("Failed to fetch model performance");
    return response.json();
  }

  async getModelUsage(modelId: string, timeRange?: string): Promise<ModelUsage> {
    const params = timeRange ? `?timeRange=${timeRange}` : "";
    const response = await fetch(`${this.base}/${modelId}/usage${params}`);
    if (!response.ok) throw new Error("Failed to fetch model usage");
    return response.json();
  }

  async getModelCosts(modelId: string, timeRange?: string): Promise<ModelCosts> {
    const params = timeRange ? `?timeRange=${timeRange}` : "";
    const response = await fetch(`${this.base}/${modelId}/costs${params}`);
    if (!response.ok) throw new Error("Failed to fetch model costs");
    return response.json();
  }

  async getProviders(): Promise<string[]> {
    const response = await fetch(`${this.base}/providers`);
    if (!response.ok) throw new Error("Failed to fetch providers");
    return response.json();
  }

  async getProviderModels(provider: string): Promise<string[]> {
    const response = await fetch(`${this.base}/providers/${provider}/models`);
    if (!response.ok) throw new Error("Failed to fetch provider models");
    return response.json();
  }

  async validateModel(modelData: ModelCreate): Promise<{ valid: boolean; errors?: string[] }> {
    const response = await fetch(`${this.base}/models/validate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(modelData),
    });
    if (!response.ok) throw new Error("Failed to validate model");
    return response.json();
  }

  async compareModels(modelIds: string[]): Promise<CompareModelsResult> {
    const response = await fetch(`${this.base}/models/compare`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ modelIds }),
    });
    if (!response.ok) throw new Error("Failed to compare models");
    return response.json();
  }

  async getModelRecommendations(
    useCase: string,
    requirements?: Partial<Record<string, unknown>>,
  ): Promise<AIModel[]> {
    const response = await fetch(`${this.base}/models/recommendations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ useCase, requirements }),
    });
    if (!response.ok) throw new Error("Failed to get model recommendations");
    return response.json();
  }

  async getModelAnalytics(timeRange?: string, filters?: Partial<Record<string, unknown>>): Promise<ModelAnalytics> {
    const params = new URLSearchParams();
    if (timeRange) params.append("timeRange", timeRange);
    if (filters) params.append("filters", JSON.stringify(filters));

    const response = await fetch(`${this.base}/models/analytics?${params}`);
    if (!response.ok) throw new Error("Failed to fetch model analytics");
    return response.json();
  }
}

export const aiModelsService = new AIModelsService();
export default aiModelsService;
