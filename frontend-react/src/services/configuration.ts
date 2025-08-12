import api from "./api";
import config from "../config";

export interface SystemConfig {
  general: {
    appName: string;
    appVersion: string;
    environment: "development" | "staging" | "production";
    debugMode: boolean;
    maintenanceMode: boolean;
    maintenanceMessage?: string;
  };
  security: {
    sessionTimeout: number;
    maxLoginAttempts: number;
    passwordPolicy: {
      minLength: number;
      requireUppercase: boolean;
      requireLowercase: boolean;
      requireNumbers: boolean;
      requireSpecialChars: boolean;
    };
    mfaEnabled: boolean;
    mfaMethods: string[];
    ipWhitelist: string[];
  };
  features: {
    chatEnabled: boolean;
    knowledgeBaseEnabled: boolean;
    analyticsEnabled: boolean;
    exportEnabled: boolean;
    backupEnabled: boolean;
    ssoEnabled: boolean;
    ragEnabled: boolean;
    monitoringEnabled: boolean;
  };
  integrations: {
    openai: {
      enabled: boolean;
      apiKey?: string;
      model: string;
      maxTokens: number;
      temperature: number;
    };
    anthropic: {
      enabled: boolean;
      apiKey?: string;
      model: string;
      maxTokens: number;
      temperature: number;
    };
    azure: {
      enabled: boolean;
      endpoint?: string;
      apiKey?: string;
      deploymentName?: string;
    };
    email: {
      enabled: boolean;
      provider: "smtp" | "sendgrid" | "mailgun";
      host?: string;
      port?: number;
      username?: string;
      password?: string;
      fromEmail?: string;
      fromName?: string;
    };
    storage: {
      provider: "local" | "s3" | "gcs" | "azure";
      bucket?: string;
      region?: string;
      accessKey?: string;
      secretKey?: string;
    };
  };
  ui: {
    theme: "light" | "dark" | "auto";
    language: string;
    timezone: string;
    dateFormat: string;
    timeFormat: string;
    sidebarCollapsed: boolean;
    animationsEnabled: boolean;
  };
  performance: {
    cacheEnabled: boolean;
    cacheTtl: number;
    rateLimitEnabled: boolean;
    rateLimitRequests: number;
    rateLimitWindow: number;
    compressionEnabled: boolean;
    gzipLevel: number;
  };
  logging: {
    level: "debug" | "info" | "warn" | "error";
    fileEnabled: boolean;
    filePath?: string;
    maxFileSize: number;
    maxFiles: number;
    consoleEnabled: boolean;
    syslogEnabled: boolean;
    syslogHost?: string;
    syslogPort?: number;
  };
}

export interface UserPreferences {
  id: string;
  userId: string;
  theme: "light" | "dark" | "auto";
  language: string;
  timezone: string;
  dateFormat: string;
  timeFormat: string;
  sidebarCollapsed: boolean;
  animationsEnabled: boolean;
  notifications: {
    email: boolean;
    push: boolean;
    desktop: boolean;
    sound: boolean;
  };
  privacy: {
    dataSharing: boolean;
    analytics: boolean;
    marketing: boolean;
  };
  accessibility: {
    highContrast: boolean;
    largeText: boolean;
    reducedMotion: boolean;
    screenReader: boolean;
  };
  chat: {
    defaultAssistant: string;
    messageHistory: number;
    autoSave: boolean;
    typingIndicator: boolean;
  };
  createdAt: string;
  updatedAt: string;
}

export interface ConfigValidation {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export interface ConfigTemplate {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
  data: Partial<SystemConfig>;
}

export interface ConfigHistoryEntry {
  id: string;
  version: string;
  createdAt: string;
  createdBy: string;
  message?: string;
}

export interface ConfigStats {
  totalKeys: number;
  overriddenKeys: number;
  lastUpdatedAt: string;
}

export interface CompareResult {
  added: string[];
  removed: string[];
  changed: string[];
}

export const configurationService = {
  // System Configuration
  getSystemConfig: async (): Promise<SystemConfig> => {
    const response = await api.get(`${config.apiEndpoints.config}/system`);
    return response.data as SystemConfig;
  },

  updateSystemConfig: async (
    cfg: Partial<SystemConfig>,
  ): Promise<SystemConfig> => {
    const response = await api.put(
      `${config.apiEndpoints.config}/system`,
      cfg,
    );
    return response.data as SystemConfig;
  },

  validateSystemConfig: async (
    cfg: Partial<SystemConfig>,
  ): Promise<ConfigValidation> => {
    const response = await api.post(
      `${config.apiEndpoints.config}/system/validate`,
      cfg,
    );
    return response.data as ConfigValidation;
  },

  resetSystemConfig: async (): Promise<SystemConfig> => {
    const response = await api.post(
      `${config.apiEndpoints.config}/system/reset`,
    );
    return response.data as SystemConfig;
  },

  exportSystemConfig: async (
    format: "json" | "yaml" = "json",
  ): Promise<Blob> => {
    const response = await api.get(
      `${config.apiEndpoints.config}/system/export`,
      {
        params: { format },
        responseType: "blob",
      },
    );
    return response.data as Blob;
  },

  importSystemConfig: async (file: File): Promise<SystemConfig> => {
    const formData = new FormData();
    formData.append("config", file);
    const response = await api.post(
      `${config.apiEndpoints.config}/system/import`,
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
      },
    );
    return response.data as SystemConfig;
  },

