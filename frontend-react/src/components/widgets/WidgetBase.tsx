import React, { useState } from "react";
import { Card, Space, Typography, Tooltip, Dropdown } from "antd";
import ModernButton from "../ModernButton";
import {
  MoreOutlined,
  ReloadOutlined,
  SettingOutlined,
  FullscreenOutlined,
  CloseOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useThemeStore } from "../../store/themeStore";
import type { MenuProps } from "antd";

const { Title, Text } = Typography;

export interface WidgetConfig {
  id: string;
  type: string;
  title: string;
  description?: string;
  size: "small" | "medium" | "large" | "full";
  position: { x: number; y: number };
  settings: Record<string, any>;
  isVisible: boolean;
  isCollapsed: boolean;
  refreshInterval?: number; // in seconds
  lastRefresh?: string;
}

export interface WidgetProps {
  config: WidgetConfig;
  onConfigChange: (config: WidgetConfig) => void;
  onRemove: (widgetId: string) => void;
  onRefresh?: () => void;
  children?: React.ReactNode;
  loading?: boolean;
  error?: string | null;
  className?: string;
}

const WidgetBase: React.FC<WidgetProps> = ({
  config,
  onConfigChange,
  onRemove,
  onRefresh,
  children,
  loading = false,
  error = null,
  className,
}) => {
  const { t } = useTranslation();
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const [isFullscreen, setIsFullscreen] = useState(false);

  const handleToggleCollapse = () => {
    onConfigChange({
      ...config,
      isCollapsed: !config.isCollapsed,
    });
  };

  const handleToggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const handleRefresh = () => {
    if (onRefresh) {
      onRefresh();
      onConfigChange({
        ...config,
        lastRefresh: new Date().toISOString(),
      });
    }
  };

  const handleSettings = () => {
    // TODO: Implement settings modal
    console.log("Open settings for widget:", config.id);
  };

  const getSizeStyles = () => {
    switch (config.size) {
      case "small":
        return { width: "250px", minHeight: "200px" };
      case "medium":
        return { width: "400px", minHeight: "300px" };
      case "large":
        return { width: "600px", minHeight: "400px" };
      case "full":
        return { width: "100%", minHeight: "500px" };
      default:
        return { width: "400px", minHeight: "300px" };
    }
  };

  const getDropdownItems = (): MenuProps["items"] => [
    {
      key: "refresh",
      icon: <ReloadOutlined />,
      label: t("widgets.refresh"),
      onClick: handleRefresh,
    },
    {
      key: "settings",
      icon: <SettingOutlined />,
      label: t("widgets.settings"),
      onClick: handleSettings,
    },
    {
      key: "fullscreen",
      icon: <FullscreenOutlined />,
      label: isFullscreen
        ? t("widgets.exit_fullscreen")
        : t("widgets.fullscreen"),
      onClick: handleToggleFullscreen,
    },
    {
      type: "divider",
    },
    {
      key: "remove",
      icon: <CloseOutlined />,
      label: t("widgets.remove"),
      danger: true,
      onClick: () => onRemove(config.id),
    },
  ];

  const renderHeader = () => (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "12px 16px",
        borderBottom: `1px solid ${colors.colorBorder}`,
        background: colors.colorBgContainer,
      }}
    >
      <div style={{ flex: 1, minWidth: 0 }}>
        <Title level={5} style={{ margin: 0, fontSize: "14px" }}>
          {config.title}
        </Title>
        {config.description && (
          <Text type="secondary" style={{ fontSize: "12px" }}>
            {config.description}
          </Text>
        )}
      </div>

      <Space size="small">
        {loading && (
          <Tooltip title={t("widgets.refreshing")}>
            <ReloadOutlined spin style={{ color: colors.colorPrimary }} />
          </Tooltip>
        )}

        {config.lastRefresh && (
          <Tooltip
            title={t("widgets.last_refresh", {
              time: new Date(config.lastRefresh).toLocaleTimeString(),
            })}
          >
            <Text type="secondary" style={{ fontSize: "11px" }}>
              {new Date(config.lastRefresh).toLocaleTimeString()}
            </Text>
          </Tooltip>
        )}

        <Dropdown
          menu={{ items: getDropdownItems() }}
          trigger={["click"]}
          placement="bottomRight"
        >
          <ModernButton
            variant="ghost"
            size="sm"
            icon={<MoreOutlined />}
            style={{ color: colors.colorTextSecondary }}
          />
        </Dropdown>
      </Space>
    </div>
  );

  const renderContent = () => {
    if (config.isCollapsed) {
      return (
        <div
          style={{
            padding: "20px",
            textAlign: "center",
            color: colors.colorTextSecondary,
          }}
        >
          <Text type="secondary">{t("widgets.collapsed")}</Text>
        </div>
      );
    }

    if (error) {
      return (
        <div
          style={{
            padding: "20px",
            textAlign: "center",
            color: colors.colorError,
          }}
        >
          <Text type="danger">{error}</Text>
        </div>
      );
    }

    return <div style={{ padding: "16px", height: "100%" }}>{children}</div>;
  };

  const widgetStyle: React.CSSProperties = {
    ...getSizeStyles(),
    position: "relative",
    background: colors.colorBgContainer,
    border: `1px solid ${colors.colorBorder}`,
    borderRadius: "8px",
    boxShadow: colors.boxShadow,
    overflow: "hidden",
    transition: "all 0.3s ease",
    ...(isFullscreen && {
      position: "fixed",
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      zIndex: 1000,
      width: "100vw",
      height: "100vh",
    }),
  };

  return (
    <div
      className={`widget-base ${className || ""}`}
      style={widgetStyle}
      data-widget-id={config.id}
      data-widget-type={config.type}
    >
      {renderHeader()}
      {renderContent()}
    </div>
  );
};

export default WidgetBase;
