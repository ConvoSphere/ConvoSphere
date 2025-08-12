import React from "react";
import {
  Table,
  Tag,
  Space,
  Progress,
  Tooltip,
  Popconfirm,
  message,
} from "antd";
import ModernButton from "../ModernButton";
import {
  DownloadOutlined,
  DeleteOutlined,
  ReloadOutlined,
  FileTextOutlined,
  DatabaseOutlined,
  BarChartOutlined,
  SettingOutlined,
  UserOutlined,
  RobotOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  CloseCircleOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import type { ExportJob } from "../../services/export";
import ModernCard from "../ModernCard";

interface ExportJobListProps {
  jobs: ExportJob[];
  loading?: boolean;
  onDownload: (jobId: string) => void;
  onCancel: (jobId: string) => void;
  onRefresh: (jobId: string) => void;
}

const ExportJobList: React.FC<ExportJobListProps> = ({
  jobs,
  loading = false,
  onDownload,
  onCancel,
  onRefresh,
}) => {
  const { t } = useTranslation();

  const getJobTypeIcon = (type: string) => {
    switch (type) {
      case "conversations":
        return <FileTextOutlined />;
      case "knowledge":
        return <DatabaseOutlined />;
      case "analytics":
        return <BarChartOutlined />;
      case "system":
        return <SettingOutlined />;
      case "users":
        return <UserOutlined />;
      case "assistants":
        return <RobotOutlined />;
      default:
        return <FileTextOutlined />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircleOutlined style={{ color: "#52c41a" }} />;
      case "processing":
        return <ClockCircleOutlined style={{ color: "#1890ff" }} />;
      case "pending":
        return <ClockCircleOutlined style={{ color: "#faad14" }} />;
      case "failed":
        return <CloseCircleOutlined style={{ color: "#ff4d4f" }} />;
      default:
        return <ExclamationCircleOutlined style={{ color: "#faad14" }} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "success";
      case "processing":
        return "processing";
      case "pending":
        return "warning";
      case "failed":
        return "error";
      default:
        return "default";
    }
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return "-";
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const columns = [
    {
      title: t("export.job_type"),
      dataIndex: "type",
      key: "type",
      render: (type: string) => (
        <Space>
          {getJobTypeIcon(type)}
          <span>{t(`export.types.${type}`)}</span>
        </Space>
      ),
    },
    {
      title: t("export.status"),
      dataIndex: "status",
      key: "status",
      render: (status: string, record: ExportJob) => (
        <Space direction="vertical" size="small" style={{ width: "100%" }}>
          <Space>
            {getStatusIcon(status)}
            <Tag color={getStatusColor(status)}>
              {t(`export.status.${status}`)}
            </Tag>
          </Space>
          {status === "processing" && (
            <Progress
              percent={record.progress}
              size="small"
              status="active"
              style={{ marginTop: 4 }}
            />
          )}
        </Space>
      ),
    },
    {
      title: t("export.file_size"),
      dataIndex: "fileSize",
      key: "fileSize",
      render: (fileSize?: number) => formatFileSize(fileSize),
    },
    {
      title: t("export.record_count"),
      dataIndex: "recordCount",
      key: "recordCount",
      render: (count?: number) => (count ? count.toLocaleString() : "-"),
    },
    {
      title: t("export.created_at"),
      dataIndex: "createdAt",
      key: "createdAt",
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: t("export.completed_at"),
      dataIndex: "completedAt",
      key: "completedAt",
      render: (date?: string) => (date ? new Date(date).toLocaleString() : "-"),
    },
    {
      title: t("export.actions"),
      key: "actions",
      render: (_, record: ExportJob) => (
        <Space>
          {record.status === "completed" && (
            <Tooltip title={t("export.download")}>
              <ModernButton
                variant="primary"
                icon={<DownloadOutlined />}
                size="sm"
                onClick={() => onDownload(record.id)}
              >
                {t("export.download")}
              </ModernButton>
            </Tooltip>
          )}

          {record.status === "processing" && (
            <Tooltip title={t("export.cancel")}>
              <Popconfirm
                title={t("export.cancel_confirm")}
                onConfirm={() => onCancel(record.id)}
                okText={t("common.yes")}
                cancelText={t("common.no")}
              >
                <ModernButton
                  variant="error"
                  icon={<DeleteOutlined />}
                  size="sm"
                >
                  {t("export.cancel")}
                </ModernButton>
              </Popconfirm>
            </Tooltip>
          )}

          {(record.status === "pending" || record.status === "processing") && (
            <Tooltip title={t("export.refresh_status")}>
              <ModernButton
                icon={<ReloadOutlined />}
                size="sm"
                onClick={() => onRefresh(record.id)}
              >
                {t("export.refresh")}
              </ModernButton>
            </Tooltip>
          )}
        </Space>
      ),
    },
  ];

  return (
    <ModernCard title={t("export.jobs")}>
      <Table
        columns={columns}
        dataSource={jobs}
        rowKey="id"
        loading={loading}
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) =>
            t("common.showing_range", {
              start: range[0],
              end: range[1],
              total,
            }),
        }}
        expandable={{
          expandedRowRender: (record) => (
            <div style={{ padding: "16px" }}>
              <h4>{t("export.job_details")}</h4>
              <div style={{ marginBottom: "8px" }}>
                <strong>{t("export.format")}:</strong>{" "}
                {record.options.format.toUpperCase()}
              </div>
              {record.options.dateRange && (
                <div style={{ marginBottom: "8px" }}>
                  <strong>{t("export.date_range")}:</strong>
                  {new Date(
                    record.options.dateRange.start,
                  ).toLocaleDateString()}{" "}
                  -{new Date(record.options.dateRange.end).toLocaleDateString()}
                </div>
              )}
              {record.options.includeMetadata && (
                <div style={{ marginBottom: "8px" }}>
                  <strong>{t("export.include_metadata")}:</strong>{" "}
                  {t("common.yes")}
                </div>
              )}
              {record.options.compression && (
                <div style={{ marginBottom: "8px" }}>
                  <strong>{t("export.compression")}:</strong> {t("common.yes")}
                </div>
              )}
              {record.error && (
                <div style={{ marginTop: "8px", color: "#ff4d4f" }}>
                  <strong>{t("export.error")}:</strong> {record.error}
                </div>
              )}
            </div>
          ),
        }}
      />
    </ModernCard>
  );
};

export default ExportJobList;
