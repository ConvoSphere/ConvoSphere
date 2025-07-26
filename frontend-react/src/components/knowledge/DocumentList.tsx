import React, { useState } from "react";
import {
  Table,
  Button,
  Tag,
  Space,
  Tooltip,
  Popconfirm,
  Badge,
  Typography,
  Card,
} from "antd";
import {
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  DownloadOutlined,
  ReloadOutlined,
  FileTextOutlined,
  FilePdfOutlined,
  FileWordOutlined,
  FileExcelOutlined,
} from "@ant-design/icons";
import type { Document } from "../../services/knowledge";
import { formatFileSize, formatDate } from "../../utils/formatters";

const { Text } = Typography;

interface DocumentListProps {
  documents: Document[];
  loading: boolean;
  onView: (document: Document) => void;
  onEdit: (document: Document) => void;
  onDelete: (documentId: string) => void;
  onDownload: (document: Document) => void;
  onReprocess: (documentId: string) => void;
  selectedRowKeys: string[];
  onSelectionChange: (selectedRowKeys: string[]) => void;
}

const DocumentList: React.FC<DocumentListProps> = ({
  documents,
  loading,
  onView,
  onEdit,
  onDelete,
  onDownload,
  onReprocess,
  selectedRowKeys,
  onSelectionChange,
}) => {
  const [expandedRowKeys, setExpandedRowKeys] = useState<string[]>([]);

  const getFileIcon = (fileType: string) => {
    switch (fileType.toLowerCase()) {
      case "pdf":
        return <FilePdfOutlined style={{ color: "#ff4d4f" }} />;
      case "doc":
      case "docx":
        return <FileWordOutlined style={{ color: "#1890ff" }} />;
      case "xls":
      case "xlsx":
        return <FileExcelOutlined style={{ color: "#52c41a" }} />;
      default:
        return <FileTextOutlined style={{ color: "#8c8c8c" }} />;
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      UPLOADED: { color: "default", text: "Uploaded" },
      PROCESSING: { color: "processing", text: "Processing" },
      PROCESSED: { color: "success", text: "Processed" },
      ERROR: { color: "error", text: "Error" },
      REPROCESSING: { color: "warning", text: "Reprocessing" },
    };

    const config =
      statusConfig[status as keyof typeof statusConfig] ||
      statusConfig.UPLOADED;
    return <Badge status={config.color as any} text={config.text} />;
  };

  const columns = [
    {
      title: "Document",
      key: "document",
      render: (record: Document) => (
        <Space>
          {getFileIcon(record.file_type)}
          <div>
            <div style={{ fontWeight: 500 }}>{record.title}</div>
            <Text type="secondary" style={{ fontSize: "12px" }}>
              {record.file_name}
            </Text>
          </div>
        </Space>
      ),
      sorter: (a: Document, b: Document) => a.title.localeCompare(b.title),
    },
    {
      title: "Type",
      dataIndex: "document_type",
      key: "type",
      render: (type: string) =>
        type ? <Tag color="blue">{type}</Tag> : <Text type="secondary">-</Text>,
      filters: [
        { text: "PDF", value: "PDF" },
        { text: "Document", value: "DOCUMENT" },
        { text: "Text", value: "TEXT" },
        { text: "Spreadsheet", value: "SPREADSHEET" },
      ],
      onFilter: (value: string, record: Document) =>
        record.document_type === value,
    },
    {
      title: "Author",
      dataIndex: "author",
      key: "author",
      render: (author: string) => author || <Text type="secondary">-</Text>,
      sorter: (a: Document, b: Document) =>
        (a.author || "").localeCompare(b.author || ""),
    },
    {
      title: "Language",
      dataIndex: "language",
      key: "language",
      render: (language: string) =>
        language ? (
          <Tag color="green">{language.toUpperCase()}</Tag>
        ) : (
          <Text type="secondary">-</Text>
        ),
      filters: [
        { text: "English", value: "en" },
        { text: "German", value: "de" },
        { text: "French", value: "fr" },
        { text: "Spanish", value: "es" },
      ],
      onFilter: (value: string, record: Document) => record.language === value,
    },
    {
      title: "Year",
      dataIndex: "year",
      key: "year",
      render: (year: number) => year || <Text type="secondary">-</Text>,
      sorter: (a: Document, b: Document) => (a.year || 0) - (b.year || 0),
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (status: string) => getStatusBadge(status),
      filters: [
        { text: "Uploaded", value: "UPLOADED" },
        { text: "Processing", value: "PROCESSING" },
        { text: "Processed", value: "PROCESSED" },
        { text: "Error", value: "ERROR" },
        { text: "Reprocessing", value: "REPROCESSING" },
      ],
      onFilter: (value: string, record: Document) => record.status === value,
    },
    {
      title: "Tags",
      key: "tags",
      render: (record: Document) => (
        <Space wrap>
          {record.tag_names?.slice(0, 3).map((tag, index) => (
            <Tag key={index} color="blue">
              {tag}
            </Tag>
          ))}
          {record.tag_names && record.tag_names.length > 3 && (
            <Tag color="blue">+{record.tag_names.length - 3}</Tag>
          )}
        </Space>
      ),
    },
    {
      title: "Size",
      dataIndex: "file_size",
      key: "size",
      render: (size: number) => formatFileSize(size),
      sorter: (a: Document, b: Document) => a.file_size - b.file_size,
    },
    {
      title: "Uploaded",
      dataIndex: "created_at",
      key: "created_at",
      render: (date: string) => formatDate(date),
      sorter: (a: Document, b: Document) =>
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
    },
    {
      title: "Actions",
      key: "actions",
      render: (record: Document) => (
        <Space>
          <Tooltip title="View Details">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => onView(record)}
            />
          </Tooltip>
          <Tooltip title="Edit">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => onEdit(record)}
            />
          </Tooltip>
          <Tooltip title="Download">
            <Button
              type="text"
              icon={<DownloadOutlined />}
              onClick={() => onDownload(record)}
            />
          </Tooltip>
          {record.status === "ERROR" && (
            <Tooltip title="Reprocess">
              <Button
                type="text"
                icon={<ReloadOutlined />}
                onClick={() => onReprocess(record.id)}
              />
            </Tooltip>
          )}
          <Popconfirm
            title="Are you sure you want to delete this document?"
            onConfirm={() => onDelete(record.id)}
            okText="Yes"
            cancelText="No"
          >
            <Tooltip title="Delete">
              <Button type="text" danger icon={<DeleteOutlined />} />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const expandedRowRender = (record: Document) => (
    <Card size="small" style={{ margin: "8px 0" }}>
      <Space direction="vertical" style={{ width: "100%" }}>
        {record.description && (
          <div>
            <Text strong>Description:</Text> {record.description}
          </div>
        )}
        {record.source && (
          <div>
            <Text strong>Source:</Text> {record.source}
          </div>
        )}
        {record.version && (
          <div>
            <Text strong>Version:</Text> {record.version}
          </div>
        )}
        {record.keywords && record.keywords.length > 0 && (
          <div>
            <Text strong>Keywords:</Text>
            <Space wrap style={{ marginLeft: 8 }}>
              {record.keywords.map((keyword, index) => (
                <Tag key={index}>{keyword}</Tag>
              ))}
            </Space>
          </div>
        )}
        {record.page_count && (
          <div>
            <Text strong>Pages:</Text> {record.page_count}
          </div>
        )}
        {record.word_count && (
          <div>
            <Text strong>Words:</Text> {record.word_count.toLocaleString()}
          </div>
        )}
        {record.error_message && (
          <div>
            <Text strong type="danger">
              Error:
            </Text>{" "}
            {record.error_message}
          </div>
        )}
      </Space>
    </Card>
  );

  const rowSelection = {
    selectedRowKeys,
    onChange: onSelectionChange,
  };

  return (
    <Table
      columns={columns}
      dataSource={documents}
      loading={loading}
      rowKey="id"
      rowSelection={rowSelection}
      expandable={{
        expandedRowRender,
        expandedRowKeys,
        onExpandedRowsChange: setExpandedRowKeys,
      }}
      pagination={{
        showSizeChanger: true,
        showQuickJumper: true,
        showTotal: (total, range) =>
          `${range[0]}-${range[1]} of ${total} documents`,
        pageSizeOptions: ["10", "20", "50", "100"],
        defaultPageSize: 20,
      }}
      scroll={{ x: 1200 }}
    />
  );
};

export default DocumentList;
