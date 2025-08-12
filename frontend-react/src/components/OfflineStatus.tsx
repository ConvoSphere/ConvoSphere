import React from "react";
import { Badge, Card, List, Progress, Space, Typography, Tooltip } from "antd";
import ModernButton from "./ModernButton";
import {
  WifiOutlined,
  WifiOffOutlined,
  SyncOutlined,
  CloudSyncOutlined,
  ClearOutlined,
} from "@ant-design/icons";
import { useOfflineStatus, offlineService } from "../services/offlineService";
import { useThemeStore } from "../store/themeStore";

const { Text, Title } = Typography;

const OfflineStatus: React.FC = () => {
  const isOnline = useOfflineStatus();
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const [stats, setStats] = React.useState(offlineService.getOfflineStats());
  const [queuedActions, setQueuedActions] = React.useState(
    offlineService.getQueuedActions(),
  );

  // Update stats periodically
  React.useEffect(() => {
    const interval = setInterval(() => {
      setStats(offlineService.getOfflineStats());
      setQueuedActions(offlineService.getQueuedActions());
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleClearCache = () => {
    offlineService.clearCache();
    setStats(offlineService.getOfflineStats());
  };

  const handleClearQueue = () => {
    offlineService.clearAllData();
    setStats(offlineService.getOfflineStats());
    setQueuedActions(offlineService.getQueuedActions());
  };

  const getStatusIcon = () => {
    if (isOnline) {
      return <WifiOutlined style={{ color: colors.colorSuccess }} />;
    } else {
      return <WifiOffOutlined style={{ color: colors.colorError }} />;
    }
  };

  const getStatusText = () => {
    if (isOnline) {
      return "Online";
    } else {
      return "Offline";
    }
  };

  const getStatusColor = () => {
    if (isOnline) {
      return colors.colorSuccess;
    } else {
      return colors.colorError;
    }
  };

  return (
    <Card
      size="small"
      style={{
        backgroundColor: colors.colorBgContainer,
        border: `1px solid ${colors.colorBorder}`,
        marginBottom: "16px",
      }}
    >
      <Space direction="vertical" size="small" style={{ width: "100%" }}>
        {/* Status Header */}
        <Space align="center">
          {getStatusIcon()}
          <Text strong style={{ color: colors.colorTextBase }}>
            Connection Status: {getStatusText()}
          </Text>
          <Badge
            status={isOnline ? "success" : "error"}
            text={isOnline ? "Connected" : "Disconnected"}
          />
        </Space>

        {/* Stats Row */}
        <Space size="large">
          <Space>
            <CloudSyncOutlined style={{ color: colors.colorTextSecondary }} />
            <Text style={{ color: colors.colorTextSecondary }}>
              Queued: {stats.queuedActions}
            </Text>
          </Space>
          <Space>
            <SyncOutlined style={{ color: colors.colorTextSecondary }} />
            <Text style={{ color: colors.colorTextSecondary }}>
              Cached: {stats.cacheSize}
            </Text>
          </Space>
          {stats.syncInProgress && (
            <Space>
              <SyncOutlined spin style={{ color: colors.colorPrimary }} />
              <Text style={{ color: colors.colorPrimary }}>Syncing...</Text>
            </Space>
          )}
        </Space>

        {/* Queued Actions */}
        {queuedActions.length > 0 && (
          <div>
            <Title
              level={5}
              style={{ color: colors.colorTextBase, margin: "8px 0" }}
            >
              Queued Actions ({queuedActions.length})
            </Title>
            <List
              size="small"
              dataSource={queuedActions.slice(0, 5)} // Show only first 5
              renderItem={(action) => (
                <List.Item
                  style={{
                    padding: "4px 0",
                    borderBottom: `1px solid ${colors.colorBorder}`,
                  }}
                >
                  <Space
                    direction="vertical"
                    size="small"
                    style={{ width: "100%" }}
                  >
                    <Space>
                      <Text strong style={{ color: colors.colorTextBase }}>
                        {action.method} {action.endpoint.split("/").pop()}
                      </Text>
                      <Badge
                        count={action.retryCount}
                        style={{ backgroundColor: colors.colorWarning }}
                      />
                    </Space>
                    <Text type="secondary" style={{ fontSize: "12px" }}>
                      {new Date(action.timestamp).toLocaleTimeString()}
                    </Text>
                  </Space>
                </List.Item>
              )}
            />
            {queuedActions.length > 5 && (
              <Text type="secondary" style={{ fontSize: "12px" }}>
                ... and {queuedActions.length - 5} more actions
              </Text>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <Space>
          <Tooltip title="Clear cache">
            <ModernButton
              size="sm"
              icon={<ClearOutlined />}
              onClick={handleClearCache}
              disabled={stats.cacheSize === 0}
            >
              Clear Cache
            </ModernButton>
          </Tooltip>
          <Tooltip title="Clear all offline data">
            <ModernButton
              size="sm"
              variant="error"
              icon={<ClearOutlined />}
              onClick={handleClearQueue}
              disabled={stats.queuedActions === 0}
            >
              Clear Queue
            </ModernButton>
          </Tooltip>
        </Space>

        {/* Progress Bar for Sync */}
        {stats.syncInProgress && (
          <Progress
            percent={100}
            status="active"
            strokeColor={colors.colorPrimary}
            showInfo={false}
            style={{ marginTop: "8px" }}
          />
        )}
      </Space>
    </Card>
  );
};

export default OfflineStatus;
