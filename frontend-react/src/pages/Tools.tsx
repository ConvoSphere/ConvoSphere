import React, { useEffect, useState } from 'react';
import {
  Card,
  List,
  Button,
  Input,
  Modal,
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
  TextArea,
  Upload,
  Progress,
  Table,
  Descriptions,
  Alert
} from 'antd';
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
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  CopyOutlined,
  UploadOutlined
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { useThemeStore } from '../store/themeStore';
import { getTools, runTool } from '../services/tools';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

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
  type: 'string' | 'number' | 'boolean' | 'file' | 'select';
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
  status: 'success' | 'error' | 'running';
  executionTime: number;
  timestamp: string;
  error?: string;
}

const Tools: React.FC = () => {
  const { t } = useTranslation();
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const [tools, setTools] = useState<Tool[]>([]);
  const [selectedTool, setSelectedTool] = useState<Tool | null>(null);
  const [visible, setVisible] = useState(false);
  const [executionHistory, setExecutionHistory] = useState<ToolExecution[]>([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [activeTab, setActiveTab] = useState('all');
  const [form] = Form.useForm();

  // Mock data for demonstration
  const mockTools: Tool[] = [
    {
      id: 1,
      name: 'Web Search',
      description: 'Search the web for current information',
      category: 'search',
      isActive: true,
      parameters: [
        {
          name: 'query',
          type: 'string',
          required: true,
          description: 'Search query'
        },
        {
          name: 'max_results',
          type: 'number',
          required: false,
          description: 'Maximum number of results',
          defaultValue: 5
        }
      ],
      executionTime: 2.5,
      successRate: 98.5,
      lastUsed: '2024-01-15T10:30:00Z',
      usageCount: 1250,
      tags: ['search', 'web', 'information'],
      version: '1.2.0',
      author: 'System'
    },
    {
      id: 2,
      name: 'Calculator',
      description: 'Perform mathematical calculations',
      category: 'utility',
      isActive: true,
      parameters: [
        {
          name: 'expression',
          type: 'string',
          required: true,
          description: 'Mathematical expression to evaluate'
        }
      ],
      executionTime: 0.1,
      successRate: 99.9,
      lastUsed: '2024-01-15T09:15:00Z',
      usageCount: 890,
      tags: ['math', 'calculation', 'utility'],
      version: '1.0.0',
      author: 'System'
    },
    {
      id: 3,
      name: 'Code Interpreter',
      description: 'Execute and analyze code',
      category: 'development',
      isActive: true,
      parameters: [
        {
          name: 'code',
          type: 'string',
          required: true,
          description: 'Code to execute'
        },
        {
          name: 'language',
          type: 'select',
          required: true,
          description: 'Programming language',
          options: ['python', 'javascript', 'java', 'cpp']
        }
      ],
      executionTime: 5.2,
      successRate: 95.2,
      lastUsed: '2024-01-15T08:45:00Z',
      usageCount: 450,
      tags: ['code', 'development', 'execution'],
      version: '2.1.0',
      author: 'System'
    },
    {
      id: 4,
      name: 'File Processor',
      description: 'Process and analyze files',
      category: 'file',
      isActive: false,
      parameters: [
        {
          name: 'file',
          type: 'file',
          required: true,
          description: 'File to process'
        },
        {
          name: 'operation',
          type: 'select',
          required: true,
          description: 'Operation to perform',
          options: ['analyze', 'convert', 'extract']
        }
      ],
      executionTime: 8.7,
      successRate: 92.1,
      lastUsed: '2024-01-14T16:20:00Z',
      usageCount: 320,
      tags: ['file', 'processing', 'analysis'],
      version: '1.5.0',
      author: 'System'
    }
  ];

  const mockExecutionHistory: ToolExecution[] = [
    {
      id: '1',
      toolId: 1,
      toolName: 'Web Search',
      parameters: { query: 'AI trends 2024', max_results: 5 },
      result: { results: ['Result 1', 'Result 2', 'Result 3'] },
      status: 'success',
      executionTime: 2.3,
      timestamp: '2024-01-15T10:30:00Z'
    },
    {
      id: '2',
      toolId: 2,
      toolName: 'Calculator',
      parameters: { expression: '2 + 2 * 3' },
      result: { result: 8 },
      status: 'success',
      executionTime: 0.1,
      timestamp: '2024-01-15T09:15:00Z'
    },
    {
      id: '3',
      toolId: 3,
      toolName: 'Code Interpreter',
      parameters: { code: 'print("Hello World")', language: 'python' },
      result: { output: 'Hello World' },
      status: 'success',
      executionTime: 4.8,
      timestamp: '2024-01-15T08:45:00Z'
    }
  ];

  const categories = [
    { value: 'search', label: 'Search', icon: <SearchOutlined /> },
    { value: 'utility', label: 'Utility', icon: <ToolOutlined /> },
    { value: 'development', label: 'Development', icon: <CodeOutlined /> },
    { value: 'file', label: 'File', icon: <FileTextOutlined /> },
    { value: 'api', label: 'API', icon: <ApiOutlined /> }
  ];

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setTools(mockTools);
      setExecutionHistory(mockExecutionHistory);
      setLoading(false);
    }, 1000);
  }, []);

  const handleRunTool = async () => {
    if (!selectedTool) return;

    try {
      setRunning(true);
      const values = await form.validateFields();

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));

      const execution: ToolExecution = {
        id: Date.now().toString(),
        toolId: selectedTool.id,
        toolName: selectedTool.name,
        parameters: values,
        result: { output: 'Tool executed successfully' },
        status: 'success',
        executionTime: Math.random() * 10,
        timestamp: new Date().toISOString()
      };

      setExecutionHistory(prev => [execution, ...prev]);
      setVisible(false);
      form.resetFields();
      message.success(t('tools.execution_success'));
    } catch (error) {
      message.error(t('tools.execution_failed'));
    } finally {
      setRunning(false);
    }
  };

  const handleToggleActive = async (tool: Tool) => {
    try {
      const updatedTool = { ...tool, isActive: !tool.isActive };
      setTools(prev => prev.map(t => t.id === tool.id ? updatedTool : t));
      message.success(tool.isActive ? t('tools.deactivated') : t('tools.activated'));
    } catch (error) {
      message.error(t('tools.toggle_failed'));
    }
  };

  const openToolModal = (tool: Tool) => {
    setSelectedTool(tool);
    form.resetFields();
    setVisible(true);
  };

  const filteredTools = tools.filter(tool => {
    if (activeTab === 'all') return true;
    return tool.category === activeTab;
  });

  const getCategoryIcon = (category: string) => {
    const cat = categories.find(c => c.value === category);
    return cat ? cat.icon : <ToolOutlined />;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'success';
      case 'error': return 'error';
      case 'running': return 'processing';
      default: return 'default';
    }
  };

  const executionColumns = [
    {
      title: t('tools.history.tool'),
      dataIndex: 'toolName',
      key: 'toolName',
    },
    {
      title: t('tools.history.status'),
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>
          {status === 'success' && <CheckCircleOutlined />}
          {status === 'error' && <ExclamationCircleOutlined />}
          {status === 'running' && <ClockCircleOutlined />}
          {t(`tools.status.${status}`)}
        </Tag>
      ),
    },
    {
      title: t('tools.history.execution_time'),
      dataIndex: 'executionTime',
      key: 'executionTime',
      render: (time: number) => `${time.toFixed(2)}s`,
    },
    {
      title: t('tools.history.timestamp'),
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (timestamp: string) => new Date(timestamp).toLocaleString(),
    },
  ];

  return (
    <div style={{ padding: '24px 0' }}>
      <div style={{ marginBottom: 24 }}>
        <Title level={2} style={{ color: colors.colorTextBase, marginBottom: 8 }}>
          {t('tools.title')}
        </Title>
        <Text type="secondary">
          {t('tools.subtitle')}
        </Text>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <Card>
            <div style={{ marginBottom: 16 }}>
              <Tabs activeKey={activeTab} onChange={setActiveTab}>
                <TabPane tab={t('tools.categories.all')} key="all" />
                {categories.map(category => (
                  <TabPane
                    tab={
                      <Space>
                        {category.icon}
                        {category.label}
                      </Space>
                    }
                    key={category.value}
                  />
                ))}
              </Tabs>
            </div>

            {loading ? (
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <Spin size="large" />
              </div>
            ) : (
              <List
                grid={{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 2, xl: 2, xxl: 2 }}
                dataSource={filteredTools}
                renderItem={(tool) => (
                  <List.Item>
                    <Card
                      hoverable
                      actions={[
                        <Tooltip title={t('tools.actions.run')}>
                          <Button
                            type="primary"
                            icon={<PlayCircleOutlined />}
                            onClick={() => openToolModal(tool)}
                            disabled={!tool.isActive}
                          >
                            {t('tools.run')}
                          </Button>
                        </Tooltip>,
                        <Tooltip title={tool.isActive ? t('tools.actions.deactivate') : t('tools.actions.activate')}>
                          <Button
                            type="text"
                            icon={tool.isActive ? <CheckCircleOutlined /> : <ExclamationCircleOutlined />}
                            onClick={() => handleToggleActive(tool)}
                          />
                        </Tooltip>
                      ]}
                    >
                      <List.Item.Meta
                        avatar={
                          <Badge status={tool.isActive ? 'success' : 'default'}>
                            <Avatar
                              size={48}
                              icon={getCategoryIcon(tool.category)}
                              style={{ backgroundColor: colors.colorPrimary }}
                            />
                          </Badge>
                        }
                        title={
                          <Space>
                            <Text strong>{tool.name}</Text>
                            <Tag color={tool.isActive ? 'green' : 'default'}>
                              {tool.isActive ? t('tools.status.active') : t('tools.status.inactive')}
                            </Tag>
                          </Space>
                        }
                        description={
                          <div>
                            <Text type="secondary">{tool.description}</Text>
                            <div style={{ marginTop: 8 }}>
                              <Space wrap>
                                <Tag color="blue">v{tool.version}</Tag>
                                <Tag color="purple">{tool.category}</Tag>
                                <Tag color="orange">{tool.usageCount} {t('tools.usage_count')}</Tag>
                              </Space>
                            </div>
                            <div style={{ marginTop: 8 }}>
                              <Space>
                                <Text type="secondary">
                                  <ClockCircleOutlined /> {tool.executionTime.toFixed(1)}s
                                </Text>
                                <Text type="secondary">
                                  <CheckCircleOutlined /> {tool.successRate.toFixed(1)}%
                                </Text>
                              </Space>
                            </div>
                          </div>
                        }
                      />

                      <div style={{ marginTop: 12 }}>
                        <Space wrap>
                          {tool.tags.map(tag => (
                            <Tag key={tag} size="small">{tag}</Tag>
                          ))}
                        </Space>
                      </div>
                    </Card>
                  </List.Item>
                )}
              />
            )}
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          <Card title={t('tools.execution_history')}>
            <Table
              dataSource={executionHistory}
              columns={executionColumns}
              pagination={{ pageSize: 5 }}
              size="small"
              scroll={{ y: 300 }}
            />
          </Card>
        </Col>
      </Row>

      <Modal
        open={visible}
        title={selectedTool?.name}
        onCancel={() => {
          setVisible(false);
          setSelectedTool(null);
          form.resetFields();
        }}
        onOk={handleRunTool}
        okText={t('tools.run')}
        cancelText={t('common.cancel')}
        confirmLoading={running}
        width={600}
      >
        {selectedTool && (
          <div>
            <Descriptions column={1} size="small" style={{ marginBottom: 16 }}>
              <Descriptions.Item label={t('tools.details.description')}>
                {selectedTool.description}
              </Descriptions.Item>
              <Descriptions.Item label={t('tools.details.category')}>
                {categories.find(c => c.value === selectedTool.category)?.label}
              </Descriptions.Item>
              <Descriptions.Item label={t('tools.details.version')}>
                {selectedTool.version}
              </Descriptions.Item>
              <Descriptions.Item label={t('tools.details.author')}>
                {selectedTool.author}
              </Descriptions.Item>
            </Descriptions>

            <Divider />

            <Form form={form} layout="vertical">
              {selectedTool.parameters.map(param => (
                <Form.Item
                  key={param.name}
                  name={param.name}
                  label={param.name}
                  rules={[
                    {
                      required: param.required,
                      message: t('tools.parameter_required', { name: param.name })
                    }
                  ]}
                  extra={param.description}
                >
                  {param.type === 'string' && <Input placeholder={param.description} />}
                  {param.type === 'number' && <Input type="number" placeholder={param.description} />}
                  {param.type === 'boolean' && <Switch />}
                  {param.type === 'select' && (
                    <Select placeholder={param.description}>
                      {param.options?.map(option => (
                        <Option key={option} value={option}>{option}</Option>
                      ))}
                    </Select>
                  )}
                  {param.type === 'file' && (
                    <Upload>
                      <Button icon={<UploadOutlined />}>{t('tools.upload_file')}</Button>
                    </Upload>
                  )}
                </Form.Item>
              ))}
            </Form>

            {selectedTool.parameters.length === 0 && (
              <Alert
                message={t('tools.no_parameters')}
                description={t('tools.no_parameters_description')}
                type="info"
                showIcon
              />
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Tools; 