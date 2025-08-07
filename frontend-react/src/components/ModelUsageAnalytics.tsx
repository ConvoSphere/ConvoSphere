import React, { useState, useEffect } from "react";
import {
  Card,
  Row,
  Col,
  Statistic,
  Progress,
  Table,
  Typography,
  Space,
  Tag,
  Button,
  Select,
  DatePicker,
  Tooltip,
  Alert,
  Divider,
  List,
  Badge,
  Modal,
  Form,
  Input,
  Switch,
  message,
  Spin,
  Empty,
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
  AreaChart,
  Area,
  ComposedChart,
  Legend,
} from "recharts";
import {
  BarChartOutlined,
  DollarOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  TrendingUpOutlined,
  TrendingDownOutlined,
  EyeOutlined,
  DownloadOutlined,
  FilterOutlined,
  CalendarOutlined,
  ReloadOutlined,
  SettingOutlined,
  InfoCircleOutlined,
  UserOutlined,
  RobotOutlined,
  ThunderboltOutlined,
  FileTextOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { colors } from "../styles/colors";
import { useAIModelsStore, type AIModel } from "../store/aiModelsStore";
import { aiModelsService } from "../services/aiModels";

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;

interface UsageData {
  timestamp: string;
  modelId: string;
  requests: number;
  tokens: number;
  cost: number;
  responseTime: number;
  successRate: number;
  errorRate: number;
  userId?: string;
  sessionId?: string;
}

interface UsageSummary {
  modelId: string;
  modelName: string;
  totalRequests: number;
  totalTokens: number;
  totalCost: number;
  avgResponseTime: number;
  avgSuccessRate: number;
  avgErrorRate: number;
  peakUsage: {
    timestamp: string;
    requests: number;
  };
  usageTrend: "increasing" | "decreasing" | "stable";
  costTrend: "increasing" | "decreasing" | "stable";
}

interface CostBreakdown {
  modelId: string;
  modelName: string;
  cost: number;
  percentage: number;
  requests: number;
  avgCostPerRequest: number;
}

interface UserUsage {
  userId: string;
  username: string;
  totalRequests: number;
  totalCost: number;
  favoriteModel: string;
  lastActivity: string;
  usagePattern: "heavy" | "moderate" | "light";
}

const ModelUsageAnalytics: React.FC = () => {
  const { t } = useTranslation();
  const { models } = useAIModelsStore();
  
  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState<[string, string]>([
    new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    new Date().toISOString(),
  ]);
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [selectedUsers, setSelectedUsers] = useState<string[]>([]);
  const [viewMode, setViewMode] = useState<"overview" | "detailed" | "costs" | "users">("overview");
  const [refreshInterval, setRefreshInterval] = useState<number>(30000);
  const [autoRefresh, setAutoRefresh] = useState<boolean>(true);
  
  // Data states
  const [usageData, setUsageData] = useState<UsageData[]>([]);
  const [usageSummary, setUsageSummary] = useState<UsageSummary[]>([]);
  const [costBreakdown, setCostBreakdown] = useState<CostBreakdown[]>([]);
  const [userUsage, setUserUsage] = useState<UserUsage[]>([]);
  const [exportModalVisible, setExportModalVisible] = useState(false);
  const [settingsModalVisible, setSettingsModalVisible] = useState(false);

  useEffect(() => {
    loadUsageData();
    
    if (autoRefresh) {
      const interval = setInterval(loadUsageData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [timeRange, selectedModels, selectedUsers, autoRefresh, refreshInterval]);

  const loadUsageData = async () => {
    try {
      setLoading(true);
      
      // Mock data - replace with API calls
      const mockUsageData: UsageData[] = Array.from({ length: 168 }, (_, i) => ({
        timestamp: new Date(Date.now() - (168 - i) * 60 * 60 * 1000).toISOString(),
        modelId: ["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet"][Math.floor(Math.random() * 3)],
        requests: Math.floor(Math.random() * 50) + 10,
        tokens: Math.floor(Math.random() * 10000) + 1000,
        cost: Math.random() * 0.5 + 0.01,
        responseTime: Math.random() * 3000 + 500,
        successRate: Math.random() * 0.1 + 0.9,
        errorRate: Math.random() * 0.1,
        userId: `user${Math.floor(Math.random() * 5) + 1}`,
        sessionId: `session${Math.floor(Math.random() * 1000)}`,
      }));
      
      const mockSummary: UsageSummary[] = models.map(model => ({
        modelId: model.id,
        modelName: model.displayName,
        totalRequests: Math.floor(Math.random() * 10000) + 1000,
        totalTokens: Math.floor(Math.random() * 1000000) + 100000,
        totalCost: Math.random() * 100 + 10,
        avgResponseTime: Math.random() * 2000 + 500,
        avgSuccessRate: Math.random() * 0.1 + 0.9,
        avgErrorRate: Math.random() * 0.1,
        peakUsage: {
          timestamp: new Date().toISOString(),
          requests: Math.floor(Math.random() * 100) + 50,
        },
        usageTrend: ["increasing", "decreasing", "stable"][Math.floor(Math.random() * 3)] as any,
        costTrend: ["increasing", "decreasing", "stable"][Math.floor(Math.random() * 3)] as any,
      }));
      
      const mockCostBreakdown: CostBreakdown[] = models.map(model => ({
        modelId: model.id,
        modelName: model.displayName,
        cost: Math.random() * 100 + 10,
        percentage: Math.random() * 40 + 10,
        requests: Math.floor(Math.random() * 10000) + 1000,
        avgCostPerRequest: Math.random() * 0.01 + 0.001,
      }));
      
      const mockUserUsage: UserUsage[] = Array.from({ length: 10 }, (_, i) => ({
        userId: `user${i + 1}`,
        username: `User ${i + 1}`,
        totalRequests: Math.floor(Math.random() * 5000) + 100,
        totalCost: Math.random() * 50 + 5,
        favoriteModel: models[Math.floor(Math.random() * models.length)]?.id || "",
        lastActivity: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
        usagePattern: ["heavy", "moderate", "light"][Math.floor(Math.random() * 3)] as any,
      }));
      
      setUsageData(mockUsageData);
      setUsageSummary(mockSummary);
      setCostBreakdown(mockCostBreakdown);
      setUserUsage(mockUserUsage);
    } catch (error) {
      message.error(t("analytics.load_failed"));
    } finally {
      setLoading(false);
    }
  };

  const getModelName = (modelId: string) => {
    return models.find(m => m.id === modelId)?.displayName || modelId;
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "increasing":
        return <TrendingUpOutlined style={{ color: colors.colorSuccess }} />;
      case "decreasing":
        return <TrendingDownOutlined style={{ color: colors.colorError }} />;
      default:
        return <TrendingUpOutlined style={{ color: colors.colorTextSecondary }} />;
    }
  };

  const getUsagePatternColor = (pattern: string) => {
    switch (pattern) {
      case "heavy":
        return colors.colorError;
      case "moderate":
        return colors.colorWarning;
      case "light":
        return colors.colorSuccess;
      default:
        return colors.colorTextSecondary;
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("de-DE", {
      style: "currency",
      currency: "EUR",
    }).format(amount);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat("de-DE").format(num);
  };

  const exportData = async (format: "csv" | "json" | "excel") => {
    try {
      // TODO: Implement export functionality
      message.success(t("analytics.export_success"));
    } catch (error) {
      message.error(t("analytics.export_failed"));
    }
  };

  const usageColumns = [
    {
      title: t("analytics.table.model"),
      dataIndex: "modelName",
      key: "modelName",
      render: (text: string, record: UsageSummary) => (
        <Space>
          <Text strong>{text}</Text>
          <Tag color="blue">{record.modelId}</Tag>
        </Space>
      ),
    },
    {
      title: t("analytics.table.requests"),
      dataIndex: "totalRequests",
      key: "totalRequests",
      render: (value: number) => formatNumber(value),
      sorter: (a: UsageSummary, b: UsageSummary) => a.totalRequests - b.totalRequests,
    },
    {
      title: t("analytics.table.tokens"),
      dataIndex: "totalTokens",
      key: "totalTokens",
      render: (value: number) => formatNumber(value),
      sorter: (a: UsageSummary, b: UsageSummary) => a.totalTokens - b.totalTokens,
    },
    {
      title: t("analytics.table.cost"),
      dataIndex: "totalCost",
      key: "totalCost",
      render: (value: number) => formatCurrency(value),
      sorter: (a: UsageSummary, b: UsageSummary) => a.totalCost - b.totalCost,
    },
    {
      title: t("analytics.table.response_time"),
      dataIndex: "avgResponseTime",
      key: "avgResponseTime",
      render: (value: number) => `${value.toFixed(0)}ms`,
      sorter: (a: UsageSummary, b: UsageSummary) => a.avgResponseTime - b.avgResponseTime,
    },
    {
      title: t("analytics.table.success_rate"),
      dataIndex: "avgSuccessRate",
      key: "avgSuccessRate",
      render: (value: number) => (
        <Progress 
          percent={value * 100} 
          size="small" 
          status={value > 0.95 ? "success" : value > 0.9 ? "normal" : "exception"}
        />
      ),
      sorter: (a: UsageSummary, b: UsageSummary) => a.avgSuccessRate - b.avgSuccessRate,
    },
    {
      title: t("analytics.table.trend"),
      key: "trend",
      render: (record: UsageSummary) => (
        <Space>
          {getTrendIcon(record.usageTrend)}
          <Text type="secondary">{t(`analytics.trend.${record.usageTrend}`)}</Text>
        </Space>
      ),
    },
  ];

  const costColumns = [
    {
      title: t("analytics.table.model"),
      dataIndex: "modelName",
      key: "modelName",
      render: (text: string, record: CostBreakdown) => (
        <Space>
          <Text strong>{text}</Text>
          <Tag color="blue">{record.modelId}</Tag>
        </Space>
      ),
    },
    {
      title: t("analytics.table.cost"),
      dataIndex: "cost",
      key: "cost",
      render: (value: number) => formatCurrency(value),
      sorter: (a: CostBreakdown, b: CostBreakdown) => a.cost - b.cost,
    },
    {
      title: t("analytics.table.percentage"),
      dataIndex: "percentage",
      key: "percentage",
      render: (value: number) => (
        <Progress percent={value} size="small" />
      ),
      sorter: (a: CostBreakdown, b: CostBreakdown) => a.percentage - b.percentage,
    },
    {
      title: t("analytics.table.requests"),
      dataIndex: "requests",
      key: "requests",
      render: (value: number) => formatNumber(value),
      sorter: (a: CostBreakdown, b: CostBreakdown) => a.requests - b.requests,
    },
    {
      title: t("analytics.table.avg_cost_per_request"),
      dataIndex: "avgCostPerRequest",
      key: "avgCostPerRequest",
      render: (value: number) => formatCurrency(value),
      sorter: (a: CostBreakdown, b: CostBreakdown) => a.avgCostPerRequest - b.avgCostPerRequest,
    },
  ];

  const userColumns = [
    {
      title: t("analytics.table.user"),
      dataIndex: "username",
      key: "username",
      render: (text: string, record: UserUsage) => (
        <Space>
          <UserOutlined />
          <Text strong>{text}</Text>
          <Tag color="blue">{record.userId}</Tag>
        </Space>
      ),
    },
    {
      title: t("analytics.table.requests"),
      dataIndex: "totalRequests",
      key: "totalRequests",
      render: (value: number) => formatNumber(value),
      sorter: (a: UserUsage, b: UserUsage) => a.totalRequests - b.totalRequests,
    },
    {
      title: t("analytics.table.cost"),
      dataIndex: "totalCost",
      key: "totalCost",
      render: (value: number) => formatCurrency(value),
      sorter: (a: UserUsage, b: UserUsage) => a.totalCost - b.totalCost,
    },
    {
      title: t("analytics.table.favorite_model"),
      dataIndex: "favoriteModel",
      key: "favoriteModel",
      render: (modelId: string) => getModelName(modelId),
    },
    {
      title: t("analytics.table.usage_pattern"),
      dataIndex: "usagePattern",
      key: "usagePattern",
      render: (pattern: string) => (
        <Tag color={getUsagePatternColor(pattern)}>
          {t(`analytics.pattern.${pattern}`)}
        </Tag>
      ),
    },
    {
      title: t("analytics.table.last_activity"),
      dataIndex: "lastActivity",
      key: "lastActivity",
      render: (timestamp: string) => new Date(timestamp).toLocaleDateString(),
      sorter: (a: UserUsage, b: UserUsage) => 
        new Date(a.lastActivity).getTime() - new Date(b.lastActivity).getTime(),
    },
  ];

  const totalRequests = usageSummary.reduce((sum, item) => sum + item.totalRequests, 0);
  const totalTokens = usageSummary.reduce((sum, item) => sum + item.totalTokens, 0);
  const totalCost = usageSummary.reduce((sum, item) => sum + item.totalCost, 0);
  const avgResponseTime = usageSummary.reduce((sum, item) => sum + item.avgResponseTime, 0) / usageSummary.length;

  const chartData = usageData
    .filter(data => selectedModels.length === 0 || selectedModels.includes(data.modelId))
    .reduce((acc, data) => {
      const date = new Date(data.timestamp).toLocaleDateString();
      const existing = acc.find(item => item.date === date);
      if (existing) {
        existing.requests += data.requests;
        existing.cost += data.cost;
        existing.tokens += data.tokens;
      } else {
        acc.push({
          date,
          requests: data.requests,
          cost: data.cost,
          tokens: data.tokens,
        });
      }
      return acc;
    }, [] as any[]);

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        <BarChartOutlined style={{ marginRight: 8 }} />
        {t("analytics.title")}
      </Title>

      {/* Controls */}
      <Card style={{ marginBottom: 16 }}>
        <Row gutter={16} align="middle">
          <Col span={6}>
            <RangePicker
              value={[new Date(timeRange[0]), new Date(timeRange[1])]}
              onChange={(dates) => {
                if (dates) {
                  setTimeRange([dates[0]!.toISOString(), dates[1]!.toISOString()]);
                }
              }}
              style={{ width: "100%" }}
            />
          </Col>
          <Col span={4}>
            <Select
              mode="multiple"
              placeholder={t("analytics.select_models")}
              value={selectedModels}
              onChange={setSelectedModels}
              style={{ width: "100%" }}
              allowClear
            >
              {models.map(model => (
                <Option key={model.id} value={model.id}>
                  {model.displayName}
                </Option>
              ))}
            </Select>
          </Col>
          <Col span={3}>
            <Select
              value={viewMode}
              onChange={setViewMode}
              style={{ width: "100%" }}
            >
              <Option value="overview">{t("analytics.view.overview")}</Option>
              <Option value="detailed">{t("analytics.view.detailed")}</Option>
              <Option value="costs">{t("analytics.view.costs")}</Option>
              <Option value="users">{t("analytics.view.users")}</Option>
            </Select>
          </Col>
          <Col span={3}>
            <Button
              icon={<ReloadOutlined />}
              onClick={loadUsageData}
              loading={loading}
            >
              {t("analytics.refresh")}
            </Button>
          </Col>
          <Col span={3}>
            <Button
              icon={<DownloadOutlined />}
              onClick={() => setExportModalVisible(true)}
            >
              {t("analytics.export")}
            </Button>
          </Col>
          <Col span={3}>
            <Button
              icon={<SettingOutlined />}
              onClick={() => setSettingsModalVisible(true)}
            >
              {t("analytics.settings")}
            </Button>
          </Col>
          <Col span={2}>
            <Switch
              checked={autoRefresh}
              onChange={setAutoRefresh}
              size="small"
            />
          </Col>
        </Row>
      </Card>

      {/* Overview Statistics */}
      {viewMode === "overview" && (
        <>
          <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title={t("analytics.stats.total_requests")}
                  value={totalRequests}
                  prefix={<FileTextOutlined />}
                  formatter={(value) => formatNumber(value as number)}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title={t("analytics.stats.total_tokens")}
                  value={totalTokens}
                  prefix={<ThunderboltOutlined />}
                  formatter={(value) => formatNumber(value as number)}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title={t("analytics.stats.total_cost")}
                  value={totalCost}
                  prefix={<DollarOutlined />}
                  formatter={(value) => formatCurrency(value as number)}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title={t("analytics.stats.avg_response_time")}
                  value={avgResponseTime}
                  prefix={<ClockCircleOutlined />}
                  suffix="ms"
                  formatter={(value) => (value as number).toFixed(0)}
                />
              </Card>
            </Col>
          </Row>

          {/* Charts */}
          <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
            <Col xs={24} lg={12}>
              <Card title={t("analytics.charts.requests_trend")}>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <RechartsTooltip />
                    <Line type="monotone" dataKey="requests" stroke={colors.colorPrimary} />
                  </LineChart>
                </ResponsiveContainer>
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card title={t("analytics.charts.cost_trend")}>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <RechartsTooltip />
                    <Area type="monotone" dataKey="cost" stroke={colors.colorSuccess} fill={colors.colorSuccess} fillOpacity={0.3} />
                  </AreaChart>
                </ResponsiveContainer>
              </Card>
            </Col>
          </Row>

          <Row gutter={[16, 16]}>
            <Col xs={24} lg={12}>
              <Card title={t("analytics.charts.model_distribution")}>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={costBreakdown}
                      dataKey="cost"
                      nameKey="modelName"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      label
                    >
                      {costBreakdown.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={[colors.colorPrimary, colors.colorSuccess, colors.colorWarning, colors.colorError][index % 4]} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card title={t("analytics.charts.performance_comparison")}>
                <ResponsiveContainer width="100%" height={300}>
                  <ComposedChart data={usageSummary}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="modelName" />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <RechartsTooltip />
                    <Legend />
                    <Bar yAxisId="left" dataKey="totalRequests" fill={colors.colorPrimary} />
                    <Line yAxisId="right" type="monotone" dataKey="avgResponseTime" stroke={colors.colorError} />
                  </ComposedChart>
                </ResponsiveContainer>
              </Card>
            </Col>
          </Row>
        </>
      )}

      {/* Detailed Usage Table */}
      {viewMode === "detailed" && (
        <Card title={t("analytics.detailed_usage")}>
          <Table
            columns={usageColumns}
            dataSource={usageSummary}
            rowKey="modelId"
            pagination={{ pageSize: 10 }}
            loading={loading}
          />
        </Card>
      )}

      {/* Cost Analysis */}
      {viewMode === "costs" && (
        <Card title={t("analytics.cost_analysis")}>
          <Table
            columns={costColumns}
            dataSource={costBreakdown}
            rowKey="modelId"
            pagination={{ pageSize: 10 }}
            loading={loading}
          />
        </Card>
      )}

      {/* User Usage */}
      {viewMode === "users" && (
        <Card title={t("analytics.user_usage")}>
          <Table
            columns={userColumns}
            dataSource={userUsage}
            rowKey="userId"
            pagination={{ pageSize: 10 }}
            loading={loading}
          />
        </Card>
      )}

      {/* Export Modal */}
      <Modal
        title={t("analytics.export_data")}
        open={exportModalVisible}
        onCancel={() => setExportModalVisible(false)}
        footer={null}
      >
        <Space direction="vertical" style={{ width: "100%" }}>
          <Button 
            block 
            icon={<DownloadOutlined />}
            onClick={() => exportData("csv")}
          >
            {t("analytics.export_csv")}
          </Button>
          <Button 
            block 
            icon={<DownloadOutlined />}
            onClick={() => exportData("json")}
          >
            {t("analytics.export_json")}
          </Button>
          <Button 
            block 
            icon={<DownloadOutlined />}
            onClick={() => exportData("excel")}
          >
            {t("analytics.export_excel")}
          </Button>
        </Space>
      </Modal>

      {/* Settings Modal */}
      <Modal
        title={t("analytics.settings")}
        open={settingsModalVisible}
        onCancel={() => setSettingsModalVisible(false)}
        footer={null}
      >
        <Form layout="vertical">
          <Form.Item label={t("analytics.settings.auto_refresh")}>
            <Switch
              checked={autoRefresh}
              onChange={setAutoRefresh}
            />
          </Form.Item>
          <Form.Item label={t("analytics.settings.refresh_interval")}>
            <Select
              value={refreshInterval}
              onChange={setRefreshInterval}
              disabled={!autoRefresh}
            >
              <Option value={10000}>10 {t("analytics.settings.seconds")}</Option>
              <Option value={30000}>30 {t("analytics.settings.seconds")}</Option>
              <Option value={60000}>1 {t("analytics.settings.minute")}</Option>
              <Option value={300000}>5 {t("analytics.settings.minutes")}</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ModelUsageAnalytics;