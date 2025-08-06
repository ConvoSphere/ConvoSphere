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
  DownloadOutlined,
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
    color: colors?.colorTextBase || "#ffffff",
    padding: "8px",
    // Verbesserte Menu-Styles für bessere Lesbarkeit
    "--ant-menu-item-color": colors?.colorTextBase || "#ffffff",
    "--ant-menu-item-selected-color": colors?.colorPrimary || "#1890ff",
    "--ant-menu-item-hover-color": colors?.colorPrimary || "#1890ff",
    "--ant-menu-item-active-color": colors?.colorPrimary || "#1890ff",
    "--ant-menu-item-selected-bg": colors?.colorBgElevated || "#f0f0f0",
    "--ant-menu-item-hover-bg": colors?.colorBgElevated || "#f0f0f0",
  } as React.CSSProperties;

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
      icon: <BarChartOutlined style={{ color: colors?.colorTextSecondary || "#cccccc" }} />,
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
      icon: <ToolOutlined style={{ color: colors?.colorTextSecondary || "#cccccc" }} />,
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
      key: "/export-backup",
      icon: <DownloadOutlined style={{ color: colors?.colorPrimary || "#1890ff" }} />,
      label: t("navigation.export_backup"),
    },
    {
      key: "/mcp-tools",
      icon: <ApiOutlined style={{ color: colors?.colorPrimary || "#1890ff" }} />,
      label: t("navigation.mcp_tools"),
    },
    {
      key: "/settings",
      icon: <SettingOutlined style={{ color: colors?.colorTextSecondary || "#cccccc" }} />,
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
            icon: <BarChartOutlined style={{ color: colors?.colorTextSecondary || "#cccccc" }} />,
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
              color: colors?.colorTextBase || "#ffffff",
            }}
          >
            {t("app.title", "ConvoSphere")}
          </div>
          <div
            style={{
              fontSize: "12px",
              color: colors?.colorTextSecondary || "#cccccc",
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
              backgroundColor: colors?.colorTextSecondary || "#cccccc",
              color: colors?.colorTextBase || "#ffffff",
            }}
          />
          <div style={{ flex: 1 }}>
            <div
              style={{
                fontSize: "14px",
                fontWeight: 500,
                color: colors?.colorTextBase || "#ffffff",
              }}
            >
              {user?.username || t("navigation.user")}
            </div>
            <div
              style={{
                fontSize: "12px",
                color: colors?.colorTextSecondary || "#cccccc",
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
