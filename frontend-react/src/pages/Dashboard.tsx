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
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/authStore";
import { useThemeStore } from "../store/themeStore";
import ModernCard from "../components/ModernCard";
import ModernButton from "../components/ModernButton";

const { Title, Text } = Typography;

interface DashboardStats {
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

const Dashboard: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();
  const isAdmin =
    user && (user.role === "admin" || user.role === "super_admin");

  const [stats, setStats] = useState<DashboardStats>({
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
    // Simulate loading dashboard data
    const loadDashboardData = async () => {
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
        console.error("Error loading dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
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

  const quickActions = [
    {
      title: t("dashboard.quick_actions.start_chat"),
      icon: <MessageOutlined />,
      action: () => navigate("/chat"),
      variant: "primary" as const,
    },
    {
      title: t("dashboard.quick_actions.upload_document"),
      icon: <FileTextOutlined />,
      action: () => navigate("/knowledge-base"),
      variant: "secondary" as const,
    },
    {
      title: t("dashboard.quick_actions.manage_assistants"),
      icon: <RobotOutlined />,
      action: () => navigate("/assistants"),
      variant: "accent" as const,
    },
    {
      title: t("dashboard.quick_actions.view_tools"),
      icon: <ToolOutlined />,
      action: () => navigate("/tools"),
      variant: "gradient" as const,
    },
  ];

  return (
    <div style={{ padding: "24px 0" }}>
      {/* Welcome Section */}
      <ModernCard variant="gradient" size="lg" className="stagger-children">
        <div style={{ textAlign: "center", padding: "32px 0" }}>
          <Title
            level={1}
            style={{ color: "#FFFFFF", marginBottom: 16, fontSize: "2.5rem" }}
          >
            {t("dashboard.welcome", {
              username: user?.username || t("common.user"),
            })}
          </Title>
          <Text style={{ fontSize: "18px", color: "rgba(255, 255, 255, 0.9)" }}>
            {t("dashboard.subtitle")}
          </Text>
        </div>
      </ModernCard>

      {/* Statistics Cards */}
      <div className="modern-card-grid" style={{ marginBottom: 32 }}>
        <ModernCard
          variant="elevated"
          size="md"
          loading={loading}
          className="stagger-children"
        >
          <Statistic
            title={t("dashboard.stats.conversations")}
            value={stats.totalConversations}
            prefix={<MessageOutlined style={{ color: colors.colorPrimary }} />}
            valueStyle={{ color: colors.colorPrimary, fontSize: "2rem" }}
          />
        </ModernCard>

        <ModernCard
          variant="elevated"
          size="md"
          loading={loading}
          className="stagger-children"
        >
          <Statistic
            title={t("dashboard.stats.messages")}
            value={stats.totalMessages}
            prefix={
              <MessageOutlined style={{ color: colors.colorSecondary }} />
            }
            valueStyle={{ color: colors.colorSecondary, fontSize: "2rem" }}
          />
        </ModernCard>

        <ModernCard
          variant="elevated"
          size="md"
          loading={loading}
          className="stagger-children"
        >
          <Statistic
            title={t("dashboard.stats.documents")}
            value={stats.totalDocuments}
            prefix={<BookOutlined style={{ color: colors.colorAccent }} />}
            valueStyle={{ color: colors.colorAccent, fontSize: "2rem" }}
          />
        </ModernCard>

        <ModernCard
          variant="elevated"
          size="md"
          loading={loading}
          className="stagger-children"
        >
          <Statistic
            title={t("dashboard.stats.assistants")}
            value={stats.totalAssistants}
            prefix={<TeamOutlined style={{ color: colors.colorPrimary }} />}
            valueStyle={{ color: colors.colorPrimary, fontSize: "2rem" }}
          />
        </ModernCard>
      </div>

      {/* System Health and Quick Actions */}
      <Row gutter={[24, 24]} style={{ marginBottom: 32 }}>
        <Col xs={24} lg={16}>
          <ModernCard
            variant="interactive"
            size="lg"
            header={
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Title level={4} style={{ margin: 0 }}>
                  {t("dashboard.system_health")}
                </Title>
                <Tag
                  color={getHealthColor(stats.systemHealth)}
                  style={{ fontSize: "12px", padding: "4px 8px" }}
                >
                  {t(`dashboard.health.${stats.systemHealth}`)}
                </Tag>
              </div>
            }
          >
            <Row gutter={24}>
              <Col span={12}>
                <Statistic
                  title={t("dashboard.stats.active_users")}
                  value={stats.activeUsers}
                  prefix={
                    <UserOutlined style={{ color: colors.colorPrimary }} />
                  }
                  valueStyle={{ color: colors.colorPrimary }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title={t("dashboard.stats.tools")}
                  value={stats.totalTools}
                  prefix={
                    <ToolOutlined style={{ color: colors.colorSecondary }} />
                  }
                  valueStyle={{ color: colors.colorSecondary }}
                />
              </Col>
            </Row>
            <Divider />
            <div>
              <Text strong style={{ fontSize: "16px" }}>
                {t("dashboard.performance")}
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
        </Col>

        <Col xs={24} lg={8}>
          <ModernCard
            variant="outlined"
            size="lg"
            header={
              <Title level={4} style={{ margin: 0 }}>
                {t("dashboard.quick_actions.title")}
              </Title>
            }
          >
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {quickActions.map((action, index) => (
                <ModernButton
                  key={index}
                  variant={action.variant}
                  size="md"
                  icon={action.icon}
                  onClick={action.action}
                  style={{
                    width: "100%",
                    justifyContent: "flex-start",
                    padding: "12px 16px",
                  }}
                >
                  {action.title}
                </ModernButton>
              ))}
            </div>
          </ModernCard>
        </Col>
      </Row>

      {/* Recent Activity */}
      <ModernCard
        variant="default"
        size="lg"
        header={
          <Title level={4} style={{ margin: 0 }}>
            {t("dashboard.recent_activity")}
          </Title>
        }
      >
        <List
          loading={loading}
          dataSource={stats.recentActivity}
          renderItem={(item) => (
            <List.Item
              style={{
                padding: "16px 0",
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
                      width: 40,
                      height: 40,
                    }}
                  />
                }
                title={
                  <Space>
                    <Text strong style={{ fontSize: "16px" }}>
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

      {/* Admin Section */}
      {isAdmin && (
        <ModernCard
          variant="elevated"
          size="lg"
          header={
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <Title level={4} style={{ margin: 0 }}>
                {t("dashboard.admin_section")}
              </Title>
              <ModernButton
                variant="primary"
                size="md"
                onClick={() => navigate("/admin")}
              >
                {t("dashboard.admin_dashboard")}
              </ModernButton>
            </div>
          }
          style={{ marginTop: 24 }}
        >
          <Row gutter={24}>
            <Col span={8}>
              <Statistic
                title={t("dashboard.admin.total_users")}
                value={156}
                prefix={<UserOutlined style={{ color: colors.colorPrimary }} />}
                valueStyle={{ color: colors.colorPrimary }}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title={t("dashboard.admin.system_load")}
                value={23}
                suffix="%"
                prefix={
                  <RiseOutlined style={{ color: colors.colorSecondary }} />
                }
                valueStyle={{ color: colors.colorSecondary }}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title={t("dashboard.admin.uptime")}
                value={99.9}
                suffix="%"
                precision={1}
                prefix={
                  <ClockCircleOutlined style={{ color: colors.colorAccent }} />
                }
                valueStyle={{ color: colors.colorAccent }}
              />
            </Col>
          </Row>
        </ModernCard>
      )}
    </div>
  );
};

export default Dashboard;
