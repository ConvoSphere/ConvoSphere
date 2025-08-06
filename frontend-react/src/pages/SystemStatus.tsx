import React, { useEffect, useState, useRef } from "react";
import {
  Row,
  Col,
  Tag,
  Spin,
  Alert,
  Typography,
  Space,
  Tabs,
  Button,
  Select,
  DatePicker,
  Table,
  List,
  Avatar,
  Tooltip,
  Popconfirm,
  message,
} from "antd";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  LineChart,
  Line,
  BarChart,
  Bar,
} from "recharts";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "../store/authStore";
import { useThemeStore } from "../store/themeStore";
import { useMonitoringStore } from "../store/monitoringStore";
import { RangePickerProps } from "antd/es/date-picker";
import dayjs from "dayjs";

import ModernCard from "../components/ModernCard";
import ModernButton from "../components/ModernButton";
import ModernSelect from "../components/ModernSelect";
import SystemMetrics from "../components/monitoring/SystemMetrics";
import {
  DatabaseOutlined,
  CloudOutlined,
  BugOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ClockCircleOutlined,
  ReloadOutlined,
  LineChartOutlined,
  HddOutlined,
  CloudServerOutlined,
  SafetyOutlined,
  MonitorOutlined,
  DownloadOutlined,
  SettingOutlined,
  WarningOutlined,
  InfoCircleOutlined,
  ThunderboltOutlined,
  DesktopOutlined,
  MemoryOutlined,
  WifiOutlined,
  ApiOutlined,
} from "@ant-design/icons";
import type { Alert as AlertType, ServiceHealth } from "../services/monitoring";

const { Title, Text } = Typography;

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

