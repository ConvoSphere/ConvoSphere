import React, { useState, useEffect } from "react";
import { Row, Col, Statistic, Progress, Typography, Space } from "antd";
import {
  MessageOutlined,
  BookOutlined,
  TeamOutlined,
  ToolOutlined,
  UserOutlined,
  RiseOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "../../store/authStore";
import { useThemeStore } from "../../store/themeStore";
import WidgetBase, { type WidgetConfig, type WidgetProps } from "./WidgetBase";
import { statisticsService } from "../../services/statistics";
import { realtimeService } from "../../services/realtime";

const { Title, Text } = Typography;

interface StatsWidgetProps extends Omit<WidgetProps, "children"> {
  config: WidgetConfig & {
    settings: {
      showConversations: boolean;
      showMessages: boolean;
      showDocuments: boolean;
      showAssistants: boolean;
      showTools: boolean;
      showUsers: boolean;
      showPerformance: boolean;
      refreshInterval: number;
    };
  };
}

const StatsWidget: React.FC<StatsWidgetProps> = ({
  config,
  onConfigChange,
  onRemove,
  onRefresh,
  loading = false,
  error = null,
}) => {
  const { t } = useTranslation();
  const { token } = useAuthStore();
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const [stats, setStats] = useState<any>(null);
  const [localLoading, setLocalLoading] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  useEffect(() => {
    if (token) {
      loadStats();
      setupRealtimeUpdates();
    }
  }, [token]);

  useEffect(() => {
    if (config.settings.refreshInterval && config.settings.refreshInterval > 0) {
      const interval = setInterval(loadStats, config.settings.refreshInterval * 1000);
      return () => clearInterval(interval);
    }
  }, [config.settings.refreshInterval]);

  const loadStats = async () => {
    if (!token) return;

    try {
      setLocalLoading(true);
      setLocalError(null);

      const data = await statisticsService.getOverviewStats(token);
      setStats(data);
    } catch (error) {
      console.error("Error loading stats:", error);
      setLocalError(t("widgets.error_loading_stats"));
    } finally {
      setLocalLoading(false);
    }
  };

  const setupRealtimeUpdates = () => {
    if (!token) return;

    const unsubscribeStats = realtimeService.onStatsUpdate((statsUpdate) => {
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

    return () => {
      unsubscribeStats();
    };
  };

  const handleRefresh = () => {
    loadStats();
    if (onRefresh) {
      onRefresh();
    }
  };

  const renderStatistic = (
    title: string,
    value: number,
    icon: React.ReactNode,
    color: string,
    suffix?: string
  ) => (
    <Col span={12} style={{ marginBottom: 16 }}>
      <Statistic
        title={title}
        value={value}
        prefix={icon}
        suffix={suffix}
        valueStyle={{ color, fontSize: "18px" }}
        style={{ textAlign: "center" }}
      />
    </Col>
  );

  const renderPerformanceSection = () => {
    if (!config.settings.showPerformance || !stats) return null;

    return (
      <div style={{ marginTop: 16 }}>
        <Title level={5} style={{ marginBottom: 12 }}>
          {t("widgets.performance")}
        </Title>
        <Row gutter={16}>
          <Col span={12}>
            <div style={{ marginBottom: 8 }}>
              <Text type="secondary" style={{ fontSize: "12px" }}>
                CPU: {stats.systemStats.performance.cpuUsage}%
              </Text>
            </div>
            <Progress
              percent={stats.systemStats.performance.cpuUsage}
              strokeColor={colors.colorPrimary}
              size="small"
              showInfo={false}
            />
          </Col>
          <Col span={12}>
            <div style={{ marginBottom: 8 }}>
              <Text type="secondary" style={{ fontSize: "12px" }}>
                RAM: {stats.systemStats.performance.memoryUsage}%
              </Text>
            </div>
            <Progress
              percent={stats.systemStats.performance.memoryUsage}
              strokeColor={colors.colorSecondary}
              size="small"
              showInfo={false}
            />
          </Col>
        </Row>
        <Row gutter={16} style={{ marginTop: 12 }}>
          <Col span={12}>
            <Statistic
              title={t("widgets.response_time")}
              value={stats.systemStats.performance.responseTime}
              suffix="ms"
              valueStyle={{ fontSize: "14px" }}
            />
          </Col>
          <Col span={12}>
            <Statistic
              title={t("widgets.uptime")}
              value={stats.systemStats.performance.uptime}
              suffix="%"
              precision={1}
              valueStyle={{ fontSize: "14px" }}
            />
          </Col>
        </Row>
      </div>
    );
  };

  const renderContent = () => {
    if (!stats) {
      return (
        <div style={{ textAlign: "center", padding: "20px" }}>
          <Text type="secondary">{t("widgets.no_data")}</Text>
        </div>
      );
    }

    return (
      <div>
        <Row gutter={16}>
          {config.settings.showConversations &&
            renderStatistic(
              t("widgets.conversations"),
              stats.systemStats.totalConversations,
              <MessageOutlined style={{ color: colors.colorPrimary }} />,
              colors.colorPrimary
            )}

          {config.settings.showMessages &&
            renderStatistic(
              t("widgets.messages"),
              stats.systemStats.totalMessages,
              <MessageOutlined style={{ color: colors.colorSecondary }} />,
              colors.colorSecondary
            )}

          {config.settings.showDocuments &&
            renderStatistic(
              t("widgets.documents"),
              stats.systemStats.totalDocuments,
              <BookOutlined style={{ color: colors.colorAccent }} />,
              colors.colorAccent
            )}

          {config.settings.showAssistants &&
            renderStatistic(
              t("widgets.assistants"),
              stats.systemStats.totalAssistants,
              <TeamOutlined style={{ color: colors.colorPrimary }} />,
              colors.colorPrimary
            )}

          {config.settings.showTools &&
            renderStatistic(
              t("widgets.tools"),
              stats.systemStats.totalTools,
              <ToolOutlined style={{ color: colors.colorSecondary }} />,
              colors.colorSecondary
            )}

          {config.settings.showUsers &&
            renderStatistic(
              t("widgets.active_users"),
              stats.systemStats.activeUsers,
              <UserOutlined style={{ color: colors.colorAccent }} />,
              colors.colorAccent
            )}
        </Row>

        {renderPerformanceSection()}
      </div>
    );
  };

  return (
    <WidgetBase
      config={config}
      onConfigChange={onConfigChange}
      onRemove={onRemove}
      onRefresh={handleRefresh}
      loading={loading || localLoading}
      error={error || localError}
    >
      {renderContent()}
    </WidgetBase>
  );
};

export default StatsWidget;