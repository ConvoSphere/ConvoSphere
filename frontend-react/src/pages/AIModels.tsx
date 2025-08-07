import React, { useState, useEffect } from "react";
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Switch,
  Tag,
  Space,
  Tooltip,
  Progress,
  Statistic,
  Row,
  Col,
  Typography,
  message,
  Spin,
  Tabs,
  Badge,
  Alert,
  Divider,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  SettingOutlined,
  EyeOutlined,
  TestOutlined,
  BarChartOutlined,
  DollarOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { config } from "../config";
import { colors } from "../styles/colors";

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

interface AIModel {
  id: string;
  name: string;
  provider: string;
  modelId: string;
  displayName: string;
  description: string;
  maxTokens: number;
  costPer1kTokens: number;
  isActive: boolean;
  isDefault: boolean;
  performance: {
    responseTime: number;
    errorRate: number;
    successRate: number;
    totalRequests: number;
  };
  capabilities: string[];
  lastUsed: string;
  createdAt: string;
  updatedAt: string;
}

interface ModelTest {
  id: string;
  modelId: string;
  prompt: string;
  response: string;
  responseTime: number;
  tokensUsed: number;
  cost: number;
  timestamp: string;
}

const AIModels: React.FC = () => {
  const { t } = useTranslation();
  const [models, setModels] = useState<AIModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [testModalVisible, setTestModalVisible] = useState(false);
  const [selectedModel, setSelectedModel] = useState<AIModel | null>(null);
  const [editingModel, setEditingModel] = useState<AIModel | null>(null);
  const [form] = Form.useForm();
  const [testForm] = Form.useForm();
  const [testResults, setTestResults] = useState<ModelTest[]>([]);
  const [activeTab, setActiveTab] = useState("overview");

  // Load models on component mount
  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${config.apiUrl}${config.apiEndpoints.assistants}/models`);
      if (response.ok) {
        const data = await response.json();
        setModels(data);
      } else {
        message.error(t("ai_models.load_failed"));
      }
    } catch (error) {
      message.error(t("ai_models.load_failed"));
    } finally {
      setLoading(false);
    }
  };

  const handleAddModel = () => {
    setEditingModel(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEditModel = (model: AIModel) => {
    setEditingModel(model);
    form.setFieldsValue({
      name: model.name,
      provider: model.provider,
      modelId: model.modelId,
      displayName: model.displayName,
      description: model.description,
      maxTokens: model.maxTokens,
      costPer1kTokens: model.costPer1kTokens,
      isActive: model.isActive,
      capabilities: model.capabilities,
    });
    setModalVisible(true);
  };

  const handleSaveModel = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingModel) {
        // Update existing model
        const response = await fetch(`${config.apiUrl}${config.apiEndpoints.assistants}/models/${editingModel.id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(values),
        });
        
        if (response.ok) {
          message.success(t("ai_models.updated_success"));
          loadModels();
        } else {
          message.error(t("ai_models.update_failed"));
        }
      } else {
        // Create new model
        const response = await fetch(`${config.apiUrl}${config.apiEndpoints.assistants}/models`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(values),
        });
        
        if (response.ok) {
          message.success(t("ai_models.added_success"));
          loadModels();
        } else {
          message.error(t("ai_models.add_failed"));
        }
      }
      
      setModalVisible(false);
    } catch (error) {
      message.error(t("ai_models.save_failed"));
    }
  };

  const handleDeleteModel = async (modelId: string) => {
    try {
      const response = await fetch(`${config.apiUrl}${config.apiEndpoints.assistants}/models/${modelId}`, {
        method: "DELETE",
      });
      
      if (response.ok) {
        message.success(t("ai_models.deleted_success"));
        loadModels();
      } else {
        message.error(t("ai_models.delete_failed"));
      }
    } catch (error) {
      message.error(t("ai_models.delete_failed"));
    }
  };

  const handleToggleActive = async (model: AIModel) => {
    try {
      const response = await fetch(`${config.apiUrl}${config.apiEndpoints.assistants}/models/${model.id}/toggle`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ isActive: !model.isActive }),
      });
      
      if (response.ok) {
        message.success(t("ai_models.toggle_success"));
        loadModels();
      } else {
        message.error(t("ai_models.toggle_failed"));
      }
    } catch (error) {
      message.error(t("ai_models.toggle_failed"));
    }
  };

  const handleTestModel = (model: AIModel) => {
    setSelectedModel(model);
    setTestResults([]);
    testForm.resetFields();
    setTestModalVisible(true);
  };

  const handleRunTest = async () => {
    try {
      const values = await testForm.validateFields();
      
      const response = await fetch(`${config.apiUrl}${config.apiEndpoints.assistants}/models/${selectedModel?.id}/test`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: values.prompt }),
      });
      
      if (response.ok) {
        const result = await response.json();
        setTestResults(prev => [result, ...prev]);
        message.success(t("ai_models.test_success"));
      } else {
        message.error(t("ai_models.test_failed"));
      }
    } catch (error) {
      message.error(t("ai_models.test_failed"));
    }
  };

  const getPerformanceColor = (rate: number) => {
    if (rate >= 95) return "success";
    if (rate >= 80) return "warning";
    return "error";
  };

  const getResponseTimeColor = (time: number) => {
    if (time <= 1000) return "success";
    if (time <= 3000) return "warning";
    return "error";
  };

  const columns = [
    {
      title: t("ai_models.columns.name"),
      dataIndex: "displayName",
      key: "name",
      render: (text: string, record: AIModel) => (
        <div>
          <div style={{ fontWeight: 500 }}>{text}</div>
          <div style={{ fontSize: "12px", color: colors.colorTextSecondary }}>
            {record.provider} • {record.modelId}
          </div>
        </div>
      ),
    },
    {
      title: t("ai_models.columns.status"),
      dataIndex: "isActive",
      key: "status",
      render: (isActive: boolean, record: AIModel) => (
        <Space>
          <Badge 
            status={isActive ? "success" : "default"} 
            text={isActive ? t("ai_models.status.active") : t("ai_models.status.inactive")} 
          />
          {record.isDefault && (
            <Tag color="blue">{t("ai_models.status.default")}</Tag>
          )}
        </Space>
      ),
    },
    {
      title: t("ai_models.columns.performance"),
      key: "performance",
      render: (record: AIModel) => (
        <div>
          <div style={{ marginBottom: 4 }}>
            <Text style={{ fontSize: "12px" }}>{t("ai_models.performance.response_time")}</Text>
            <Tag color={getResponseTimeColor(record.performance.responseTime)}>
              {record.performance.responseTime}ms
            </Tag>
          </div>
          <div>
            <Text style={{ fontSize: "12px" }}>{t("ai_models.performance.success_rate")}</Text>
            <Tag color={getPerformanceColor(record.performance.successRate)}>
              {record.performance.successRate}%
            </Tag>
          </div>
        </div>
      ),
    },
    {
      title: t("ai_models.columns.cost"),
      dataIndex: "costPer1kTokens",
      key: "cost",
      render: (cost: number) => (
        <div>
          <DollarOutlined style={{ marginRight: 4 }} />
          {cost.toFixed(4)}/1k tokens
        </div>
      ),
    },
    {
      title: t("ai_models.columns.usage"),
      key: "usage",
      render: (record: AIModel) => (
        <div>
          <div style={{ marginBottom: 4 }}>
            <Text style={{ fontSize: "12px" }}>{t("ai_models.usage.requests")}</Text>
            <div>{record.performance.totalRequests.toLocaleString()}</div>
          </div>
          <div>
            <Text style={{ fontSize: "12px" }}>{t("ai_models.usage.last_used")}</Text>
            <div>{new Date(record.lastUsed).toLocaleDateString()}</div>
          </div>
        </div>
      ),
    },
    {
      title: t("ai_models.columns.actions"),
      key: "actions",
      render: (record: AIModel) => (
        <Space>
          <Tooltip title={t("ai_models.actions.test")}>
            <Button
              type="text"
              icon={<TestOutlined />}
              onClick={() => handleTestModel(record)}
            />
          </Tooltip>
          <Tooltip title={t("ai_models.actions.edit")}>
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => handleEditModel(record)}
            />
          </Tooltip>
          <Tooltip title={record.isActive ? t("ai_models.actions.deactivate") : t("ai_models.actions.activate")}>
            <Button
              type="text"
              icon={record.isActive ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
              onClick={() => handleToggleActive(record)}
            />
          </Tooltip>
          <Tooltip title={t("ai_models.actions.delete")}>
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
              onClick={() => handleDeleteModel(record.id)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  const overviewStats = {
    totalModels: models.length,
    activeModels: models.filter(m => m.isActive).length,
    totalRequests: models.reduce((sum, m) => sum + m.performance.totalRequests, 0),
    avgResponseTime: models.length > 0 
      ? models.reduce((sum, m) => sum + m.performance.responseTime, 0) / models.length 
      : 0,
  };

  return (
    <div style={{ padding: "24px 0" }}>
      <div style={{ marginBottom: 24 }}>
        <Title level={2} style={{ color: colors.colorTextBase, marginBottom: 8 }}>
          {t("ai_models.title")}
        </Title>
        <Text type="secondary">{t("ai_models.subtitle")}</Text>
      </div>

      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab={t("ai_models.tabs.overview")} key="overview">
          <Row gutter={[24, 24]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title={t("ai_models.stats.total_models")}
                  value={overviewStats.totalModels}
                  prefix={<BarChartOutlined />}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title={t("ai_models.stats.active_models")}
                  value={overviewStats.activeModels}
                  prefix={<CheckCircleOutlined />}
                  valueStyle={{ color: colors.colorSuccess }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title={t("ai_models.stats.total_requests")}
                  value={overviewStats.totalRequests}
                  prefix={<EyeOutlined />}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title={t("ai_models.stats.avg_response_time")}
                  value={Math.round(overviewStats.avgResponseTime)}
                  suffix="ms"
                  prefix={<ClockCircleOutlined />}
                />
              </Card>
            </Col>
          </Row>

          <Card
            title={t("ai_models.performance_overview")}
            extra={
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={handleAddModel}
                style={{ backgroundColor: colors.colorPrimary }}
              >
                {t("ai_models.add_model")}
              </Button>
            }
          >
            {loading ? (
              <div style={{ textAlign: "center", padding: "40px" }}>
                <Spin size="large" />
              </div>
            ) : (
              <Table
                columns={columns}
                dataSource={models}
                rowKey="id"
                pagination={{
                  pageSize: 10,
                  showSizeChanger: true,
                  showQuickJumper: true,
                }}
              />
            )}
          </Card>
        </TabPane>

        <TabPane tab={t("ai_models.tabs.providers")} key="providers">
          <Card title={t("ai_models.provider_management")}>
            <Alert
              message={t("ai_models.provider_info")}
              description={t("ai_models.provider_description")}
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />
            <Text type="secondary">
              {t("ai_models.provider_coming_soon")}
            </Text>
          </Card>
        </TabPane>

        <TabPane tab={t("ai_models.tabs.analytics")} key="analytics">
          <Card title={t("ai_models.analytics")}>
            <Text type="secondary">
              {t("ai_models.analytics_coming_soon")}
            </Text>
          </Card>
        </TabPane>
      </Tabs>

      {/* Add/Edit Model Modal */}
      <Modal
        title={editingModel ? t("ai_models.edit_model") : t("ai_models.add_model")}
        open={modalVisible}
        onOk={handleSaveModel}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="name"
                label={t("ai_models.form.name")}
                rules={[{ required: true }]}
              >
                <Input placeholder={t("ai_models.form.name_placeholder")} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="provider"
                label={t("ai_models.form.provider")}
                rules={[{ required: true }]}
              >
                <Select placeholder={t("ai_models.form.provider_placeholder")}>
                  <Option value="openai">OpenAI</Option>
                  <Option value="anthropic">Anthropic</Option>
                  <Option value="google">Google</Option>
                  <Option value="azure">Azure OpenAI</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="modelId"
                label={t("ai_models.form.model_id")}
                rules={[{ required: true }]}
              >
                <Input placeholder={t("ai_models.form.model_id_placeholder")} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="displayName"
                label={t("ai_models.form.display_name")}
                rules={[{ required: true }]}
              >
                <Input placeholder={t("ai_models.form.display_name_placeholder")} />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="description"
            label={t("ai_models.form.description")}
          >
            <Input.TextArea rows={3} placeholder={t("ai_models.form.description_placeholder")} />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="maxTokens"
                label={t("ai_models.form.max_tokens")}
                rules={[{ required: true }]}
              >
                <Input type="number" placeholder="4096" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="costPer1kTokens"
                label={t("ai_models.form.cost_per_1k_tokens")}
                rules={[{ required: true }]}
              >
                <Input type="number" step="0.0001" placeholder="0.002" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="capabilities"
            label={t("ai_models.form.capabilities")}
          >
            <Select mode="multiple" placeholder={t("ai_models.form.capabilities_placeholder")}>
              <Option value="chat">Chat</Option>
              <Option value="completion">Completion</Option>
              <Option value="embedding">Embedding</Option>
              <Option value="vision">Vision</Option>
              <Option value="function_calling">Function Calling</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="isActive"
            label={t("ai_models.form.active")}
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </Form>
      </Modal>

      {/* Test Model Modal */}
      <Modal
        title={t("ai_models.test_model", { model: selectedModel?.displayName })}
        open={testModalVisible}
        onCancel={() => setTestModalVisible(false)}
        footer={null}
        width={800}
      >
        <Form form={testForm} layout="vertical">
          <Form.Item
            name="prompt"
            label={t("ai_models.test.prompt")}
            rules={[{ required: true }]}
          >
            <Input.TextArea 
              rows={4} 
              placeholder={t("ai_models.test.prompt_placeholder")} 
            />
          </Form.Item>
          
          <Button 
            type="primary" 
            onClick={handleRunTest}
            icon={<PlayCircleOutlined />}
            style={{ marginBottom: 16 }}
          >
            {t("ai_models.test.run_test")}
          </Button>
        </Form>

        <Divider>{t("ai_models.test.results")}</Divider>

        {testResults.map((result, index) => (
          <Card key={index} size="small" style={{ marginBottom: 8 }}>
            <div style={{ marginBottom: 8 }}>
              <Text strong>{t("ai_models.test.response")}:</Text>
            </div>
            <div style={{ 
              backgroundColor: colors.colorBgContainer, 
              padding: 8, 
              borderRadius: 4,
              marginBottom: 8 
            }}>
              {result.response}
            </div>
            <Row gutter={16}>
              <Col span={6}>
                <Text type="secondary">{t("ai_models.test.response_time")}: {result.responseTime}ms</Text>
              </Col>
              <Col span={6}>
                <Text type="secondary">{t("ai_models.test.tokens_used")}: {result.tokensUsed}</Text>
              </Col>
              <Col span={6}>
                <Text type="secondary">{t("ai_models.test.cost")}: ${result.cost.toFixed(4)}</Text>
              </Col>
              <Col span={6}>
                <Text type="secondary">{new Date(result.timestamp).toLocaleTimeString()}</Text>
              </Col>
            </Row>
          </Card>
        ))}
      </Modal>
    </div>
  );
};

export default AIModels;