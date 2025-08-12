import React from "react";
import { Row, Col, Typography, Space, Tag } from "antd";
import {
  LineChartOutlined,
  HddOutlined,
  DatabaseOutlined,
  CloudOutlined,
  BugOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  SafetyOutlined,
  ReloadOutlined,
  ClockCircleOutlined,
  CloudServerOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import ModernCard from "../../components/ModernCard";
import ModernButton from "../../components/ModernButton";
import { useThemeStore } from "../../store/themeStore";

const { Title, Text } = Typography;

interface SystemData {
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

interface SystemOverviewProps {
  data: SystemData | null;
  cpuHistory: { time: string; cpu: number }[];
  ramHistory: { time: string; ram: number }[];
  lastUpdate: Date;
  onRefresh: () => void;
  loading: boolean;
}

const SystemOverview: React.FC<SystemOverviewProps> = ({
  data,
  cpuHistory,
  ramHistory,
  lastUpdate,
  onRefresh,
  loading,
}) => {
  const { t } = useTranslation();
  const { colors } = useThemeStore();

  if (!data) return null;

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

  return (
    <div>
      {/* Header Card */}
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
          {/* Real-time Metrics */}
          <ModernCard variant="elevated" size="lg" style={{ marginBottom: 24 }}>
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
                  onClick={onRefresh}
                  loading={loading}
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
                      data={cpuHistory}
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
                      data={ramHistory}
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

          {/* Service Status */}
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
          {/* Overall Status */}
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

          {/* Quick Stats */}
          <ModernCard variant="outlined" size="md" style={{ marginBottom: 24 }}>
            <Title level={4}>{t("system.quick_stats")}</Title>
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
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

          {/* Trace Info */}
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
    </div>
  );
};

export default SystemOverview;
