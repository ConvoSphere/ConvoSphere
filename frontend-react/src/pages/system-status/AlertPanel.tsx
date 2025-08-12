import React from "react";
import { List, Avatar, Typography, Space, Tag } from "antd";
import {
  ExclamationCircleOutlined,
  WarningOutlined,
  InfoCircleOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import ModernCard from "../../components/ModernCard";
import ModernButton from "../../components/ModernButton";
import type { Alert as AlertType } from "../../services/monitoring";

const { Text } = Typography;

interface AlertPanelProps {
  alerts: AlertType[];
  onAcknowledgeAlert: (alertId: string) => void;
  loading?: boolean;
}

const AlertPanel: React.FC<AlertPanelProps> = ({
  alerts,
  onAcknowledgeAlert,
  loading = false,
}) => {
  const { t } = useTranslation();

  const getAlertIcon = (type: string) => {
    switch (type) {
      case "critical":
      case "error":
        return <ExclamationCircleOutlined />;
      case "warning":
        return <WarningOutlined />;
      default:
        return <InfoCircleOutlined />;
    }
  };

  const getAlertColor = (type: string) => {
    switch (type) {
      case "critical":
        return "#ff4d4f";
      case "error":
        return "#ff7875";
      case "warning":
        return "#faad14";
      default:
        return "#1890ff";
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "red";
      case "high":
        return "orange";
      case "medium":
        return "gold";
      default:
        return "blue";
    }
  };

  return (
    <ModernCard>
      {alerts.length > 0 ? (
        <List
          dataSource={alerts}
          renderItem={(alert: AlertType) => (
            <List.Item
              actions={[
                !alert.acknowledged && (
                  <ModernButton
                    key="acknowledge"
                    size="small"
                    onClick={() => onAcknowledgeAlert(alert.id)}
                  >
                    {t("monitoring.acknowledge")}
                  </ModernButton>
                ),
              ].filter(Boolean)}
            >
              <List.Item.Meta
                avatar={
                  <Avatar
                    icon={getAlertIcon(alert.type)}
                    style={{
                      backgroundColor: getAlertColor(alert.type),
                    }}
                  />
                }
                title={
                  <Space>
                    <Text strong>{alert.title}</Text>
                    <Tag color={getSeverityColor(alert.severity)}>
                      {t(`monitoring.severity.${alert.severity}`)}
                    </Tag>
                    {alert.acknowledged && (
                      <Tag color="green">{t("monitoring.acknowledged")}</Tag>
                    )}
                  </Space>
                }
                description={
                  <Space direction="vertical" size="small">
                    <Text>{alert.message}</Text>
                    <Text type="secondary" style={{ fontSize: "12px" }}>
                      {t("monitoring.source")}: {alert.source} |
                      {t("monitoring.timestamp")}:{" "}
                      {new Date(alert.timestamp).toLocaleString()}
                    </Text>
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      ) : (
        <div style={{ textAlign: "center", padding: "40px" }}>
          <Text type="secondary">{t("monitoring.no_alerts")}</Text>
        </div>
      )}
    </ModernCard>
  );
};

export default AlertPanel;
