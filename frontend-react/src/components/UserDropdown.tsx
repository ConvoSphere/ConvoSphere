import React from "react";
import { Dropdown, Avatar, Typography, Space, Divider } from "antd";
import ModernButton from "./ModernButton";
import { UserOutlined, SettingOutlined, LogoutOutlined, DashboardOutlined, TeamOutlined, ProfileOutlined } from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/authStore";
import { useThemeStore } from "../store/themeStore";
import LogoutButton from "./LogoutButton";

const { Text } = Typography;

const UserDropdown: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();
  
  const isAdmin = user && (user.role === "admin" || user.role === "super_admin");

  const userMenuItems = [
    {
      key: "profile",
      label: (
        <div style={{ padding: "8px 16px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <Avatar
              icon={<UserOutlined />}
              size="small"
              style={{
                backgroundColor: colors?.colorPrimary || "#1890ff",
                color: colors?.colorTextBase || "#ffffff",
              }}
            />
            <div style={{ flex: 1 }}>
              <Text strong style={{ fontSize: "14px", color: colors?.colorTextBase || "#000000", display: "block" }}>
                {user?.username || t("navigation.user")}
              </Text>
              <Text style={{ fontSize: "12px", color: colors?.colorTextSecondary || "#666666" }}>
                {user?.email || "user@example.com"}
              </Text>
            </div>
          </div>
        </div>
      ),
    },
    {
      type: "divider" as const,
    },
    {
      key: "profile-settings",
      icon: <ProfileOutlined />,
      label: t("profile.title", "Profile"),
      onClick: () => navigate("/profile"),
    },
    {
      key: "settings",
      icon: <SettingOutlined />,
      label: t("settings.title", "Settings"),
      onClick: () => navigate("/settings"),
    },
    ...(isAdmin ? [
      {
        type: "divider" as const,
      },
      {
        key: "admin",
        icon: <TeamOutlined />,
        label: t("admin.title", "Admin Panel"),
        onClick: () => navigate("/admin"),
      },
      {
        key: "system-status",
        icon: <DashboardOutlined />,
        label: t("admin.system_status", "System Status"),
        onClick: () => navigate("/admin/system-status"),
      },
    ] : []),
    {
      type: "divider" as const,
    },
    {
      key: "logout",
      icon: <LogoutOutlined />,
      label: t("auth.logout", "Logout"),
      danger: true,
      onClick: () => {
        // The LogoutButton component will handle the actual logout
        const logoutButton = document.querySelector('[data-testid="logout-button"]') as HTMLElement;
        if (logoutButton) {
          logoutButton.click();
        }
      },
    },
  ];

  return (
    <Dropdown
      menu={{ items: userMenuItems }}
      placement="bottomRight"
      trigger={["click"]}
      overlayStyle={{
        minWidth: 200,
        backgroundColor: colors?.colorBgContainer || "#ffffff",
        border: `1px solid ${colors?.colorBorder || "#d9d9d9"}`,
        borderRadius: "8px",
        boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "12px",
          padding: "8px 16px",
          backgroundColor: colors?.colorBgElevated || "#fafafa",
          borderRadius: "12px",
          border: `1px solid ${colors?.colorBorder || "#d9d9d9"}`,
          transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
          cursor: "pointer",
        }}
        className="user-dropdown-trigger"
      >
        <Avatar
          icon={<UserOutlined />}
          size="small"
          style={{
            backgroundColor: colors?.colorPrimary || "#1890ff",
            color: colors?.colorTextBase || "#ffffff",
          }}
        />
        <div>
          <Text
            style={{
              fontSize: "14px",
              fontWeight: 500,
              color: colors?.colorTextBase || "#000000",
              display: "block",
            }}
          >
            {user?.username || t("navigation.user")}
          </Text>
          <Text
            style={{
              fontSize: "12px",
              color: colors?.colorTextSecondary || "#666666",
            }}
          >
            {user?.role || t("navigation.user")}
          </Text>
        </div>
      </div>
    </Dropdown>
  );
};

export default UserDropdown; 