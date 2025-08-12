import api from "./api";
import config from "../config";

export interface SystemMetrics {
  cpu: {
    usage: number;
    cores: number;
    temperature: number;
  };
  memory: {
    total: number;
    used: number;
    available: number;
    usage: number;
  };
  disk: {
    total: number;
    used: number;
    available: number;
    usage: number;
  };
  network: {
    bytesIn: number;
    bytesOut: number;
    packetsIn: number;
    packetsOut: number;
  };
  uptime: number;
  loadAverage: {
    oneMin: number;
    fiveMin: number;
    fifteenMin: number;
  };
}

export interface PerformanceData {
  timestamp: string;
  responseTime: number;
  throughput: number;
  errorRate: number;
  activeConnections: number;
  queueLength: number;
}

export interface Alert {
  id: string;
  type: "info" | "warning" | "error" | "critical";
  title: string;
  message: string;
  timestamp: string;
  acknowledged: boolean;
  acknowledgedBy?: string;
  acknowledgedAt?: string;
  source: string;
  severity: "low" | "medium" | "high" | "critical";
  tags: string[];
}

export interface ServiceHealth {
  service: string;
  status: "healthy" | "degraded" | "down" | "unknown";
  responseTime: number;
  lastCheck: string;
  uptime: number;
  version: string;
  endpoints: {
    name: string;
    status: "up" | "down";
    responseTime: number;
  }[];
}

export interface MonitoringConfig {
  alertThresholds: {
    cpu: number;
    memory: number;
    disk: number;
    responseTime: number;
    errorRate: number;
  };
  checkIntervals: {
    system: number;
    services: number;
    alerts: number;
  };
  notifications: {
    email: boolean;
    slack: boolean;
    webhook: string;
  };
}

export const monitoringService = {
  // Get real-time system metrics
  getSystemMetrics: async (): Promise<SystemMetrics> => {
    const response = await api.get(
      `${config.apiEndpoints.monitoring}/metrics/system`,
    );
    return response.data;
  },

  // Get performance data over time
  getPerformanceData: async (
    timeRange: string,
    interval: string = "1m",
  ): Promise<PerformanceData[]> => {
    const response = await api.get(
      `${config.apiEndpoints.monitoring}/performance`,
      {
        params: { timeRange, interval },
      },
    );
    return response.data;
  },

  // Get all alerts
  getAlerts: async (filters?: {
    type?: string;
    severity?: string;
    acknowledged?: boolean;
    source?: string;
  }): Promise<Alert[]> => {
    const response = await api.get(`${config.apiEndpoints.monitoring}/alerts`, {
      params: filters,
    });
    return response.data;
  },

  // Acknowledge an alert
  acknowledgeAlert: async (alertId: string, userId: string): Promise<Alert> => {
    const response = await api.post(
      `${config.apiEndpoints.monitoring}/alerts/${alertId}/acknowledge`,
      {
        userId,
      },
    );
    return response.data;
  },

  // Get service health status
  getServiceHealth: async (): Promise<ServiceHealth[]> => {
    const response = await api.get(
      `${config.apiEndpoints.monitoring}/health/services`,
    );
    return response.data;
  },

  // Get specific service health
  getServiceHealthById: async (serviceId: string): Promise<ServiceHealth> => {
    const response = await api.get(
      `${config.apiEndpoints.monitoring}/health/services/${serviceId}`,
    );
    return response.data;
  },

  // Get monitoring configuration
  getMonitoringConfig: async (): Promise<MonitoringConfig> => {
    const response = await api.get(`${config.apiEndpoints.monitoring}/config`);
    return response.data;
  },

  // Update monitoring configuration
  updateMonitoringConfig: async (
    config: Partial<MonitoringConfig>,
  ): Promise<MonitoringConfig> => {
    const response = await api.put(
      `${config.apiEndpoints.monitoring}/config`,
      config,
    );
    return response.data;
  },

  // Get system logs
  getSystemLogs: async (filters?: {
    level?: string;
    service?: string;
    startTime?: string;
    endTime?: string;
    limit?: number;
  }): Promise<any[]> => {
    const response = await api.get(`${config.apiEndpoints.monitoring}/logs`, {
      params: filters,
    });
    return response.data;
  },

  // Get error statistics
  getErrorStats: async (timeRange: string = "24h"): Promise<any> => {
    const response = await api.get(
      `${config.apiEndpoints.monitoring}/stats/errors`,
      {
        params: { timeRange },
      },
    );
    return response.data;
  },

  // Get API usage statistics
  getApiUsageStats: async (timeRange: string = "24h"): Promise<any> => {
    const response = await api.get(
      `${config.apiEndpoints.monitoring}/stats/api-usage`,
      {
        params: { timeRange },
      },
    );
    return response.data;
  },

  // Get database performance metrics
  getDatabaseMetrics: async (): Promise<any> => {
    const response = await api.get(
      `${config.apiEndpoints.monitoring}/metrics/database`,
    );
    return response.data;
  },

  // Get cache performance metrics
  getCacheMetrics: async (): Promise<any> => {
    const response = await api.get(
      `${config.apiEndpoints.monitoring}/metrics/cache`,
    );
    return response.data;
  },

  // Trigger manual health check
  triggerHealthCheck: async (serviceId?: string): Promise<any> => {
    const url = serviceId
      ? `${config.apiEndpoints.monitoring}/health/check/${serviceId}`
      : `${config.apiEndpoints.monitoring}/health/check`;
    const response = await api.post(url);
    return response.data;
  },

  // Get monitoring dashboard data
  getDashboardData: async (): Promise<any> => {
    const response = await api.get(
      `${config.apiEndpoints.monitoring}/dashboard`,
    );
    return response.data;
  },

  // Export monitoring data
  exportMonitoringData: async (
    format: "csv" | "json" = "csv",
    filters?: any,
  ): Promise<Blob> => {
    const response = await api.get(`${config.apiEndpoints.monitoring}/export`, {
      params: { format, ...filters },
      responseType: "blob",
    });
    return response.data;
  },
};
