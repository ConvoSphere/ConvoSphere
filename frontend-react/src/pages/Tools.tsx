import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useThemeStore } from "../store/themeStore";
import {
  Typography,
  Space,
  Divider,
  Row,
  Col,
  Avatar,
  Tag,
  Spin,
  message,
  Empty,
  Statistic,
  Modal,
  Form,
  Switch,
  Upload,
  Table,
  Alert,
  Badge,
} from "antd";
import {
  PlayCircleOutlined,
  SettingOutlined,
  ToolOutlined,
  ApiOutlined,
  CodeOutlined,
  SearchOutlined,
  CalculatorOutlined,
  FileTextOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ReloadOutlined,
  PlusOutlined,
  UploadOutlined,
  DownloadOutlined,
  InfoCircleOutlined,
  StarOutlined,
  ThunderboltOutlined,
} from "@ant-design/icons";
import { getTools, runTool } from "../services/tools";
import ModernCard from "../components/ModernCard";
import ModernButton from "../components/ModernButton";
import ModernInput from "../components/ModernInput";
import ModernSelect from "../components/ModernSelect";
import ModernForm, { ModernFormItem } from "../components/ModernForm";

const { Title, Text, Paragraph } = Typography;


interface Tool {
  id: number;
  name: string;
  description: string;
  category: string;
  isActive: boolean;
  parameters: ToolParameter[];
  executionTime: number;
  successRate: number;
  lastUsed: string;
  usageCount: number;
  tags: string[];
  version: string;
  author: string;
}

interface ToolParameter {
  name: string;
  type: "string" | "number" | "boolean" | "file" | "select";
  required: boolean;
  description: string;
  defaultValue?: any;
  options?: string[];
}

interface ToolExecution {
  id: string;
  toolId: number;
  toolName: string;
  parameters: Record<string, any>;
  result: any;
  status: "success" | "error" | "running";
  executionTime: number;
  timestamp: string;
  error?: string;
}

