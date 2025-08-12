import React from "react";
import { Row, Col, Card, Avatar, Typography, Space, Tag } from "antd";
import {
  CheckCircleOutlined,
  WarningOutlined,
  ExclamationCircleOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import ModernCard from "../../components/ModernCard";
import ModernButton from "../../components/ModernButton";
import type { ServiceHealth } from "../../services/monitoring";

const { Title, Text } = Typography;

interface ServiceStatusProps {
  serviceHealth: ServiceHealth[];
  onHealthCheck: (serviceId?: string) => void;
  loading?: boolean;
}

const ServiceStatus: React.FC<ServiceStatusProps> = ({
  serviceHealth,
  onHealthCheck,
  loading = false,
}) => {
  const { t } = useTranslation();

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (days > 0) return `${days}d ${hours}h ${minutes}m`;
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "healthy":
        return <CheckCircleOutlined />;
      case "degraded":
        return <WarningOutlined />;
      default:
        return <ExclamationCircleOutlined />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "#52c41a";
      case "degraded":
        return "#faad14";
      default:
        return "#ff4d4f";
    }
  };

  const getStatusTagColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "success";
      case "degraded":
        return "warning";
      default:
        return "error";
    }
  };

  return (
    <ModernCard>
      <Row gutter={[16, 16]}>
        {serviceHealth.map((service: ServiceHealth) => (
          <Col xs={24} sm={12} lg={8} key={service.service}>
            <Card size="small">
              <div style={{ textAlign: "center" }}>
                <Avatar
                  size={48}
                  icon={getStatusIcon(service.status)}
                  style={{
                    backgroundColor: getStatusColor(service.status),
                    marginBottom: 8,
                  }}
                />
                <Title level={5} style={{ marginTop: 8 }}>
                  {service.service}
                </Title>
                <Space direction="vertical" size="small">
                  <Tag color={getStatusTagColor(service.status)}>
                    {t(`monitoring.status.${service.status}`)}
                  </Tag>
                  <Text type="secondary">
                    {t("monitoring.response_time")}: {service.responseTime}ms
                  </Text>
                  <Text type="secondary">
                    {t("monitoring.uptime")}: {formatUptime(service.uptime)}
                  </Text>
                  <Text type="secondary">
                    {t("monitoring.version")}: {service.version}
                  </Text>
                </Space>
                <div style={{ marginTop: 8 }}>
                  <ModernButton
                    size="small"
                    onClick={() => onHealthCheck(service.service)}
                    loading={loading}
                  >
                    {t("monitoring.check_health")}
                  </ModernButton>
                </div>
              </div>
            </Card>
          </Col>
        ))}
      </Row>
    </ModernCard>
  );
};

export default ServiceStatus;
