import api from './api';
import config from '../config';

export interface ExportOptions {
  format: 'csv' | 'json' | 'xlsx' | 'pdf';
  dateRange?: {
    start: string;
    end: string;
  };
  filters?: Record<string, any>;
  includeMetadata?: boolean;
  compression?: boolean;
  customFields?: string[];
}

export interface ExportJob {
  id: string;
  type: 'conversations' | 'knowledge' | 'analytics' | 'system' | 'users' | 'assistants';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  createdAt: string;
  completedAt?: string;
  downloadUrl?: string;
  error?: string;
  options: ExportOptions;
  fileSize?: number;
  recordCount?: number;
}

export interface BackupConfig {
  autoBackup: boolean;
  backupInterval: 'daily' | 'weekly' | 'monthly';
  retentionDays: number;
  includeFiles: boolean;
  includeDatabase: boolean;
  includeConfig: boolean;
  backupLocation: 'local' | 's3' | 'gcs';
  credentials?: Record<string, any>;
}

export interface BackupJob {
  id: string;
  type: 'manual' | 'scheduled';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  createdAt: string;
  completedAt?: string;
  fileSize?: number;
  backupLocation: string;
  error?: string;
  config: BackupConfig;
}

export const exportService = {
  // Export conversations
  exportConversations: async (options: ExportOptions): Promise<ExportJob> => {
    const response = await api.post(`${config.apiEndpoints.export}/conversations`, options);
    return response.data;
  },

  // Export knowledge base
  exportKnowledgeBase: async (options: ExportOptions): Promise<ExportJob> => {
    const response = await api.post(`${config.apiEndpoints.export}/knowledge`, options);
    return response.data;
  },

  // Export analytics data
  exportAnalytics: async (options: ExportOptions): Promise<ExportJob> => {
    const response = await api.post(`${config.apiEndpoints.export}/analytics`, options);
    return response.data;
  },

  // Export system data
  exportSystemData: async (options: ExportOptions): Promise<ExportJob> => {
    const response = await api.post(`${config.apiEndpoints.export}/system`, options);
    return response.data;
  },

  // Export users
  exportUsers: async (options: ExportOptions): Promise<ExportJob> => {
    const response = await api.post(`${config.apiEndpoints.export}/users`, options);
    return response.data;
  },

  // Export assistants
  exportAssistants: async (options: ExportOptions): Promise<ExportJob> => {
    const response = await api.post(`${config.apiEndpoints.export}/assistants`, options);
    return response.data;
  },

  // Get export job status
  getExportJobStatus: async (jobId: string): Promise<ExportJob> => {
    const response = await api.get(`${config.apiEndpoints.export}/jobs/${jobId}`);
    return response.data;
  },

  // List export jobs
  listExportJobs: async (filters?: {
    type?: string;
    status?: string;
    dateRange?: { start: string; end: string };
  }): Promise<ExportJob[]> => {
    const response = await api.get(`${config.apiEndpoints.export}/jobs`, {
      params: filters,
    });
    return response.data;
  },

  // Cancel export job
  cancelExportJob: async (jobId: string): Promise<void> => {
    await api.delete(`${config.apiEndpoints.export}/jobs/${jobId}`);
  },

  // Download export file
  downloadExport: async (jobId: string): Promise<Blob> => {
    const response = await api.get(`${config.apiEndpoints.export}/jobs/${jobId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Bulk export
  bulkExport: async (types: string[], options: ExportOptions): Promise<ExportJob[]> => {
    const response = await api.post(`${config.apiEndpoints.export}/bulk`, {
      types,
      options,
    });
    return response.data;
  },

  // Get export templates
  getExportTemplates: async (): Promise<any[]> => {
    const response = await api.get(`${config.apiEndpoints.export}/templates`);
    return response.data;
  },

  // Save export template
  saveExportTemplate: async (template: any): Promise<any> => {
    const response = await api.post(`${config.apiEndpoints.export}/templates`, template);
    return response.data;
  },

  // Backup Management
  createBackup: async (config: Partial<BackupConfig>): Promise<BackupJob> => {
    const response = await api.post(`${config.apiEndpoints.backup}/create`, config);
    return response.data;
  },

  // Get backup status
  getBackupStatus: async (backupId: string): Promise<BackupJob> => {
    const response = await api.get(`${config.apiEndpoints.backup}/jobs/${backupId}`);
    return response.data;
  },

  // List backups
  listBackups: async (filters?: {
    type?: string;
    status?: string;
    dateRange?: { start: string; end: string };
  }): Promise<BackupJob[]> => {
    const response = await api.get(`${config.apiEndpoints.backup}/jobs`, {
      params: filters,
    });
    return response.data;
  },

  // Restore from backup
  restoreBackup: async (backupId: string, options?: {
    restoreFiles?: boolean;
    restoreDatabase?: boolean;
    restoreConfig?: boolean;
  }): Promise<any> => {
    const response = await api.post(`${config.apiEndpoints.backup}/jobs/${backupId}/restore`, options);
    return response.data;
  },

  // Delete backup
  deleteBackup: async (backupId: string): Promise<void> => {
    await api.delete(`${config.apiEndpoints.backup}/jobs/${backupId}`);
  },

  // Download backup
  downloadBackup: async (backupId: string): Promise<Blob> => {
    const response = await api.get(`${config.apiEndpoints.backup}/jobs/${backupId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Get backup configuration
  getBackupConfig: async (): Promise<BackupConfig> => {
    const response = await api.get(`${config.apiEndpoints.backup}/config`);
    return response.data;
  },

  // Update backup configuration
  updateBackupConfig: async (config: Partial<BackupConfig>): Promise<BackupConfig> => {
    const response = await api.put(`${config.apiEndpoints.backup}/config`, config);
    return response.data;
  },

  // Test backup configuration
  testBackupConfig: async (config: Partial<BackupConfig>): Promise<any> => {
    const response = await api.post(`${config.apiEndpoints.backup}/config/test`, config);
    return response.data;
  },

  // Get export statistics
  getExportStats: async (timeRange?: string): Promise<any> => {
    const response = await api.get(`${config.apiEndpoints.export}/stats`, {
      params: { timeRange },
    });
    return response.data;
  },

  // Get backup statistics
  getBackupStats: async (timeRange?: string): Promise<any> => {
    const response = await api.get(`${config.apiEndpoints.backup}/stats`, {
      params: { timeRange },
    });
    return response.data;
  },

  // Schedule export
  scheduleExport: async (schedule: {
    type: string;
    options: ExportOptions;
    cronExpression: string;
    enabled: boolean;
  }): Promise<any> => {
    const response = await api.post(`${config.apiEndpoints.export}/schedule`, schedule);
    return response.data;
  },

  // List scheduled exports
  listScheduledExports: async (): Promise<any[]> => {
    const response = await api.get(`${config.apiEndpoints.export}/schedule`);
    return response.data;
  },

  // Update scheduled export
  updateScheduledExport: async (scheduleId: string, updates: any): Promise<any> => {
    const response = await api.put(`${config.apiEndpoints.export}/schedule/${scheduleId}`, updates);
    return response.data;
  },

  // Delete scheduled export
  deleteScheduledExport: async (scheduleId: string): Promise<void> => {
    await api.delete(`${config.apiEndpoints.export}/schedule/${scheduleId}`);
  },
};