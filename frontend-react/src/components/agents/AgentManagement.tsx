import React, { useState, useEffect } from "react";
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  Select,
  Switch,
  message,
  Popconfirm,
  Tooltip,
  Progress,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  SwapOutlined,
  TeamOutlined,
  BarChartOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";

const { Option } = Select;
const { TextArea } = Input;

interface Agent {
  id: string;
  name: string;
  description: string;
  model: string;
  temperature: number;
  tools: string[];
  is_public: boolean;
  is_template: boolean;
  planning_strategy?: "none" | "react" | "plan_execute" | "tree_of_thought";
  max_planning_steps?: number;
  abort_criteria?: {
    max_time_seconds?: number;
    max_steps?: number;
    stop_on_tool_error?: boolean;
    no_progress_iterations?: number;
    confidence_threshold?: number;
  };
}

interface AgentManagementProps {
  onAgentSelect?: (agentId: string) => void;
  onCollaborationStart?: (agentIds: string[]) => void;
}

const AgentManagement: React.FC<AgentManagementProps> = ({
  onAgentSelect,
  onCollaborationStart,
}) => {
  const { t } = useTranslation();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingAgent, setEditingAgent] = useState<Agent | null>(null);
  const [form] = Form.useForm();
  const [collaborationModalVisible, setCollaborationModalVisible] =
    useState(false);
  const [selectedAgents, setSelectedAgents] = useState<string[]>([]);

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    setLoading(true);
    try {
      const response = await fetch("/api/v1/agents/");
      if (response.ok) {
        const data = await response.json();
        setAgents(data);
      } else {
        message.error(t("agents.fetchError"));
      }
    } catch (error) {
      message.error(t("agents.fetchError"));
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAgent = () => {
    setEditingAgent(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEditAgent = (agent: Agent) => {
    setEditingAgent(agent);
    form.setFieldsValue({
      name: agent.name,
      description: agent.description,
      model: agent.model,
      temperature: agent.temperature,
      tools: agent.tools,
      is_public: agent.is_public,
      is_template: agent.is_template,
      planning_strategy: agent.planning_strategy || "none",
      max_planning_steps: agent.max_planning_steps || 10,
      abort_criteria: agent.abort_criteria || {
        max_time_seconds: 300,
        max_steps: 10,
        stop_on_tool_error: false,
        no_progress_iterations: 3,
        confidence_threshold: undefined,
      },
    });
    setModalVisible(true);
  };

  const handleDeleteAgent = async (agentId: string) => {
    try {
      const response = await fetch(`/api/v1/agents/${agentId}`, {
        method: "DELETE",
      });
      if (response.ok) {
        message.success(t("agents.deleteSuccess"));
        fetchAgents();
      } else {
        message.error(t("agents.deleteError"));
      }
    } catch (error) {
      message.error(t("agents.deleteError"));
    }
  };

  const handleSubmit = async (values: any) => {
    try {
      const url = editingAgent
        ? `/api/v1/agents/${editingAgent.id}`
        : "/api/v1/agents/";

      const method = editingAgent ? "PUT" : "POST";

      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(values),
      });

      if (response.ok) {
        message.success(
          editingAgent ? t("agents.updateSuccess") : t("agents.createSuccess"),
        );
        setModalVisible(false);
        fetchAgents();
      } else {
        message.error(
          editingAgent ? t("agents.updateError") : t("agents.createError"),
        );
      }
    } catch (error) {
      message.error(
        editingAgent ? t("agents.updateError") : t("agents.createError"),
      );
    }
  };

  const handleStartCollaboration = () => {
    if (selectedAgents.length < 2) {
      message.warning(t("agents.collaborationMinAgents"));
      return;
    }
    setCollaborationModalVisible(true);
  };

  const handleCollaborationSubmit = async (values: any) => {
    try {
      const response = await fetch("/api/v1/agents/collaborate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          agent_ids: selectedAgents,
          collaboration_type: values.collaboration_type,
          coordination_strategy: values.coordination_strategy,
          shared_context: values.shared_context || {},
        }),
      });

      if (response.ok) {
        message.success(t("agents.collaborationStarted"));
        setCollaborationModalVisible(false);
        setSelectedAgents([]);
        if (onCollaborationStart) {
          onCollaborationStart(selectedAgents);
        }
      } else {
        message.error(t("agents.collaborationError"));
      }
    } catch (error) {
      message.error(t("agents.collaborationError"));
    }
  };

  const columns = [
    {
      title: t("agents.name"),
      dataIndex: "name",
      key: "name",
      render: (text: string, record: Agent) => (
        <Space>
          <span>{text}</span>
          {record.is_public && <Tag color="blue">{t("agents.public")}</Tag>}
          {record.is_template && (
            <Tag color="green">{t("agents.template")}</Tag>
          )}
        </Space>
      ),
    },
    {
      title: t("agents.description"),
      dataIndex: "description",
      key: "description",
      ellipsis: true,
    },
    {
      title: t("agents.model"),
      dataIndex: "model",
      key: "model",
    },
    {
      title: t("agents.temperature"),
      dataIndex: "temperature",
      key: "temperature",
      render: (value: number) => (
        <Progress
          percent={Math.round(value * 100)}
          size="small"
          showInfo={false}
        />
      ),
    },
    {
      title: t("agents.tools"),
      dataIndex: "tools",
      key: "tools",
      render: (tools: string[]) => (
        <Space wrap>
          {tools.slice(0, 2).map((tool) => (
            <Tag key={tool} size="small">
              {tool}
            </Tag>
          ))}
          {tools.length > 2 && <Tag size="small">+{tools.length - 2}</Tag>}
        </Space>
      ),
    },
    {
      title: t("agents.planning", "Planning"),
      dataIndex: "planning_strategy",
      key: "planning_strategy",
      render: (strategy: Agent["planning_strategy"]) => (
        strategy && strategy !== "none" ? (
          <Tag color="purple">{strategy}</Tag>
        ) : (
          <Tag>{t("agents.none", "none")}</Tag>
        )
      ),
    },
    {
      title: t("agents.actions"),
      key: "actions",
      render: (text: string, record: Agent) => (
        <Space>
          <Tooltip title={t("agents.view")}>
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => onAgentSelect?.(record.id)}
            />
          </Tooltip>
          <Tooltip title={t("agents.edit")}>
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => handleEditAgent(record)}
            />
          </Tooltip>
          <Popconfirm
            title={t("agents.deleteConfirm")}
            onConfirm={() => handleDeleteAgent(record.id)}
            okText={t("common.yes")}
            cancelText={t("common.no")}
          >
            <Tooltip title={t("agents.delete")}>
              <Button type="text" danger icon={<DeleteOutlined />} />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div className="agent-management">
      <Card
        title={t("agents.title")}
        extra={
          <Space>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleCreateAgent}
            >
              {t("agents.create")}
            </Button>
            <Button
              icon={<TeamOutlined />}
              onClick={handleStartCollaboration}
              disabled={selectedAgents.length < 2}
            >
              {t("agents.collaborate")}
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={agents}
          loading={loading}
          rowKey="id"
          rowSelection={{
            type: "checkbox",
            selectedRowKeys: selectedAgents,
            onChange: (selectedRowKeys) => {
              setSelectedAgents(selectedRowKeys as string[]);
            },
          }}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
          }}
        />
      </Card>

      {/* Agent Create/Edit Modal */}
      <Modal
        title={editingAgent ? t("agents.editTitle") : t("agents.createTitle")}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            name="name"
            label={t("agents.name")}
            rules={[{ required: true, message: t("agents.nameRequired") }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="description"
            label={t("agents.description")}
            rules={[
              { required: true, message: t("agents.descriptionRequired") },
            ]}
          >
            <TextArea rows={3} />
          </Form.Item>

          <Form.Item
            name="model"
            label={t("agents.model")}
            rules={[{ required: true, message: t("agents.modelRequired") }]}
          >
            <Select>
              <Option value="gpt-4">GPT-4</Option>
              <Option value="gpt-3.5-turbo">GPT-3.5 Turbo</Option>
              <Option value="claude-3">Claude-3</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="temperature"
            label={t("agents.temperature")}
            rules={[
              { required: true, message: t("agents.temperatureRequired") },
            ]}
          >
            <Input type="number" min={0} max={2} step={0.1} />
          </Form.Item>

          <Form.Item name="tools" label={t("agents.tools")}>
            <Select mode="tags" placeholder={t("agents.toolsPlaceholder")}>
              <Option value="web_search">Web Search</Option>
              <Option value="calculator">Calculator</Option>
              <Option value="code_analyzer">Code Analyzer</Option>
              <Option value="data_analyzer">Data Analyzer</Option>
            </Select>
          </Form.Item>

          <Form.Item name="planning_strategy" label={t("agents.planningStrategy", "Planning Strategy")}>
            <Select>
              <Option value="none">{t("agents.none", "none")}</Option>
              <Option value="react">ReAct</Option>
              <Option value="plan_execute">Plan-Execute</Option>
              <Option value="tree_of_thought">Tree-of-Thought</Option>
            </Select>
          </Form.Item>

          <Form.Item name="max_planning_steps" label={t("agents.maxPlanningSteps", "Max planning steps")}>
            <Input type="number" min={1} max={200} step={1} />
          </Form.Item>

          <Card size="small" title={t("agents.abortCriteria", "Abort Criteria")} style={{ marginBottom: 16 }}>
            <Space direction="vertical" style={{ width: "100%" }}>
              <Form.Item name={["abort_criteria", "max_time_seconds"]} label={t("agents.maxTimeSeconds", "Max time (s)")}>
                <Input type="number" min={1} max={36000} step={1} />
              </Form.Item>
              <Form.Item name={["abort_criteria", "max_steps"]} label={t("agents.maxSteps", "Max steps")}>
                <Input type="number" min={1} max={200} step={1} />
              </Form.Item>
              <Form.Item name={["abort_criteria", "no_progress_iterations"]} label={t("agents.noProgressIterations", "No-progress iterations")}>
                <Input type="number" min={0} max={50} step={1} />
              </Form.Item>
              <Form.Item name={["abort_criteria", "confidence_threshold"]} label={t("agents.confidenceThreshold", "Confidence threshold (0-1)")}>
                <Input type="number" min={0} max={1} step={0.01} />
              </Form.Item>
              <Form.Item name={["abort_criteria", "stop_on_tool_error"]} label={t("agents.stopOnToolError", "Stop on tool error")} valuePropName="checked">
                <Switch />
              </Form.Item>
            </Space>
          </Card>

          <Form.Item
            name="is_public"
            label={t("agents.public")}
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            name="is_template"
            label={t("agents.template")}
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingAgent ? t("common.update") : t("common.create")}
              </Button>
              <Button onClick={() => setModalVisible(false)}>
                {t("common.cancel")}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Collaboration Modal */}
      <Modal
        title={t("agents.collaborationTitle")}
        open={collaborationModalVisible}
        onCancel={() => setCollaborationModalVisible(false)}
        footer={null}
      >
        <Form layout="vertical" onFinish={handleCollaborationSubmit}>
          <Form.Item
            name="collaboration_type"
            label={t("agents.collaborationType")}
            rules={[
              {
                required: true,
                message: t("agents.collaborationTypeRequired"),
              },
            ]}
          >
            <Select>
              <Option value="parallel">{t("agents.parallel")}</Option>
              <Option value="sequential">{t("agents.sequential")}</Option>
              <Option value="hierarchical">{t("agents.hierarchical")}</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="coordination_strategy"
            label={t("agents.coordinationStrategy")}
            rules={[
              {
                required: true,
                message: t("agents.coordinationStrategyRequired"),
              },
            ]}
          >
            <Select>
              <Option value="round_robin">{t("agents.roundRobin")}</Option>
              <Option value="priority">{t("agents.priority")}</Option>
              <Option value="expertise">{t("agents.expertise")}</Option>
            </Select>
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {t("agents.startCollaboration")}
              </Button>
              <Button onClick={() => setCollaborationModalVisible(false)}>
                {t("common.cancel")}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default AgentManagement;
