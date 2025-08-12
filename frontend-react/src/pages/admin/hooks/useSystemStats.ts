import { useState, useCallback, useEffect } from "react";
import { message } from "antd";
import { SystemStats } from "../types/admin.types";

export const useSystemStats = () => {
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState(false);

  const loadSystemStats = useCallback(async () => {
    setLoading(true);
    try {
      // Mock data for now - replace with actual API call
      const mockStats: SystemStats = {
        totalUsers: 1250,
        activeUsers: 890,
        totalConversations: 5670,
        totalMessages: 23450,
        totalDocuments: 1234,
        systemUptime: 99.8,
        cpuUsage: 45.2,
        memoryUsage: 67.8,
        diskUsage: 23.4,
      };
      setSystemStats(mockStats);
    } catch (error) {
      message.error("Failed to load system statistics");
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshStats = useCallback(async () => {
    await loadSystemStats();
    message.success("Statistics refreshed");
  }, [loadSystemStats]);

  useEffect(() => {
    loadSystemStats();

    // Auto-refresh every 30 seconds
    const interval = setInterval(loadSystemStats, 30000);

    return () => clearInterval(interval);
  }, [loadSystemStats]);

  return {
    systemStats,
    loading,
    loadSystemStats,
    refreshStats,
  };
};
