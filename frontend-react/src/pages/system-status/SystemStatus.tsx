import React, { useState } from "react";
import {
  Row,
  Col,
  Spin,
  Alert,
  Typography,
  Space,
  Tabs,
  Button,
  message,
  Tooltip,
  Tag,
} from "antd";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "../../store/authStore";
import { useThemeStore } from "../../store/themeStore";
import { useMonitoringStore } from "../../store/monitoringStore";
import {
  MonitorOutlined,
  DesktopOutlined,
  LineChartOutlined,
  WarningOutlined,
  SafetyOutlined,
  ReloadOutlined,
  DownloadOutlined,
} from "@ant-design/icons";

import ModernCard from "../../components/ModernCard";
import ModernButton from "../../components/ModernButton";
import SystemMetrics from "../../components/monitoring/SystemMetrics";

// Import modular components
import SystemOverview from "./SystemOverview";
import PerformanceMetrics from "./PerformanceMetrics";
import AlertPanel from "./AlertPanel";
import ServiceStatus from "./ServiceStatus";

// Import custom hooks
import { useSystemStatus } from "./hooks/useSystemStatus";
import { usePerformanceMetrics } from "./hooks/usePerformanceMetrics";
import { useServiceHealth } from "./hooks/useServiceHealth";

const { Title, Text } = Typography;

