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

export const configurationService = {
  // System Configuration
  getSystemConfig: async (): Promise<SystemConfig> => {
    const response = await api.get(`${config.apiEndpoints.config}/system`);
    return response.data;
  },

  updateSystemConfig: async (
    config: Partial<SystemConfig>,
  ): Promise<SystemConfig> => {
    const response = await api.put(
      `${config.apiEndpoints.config}/system`,
      config,
    );
    return response.data;
  },

  validateSystemConfig: async (
    config: Partial<SystemConfig>,
  ): Promise<ConfigValidation> => {
    const response = await api.post(
      `${config.apiEndpoints.config}/system/validate`,
      config,
    );
    return response.data;
  },

  resetSystemConfig: async (): Promise<SystemConfig> => {
    const response = await api.post(
      `${config.apiEndpoints.config}/system/reset`,
    );
    return response.data;
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
    return response.data;
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
    return response.data;
  },

  // User Preferences
  getUserPreferences: async (userId?: string): Promise<UserPreferences> => {
    const response = await api.get(
      `${config.apiEndpoints.config}/preferences${userId ? `/${userId}` : ""}`,
    );
    return response.data;
  },

  updateUserPreferences: async (
    preferences: Partial<UserPreferences>,
  ): Promise<UserPreferences> => {
    const response = await api.put(
      `${config.apiEndpoints.config}/preferences`,
      preferences,
    );
    return response.data;
  },

  resetUserPreferences: async (): Promise<UserPreferences> => {
    const response = await api.post(
      `${config.apiEndpoints.config}/preferences/reset`,
    );
    return response.data;
  },

  // Configuration Templates
  getConfigTemplates: async (): Promise<any[]> => {
    const response = await api.get(`${config.apiEndpoints.config}/templates`);
    return response.data;
  },

  saveConfigTemplate: async (template: any): Promise<any> => {
    const response = await api.post(
      `${config.apiEndpoints.config}/templates`,
      template,
    );
    return response.data;
  },

  updateConfigTemplate: async (
    templateId: string,
    template: any,
  ): Promise<any> => {
    const response = await api.put(
      `${config.apiEndpoints.config}/templates/${templateId}`,
      template,
    );
    return response.data;
  },

  deleteConfigTemplate: async (templateId: string): Promise<void> => {
    await api.delete(`${config.apiEndpoints.config}/templates/${templateId}`);
  },

  applyConfigTemplate: async (templateId: string): Promise<SystemConfig> => {
    const response = await api.post(
      `${config.apiEndpoints.config}/templates/${templateId}/apply`,
    );
    return response.data;
  },

  // Environment Management
  getEnvironmentConfig: async (environment: string): Promise<SystemConfig> => {
    const response = await api.get(
      `${config.apiEndpoints.config}/environments/${environment}`,
    );
    return response.data;
  },

  updateEnvironmentConfig: async (
    environment: string,
    config: Partial<SystemConfig>,
  ): Promise<SystemConfig> => {
    const response = await api.put(
      `${config.apiEndpoints.config}/environments/${environment}`,
      config,
    );
    return response.data;
  },

  listEnvironments: async (): Promise<string[]> => {
    const response = await api.get(
      `${config.apiEndpoints.config}/environments`,
    );
    return response.data;
  },

  // Configuration History
  getConfigHistory: async (limit: number = 50): Promise<any[]> => {
    const response = await api.get(`${config.apiEndpoints.config}/history`, {
      params: { limit },
    });
    return response.data;
  },

  revertConfig: async (versionId: string): Promise<SystemConfig> => {
    const response = await api.post(
      `${config.apiEndpoints.config}/history/${versionId}/revert`,
    );
    return response.data;
  },

  // Configuration Backup
  backupConfig: async (): Promise<Blob> => {
    const response = await api.get(`${config.apiEndpoints.config}/backup`, {
      responseType: "blob",
    });
    return response.data;
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
    return response.data;
  },

  // Configuration Validation
  validateConfig: async (config: any): Promise<ConfigValidation> => {
    const response = await api.post(
      `${config.apiEndpoints.config}/validate`,
      config,
    );
    return response.data;
  },

  // Configuration Testing
  testConfig: async (config: Partial<SystemConfig>): Promise<any> => {
    const response = await api.post(
      `${config.apiEndpoints.config}/test`,
      config,
    );
    return response.data;
  },

  // Configuration Statistics
  getConfigStats: async (): Promise<any> => {
    const response = await api.get(`${config.apiEndpoints.config}/stats`);
    return response.data;
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
    return response.data;
  },

  // Configuration Comparison
  compareConfigs: async (config1: any, config2: any): Promise<any> => {
    const response = await api.post(`${config.apiEndpoints.config}/compare`, {
      config1,
      config2,
    });
    return response.data;
  },

  // Configuration Search
  searchConfig: async (query: string): Promise<any[]> => {
    const response = await api.get(`${config.apiEndpoints.config}/search`, {
      params: { q: query },
    });
    return response.data;
  },

  // Configuration Documentation
  getConfigDocs: async (): Promise<any> => {
    const response = await api.get(`${config.apiEndpoints.config}/docs`);
    return response.data;
  },

  // Configuration Schema
  getConfigSchema: async (): Promise<any> => {
    const response = await api.get(`${config.apiEndpoints.config}/schema`);
    return response.data;
  },
};
