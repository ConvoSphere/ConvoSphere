import React, { useState, useEffect } from "react";
import {
  Card,
  Row,
  Col,
  Form,
  Input,
  Button,
  Select,
  Switch,
  Table,
  Typography,
  Space,
  Tag,
  Modal,
  message,
  Tooltip,
  Collapse,
  List,
  Badge,
  Alert,
  Divider,
  InputNumber,
  Slider,
  Checkbox,
  Radio,
  Tabs,
} from "antd";
import {
  SettingOutlined,
  SaveOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  CopyOutlined,
  EyeOutlined,
  RobotOutlined,
  ThunderboltOutlined,
  SwapOutlined,
  BranchesOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
// // import { colors } from "../styles/colors";
import { useAIModelsStore, type AIModel } from "../store/aiModelsStore";
import { aiModelsService } from "../services/aiModels";

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { TextArea } = Input;
const { TabPane } = Tabs;
const { Panel } = Collapse;

interface PromptTemplate {
  id: string;
  name: string;
  description: string;
  template: string;
  category: string;
  variables: string[];
  isDefault: boolean;
  modelId?: string;
  createdAt: string;
  updatedAt: string;
}

interface FallbackStrategy {
  id: string;
  name: string;
  description: string;
  primaryModel: string;
  fallbackModels: string[];
  conditions: {
    responseTimeThreshold: number;
    errorRateThreshold: number;
    costThreshold: number;
    maxRetries: number;
  };
  isActive: boolean;
}

interface AutoRoutingRule {
  id: string;
  name: string;
  description: string;
  conditions: {
    complexity: "low" | "medium" | "high";
    taskType: string[];
    tokenEstimate: number;
    costBudget: number;
    priority: "low" | "medium" | "high";
  };
  targetModel: string;
  isActive: boolean;
}

interface ModelConfigurationProps {
  modelId?: string;
  onSave?: () => void;
}

const ModelConfiguration: React.FC<ModelConfigurationProps> = ({
  modelId,
  onSave,
}) => {
  const { t } = useTranslation();
  const { models, updateModel } = useAIModelsStore();
  
  const [activeTab, setActiveTab] = useState("templates");
  const [templates, setTemplates] = useState<PromptTemplate[]>([]);
  const [fallbackStrategies, setFallbackStrategies] = useState<FallbackStrategy[]>([]);
  const [autoRoutingRules, setAutoRoutingRules] = useState<AutoRoutingRule[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingItem, setEditingItem] = useState<any>(null);
  const [modalType, setModalType] = useState<"template" | "fallback" | "routing">("template");
  
  // Forms
  const [templateForm] = Form.useForm();
  const [fallbackForm] = Form.useForm();
  const [routingForm] = Form.useForm();

  useEffect(() => {
    loadConfiguration();
  }, [modelId]);

  const loadConfiguration = async () => {
    try {
      setLoading(true);
      // TODO: Load from API
      const mockTemplates: PromptTemplate[] = [
        {
          id: "1",
          name: "General Assistant",
          description: "General purpose assistant template",
          template: "You are a helpful AI assistant. Please help the user with their request: {{user_input}}",
          category: "general",
          variables: ["user_input"],
          isDefault: true,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
        {
          id: "2",
          name: "Code Review",
          description: "Code review and analysis template",
          template: "You are an expert code reviewer. Please review this code and provide feedback:\n\n{{code}}\n\nFocus on: {{focus_areas}}",
          category: "programming",
          variables: ["code", "focus_areas"],
          isDefault: false,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      ];

      const mockFallbacks: FallbackStrategy[] = [
        {
          id: "1",
          name: "Performance Fallback",
          description: "Fallback to faster model if response time exceeds threshold",
          primaryModel: "gpt-4",
          fallbackModels: ["gpt-3.5-turbo", "claude-3-haiku"],
          conditions: {
            responseTimeThreshold: 5000,
            errorRateThreshold: 10,
            costThreshold: 0.01,
            maxRetries: 3,
          },
          isActive: true,
        },
      ];

      const mockRouting: AutoRoutingRule[] = [
        {
          id: "1",
          name: "Simple Tasks",
          description: "Route simple tasks to cost-effective models",
          conditions: {
            complexity: "low",
            taskType: ["question", "translation"],
            tokenEstimate: 100,
            costBudget: 0.001,
            priority: "low",
          },
          targetModel: "gpt-3.5-turbo",
          isActive: true,
        },
        {
          id: "2",
          name: "Complex Analysis",
          description: "Route complex analysis to powerful models",
          conditions: {
            complexity: "high",
            taskType: ["analysis", "reasoning"],
            tokenEstimate: 1000,
            costBudget: 0.05,
            priority: "high",
          },
          targetModel: "gpt-4",
          isActive: true,
        },
      ];

      setTemplates(mockTemplates);
      setFallbackStrategies(mockFallbacks);
      setAutoRoutingRules(mockRouting);
    } catch (error) {
      message.error(t("configuration.load_failed"));
    } finally {
      setLoading(false);
    }
  };

  const handleSaveTemplate = async () => {
    try {
      const values = await templateForm.validateFields();
      
      if (editingItem) {
        const updatedTemplate = { ...editingItem, ...values };
        setTemplates(prev => prev.map(t => t.id === editingItem.id ? updatedTemplate : t));
        message.success(t("configuration.template_updated"));
      } else {
        const newTemplate: PromptTemplate = {
          id: Date.now().toString(),
          ...values,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        setTemplates(prev => [...prev, newTemplate]);
        message.success(t("configuration.template_created"));
      }
      
      setModalVisible(false);
      templateForm.resetFields();
      setEditingItem(null);
    } catch (error) {
      message.error(t("configuration.save_failed"));
    }
  };

  const handleSaveFallback = async () => {
    try {
      const values = await fallbackForm.validateFields();
      
      if (editingItem) {
        const updatedFallback = { ...editingItem, ...values };
        setFallbackStrategies(prev => prev.map(f => f.id === editingItem.id ? updatedFallback : f));
        message.success(t("configuration.fallback_updated"));
      } else {
        const newFallback: FallbackStrategy = {
          id: Date.now().toString(),
          ...values,
        };
        setFallbackStrategies(prev => [...prev, newFallback]);
        message.success(t("configuration.fallback_created"));
      }
      
      setModalVisible(false);
      fallbackForm.resetFields();
      setEditingItem(null);
    } catch (error) {
      message.error(t("configuration.save_failed"));
    }
  };

  const handleSaveRouting = async () => {
    try {
      const values = await routingForm.validateFields();
      
      if (editingItem) {
        const updatedRouting = { ...editingItem, ...values };
        setAutoRoutingRules(prev => prev.map(r => r.id === editingItem.id ? updatedRouting : r));
        message.success(t("configuration.routing_updated"));
      } else {
        const newRouting: AutoRoutingRule = {
          id: Date.now().toString(),
          ...values,
        };
        setAutoRoutingRules(prev => [...prev, newRouting]);
        message.success(t("configuration.routing_created"));
      }
      
      setModalVisible(false);
      routingForm.resetFields();
      setEditingItem(null);
    } catch (error) {
      message.error(t("configuration.save_failed"));
    }
  };

  const openModal = (type: "template" | "fallback" | "routing", item?: any) => {
    setModalType(type);
    setEditingItem(item || null);
    setModalVisible(true);
    
    if (item) {
      if (type === "template") {
        templateForm.setFieldsValue(item);
      } else if (type === "fallback") {
        fallbackForm.setFieldsValue(item);
      } else if (type === "routing") {
        routingForm.setFieldsValue(item);
      }
    }
  };

  const deleteItem = (type: "template" | "fallback" | "routing", id: string) => {
    if (type === "template") {
      setTemplates(prev => prev.filter(t => t.id !== id));
    } else if (type === "fallback") {
      setFallbackStrategies(prev => prev.filter(f => f.id !== id));
    } else if (type === "routing") {
      setAutoRoutingRules(prev => prev.filter(r => r.id !== id));
    }
    message.success(t("configuration.item_deleted"));
  };

  const copyTemplate = (template: PromptTemplate) => {
    navigator.clipboard.writeText(template.template);
    message.success(t("configuration.template_copied"));
  };

  const getModelName = (modelId: string) => {
    return models.find(m => m.id === modelId)?.displayName || modelId;
  };

  const templateColumns = [
    {
      title: t("configuration.templates.name"),
      dataIndex: "name",
      key: "name",
      render: (text: string, record: PromptTemplate) => (
        <Space>
          <Text strong>{text}</Text>
          {record.isDefault && <Tag color="blue">{t("configuration.default")}</Tag>}
        </Space>
      ),
    },
    {
      title: t("configuration.templates.category"),
      dataIndex: "category",
      key: "category",
      render: (category: string) => (
        <Tag color="green">{category}</Tag>
      ),
    },
    {
      title: t("configuration.templates.variables"),
      dataIndex: "variables",
      key: "variables",
      render: (variables: string[]) => (
        <Space>
          {variables.map(v => (
            <Tag key={v} size="small">{{v}}</Tag>
          ))}
        </Space>
      ),
    },
    {
      title: t("configuration.templates.actions"),
      key: "actions",
      render: (record: PromptTemplate) => (
        <Space>
          <Tooltip title={t("configuration.templates.copy")}>
            <Button 
              type="text" 
              icon={<CopyOutlined />}
              onClick={() => copyTemplate(record)}
            />
          </Tooltip>
          <Tooltip title={t("configuration.templates.edit")}>
            <Button 
              type="text" 
              icon={<EditOutlined />}
              onClick={() => openModal("template", record)}
            />
          </Tooltip>
          <Tooltip title={t("configuration.templates.delete")}>
            <Button 
              type="text" 
              danger
              icon={<DeleteOutlined />}
              onClick={() => deleteItem("template", record.id)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  const fallbackColumns = [
    {
      title: t("configuration.fallbacks.name"),
      dataIndex: "name",
      key: "name",
      render: (text: string, record: FallbackStrategy) => (
        <Space>
          <Text strong>{text}</Text>
          <Badge status={record.isActive ? "success" : "default"} />
        </Space>
      ),
    },
    {
      title: t("configuration.fallbacks.primary"),
      dataIndex: "primaryModel",
      key: "primaryModel",
      render: (modelId: string) => getModelName(modelId),
    },
    {
      title: t("configuration.fallbacks.fallbacks"),
      dataIndex: "fallbackModels",
      key: "fallbackModels",
      render: (models: string[]) => (
        <Space>
          {models.map(m => (
            <Tag key={m} size="small">{getModelName(m)}</Tag>
          ))}
        </Space>
      ),
    },
    {
      title: t("configuration.fallbacks.conditions"),
      key: "conditions",
      render: (record: FallbackStrategy) => (
        <Space direction="vertical" size="small">
          <Text type="secondary">RT: {record.conditions.responseTimeThreshold}ms</Text>
          <Text type="secondary">ER: {record.conditions.errorRateThreshold}%</Text>
          <Text type="secondary">Cost: ${record.conditions.costThreshold}</Text>
        </Space>
      ),
    },
    {
      title: t("configuration.fallbacks.actions"),
      key: "actions",
      render: (record: FallbackStrategy) => (
        <Space>
          <Button 
            type="text" 
            icon={<EditOutlined />}
            onClick={() => openModal("fallback", record)}
          />
          <Button 
            type="text" 
            danger
            icon={<DeleteOutlined />}
            onClick={() => deleteItem("fallback", record.id)}
          />
        </Space>
      ),
    },
  ];

  const routingColumns = [
    {
      title: t("configuration.routing.name"),
      dataIndex: "name",
      key: "name",
      render: (text: string, record: AutoRoutingRule) => (
        <Space>
          <Text strong>{text}</Text>
          <Badge status={record.isActive ? "success" : "default"} />
        </Space>
      ),
    },
    {
      title: t("configuration.routing.conditions"),
      key: "conditions",
      render: (record: AutoRoutingRule) => (
        <Space direction="vertical" size="small">
          <Tag color="blue">{record.conditions.complexity}</Tag>
          <Text type="secondary">{record.conditions.taskType.join(", ")}</Text>
          <Text type="secondary">Tokens: {record.conditions.tokenEstimate}</Text>
        </Space>
      ),
    },
    {
      title: t("configuration.routing.target"),
      dataIndex: "targetModel",
      key: "targetModel",
      render: (modelId: string) => getModelName(modelId),
    },
    {
      title: t("configuration.routing.priority"),
      dataIndex: ["conditions", "priority"],
      key: "priority",
      render: (priority: string) => (
        <Tag color={
          priority === "high" ? "red" : 
          priority === "medium" ? "orange" : "green"
        }>
          {priority}
        </Tag>
      ),
    },
    {
      title: t("configuration.routing.actions"),
      key: "actions",
      render: (record: AutoRoutingRule) => (
        <Space>
          <Button 
            type="text" 
            icon={<EditOutlined />}
            onClick={() => openModal("routing", record)}
          />
          <Button 
            type="text" 
            danger
            icon={<DeleteOutlined />}
            onClick={() => deleteItem("routing", record.id)}
          />
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        <SettingOutlined style={{ marginRight: 8 }} />
        {t("configuration.title")}
      </Title>

      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        {/* Prompt Templates */}
        <TabPane tab={t("configuration.tabs.templates")} key="templates">
          <Card
            title={t("configuration.templates.title")}
            extra={
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => openModal("template")}
              >
                {t("configuration.templates.create")}
              </Button>
            }
          >
            <Alert
              message={t("configuration.templates.info")}
              description={t("configuration.templates.description")}
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />
            
            <Table
              columns={templateColumns}
              dataSource={templates}
              rowKey="id"
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </TabPane>

        {/* Fallback Strategies */}
        <TabPane tab={t("configuration.tabs.fallbacks")} key="fallbacks">
          <Card
            title={t("configuration.fallbacks.title")}
            extra={
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => openModal("fallback")}
              >
                {t("configuration.fallbacks.create")}
              </Button>
            }
          >
            <Alert
              message={t("configuration.fallbacks.info")}
              description={t("configuration.fallbacks.description")}
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />
            
            <Table
              columns={fallbackColumns}
              dataSource={fallbackStrategies}
              rowKey="id"
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </TabPane>

        {/* Auto Routing */}
        <TabPane tab={t("configuration.tabs.routing")} key="routing">
          <Card
            title={t("configuration.routing.title")}
            extra={
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => openModal("routing")}
              >
                {t("configuration.routing.create")}
              </Button>
            }
          >
            <Alert
              message={t("configuration.routing.info")}
              description={t("configuration.routing.description")}
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />
            
            <Table
              columns={routingColumns}
              dataSource={autoRoutingRules}
              rowKey="id"
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </TabPane>
      </Tabs>

      {/* Template Modal */}
      <Modal
        title={editingItem ? t("configuration.templates.edit") : t("configuration.templates.create")}
        open={modalVisible && modalType === "template"}
        onOk={handleSaveTemplate}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={templateForm} layout="vertical">
          <Form.Item
            name="name"
            label={t("configuration.templates.form.name")}
            rules={[{ required: true }]}
          >
            <Input placeholder={t("configuration.templates.form.name_placeholder")} />
          </Form.Item>
          
          <Form.Item
            name="description"
            label={t("configuration.templates.form.description")}
          >
            <Input placeholder={t("configuration.templates.form.description_placeholder")} />
          </Form.Item>
          
          <Form.Item
            name="category"
            label={t("configuration.templates.form.category")}
            rules={[{ required: true }]}
          >
            <Select placeholder={t("configuration.templates.form.category_placeholder")}>
              <Option value="general">{t("configuration.categories.general")}</Option>
              <Option value="programming">{t("configuration.categories.programming")}</Option>
              <Option value="creative">{t("configuration.categories.creative")}</Option>
              <Option value="analysis">{t("configuration.categories.analysis")}</Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            name="template"
            label={t("configuration.templates.form.template")}
            rules={[{ required: true }]}
          >
            <TextArea 
              rows={6} 
              placeholder={t("configuration.templates.form.template_placeholder")}
            />
          </Form.Item>
          
          <Form.Item
            name="isDefault"
            label={t("configuration.templates.form.is_default")}
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </Form>
      </Modal>

      {/* Fallback Modal */}
      <Modal
        title={editingItem ? t("configuration.fallbacks.edit") : t("configuration.fallbacks.create")}
        open={modalVisible && modalType === "fallback"}
        onOk={handleSaveFallback}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={fallbackForm} layout="vertical">
          <Form.Item
            name="name"
            label={t("configuration.fallbacks.form.name")}
            rules={[{ required: true }]}
          >
            <Input placeholder={t("configuration.fallbacks.form.name_placeholder")} />
          </Form.Item>
          
          <Form.Item
            name="description"
            label={t("configuration.fallbacks.form.description")}
          >
            <Input placeholder={t("configuration.fallbacks.form.description_placeholder")} />
          </Form.Item>
          
          <Form.Item
            name="primaryModel"
            label={t("configuration.fallbacks.form.primary_model")}
            rules={[{ required: true }]}
          >
            <Select placeholder={t("configuration.fallbacks.form.primary_model_placeholder")}>
              {models.map(model => (
                <Option key={model.id} value={model.id}>
                  {model.displayName}
                </Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item
            name="fallbackModels"
            label={t("configuration.fallbacks.form.fallback_models")}
            rules={[{ required: true }]}
          >
            <Select 
              mode="multiple"
              placeholder={t("configuration.fallbacks.form.fallback_models_placeholder")}
            >
              {models.map(model => (
                <Option key={model.id} value={model.id}>
                  {model.displayName}
                </Option>
              ))}
            </Select>
          </Form.Item>
          
          <Divider>{t("configuration.fallbacks.form.conditions")}</Divider>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name={["conditions", "responseTimeThreshold"]}
                label={t("configuration.fallbacks.form.response_time_threshold")}
              >
                <InputNumber 
                  min={1000} 
                  max={30000} 
                  step={1000}
                  style={{ width: "100%" }}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name={["conditions", "errorRateThreshold"]}
                label={t("configuration.fallbacks.form.error_rate_threshold")}
              >
                <InputNumber 
                  min={1} 
                  max={50} 
                  step={1}
                  style={{ width: "100%" }}
                />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name={["conditions", "costThreshold"]}
                label={t("configuration.fallbacks.form.cost_threshold")}
              >
                <InputNumber 
                  min={0.001} 
                  max={1} 
                  step={0.001}
                  precision={3}
                  style={{ width: "100%" }}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name={["conditions", "maxRetries"]}
                label={t("configuration.fallbacks.form.max_retries")}
              >
                <InputNumber 
                  min={1} 
                  max={10} 
                  step={1}
                  style={{ width: "100%" }}
                />
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item
            name="isActive"
            label={t("configuration.fallbacks.form.is_active")}
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </Form>
      </Modal>

      {/* Routing Modal */}
      <Modal
        title={editingItem ? t("configuration.routing.edit") : t("configuration.routing.create")}
        open={modalVisible && modalType === "routing"}
        onOk={handleSaveRouting}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={routingForm} layout="vertical">
          <Form.Item
            name="name"
            label={t("configuration.routing.form.name")}
            rules={[{ required: true }]}
          >
            <Input placeholder={t("configuration.routing.form.name_placeholder")} />
          </Form.Item>
          
          <Form.Item
            name="description"
            label={t("configuration.routing.form.description")}
          >
            <Input placeholder={t("configuration.routing.form.description_placeholder")} />
          </Form.Item>
          
          <Divider>{t("configuration.routing.form.conditions")}</Divider>
          
          <Form.Item
            name={["conditions", "complexity"]}
            label={t("configuration.routing.form.complexity")}
            rules={[{ required: true }]}
          >
            <Radio.Group>
              <Radio value="low">{t("configuration.complexity.low")}</Radio>
              <Radio value="medium">{t("configuration.complexity.medium")}</Radio>
              <Radio value="high">{t("configuration.complexity.high")}</Radio>
            </Radio.Group>
          </Form.Item>
          
          <Form.Item
            name={["conditions", "taskType"]}
            label={t("configuration.routing.form.task_type")}
            rules={[{ required: true }]}
          >
            <Select mode="multiple" placeholder={t("configuration.routing.form.task_type_placeholder")}>
              <Option value="question">{t("configuration.task_types.question")}</Option>
              <Option value="translation">{t("configuration.task_types.translation")}</Option>
              <Option value="analysis">{t("configuration.task_types.analysis")}</Option>
              <Option value="reasoning">{t("configuration.task_types.reasoning")}</Option>
              <Option value="creative">{t("configuration.task_types.creative")}</Option>
              <Option value="code">{t("configuration.task_types.code")}</Option>
            </Select>
          </Form.Item>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name={["conditions", "tokenEstimate"]}
                label={t("configuration.routing.form.token_estimate")}
              >
                <InputNumber 
                  min={1} 
                  max={4000} 
                  step={100}
                  style={{ width: "100%" }}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name={["conditions", "costBudget"]}
                label={t("configuration.routing.form.cost_budget")}
              >
                <InputNumber 
                  min={0.001} 
                  max={1} 
                  step={0.001}
                  precision={3}
                  style={{ width: "100%" }}
                />
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item
            name={["conditions", "priority"]}
            label={t("configuration.routing.form.priority")}
            rules={[{ required: true }]}
          >
            <Radio.Group>
              <Radio value="low">{t("configuration.priority.low")}</Radio>
              <Radio value="medium">{t("configuration.priority.medium")}</Radio>
              <Radio value="high">{t("configuration.priority.high")}</Radio>
            </Radio.Group>
          </Form.Item>
          
          <Form.Item
            name="targetModel"
            label={t("configuration.routing.form.target_model")}
            rules={[{ required: true }]}
          >
            <Select placeholder={t("configuration.routing.form.target_model_placeholder")}>
              {models.map(model => (
                <Option key={model.id} value={model.id}>
                  {model.displayName}
                </Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item
            name="isActive"
            label={t("configuration.routing.form.is_active")}
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ModelConfiguration;