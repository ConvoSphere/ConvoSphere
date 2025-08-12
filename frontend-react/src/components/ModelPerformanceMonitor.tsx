import React, { useState, useEffect, useRef } from "react";
import {
  Card,
  Row,
  Col,
  Statistic,
  Progress,
  Alert,
  Badge,
  Tag,
  Space,
  Button,
  Select,
  DatePicker,
  Table,
  Typography,
  Tooltip,
  Modal,
  List,
  Timeline,
  Switch,
  notification,
} from "antd";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import {
  ClockCircleOutlined,
  DollarOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  WarningOutlined,
  InfoCircleOutlined,
  BellOutlined,
  SettingOutlined,
  ReloadOutlined,
  EyeOutlined,
  BarChartOutlined,
  TrendingUpOutlined,
  AlertOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
// // import { colors } from "../styles/colors";
import { useAIModelsStore, type AIModel } from "../store/aiModelsStore";
import { aiModelsService } from "../services/aiModels";

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;

interface PerformanceData {
  timestamp: string;
  responseTime: number;
  successRate: number;
  errorRate: number;
  requestsPerMinute: number;
  costPerRequest: number;
  totalRequests: number;
  totalCost: number;
}

interface Alert {
  id: string;
  type: "error" | "warning" | "info";
  title: string;
  message: string;
  timestamp: string;
  modelId: string;
  severity: "low" | "medium" | "high";
  acknowledged: boolean;
}

interface ModelPerformanceMonitorProps {
  modelId?: string;
  showAlerts?: boolean;
  showCharts?: boolean;
  refreshInterval?: number;
}

const ModelPerformanceMonitor: React.FC<ModelPerformanceMonitorProps> = ({
  modelId,
  showAlerts = true,
  showCharts = true,
  refreshInterval = 30000, // 30 seconds
}) => {
  const { t } = useTranslation();
  const { models, selectedModel } = useAIModelsStore();

  const [performanceData, setPerformanceData] = useState<PerformanceData[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState("1h");
  const [selectedModelId, setSelectedModelId] = useState(modelId || "");
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [alertSettings, setAlertSettings] = useState({
    responseTimeThreshold: 3000,
    errorRateThreshold: 5,
    costThreshold: 0.01,
  });

  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (selectedModelId) {
      loadPerformanceData();
      if (autoRefresh) {
        startAutoRefresh();
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [selectedModelId, timeRange, autoRefresh]);

  const startAutoRefresh = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    intervalRef.current = setInterval(() => {
      loadPerformanceData();
      checkAlerts();
    }, refreshInterval);
  };

  const loadPerformanceData = async () => {
    if (!selectedModelId) return;

    try {
      setLoading(true);
      const data = await aiModelsService.getModelPerformance(
        selectedModelId,
        timeRange,
      );
      setPerformanceData(data);
    } catch (error) {
      console.error("Failed to load performance data:", error);
    } finally {
      setLoading(false);
    }
  };

  const checkAlerts = async () => {
    if (!selectedModelId) return;

    const currentModel = models.find((m) => m.id === selectedModelId);
    if (!currentModel) return;

    const newAlerts: Alert[] = [];

    // Check response time
    if (
      currentModel.performance.responseTime >
      alertSettings.responseTimeThreshold
    ) {
      newAlerts.push({
        id: `response-time-${Date.now()}`,
        type: "warning",
        title: "High Response Time",
        message: `Response time (${currentModel.performance.responseTime}ms) exceeds threshold (${alertSettings.responseTimeThreshold}ms)`,
        timestamp: new Date().toISOString(),
        modelId: selectedModelId,
        severity:
          currentModel.performance.responseTime >
          alertSettings.responseTimeThreshold * 2
            ? "high"
            : "medium",
        acknowledged: false,
      });
    }

    // Check error rate
    if (currentModel.performance.errorRate > alertSettings.errorRateThreshold) {
      newAlerts.push({
        id: `error-rate-${Date.now()}`,
        type: "error",
        title: "High Error Rate",
        message: `Error rate (${currentModel.performance.errorRate}%) exceeds threshold (${alertSettings.errorRateThreshold}%)`,
        timestamp: new Date().toISOString(),
        modelId: selectedModelId,
        severity:
          currentModel.performance.errorRate >
          alertSettings.errorRateThreshold * 2
            ? "high"
            : "medium",
        acknowledged: false,
      });
    }

    // Check cost
    if (currentModel.costPer1kTokens > alertSettings.costThreshold) {
      newAlerts.push({
        id: `cost-${Date.now()}`,
        type: "warning",
        title: "High Cost",
        message: `Cost per 1k tokens ($${currentModel.costPer1kTokens}) exceeds threshold ($${alertSettings.costThreshold})`,
        timestamp: new Date().toISOString(),
        modelId: selectedModelId,
        severity: "medium",
        acknowledged: false,
      });
    }

    if (newAlerts.length > 0) {
      setAlerts((prev) => [...newAlerts, ...prev]);

      // Show notification for high severity alerts
      newAlerts.forEach((alert) => {
        if (alert.severity === "high") {
          notification.error({
            message: alert.title,
            description: alert.message,
            icon: <AlertOutlined />,
          });
        }
      });
    }
  };

  const acknowledgeAlert = (alertId: string) => {
    setAlerts((prev) =>
      prev.map((alert) =>
        alert.id === alertId ? { ...alert, acknowledged: true } : alert,
      ),
    );
  };

  const getPerformanceColor = (value: number, threshold: number) => {
    if (value <= threshold * 0.7) return colors.colorSuccess;
    if (value <= threshold) return colors.colorWarning;
    return colors.colorError;
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high":
        return colors.colorError;
      case "medium":
        return colors.colorWarning;
      case "low":
        return colors.colorInfo;
      default:
        return colors.colorTextSecondary;
    }
  };

  const chartData = performanceData.map((item) => ({
    ...item,
    timestamp: new Date(item.timestamp).toLocaleTimeString(),
  }));

  const alertColumns = [
    {
      title: t("performance.alerts.type"),
      dataIndex: "type",
      key: "type",
      render: (type: string, record: Alert) => (
        <Badge
          status={
            type === "error"
              ? "error"
              : type === "warning"
                ? "warning"
                : "processing"
          }
          text={t(`performance.alerts.types.${type}`)}
        />
      ),
    },
    {
      title: t("performance.alerts.title"),
      dataIndex: "title",
      key: "title",
    },
    {
      title: t("performance.alerts.severity"),
      dataIndex: "severity",
      key: "severity",
      render: (severity: string) => (
        <Tag color={getSeverityColor(severity)}>
          {t(`performance.alerts.severity.${severity}`)}
        </Tag>
      ),
    },
    {
      title: t("performance.alerts.timestamp"),
      dataIndex: "timestamp",
      key: "timestamp",
      render: (timestamp: string) => new Date(timestamp).toLocaleString(),
    },
    {
      title: t("performance.alerts.actions"),
      key: "actions",
      render: (record: Alert) => (
        <Space>
          {!record.acknowledged && (
            <Button size="small" onClick={() => acknowledgeAlert(record.id)}>
              {t("performance.alerts.acknowledge")}
            </Button>
          )}
          <Button size="small" icon={<EyeOutlined />}>
            {t("performance.alerts.view")}
          </Button>
        </Space>
      ),
    },
  ];

  const currentModel = models.find((m) => m.id === selectedModelId);

  return (
    <div>
      {/* Header Controls */}
      <Card style={{ marginBottom: 16 }}>
        <Row gutter={16} align="middle">
          <Col span={6}>
            <Select
              value={selectedModelId}
              onChange={setSelectedModelId}
              placeholder={t("performance.select_model")}
              style={{ width: "100%" }}
            >
              {models.map((model) => (
                <Option key={model.id} value={model.id}>
                  {model.displayName}
                </Option>
              ))}
            </Select>
          </Col>
          <Col span={4}>
            <Select
              value={timeRange}
              onChange={setTimeRange}
              style={{ width: "100%" }}
            >
              <Option value="1h">{t("performance.time_ranges.1h")}</Option>
              <Option value="6h">{t("performance.time_ranges.6h")}</Option>
              <Option value="24h">{t("performance.time_ranges.24h")}</Option>
              <Option value="7d">{t("performance.time_ranges.7d")}</Option>
              <Option value="30d">{t("performance.time_ranges.30d")}</Option>
            </Select>
          </Col>
          <Col span={4}>
            <Switch
              checked={autoRefresh}
              onChange={setAutoRefresh}
              checkedChildren={t("performance.auto_refresh.on")}
              unCheckedChildren={t("performance.auto_refresh.off")}
            />
          </Col>
          <Col span={4}>
            <Button
              icon={<ReloadOutlined />}
              onClick={loadPerformanceData}
              loading={loading}
            >
              {t("performance.refresh")}
            </Button>
          </Col>
          <Col span={6}>
            <Space>
              <Button
                icon={<SettingOutlined />}
                onClick={() => {
                  /* TODO: Open alert settings modal */
                }}
              >
                {t("performance.alert_settings")}
              </Button>
              <Button
                icon={<BellOutlined />}
                onClick={() => {
                  /* TODO: Open alerts modal */
                }}
              >
                {t("performance.alerts.title")} (
                {alerts.filter((a) => !a.acknowledged).length})
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {selectedModelId && currentModel && (
        <>
          {/* Performance Statistics */}
          <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title={t("performance.stats.response_time")}
                  value={currentModel.performance.responseTime}
                  suffix="ms"
                  valueStyle={{
                    color: getPerformanceColor(
                      currentModel.performance.responseTime,
                      alertSettings.responseTimeThreshold,
                    ),
                  }}
                  prefix={<ClockCircleOutlined />}
                />
                <Progress
                  percent={Math.min(
                    (currentModel.performance.responseTime /
                      alertSettings.responseTimeThreshold) *
                      100,
                    100,
                  )}
                  strokeColor={getPerformanceColor(
                    currentModel.performance.responseTime,
                    alertSettings.responseTimeThreshold,
                  )}
                  size="small"
                  style={{ marginTop: 8 }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title={t("performance.stats.success_rate")}
                  value={currentModel.performance.successRate}
                  suffix="%"
                  valueStyle={{
                    color: getPerformanceColor(
                      100 - currentModel.performance.successRate,
                      alertSettings.errorRateThreshold,
                    ),
                  }}
                  prefix={<CheckCircleOutlined />}
                />
                <Progress
                  percent={currentModel.performance.successRate}
                  strokeColor={getPerformanceColor(
                    100 - currentModel.performance.successRate,
                    alertSettings.errorRateThreshold,
                  )}
                  size="small"
                  style={{ marginTop: 8 }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title={t("performance.stats.error_rate")}
                  value={currentModel.performance.errorRate}
                  suffix="%"
                  valueStyle={{
                    color: getPerformanceColor(
                      currentModel.performance.errorRate,
                      alertSettings.errorRateThreshold,
                    ),
                  }}
                  prefix={<ExclamationCircleOutlined />}
                />
                <Progress
                  percent={Math.min(
                    (currentModel.performance.errorRate /
                      alertSettings.errorRateThreshold) *
                      100,
                    100,
                  )}
                  strokeColor={getPerformanceColor(
                    currentModel.performance.errorRate,
                    alertSettings.errorRateThreshold,
                  )}
                  size="small"
                  style={{ marginTop: 8 }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title={t("performance.stats.cost_per_1k")}
                  value={currentModel.costPer1kTokens}
                  precision={4}
                  valueStyle={{
                    color: getPerformanceColor(
                      currentModel.costPer1kTokens,
                      alertSettings.costThreshold,
                    ),
                  }}
                  prefix={<DollarOutlined />}
                />
                <Progress
                  percent={Math.min(
                    (currentModel.costPer1kTokens /
                      alertSettings.costThreshold) *
                      100,
                    100,
                  )}
                  strokeColor={getPerformanceColor(
                    currentModel.costPer1kTokens,
                    alertSettings.costThreshold,
                  )}
                  size="small"
                  style={{ marginTop: 8 }}
                />
              </Card>
            </Col>
          </Row>

          {/* Performance Charts */}
          {showCharts && (
            <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
              <Col xs={24} lg={12}>
                <Card title={t("performance.charts.response_time")}>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="timestamp" />
                      <YAxis />
                      <RechartsTooltip />
                      <Line
                        type="monotone"
                        dataKey="responseTime"
                        stroke={colors.colorPrimary}
                        strokeWidth={2}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Card>
              </Col>
              <Col xs={24} lg={12}>
                <Card title={t("performance.charts.success_rate")}>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="timestamp" />
                      <YAxis />
                      <RechartsTooltip />
                      <Line
                        type="monotone"
                        dataKey="successRate"
                        stroke={colors.colorSuccess}
                        strokeWidth={2}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Card>
              </Col>
              <Col xs={24} lg={12}>
                <Card title={t("performance.charts.requests_per_minute")}>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="timestamp" />
                      <YAxis />
                      <RechartsTooltip />
                      <Bar
                        dataKey="requestsPerMinute"
                        fill={colors.colorPrimary}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </Card>
              </Col>
              <Col xs={24} lg={12}>
                <Card title={t("performance.charts.cost_trend")}>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="timestamp" />
                      <YAxis />
                      <RechartsTooltip />
                      <Line
                        type="monotone"
                        dataKey="costPerRequest"
                        stroke={colors.colorWarning}
                        strokeWidth={2}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Card>
              </Col>
            </Row>
          )}

          {/* Alerts */}
          {showAlerts && (
            <Card
              title={
                <Space>
                  <BellOutlined />
                  {t("performance.alerts.title")}
                  <Badge count={alerts.filter((a) => !a.acknowledged).length} />
                </Space>
              }
            >
              {alerts.length === 0 ? (
                <Alert
                  message={t("performance.alerts.no_alerts")}
                  description={t("performance.alerts.no_alerts_description")}
                  type="success"
                  showIcon
                />
              ) : (
                <Table
                  columns={alertColumns}
                  dataSource={alerts}
                  rowKey="id"
                  pagination={{ pageSize: 5 }}
                  size="small"
                />
              )}
            </Card>
          )}
        </>
      )}

      {!selectedModelId && (
        <Card>
          <Alert
            message={t("performance.no_model_selected")}
            description={t("performance.select_model_to_view")}
            type="info"
            showIcon
          />
        </Card>
      )}
    </div>
  );
};

export default ModelPerformanceMonitor;
