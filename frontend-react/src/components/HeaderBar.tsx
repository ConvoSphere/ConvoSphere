import React from "react";
import { Typography } from "antd";
import { useTranslation } from "react-i18next";
import ThemeSwitcher from "./ThemeSwitcher";
import NotificationDropdown from "./NotificationDropdown";
import UserDropdown from "./UserDropdown";
import { useThemeStore } from "../store/themeStore";

const { Text } = Typography;

const HeaderBar: React.FC = () => {
  const { t } = useTranslation();
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const headerStyle: React.CSSProperties = {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    height: "64px",
    padding: "0 24px",
    backgroundColor: colors?.colorBgContainer || "#ffffff",
    borderBottom: `1px solid ${colors?.colorBorder || "#d9d9d9"}`,
    boxShadow: colors?.boxShadow || "0 2px 8px rgba(0, 0, 0, 0.1)",
    backdropFilter: "blur(10px)",
    position: "sticky",
    top: 0,
    zIndex: 1000,
  };

  const leftSectionStyle: React.CSSProperties = {
    display: "flex",
    alignItems: "center",
    gap: "16px",
  };

  const controlsStyle: React.CSSProperties = {
    display: "flex",
    alignItems: "center",
    gap: "16px",
  };

  return (
    <div style={headerStyle}>
      {/* Left Section - Page Title */}
      <div style={leftSectionStyle}>
        <Text
          style={{
            fontSize: "18px",
            fontWeight: 600,
            color: colors?.colorTextBase || "#ffffff",
          }}
        >
          {t("app.title", "ConvoSphere")}
        </Text>
      </div>

      {/* Right Section - Controls */}
      <div style={controlsStyle}>
        {/* Notifications */}
        <NotificationDropdown />

        {/* Theme Switcher */}
        <ThemeSwitcher />

        {/* User Dropdown */}
        <UserDropdown />
      </div>
    </div>
  );
};

export default HeaderBar;
