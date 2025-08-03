import { create } from 'zustand';
import { exportService, type ExportJob, type BackupJob, type ExportOptions, type BackupConfig } from '../services/export';

interface ExportState {
  // State
  exportJobs: ExportJob[];
  backupJobs: BackupJob[];
  exportTemplates: any[];
  scheduledExports: any[];
  backupConfig: BackupConfig | null;
  loading: boolean;
  error: string | null;
  pollingInterval: number;

  // Actions
  // Export Jobs
  createExportJob: (type: string, options: ExportOptions) => Promise<ExportJob>;
  getExportJobStatus: (jobId: string) => Promise<void>;
  listExportJobs: (filters?: any) => Promise<void>;
  cancelExportJob: (jobId: string) => Promise<void>;
  downloadExport: (jobId: string) => Promise<void>;
  bulkExport: (types: string[], options: ExportOptions) => Promise<void>;

  // Export Templates
  getExportTemplates: () => Promise<void>;
  saveExportTemplate: (template: any) => Promise<void>;

  // Scheduled Exports
  scheduleExport: (schedule: any) => Promise<void>;
  listScheduledExports: () => Promise<void>;
  updateScheduledExport: (scheduleId: string, updates: any) => Promise<void>;
  deleteScheduledExport: (scheduleId: string) => Promise<void>;

  // Backup Jobs
  createBackup: (config: Partial<BackupConfig>) => Promise<BackupJob>;
  getBackupStatus: (backupId: string) => Promise<void>;
  listBackups: (filters?: any) => Promise<void>;
  restoreBackup: (backupId: string, options?: any) => Promise<void>;
  deleteBackup: (backupId: string) => Promise<void>;
  downloadBackup: (backupId: string) => Promise<void>;

  // Backup Configuration
  getBackupConfig: () => Promise<void>;
  updateBackupConfig: (config: Partial<BackupConfig>) => Promise<void>;
  testBackupConfig: (config: Partial<BackupConfig>) => Promise<void>;

  // Statistics
  getExportStats: (timeRange?: string) => Promise<any>;
  getBackupStats: (timeRange?: string) => Promise<any>;

  // Utility
  setPollingInterval: (interval: number) => void;
  clearError: () => void;
  reset: () => void;
}

