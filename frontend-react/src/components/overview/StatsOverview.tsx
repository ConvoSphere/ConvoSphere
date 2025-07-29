// @ts-nocheck
import React, { useState, useEffect } from "react";
import {
  Row,
  Col,
  Statistic,
  List,
  Avatar,
  Progress,
  Tag,
  Space,
  Typography,
  Divider,
  Alert,
  Tooltip,
} from "antd";
import {
  MessageOutlined,
  BookOutlined,
  TeamOutlined,
  ToolOutlined,
  UserOutlined,
  FileTextOutlined,
  ClockCircleOutlined,
  RiseOutlined,
  RobotOutlined,
  ApiOutlined,
  ReloadOutlined,
  WifiOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useThemeStore } from "../../store/themeStore";
import { useAuthStore } from "../../store/authStore";
import ModernCard from "../ModernCard";
import ModernButton from "../ModernButton";
import { statisticsService, type OverviewStats, type ActivityItem } from "../../services/statistics";
import { realtimeService, type StatsUpdate, type SystemHealthUpdate, type ActivityUpdate } from "../../services/realtime";

const { Title, Text } = Typography;

interface StatsOverviewProps {
  variant?: "full" | "compact" | "minimal";
  showActivity?: boolean;
  showHealth?: boolean;
  className?: string;
}

