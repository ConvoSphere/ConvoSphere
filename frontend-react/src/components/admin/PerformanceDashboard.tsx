import React, { useState, useEffect } from "react";
import {
  Card,
  Row,
  Col,
  Statistic,
  Progress,
  Table,
  Tag,
  Typography,
  Space,
  Button,
  DatePicker,
  Select,
  Alert,
  Spin,
  Divider,
  List,
  Badge,
} from "antd";
import {
  DashboardOutlined,
  AlertOutlined,
  ClockCircleOutlined,
  DatabaseOutlined,
  CloudOutlined,
  DesktopOutlined,
  HddOutlined,
  ReloadOutlined,
  LineChartOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  InfoCircleOutlined,
  GlobalOutlined,
} from "@ant-design/icons";
import { LineChart, Line, BarChart, Bar, PieChart, Pie, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;

interface PerformanceMetrics {
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
  network_bytes_sent_per_sec: number;
  network_bytes_recv_per_sec: number;
  memory_available_gb: number;
  disk_free_gb: number;
}

interface DatabaseMetrics {
  avg_query_time: number;
  max_query_time: number;
  total_queries: number;
  slow_queries_count: number;
}

interface CacheMetrics {
  hits: number;
  misses: number;
  hit_rate: number;
  evictions: number;
  set_operations: number;
  get_operations: number;
  delete_operations: number;
  memory_cache_size: number;
  memory_cache_capacity: number;
}

interface Alert {
  name: string;
  message: string;
  severity: string;
  timestamp: string;
  metric_name: string;
  threshold: number;
  current_value: number;
  tags: Record<string, string>;
}

interface PerformanceReport {
  period: {
    start: string;
    end: string;
  };
  system_metrics: Record<string, any>;
  application_metrics: Record<string, any>;
  database_metrics: Record<string, any>;
  cache_metrics: Record<string, any>;
  alerts: Alert[];
}

const PerformanceDashboard: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [dbMetrics, setDbMetrics] = useState<DatabaseMetrics | null>(null);
  const [cacheMetrics, setCacheMetrics] = useState<CacheMetrics | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [report, setReport] = useState<PerformanceReport | null>(null);
  const [timeRange, setTimeRange] = useState<[string, string]>([
    new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    new Date().toISOString(),
  ]);
  const [refreshInterval, setRefreshInterval] = useState<number>(30);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, refreshInterval * 1000);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  useEffect(() => {
    fetchReport();
  }, [timeRange]);

  const fetchMetrics = async () => {
    try {
      const [metricsRes, dbRes, cacheRes, alertsRes] = await Promise.all([
        fetch("/api/v1/monitoring/metrics"),
        fetch("/api/v1/monitoring/database"),
        fetch("/api/v1/monitoring/cache"),
        fetch("/api/v1/monitoring/alerts"),
      ]);

      if (metricsRes.ok) {
        const metricsData = await metricsRes.json();
        setMetrics(metricsData);
      }

      if (dbRes.ok) {
        const dbData = await dbRes.json();
        setDbMetrics(dbData);
      }

      if (cacheRes.ok) {
        const cacheData = await cacheRes.json();
        setCacheMetrics(cacheData);
      }

      if (alertsRes.ok) {
        const alertsData = await alertsRes.json();
        setAlerts(alertsData);
      }
    } catch (error) {
      console.error("Failed to fetch metrics:", error);
    }
  };

  const fetchReport = async () => {
    setLoading(true);
    try {
      const response = await fetch("/api/v1/monitoring/report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          since: timeRange[0],
          until: timeRange[1],
        }),
      });

      if (response.ok) {
        const reportData = await response.json();
        setReport(reportData);
      }
    } catch (error) {
      console.error("Failed to fetch report:", error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "critical":
        return "red";
      case "error":
        return "orange";
      case "warning":
        return "gold";
      case "info":
        return "blue";
      default:
        return "default";
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "critical":
        return <ExclamationCircleOutlined />;
      case "error":
        return <ExclamationCircleOutlined />;
      case "warning":
        return <WarningOutlined />;
      case "info":
        return <InfoCircleOutlined />;
      default:
        return <InfoCircleOutlined />;
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const formatDuration = (seconds: number) => {
    if (seconds < 1) return `${(seconds * 1000).toFixed(2)}ms`;
    return `${seconds.toFixed(2)}s`;
  };

  // Chart configurations
  const systemChartConfig = {
    data: report?.system_metrics ? Object.entries(report.system_metrics).map(([key, value]) => ({
      metric: key,
      value: value.average || 0,
      max: value.max || 0,
    })) : [],
    xField: "metric",
    yField: "value",
    seriesField: "type",
    color: ["#1890ff", "#52c41a"],
  };

  const alertsChartConfig = {
    data: alerts.reduce((acc, alert) => {
      const severity = alert.severity.toLowerCase();
      acc[severity] = (acc[severity] || 0) + 1;
      return acc;
    }, {} as Record<string, number>),
    angleField: "value",
    colorField: "type",
    radius: 0.8,
    label: {
      type: "outer",
      content: "{name} {percentage}",
    },
  };

  return (
    <div>
      <Title level={2}>
        <DashboardOutlined /> Performance Dashboard
      </Title>

      {/* Controls */}
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Button
            type="primary"
            icon={<ReloadOutlined />}
            onClick={fetchMetrics}
            loading={loading}
          >
            Refresh
          </Button>
          <RangePicker
            showTime
            value={[new Date(timeRange[0]), new Date(timeRange[1])]}
            onChange={(dates) => {
              if (dates) {
                setTimeRange([dates[0]!.toISOString(), dates[1]!.toISOString()]);
              }
            }}
          />
          <Select
            value={refreshInterval}
            onChange={setRefreshInterval}
            style={{ width: 120 }}
          >
            <Option value={10}>10s</Option>
            <Option value={30}>30s</Option>
            <Option value={60}>1m</Option>
            <Option value={300}>5m</Option>
          </Select>
        </Space>
      </Card>

      {/* System Metrics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="CPU Usage"
              value={metrics?.cpu_percent || 0}
              suffix="%"
              prefix={<DesktopOutlined />}
              valueStyle={{ color: metrics?.cpu_percent > 80 ? "#cf1322" : "#3f8600" }}
            />
            <Progress
              percent={metrics?.cpu_percent || 0}
              status={metrics?.cpu_percent > 80 ? "exception" : "normal"}
              showInfo={false}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Memory Usage"
              value={metrics?.memory_percent || 0}
              suffix="%"
              prefix={<DesktopOutlined />}
              valueStyle={{ color: metrics?.memory_percent > 85 ? "#cf1322" : "#3f8600" }}
            />
            <Progress
              percent={metrics?.memory_percent || 0}
              status={metrics?.memory_percent > 85 ? "exception" : "normal"}
              showInfo={false}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Disk Usage"
              value={metrics?.disk_percent || 0}
              suffix="%"
              prefix={<HddOutlined />}
              valueStyle={{ color: metrics?.disk_percent > 90 ? "#cf1322" : "#3f8600" }}
            />
            <Progress
              percent={metrics?.disk_percent || 0}
              status={metrics?.disk_percent > 90 ? "exception" : "normal"}
              showInfo={false}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Cache Hit Rate"
              value={cacheMetrics?.hit_rate ? (cacheMetrics.hit_rate * 100).toFixed(1) : 0}
              suffix="%"
              prefix={<CloudOutlined />}
              valueStyle={{ color: cacheMetrics?.hit_rate > 0.8 ? "#3f8600" : "#cf1322" }}
            />
            <Progress
              percent={cacheMetrics?.hit_rate ? cacheMetrics.hit_rate * 100 : 0}
              status={cacheMetrics?.hit_rate > 0.8 ? "normal" : "exception"}
              showInfo={false}
            />
          </Card>
        </Col>
      </Row>

      {/* Database and Cache Metrics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={12}>
          <Card title={<><DatabaseOutlined /> Database Performance</>}>
            <Row gutter={16}>
              <Col span={12}>
                <Statistic
                  title="Avg Query Time"
                  value={dbMetrics?.avg_query_time ? formatDuration(dbMetrics.avg_query_time) : "0ms"}
                  prefix={<ClockCircleOutlined />}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="Total Queries"
                  value={dbMetrics?.total_queries || 0}
                  prefix={<DatabaseOutlined />}
                />
              </Col>
            </Row>
            <Divider />
            <Row gutter={16}>
              <Col span={12}>
                <Statistic
                  title="Max Query Time"
                  value={dbMetrics?.max_query_time ? formatDuration(dbMetrics.max_query_time) : "0ms"}
                  prefix={<ClockCircleOutlined />}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="Slow Queries"
                  value={dbMetrics?.slow_queries_count || 0}
                  prefix={<AlertOutlined />}
                  valueStyle={{ color: dbMetrics?.slow_queries_count > 0 ? "#cf1322" : "#3f8600" }}
                />
              </Col>
            </Row>
          </Card>
        </Col>
        <Col span={12}>
          <Card title={<><CloudOutlined /> Cache Performance</>}>
            <Row gutter={16}>
              <Col span={12}>
                <Statistic
                  title="Cache Hits"
                  value={cacheMetrics?.hits || 0}
                  prefix={<CheckCircleOutlined />}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="Cache Misses"
                  value={cacheMetrics?.misses || 0}
                  prefix={<AlertOutlined />}
                />
              </Col>
            </Row>
            <Divider />
            <Row gutter={16}>
              <Col span={12}>
                <Statistic
                  title="Memory Cache Size"
                  value={cacheMetrics?.memory_cache_size || 0}
                  suffix={`/ ${cacheMetrics?.memory_cache_capacity || 0}`}
                  prefix={<DesktopOutlined />}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="Evictions"
                  value={cacheMetrics?.evictions || 0}
                  prefix={<AlertOutlined />}
                />
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* Network and Storage */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={12}>
          <Card title={<><GlobalOutlined /> Network I/O</>}>
            <Row gutter={16}>
              <Col span={12}>
                <Statistic
                  title="Bytes Sent/sec"
                  value={metrics?.network_bytes_sent_per_sec ? formatBytes(metrics.network_bytes_sent_per_sec) : "0 B"}
                  prefix={<GlobalOutlined />}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="Bytes Received/sec"
                  value={metrics?.network_bytes_recv_per_sec ? formatBytes(metrics.network_bytes_recv_per_sec) : "0 B"}
                  prefix={<GlobalOutlined />}
                />
              </Col>
            </Row>
          </Card>
        </Col>
        <Col span={12}>
          <Card title={<><HddOutlined /> Storage</>}>
            <Row gutter={16}>
              <Col span={12}>
                <Statistic
                  title="Available Memory"
                  value={metrics?.memory_available_gb ? `${metrics.memory_available_gb.toFixed(2)} GB` : "0 GB"}
                  prefix={<DesktopOutlined />}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="Free Disk Space"
                  value={metrics?.disk_free_gb ? `${metrics.disk_free_gb.toFixed(2)} GB` : "0 GB"}
                  prefix={<HddOutlined />}
                />
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* Alerts */}
      <Card
        title={
          <Space>
            <AlertOutlined />
            Active Alerts
            <Badge count={alerts.length} style={{ backgroundColor: "#52c41a" }} />
          </Space>
        }
        style={{ marginBottom: 24 }}
      >
        {alerts.length === 0 ? (
          <Alert
            message="No active alerts"
            description="All systems are operating normally."
            type="success"
            showIcon
          />
        ) : (
          <List
            dataSource={alerts}
            renderItem={(alert) => (
              <List.Item>
                <List.Item.Meta
                  avatar={
                    <Tag color={getSeverityColor(alert.severity)} icon={getSeverityIcon(alert.severity)}>
                      {alert.severity.toUpperCase()}
                    </Tag>
                  }
                  title={alert.name}
                  description={
                    <Space direction="vertical" size="small">
                      <Text>{alert.message}</Text>
                      <Text type="secondary">
                        {new Date(alert.timestamp).toLocaleString()} | {alert.metric_name}: {alert.current_value} (threshold: {alert.threshold})
                      </Text>
                    </Space>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </Card>

      {/* Performance Charts */}
      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Card title={<><LineChartOutlined /> System Metrics Trend</>}>
            <Bar {...systemChartConfig} height={300} />
          </Card>
        </Col>
        <Col span={12}>
          <Card title={<><LineChartOutlined /> Alerts by Severity</>}>
            <Pie {...alertsChartConfig} height={300} />
          </Card>
        </Col>
      </Row>

      {/* Performance Report */}
      {report && (
        <Card title="Performance Report" style={{ marginTop: 24 }}>
          <Spin spinning={loading}>
            <Row gutter={[16, 16]}>
              <Col span={24}>
                <Text strong>Report Period: </Text>
                <Text>
                  {new Date(report.period.start).toLocaleString()} - {new Date(report.period.end).toLocaleString()}
                </Text>
              </Col>
            </Row>
            <Divider />
            <Row gutter={[16, 16]}>
              <Col span={6}>
                <Card size="small" title="Application Metrics">
                  <List
                    size="small"
                    dataSource={Object.entries(report.application_metrics)}
                    renderItem={([key, value]) => (
                      <List.Item>
                        <Text>{key}: {value.total || value.average?.toFixed(2) || 0}</Text>
                      </List.Item>
                    )}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small" title="Database Metrics">
                  <List
                    size="small"
                    dataSource={Object.entries(report.database_metrics)}
                    renderItem={([key, value]) => (
                      <List.Item>
                        <Text>{key}: {value.average?.toFixed(2) || 0}</Text>
                      </List.Item>
                    )}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small" title="Cache Metrics">
                  <List
                    size="small"
                    dataSource={Object.entries(report.cache_metrics)}
                    renderItem={([key, value]) => (
                      <List.Item>
                        <Text>{key}: {value.average?.toFixed(2) || 0}</Text>
                      </List.Item>
                    )}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small" title="System Metrics">
                  <List
                    size="small"
                    dataSource={Object.entries(report.system_metrics)}
                    renderItem={([key, value]) => (
                      <List.Item>
                        <Text>{key}: {value.average?.toFixed(2) || 0}</Text>
                      </List.Item>
                    )}
                  />
                </Card>
              </Col>
            </Row>
          </Spin>
        </Card>
      )}
    </div>
  );
};

export default PerformanceDashboard;