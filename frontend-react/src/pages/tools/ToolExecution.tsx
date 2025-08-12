import React from "react";
import {
  Modal,
  Alert,
  Typography,
  Space,
  Tag,
  Table,
  Form,
  Switch,
  Upload,
} from "antd";
import {
  PlayCircleOutlined,
  ToolOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined,
  UploadOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import ModernCard from "../../components/ModernCard";
import ModernButton from "../../components/ModernButton";
import ModernForm, { ModernFormItem } from "../../components/ModernForm";
import ModernInput from "../../components/ModernInput";
import ModernSelect from "../../components/ModernSelect";
import { useThemeStore } from "../../store/themeStore";
import type { Tool, ToolExecution, ToolParameter } from "./types/tools.types";

const { Title, Text } = Typography;

interface ToolExecutionProps {
  executions: ToolExecution[];
  selectedTool: Tool | null;
  visible: boolean;
  running: boolean;
  onClose: () => void;
  onRunTool: (tool: Tool, parameters: Record<string, any>) => Promise<void>;
  onToolSelect: (tool: Tool) => void;
}

const ToolExecution: React.FC<ToolExecutionProps> = ({
  executions,
  selectedTool,
  visible,
  running,
  onClose,
  onRunTool,
  onToolSelect,
}) => {
  const { t } = useTranslation();
  const { colors } = useThemeStore();
  const [form] = Form.useForm();

  const categories = [
    { value: "utility", label: t("tools.categories.utility", "Utility") },
    { value: "api", label: t("tools.categories.api", "API") },
    {
      value: "calculation",
      label: t("tools.categories.calculation", "Calculation"),
    },
    { value: "file", label: t("tools.categories.file", "File") },
    { value: "code", label: t("tools.categories.code", "Code") },
  ];

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

  const handleRunTool = async () => {
    if (!selectedTool) return;

    try {
      const values = await form.validateFields();
      await onRunTool(selectedTool, values);
      form.resetFields();
    } catch (error) {
      // Form validation error - handled by form
    }
  };

  const handleClose = () => {
    form.resetFields();
    onClose();
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

  const renderParameterInput = (param: ToolParameter) => {
    switch (param.type) {
      case "string":
        return (
          <ModernInput
            placeholder={t("tools.parameter_placeholder", "Wert eingeben")}
            defaultValue={param.defaultValue}
          />
        );
      case "number":
        return (
          <ModernInput
            type="number"
            placeholder={t("tools.parameter_placeholder", "Wert eingeben")}
            defaultValue={param.defaultValue}
          />
        );
      case "boolean":
        return <Switch defaultChecked={param.defaultValue} />;
      case "select":
        return (
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
        );
      case "file":
        return (
          <Upload>
            <ModernButton icon={<UploadOutlined />}>
              {t("tools.upload_file", "Datei hochladen")}
            </ModernButton>
          </Upload>
        );
      default:
        return (
          <ModernInput
            placeholder={t("tools.parameter_placeholder", "Wert eingeben")}
            defaultValue={param.defaultValue}
          />
        );
    }
  };

  return (
    <>
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
        onCancel={handleClose}
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
              {renderParameterInput(param)}
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
              onClick={handleClose}
              style={{ flex: 1 }}
            >
              {t("tools.cancel", "Abbrechen")}
            </ModernButton>
          </div>
        </ModernForm>
      </Modal>
    </>
  );
};

export default ToolExecution;