const StatsOverview: React.FC<StatsOverviewProps> = ({
  variant = "full",
  showActivity = true,
  showHealth = true,
  className,
}) => {
  const { t } = useTranslation();
  const { getCurrentColors } = useThemeStore();
  const { token } = useAuthStore();
  const colors = getCurrentColors();

  const [stats, setStats] = useState<OverviewStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [realtimeConnected, setRealtimeConnected] = useState(false);

  useEffect(() => {
    loadOverviewData();
    setupRealtimeUpdates();
  }, [token]);

  const setupRealtimeUpdates = () => {
    if (!token) return;

    // Connect to realtime service
    realtimeService.connect(token)
      .then(() => {
        setRealtimeConnected(true);
        console.log("Realtime updates connected");
      })
      .catch((error) => {
        console.error("Failed to connect to realtime service:", error);
        setRealtimeConnected(false);
      });

    // Subscribe to realtime updates
    const unsubscribeStats = realtimeService.onStatsUpdate((statsUpdate: StatsUpdate) => {
      setStats(prevStats => {
        if (!prevStats) return prevStats;
        return {
          ...prevStats,
          systemStats: {
            ...prevStats.systemStats,
            ...statsUpdate,
          }
        };
      });
    });

    const unsubscribeHealth = realtimeService.onSystemHealth((healthUpdate: SystemHealthUpdate) => {
      setStats(prevStats => {
        if (!prevStats) return prevStats;
        return {
          ...prevStats,
          systemStats: {
            ...prevStats.systemStats,
            systemHealth: healthUpdate.status,
            performance: healthUpdate.performance,
          }
        };
      });
    });

    const unsubscribeActivity = realtimeService.onActivity((activityUpdate: ActivityUpdate) => {
      setStats(prevStats => {
        if (!prevStats) return prevStats;
        return {
          ...prevStats,
          recentActivity: [activityUpdate, ...prevStats.recentActivity.slice(0, 9)], // Keep max 10 activities
        };
      });
    });

    // Cleanup function
    return () => {
      unsubscribeStats();
      unsubscribeHealth();
      unsubscribeActivity();
      realtimeService.disconnect();
    };
  };

  const loadOverviewData = async (isRefresh = false) => {
    if (!token) return;

    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);

      const data = await statisticsService.getOverviewStats(token);
      setStats(data);
    } catch (error) {
      console.error("Error loading overview data:", error);
      setError(t("overview.error_loading_stats"));
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    loadOverviewData(true);
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case "conversation":
        return <MessageOutlined />;
      case "document":
        return <FileTextOutlined />;
      case "assistant":
        return <RobotOutlined />;
      case "tool":
        return <ToolOutlined />;
      default:
        return <ApiOutlined />;
    }
  };

  const getHealthColor = (health: string) => {
    switch (health) {
      case "healthy":
        return "success";
      case "warning":
        return "warning";
      case "error":
        return "error";
      default:
        return "default";
    }
  };

  const renderStatsCards = () => {
    if (!stats) return null;

    const statsData = [
      {
        title: t("overview.stats.conversations"),
        value: stats.systemStats.totalConversations,
        icon: <MessageOutlined style={{ color: colors.colorPrimary }} />,
        color: colors.colorPrimary,
      },
      {
        title: t("overview.stats.messages"),
        value: stats.systemStats.totalMessages,
        icon: <MessageOutlined style={{ color: colors.colorSecondary }} />,
        color: colors.colorSecondary,
      },
      {
        title: t("overview.stats.documents"),
        value: stats.systemStats.totalDocuments,
        icon: <BookOutlined style={{ color: colors.colorAccent }} />,
        color: colors.colorAccent,
      },
      {
        title: t("overview.stats.assistants"),
        value: stats.systemStats.totalAssistants,
        icon: <TeamOutlined style={{ color: colors.colorPrimary }} />,
        color: colors.colorPrimary,
      },
    ];

    if (variant === "minimal") {
      return (
        <Row gutter={[16, 16]}>
          {statsData.slice(0, 2).map((stat, index) => (
            <Col span={12} key={index}>
              <ModernCard
                variant="elevated"
                size="sm"
                loading={loading}
                className="stagger-children"
              >
                <Statistic
                  title={stat.title}
                  value={stat.value}
                  prefix={stat.icon}
                  valueStyle={{ color: stat.color, fontSize: "1.5rem" }}
                />
              </ModernCard>
            </Col>
          ))}
        </Row>
      );
    }

    if (variant === "compact") {
      return (
        <div className="modern-card-grid" style={{ marginBottom: 24 }}>
          {statsData.map((stat, index) => (
            <ModernCard
              key={index}
              variant="elevated"
              size="md"
              loading={loading}
              className="stagger-children"
            >
              <Statistic
                title={stat.title}
                value={stat.value}
                prefix={stat.icon}
                valueStyle={{ color: stat.color, fontSize: "1.8rem" }}
              />
            </ModernCard>
          ))}
        </div>
      );
    }

    // Full variant
    return (
      <div className="modern-card-grid" style={{ marginBottom: 32 }}>
        {statsData.map((stat, index) => (
          <ModernCard
            key={index}
            variant="elevated"
            size="md"
            loading={loading}
            className="stagger-children"
          >
            <Statistic
              title={stat.title}
              value={stat.value}
              prefix={stat.icon}
              valueStyle={{ color: stat.color, fontSize: "2rem" }}
            />
          </ModernCard>
        ))}
      </div>
    );
  };

  const renderHealthSection = () => {
    if (!showHealth || variant === "minimal" || !stats) return null;

    return (
      <ModernCard
        variant="interactive"
        size={variant === "compact" ? "md" : "lg"}
        header={
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <Title level={variant === "compact" ? 5 : 4} style={{ margin: 0 }}>
              {t("overview.system_health")}
            </Title>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <Tag
                color={getHealthColor(stats.systemStats.systemHealth)}
                style={{ fontSize: "12px", padding: "4px 8px" }}
              >
                {t(`overview.health.${stats.systemStats.systemHealth}`)}
              </Tag>
              <Tooltip title={realtimeConnected ? t("overview.realtime_connected") : t("overview.realtime_disconnected")}>
                <WifiOutlined 
                  style={{ 
                    color: realtimeConnected ? colors.colorSuccess : colors.colorTextSecondary,
                    fontSize: "14px"
                  }} 
                />
              </Tooltip>
              <ModernButton
                type="text"
                size="small"
                icon={<ReloadOutlined spin={refreshing} />}
                onClick={handleRefresh}
                disabled={refreshing}
              />
            </div>
          </div>
        }
      >
        <Row gutter={24}>
          <Col span={12}>
            <Statistic
              title={t("overview.stats.active_users")}
              value={stats.systemStats.activeUsers}
              prefix={<UserOutlined style={{ color: colors.colorPrimary }} />}
              valueStyle={{ color: colors.colorPrimary }}
            />
          </Col>
          <Col span={12}>
            <Statistic
              title={t("overview.stats.tools")}
              value={stats.systemStats.totalTools}
              prefix={<ToolOutlined style={{ color: colors.colorSecondary }} />}
              valueStyle={{ color: colors.colorSecondary }}
            />
          </Col>
        </Row>
        <Divider />
        <div>
          <Text strong style={{ fontSize: "16px" }}>
            {t("overview.performance")}
          </Text>
          <Row gutter={16} style={{ marginTop: 12 }}>
            <Col span={12}>
              <Progress
                percent={stats.systemStats.performance.cpuUsage}
                status="active"
                strokeColor={colors.colorPrimary}
                strokeWidth={8}
                format={(percent) => `CPU: ${percent}%`}
              />
            </Col>
            <Col span={12}>
              <Progress
                percent={stats.systemStats.performance.memoryUsage}
                status="active"
                strokeColor={colors.colorSecondary}
                strokeWidth={8}
                format={(percent) => `RAM: ${percent}%`}
              />
            </Col>
          </Row>
          <Row gutter={16} style={{ marginTop: 12 }}>
            <Col span={12}>
              <Statistic
                title={t("overview.response_time")}
                value={stats.systemStats.performance.responseTime}
                suffix="ms"
                valueStyle={{ fontSize: "14px" }}
              />
            </Col>
            <Col span={12}>
              <Statistic
                title={t("overview.uptime")}
                value={stats.systemStats.performance.uptime}
                suffix="%"
                precision={1}
                valueStyle={{ fontSize: "14px" }}
              />
            </Col>
          </Row>
        </div>
      </ModernCard>
    );
  };

  const renderActivitySection = () => {
    if (!showActivity || variant === "minimal" || !stats) return null;

    return (
      <ModernCard
        variant="default"
        size={variant === "compact" ? "md" : "lg"}
        header={
          <Title level={variant === "compact" ? 5 : 4} style={{ margin: 0 }}>
            {t("overview.recent_activity")}
          </Title>
        }
      >
        <List
          loading={loading}
          dataSource={stats.recentActivity.slice(0, variant === "compact" ? 3 : 5)}
          renderItem={(item: ActivityItem) => (
            <List.Item
              style={{
                padding: "12px 0",
                borderBottom: "1px solid var(--colorBorder)",
              }}
            >
              <List.Item.Meta
                avatar={
                  <Avatar
                    icon={getActivityIcon(item.type)}
                    style={{
                      backgroundColor: colors.colorPrimary,
                      color: "#FFFFFF",
                      width: variant === "compact" ? 32 : 40,
                      height: variant === "compact" ? 32 : 40,
                    }}
                  />
                }
                title={
                  <Space>
                    <Text strong style={{ fontSize: variant === "compact" ? "14px" : "16px" }}>
                      {item.title}
                    </Text>
                    <Tag color="blue" style={{ fontSize: "12px" }}>
                      {item.user}
                    </Tag>
                  </Space>
                }
                description={
                  <div>
                    {item.description && (
                      <Text type="secondary" style={{ display: "block", marginBottom: 4 }}>
                        {item.description}
                      </Text>
                    )}
                    <Space>
                      <ClockCircleOutlined
                        style={{ color: colors.colorTextSecondary }}
                      />
                      <Text type="secondary">
                        {new Date(item.timestamp).toLocaleString()}
                      </Text>
                    </Space>
                  </div>
                }
              />
            </List.Item>
          )}
        />
      </ModernCard>
    );
  };

  return (
    <div className={className}>
      {error && (
        <Alert
          message={error}
          type="error"
          showIcon
          closable
          onClose={() => setError(null)}
          style={{ marginBottom: 16 }}
          action={
            <ModernButton size="small" onClick={handleRefresh}>
              {t("common.retry")}
            </ModernButton>
          }
        />
      )}
      
      {renderStatsCards()}
      
      {variant === "full" && (
        <Row gutter={[24, 24]} style={{ marginBottom: 32 }}>
          <Col xs={24} lg={16}>
            {renderHealthSection()}
          </Col>
          <Col xs={24} lg={8}>
            {renderActivitySection()}
          </Col>
        </Row>
      )}

      {variant === "compact" && (
        <Row gutter={[16, 16]}>
          <Col span={12}>
            {renderHealthSection()}
          </Col>
          <Col span={12}>
            {renderActivitySection()}
          </Col>
        </Row>
      )}

      {variant === "minimal" && (
        <Row gutter={[16, 16]}>
          <Col span={12}>
            {renderHealthSection()}
          </Col>
        </Row>
      )}
    </div>
  );
};

export default StatsOverview;