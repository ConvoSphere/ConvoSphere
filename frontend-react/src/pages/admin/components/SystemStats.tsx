import React from "react";
import { Row, Col, Statistic, Progress, Card, Space } from "antd";
import {
  UserOutlined,
  MessageOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useSystemStats } from "../hooks/useSystemStats";
import ModernCard from "../../../components/ModernCard";
import ModernButton from "../../../components/ModernButton";

const SystemStats: React.FC = () => {
  const { t } = useTranslation();
  const { systemStats, loading, refreshStats } = useSystemStats();

  if (!systemStats) {
    return <div>Loading...</div>;
  }

  const formatUptime = (uptime: number) => {
    const days = Math.floor(uptime / 24);
    const hours = Math.floor(uptime % 24);
    return `${days}d ${hours}h`;
  };

  const getUsageColor = (usage: number) => {
    if (usage < 50) return "#52c41a";
    if (usage < 80) return "#faad14";
    return "#ff4d4f";
  };

  return (
    <div>
      <ModernCard
        title={t("admin.stats.title")}
        extra={
          <ModernButton
            icon={<ReloadOutlined />}
            onClick={refreshStats}
            loading={loading}
          >
            {t("common.refresh")}
          </ModernButton>
        }
      >
        <Row gutter={[24, 24]}>
          {/* User Statistics */}
          <Col xs={24} sm={12} lg={6}>
            <Card size="small">
              <Statistic
                title={t("admin.stats.total_users")}
                value={systemStats.totalUsers}
                prefix={<UserOutlined />}
                valueStyle={{ color: "#1890ff" }}
              />
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card size="small">
              <Statistic
                title={t("admin.stats.active_users")}
                value={systemStats.activeUsers}
                prefix={<UserOutlined />}
                valueStyle={{ color: "#52c41a" }}
              />
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card size="small">
              <Statistic
                title={t("admin.stats.total_conversations")}
                value={systemStats.totalConversations}
                prefix={<MessageOutlined />}
                valueStyle={{ color: "#722ed1" }}
              />
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card size="small">
              <Statistic
                title={t("admin.stats.total_messages")}
                value={systemStats.totalMessages}
                prefix={<MessageOutlined />}
                valueStyle={{ color: "#13c2c2" }}
              />
            </Card>
          </Col>

          {/* System Resources */}
          <Col xs={24} lg={12}>
            <Card title={t("admin.stats.system_resources")} size="small">
              <Space direction="vertical" style={{ width: "100%" }}>
                <div>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      marginBottom: 4,
                    }}
                  >
                    <span>{t("admin.stats.cpu_usage")}</span>
                    <span>{systemStats.cpuUsage.toFixed(1)}%</span>
                  </div>
                  <Progress
                    percent={systemStats.cpuUsage}
                    strokeColor={getUsageColor(systemStats.cpuUsage)}
                    showInfo={false}
                  />
                </div>

                <div>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      marginBottom: 4,
                    }}
                  >
                    <span>{t("admin.stats.memory_usage")}</span>
                    <span>{systemStats.memoryUsage.toFixed(1)}%</span>
                  </div>
                  <Progress
                    percent={systemStats.memoryUsage}
                    strokeColor={getUsageColor(systemStats.memoryUsage)}
                    showInfo={false}
                  />
                </div>

                <div>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      marginBottom: 4,
                    }}
                  >
                    <span>{t("admin.stats.disk_usage")}</span>
                    <span>{systemStats.diskUsage.toFixed(1)}%</span>
                  </div>
                  <Progress
                    percent={systemStats.diskUsage}
                    strokeColor={getUsageColor(systemStats.diskUsage)}
                    showInfo={false}
                  />
                </div>
              </Space>
            </Card>
          </Col>

          {/* System Information */}
          <Col xs={24} lg={12}>
            <Card title={t("admin.stats.system_info")} size="small">
              <Space direction="vertical" style={{ width: "100%" }}>
                <div
                  style={{ display: "flex", justifyContent: "space-between" }}
                >
                  <span>{t("admin.stats.system_uptime")}</span>
                  <span style={{ fontWeight: "bold" }}>
                    {formatUptime(systemStats.systemUptime)}
                  </span>
                </div>

                <div
                  style={{ display: "flex", justifyContent: "space-between" }}
                >
                  <span>{t("admin.stats.total_documents")}</span>
                  <span style={{ fontWeight: "bold" }}>
                    {systemStats.totalDocuments.toLocaleString()}
                  </span>
                </div>

                <div
                  style={{ display: "flex", justifyContent: "space-between" }}
                >
                  <span>{t("admin.stats.uptime_percentage")}</span>
                  <span style={{ fontWeight: "bold", color: "#52c41a" }}>
                    {systemStats.systemUptime.toFixed(2)}%
                  </span>
                </div>
              </Space>
            </Card>
          </Col>
        </Row>
      </ModernCard>
    </div>
  );
};

export default SystemStats;
