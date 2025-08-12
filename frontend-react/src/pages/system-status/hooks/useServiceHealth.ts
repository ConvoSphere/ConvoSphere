import { useState, useEffect } from "react";
import { message } from "antd";
import type { ServiceHealth } from "../../../services/monitoring";

export const useServiceHealth = () => {
  const [serviceHealth, setServiceHealth] = useState<ServiceHealth[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchServiceHealth = async () => {
    try {
      setLoading(true);

      const response = await fetch("/api/v1/monitoring/service-health");
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ServiceHealth[] = await response.json();
      setServiceHealth(data);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Unknown error occurred";
      message.error(`Failed to fetch service health: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const handleHealthCheck = async (serviceId?: string) => {
    try {
      setLoading(true);

      const url = serviceId
        ? `/api/v1/monitoring/health-check/${serviceId}`
        : "/api/v1/monitoring/health-check";

      const response = await fetch(url, { method: "POST" });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Refresh service health data after check
      await fetchServiceHealth();
      message.success("Health check completed successfully");
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Unknown error occurred";
      message.error(`Health check failed: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchServiceHealth();
  }, []);

  return {
    serviceHealth,
    loading,
    fetchServiceHealth,
    handleHealthCheck,
  };
};
