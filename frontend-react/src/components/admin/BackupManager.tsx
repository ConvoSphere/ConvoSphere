import React, { useState, useEffect } from "react";
import {
  Card,
  Button,
  Table,
  Space,
  Modal,
  Form,
  Select,
  InputNumber,
  message,
  Tag,
  Typography,
  Row,
  Col,
  Statistic,
  Alert,
  Popconfirm,
  Tooltip,
  Progress,
} from "antd";
import {
  CloudUploadOutlined,
  CloudDownloadOutlined,
  DeleteOutlined,
  ReloadOutlined,
  SettingOutlined,
  HistoryOutlined,
  SafetyOutlined,
  ExclamationCircleOutlined,
} from "@ant-design/icons";
import { formatFileSize, formatDate } from "../../utils/formatters";

const { Title, Text } = Typography;
const { Option } = Select;

interface BackupInfo {
  backup_id: string;
  backup_type: string;
  status: string;
  created_at: string;
  completed_at?: string;
  size_bytes: number;
  document_count: number;
  retention_days: number;
  error_message?: string;
}

interface BackupStats {
  total_backups: number;
  successful_backups: number;
  failed_backups: number;
  success_rate: number;
  total_size_bytes: number;
  total_documents: number;
  average_backup_size: number;
}

interface RecoveryStats {
  total_attempts: number;
  successful_recoveries: number;
  overall_success_rate: number;
  strategy_statistics: Record<string, any>;
}

