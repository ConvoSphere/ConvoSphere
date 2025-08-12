import React from "react";
import { Row, Col, Statistic, Typography } from "antd";
import {
  UserOutlined,
  ClockCircleOutlined,
  RiseOutlined,
  BarChartOutlined,
  MessageOutlined,
  FileTextOutlined,
  RobotOutlined,
  ToolOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/authStore";
import { useThemeStore } from "../store/themeStore";
import ModernCard from "../components/ModernCard";
import ModernButton from "../components/ModernButton";
import StatsOverview from "../components/overview/StatsOverview";

const { Title, Text } = Typography;

const Overview: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();
  const isAdmin =
    user && (user.role === "admin" || user.role === "super_admin");

  const quickActions = [
    {
      title: t("overview.quick_actions.start_chat"),
      icon: <MessageOutlined />,
      action: () => navigate("/"),
      variant: "primary" as const,
    },
    {
      title: t("overview.quick_actions.upload_document"),
      icon: <FileTextOutlined />,
      action: () => navigate("/knowledge-base"),
      variant: "secondary" as const,
    },
    {
      title: t("overview.quick_actions.manage_assistants"),
      icon: <RobotOutlined />,
      action: () => navigate("/assistants"),
      variant: "accent" as const,
    },
    {
      title: t("overview.quick_actions.view_tools"),
      icon: <ToolOutlined />,
      action: () => navigate("/tools"),
      variant: "gradient" as const,
    },
  ];

  return (
    <div style={{ padding: "24px 0" }}>
      {/* Header Section */}
      <ModernCard variant="gradient" size="lg" className="stagger-children">
        <div style={{ textAlign: "center", padding: "32px 0" }}>
          <Title
            level={1}
            style={{ color: "#FFFFFF", marginBottom: 16, fontSize: "2.5rem" }}
          >
            <BarChartOutlined style={{ marginRight: 16 }} />
            {t("overview.title")}
          </Title>
          <Text style={{ fontSize: "18px", color: "rgba(255, 255, 255, 0.9)" }}>
            {t("overview.subtitle")}
          </Text>
        </div>
      </ModernCard>

      {/* Statistics Overview */}
      <StatsOverview variant="full" />

      {/* Quick Actions */}
      <ModernCard
        variant="outlined"
        size="lg"
        header={
          <Title level={4} style={{ margin: 0 }}>
            {t("overview.quick_actions.title")}
          </Title>
        }
        style={{ marginBottom: 32 }}
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
                {t("overview.admin_section")}
              </Title>
              <ModernButton
                variant="primary"
                size="md"
                onClick={() => navigate("/admin")}
              >
                {t("overview.admin_dashboard")}
              </ModernButton>
            </div>
          }
          style={{ marginTop: 24 }}
        >
          <Row gutter={24}>
            <Col span={8}>
              <Statistic
                title={t("overview.admin.total_users")}
                value={156}
                prefix={<UserOutlined style={{ color: colors.colorPrimary }} />}
                valueStyle={{ color: colors.colorPrimary }}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title={t("overview.admin.system_load")}
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
                title={t("overview.admin.uptime")}
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

export default Overview;
