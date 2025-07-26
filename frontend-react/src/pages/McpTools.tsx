import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  Row,
  Col,
  Space,
  Typography,
  Modal,
  message,
  Spin,
  Avatar,
  Tag,
  Empty,
} from "antd";
import { getMcpTools, runMcpTool } from "../services/mcpTools";
import { useThemeStore } from "../store/themeStore";
import ModernCard from "../components/ModernCard";
import ModernButton from "../components/ModernButton";
import ModernInput from "../components/ModernInput";
import ModernForm, { ModernFormItem } from "../components/ModernForm";
import {
  ToolOutlined,
  PlayCircleOutlined,
  SettingOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  ReloadOutlined,
  HistoryOutlined,
  ThunderboltOutlined,
  CodeOutlined,
  ApiOutlined,
  DatabaseOutlined,
} from "@ant-design/icons";

const { Title, Text, Paragraph } = Typography;

interface McpTool {
  id: number;
  name: string;
  description: string;
}

interface ToolExecution {
  id: string;
  toolName: string;
  status: "success" | "error" | "running";
  timestamp: Date;
  duration?: number;
  output?: string;
}

const McpTools: React.FC = () => {
  const { t } = useTranslation();
  const { colors } = useThemeStore();
  const [tools, setTools] = useState<McpTool[]>([]);
  const [selected, setSelected] = useState<McpTool | null>(null);
  const [visible, setVisible] = useState(false);
  const [param, setParam] = useState("");
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [executionHistory, setExecutionHistory] = useState<ToolExecution[]>([]);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    getMcpTools()
      .then(setTools)
      .catch(() => message.error(t("mcp_tools.load_failed")))
      .finally(() => setLoading(false));
  }, []);

  const handleRun = async () => {
    if (!selected) return;
    setRunning(true);

    const execution: ToolExecution = {
      id: Date.now().toString(),
      toolName: selected.name,
      status: "running",
      timestamp: new Date(),
    };

    setExecutionHistory((prev) => [execution, ...prev.slice(0, 9)]);

    try {
      const startTime = Date.now();
      const result = await runMcpTool(selected.id, { param });
      const duration = Date.now() - startTime;

      // Update execution history
      setExecutionHistory((prev) =>
        prev.map((exec) =>
          exec.id === execution.id
            ? { ...exec, status: "success", duration, output: result.output }
            : exec,
        ),
      );

      message.success(
        `${t("mcp_tools.result")}: ${result.output || t("mcp_tools.success")}`,
      );
      setVisible(false);
      setParam("");
    } catch {
      // Update execution history with error
      setExecutionHistory((prev) =>
        prev.map((exec) =>
          exec.id === execution.id ? { ...exec, status: "error" } : exec,
        ),
      );

      message.error(t("mcp_tools.execution_failed"));
    } finally {
      setRunning(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "success":
        return colors.colorSuccess;
      case "error":
        return colors.colorError;
      case "running":
        return colors.colorWarning;
      default:
        return colors.colorTextSecondary;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "success":
        return <CheckCircleOutlined />;
      case "error":
        return <ExclamationCircleOutlined />;
      case "running":
        return <ClockCircleOutlined />;
      default:
        return <ClockCircleOutlined />;
    }
  };

  const getToolIcon = (toolName: string) => {
    const name = toolName.toLowerCase();
    if (name.includes("api")) return <ApiOutlined />;
    if (name.includes("database") || name.includes("db"))
      return <DatabaseOutlined />;
    if (name.includes("code")) return <CodeOutlined />;
    return <ToolOutlined />;
  };

  const filteredTools = tools.filter(
    (tool) =>
      tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tool.description.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  const renderToolCard = (tool: McpTool) => (
    <ModernCard key={tool.id} variant="interactive" size="md">
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <Avatar
          icon={getToolIcon(tool.name)}
          size="large"
          style={{ backgroundColor: colors.colorPrimary }}
        />
        <div style={{ flex: 1 }}>
          <Title level={5} style={{ margin: 0 }}>
            {tool.name}
          </Title>
          <Text type="secondary" style={{ fontSize: "14px" }}>
            {tool.description}
          </Text>
        </div>
        <ModernButton
          variant="primary"
          icon={<PlayCircleOutlined />}
          onClick={() => {
            setSelected(tool);
            setVisible(true);
          }}
        >
          {t("common.run")}
        </ModernButton>
      </div>
    </ModernCard>
  );

  const renderExecutionHistory = () => (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      {executionHistory.length === 0 ? (
        <Empty description={t("mcp_tools.no_executions")} size="small" />
      ) : (
        executionHistory.map((exec) => (
          <ModernCard key={exec.id} variant="outlined" size="sm">
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <div style={{ color: getStatusColor(exec.status) }}>
                  {getStatusIcon(exec.status)}
                </div>
                <Text strong style={{ fontSize: "14px" }}>
                  {exec.toolName}
                </Text>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                {exec.duration && (
                  <Text type="secondary" style={{ fontSize: "12px" }}>
                    {exec.duration}ms
                  </Text>
                )}
                <Text type="secondary" style={{ fontSize: "12px" }}>
                  {exec.timestamp.toLocaleTimeString()}
                </Text>
              </div>
            </div>
          </ModernCard>
        ))
      )}
    </div>
  );

  return (
    <div
      style={{
        minHeight: "100vh",
        background: colors.colorGradientPrimary,
        padding: "24px",
      }}
    >
      <div style={{ maxWidth: 1400, margin: "0 auto" }}>
        <ModernCard variant="gradient" size="lg" className="stagger-children">
          <div style={{ textAlign: "center", padding: "32px 0" }}>
            <div
              style={{
                fontSize: "48px",
                marginBottom: "16px",
                filter: "drop-shadow(0 4px 8px rgba(0,0,0,0.1))",
              }}
            >
              ⚙️
            </div>
            <Title level={1} style={{ color: "#FFFFFF", margin: 0 }}>
              {t("mcp_tools.title")}
            </Title>
            <Text style={{ color: "rgba(255,255,255,0.8)", fontSize: "16px" }}>
              {t("mcp_tools.subtitle")}
            </Text>
          </div>
        </ModernCard>

        <Row gutter={[24, 24]} style={{ marginTop: 32 }}>
          <Col xs={24} lg={16}>
            <ModernCard
              variant="elevated"
              size="md"
              style={{ marginBottom: 24 }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                <ModernInput
                  placeholder={t("mcp_tools.search_placeholder")}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  prefix={<ToolOutlined />}
                  style={{ flex: 1 }}
                />
                <ModernButton
                  variant="outlined"
                  icon={<ReloadOutlined />}
                  onClick={() => {
                    setLoading(true);
                    getMcpTools()
                      .then(setTools)
                      .catch(() => message.error(t("mcp_tools.load_failed")))
                      .finally(() => setLoading(false));
                  }}
                >
                  {t("common.refresh")}
                </ModernButton>
              </div>
            </ModernCard>

            <ModernCard variant="elevated" size="lg">
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: 24,
                }}
              >
                <Title level={3} style={{ margin: 0 }}>
                  <ToolOutlined
                    style={{ marginRight: 8, color: colors.colorPrimary }}
                  />
                  {t("mcp_tools.available_tools")}
                </Title>
                <Tag color="blue">
                  {filteredTools.length} {t("mcp_tools.tools")}
                </Tag>
              </div>

              {loading ? (
                <div style={{ textAlign: "center", padding: "40px" }}>
                  <Spin size="large" />
                  <Text style={{ display: "block", marginTop: 16 }}>
                    {t("mcp_tools.loading")}
                  </Text>
                </div>
              ) : filteredTools.length === 0 ? (
                <Empty
                  description={
                    searchQuery
                      ? t("mcp_tools.no_results")
                      : t("mcp_tools.no_tools")
                  }
                  style={{ padding: "40px 0" }}
                />
              ) : (
                <div
                  style={{ display: "flex", flexDirection: "column", gap: 16 }}
                >
                  {filteredTools.map(renderToolCard)}
                </div>
              )}
            </ModernCard>
          </Col>

          <Col xs={24} lg={8}>
            <ModernCard
              variant="interactive"
              size="md"
              style={{ marginBottom: 24 }}
            >
              <Title level={4}>
                <ThunderboltOutlined
                  style={{ marginRight: 8, color: colors.colorPrimary }}
                />
                {t("mcp_tools.quick_stats")}
              </Title>
              <div
                style={{ display: "flex", flexDirection: "column", gap: 16 }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <Text>{t("mcp_tools.stats.total_tools")}</Text>
                  <Text strong style={{ color: colors.colorPrimary }}>
                    {tools.length}
                  </Text>
                </div>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <Text>{t("mcp_tools.stats.successful_executions")}</Text>
                  <Text strong style={{ color: colors.colorSuccess }}>
                    {
                      executionHistory.filter(
                        (exec) => exec.status === "success",
                      ).length
                    }
                  </Text>
                </div>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <Text>{t("mcp_tools.stats.failed_executions")}</Text>
                  <Text strong style={{ color: colors.colorError }}>
                    {
                      executionHistory.filter((exec) => exec.status === "error")
                        .length
                    }
                  </Text>
                </div>
              </div>
            </ModernCard>

            <ModernCard
              variant="outlined"
              size="md"
              style={{ marginBottom: 24 }}
            >
              <Title level={4}>
                <SettingOutlined
                  style={{ marginRight: 8, color: colors.colorPrimary }}
                />
                {t("mcp_tools.quick_actions")}
              </Title>
              <div
                style={{ display: "flex", flexDirection: "column", gap: 12 }}
              >
                <ModernButton variant="primary" icon={<ToolOutlined />} block>
                  {t("mcp_tools.actions.scan_tools")}
                </ModernButton>
                <ModernButton
                  variant="secondary"
                  icon={<HistoryOutlined />}
                  block
                >
                  {t("mcp_tools.actions.view_history")}
                </ModernButton>
                <ModernButton
                  variant="outlined"
                  icon={<ReloadOutlined />}
                  block
                >
                  {t("mcp_tools.actions.refresh_cache")}
                </ModernButton>
              </div>
            </ModernCard>

            <ModernCard variant="elevated" size="md">
              <Title level={4}>
                <HistoryOutlined
                  style={{ marginRight: 8, color: colors.colorPrimary }}
                />
                {t("mcp_tools.recent_executions")}
              </Title>
              {renderExecutionHistory()}
            </ModernCard>
          </Col>
        </Row>
      </div>

      <Modal
        title={
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <ThunderboltOutlined style={{ color: colors.colorPrimary }} />
            {selected?.name}
          </div>
        }
        open={visible}
        onCancel={() => setVisible(false)}
        footer={null}
        width={600}
      >
        <div style={{ marginBottom: 24 }}>
          <Paragraph type="secondary">{selected?.description}</Paragraph>
        </div>

        <ModernForm layout="vertical" onFinish={handleRun}>
          <ModernFormItem label={t("mcp_tools.parameter_label")} required>
            <ModernInput
              value={param}
              onChange={(e) => setParam(e.target.value)}
              placeholder={t("mcp_tools.parameter_placeholder")}
              size="large"
            />
          </ModernFormItem>

          <div
            style={{
              display: "flex",
              gap: 12,
              justifyContent: "flex-end",
              marginTop: 24,
            }}
          >
            <ModernButton variant="outlined" onClick={() => setVisible(false)}>
              {t("common.cancel")}
            </ModernButton>
            <ModernButton
              variant="primary"
              icon={<PlayCircleOutlined />}
              htmlType="submit"
              loading={running}
            >
              {t("common.run")}
            </ModernButton>
          </div>
        </ModernForm>
      </Modal>
    </div>
  );
};

export default McpTools;
