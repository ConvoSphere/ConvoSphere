import React, { useState, useEffect } from "react";
import {
  Card,
  Button,
  Space,
  Typography,
  Modal,
  Form,
  Input,
  Table,
  Tag,
  Popconfirm,
  message,
  Spin,
  Alert,
} from "antd";
import {
  PlusOutlined,
  DeleteOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ServerOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import ModernCard from "../ModernCard";
import ModernButton from "../ModernButton";
import ModernInput from "../ModernInput";
import ModernForm, { ModernFormItem } from "../ModernForm";

const { Title, Text } = Typography;

interface McpServer {
  server_id: string;
  server_name: string;
  server_url: string;
  is_connected: boolean;
  tool_count: number;
  resource_count: number;
}

interface McpServerManagerProps {
  onServerChange: () => void;
}

const McpServerManager: React.FC<McpServerManagerProps> = ({
  onServerChange,
}) => {
  const { t } = useTranslation();
  const [servers, setServers] = useState<McpServer[]>([]);
  const [loading, setLoading] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    loadServers();
  }, []);

  const loadServers = async () => {
    setLoading(true);
    try {
      // TODO: Implement API call to get MCP servers
      // const response = await api.get('/mcp/servers');
      // setServers(response.data);

      // Mock data for now
      setServers([
        {
          server_id: "filesystem",
          server_name: "File System Server",
          server_url: "mcp://localhost:3000",
          is_connected: true,
          tool_count: 5,
          resource_count: 10,
        },
        {
          server_id: "github",
          server_name: "GitHub Server",
          server_url: "mcp://localhost:3001",
          is_connected: false,
          tool_count: 3,
          resource_count: 0,
        },
      ]);
    } catch (error) {
      message.error(t("mcp.load_servers_failed", "Failed to load MCP servers"));
    } finally {
      setLoading(false);
    }
  };

  const handleAddServer = async (values: any) => {
    try {
      // TODO: Implement API call to add MCP server
      // await api.post('/mcp/servers', values);

      message.success(t("mcp.server_added", "MCP server added successfully"));
      setShowAddModal(false);
      form.resetFields();
      loadServers();
      onServerChange();
    } catch (error) {
      message.error(t("mcp.add_server_failed", "Failed to add MCP server"));
    }
  };

  const handleRemoveServer = async (serverId: string) => {
    try {
      // TODO: Implement API call to remove MCP server
      // await api.delete(`/mcp/servers/${serverId}`);

      message.success(
        t("mcp.server_removed", "MCP server removed successfully"),
      );
      loadServers();
      onServerChange();
    } catch (error) {
      message.error(
        t("mcp.remove_server_failed", "Failed to remove MCP server"),
      );
    }
  };

  const columns = [
    {
      title: t("mcp.server_name", "Server Name"),
      dataIndex: "server_name",
      key: "server_name",
      render: (name: string, record: McpServer) => (
        <Space>
          <ServerOutlined
            style={{ color: record.is_connected ? "#52c41a" : "#ff4d4f" }}
          />
          <Text strong>{name}</Text>
        </Space>
      ),
    },
    {
      title: t("mcp.server_url", "Server URL"),
      dataIndex: "server_url",
      key: "server_url",
      render: (url: string) => (
        <Text code style={{ fontSize: "12px" }}>
          {url}
        </Text>
      ),
    },
    {
      title: t("mcp.status", "Status"),
      dataIndex: "is_connected",
      key: "is_connected",
      render: (connected: boolean) => (
        <Tag
          color={connected ? "green" : "red"}
          icon={
            connected ? <CheckCircleOutlined /> : <ExclamationCircleOutlined />
          }
        >
          {connected
            ? t("mcp.connected", "Connected")
            : t("mcp.disconnected", "Disconnected")}
        </Tag>
      ),
    },
    {
      title: t("mcp.tools", "Tools"),
      dataIndex: "tool_count",
      key: "tool_count",
      render: (count: number) => <Tag color="blue">{count}</Tag>,
    },
    {
      title: t("mcp.resources", "Resources"),
      dataIndex: "resource_count",
      key: "resource_count",
      render: (count: number) => <Tag color="purple">{count}</Tag>,
    },
    {
      title: t("common.actions", "Actions"),
      key: "actions",
      render: (record: McpServer) => (
        <Space>
          <ModernButton
            variant="text"
            size="small"
            icon={<ReloadOutlined />}
            onClick={() => loadServers()}
          >
            {t("common.refresh", "Refresh")}
          </ModernButton>
          <Popconfirm
            title={t(
              "mcp.remove_server_confirm",
              "Are you sure you want to remove this server?",
            )}
            onConfirm={() => handleRemoveServer(record.server_id)}
            okText={t("common.yes", "Yes")}
            cancelText={t("common.no", "No")}
          >
            <ModernButton
              variant="text"
              danger
              size="small"
              icon={<DeleteOutlined />}
            >
              {t("common.remove", "Remove")}
            </ModernButton>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
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
          <Title level={4} style={{ margin: 0 }}>
            {t("mcp.server_management", "MCP Server Management")}
          </Title>
          <Space>
            <ModernButton
              variant="outlined"
              icon={<ReloadOutlined />}
              onClick={loadServers}
              loading={loading}
            >
              {t("common.refresh", "Refresh")}
            </ModernButton>
            <ModernButton
              variant="primary"
              icon={<PlusOutlined />}
              onClick={() => setShowAddModal(true)}
            >
              {t("mcp.add_server", "Add Server")}
            </ModernButton>
          </Space>
        </div>
      }
    >
      {loading ? (
        <div style={{ textAlign: "center", padding: "48px" }}>
          <Spin size="large" />
        </div>
      ) : servers.length === 0 ? (
        <Alert
          message={t("mcp.no_servers", "No MCP servers configured")}
          description={t(
            "mcp.no_servers_desc",
            "Add an MCP server to get started",
          )}
          type="info"
          showIcon
          action={
            <ModernButton
              variant="primary"
              size="small"
              onClick={() => setShowAddModal(true)}
            >
              {t("mcp.add_first_server", "Add First Server")}
            </ModernButton>
          }
        />
      ) : (
        <Table
          columns={columns}
          dataSource={servers}
          rowKey="server_id"
          pagination={false}
          size="small"
        />
      )}

      {/* Add Server Modal */}
      <Modal
        title={
          <Space>
            <ServerOutlined style={{ color: "#1890ff" }} />
            <Title level={4} style={{ margin: 0 }}>
              {t("mcp.add_server", "Add MCP Server")}
            </Title>
          </Space>
        }
        open={showAddModal}
        onCancel={() => {
          setShowAddModal(false);
          form.resetFields();
        }}
        footer={null}
        width={600}
      >
        <ModernForm
          form={form}
          layout="vertical"
          onFinish={handleAddServer}
          style={{ marginTop: 16 }}
        >
          <ModernFormItem
            name="server_id"
            label={t("mcp.server_id", "Server ID")}
            rules={[
              {
                required: true,
                message: t("mcp.server_id_required", "Server ID is required"),
              },
            ]}
          >
            <ModernInput
              placeholder={t(
                "mcp.server_id_placeholder",
                "Enter unique server ID",
              )}
            />
          </ModernFormItem>

          <ModernFormItem
            name="server_name"
            label={t("mcp.server_name", "Server Name")}
            rules={[
              {
                required: true,
                message: t(
                  "mcp.server_name_required",
                  "Server name is required",
                ),
              },
            ]}
          >
            <ModernInput
              placeholder={t(
                "mcp.server_name_placeholder",
                "Enter server name",
              )}
            />
          </ModernFormItem>

          <ModernFormItem
            name="server_url"
            label={t("mcp.server_url", "Server URL")}
            rules={[
              {
                required: true,
                message: t("mcp.server_url_required", "Server URL is required"),
              },
            ]}
          >
            <ModernInput placeholder="mcp://localhost:3000" />
          </ModernFormItem>

          <div
            style={{
              display: "flex",
              justifyContent: "flex-end",
              gap: 12,
              marginTop: 24,
            }}
          >
            <ModernButton
              variant="outlined"
              onClick={() => {
                setShowAddModal(false);
                form.resetFields();
              }}
            >
              {t("common.cancel", "Cancel")}
            </ModernButton>
            <ModernButton variant="primary" htmlType="submit">
              {t("mcp.add_server", "Add Server")}
            </ModernButton>
          </div>
        </ModernForm>
      </Modal>
    </ModernCard>
  );
};

export default McpServerManager;
