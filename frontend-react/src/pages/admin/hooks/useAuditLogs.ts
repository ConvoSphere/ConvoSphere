import { useState, useCallback, useEffect } from "react";
import { message } from "antd";
import { AuditLog } from "../types/admin.types";

export const useAuditLogs = () => {
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });

  const loadAuditLogs = useCallback(
    async (page: number = 1, pageSize: number = 20) => {
      setLoading(true);
      try {
        // Mock data for now - replace with actual API call
        const mockLogs: AuditLog[] = [
          {
            id: "1",
            userId: 1,
            username: "admin",
            action: "LOGIN",
            resource: "AUTH",
            details: "User logged in successfully",
            ipAddress: "192.168.1.100",
            timestamp: "2024-01-15T10:30:00Z",
            status: "success",
          },
          {
            id: "2",
            userId: 2,
            username: "user1",
            action: "CREATE",
            resource: "DOCUMENT",
            details: 'Document "report.pdf" created',
            ipAddress: "192.168.1.101",
            timestamp: "2024-01-15T09:15:00Z",
            status: "success",
          },
          {
            id: "3",
            userId: 3,
            username: "user2",
            action: "UPDATE",
            resource: "PROFILE",
            details: "Profile information updated",
            ipAddress: "192.168.1.102",
            timestamp: "2024-01-15T08:45:00Z",
            status: "success",
          },
          {
            id: "4",
            userId: 4,
            username: "user3",
            action: "DELETE",
            resource: "MESSAGE",
            details: "Failed to delete message - insufficient permissions",
            ipAddress: "192.168.1.103",
            timestamp: "2024-01-15T08:30:00Z",
            status: "failed",
          },
        ];

        setAuditLogs(mockLogs);
        setPagination((prev) => ({
          ...prev,
          current: page,
          pageSize,
          total: mockLogs.length,
        }));
      } catch (error) {
        message.error("Failed to load audit logs");
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  const handleTableChange = useCallback(
    (pagination: any) => {
      loadAuditLogs(pagination.current, pagination.pageSize);
    },
    [loadAuditLogs],
  );

  const exportLogs = useCallback(async () => {
    try {
      // Mock export functionality - replace with actual API call
      const csvContent = auditLogs
        .map(
          (log) =>
            `${log.timestamp},${log.username},${log.action},${log.resource},${log.status}`,
        )
        .join("\n");

      const blob = new Blob([csvContent], { type: "text/csv" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `audit-logs-${new Date().toISOString().split("T")[0]}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);

      message.success("Audit logs exported successfully");
    } catch (error) {
      message.error("Failed to export audit logs");
    }
  }, [auditLogs]);

  const clearLogs = useCallback(async () => {
    try {
      // Mock clear functionality - replace with actual API call
      setAuditLogs([]);
      setPagination((prev) => ({ ...prev, total: 0 }));
      message.success("Audit logs cleared successfully");
    } catch (error) {
      message.error("Failed to clear audit logs");
    }
  }, []);

  useEffect(() => {
    loadAuditLogs();
  }, [loadAuditLogs]);

  return {
    auditLogs,
    loading,
    pagination,
    loadAuditLogs,
    handleTableChange,
    exportLogs,
    clearLogs,
  };
};
