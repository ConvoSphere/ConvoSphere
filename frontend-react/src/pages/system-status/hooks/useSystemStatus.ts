import { useState, useEffect, useRef } from "react";
import { message } from "antd";

interface StatusData {
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

const MAX_POINTS = 60; // z.B. 5 Minuten bei 5s Intervall

export const useSystemStatus = () => {
  const [data, setData] = useState<StatusData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const cpuHistory = useRef<{ time: string; cpu: number }[]>([]);
  const ramHistory = useRef<{ time: string; ram: number }[]>([]);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch("/api/v1/system/status");
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const statusData: StatusData = await response.json();
      setData(statusData);
      setLastUpdate(new Date());

      // Update history
      const now = new Date().toLocaleTimeString();
      cpuHistory.current.push({
        time: now,
        cpu: statusData.system.cpu_percent,
      });
      ramHistory.current.push({
        time: now,
        ram: statusData.system.ram.percent,
      });

      // Keep only last MAX_POINTS
      if (cpuHistory.current.length > MAX_POINTS) {
        cpuHistory.current = cpuHistory.current.slice(-MAX_POINTS);
      }
      if (ramHistory.current.length > MAX_POINTS) {
        ramHistory.current = ramHistory.current.slice(-MAX_POINTS);
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Unknown error occurred";
      setError(errorMessage);
      message.error(`Failed to fetch system status: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const clearError = () => {
    setError(null);
  };

  useEffect(() => {
    fetchStatus();

    // Set up interval for real-time updates
    const interval = setInterval(fetchStatus, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, []);

  return {
    data,
    loading,
    error,
    lastUpdate,
    cpuHistory: cpuHistory.current,
    ramHistory: ramHistory.current,
    fetchStatus,
    clearError,
  };
};
