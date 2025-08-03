import React from "react";
import { Menu, Avatar } from "antd";
import { useLocation, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  DashboardOutlined,
  MessageOutlined,
  TeamOutlined,
  BookOutlined,
  ToolOutlined,
  SettingOutlined,
  UserOutlined,
  AppstoreOutlined,
  ApiOutlined,
  BarChartOutlined,
  RobotOutlined,
} from "@ant-design/icons";
import { useAuthStore } from "../store/authStore";
import { useThemeStore } from "../store/themeStore";

const Sidebar: React.FC = () => {
  const { t } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();
  const isAdmin =
    user && (user.role === "admin" || user.role === "super_admin");

  const menuStyle: React.CSSProperties = {
    height: "100%",
    borderRight: 0,
    backgroundColor: colors?.colorBgContainer || "#ffffff",
    color: colors?.colorTextBase || "#000000",
    padding: "8px",
  };

  const logoStyle: React.CSSProperties = {
    display: "flex",
    alignItems: "center",
    gap: "12px",
    padding: "20px 16px",
    borderBottom: `1px solid ${colors?.colorBorder || "#d9d9d9"}`,
    backgroundColor: colors?.colorBgElevated || "#fafafa",
  };

  const userSectionStyle: React.CSSProperties = {
    padding: "16px",
    borderTop: `1px solid ${colors?.colorBorder || "#d9d9d9"}`,
    backgroundColor: colors?.colorBgElevated || "#fafafa",
  };

  const items = [
    {
      key: "/",
      icon: <MessageOutlined style={{ color: colors?.colorPrimary || "#1890ff" }} />,
      label: t("navigation.home"),
    },
    {
      key: "/dashboard",
      icon: <DashboardOutlined style={{ color: colors?.colorPrimary || "#1890ff" }} />,
      label: t("navigation.dashboard"),
    },
    {
      key: "/overview",
      icon: <BarChartOutlined style={{ color: colors?.colorTextSecondary || "#8c8c8c" }} />,
      label: t("navigation.overview"),
    },
    {
      key: "/chat",
      icon: <MessageOutlined style={{ color: colors?.colorPrimary || "#1890ff" }} />,
      label: t("chat.title"),
    },
    {
      key: "/assistants",
      icon: <TeamOutlined style={{ color: colors?.colorPrimary || "#1890ff" }} />,
      label: t("navigation.assistants"),
    },
    {
      key: "/knowledge-base",
      icon: <BookOutlined style={{ color: colors?.colorPrimary || "#1890ff" }} />,
      label: t("knowledge.title"),
    },
    {
      key: "/tools",
      icon: <ToolOutlined style={{ color: colors?.colorTextSecondary || "#8c8c8c" }} />,
      label: t("tools.title"),
    },
    {
      key: "/conversations",
      icon: <AppstoreOutlined style={{ color: colors?.colorPrimary || "#1890ff" }} />,
      label: t("navigation.conversations"),
    },
    {
      key: "/conversation-intelligence",
      icon: <BarChartOutlined style={{ color: colors?.colorPrimary || "#1890ff" }} />,
      label: t("navigation.conversation_intelligence"),
    },
    {
      key: "/domain-groups",
      icon: <TeamOutlined style={{ color: colors?.colorPrimary || "#1890ff" }} />,
      label: t("navigation.domain_groups"),
    },
    {
      key: "/mcp-tools",
      icon: <ApiOutlined style={{ color: colors?.colorPrimary || "#1890ff" }} />,
      label: t("navigation.mcp_tools"),
    },
    {
      key: "/settings",
      icon: <SettingOutlined style={{ color: colors?.colorTextSecondary || "#8c8c8c" }} />,
      label: t("settings.title"),
    },
    {
      key: "/profile",
      icon: <UserOutlined style={{ color: colors?.colorPrimary || "#1890ff" }} />,
      label: t("profile.title"),
    },
    ...(isAdmin
      ? [
          {
            key: "/admin",
            icon: <TeamOutlined style={{ color: colors?.colorPrimary || "#1890ff" }} />,
            label: t("admin.title"),
          },
          {
            key: "/admin/system-status",
            icon: <BarChartOutlined style={{ color: colors?.colorTextSecondary || "#8c8c8c" }} />,
            label: t("admin.system_status"),
          },
        ]
      : []),
  ];

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      {/* Logo Section */}
      <div style={logoStyle}>
        <Avatar
          icon={<RobotOutlined />}
          size="large"
          style={{
            backgroundColor: colors?.colorPrimary || "#1890ff",
            color: colors?.colorTextBase || "#ffffff",
          }}
        />
        <div style={{ flex: 1 }}>
          <div
            style={{
              fontWeight: 600,
              fontSize: "16px",
              color: colors?.colorTextBase || "#000000",
            }}
          >
            {t("app.title", "ConvoSphere")}
          </div>
          <div
            style={{
              fontSize: "12px",
              color: colors?.colorTextSecondary || "#666666",
            }}
          >
            {t("app.subtitle", "AI Assistant Platform")}
          </div>
        </div>
      </div>

      {/* Navigation Menu */}
      <div style={{ flex: 1, overflow: "auto" }}>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          style={menuStyle}
          items={items}
          onClick={({ key }) => navigate(key)}
          theme="light"
        />
      </div>

      {/* User Section */}
      <div style={userSectionStyle}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "12px",
            marginBottom: "8px",
          }}
        >
          <Avatar
            icon={<UserOutlined />}
            size="small"
            style={{
              backgroundColor: colors?.colorTextSecondary || "#8c8c8c",
              color: colors?.colorTextBase || "#ffffff",
            }}
          />
          <div style={{ flex: 1 }}>
            <div
              style={{
                fontSize: "14px",
                fontWeight: 500,
                color: colors?.colorTextBase || "#000000",
              }}
            >
              {user?.username || t("navigation.user")}
            </div>
            <div
              style={{
                fontSize: "12px",
                color: colors?.colorTextSecondary || "#666666",
              }}
            >
              {user?.email || "user@example.com"}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
