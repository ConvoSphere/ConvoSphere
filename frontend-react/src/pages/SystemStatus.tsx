import React, { useEffect, useState, useRef } from "react";
import {
  Row,
  Col,
  Tag,
  Spin,
  Alert,
  Typography,
  Space,
} from "antd";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "../store/authStore";
import { useThemeStore } from "../store/themeStore";
import api from "../services/api";

import ModernCard from "../components/ModernCard";
import ModernButton from "../components/ModernButton";
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
} from "@ant-design/icons";

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
  const [data, setData] = useState<StatusData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const cpuHistory = useRef<{ time: string; cpu: number }[]>([]);
  const ramHistory = useRef<{ time: string; ram: number }[]>([]);

  const fetchStatus = async () => {
    try {
      const res = await api.get("/users/admin/system-status");
      setData(res.data);
      const now = new Date().toLocaleTimeString();
      // CPU
      cpuHistory.current.push({ time: now, cpu: res.data.system.cpu_percent });
      if (cpuHistory.current.length > MAX_POINTS) cpuHistory.current.shift();
      // RAM
      ramHistory.current.push({ time: now, ram: res.data.system.ram.percent });
      if (ramHistory.current.length > MAX_POINTS) ramHistory.current.shift();
      setLastUpdate(new Date());
      setError(null);
    } catch {
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
  }, [isAdmin]);

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
      </div>
    </div>
  );
};

export default SystemStatus;
