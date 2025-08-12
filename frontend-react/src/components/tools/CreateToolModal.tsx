import React, { useState } from "react";
import {
  Modal,
  Form,
  Input,
  Select,
  Switch,
  Button,
  Space,
  Divider,
  Typography,
  message,
} from "antd";
import {
  ToolOutlined,
  CodeOutlined,
  SettingOutlined,
  SaveOutlined,
  CloseOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import ModernForm, { ModernFormItem } from "../ModernForm";
import ModernInput from "../ModernInput";
import ModernSelect from "../ModernSelect";
import ModernButton from "../ModernButton";
import { createTool, type ToolCreate } from "../../services/tools";

const { TextArea } = Input;
const { Option } = Select;
const { Title, Text } = Typography;

interface ToolParameter {
  name: string;
  type: "string" | "number" | "boolean" | "file" | "select";
  required: boolean;
  description: string;
  defaultValue?: any;
  options?: string[];
}

interface CreateToolData {
  name: string;
  description: string;
  category: string;
  version: string;
  function_name: string;
  parameters_schema: ToolParameter[];
  implementation_path: string;
  is_builtin: boolean;
  is_enabled: boolean;
  requires_auth: boolean;
  required_permissions: string[];
  rate_limit: string;
  tags: string[];
  tool_metadata: Record<string, any>;
}

interface CreateToolModalProps {
  visible: boolean;
  onCancel: () => void;
  onSuccess: () => void;
}

const CreateToolModal: React.FC<CreateToolModalProps> = ({
  visible,
  onCancel,
  onSuccess,
}) => {
  const { t } = useTranslation();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [parameters, setParameters] = useState<ToolParameter[]>([]);

  const categories = [
    { value: "utility", label: "Utility", icon: "🔧" },
    { value: "data", label: "Data Processing", icon: "📊" },
    { value: "communication", label: "Communication", icon: "💬" },
    { value: "file", label: "File Operations", icon: "📁" },
    { value: "web", label: "Web Services", icon: "🌐" },
    { value: "ai", label: "AI/ML", icon: "🤖" },
    { value: "custom", label: "Custom", icon: "⚙️" },
  ];

  const parameterTypes = [
    { value: "string", label: "String" },
    { value: "number", label: "Number" },
    { value: "boolean", label: "Boolean" },
    { value: "file", label: "File" },
    { value: "select", label: "Select" },
  ];

  const handleAddParameter = () => {
    const newParameter: ToolParameter = {
      name: "",
      type: "string",
      required: false,
      description: "",
    };
    setParameters([...parameters, newParameter]);
  };

  const handleRemoveParameter = (index: number) => {
    setParameters(parameters.filter((_, i) => i !== index));
  };

  const handleParameterChange = (
    index: number,
    field: keyof ToolParameter,
    value: any,
  ) => {
    const updatedParameters = [...parameters];
    updatedParameters[index] = { ...updatedParameters[index], [field]: value };
    setParameters(updatedParameters);
  };

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      const toolData: ToolCreate = {
        name: values.name,
        description: values.description || "",
        category: values.category,
        version: values.version || "1.0.0",
        function_name: values.function_name,
        parameters_schema: parameters,
        implementation_path: values.implementation_path || "",
        is_builtin: false,
        is_enabled: values.is_enabled !== false,
        requires_auth: values.requires_auth || false,
        required_permissions: values.required_permissions || [],
        rate_limit: values.rate_limit || "",
        tags: values.tags || [],
        tool_metadata: {},
      };

      await createTool(toolData);

      message.success(t("tools.create_success", "Tool created successfully"));
      form.resetFields();
      setParameters([]);
      onSuccess();
    } catch (error) {
      message.error(t("tools.create_error", "Failed to create tool"));
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    form.resetFields();
    setParameters([]);
    onCancel();
  };

  return (
    <Modal
      title={
        <Space>
          <ToolOutlined style={{ color: "#1890ff" }} />
          <Title level={4} style={{ margin: 0 }}>
            {t("tools.create_title", "Create New Tool")}
          </Title>
        </Space>
      }
      open={visible}
      onCancel={handleCancel}
      footer={null}
      width={800}
      destroyOnClose
    >
      <ModernForm
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        style={{ marginTop: 16 }}
      >
        <div
          style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}
        >
          <ModernFormItem
            name="name"
            label={t("tools.name", "Tool Name")}
            rules={[
              {
                required: true,
                message: t("tools.name_required", "Tool name is required"),
              },
            ]}
          >
            <ModernInput
              placeholder={t("tools.name_placeholder", "Enter tool name")}
            />
          </ModernFormItem>

          <ModernFormItem
            name="category"
            label={t("tools.category", "Category")}
            rules={[
              {
                required: true,
                message: t("tools.category_required", "Category is required"),
              },
            ]}
          >
            <ModernSelect
              placeholder={t("tools.category_placeholder", "Select category")}
            >
              {categories.map((category) => (
                <Option key={category.value} value={category.value}>
                  <Space>
                    <span>{category.icon}</span>
                    <span>{category.label}</span>
                  </Space>
                </Option>
              ))}
            </ModernSelect>
          </ModernFormItem>
        </div>

        <ModernFormItem
          name="description"
          label={t("tools.description", "Description")}
        >
          <TextArea
            rows={3}
            placeholder={t(
              "tools.description_placeholder",
              "Enter tool description",
            )}
          />
        </ModernFormItem>

        <div
          style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}
        >
          <ModernFormItem
            name="function_name"
            label={t("tools.function_name", "Function Name")}
            rules={[
              {
                required: true,
                message: t(
                  "tools.function_name_required",
                  "Function name is required",
                ),
              },
            ]}
          >
            <ModernInput
              placeholder={t(
                "tools.function_name_placeholder",
                "Enter function name",
              )}
            />
          </ModernFormItem>

          <ModernFormItem
            name="version"
            label={t("tools.version", "Version")}
            initialValue="1.0.0"
          >
            <ModernInput placeholder="1.0.0" />
          </ModernFormItem>
        </div>

        <ModernFormItem
          name="implementation_path"
          label={t("tools.implementation_path", "Implementation Path")}
        >
          <ModernInput
            placeholder={t(
              "tools.implementation_path_placeholder",
              "Path to implementation file",
            )}
          />
        </ModernFormItem>

        <Divider>
          <Space>
            <SettingOutlined />
            <Text strong>{t("tools.parameters", "Parameters")}</Text>
          </Space>
        </Divider>

        {parameters.map((param, index) => (
          <div
            key={index}
            style={{
              border: "1px solid #d9d9d9",
              borderRadius: 8,
              padding: 16,
              marginBottom: 16,
            }}
          >
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr 1fr auto",
                gap: 16,
                alignItems: "end",
              }}
            >
              <ModernInput
                placeholder={t("tools.parameter_name", "Parameter name")}
                value={param.name}
                onChange={(e) =>
                  handleParameterChange(index, "name", e.target.value)
                }
              />

              <ModernSelect
                value={param.type}
                onChange={(value) =>
                  handleParameterChange(index, "type", value)
                }
              >
                {parameterTypes.map((type) => (
                  <Option key={type.value} value={type.value}>
                    {type.label}
                  </Option>
                ))}
              </ModernSelect>

              <Switch
                checked={param.required}
                onChange={(checked) =>
                  handleParameterChange(index, "required", checked)
                }
                checkedChildren={t("tools.required", "Required")}
                unCheckedChildren={t("tools.optional", "Optional")}
              />

              <ModernButton
                variant="text"
                danger
                icon={<CloseOutlined />}
                onClick={() => handleRemoveParameter(index)}
              />
            </div>

            <div style={{ marginTop: 12 }}>
              <TextArea
                placeholder={t(
                  "tools.parameter_description",
                  "Parameter description",
                )}
                value={param.description}
                onChange={(e) =>
                  handleParameterChange(index, "description", e.target.value)
                }
                rows={2}
              />
            </div>
          </div>
        ))}

        <ModernButton
          variant="outlined"
          icon={<CodeOutlined />}
          onClick={handleAddParameter}
          style={{ marginBottom: 24 }}
        >
          {t("tools.add_parameter", "Add Parameter")}
        </ModernButton>

        <Divider>
          <Space>
            <SettingOutlined />
            <Text strong>{t("tools.settings", "Settings")}</Text>
          </Space>
        </Divider>

        <div
          style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}
        >
          <ModernFormItem
            name="is_enabled"
            label={t("tools.enabled", "Enabled")}
            initialValue={true}
          >
            <Switch />
          </ModernFormItem>

          <ModernFormItem
            name="requires_auth"
            label={t("tools.requires_auth", "Requires Authentication")}
            initialValue={false}
          >
            <Switch />
          </ModernFormItem>
        </div>

        <ModernFormItem
          name="rate_limit"
          label={t("tools.rate_limit", "Rate Limit")}
        >
          <ModernInput placeholder="100/hour" />
        </ModernFormItem>

        <ModernFormItem name="tags" label={t("tools.tags", "Tags")}>
          <ModernSelect
            mode="tags"
            placeholder={t("tools.tags_placeholder", "Add tags")}
          />
        </ModernFormItem>

        <div
          style={{
            display: "flex",
            justifyContent: "flex-end",
            gap: 12,
            marginTop: 24,
          }}
        >
          <ModernButton variant="outlined" onClick={handleCancel}>
            {t("common.cancel", "Cancel")}
          </ModernButton>
          <ModernButton
            variant="primary"
            icon={<SaveOutlined />}
            loading={loading}
            htmlType="submit"
          >
            {t("tools.create", "Create Tool")}
          </ModernButton>
        </div>
      </ModernForm>
    </Modal>
  );
};

export default CreateToolModal;
