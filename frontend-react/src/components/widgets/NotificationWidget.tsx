import React, { useState, useEffect, useMemo } from "react";
import { List, Badge, Typography, Space, Tag, Avatar, Tooltip } from "antd";
import ModernButton from "../ModernButton";
import {
  BellOutlined,
  CheckOutlined,
  DeleteOutlined,
  SettingOutlined,
  InfoCircleOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  WarningOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "../../store/authStore";
import { useThemeStore } from "../../store/themeStore";
import WidgetBase, { type WidgetConfig, type WidgetProps } from "./WidgetBase";
import ModernButton from "../ModernButton";

const { Title, Text } = Typography;

interface Notification {
  id: string;
  title: string;
  message: string;
  type: "info" | "success" | "warning" | "error";
  category: "system" | "user" | "chat" | "assistant" | "document";
  timestamp: Date;
  isRead: boolean;
  isImportant: boolean;
  actionUrl?: string;
  metadata?: Record<string, any>;
}

interface NotificationWidgetProps extends Omit<WidgetProps, "children"> {
  config: WidgetConfig & {
    settings: {
      maxNotifications: number;
      showRead: boolean;
      autoMarkAsRead: boolean;
      filterCategories: string[];
      refreshInterval: number;
      soundEnabled: boolean;
    };
  };
}

const NotificationWidget: React.FC<NotificationWidgetProps> = ({
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

  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [localLoading, setLocalLoading] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  // Mock notifications for demonstration
  const mockNotifications: Notification[] = [
    {
      id: "1",
      title: "Neue Nachricht",
      message: "Sie haben eine neue Nachricht von Max Mustermann erhalten",
      type: "info",
      category: "chat",
      timestamp: new Date(Date.now() - 5 * 60 * 1000), // 5 minutes ago
      isRead: false,
      isImportant: false,
      actionUrl: "/chat",
    },
    {
      id: "2",
      title: "System-Update",
      message: "Ein neues System-Update ist verfügbar",
      type: "warning",
      category: "system",
      timestamp: new Date(Date.now() - 30 * 60 * 1000), // 30 minutes ago
      isRead: false,
      isImportant: true,
    },
    {
      id: "3",
      title: "Assistent erstellt",
      message: "Der Assistent 'Support Bot' wurde erfolgreich erstellt",
      type: "success",
      category: "assistant",
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
      isRead: true,
      isImportant: false,
    },
    {
      id: "4",
      title: "Dokument hochgeladen",
      message: "Das Dokument 'Projektplan.pdf' wurde erfolgreich hochgeladen",
      type: "success",
      category: "document",
      timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000), // 4 hours ago
      isRead: true,
      isImportant: false,
    },
    {
      id: "5",
      title: "Fehler beim Export",
      message: "Der Export konnte nicht abgeschlossen werden",
      type: "error",
      category: "system",
      timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000), // 6 hours ago
      isRead: false,
      isImportant: true,
    },
  ];

  useEffect(() => {
    loadNotifications();
  }, [token]);

  useEffect(() => {
    if (config.settings.refreshInterval && config.settings.refreshInterval > 0) {
      const interval = setInterval(loadNotifications, config.settings.refreshInterval * 1000);
      return () => clearInterval(interval);
    }
  }, [config.settings.refreshInterval]);

  const loadNotifications = async () => {
    try {
      setLocalLoading(true);
      setLocalError(null);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      setNotifications(mockNotifications);
    } catch (error) {
      console.error("Error loading notifications:", error);
      setLocalError(t("widgets.error_loading_notifications"));
    } finally {
      setLocalLoading(false);
    }
  };

  const markAsRead = (notificationId: string) => {
    setNotifications(prev =>
      prev.map(notification =>
        notification.id === notificationId
          ? { ...notification, isRead: true }
          : notification
      )
    );
  };

  const markAllAsRead = () => {
    setNotifications(prev =>
      prev.map(notification => ({ ...notification, isRead: true }))
    );
  };

  const deleteNotification = (notificationId: string) => {
    setNotifications(prev =>
      prev.filter(notification => notification.id !== notificationId)
    );
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case "info": return <InfoCircleOutlined />;
      case "success": return <CheckCircleOutlined />;
      case "warning": return <WarningOutlined />;
      case "error": return <ExclamationCircleOutlined />;
      default: return <BellOutlined />;
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case "info": return colors.colorPrimary;
      case "success": return colors.colorSuccess;
      case "warning": return colors.colorWarning;
      case "error": return colors.colorError;
      default: return colors.colorTextSecondary;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "system": return colors.colorPrimary;
      case "user": return colors.colorSecondary;
      case "chat": return colors.colorAccent;
      case "assistant": return colors.colorSuccess;
      case "document": return colors.colorWarning;
      default: return colors.colorTextSecondary;
    }
  };

  const formatTimestamp = (timestamp: Date) => {
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - timestamp.getTime()) / (1000 * 60));

    if (diffInMinutes < 1) {
      return t("widgets.notifications.just_now");
    } else if (diffInMinutes < 60) {
      return t("widgets.notifications.minutes_ago", { minutes: diffInMinutes });
    } else if (diffInMinutes < 1440) {
      const hours = Math.floor(diffInMinutes / 60);
      return t("widgets.notifications.hours_ago", { hours });
    } else {
      const days = Math.floor(diffInMinutes / 1440);
      return t("widgets.notifications.days_ago", { days });
    }
  };

  const filteredNotifications = useMemo(() => {
    let filtered = notifications;

    // Filter by read status
    if (!config.settings.showRead) {
      filtered = filtered.filter(notification => !notification.isRead);
    }

    // Filter by categories
    if (config.settings.filterCategories.length > 0) {
      filtered = filtered.filter(notification =>
        config.settings.filterCategories.includes(notification.category)
      );
    }

    // Sort by importance and timestamp
    filtered.sort((a, b) => {
      if (a.isImportant !== b.isImportant) {
        return b.isImportant ? 1 : -1;
      }
      return b.timestamp.getTime() - a.timestamp.getTime();
    });

    return filtered.slice(0, config.settings.maxNotifications);
  }, [notifications, config.settings]);

  const unreadCount = notifications.filter(n => !n.isRead).length;
  const importantCount = notifications.filter(n => n.isImportant && !n.isRead).length;

  const renderNotificationItem = (notification: Notification) => (
    <List.Item
      style={{
        padding: "12px 0",
        opacity: notification.isRead ? 0.7 : 1,
        borderBottom: `1px solid ${colors.colorBorder}`,
      }}
      actions={[
        !notification.isRead && (
          <Tooltip title={t("widgets.notifications.mark_as_read")}>
            <ModernButton
              variant="ghost"
              size="sm"
              icon={<CheckOutlined />}
              onClick={() => markAsRead(notification.id)}
              style={{ color: colors.colorSuccess }}
            />
          </Tooltip>
        ),
        <Tooltip title={t("widgets.notifications.delete")}>
          <ModernButton
            variant="ghost"
            size="sm"
            icon={<DeleteOutlined />}
            onClick={() => deleteNotification(notification.id)}
            style={{ color: colors.colorError }}
          />
        </Tooltip>,
      ].filter(Boolean)}
    >
      <List.Item.Meta
        avatar={
          <Badge dot={!notification.isRead} offset={[-5, 5]}>
            <Avatar
              icon={getNotificationIcon(notification.type)}
              style={{
                backgroundColor: getNotificationColor(notification.type),
                color: "#FFFFFF",
              }}
            />
          </Badge>
        }
        title={
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <Text strong style={{ fontSize: "14px" }}>
              {notification.title}
            </Text>
            {notification.isImportant && (
              <Tag color="red" size="small">
                {t("widgets.notifications.important")}
              </Tag>
            )}
            <Tag color={getCategoryColor(notification.category)} size="small">
              {t(`widgets.notifications.category.${notification.category}`)}
            </Tag>
          </div>
        }
        description={
          <div>
            <div style={{ fontSize: "12px", marginBottom: 4 }}>
              {notification.message}
            </div>
            <div style={{ fontSize: "11px", color: colors.colorTextSecondary }}>
              {formatTimestamp(notification.timestamp)}
            </div>
          </div>
        }
      />
    </List.Item>
  );

  const renderQuickStats = () => (
    <div style={{ marginBottom: 16 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
        <div style={{ textAlign: "center", padding: "8px", background: colors.colorBgContainer, borderRadius: "4px" }}>
          <div style={{ fontSize: "18px", fontWeight: "bold", color: colors.colorPrimary }}>
            {unreadCount}
          </div>
          <div style={{ fontSize: "11px", color: colors.colorTextSecondary }}>
            {t("widgets.notifications.unread")}
          </div>
        </div>
        <div style={{ textAlign: "center", padding: "8px", background: colors.colorBgContainer, borderRadius: "4px" }}>
          <div style={{ fontSize: "18px", fontWeight: "bold", color: colors.colorError }}>
            {importantCount}
          </div>
          <div style={{ fontSize: "11px", color: colors.colorTextSecondary }}>
            {t("widgets.notifications.important")}
          </div>
        </div>
        <div style={{ textAlign: "center", padding: "8px", background: colors.colorBgContainer, borderRadius: "4px" }}>
          <div style={{ fontSize: "18px", fontWeight: "bold", color: colors.colorSuccess }}>
            {notifications.length}
          </div>
          <div style={{ fontSize: "11px", color: colors.colorTextSecondary }}>
            {t("widgets.notifications.total")}
          </div>
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    if (localError) {
      return (
        <div style={{ textAlign: "center", padding: "20px" }}>
          <Text type="danger">{localError}</Text>
        </div>
      );
    }

    return (
      <div>
        {renderQuickStats()}
        
        <div style={{ marginBottom: 16 }}>
          <Space>
            <ModernButton
              variant="outlined"
              size="small"
              onClick={markAllAsRead}
              disabled={unreadCount === 0}
            >
              {t("widgets.notifications.mark_all_read")}
            </ModernButton>
            <ModernButton
              variant="outlined"
              size="small"
              icon={<SettingOutlined />}
              onClick={() => {
                // TODO: Open notification settings
                console.log("Open notification settings");
              }}
            >
              {t("widgets.notifications.settings")}
            </ModernButton>
          </Space>
        </div>

        {filteredNotifications.length > 0 ? (
          <List
            dataSource={filteredNotifications}
            renderItem={renderNotificationItem}
            style={{ maxHeight: "400px", overflowY: "auto" }}
          />
        ) : (
          <div style={{ textAlign: "center", padding: "40px 20px" }}>
            <BellOutlined style={{ fontSize: "48px", color: colors.colorTextSecondary, marginBottom: 16 }} />
            <Text type="secondary">{t("widgets.notifications.no_notifications")}</Text>
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
      onRefresh={loadNotifications}
      loading={loading || localLoading}
      error={error || localError}
    >
      {renderContent()}
    </WidgetBase>
  );
};

export default NotificationWidget;