import React, { useState, useEffect } from "react";
import { List, Avatar, Tag, Typography, Space } from "antd";
import ModernButton from "../ModernButton";
import {
  MessageOutlined,
  BookOutlined,
  TeamOutlined,
  ToolOutlined,
  UserOutlined,
  ApiOutlined,
  ClockCircleOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "../../store/authStore";
import { useThemeStore } from "../../store/themeStore";
import WidgetBase, { type WidgetConfig, type WidgetProps } from "./WidgetBase";
import {
  statisticsService,
  type ActivityItem,
} from "../../services/statistics";
import { realtimeService, type ActivityUpdate } from "../../services/realtime";

const { Title, Text } = Typography;

interface ActivityWidgetProps extends Omit<WidgetProps, "children"> {
  config: WidgetConfig & {
    settings: {
      maxItems: number;
      showUserInfo: boolean;
      showTimestamps: boolean;
      filterTypes: string[];
      refreshInterval: number;
    };
  };
}

const ActivityWidget: React.FC<ActivityWidgetProps> = ({
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

  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [localLoading, setLocalLoading] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  useEffect(() => {
    if (token) {
      loadActivities();
      setupRealtimeUpdates();
    }
  }, [token]);

  useEffect(() => {
    if (
      config.settings.refreshInterval &&
      config.settings.refreshInterval > 0
    ) {
      const interval = setInterval(
        loadActivities,
        config.settings.refreshInterval * 1000,
      );
      return () => clearInterval(interval);
    }
  }, [config.settings.refreshInterval]);

  const loadActivities = async () => {
    if (!token) return;

    try {
      setLocalLoading(true);
      setLocalError(null);

      const data = await statisticsService.getRecentActivity(
        token,
        config.settings.maxItems,
      );
      setActivities(data);
    } catch (error) {
      console.error("Error loading activities:", error);
      setLocalError(t("widgets.error_loading_activities"));
    } finally {
      setLocalLoading(false);
    }
  };

  const setupRealtimeUpdates = () => {
    if (!token) return;

    const unsubscribeActivity = realtimeService.onActivity(
      (activityUpdate: ActivityUpdate) => {
        setActivities((prevActivities) => {
          const newActivity: ActivityItem = {
            id: activityUpdate.id,
            type: activityUpdate.type,
            title: activityUpdate.title,
            description: activityUpdate.description,
            timestamp: activityUpdate.timestamp,
            user: activityUpdate.user,
            metadata: activityUpdate.metadata,
          };

          return [
            newActivity,
            ...prevActivities.slice(0, config.settings.maxItems - 1),
          ];
        });
      },
    );

    return () => {
      unsubscribeActivity();
    };
  };

  const handleRefresh = () => {
    loadActivities();
    if (onRefresh) {
      onRefresh();
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case "conversation":
        return <MessageOutlined style={{ color: colors.colorPrimary }} />;
      case "document":
        return <BookOutlined style={{ color: colors.colorSecondary }} />;
      case "assistant":
        return <TeamOutlined style={{ color: colors.colorAccent }} />;
      case "tool":
        return <ToolOutlined style={{ color: colors.colorPrimary }} />;
      case "user":
        return <UserOutlined style={{ color: colors.colorSecondary }} />;
      case "system":
        return <ApiOutlined style={{ color: colors.colorAccent }} />;
      default:
        return <MessageOutlined style={{ color: colors.colorTextSecondary }} />;
    }
  };

  const getActivityColor = (type: string) => {
    switch (type) {
      case "conversation":
        return colors.colorPrimary;
      case "document":
        return colors.colorSecondary;
      case "assistant":
        return colors.colorAccent;
      case "tool":
        return colors.colorPrimary;
      case "user":
        return colors.colorSecondary;
      case "system":
        return colors.colorAccent;
      default:
        return colors.colorTextSecondary;
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor(
      (now.getTime() - date.getTime()) / (1000 * 60),
    );

    if (diffInMinutes < 1) {
      return t("widgets.just_now");
    } else if (diffInMinutes < 60) {
      return t("widgets.minutes_ago", { minutes: diffInMinutes });
    } else if (diffInMinutes < 1440) {
      const hours = Math.floor(diffInMinutes / 60);
      return t("widgets.hours_ago", { hours });
    } else {
      const days = Math.floor(diffInMinutes / 1440);
      return t("widgets.days_ago", { days });
    }
  };

  const filteredActivities = activities.filter(
    (activity) =>
      config.settings.filterTypes.length === 0 ||
      config.settings.filterTypes.includes(activity.type),
  );

  const renderActivityItem = (activity: ActivityItem) => (
    <List.Item
      style={{
        padding: "12px 0",
        borderBottom: "1px solid var(--colorBorder)",
      }}
    >
      <List.Item.Meta
        avatar={
          <Avatar
            icon={getActivityIcon(activity.type)}
            style={{
              backgroundColor: getActivityColor(activity.type),
              color: "#FFFFFF",
              width: 32,
              height: 32,
            }}
          />
        }
        title={
          <Space>
            <Text strong style={{ fontSize: "14px" }}>
              {activity.title}
            </Text>
            <Tag color="blue" style={{ fontSize: "11px" }}>
              {activity.type}
            </Tag>
          </Space>
        }
        description={
          <div>
            {activity.description && (
              <Text
                type="secondary"
                style={{ display: "block", marginBottom: 4, fontSize: "12px" }}
              >
                {activity.description}
              </Text>
            )}
            <Space size="small">
              {config.settings.showUserInfo && (
                <Text type="secondary" style={{ fontSize: "11px" }}>
                  {activity.user}
                </Text>
              )}
              {config.settings.showTimestamps && (
                <Space size="small">
                  <ClockCircleOutlined
                    style={{
                      fontSize: "11px",
                      color: colors.colorTextSecondary,
                    }}
                  />
                  <Text type="secondary" style={{ fontSize: "11px" }}>
                    {formatTime(activity.timestamp)}
                  </Text>
                </Space>
              )}
            </Space>
          </div>
        }
      />
    </List.Item>
  );

  const renderContent = () => {
    if (filteredActivities.length === 0) {
      return (
        <div style={{ textAlign: "center", padding: "20px" }}>
          <Text type="secondary">{t("widgets.no_activities")}</Text>
        </div>
      );
    }

    return (
      <div>
        <List
          dataSource={filteredActivities}
          renderItem={renderActivityItem}
          style={{ maxHeight: "400px", overflowY: "auto" }}
        />

        {activities.length > config.settings.maxItems && (
          <div style={{ textAlign: "center", marginTop: 12 }}>
            <ModernButton
              variant="ghost"
              size="sm"
              onClick={() => {
                // TODO: Navigate to full activity page
                console.log("View all activities");
              }}
            >
              {t("widgets.view_all_activities")}
            </ModernButton>
          </div>
        )}
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

export default ActivityWidget;