const Tools: React.FC = () => {
  const { t } = useTranslation();
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const [tools, setTools] = useState<Tool[]>([]);
  const [executions, setExecutions] = useState<ToolExecution[]>([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [visible, setVisible] = useState(false);
  const [selectedTool, setSelectedTool] = useState<Tool | null>(null);
  const [activeTab, setActiveTab] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [form] = Form.useForm();

  const categories = [
    {
      value: "utility",
      label: t("tools.categories.utility", "Utility"),
      icon: <ToolOutlined />,
    },
    {
      value: "api",
      label: t("tools.categories.api", "API"),
      icon: <ApiOutlined />,
    },
    {
      value: "calculation",
      label: t("tools.categories.calculation", "Calculation"),
      icon: <CalculatorOutlined />,
    },
    {
      value: "file",
      label: t("tools.categories.file", "File"),
      icon: <FileTextOutlined />,
    },
    {
      value: "code",
      label: t("tools.categories.code", "Code"),
      icon: <CodeOutlined />,
    },
  ];

  useEffect(() => {
    loadTools();
  }, []);

  const loadTools = async () => {
    setLoading(true);
    try {
      const toolsData = await getTools();
      setTools(toolsData);

      // Mock execution history
      setExecutions([
        {
          id: "1",
          toolId: 1,
          toolName: "Data Processor",
          parameters: { input: "test.csv" },
          result: { processed: 1000, errors: 0 },
          status: "success",
          executionTime: 2.5,
          timestamp: "2024-01-15T10:30:00Z",
        },
        {
          id: "2",
          toolId: 2,
          toolName: "API Validator",
          parameters: { endpoint: "https://api.example.com" },
          result: { valid: true, responseTime: 150 },
          status: "success",
          executionTime: 0.8,
          timestamp: "2024-01-15T09:15:00Z",
        },
      ]);
    } catch (_error) {
      message.error(t("tools.load_failed", "Fehler beim Laden der Tools"));
    } finally {
      setLoading(false);
    }
  };

  const handleRunTool = async () => {
    if (!selectedTool) return;

    setRunning(true);
    try {
      const values = await form.validateFields();
      const result = await runTool(selectedTool.id, values);

      const newExecution: ToolExecution = {
        id: Date.now().toString(),
        toolId: selectedTool.id,
        toolName: selectedTool.name,
        parameters: values,
        result,
        status: "success",
        executionTime: Math.random() * 5 + 0.5,
        timestamp: new Date().toISOString(),
      };

      setExecutions((prev) => [newExecution, ...prev]);
      setVisible(false);
      form.resetFields();
      message.success(
        t("tools.execution_success", "Tool erfolgreich ausgeführt"),
      );
    } catch (_error) {
      message.error(
        t("tools.execution_failed", "Fehler bei der Tool-Ausführung"),
      );
    } finally {
      setRunning(false);
    }
  };

  const handleToggleActive = async (tool: Tool) => {
    try {
      const updatedTool = { ...tool, isActive: !tool.isActive };
      setTools((prev) => prev.map((t) => (t.id === tool.id ? updatedTool : t)));
      message.success(
        tool.isActive
          ? t("tools.deactivated", "Tool deaktiviert")
          : t("tools.activated", "Tool aktiviert"),
      );
    } catch (_error) {
      message.error(
        t("tools.toggle_failed", "Fehler beim Umschalten des Tools"),
      );
    }
  };

  const openToolModal = (tool: Tool) => {
    setSelectedTool(tool);
    form.resetFields();
    setVisible(true);
  };

  const getCategoryIcon = (category: string) => {
    const cat = categories.find((c) => c.value === category);
    return cat ? cat.icon : <ToolOutlined />;
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "utility":
        return colors.colorPrimary;
      case "api":
        return colors.colorSecondary;
      case "calculation":
        return colors.colorAccent;
      case "file":
        return "#FF6B6B";
      case "code":
        return "#4ECDC4";
      default:
        return colors.colorPrimary;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "success":
        return "success";
      case "error":
        return "error";
      case "running":
        return "processing";
      default:
        return "default";
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
        return <InfoCircleOutlined />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("de-DE", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const filteredTools = tools.filter((tool) => {
    const matchesSearch =
      tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tool.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = activeTab === "all" || tool.category === activeTab;
    return matchesSearch && matchesCategory;
  });

  const stats = {
    total: tools.length,
    active: tools.filter((t) => t.isActive).length,
    totalExecutions: executions.length,
    successRate:
      executions.length > 0
        ? (
            (executions.filter((e) => e.status === "success").length /
              executions.length) *
            100
          ).toFixed(1)
        : "0",
  };

  const executionColumns = [
    {
      title: t("tools.history.tool", "Tool"),
      dataIndex: "toolName",
      key: "toolName",
      render: (name: string) => (
        <Space>
          <ToolOutlined style={{ color: colors.colorPrimary }} />
          <Text strong>{name}</Text>
        </Space>
      ),
    },
    {
      title: t("tools.history.status", "Status"),
      dataIndex: "status",
      key: "status",
      render: (status: string) => (
        <Tag color={getStatusColor(status)} icon={getStatusIcon(status)}>
          {t(`tools.status.${status}`, status)}
        </Tag>
      ),
    },
    {
      title: t("tools.history.execution_time", "Ausführungszeit"),
      dataIndex: "executionTime",
      key: "executionTime",
      render: (time: number) => (
        <Text type="secondary">{time.toFixed(2)}s</Text>
      ),
    },
    {
      title: t("tools.history.timestamp", "Zeitstempel"),
      dataIndex: "timestamp",
      key: "timestamp",
      render: (timestamp: string) => (
        <Text type="secondary" style={{ fontSize: "12px" }}>
          {formatDate(timestamp)}
        </Text>
      ),
    },
  ];

  return (
    <div
      style={{
        minHeight: "100vh",
        background: colors.colorGradientPrimary,
        padding: "24px",
      }}
    >
      <div style={{ maxWidth: 1400, margin: "0 auto" }}>
        {/* Header Section */}
        <ModernCard variant="gradient" size="lg" className="stagger-children">
          <div style={{ textAlign: "center", padding: "32px 0" }}>
            <div
              style={{
                width: 80,
                height: 80,
                borderRadius: "50%",
                backgroundColor: "rgba(255, 255, 255, 0.2)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto 24px",
                fontSize: "32px",
              }}
            >
              ⚡
            </div>
            <Title
              level={1}
              style={{ color: "#FFFFFF", marginBottom: 8, fontSize: "2.5rem" }}
            >
              {t("tools.title", "Tools")}
            </Title>
            <Text
              style={{ fontSize: "18px", color: "rgba(255, 255, 255, 0.9)" }}
            >
              {t("tools.subtitle", "Verwalten und ausführen Sie Ihre Tools")}
            </Text>
          </div>
        </ModernCard>

        <div style={{ marginTop: 32 }}>
          <Row gutter={[24, 24]}>
            {/* Main Content */}
            <Col xs={24} lg={16}>
              <div
                style={{ display: "flex", flexDirection: "column", gap: 24 }}
              >
                {/* Search and Filters */}
                <ModernCard variant="elevated" size="md">
                  <Row gutter={[16, 16]} align="middle">
                    <Col xs={24} md={12}>
                      <ModernInput
                        placeholder={t(
                          "tools.search_placeholder",
                          "Tools durchsuchen...",
                        )}
                        prefix={
                          <SearchOutlined
                            style={{ color: colors.colorTextSecondary }}
                          />
                        }
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        allowClear
                      />
                    </Col>

                    <Col xs={24} md={12}>
                      <div
                        style={{ display: "flex", gap: 8, flexWrap: "wrap" }}
                      >
                        <ModernButton
                          variant={activeTab === "all" ? "primary" : "outlined"}
                          size="sm"
                          onClick={() => setActiveTab("all")}
                        >
                          {t("tools.categories.all", "Alle")}
                        </ModernButton>
                        {categories.map((category) => (
                          <ModernButton
                            key={category.value}
                            variant={
                              activeTab === category.value
                                ? "primary"
                                : "outlined"
                            }
                            size="sm"
                            icon={category.icon}
                            onClick={() => setActiveTab(category.value)}
                          >
                            {category.label}
                          </ModernButton>
                        ))}
                      </div>
                    </Col>
                  </Row>
                </ModernCard>

                {/* Tools Grid */}
                <ModernCard
                  variant="elevated"
                  size="lg"
                  header={
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                      }}
                    >
                      <Title level={3} style={{ margin: 0 }}>
                        {t("tools.available_tools", "Verfügbare Tools")}
                      </Title>
                      <ModernButton
                        variant="primary"
                        size="md"
                        icon={<PlusOutlined />}
                        onClick={() =>
                          message.info(t("tools.add_tool", "Tool hinzufügen"))
                        }
                      >
                        {t("tools.add", "Hinzufügen")}
                      </ModernButton>
                    </div>
                  }
                >
                  {loading ? (
                    <div style={{ textAlign: "center", padding: "48px" }}>
                      <Spin size="large" />
                    </div>
                  ) : filteredTools.length === 0 ? (
                    <Empty
                      description={t("tools.no_tools", "Keine Tools gefunden")}
                      style={{ padding: "48px 0" }}
                    />
                  ) : (
                    <div className="modern-card-grid" style={{ gap: 16 }}>
                      {filteredTools.map((tool) => (
                        <ModernCard
                          key={tool.id}
                          variant="interactive"
                          size="md"
                          hoverable
                          style={{ cursor: "pointer" }}
                          onClick={() => openToolModal(tool)}
                        >
                          <div
                            style={{
                              display: "flex",
                              alignItems: "flex-start",
                              gap: 16,
                            }}
                          >
                            <Avatar
                              size={48}
                              icon={getCategoryIcon(tool.category)}
                              style={{
                                backgroundColor: getCategoryColor(
                                  tool.category,
                                ),
                                color: "#FFFFFF",
                              }}
                            />

                            <div style={{ flex: 1, minWidth: 0 }}>
                              <div
                                style={{
                                  display: "flex",
                                  justifyContent: "space-between",
                                  alignItems: "flex-start",
                                  marginBottom: 8,
                                }}
                              >
                                <Title
                                  level={5}
                                  style={{ margin: 0, fontSize: "16px" }}
                                >
                                  {tool.name}
                                </Title>
                                <div
                                  style={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 8,
                                  }}
                                >
                                  <Tag
                                    color={tool.isActive ? "green" : "orange"}
                                    size="small"
                                  >
                                    {tool.isActive
                                      ? t("tools.active", "Aktiv")
                                      : t("tools.inactive", "Inaktiv")}
                                  </Tag>
                                  <Badge count={tool.usageCount} size="small" />
                                </div>
                              </div>

                              <Paragraph
                                ellipsis={{ rows: 2 }}
                                style={{
                                  margin: 0,
                                  color: colors.colorTextSecondary,
                                  fontSize: "14px",
                                }}
                              >
                                {tool.description}
                              </Paragraph>

                              <div
                                style={{
                                  display: "flex",
                                  alignItems: "center",
                                  gap: 16,
                                  marginTop: 12,
                                }}
                              >
                                <Text
                                  type="secondary"
                                  style={{ fontSize: "12px" }}
                                >
                                  <ClockCircleOutlined
                                    style={{ marginRight: 4 }}
                                  />
                                  {tool.executionTime.toFixed(2)}s
                                </Text>
                                <Text
                                  type="secondary"
                                  style={{ fontSize: "12px" }}
                                >
                                  <CheckCircleOutlined
                                    style={{ marginRight: 4 }}
                                  />
                                  {tool.successRate}%
                                </Text>
                                <Text
                                  type="secondary"
                                  style={{ fontSize: "12px" }}
                                >
                                  <StarOutlined style={{ marginRight: 4 }} />v
                                  {tool.version}
                                </Text>
                              </div>

                              <div
                                style={{
                                  display: "flex",
                                  alignItems: "center",
                                  gap: 8,
                                  marginTop: 12,
                                }}
                              >
                                {tool.tags.slice(0, 3).map((tag, index) => (
                                  <Tag
                                    key={index}
                                    size="small"
                                    style={{ fontSize: "10px" }}
                                  >
                                    {tag}
                                  </Tag>
                                ))}
                                {tool.tags.length > 3 && (
                                  <Tag
                                    size="small"
                                    style={{ fontSize: "10px" }}
                                  >
                                    +{tool.tags.length - 3}
                                  </Tag>
                                )}
                              </div>
                            </div>

                            <div
                              style={{
                                display: "flex",
                                flexDirection: "column",
                                gap: 8,
                              }}
                            >
                              <ModernButton
                                variant="primary"
                                size="sm"
                                icon={<PlayCircleOutlined />}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  openToolModal(tool);
                                }}
                              />
                              <ModernButton
                                variant="secondary"
                                size="sm"
                                icon={<SettingOutlined />}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleToggleActive(tool);
                                }}
                              />
                            </div>
                          </div>
                        </ModernCard>
                      ))}
                    </div>
                  )}
                </ModernCard>

                {/* Execution History */}
                <ModernCard
                  variant="elevated"
                  size="lg"
                  header={
                    <Title level={3} style={{ margin: 0 }}>
                      {t("tools.execution_history", "Ausführungsverlauf")}
                    </Title>
                  }
                >
                  <Table
                    dataSource={executions}
                    columns={executionColumns}
                    rowKey="id"
                    pagination={{
                      pageSize: 10,
                      showSizeChanger: true,
                      showQuickJumper: true,
                      showTotal: (total, range) =>
                        t(
                          "tools.table.showing",
                          "{{start}}-{{end}} von {{total}} Einträgen",
                          {
                            start: range[0],
                            end: range[1],
                            total,
                          },
                        ),
                    }}
                    scroll={{ x: 800 }}
                  />
                </ModernCard>
              </div>
            </Col>

            {/* Sidebar */}
            <Col xs={24} lg={8}>
              <div
                style={{ display: "flex", flexDirection: "column", gap: 24 }}
              >
                {/* Statistics */}
                <ModernCard variant="interactive" size="md">
                  <Title level={4} style={{ marginBottom: 24 }}>
                    {t("tools.statistics", "Statistiken")}
                  </Title>

                  <Space
                    direction="vertical"
                    size="large"
                    style={{ width: "100%" }}
                  >
                    <Statistic
                      title={t("tools.stats.total_tools", "Gesamt Tools")}
                      value={stats.total}
                      prefix={
                        <ToolOutlined style={{ color: colors.colorPrimary }} />
                      }
                      valueStyle={{
                        color: colors.colorPrimary,
                        fontSize: "1.5rem",
                      }}
                    />

                    <Divider style={{ margin: "16px 0" }} />

                    <Statistic
                      title={t("tools.stats.active_tools", "Aktive Tools")}
                      value={stats.active}
                      prefix={
                        <ThunderboltOutlined
                          style={{ color: colors.colorSecondary }}
                        />
                      }
                      valueStyle={{
                        color: colors.colorSecondary,
                        fontSize: "1.2rem",
                      }}
                    />

                    <Statistic
                      title={t("tools.stats.total_executions", "Ausführungen")}
                      value={stats.totalExecutions}
                      prefix={
                        <PlayCircleOutlined
                          style={{ color: colors.colorAccent }}
                        />
                      }
                      valueStyle={{
                        color: colors.colorAccent,
                        fontSize: "1.2rem",
                      }}
                    />

                    <Statistic
                      title={t("tools.stats.success_rate", "Erfolgsrate")}
                      value={stats.successRate}
                      suffix="%"
                      prefix={
                        <CheckCircleOutlined style={{ color: "#52C41A" }} />
                      }
                      valueStyle={{ color: "#52C41A", fontSize: "1.2rem" }}
                    />
                  </Space>
                </ModernCard>

                {/* Quick Actions */}
                <ModernCard variant="outlined" size="md">
                  <Title level={4} style={{ marginBottom: 16 }}>
                    {t("tools.quick_actions", "Schnellaktionen")}
                  </Title>

                  <Space
                    direction="vertical"
                    size="small"
                    style={{ width: "100%" }}
                  >
                    <ModernButton
                      variant="primary"
                      size="md"
                      icon={<PlusOutlined />}
                      style={{ width: "100%", justifyContent: "flex-start" }}
                    >
                      {t("tools.add_new_tool", "Neues Tool hinzufügen")}
                    </ModernButton>

                    <ModernButton
                      variant="secondary"
                      size="md"
                      icon={<UploadOutlined />}
                      style={{ width: "100%", justifyContent: "flex-start" }}
                    >
                      {t("tools.import_tools", "Tools importieren")}
                    </ModernButton>

                    <ModernButton
                      variant="secondary"
                      size="md"
                      icon={<DownloadOutlined />}
                      style={{ width: "100%", justifyContent: "flex-start" }}
                    >
                      {t("tools.export_tools", "Tools exportieren")}
                    </ModernButton>

                    <ModernButton
                      variant="secondary"
                      size="md"
                      icon={<ReloadOutlined />}
                      onClick={loadTools}
                      style={{ width: "100%", justifyContent: "flex-start" }}
                    >
                      {t("tools.refresh", "Aktualisieren")}
                    </ModernButton>
                  </Space>
                </ModernCard>

                {/* Category Overview */}
                <ModernCard variant="outlined" size="md">
                  <Title level={4} style={{ marginBottom: 16 }}>
                    {t("tools.categories", "Kategorien")}
                  </Title>

                  <Space
                    direction="vertical"
                    size="small"
                    style={{ width: "100%" }}
                  >
                    {categories.map((category) => {
                      const count = tools.filter(
                        (t) => t.category === category.value,
                      ).length;
                      return (
                        <div
                          key={category.value}
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            padding: "12px",
                            backgroundColor: colors.colorBgContainer,
                            borderRadius: "8px",
                            cursor: "pointer",
                          }}
                          onClick={() => setActiveTab(category.value)}
                        >
                          <div
                            style={{
                              display: "flex",
                              alignItems: "center",
                              gap: 8,
                            }}
                          >
                            <span
                              style={{
                                color: getCategoryColor(category.value),
                              }}
                            >
                              {category.icon}
                            </span>
                            <Text>{category.label}</Text>
                          </div>
                          <Badge count={count} size="small" />
                        </div>
                      );
                    })}
                  </Space>
                </ModernCard>
              </div>
            </Col>
          </Row>
        </div>

        {/* Tool Execution Modal */}
        <Modal
          title={
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <PlayCircleOutlined style={{ color: colors.colorPrimary }} />
              {selectedTool
                ? t("tools.run_tool", "Tool ausführen: {{name}}", {
                    name: selectedTool.name,
                  })
                : t("tools.run_tool", "Tool ausführen")}
            </div>
          }
          open={visible}
          onCancel={() => {
            setVisible(false);
            setSelectedTool(null);
            form.resetFields();
          }}
          footer={null}
          width={600}
          style={{ top: 20 }}
        >
          {selectedTool && (
            <div style={{ marginBottom: 24 }}>
              <Alert
                message={selectedTool.name}
                description={selectedTool.description}
                type="info"
                showIcon
                style={{ marginBottom: 16 }}
              />

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 16,
                  marginBottom: 16,
                }}
              >
                <Tag color={getCategoryColor(selectedTool.category)}>
                  {
                    categories.find((c) => c.value === selectedTool.category)
                      ?.label
                  }
                </Tag>
                <Text type="secondary">
                  <ClockCircleOutlined style={{ marginRight: 4 }} />
                  {selectedTool.executionTime.toFixed(2)}s
                </Text>
                <Text type="secondary">
                  <CheckCircleOutlined style={{ marginRight: 4 }} />
                  {selectedTool.successRate}% Erfolgsrate
                </Text>
              </div>
            </div>
          )}

          <ModernForm form={form} layout="vertical" onFinish={handleRunTool}>
            {selectedTool?.parameters.map((param) => (
              <ModernFormItem
                key={param.name}
                name={param.name}
                label={param.name}
                rules={[
                  ...(param.required
                    ? [
                        {
                          required: true,
                          message: t(
                            "tools.parameter_required",
                            "Parameter ist erforderlich",
                          ),
                        },
                      ]
                    : []),
                ]}
                extra={param.description}
              >
                {param.type === "string" && (
                  <ModernInput
                    placeholder={t(
                      "tools.parameter_placeholder",
                      "Wert eingeben",
                    )}
                    defaultValue={param.defaultValue}
                  />
                )}
                {param.type === "number" && (
                  <ModernInput
                    type="number"
                    placeholder={t(
                      "tools.parameter_placeholder",
                      "Wert eingeben",
                    )}
                    defaultValue={param.defaultValue}
                  />
                )}
                {param.type === "boolean" && (
                  <Switch defaultChecked={param.defaultValue} />
                )}
                {param.type === "select" && (
                  <ModernSelect
                    placeholder={t("tools.select_option", "Option auswählen")}
                    defaultValue={param.defaultValue}
                  >
                    {param.options?.map((option) => (
                      <ModernSelect.Option key={option} value={option}>
                        {option}
                      </ModernSelect.Option>
                    ))}
                  </ModernSelect>
                )}
                {param.type === "file" && (
                  <Upload>
                    <ModernButton icon={<UploadOutlined />}>
                      {t("tools.upload_file", "Datei hochladen")}
                    </ModernButton>
                  </Upload>
                )}
              </ModernFormItem>
            ))}

            <div style={{ display: "flex", gap: 12, marginTop: 24 }}>
              <ModernButton
                variant="primary"
                size="lg"
                icon={<PlayCircleOutlined />}
                htmlType="submit"
                loading={running}
                style={{ flex: 1 }}
              >
                {t("tools.run", "Ausführen")}
              </ModernButton>

              <ModernButton
                variant="outlined"
                size="lg"
                onClick={() => {
                  setVisible(false);
                  setSelectedTool(null);
                  form.resetFields();
                }}
                style={{ flex: 1 }}
              >
                {t("tools.cancel", "Abbrechen")}
              </ModernButton>
            </div>
          </ModernForm>
        </Modal>
      </div>
    </div>
  );
};

export default Tools;