const SystemStatus: React.FC = () => {
  const { t } = useTranslation();
  const { colors } = useThemeStore();
  const user = useAuthStore((s) => s.user);
  const isAdmin =
    user && (user.role === "admin" || user.role === "super_admin");
  
  // Legacy state for backward compatibility
  const [data, setData] = useState<StatusData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const cpuHistory = useRef<{ time: string; cpu: number }[]>([]);
  const ramHistory = useRef<{ time: string; ram: number }[]>([]);

  // New monitoring store
  const {
    systemMetrics,
    performanceData,
    alerts,
    serviceHealth,
    loading: monitoringLoading,
    error: monitoringError,
    fetchSystemMetrics,
    fetchPerformanceData,
    fetchAlerts,
    fetchServiceHealth,
    acknowledgeAlert,
    triggerHealthCheck,
    exportMonitoringData,
    clearError,
  } = useMonitoringStore();

  // Local state
  const [activeTab, setActiveTab] = useState('overview');
  const [timeRange, setTimeRange] = useState('1h');
  const [selectedService, setSelectedService] = useState<string | null>(null);

  const fetchStatus = async () => {
    try {
      // Use new monitoring service for system metrics
      await fetchSystemMetrics();
      await fetchPerformanceData(timeRange);
      await fetchAlerts();
      await fetchServiceHealth();
      
      // Legacy API call for backward compatibility
      const res = await fetch("/api/v1/users/admin/system-status");
      if (res.ok) {
        const legacyData = await res.json();
        setData(legacyData);
        const now = new Date().toLocaleTimeString();
        // CPU
        cpuHistory.current.push({ time: now, cpu: legacyData.system.cpu_percent });
        if (cpuHistory.current.length > MAX_POINTS) cpuHistory.current.shift();
        // RAM
        ramHistory.current.push({ time: now, ram: legacyData.system.ram.percent });
        if (ramHistory.current.length > MAX_POINTS) ramHistory.current.shift();
      }
      
      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      setError(t("system.load_failed"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!isAdmin) return;

    // Initial fetch
    fetchStatus();

    const timer: NodeJS.Timeout = setInterval(fetchStatus, 5000);

    return () => clearInterval(timer);
  }, [isAdmin, timeRange]);

  // Handle alert acknowledgment
  const handleAcknowledgeAlert = async (alertId: string) => {
    if (!user?.id) return;
    try {
      await acknowledgeAlert(alertId, user.id);
      message.success(t('monitoring.alert_acknowledged'));
    } catch (error) {
      message.error(t('monitoring.acknowledge_error'));
    }
  };

  // Handle manual health check
  const handleHealthCheck = async (serviceId?: string) => {
    try {
      await triggerHealthCheck(serviceId);
      message.success(t('monitoring.health_check_triggered'));
    } catch (error) {
      message.error(t('monitoring.health_check_error'));
    }
  };

  // Handle export
  const handleExport = async (format: 'csv' | 'json' = 'csv') => {
    try {
      await exportMonitoringData(format);
      message.success(t('monitoring.export_success'));
    } catch (error) {
      message.error(t('monitoring.export_error'));
    }
  };

  // Format uptime for display
  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (days > 0) return `${days}d ${hours}h ${minutes}m`;
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  const getStatusColor = (healthy: boolean) => {
    return healthy ? colors.colorSuccess : colors.colorError;
  };

  const getStatusIcon = (healthy: boolean) => {
    return healthy ? <CheckCircleOutlined /> : <ExclamationCircleOutlined />;
  };

  const getSystemStatusColor = (status: string) => {
    switch (status) {
      case "ok":
        return colors.colorSuccess;
      case "degraded":
        return colors.colorWarning;
      default:
        return colors.colorError;
    }
  };

  const getSystemStatusIcon = (status: string) => {
    switch (status) {
      case "ok":
        return <CheckCircleOutlined />;
      case "degraded":
        return <ClockCircleOutlined />;
      default:
        return <ExclamationCircleOutlined />;
    }
  };

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
        <Row justify="space-between" align="middle" style={{ marginBottom: '24px' }}>
          <Col>
            <Title level={2} style={{ margin: 0, color: colors.colorTextBase }}>
              <MonitorOutlined style={{ marginRight: '8px' }} />
              {t('monitoring.system_status')}
            </Title>
            <Text type="secondary" style={{ color: colors.colorTextSecondary }}>
              {t('monitoring.system_status_description')}
            </Text>
          </Col>
          <Col>
            <Space>
              <Tooltip title={t('monitoring.refresh_data')}>
                <ModernButton
                  icon={<ReloadOutlined />}
                  onClick={fetchStatus}
                  loading={loading || monitoringLoading}
                >
                  {t('monitoring.refresh')}
                </ModernButton>
              </Tooltip>
              <Tooltip title={t('monitoring.export_data')}>
                <ModernButton
                  icon={<DownloadOutlined />}
                  onClick={() => handleExport('csv')}
                >
                  {t('monitoring.export')}
                </ModernButton>
              </Tooltip>
            </Space>
          </Col>
        </Row>

        {/* Error Alert */}
        {(error || monitoringError) && (
          <Alert
            message={t('monitoring.error')}
            description={error || monitoringError}
            type="error"
            showIcon
            closable
            onClose={() => {
              setError(null);
              clearError();
            }}
            style={{ marginBottom: '16px' }}
          />
        )}

        {/* Main Content Tabs */}
        <Tabs activeKey={activeTab} onChange={setActiveTab} type="card">
          <Tabs.TabPane
            tab={
              <span>
                <MonitorOutlined />
                {t('monitoring.overview')}
              </span>
            }
            key="overview"
          >
            <ModernCard variant="gradient" size="lg" className="stagger-children">
          <div style={{ textAlign: "center", padding: "32px 0" }}>
            <div
              style={{
                fontSize: "48px",
                marginBottom: "16px",
                filter: "drop-shadow(0 4px 8px rgba(0,0,0,0.1))",
              }}
            >
              🖥️
            </div>
            <Title level={1} style={{ color: "#FFFFFF", margin: 0 }}>
              {t("system.title")}
            </Title>
            <Text style={{ color: "rgba(255,255,255,0.8)", fontSize: "16px" }}>
              {t("system.subtitle")}
            </Text>
          </div>
        </ModernCard>

        <Row gutter={[24, 24]} style={{ marginTop: 32 }}>
          <Col xs={24} lg={16}>
            <ModernCard
              variant="elevated"
              size="lg"
              style={{ marginBottom: 24 }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: 24,
                }}
              >
                <Title level={3} style={{ margin: 0 }}>
                  <LineChartOutlined
                    style={{ marginRight: 8, color: colors.colorPrimary }}
                  />
                  {t("system.real_time_metrics")}
                </Title>
                <Space>
                  <Text type="secondary" style={{ fontSize: "12px" }}>
                    {t("system.last_update")}: {lastUpdate.toLocaleTimeString()}
                  </Text>
                  <ModernButton
                    variant="outlined"
                    icon={<ReloadOutlined />}
                    size="small"
                    onClick={fetchStatus}
                  >
                    {t("common.refresh")}
                  </ModernButton>
                </Space>
              </div>

              <Row gutter={[24, 24]}>
                <Col xs={24} lg={12}>
                  <ModernCard variant="outlined" size="sm">
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        marginBottom: 16,
                      }}
                    >
                      <LineChartOutlined
                        style={{ color: colors.colorPrimary, marginRight: 8 }}
                      />
                      <Text strong>{t("system.metrics.cpu_usage")}</Text>
                    </div>
                    <ResponsiveContainer width="100%" height={200}>
                      <AreaChart
                        data={cpuHistory.current}
                        margin={{ left: 0, right: 0, top: 8, bottom: 8 }}
                      >
                        <XAxis dataKey="time" minTickGap={20} />
                        <YAxis domain={[0, 100]} />
                        <Tooltip />
                        <CartesianGrid strokeDasharray="3 3" />
                        <Area
                          type="monotone"
                          dataKey="cpu"
                          stroke={colors.colorPrimary}
                          fill={colors.colorPrimary}
                          fillOpacity={0.3}
                          dot={false}
                          isAnimationActive={false}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                    <div style={{ textAlign: "center", marginTop: 8 }}>
                      <Text
                        strong
                        style={{ fontSize: "24px", color: colors.colorPrimary }}
                      >
                        {data.system.cpu_percent.toFixed(1)}%
                      </Text>
                    </div>
                  </ModernCard>
                </Col>

                <Col xs={24} lg={12}>
                  <ModernCard variant="outlined" size="sm">
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        marginBottom: 16,
                      }}
                    >
                      <HddOutlined
                        style={{ color: colors.colorSuccess, marginRight: 8 }}
                      />
                      <Text strong>{t("system.metrics.ram_usage")}</Text>
                    </div>
                    <ResponsiveContainer width="100%" height={200}>
                      <AreaChart
                        data={ramHistory.current}
                        margin={{ left: 0, right: 0, top: 8, bottom: 8 }}
                      >
                        <XAxis dataKey="time" minTickGap={20} />
                        <YAxis domain={[0, 100]} />
                        <Tooltip />
                        <CartesianGrid strokeDasharray="3 3" />
                        <Area
                          type="monotone"
                          dataKey="ram"
                          stroke={colors.colorSuccess}
                          fill={colors.colorSuccess}
                          fillOpacity={0.3}
                          dot={false}
                          isAnimationActive={false}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                    <div style={{ textAlign: "center", marginTop: 8 }}>
                      <Text
                        strong
                        style={{ fontSize: "24px", color: colors.colorSuccess }}
                      >
                        {data.system.ram.percent.toFixed(1)}%
                      </Text>
                    </div>
                  </ModernCard>
                </Col>
              </Row>
            </ModernCard>

            <ModernCard variant="elevated" size="lg">
              <Title level={3} style={{ marginBottom: 24 }}>
                <CloudServerOutlined
                  style={{ marginRight: 8, color: colors.colorPrimary }}
                />
                {t("system.service_status")}
              </Title>

              <Row gutter={[24, 24]}>
                <Col xs={24} sm={8}>
                  <ModernCard variant="interactive" size="md">
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        marginBottom: 12,
                      }}
                    >
                      <DatabaseOutlined
                        style={{
                          color: getStatusColor(data.database.healthy),
                          marginRight: 8,
                          fontSize: "20px",
                        }}
                      />
                      <Text strong>{t("system.metrics.database")}</Text>
                    </div>
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                      }}
                    >
                      <Tag color={data.database.healthy ? "success" : "error"}>
                        {data.database.healthy
                          ? t("system.status.ok")
                          : t("system.status.error")}
                      </Tag>
                      {getStatusIcon(data.database.healthy)}
                    </div>
                  </ModernCard>
                </Col>

                <Col xs={24} sm={8}>
                  <ModernCard variant="interactive" size="md">
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        marginBottom: 12,
                      }}
                    >
                      <CloudOutlined
                        style={{
                          color: getStatusColor(data.redis.healthy),
                          marginRight: 8,
                          fontSize: "20px",
                        }}
                      />
                      <Text strong>{t("system.metrics.redis")}</Text>
                    </div>
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                      }}
                    >
                      <Tag color={data.redis.healthy ? "success" : "error"}>
                        {data.redis.healthy
                          ? t("system.status.ok")
                          : t("system.status.error")}
                      </Tag>
                      {getStatusIcon(data.redis.healthy)}
                    </div>
                  </ModernCard>
                </Col>

                <Col xs={24} sm={8}>
                  <ModernCard variant="interactive" size="md">
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        marginBottom: 12,
                      }}
                    >
                      <BugOutlined
                        style={{
                          color: getStatusColor(data.weaviate.healthy),
                          marginRight: 8,
                          fontSize: "20px",
                        }}
                      />
                      <Text strong>{t("system.metrics.weaviate")}</Text>
                    </div>
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                      }}
                    >
                      <Tag color={data.weaviate.healthy ? "success" : "error"}>
                        {data.weaviate.healthy
                          ? t("system.status.ok")
                          : t("system.status.error")}
                      </Tag>
                      {getStatusIcon(data.weaviate.healthy)}
                    </div>
                  </ModernCard>
                </Col>
              </Row>
            </ModernCard>
          </Col>

          <Col xs={24} lg={8}>
            <ModernCard
              variant="interactive"
              size="md"
              style={{ marginBottom: 24 }}
            >
              <Title level={4}>
                <SafetyOutlined
                  style={{ marginRight: 8, color: colors.colorPrimary }}
                />
                {t("system.overall_status")}
              </Title>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  marginBottom: 16,
                }}
              >
                <Text strong>{t("system.metrics.system_status")}</Text>
                <Tag color={data.status === "ok" ? "success" : "warning"}>
                  {data.status === "ok"
                    ? t("system.status.ok")
                    : t("system.status.degraded")}
                </Tag>
              </div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <div
                  style={{
                    fontSize: "48px",
                    color: getSystemStatusColor(data.status),
                  }}
                >
                  {getSystemStatusIcon(data.status)}
                </div>
              </div>
            </ModernCard>

            <ModernCard
              variant="outlined"
              size="md"
              style={{ marginBottom: 24 }}
            >
              <Title level={4}>{t("system.quick_stats")}</Title>
              <div
                style={{ display: "flex", flexDirection: "column", gap: 16 }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <Text>{t("system.stats.uptime")}</Text>
                  <Text strong style={{ color: colors.colorSuccess }}>
                    99.9%
                  </Text>
                </div>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <Text>{t("system.stats.response_time")}</Text>
                  <Text strong style={{ color: colors.colorPrimary }}>
                    45ms
                  </Text>
                </div>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <Text>{t("system.stats.active_connections")}</Text>
                  <Text strong style={{ color: colors.colorWarning }}>
                    127
                  </Text>
                </div>
              </div>
            </ModernCard>

            <ModernCard variant="elevated" size="md">
              <Title level={4}>{t("system.trace_info")}</Title>
              <div
                style={{
                  backgroundColor: colors.colorBgContainer,
                  padding: "12px",
                  borderRadius: "8px",
                  fontFamily: "monospace",
                  fontSize: "12px",
                  wordBreak: "break-all",
                }}
              >
                {data.tracing.trace_id || "-"}
              </div>
              <Text
                type="secondary"
                style={{ fontSize: "12px", marginTop: 8, display: "block" }}
              >
                {t("system.trace_description")}
              </Text>
            </ModernCard>
          </Col>
        </Row>
          </Tabs.TabPane>

          {/* System Metrics Tab */}
          <Tabs.TabPane
            tab={
              <span>
                <DesktopOutlined />
                {t('monitoring.system_metrics')}
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
                {t('monitoring.performance')}
              </span>
            }
            key="performance"
          >
            <ModernCard>
              <Row gutter={[16, 16]} style={{ marginBottom: '16px' }}>
                <Col xs={24} sm={12} md={6}>
                  <ModernSelect
                    value={timeRange}
                    onChange={setTimeRange}
                    style={{ width: '100%' }}
                  >
                    <Select.Option value="1h">{t('monitoring.last_hour')}</Select.Option>
                    <Select.Option value="6h">{t('monitoring.last_6_hours')}</Select.Option>
                    <Select.Option value="24h">{t('monitoring.last_24_hours')}</Select.Option>
                    <Select.Option value="7d">{t('monitoring.last_7_days')}</Select.Option>
                  </ModernSelect>
                </Col>
              </Row>
              
              {performanceData.length > 0 ? (
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="timestamp" 
                      tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                    />
                    <YAxis />
                    <RechartsTooltip 
                      labelFormatter={(value) => new Date(value).toLocaleString()}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="responseTime" 
                      stroke="#1890ff" 
                      name={t('monitoring.response_time')}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="throughput" 
                      stroke="#52c41a" 
                      name={t('monitoring.throughput')}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="errorRate" 
                      stroke="#ff4d4f" 
                      name={t('monitoring.error_rate')}
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div style={{ textAlign: 'center', padding: '40px' }}>
                  <Text type="secondary">{t('monitoring.no_performance_data')}</Text>
                </div>
              )}
            </ModernCard>
          </Tabs.TabPane>

          {/* Alerts Tab */}
          <Tabs.TabPane
            tab={
              <span>
                <WarningOutlined />
                {t('monitoring.alerts')}
                {alerts.length > 0 && (
                  <Tag color="red" style={{ marginLeft: 8 }}>
                    {alerts.filter(a => !a.acknowledged).length}
                  </Tag>
                )}
              </span>
            }
            key="alerts"
          >
            <ModernCard>
              {alerts.length > 0 ? (
                <List
                  dataSource={alerts}
                  renderItem={(alert: AlertType) => (
                    <List.Item
                      actions={[
                        !alert.acknowledged && (
                          <ModernButton
                            key="acknowledge"
                            size="small"
                            onClick={() => handleAcknowledgeAlert(alert.id)}
                          >
                            {t('monitoring.acknowledge')}
                          </ModernButton>
                        ),
                      ].filter(Boolean)}
                    >
                      <List.Item.Meta
                        avatar={
                          <Avatar
                            icon={
                              alert.type === 'critical' ? <ExclamationCircleOutlined /> :
                              alert.type === 'error' ? <ExclamationCircleOutlined /> :
                              alert.type === 'warning' ? <WarningOutlined /> :
                              <InfoCircleOutlined />
                            }
                            style={{
                              backgroundColor: 
                                alert.type === 'critical' ? '#ff4d4f' :
                                alert.type === 'error' ? '#ff7875' :
                                alert.type === 'warning' ? '#faad14' :
                                '#1890ff'
                            }}
                          />
                        }
                        title={
                          <Space>
                            <Text strong>{alert.title}</Text>
                            <Tag color={
                              alert.severity === 'critical' ? 'red' :
                              alert.severity === 'high' ? 'orange' :
                              alert.severity === 'medium' ? 'gold' :
                              'blue'
                            }>
                              {t(`monitoring.severity.${alert.severity}`)}
                            </Tag>
                            {alert.acknowledged && (
                              <Tag color="green">{t('monitoring.acknowledged')}</Tag>
                            )}
                          </Space>
                        }
                        description={
                          <Space direction="vertical" size="small">
                            <Text>{alert.message}</Text>
                            <Text type="secondary" style={{ fontSize: '12px' }}>
                              {t('monitoring.source')}: {alert.source} | 
                              {t('monitoring.timestamp')}: {new Date(alert.timestamp).toLocaleString()}
                            </Text>
                          </Space>
                        }
                      />
                    </List.Item>
                  )}
                />
              ) : (
                <div style={{ textAlign: 'center', padding: '40px' }}>
                  <Text type="secondary">{t('monitoring.no_alerts')}</Text>
                </div>
              )}
            </ModernCard>
          </Tabs.TabPane>

          {/* Service Health Tab */}
          <Tabs.TabPane
            tab={
              <span>
                <SafetyOutlined />
                {t('monitoring.service_health')}
              </span>
            }
            key="services"
          >
            <ModernCard>
              <Row gutter={[16, 16]}>
                {serviceHealth.map((service: ServiceHealth) => (
                  <Col xs={24} sm={12} lg={8} key={service.service}>
                    <Card size="small">
                      <div style={{ textAlign: 'center' }}>
                        <Avatar
                          size={48}
                          icon={
                            service.status === 'healthy' ? <CheckCircleOutlined /> :
                            service.status === 'degraded' ? <WarningOutlined /> :
                            <ExclamationCircleOutlined />
                          }
                          style={{
                            backgroundColor: 
                              service.status === 'healthy' ? '#52c41a' :
                              service.status === 'degraded' ? '#faad14' :
                              '#ff4d4f',
                            marginBottom: 8
                          }}
                        />
                        <Title level={5} style={{ marginTop: 8 }}>
                          {service.service}
                        </Title>
                        <Space direction="vertical" size="small">
                          <Tag color={
                            service.status === 'healthy' ? 'success' :
                            service.status === 'degraded' ? 'warning' :
                            'error'
                          }>
                            {t(`monitoring.status.${service.status}`)}
                          </Tag>
                          <Text type="secondary">
                            {t('monitoring.response_time')}: {service.responseTime}ms
                          </Text>
                          <Text type="secondary">
                            {t('monitoring.uptime')}: {formatUptime(service.uptime)}
                          </Text>
                          <Text type="secondary">
                            {t('monitoring.version')}: {service.version}
                          </Text>
                        </Space>
                        <div style={{ marginTop: 8 }}>
                          <ModernButton
                            size="small"
                            onClick={() => handleHealthCheck(service.service)}
                          >
                            {t('monitoring.check_health')}
                          </ModernButton>
                        </div>
                      </div>
                    </Card>
                  </Col>
                ))}
              </Row>
            </ModernCard>
          </Tabs.TabPane>
        </Tabs>
      </div>
    </div>
  );
};

export default SystemStatus;