export const useExportStore = create<ExportState>((set, get) => ({
  // Initial state
  exportJobs: [],
  backupJobs: [],
  exportTemplates: [],
  scheduledExports: [],
  backupConfig: null,
  loading: false,
  error: null,
  pollingInterval: 5000, // 5 seconds

  // Actions
  createExportJob: async (type: string, options: ExportOptions) => {
    set({ loading: true, error: null });
    try {
      let job: ExportJob;
      
      switch (type) {
        case 'conversations':
          job = await exportService.exportConversations(options);
          break;
        case 'knowledge':
          job = await exportService.exportKnowledgeBase(options);
          break;
        case 'analytics':
          job = await exportService.exportAnalytics(options);
          break;
        case 'system':
          job = await exportService.exportSystemData(options);
          break;
        case 'users':
          job = await exportService.exportUsers(options);
          break;
        case 'assistants':
          job = await exportService.exportAssistants(options);
          break;
        default:
          throw new Error(`Unknown export type: ${type}`);
      }

      const { exportJobs } = get();
      set({ 
        exportJobs: [job, ...exportJobs],
        loading: false 
      });

      return job;
    } catch (error: any) {
      set({ 
        error: error.message || 'Failed to create export job', 
        loading: false 
      });
      throw error;
    }
  },

  getExportJobStatus: async (jobId: string) => {
    try {
      const job = await exportService.getExportJobStatus(jobId);
      const { exportJobs } = get();
      const updatedJobs = exportJobs.map(j => j.id === jobId ? job : j);
      set({ exportJobs: updatedJobs });
    } catch (error: any) {
      set({ error: error.message || 'Failed to get export job status' });
    }
  },

  listExportJobs: async (filters?: any) => {
    set({ loading: true, error: null });
    try {
      const jobs = await exportService.listExportJobs(filters);
      set({ exportJobs: jobs, loading: false });
    } catch (error: any) {
      set({ 
        error: error.message || 'Failed to list export jobs', 
        loading: false 
      });
    }
  },

  cancelExportJob: async (jobId: string) => {
    try {
      await exportService.cancelExportJob(jobId);
      const { exportJobs } = get();
      const updatedJobs = exportJobs.map(j => 
        j.id === jobId ? { ...j, status: 'failed', error: 'Cancelled by user' } : j
      );
      set({ exportJobs: updatedJobs });
    } catch (error: any) {
      set({ error: error.message || 'Failed to cancel export job' });
    }
  },

  downloadExport: async (jobId: string) => {
    try {
      const blob = await exportService.downloadExport(jobId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `export-${jobId}.zip`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error: any) {
      set({ error: error.message || 'Failed to download export' });
    }
  },

  bulkExport: async (types: string[], options: ExportOptions) => {
    set({ loading: true, error: null });
    try {
      const jobs = await exportService.bulkExport(types, options);
      const { exportJobs } = get();
      set({ 
        exportJobs: [...jobs, ...exportJobs],
        loading: false 
      });
    } catch (error: any) {
      set({ 
        error: error.message || 'Failed to create bulk export', 
        loading: false 
      });
    }
  },

  getExportTemplates: async () => {
    set({ loading: true, error: null });
    try {
      const templates = await exportService.getExportTemplates();
      set({ exportTemplates: templates, loading: false });
    } catch (error: any) {
      set({ 
        error: error.message || 'Failed to get export templates', 
        loading: false 
      });
    }
  },

  saveExportTemplate: async (template: any) => {
    try {
      const savedTemplate = await exportService.saveExportTemplate(template);
      const { exportTemplates } = get();
      set({ exportTemplates: [...exportTemplates, savedTemplate] });
    } catch (error: any) {
      set({ error: error.message || 'Failed to save export template' });
    }
  },

  scheduleExport: async (schedule: any) => {
    try {
      const scheduledExport = await exportService.scheduleExport(schedule);
      const { scheduledExports } = get();
      set({ scheduledExports: [...scheduledExports, scheduledExport] });
    } catch (error: any) {
      set({ error: error.message || 'Failed to schedule export' });
    }
  },

  listScheduledExports: async () => {
    set({ loading: true, error: null });
    try {
      const exports = await exportService.listScheduledExports();
      set({ scheduledExports: exports, loading: false });
    } catch (error: any) {
      set({ 
        error: error.message || 'Failed to list scheduled exports', 
        loading: false 
      });
    }
  },

  updateScheduledExport: async (scheduleId: string, updates: any) => {
    try {
      const updatedExport = await exportService.updateScheduledExport(scheduleId, updates);
      const { scheduledExports } = get();
      const updatedExports = scheduledExports.map(e => 
        e.id === scheduleId ? updatedExport : e
      );
      set({ scheduledExports: updatedExports });
    } catch (error: any) {
      set({ error: error.message || 'Failed to update scheduled export' });
    }
  },

  deleteScheduledExport: async (scheduleId: string) => {
    try {
      await exportService.deleteScheduledExport(scheduleId);
      const { scheduledExports } = get();
      const updatedExports = scheduledExports.filter(e => e.id !== scheduleId);
      set({ scheduledExports: updatedExports });
    } catch (error: any) {
      set({ error: error.message || 'Failed to delete scheduled export' });
    }
  },

  createBackup: async (config: Partial<BackupConfig>) => {
    set({ loading: true, error: null });
    try {
      const backup = await exportService.createBackup(config);
      const { backupJobs } = get();
      set({ 
        backupJobs: [backup, ...backupJobs],
        loading: false 
      });
      return backup;
    } catch (error: any) {
      set({ 
        error: error.message || 'Failed to create backup', 
        loading: false 
      });
      throw error;
    }
  },

  getBackupStatus: async (backupId: string) => {
    try {
      const backup = await exportService.getBackupStatus(backupId);
      const { backupJobs } = get();
      const updatedJobs = backupJobs.map(b => b.id === backupId ? backup : b);
      set({ backupJobs: updatedJobs });
    } catch (error: any) {
      set({ error: error.message || 'Failed to get backup status' });
    }
  },

  listBackups: async (filters?: any) => {
    set({ loading: true, error: null });
    try {
      const backups = await exportService.listBackups(filters);
      set({ backupJobs: backups, loading: false });
    } catch (error: any) {
      set({ 
        error: error.message || 'Failed to list backups', 
        loading: false 
      });
    }
  },

  restoreBackup: async (backupId: string, options?: any) => {
    try {
      const result = await exportService.restoreBackup(backupId, options);
      return result;
    } catch (error: any) {
      set({ error: error.message || 'Failed to restore backup' });
      throw error;
    }
  },

  deleteBackup: async (backupId: string) => {
    try {
      await exportService.deleteBackup(backupId);
      const { backupJobs } = get();
      const updatedJobs = backupJobs.filter(b => b.id !== backupId);
      set({ backupJobs: updatedJobs });
    } catch (error: any) {
      set({ error: error.message || 'Failed to delete backup' });
    }
  },

  downloadBackup: async (backupId: string) => {
    try {
      const blob = await exportService.downloadBackup(backupId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `backup-${backupId}.zip`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error: any) {
      set({ error: error.message || 'Failed to download backup' });
    }
  },

  getBackupConfig: async () => {
    set({ loading: true, error: null });
    try {
      const config = await exportService.getBackupConfig();
      set({ backupConfig: config, loading: false });
    } catch (error: any) {
      set({ 
        error: error.message || 'Failed to get backup config', 
        loading: false 
      });
    }
  },

  updateBackupConfig: async (config: Partial<BackupConfig>) => {
    try {
      const updatedConfig = await exportService.updateBackupConfig(config);
      set({ backupConfig: updatedConfig });
    } catch (error: any) {
      set({ error: error.message || 'Failed to update backup config' });
    }
  },

  testBackupConfig: async (config: Partial<BackupConfig>) => {
    try {
      const result = await exportService.testBackupConfig(config);
      return result;
    } catch (error: any) {
      set({ error: error.message || 'Failed to test backup config' });
      throw error;
    }
  },

  getExportStats: async (timeRange?: string) => {
    try {
      const stats = await exportService.getExportStats(timeRange);
      return stats;
    } catch (error: any) {
      set({ error: error.message || 'Failed to get export stats' });
      throw error;
    }
  },

  getBackupStats: async (timeRange?: string) => {
    try {
      const stats = await exportService.getBackupStats(timeRange);
      return stats;
    } catch (error: any) {
      set({ error: error.message || 'Failed to get backup stats' });
      throw error;
    }
  },

  setPollingInterval: (interval: number) => {
    set({ pollingInterval: interval });
  },

  clearError: () => {
    set({ error: null });
  },

  reset: () => {
    set({
      exportJobs: [],
      backupJobs: [],
      exportTemplates: [],
      scheduledExports: [],
      backupConfig: null,
      loading: false,
      error: null,
      pollingInterval: 5000,
    });
  },
}));