export interface StatusData {
  system: {
    cpu_percent: number;
    ram: { [key: string]: any };
  };
  database: { healthy: boolean; info: any };
  redis: { healthy: boolean; info: any };
  weaviate: { healthy: boolean; info: any };
  tracing: { trace_id: string | null };
  status: string;
}

export interface PerformanceData {
  timestamp: string;
  responseTime: number;
  throughput: number;
  errorRate: number;
}

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
    bytesSent: number;
    bytesReceived: number;
    connections: number;
  };
  uptime: number;
}

export interface Alert {
  id: string;
  title: string;
  message: string;
  type: "critical" | "error" | "warning" | "info";
  severity: "critical" | "high" | "medium" | "low";
  source: string;
  timestamp: string;
  acknowledged: boolean;
}

export interface ServiceHealth {
  service: string;
  status: "healthy" | "degraded" | "unhealthy";
  responseTime: number;
  uptime: number;
  version: string;
  lastCheck: string;
}
