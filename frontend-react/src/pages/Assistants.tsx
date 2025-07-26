import React, { useEffect, useState } from "react";
import {
  Card,
  List,
  Button,
  Modal,
  Input,
  Form,
  message,
  Spin,
  Row,
  Col,
  Tag,
  Space,
  Typography,
  Select,
  Switch,
  Divider,
  Avatar,
  Tooltip,
  Popconfirm,
  Badge,
  Tabs,
  Upload,
  Progress,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  RobotOutlined,
  SettingOutlined,
  BookOutlined,
  ToolOutlined,
  MessageOutlined,
  CopyOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  EyeOutlined,
  UploadOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useThemeStore } from "../store/themeStore";
import {
  getAssistants,
  addAssistant,
  deleteAssistant,
  getDefaultAssistantId,
  setDefaultAssistant,
} from "../services/assistants";

const { Title, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

interface Assistant {
  id: number;
  name: string;
  description: string;
  personality: string;
  model: string;
  temperature: number;
  isActive: boolean;
  knowledgeBaseIds: string[];
  toolIds: string[];
  createdAt: string;
  updatedAt: string;
  usageCount: number;
  avgRating: number;
  tags: string[];
}

interface AssistantFormData {
  name: string;
  description: string;
  personality: string;
  model: string;
  temperature: number;
  isActive: boolean;
  knowledgeBaseIds: string[];
  toolIds: string[];
  tags: string[];
}

const Assistants: React.FC = () => {
  const { t } = useTranslation();
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const [assistants, setAssistants] = useState<Assistant[]>([]);
  const [visible, setVisible] = useState(false);
  const [editingAssistant, setEditingAssistant] = useState<Assistant | null>(
    null,
  );
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [deleting, setDeleting] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState("all");
  const [defaultAssistantId, setDefaultAssistantId] = useState<string | null>(
    null,
  );
  const [settingDefault, setSettingDefault] = useState<string | null>(null);

  // Mock data for demonstration
  const mockAssistants: Assistant[] = [
    {
      id: 1,
      name: "Customer Support Bot",
      description: "AI assistant for customer service and support",
      personality: "Helpful, professional, and patient customer service agent",
      model: "gpt-4",
      temperature: 0.7,
      isActive: true,
      knowledgeBaseIds: ["kb1", "kb2"],
      toolIds: ["tool1", "tool2"],
      createdAt: "2024-01-01T00:00:00Z",
      updatedAt: "2024-01-15T10:30:00Z",
      usageCount: 1250,
      avgRating: 4.8,
      tags: ["support", "customer-service", "helpful"],
    },
    {
      id: 2,
      name: "Technical Advisor",
      description: "Technical expert for complex problem solving",
      personality: "Expert technical advisor with deep knowledge",
      model: "gpt-4-turbo",
      temperature: 0.3,
      isActive: true,
      knowledgeBaseIds: ["kb3"],
      toolIds: ["tool3", "tool4"],
      createdAt: "2024-01-05T00:00:00Z",
      updatedAt: "2024-01-14T15:20:00Z",
      usageCount: 890,
      avgRating: 4.9,
      tags: ["technical", "expert", "problem-solving"],
    },
    {
      id: 3,
      name: "Creative Writer",
      description: "Creative writing assistant for content creation",
      personality: "Creative and imaginative writing partner",
      model: "gpt-4",
      temperature: 0.9,
      isActive: false,
      knowledgeBaseIds: ["kb4"],
      toolIds: ["tool5"],
      createdAt: "2024-01-10T00:00:00Z",
      updatedAt: "2024-01-13T09:15:00Z",
      usageCount: 450,
      avgRating: 4.6,
      tags: ["creative", "writing", "content"],
    },
  ];

  const availableModels = [
    { value: "gpt-4", label: "GPT-4", description: "Most capable model" },
    {
      value: "gpt-4-turbo",
      label: "GPT-4 Turbo",
      description: "Faster and more efficient",
    },
    {
      value: "gpt-3.5-turbo",
      label: "GPT-3.5 Turbo",
      description: "Good balance of speed and capability",
    },
    {
      value: "claude-3-opus",
      label: "Claude 3 Opus",
      description: "Anthropic's most capable model",
    },
    {
      value: "claude-3-sonnet",
      label: "Claude 3 Sonnet",
      description: "Fast and efficient",
    },
  ];

  const availableKnowledgeBases = [
    { id: "kb1", name: "Product Documentation" },
    { id: "kb2", name: "FAQ Database" },
    { id: "kb3", name: "Technical Manuals" },
    { id: "kb4", name: "Creative Writing Guide" },
  ];

  const availableTools = [
    {
      id: "tool1",
      name: "Search Engine",
      description: "Web search capabilities",
    },
    {
      id: "tool2",
      name: "Calculator",
      description: "Mathematical calculations",
    },
    {
      id: "tool3",
      name: "Code Interpreter",
      description: "Code execution and analysis",
    },
    {
      id: "tool4",
      name: "File Manager",
      description: "File system operations",
    },
    {
      id: "tool5",
      name: "Image Generator",
      description: "Create images from text",
    },
  ];

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);

        // Load assistants
        setTimeout(() => {
          setAssistants(mockAssistants);
        }, 1000);

        // Load default assistant ID
        try {
          const defaultData = await getDefaultAssistantId();
          setDefaultAssistantId(defaultData.assistant_id);
        } catch (error) {
          // No default assistant configured yet
          console.log("No default assistant configured");
        }
      } catch (error) {
        message.error(t("assistants.load_failed"));
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [t]);

  const handleAdd = async () => {
    try {
      setAdding(true);
      const values = await form.validateFields();

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      const newAssistant: Assistant = {
        id: Date.now(),
        ...values,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        usageCount: 0,
        avgRating: 0,
        tags: values.tags || [],
      };

      setAssistants((prev) => [...prev, newAssistant]);
      setVisible(false);
      form.resetFields();
      message.success(t("assistants.added_success"));
    } catch (error) {
      message.error(t("assistants.add_failed"));
    } finally {
      setAdding(false);
    }
  };

  const handleEdit = async () => {
    if (!editingAssistant) return;

    try {
      setAdding(true);
      const values = await form.validateFields();

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      const updatedAssistant = {
        ...editingAssistant,
        ...values,
        updatedAt: new Date().toISOString(),
      };

      setAssistants((prev) =>
        prev.map((a) => (a.id === editingAssistant.id ? updatedAssistant : a)),
      );
      setVisible(false);
      setEditingAssistant(null);
      form.resetFields();
      message.success(t("assistants.updated_success"));
    } catch (error) {
      message.error(t("assistants.update_failed"));
    } finally {
      setAdding(false);
    }
  };

  const handleDelete = async (id: number) => {
    setDeleting(id);
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      setAssistants((prev) => prev.filter((a) => a.id !== id));
      message.success(t("assistants.deleted_success"));
    } catch (error) {
      message.error(t("assistants.delete_failed"));
    } finally {
      setDeleting(null);
    }
  };

  const handleToggleActive = async (assistant: Assistant) => {
    try {
      const updatedAssistant = { ...assistant, isActive: !assistant.isActive };
      setAssistants((prev) =>
        prev.map((a) => (a.id === assistant.id ? updatedAssistant : a)),
      );
      message.success(
        assistant.isActive
          ? t("assistants.deactivated")
          : t("assistants.activated"),
      );
    } catch (error) {
      message.error(t("assistants.toggle_failed"));
    }
  };

  const handleSetDefault = async (assistantId: string) => {
    try {
      setSettingDefault(assistantId);
      await setDefaultAssistant(assistantId);
      setDefaultAssistantId(assistantId);
      message.success(t("assistants.default_set_success"));
    } catch (error) {
      message.error(t("assistants.default_set_failed"));
    } finally {
      setSettingDefault(null);
    }
  };

  const openEditModal = (assistant: Assistant) => {
    setEditingAssistant(assistant);
    form.setFieldsValue(assistant);
    setVisible(true);
  };

  const openAddModal = () => {
    setEditingAssistant(null);
    form.resetFields();
    setVisible(true);
  };

  const filteredAssistants = assistants.filter((assistant) => {
    if (activeTab === "all") return true;
    if (activeTab === "active") return assistant.isActive;
    if (activeTab === "inactive") return !assistant.isActive;
    return true;
  });

  const getModelLabel = (modelValue: string) => {
    const model = availableModels.find((m) => m.value === modelValue);
    return model ? model.label : modelValue;
  };

  return (
    <div style={{ padding: "24px 0" }}>
      <div style={{ marginBottom: 24 }}>
        <Title
          level={2}
          style={{ color: colors.colorTextBase, marginBottom: 8 }}
        >
          {t("assistants.title")}
        </Title>
        <Text type="secondary">{t("assistants.subtitle")}</Text>
      </div>

      <Card>
        <div
          style={{
            marginBottom: 16,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <Tabs activeKey={activeTab} onChange={setActiveTab}>
            <TabPane tab={t("assistants.tabs.all")} key="all" />
            <TabPane tab={t("assistants.tabs.active")} key="active" />
            <TabPane tab={t("assistants.tabs.inactive")} key="inactive" />
          </Tabs>

          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={openAddModal}
            style={{ backgroundColor: colors.colorPrimary }}
          >
            {t("assistants.add_new")}
          </Button>
        </div>

        {loading ? (
          <div style={{ textAlign: "center", padding: "40px" }}>
            <Spin size="large" />
          </div>
        ) : (
          <List
            grid={{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 2, xl: 3, xxl: 3 }}
            dataSource={filteredAssistants}
            renderItem={(assistant) => (
              <List.Item>
                <Card
                  hoverable
                  actions={[
                    <Tooltip title={t("assistants.actions.edit")}>
                      <Button
                        type="text"
                        icon={<EditOutlined />}
                        onClick={() => openEditModal(assistant)}
                      />
                    </Tooltip>,
                    <Tooltip
                      title={
                        defaultAssistantId === assistant.id.toString()
                          ? t("assistants.actions.default_set")
                          : t("assistants.actions.set_default")
                      }
                    >
                      <Button
                        type="text"
                        icon={<SettingOutlined />}
                        onClick={() =>
                          handleSetDefault(assistant.id.toString())
                        }
                        loading={settingDefault === assistant.id.toString()}
                        style={{
                          color:
                            defaultAssistantId === assistant.id.toString()
                              ? colors.colorPrimary
                              : undefined,
                        }}
                      />
                    </Tooltip>,
                    <Tooltip
                      title={
                        assistant.isActive
                          ? t("assistants.actions.deactivate")
                          : t("assistants.actions.activate")
                      }
                    >
                      <Button
                        type="text"
                        icon={
                          assistant.isActive ? (
                            <PauseCircleOutlined />
                          ) : (
                            <PlayCircleOutlined />
                          )
                        }
                        onClick={() => handleToggleActive(assistant)}
                      />
                    </Tooltip>,
                    <Tooltip title={t("assistants.actions.delete")}>
                      <Popconfirm
                        title={t("assistants.delete_confirm")}
                        onConfirm={() => handleDelete(assistant.id)}
                        okText={t("common.yes")}
                        cancelText={t("common.no")}
                      >
                        <Button
                          type="text"
                          danger
                          icon={<DeleteOutlined />}
                          loading={deleting === assistant.id}
                        />
                      </Popconfirm>
                    </Tooltip>,
                  ]}
                >
                  <List.Item.Meta
                    avatar={
                      <Badge
                        status={assistant.isActive ? "success" : "default"}
                      >
                        <Avatar
                          size={48}
                          icon={<RobotOutlined />}
                          style={{ backgroundColor: colors.colorPrimary }}
                        />
                      </Badge>
                    }
                    title={
                      <Space>
                        <Text strong>{assistant.name}</Text>
                        <Tag color={assistant.isActive ? "green" : "default"}>
                          {assistant.isActive
                            ? t("assistants.status.active")
                            : t("assistants.status.inactive")}
                        </Tag>
                        {defaultAssistantId === assistant.id.toString() && (
                          <Tag color="gold" icon={<SettingOutlined />}>
                            {t("assistants.status.default")}
                          </Tag>
                        )}
                      </Space>
                    }
                    description={
                      <div>
                        <Text type="secondary">{assistant.description}</Text>
                        <div style={{ marginTop: 8 }}>
                          <Space wrap>
                            <Tag icon={<SettingOutlined />} color="blue">
                              {getModelLabel(assistant.model)}
                            </Tag>
                            <Tag icon={<BookOutlined />} color="purple">
                              {assistant.knowledgeBaseIds.length}{" "}
                              {t("assistants.knowledge_bases")}
                            </Tag>
                            <Tag icon={<ToolOutlined />} color="orange">
                              {assistant.toolIds.length} {t("assistants.tools")}
                            </Tag>
                          </Space>
                        </div>
                        <div style={{ marginTop: 8 }}>
                          <Space>
                            <Text type="secondary">
                              <MessageOutlined /> {assistant.usageCount}{" "}
                              {t("assistants.usage_count")}
                            </Text>
                            <Text type="secondary">
                              ⭐ {assistant.avgRating.toFixed(1)}
                            </Text>
                          </Space>
                        </div>
                      </div>
                    }
                  />

                  <div style={{ marginTop: 12 }}>
                    <Space wrap>
                      {assistant.tags.map((tag) => (
                        <Tag key={tag}>{tag}</Tag>
                      ))}
                    </Space>
                  </div>
                </Card>
              </List.Item>
            )}
          />
        )}
      </Card>

      <Modal
        open={visible}
        title={
          editingAssistant
            ? t("assistants.edit_title")
            : t("assistants.add_title")
        }
        onCancel={() => {
          setVisible(false);
          setEditingAssistant(null);
          form.resetFields();
        }}
        onOk={editingAssistant ? handleEdit : handleAdd}
        okText={editingAssistant ? t("common.update") : t("common.add")}
        cancelText={t("common.cancel")}
        confirmLoading={adding}
        width={800}
      >
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="name"
                label={t("assistants.form.name")}
                rules={[
                  {
                    required: true,
                    message: t("assistants.form.name_required"),
                  },
                ]}
              >
                <Input placeholder={t("assistants.form.name_placeholder")} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="model"
                label={t("assistants.form.model")}
                rules={[{ required: true }]}
              >
                <Select placeholder={t("assistants.form.model_placeholder")}>
                  {availableModels.map((model) => (
                    <Option key={model.value} value={model.value}>
                      {model.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="description"
            label={t("assistants.form.description")}
          >
            <Input.TextArea
              rows={3}
              placeholder={t("assistants.form.description_placeholder")}
            />
          </Form.Item>

          <Form.Item
            name="personality"
            label={t("assistants.form.personality")}
          >
            <Input.TextArea
              rows={4}
              placeholder={t("assistants.form.personality_placeholder")}
            />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="temperature"
                label={t("assistants.form.temperature")}
              >
                <Select defaultValue={0.7}>
                  <Option value={0.1}>
                    {t("assistants.temperature.focused")} (0.1)
                  </Option>
                  <Option value={0.3}>
                    {t("assistants.temperature.balanced")} (0.3)
                  </Option>
                  <Option value={0.7}>
                    {t("assistants.temperature.creative")} (0.7)
                  </Option>
                  <Option value={0.9}>
                    {t("assistants.temperature.very_creative")} (0.9)
                  </Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="isActive"
                label={t("assistants.form.active")}
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="knowledgeBaseIds"
            label={t("assistants.form.knowledge_bases")}
          >
            <Select
              mode="multiple"
              placeholder={t("assistants.form.knowledge_bases_placeholder")}
            >
              {availableKnowledgeBases.map((kb) => (
                <Option key={kb.id} value={kb.id}>
                  {kb.name}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item name="toolIds" label={t("assistants.form.tools")}>
            <Select
              mode="multiple"
              placeholder={t("assistants.form.tools_placeholder")}
            >
              {availableTools.map((tool) => (
                <Option key={tool.id} value={tool.id}>
                  {tool.name} - {tool.description}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item name="tags" label={t("assistants.form.tags")}>
            <Select
              mode="tags"
              placeholder={t("assistants.form.tags_placeholder")}
            >
              <Option value="support">Support</Option>
              <Option value="technical">Technical</Option>
              <Option value="creative">Creative</Option>
              <Option value="sales">Sales</Option>
              <Option value="helpful">Helpful</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Assistants;
