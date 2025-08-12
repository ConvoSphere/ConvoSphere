import { create } from "zustand";
import {
  monitoringService,
  type SystemMetrics,
  type PerformanceData,
  type Alert,
  type ServiceHealth,
  type MonitoringConfig,
} from "../services/monitoring";

interface MonitoringState {
  // State
  systemMetrics: SystemMetrics | null;
  performanceData: PerformanceData[];
  alerts: Alert[];
  serviceHealth: ServiceHealth[];
  monitoringConfig: MonitoringConfig | null;
  systemLogs: any[];
  errorStats: any;
  apiUsageStats: any;
  databaseMetrics: any;
  cacheMetrics: any;
  loading: boolean;
  error: string | null;
  refreshInterval: number;

  // Actions
  fetchSystemMetrics: () => Promise<void>;
  fetchPerformanceData: (timeRange: string, interval?: string) => Promise<void>;
  fetchAlerts: (filters?: any) => Promise<void>;
  acknowledgeAlert: (alertId: string, userId: string) => Promise<void>;
  fetchServiceHealth: () => Promise<void>;
  fetchMonitoringConfig: () => Promise<void>;
  updateMonitoringConfig: (config: Partial<MonitoringConfig>) => Promise<void>;
  fetchSystemLogs: (filters?: any) => Promise<void>;
  fetchErrorStats: (timeRange?: string) => Promise<void>;
  fetchApiUsageStats: (timeRange?: string) => Promise<void>;
  fetchDatabaseMetrics: () => Promise<void>;
  fetchCacheMetrics: () => Promise<void>;
  triggerHealthCheck: (serviceId?: string) => Promise<void>;
  exportMonitoringData: (
    format?: "csv" | "json",
    filters?: any,
  ) => Promise<void>;
  setRefreshInterval: (interval: number) => void;
  clearError: () => void;
  reset: () => void;
}

export const useMonitoringStore = create<MonitoringState>((set, get) => ({
  // Initial state
  systemMetrics: null,
  performanceData: [],
  alerts: [],
  serviceHealth: [],
  monitoringConfig: null,
  systemLogs: [],
  errorStats: null,
  apiUsageStats: null,
  databaseMetrics: null,
  cacheMetrics: null,
  loading: false,
  error: null,
  refreshInterval: 30000, // 30 seconds

  // Actions
  fetchSystemMetrics: async () => {
    set({ loading: true, error: null });
    try {
      const systemMetrics = await monitoringService.getSystemMetrics();
      set({ systemMetrics, loading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to fetch system metrics",
        loading: false,
      });
    }
  },

  fetchPerformanceData: async (timeRange: string, interval: string = "1m") => {
    set({ loading: true, error: null });
    try {
      const performanceData = await monitoringService.getPerformanceData(
        timeRange,
        interval,
      );
      set({ performanceData, loading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to fetch performance data",
        loading: false,
      });
    }
  },

  fetchAlerts: async (filters?: any) => {
    set({ loading: true, error: null });
    try {
      const alerts = await monitoringService.getAlerts(filters);
      set({ alerts, loading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to fetch alerts",
        loading: false,
      });
    }
  },

  acknowledgeAlert: async (alertId: string, userId: string) => {
    try {
      const updatedAlert = await monitoringService.acknowledgeAlert(
        alertId,
        userId,
      );
      const { alerts } = get();
      const updatedAlerts = alerts.map((alert) =>
        alert.id === alertId ? updatedAlert : alert,
      );
      set({ alerts: updatedAlerts });
    } catch (error: any) {
      set({ error: error.message || "Failed to acknowledge alert" });
    }
  },

  fetchServiceHealth: async () => {
    set({ loading: true, error: null });
    try {
      const serviceHealth = await monitoringService.getServiceHealth();
      set({ serviceHealth, loading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to fetch service health",
        loading: false,
      });
    }
  },

  fetchMonitoringConfig: async () => {
    set({ loading: true, error: null });
    try {
      const monitoringConfig = await monitoringService.getMonitoringConfig();
      set({ monitoringConfig, loading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to fetch monitoring config",
        loading: false,
      });
    }
  },

  updateMonitoringConfig: async (config: Partial<MonitoringConfig>) => {
    set({ loading: true, error: null });
    try {
      const updatedConfig =
        await monitoringService.updateMonitoringConfig(config);
      set({ monitoringConfig: updatedConfig, loading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to update monitoring config",
        loading: false,
      });
    }
  },

  fetchSystemLogs: async (filters?: any) => {
    set({ loading: true, error: null });
    try {
      const systemLogs = await monitoringService.getSystemLogs(filters);
      set({ systemLogs, loading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to fetch system logs",
        loading: false,
      });
    }
  },

  fetchErrorStats: async (timeRange: string = "24h") => {
    set({ loading: true, error: null });
    try {
      const errorStats = await monitoringService.getErrorStats(timeRange);
      set({ errorStats, loading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to fetch error stats",
        loading: false,
      });
    }
  },

  fetchApiUsageStats: async (timeRange: string = "24h") => {
    set({ loading: true, error: null });
    try {
      const apiUsageStats = await monitoringService.getApiUsageStats(timeRange);
      set({ apiUsageStats, loading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to fetch API usage stats",
        loading: false,
      });
    }
  },

  fetchDatabaseMetrics: async () => {
    set({ loading: true, error: null });
    try {
      const databaseMetrics = await monitoringService.getDatabaseMetrics();
      set({ databaseMetrics, loading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to fetch database metrics",
        loading: false,
      });
    }
  },

  fetchCacheMetrics: async () => {
    set({ loading: true, error: null });
    try {
      const cacheMetrics = await monitoringService.getCacheMetrics();
      set({ cacheMetrics, loading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to fetch cache metrics",
        loading: false,
      });
    }
  },

  triggerHealthCheck: async (serviceId?: string) => {
    try {
      await monitoringService.triggerHealthCheck(serviceId);
      // Refresh service health after manual check
      await get().fetchServiceHealth();
    } catch (error: any) {
      set({ error: error.message || "Failed to trigger health check" });
    }
  },

  exportMonitoringData: async (
    format: "csv" | "json" = "csv",
    filters?: any,
  ) => {
    try {
      const blob = await monitoringService.exportMonitoringData(
        format,
        filters,
      );
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `monitoring-data-${new Date().toISOString().split("T")[0]}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error: any) {
      set({ error: error.message || "Failed to export monitoring data" });
    }
  },

  setRefreshInterval: (interval: number) => {
    set({ refreshInterval: interval });
  },

  clearError: () => {
    set({ error: null });
  },

  reset: () => {
    set({
      systemMetrics: null,
      performanceData: [],
      alerts: [],
      serviceHealth: [],
      monitoringConfig: null,
      systemLogs: [],
      errorStats: null,
      apiUsageStats: null,
      databaseMetrics: null,
      cacheMetrics: null,
      loading: false,
      error: null,
      refreshInterval: 30000,
    });
  },
}));