  // User Preferences
  getUserPreferences: async (userId?: string): Promise<UserPreferences> => {
    const response = await api.get(
      `${config.apiEndpoints.config}/preferences${userId ? `/${userId}` : ""}`,
    );
    return response.data as UserPreferences;
  },

  updateUserPreferences: async (
    preferences: Partial<UserPreferences>,
  ): Promise<UserPreferences> => {
    const response = await api.put(
      `${config.apiEndpoints.config}/preferences`,
      preferences,
    );
    return response.data as UserPreferences;
  },

  resetUserPreferences: async (): Promise<UserPreferences> => {
    const response = await api.post(
      `${config.apiEndpoints.config}/preferences/reset`,
    );
    return response.data as UserPreferences;
  },

  // Configuration Templates
  getConfigTemplates: async (): Promise<ConfigTemplate[]> => {
    const response = await api.get(`${config.apiEndpoints.config}/templates`);
    return response.data as ConfigTemplate[];
  },

  saveConfigTemplate: async (template: ConfigTemplate): Promise<ConfigTemplate> => {
    const response = await api.post(
      `${config.apiEndpoints.config}/templates`,
      template,
    );
    return response.data as ConfigTemplate;
  },

  updateConfigTemplate: async (
    templateId: string,
    template: Partial<ConfigTemplate>,
  ): Promise<ConfigTemplate> => {
    const response = await api.put(
      `${config.apiEndpoints.config}/templates/${templateId}`,
      template,
    );
    return response.data as ConfigTemplate;
  },

  deleteConfigTemplate: async (templateId: string): Promise<void> => {
    await api.delete(`${config.apiEndpoints.config}/templates/${templateId}`);
  },

  applyConfigTemplate: async (templateId: string): Promise<SystemConfig> => {
    const response = await api.post(
      `${config.apiEndpoints.config}/templates/${templateId}/apply`,
    );
    return response.data as SystemConfig;
  },

  // Environment Management
  getEnvironmentConfig: async (environment: string): Promise<SystemConfig> => {
    const response = await api.get(
      `${config.apiEndpoints.config}/environments/${environment}`,
    );
    return response.data as SystemConfig;
  },

  updateEnvironmentConfig: async (
    environment: string,
    cfg: Partial<SystemConfig>,
  ): Promise<SystemConfig> => {
    const response = await api.put(
      `${config.apiEndpoints.config}/environments/${environment}`,
      cfg,
    );
    return response.data as SystemConfig;
  },

  listEnvironments: async (): Promise<string[]> => {
    const response = await api.get(
      `${config.apiEndpoints.config}/environments`,
    );
    return response.data as string[];
  },

  // Configuration History
  getConfigHistory: async (limit: number = 50): Promise<ConfigHistoryEntry[]> => {
    const response = await api.get(`${config.apiEndpoints.config}/history`, {
      params: { limit },
    });
    return response.data as ConfigHistoryEntry[];
  },

  revertConfig: async (versionId: string): Promise<SystemConfig> => {
    const response = await api.post(
      `${config.apiEndpoints.config}/history/${versionId}/revert`,
    );
    return response.data as SystemConfig;
  },

  // Configuration Backup
  backupConfig: async (): Promise<Blob> => {
    const response = await api.get(`${config.apiEndpoints.config}/backup`, {
      responseType: "blob",
    });
    return response.data as Blob;
  },

  restoreConfig: async (file: File): Promise<SystemConfig> => {
    const formData = new FormData();
    formData.append("backup", file);
    const response = await api.post(
      `${config.apiEndpoints.config}/restore`,
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
      },
    );
    return response.data as SystemConfig;
  },

  // Configuration Validation
  validateConfig: async (cfg: Partial<SystemConfig>): Promise<ConfigValidation> => {
    const response = await api.post(
      `${config.apiEndpoints.config}/validate`,
      cfg,
    );
    return response.data as ConfigValidation;
  },

  // Configuration Testing
  testConfig: async (cfg: Partial<SystemConfig>): Promise<ConfigValidation> => {
    const response = await api.post(
      `${config.apiEndpoints.config}/test`,
      cfg,
    );
    return response.data as ConfigValidation;
  },

  // Configuration Statistics
  getConfigStats: async (): Promise<ConfigStats> => {
    const response = await api.get(`${config.apiEndpoints.config}/stats`);
    return response.data as ConfigStats;
  },

  // Configuration Migration
  migrateConfig: async (
    fromVersion: string,
    toVersion: string,
  ): Promise<SystemConfig> => {
    const response = await api.post(`${config.apiEndpoints.config}/migrate`, {
      fromVersion,
      toVersion,
    });
    return response.data as SystemConfig;
  },

  // Configuration Comparison
  compareConfigs: async (config1: Partial<SystemConfig>, config2: Partial<SystemConfig>): Promise<CompareResult> => {
    const response = await api.post(`${config.apiEndpoints.config}/compare`, {
      config1,
      config2,
    });
    return response.data as CompareResult;
  },

  // Configuration Search
  searchConfig: async (query: string): Promise<string[]> => {
    const response = await api.get(`${config.apiEndpoints.config}/search`, {
      params: { q: query },
    });
    return response.data as string[];
  },

  // Configuration Documentation
  getConfigDocs: async (): Promise<string> => {
    const response = await api.get(`${config.apiEndpoints.config}/docs`);
    return response.data as string;
  },

  // Configuration Schema
  getConfigSchema: async (): Promise<Record<string, unknown>> => {
    const response = await api.get(`${config.apiEndpoints.config}/schema`);
    return response.data as Record<string, unknown>;
  },
};