const SystemStatus: React.FC = () => {
  const { t } = useTranslation();
  const { colors } = useThemeStore();
  const user = useAuthStore((s) => s.user);
  const isAdmin =
    user && (user.role === "admin" || user.role === "super_admin");

  // State for active tab
  const [activeTab, setActiveTab] = useState<string>("overview");

  // Custom hooks for data management
  const {
    data,
    loading,
    error,
    lastUpdate,
    cpuHistory,
    ramHistory,
    fetchStatus,
    clearError,
  } = useSystemStatus();

  const {
    performanceData,
    timeRange,
    loading: performanceLoading,
    handleTimeRangeChange,
  } = usePerformanceMetrics();

  const {
    serviceHealth,
    loading: serviceLoading,
    handleHealthCheck,
  } = useServiceHealth();

  // Monitoring store for alerts and system metrics
  const {
    alerts,
    systemMetrics,
    monitoringLoading,
    monitoringError,
    acknowledgeAlert,
    clearError: clearMonitoringError,
  } = useMonitoringStore();

  const handleAcknowledgeAlert = async (alertId: string) => {
    try {
      await acknowledgeAlert(alertId);
      message.success(t("monitoring.alert_acknowledged"));
    } catch (err) {
      message.error(t("monitoring.alert_acknowledge_failed"));
    }
  };

  const handleExport = async (format: "csv" | "json" = "csv") => {
    try {
      const response = await fetch(
        `/api/v1/monitoring/export?format=${format}`,
      );
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `system-status-${new Date().toISOString().split("T")[0]}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      message.success(t("monitoring.export_success"));
    } catch (err) {
      message.error(t("monitoring.export_failed"));
    }
  };

  // Access control
  if (!isAdmin) {
    return (
      <div
        style={{
          minHeight: "100vh",
          background: colors.colorGradientPrimary,
          padding: "24px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <ModernCard variant="elevated" size="lg">
          <Alert type="error" message={t("errors.forbidden")} showIcon />
        </ModernCard>
      </div>
    );
  }

  // Loading state
  if (loading) {
    return (
      <div
        style={{
          minHeight: "100vh",
          background: colors.colorGradientPrimary,
          padding: "24px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <ModernCard variant="elevated" size="lg">
          <div style={{ textAlign: "center", padding: "40px" }}>
            <Spin size="large" />
            <Text style={{ display: "block", marginTop: 16 }}>
              {t("system.loading")}
            </Text>
          </div>
        </ModernCard>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div
        style={{
          minHeight: "100vh",
          background: colors.colorGradientPrimary,
          padding: "24px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <ModernCard variant="elevated" size="lg">
          <Alert type="error" message={error} showIcon />
        </ModernCard>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div
      style={{
        minHeight: "100vh",
        background: colors.colorGradientPrimary,
        padding: "24px",
      }}
    >
      <div style={{ maxWidth: 1400, margin: "0 auto" }}>
        {/* Header */}
        <Row
          justify="space-between"
          align="middle"
          style={{ marginBottom: "24px" }}
        >
          <Col>
            <Title level={2} style={{ margin: 0, color: colors.colorTextBase }}>
              <MonitorOutlined style={{ marginRight: "8px" }} />
              {t("monitoring.system_status")}
            </Title>
            <Text type="secondary" style={{ color: colors.colorTextSecondary }}>
              {t("monitoring.system_status_description")}
            </Text>
          </Col>
          <Col>
            <Space>
              <Tooltip title={t("monitoring.refresh_data")}>
                <ModernButton
                  icon={<ReloadOutlined />}
                  onClick={fetchStatus}
                  loading={loading || monitoringLoading}
                >
                  {t("monitoring.refresh")}
                </ModernButton>
              </Tooltip>
              <Tooltip title={t("monitoring.export_data")}>
                <ModernButton
                  icon={<DownloadOutlined />}
                  onClick={() => handleExport("csv")}
                >
                  {t("monitoring.export")}
                </ModernButton>
              </Tooltip>
            </Space>
          </Col>
        </Row>

        {/* Error Alert */}
        {(error || monitoringError) && (
          <Alert
            message={t("monitoring.error")}
            description={error || monitoringError}
            type="error"
            showIcon
            closable
            onClose={() => {
              clearError();
              clearMonitoringError();
            }}
            style={{ marginBottom: "16px" }}
          />
        )}

        {/* Main Content Tabs */}
        <Tabs activeKey={activeTab} onChange={setActiveTab} type="card">
          {/* Overview Tab */}
          <Tabs.TabPane
            tab={
              <span>
                <MonitorOutlined />
                {t("monitoring.overview")}
              </span>
            }
            key="overview"
          >
            <SystemOverview
              data={data}
              cpuHistory={cpuHistory}
              ramHistory={ramHistory}
              lastUpdate={lastUpdate}
              onRefresh={fetchStatus}
              loading={loading}
            />
          </Tabs.TabPane>

          {/* System Metrics Tab */}
          <Tabs.TabPane
            tab={
              <span>
                <DesktopOutlined />
                {t("monitoring.system_metrics")}
              </span>
            }
            key="metrics"
          >
            <Spin spinning={monitoringLoading}>
              <SystemMetrics data={systemMetrics} loading={monitoringLoading} />
            </Spin>
          </Tabs.TabPane>

          {/* Performance Tab */}
          <Tabs.TabPane
            tab={
              <span>
                <LineChartOutlined />
                {t("monitoring.performance")}
              </span>
            }
            key="performance"
          >
            <PerformanceMetrics
              performanceData={performanceData}
              timeRange={timeRange}
              onTimeRangeChange={handleTimeRangeChange}
              loading={performanceLoading}
            />
          </Tabs.TabPane>

          {/* Alerts Tab */}
          <Tabs.TabPane
            tab={
              <span>
                <WarningOutlined />
                {t("monitoring.alerts")}
                {alerts.length > 0 && (
                  <Tag color="red" style={{ marginLeft: 8 }}>
                    {alerts.filter((a) => !a.acknowledged).length}
                  </Tag>
                )}
              </span>
            }
            key="alerts"
          >
            <AlertPanel
              alerts={alerts}
              onAcknowledgeAlert={handleAcknowledgeAlert}
              loading={monitoringLoading}
            />
          </Tabs.TabPane>

          {/* Service Health Tab */}
          <Tabs.TabPane
            tab={
              <span>
                <SafetyOutlined />
                {t("monitoring.service_health")}
              </span>
            }
            key="services"
          >
            <ServiceStatus
              serviceHealth={serviceHealth}
              onHealthCheck={handleHealthCheck}
              loading={serviceLoading}
            />
          </Tabs.TabPane>
        </Tabs>
      </div>
    </div>
  );
};

export default SystemStatus;
