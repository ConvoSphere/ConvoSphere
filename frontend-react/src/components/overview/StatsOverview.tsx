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
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useThemeStore } from "../../store/themeStore";
import ModernCard from "../ModernCard";

const { Title, Text } = Typography;

interface OverviewStats {
  totalConversations: number;
  totalMessages: number;
  totalDocuments: number;
  totalAssistants: number;
  totalTools: number;
  activeUsers: number;
  systemHealth: "healthy" | "warning" | "error";
  recentActivity: Array<{
    id: string;
    type: "conversation" | "document" | "assistant" | "tool";
    title: string;
    timestamp: string;
    user: string;
  }>;
}

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
  const colors = getCurrentColors();

  const [stats, setStats] = useState<OverviewStats>({
    totalConversations: 0,
    totalMessages: 0,
    totalDocuments: 0,
    totalAssistants: 0,
    totalTools: 0,
    activeUsers: 0,
    systemHealth: "healthy",
    recentActivity: [],
  });

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading overview data
    const loadOverviewData = async () => {
      setLoading(true);
      try {
        // TODO: Replace with actual API calls
        await new Promise((resolve) => setTimeout(resolve, 1000));

        setStats({
          totalConversations: 156,
          totalMessages: 2847,
          totalDocuments: 89,
          totalAssistants: 12,
          totalTools: 8,
          activeUsers: 23,
          systemHealth: "healthy",
          recentActivity: [
            {
              id: "1",
              type: "conversation",
              title: "Neue Konversation gestartet",
              timestamp: "2024-01-15T10:30:00Z",
              user: "Max Mustermann",
            },
            {
              id: "2",
              type: "document",
              title: "Dokument hochgeladen: Projektplan.pdf",
              timestamp: "2024-01-15T09:15:00Z",
              user: "Anna Schmidt",
            },
            {
              id: "3",
              type: "assistant",
              title: 'Assistent "Support Bot" erstellt',
              timestamp: "2024-01-15T08:45:00Z",
              user: "Admin",
            },
            {
              id: "4",
              type: "tool",
              title: 'Tool "API Connector" aktiviert',
              timestamp: "2024-01-15T08:30:00Z",
              user: "Admin",
            },
          ],
        });
      } catch (error) {
        console.error("Error loading overview data:", error);
      } finally {
        setLoading(false);
      }
    };

    loadOverviewData();
  }, []);

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
    const statsData = [
      {
        title: t("overview.stats.conversations"),
        value: stats.totalConversations,
        icon: <MessageOutlined style={{ color: colors.colorPrimary }} />,
        color: colors.colorPrimary,
      },
      {
        title: t("overview.stats.messages"),
        value: stats.totalMessages,
        icon: <MessageOutlined style={{ color: colors.colorSecondary }} />,
        color: colors.colorSecondary,
      },
      {
        title: t("overview.stats.documents"),
        value: stats.totalDocuments,
        icon: <BookOutlined style={{ color: colors.colorAccent }} />,
        color: colors.colorAccent,
      },
      {
        title: t("overview.stats.assistants"),
        value: stats.totalAssistants,
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
    if (!showHealth || variant === "minimal") return null;

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
            <Tag
              color={getHealthColor(stats.systemHealth)}
              style={{ fontSize: "12px", padding: "4px 8px" }}
            >
              {t(`overview.health.${stats.systemHealth}`)}
            </Tag>
          </div>
        }
      >
        <Row gutter={24}>
          <Col span={12}>
            <Statistic
              title={t("overview.stats.active_users")}
              value={stats.activeUsers}
              prefix={<UserOutlined style={{ color: colors.colorPrimary }} />}
              valueStyle={{ color: colors.colorPrimary }}
            />
          </Col>
          <Col span={12}>
            <Statistic
              title={t("overview.stats.tools")}
              value={stats.totalTools}
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
          <Progress
            percent={85}
            status="active"
            strokeColor={colors.colorPrimary}
            style={{ marginTop: 12 }}
            strokeWidth={8}
          />
        </div>
      </ModernCard>
    );
  };

  const renderActivitySection = () => {
    if (!showActivity || variant === "minimal") return null;

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
          renderItem={(item) => (
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
                  <Space style={{ marginTop: 8 }}>
                    <ClockCircleOutlined
                      style={{ color: colors.colorTextSecondary }}
                    />
                    <Text type="secondary">
                      {new Date(item.timestamp).toLocaleString()}
                    </Text>
                  </Space>
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