const BackupManager: React.FC = () => {
  const [backups, setBackups] = useState<BackupInfo[]>([]);
  const [stats, setStats] = useState<BackupStats | null>(null);
  const [recoveryStats, setRecoveryStats] = useState<RecoveryStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [restoreModalVisible, setRestoreModalVisible] = useState(false);
  const [selectedBackup, setSelectedBackup] = useState<BackupInfo | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchBackups();
    fetchStats();
  }, []);

  const fetchBackups = async () => {
    setLoading(true);
    try {
      const response = await fetch("/api/v1/knowledge/backups");
      if (response.ok) {
        const data = await response.json();
        setBackups(data.backups);
      }
    } catch (error) {
      message.error("Failed to fetch backups");
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const [backupResponse, recoveryResponse] = await Promise.all([
        fetch("/api/v1/knowledge/backups/stats"),
        fetch("/api/v1/knowledge/recovery/stats"),
      ]);

      if (backupResponse.ok) {
        const backupStats = await backupResponse.json();
        setStats(backupStats);
      }

      if (recoveryResponse.ok) {
        const recoveryData = await recoveryResponse.json();
        setRecoveryStats(recoveryData);
      }
    } catch (error) {
      message.error("Failed to fetch statistics");
    }
  };

  const createBackup = async (values: any) => {
    try {
      const response = await fetch("/api/v1/knowledge/backups", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });

      if (response.ok) {
        message.success("Backup created successfully");
        setCreateModalVisible(false);
        form.resetFields();
        fetchBackups();
      } else {
        message.error("Failed to create backup");
      }
    } catch (error) {
      message.error("Failed to create backup");
    }
  };

  const restoreBackup = async (values: any) => {
    if (!selectedBackup) return;

    try {
      const response = await fetch(`/api/v1/knowledge/backups/${selectedBackup.backup_id}/restore`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });

      if (response.ok) {
        message.success("Backup restored successfully");
        setRestoreModalVisible(false);
        setSelectedBackup(null);
      } else {
        message.error("Failed to restore backup");
      }
    } catch (error) {
      message.error("Failed to restore backup");
    }
  };

  const deleteBackup = async (backupId: string) => {
    try {
      const response = await fetch(`/api/v1/knowledge/backups/${backupId}`, {
        method: "DELETE",
      });

      if (response.ok) {
        message.success("Backup deleted successfully");
        fetchBackups();
      } else {
        message.error("Failed to delete backup");
      }
    } catch (error) {
      message.error("Failed to delete backup");
    }
  };

  const cleanupBackups = async () => {
    try {
      const response = await fetch("/api/v1/knowledge/backups/cleanup", {
        method: "POST",
      });

      if (response.ok) {
        const data = await response.json();
        message.success(data.message);
        fetchBackups();
      } else {
        message.error("Failed to cleanup backups");
      }
    } catch (error) {
      message.error("Failed to cleanup backups");
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "success";
      case "in_progress":
        return "processing";
      case "failed":
        return "error";
      case "expired":
        return "default";
      default:
        return "default";
    }
  };

  const getBackupTypeIcon = (type: string) => {
    switch (type) {
      case "full":
        return <CloudUploadOutlined style={{ color: "#1890ff" }} />;
      case "incremental":
        return <CloudDownloadOutlined style={{ color: "#52c41a" }} />;
      case "differential":
        return <HistoryOutlined style={{ color: "#722ed1" }} />;
      case "metadata_only":
        return <SettingOutlined style={{ color: "#fa8c16" }} />;
      default:
        return <CloudUploadOutlined />;
    }
  };

  const columns = [
    {
      title: "Backup ID",
      dataIndex: "backup_id",
      key: "backup_id",
      render: (id: string) => <Text code>{id}</Text>,
    },
    {
      title: "Type",
      dataIndex: "backup_type",
      key: "backup_type",
      render: (type: string) => (
        <Space>
          {getBackupTypeIcon(type)}
          <Text>{type}</Text>
        </Space>
      ),
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>{status}</Tag>
      ),
    },
    {
      title: "Created",
      dataIndex: "created_at",
      key: "created_at",
      render: (date: string) => formatDate(date),
    },
    {
      title: "Size",
      dataIndex: "size_bytes",
      key: "size_bytes",
      render: (size: number) => formatFileSize(size),
    },
    {
      title: "Documents",
      dataIndex: "document_count",
      key: "document_count",
    },
    {
      title: "Retention",
      dataIndex: "retention_days",
      key: "retention_days",
      render: (days: number) => `${days} days`,
    },
    {
      title: "Actions",
      key: "actions",
      render: (_, record: BackupInfo) => (
        <Space>
          <Tooltip title="Restore backup">
            <Button
              type="link"
              icon={<CloudDownloadOutlined />}
              onClick={() => {
                setSelectedBackup(record);
                setRestoreModalVisible(true);
              }}
              disabled={record.status !== "completed"}
            />
          </Tooltip>
          <Popconfirm
            title="Are you sure you want to delete this backup?"
            onConfirm={() => deleteBackup(record.backup_id)}
            okText="Yes"
            cancelText="No"
          >
            <Button type="link" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Title level={2}>Backup & Recovery Manager</Title>

      {/* Statistics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Backups"
              value={stats?.total_backups || 0}
              prefix={<CloudUploadOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Success Rate"
              value={stats?.success_rate ? (stats.success_rate * 100).toFixed(1) : 0}
              suffix="%"
              prefix={<SafetyOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Size"
              value={stats?.total_size_bytes ? formatFileSize(stats.total_size_bytes) : "0 B"}
              prefix={<CloudUploadOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Recovery Success"
              value={recoveryStats?.overall_success_rate ? (recoveryStats.overall_success_rate * 100).toFixed(1) : 0}
              suffix="%"
              prefix={<ExclamationCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* Actions */}
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Button
            type="primary"
            icon={<CloudUploadOutlined />}
            onClick={() => setCreateModalVisible(true)}
          >
            Create Backup
          </Button>
          <Button
            icon={<ReloadOutlined />}
            onClick={fetchBackups}
            loading={loading}
          >
            Refresh
          </Button>
          <Popconfirm
            title="Are you sure you want to cleanup expired backups?"
            onConfirm={cleanupBackups}
            okText="Yes"
            cancelText="No"
          >
            <Button icon={<DeleteOutlined />}>
              Cleanup Expired
            </Button>
          </Popconfirm>
        </Space>
      </Card>

      {/* Recovery Statistics */}
      {recoveryStats && (
        <Card title="Recovery Statistics" style={{ marginBottom: 16 }}>
          <Row gutter={[16, 16]}>
            <Col span={8}>
              <Statistic
                title="Total Recovery Attempts"
                value={recoveryStats.total_attempts}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="Successful Recoveries"
                value={recoveryStats.successful_recoveries}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="Success Rate"
                value={(recoveryStats.overall_success_rate * 100).toFixed(1)}
                suffix="%"
              />
            </Col>
          </Row>
          
          <div style={{ marginTop: 16 }}>
            <Text strong>Strategy Statistics:</Text>
            <Row gutter={[16, 16]} style={{ marginTop: 8 }}>
              {Object.entries(recoveryStats.strategy_statistics).map(([strategy, stats]) => (
                <Col span={6} key={strategy}>
                  <Card size="small">
                    <Statistic
                      title={strategy}
                      value={stats.attempts}
                      suffix={`(${(stats.success_rate * 100).toFixed(1)}%)`}
                    />
                  </Card>
                </Col>
              ))}
            </Row>
          </div>
        </Card>
      )}

      {/* Backups Table */}
      <Card title="Backups">
        <Table
          columns={columns}
          dataSource={backups}
          loading={loading}
          rowKey="backup_id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
          }}
        />
      </Card>

      {/* Create Backup Modal */}
      <Modal
        title="Create Backup"
        open={createModalVisible}
        onCancel={() => setCreateModalVisible(false)}
        footer={null}
      >
        <Form form={form} onFinish={createBackup} layout="vertical">
          <Form.Item
            name="backup_type"
            label="Backup Type"
            rules={[{ required: true, message: "Please select backup type" }]}
          >
            <Select placeholder="Select backup type">
              <Option value="full">Full Backup</Option>
              <Option value="incremental">Incremental Backup</Option>
              <Option value="differential">Differential Backup</Option>
              <Option value="metadata_only">Metadata Only</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="retention_days"
            label="Retention Period (days)"
            initialValue={30}
          >
            <InputNumber min={1} max={365} style={{ width: "100%" }} />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                Create Backup
              </Button>
              <Button onClick={() => setCreateModalVisible(false)}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Restore Backup Modal */}
      <Modal
        title="Restore Backup"
        open={restoreModalVisible}
        onCancel={() => setRestoreModalVisible(false)}
        footer={null}
      >
        {selectedBackup && (
          <div>
            <Alert
              message="Restore Warning"
              description="Restoring a backup will overwrite existing data. Make sure you have a current backup before proceeding."
              type="warning"
              showIcon
              style={{ marginBottom: 16 }}
            />

            <Form onFinish={restoreBackup} layout="vertical">
              <Form.Item
                name="restore_documents"
                label="Restore Documents"
                initialValue={true}
              >
                <Select>
                  <Option value={true}>Yes</Option>
                  <Option value={false}>No</Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="restore_jobs"
                label="Restore Processing Jobs"
                initialValue={false}
              >
                <Select>
                  <Option value={true}>Yes</Option>
                  <Option value={false}>No</Option>
                </Select>
              </Form.Item>

              <Form.Item>
                <Space>
                  <Button type="primary" htmlType="submit" danger>
                    Restore Backup
                  </Button>
                  <Button onClick={() => setRestoreModalVisible(false)}>
                    Cancel
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default BackupManager;