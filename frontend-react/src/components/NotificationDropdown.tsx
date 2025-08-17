import React, { useState, useEffect } from "react";
import {
  Badge,
  Dropdown,
  Avatar,
  List,
  Typography,
  Space,
  Tag,
  Tooltip,
  Divider,
  Button,
} from "antd";
import ModernButton from "./ModernButton";
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
import { useAuthStore } from "../store/authStore";
import { useThemeStore } from "../store/themeStore";

const { Text, Title } = Typography;

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

const NotificationDropdown: React.FC = () => {
  const { t } = useTranslation();
  const { token } = useAuthStore();
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(false);

  // Mock notifications for demonstration
  const mockNotifications: Notification[] = [
    {
      id: "1",
      title: "New Message",
      message: "You have received a new message from the AI assistant",
      type: "info",
      category: "chat",
      timestamp: new Date(Date.now() - 5 * 60 * 1000), // 5 minutes ago
      isRead: false,
      isImportant: false,
      actionUrl: "/chat",
    },
    {
      id: "2",
      title: "System Update",
      message: "A new system update is available",
      type: "warning",
      category: "system",
      timestamp: new Date(Date.now() - 30 * 60 * 1000), // 30 minutes ago
      isRead: false,
      isImportant: true,
    },
    {
      id: "3",
      title: "Assistant Created",
      message: "The assistant 'Support Bot' was successfully created",
      type: "success",
      category: "assistant",
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
      isRead: true,
      isImportant: false,
    },
    {
      id: "4",
      title: "Document Uploaded",
      message: "The document 'Project Plan.pdf' was successfully uploaded",
      type: "success",
      category: "document",
      timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000), // 4 hours ago
      isRead: true,
      isImportant: false,
    },
  ];

  useEffect(() => {
    loadNotifications();
  }, [token]);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 300));
      setNotifications(mockNotifications);
    } catch (error) {
      console.error("Error loading notifications:", error);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = (notificationId: string) => {
    setNotifications((prev) =>
      prev.map((notification) =>
        notification.id === notificationId
          ? { ...notification, isRead: true }
          : notification,
      ),
    );
  };

  const markAllAsRead = () => {
    setNotifications((prev) =>
      prev.map((notification) => ({ ...notification, isRead: true })),
    );
  };

  const deleteNotification = (notificationId: string) => {
    setNotifications((prev) =>
      prev.filter((notification) => notification.id !== notificationId),
    );
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case "info":
        return <InfoCircleOutlined />;
      case "success":
        return <CheckCircleOutlined />;
      case "warning":
        return <WarningOutlined />;
      case "error":
        return <ExclamationCircleOutlined />;
      default:
        return <BellOutlined />;
    }
  };

  const getNotificationColor = (type: string) => {
    if (!colors) return "#8c8c8c";
    switch (type) {
      case "info":
        return colors.colorPrimary;
      case "success":
        return colors.colorSuccess;
      case "warning":
        return colors.colorWarning;
      case "error":
        return colors.colorError;
      default:
        return colors.colorTextSecondary;
    }
  };

  const formatTimestamp = (timestamp: Date) => {
    const now = new Date();
    const diffInMinutes = Math.floor(
      (now.getTime() - timestamp.getTime()) / (1000 * 60),
    );

    if (diffInMinutes < 1) {
      return "Just now";
    } else if (diffInMinutes < 60) {
      return `${diffInMinutes}m ago`;
    } else if (diffInMinutes < 1440) {
      const hours = Math.floor(diffInMinutes / 60);
      return `${hours}h ago`;
    } else {
      const days = Math.floor(diffInMinutes / 1440);
      return `${days}d ago`;
    }
  };

  const unreadCount = notifications.filter((n) => !n.isRead).length;

  const notificationItems = [
    {
      key: "header",
      label: (
        <div
          style={{
            padding: "8px 16px",
            borderBottom: `1px solid ${colors?.colorBorder || "#d9d9d9"}`,
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <Title
              level={5}
              style={{ margin: 0, color: colors?.colorTextBase || "#ffffff" }}
            >
              {t("notifications.title", "Notifications")}
            </Title>
            <Space>
              <ModernButton
                variant="ghost"
                size="sm"
                onClick={markAllAsRead}
                disabled={unreadCount === 0}
                style={{ fontSize: "12px" }}
              >
                {t("notifications.mark_all_read", "Mark all read")}
              </ModernButton>
              <ModernButton
                variant="ghost"
                size="sm"
                icon={<SettingOutlined />}
                onClick={() => {
                  // TODO: Navigate to notification settings
                  console.log("Open notification settings");
                }}
                style={{ fontSize: "12px" }}
              >
                {t("notifications.settings", "Settings")}
              </ModernButton>
            </Space>
          </div>
        </div>
      ),
    },
    ...notifications.slice(0, 5).map((notification) => ({
      key: notification.id,
      label: (
        <div
          style={{
            padding: "12px 16px",
            opacity: notification.isRead ? 0.7 : 1,
            borderBottom: `1px solid ${colors?.colorBorder || "#d9d9d9"}`,
            backgroundColor: notification.isRead
              ? "transparent"
              : colors?.colorBgElevated || "#fafafa",
          }}
        >
          <div
            style={{ display: "flex", alignItems: "flex-start", gap: "12px" }}
          >
            <Avatar
              icon={getNotificationIcon(notification.type)}
              size="small"
              style={{
                backgroundColor: getNotificationColor(notification.type),
                color: "#FFFFFF",
                marginTop: "2px",
              }}
            />
            <div style={{ flex: 1, minWidth: 0 }}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  marginBottom: 4,
                }}
              >
                <Text
                  strong
                  style={{
                    fontSize: "14px",
                    color: colors?.colorTextBase || "#ffffff",
                  }}
                >
                  {notification.title}
                </Text>
                {notification.isImportant && (
                  <Tag color="red">
                    {t("notifications.important", "Important")}
                  </Tag>
                )}
              </div>
              <Text
                style={{
                  fontSize: "12px",
                  color: colors?.colorTextSecondary || "#cccccc",
                  display: "block",
                  marginBottom: 4,
                }}
              >
                {notification.message}
              </Text>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Text
                  style={{
                    fontSize: "11px",
                    color: colors?.colorTextSecondary || "#cccccc",
                  }}
                >
                  {formatTimestamp(notification.timestamp)}
                </Text>
                <Space size="small">
                  {!notification.isRead && (
                    <Tooltip
                      title={t("notifications.mark_as_read", "Mark as read")}
                    >
                      <ModernButton
                        variant="ghost"
                        size="sm"
                        icon={<CheckOutlined />}
                        onClick={(e) => {
                          e.stopPropagation();
                          markAsRead(notification.id);
                        }}
                        style={{
                          color: colors?.colorSuccess || "#52c41a",
                          fontSize: "12px",
                        }}
                      />
                    </Tooltip>
                  )}
                  <Tooltip title={t("notifications.delete", "Delete")}>
                    <ModernButton
                      variant="ghost"
                      size="sm"
                      icon={<DeleteOutlined />}
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteNotification(notification.id);
                      }}
                      style={{
                        color: colors?.colorError || "#ff4d4f",
                        fontSize: "12px",
                      }}
                    />
                  </Tooltip>
                </Space>
              </div>
            </div>
          </div>
        </div>
      ),
    })),
    {
      key: "footer",
      label: (
        <div style={{ padding: "8px 16px", textAlign: "center" }}>
          <Button
            type="link"
            size="small"
            onClick={() => {
              // TODO: Navigate to full notifications page
              console.log("View all notifications");
            }}
            style={{ fontSize: "12px" }}
          >
            {t("notifications.view_all", "View all notifications")}
          </Button>
        </div>
      ),
    },
  ];

  return (
    <Dropdown
      menu={{ items: notificationItems }}
      placement="bottomRight"
      trigger={["click"]}
      overlayStyle={{
        width: 400,
        maxHeight: 500,
        overflow: "auto",
        backgroundColor: colors?.colorBgContainer || "#ffffff",
        border: `1px solid ${colors?.colorBorder || "#d9d9d9"}`,
        borderRadius: "8px",
        boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)",
      }}
    >
      <Badge count={unreadCount} size="small" offset={[-5, 5]}>
        <Avatar
          icon={<BellOutlined />}
          size="small"
          style={{
            backgroundColor: colors?.colorPrimary || "#1890ff",
            color: colors?.colorTextBase || "#ffffff",
            cursor: "pointer",
            transition: "all 0.3s ease",
          }}
          className="notification-bell"
        />
      </Badge>
    </Dropdown>
  );
};

export default NotificationDropdown;
