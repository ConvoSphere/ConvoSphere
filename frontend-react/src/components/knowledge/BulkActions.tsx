import React, { useState } from "react";
import {
  Modal,
  Form,
  Select,
  Button,
  Space,
  Typography,
  Alert,
  Progress,
  List,
  Tag,
  message,
} from "antd";
import {
  DeleteOutlined,
  TagOutlined,
  ReloadOutlined,
  DownloadOutlined,
  ExclamationCircleOutlined,
} from "@ant-design/icons";
import type { Document } from "../../services/knowledge";
import { useTags } from "../../store/knowledgeStore";

const { Title, Text } = Typography;
const { Option } = Select;

interface BulkActionsProps {
  visible: boolean;
  onCancel: () => void;
  selectedDocuments: Document[];
  onBulkDelete?: (documentIds: string[]) => Promise<void>;
  onBulkTag?: (documentIds: string[], tagNames: string[]) => Promise<void>;
  onBulkReprocess?: (documentIds: string[]) => Promise<void>;
  onBulkDownload?: (documentIds: string[]) => Promise<void>;
}

const BulkActions: React.FC<BulkActionsProps> = ({
  visible,
  onCancel,
  selectedDocuments,
  onBulkDelete,
  onBulkTag,
  onBulkReprocess,
  onBulkDownload,
}) => {
  const { tags } = useTags();
  const [actionType, setActionType] = useState<
    "delete" | "tag" | "reprocess" | "download"
  >("tag");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [form] = Form.useForm();

  const handleAction = async (values: any) => {
    setLoading(true);
    setProgress(0);

    const documentIds = selectedDocuments.map((doc) => doc.id);

    try {
      switch (actionType) {
        case "delete":
          if (onBulkDelete) {
            await onBulkDelete(documentIds);
            message.success(
              `${selectedDocuments.length} documents deleted successfully`,
            );
          }
          break;

        case "tag":
          if (onBulkTag && values.tagNames) {
            await onBulkTag(documentIds, values.tagNames);
            message.success(
              `Tags applied to ${selectedDocuments.length} documents`,
            );
          }
          break;

        case "reprocess":
          if (onBulkReprocess) {
            await onBulkReprocess(documentIds);
            message.success(
              `${selectedDocuments.length} documents queued for reprocessing`,
            );
          }
          break;

        case "download":
          if (onBulkDownload) {
            await onBulkDownload(documentIds);
            message.success(
              `Download started for ${selectedDocuments.length} documents`,
            );
          }
          break;
      }

      onCancel();
      form.resetFields();
    } catch (error) {
      message.error("Failed to perform bulk action");
    } finally {
      setLoading(false);
      setProgress(0);
    }
  };

  const getActionTitle = () => {
    switch (actionType) {
      case "delete":
        return "Delete Documents";
      case "tag":
        return "Apply Tags";
      case "reprocess":
        return "Reprocess Documents";
      case "download":
        return "Download Documents";
      default:
        return "Bulk Actions";
    }
  };

  const getActionDescription = () => {
    switch (actionType) {
      case "delete":
        return `This will permanently delete ${selectedDocuments.length} selected documents. This action cannot be undone.`;
      case "tag":
        return `Apply tags to ${selectedDocuments.length} selected documents.`;
      case "reprocess":
        return `Queue ${selectedDocuments.length} selected documents for reprocessing.`;
      case "download":
        return `Download ${selectedDocuments.length} selected documents.`;
      default:
        return "";
    }
  };

  const getActionIcon = () => {
    switch (actionType) {
      case "delete":
        return <DeleteOutlined />;
      case "tag":
        return <TagOutlined />;
      case "reprocess":
        return <ReloadOutlined />;
      case "download":
        return <DownloadOutlined />;
      default:
        return null;
    }
  };

  const getActionButtonText = () => {
    switch (actionType) {
      case "delete":
        return "Delete Documents";
      case "tag":
        return "Apply Tags";
      case "reprocess":
        return "Queue for Reprocessing";
      case "download":
        return "Start Download";
      default:
        return "Execute";
    }
  };

  const getActionButtonType = () => {
    switch (actionType) {
      case "delete":
        return "primary" as const;
      case "tag":
        return "primary" as const;
      case "reprocess":
        return "default" as const;
      case "download":
        return "default" as const;
      default:
        return "primary" as const;
    }
  };

  const getActionButtonDanger = () => {
    return actionType === "delete";
  };

  const renderActionForm = () => {
    switch (actionType) {
      case "tag":
        return (
          <Form.Item
            name="tagNames"
            label="Select Tags"
            rules={[
              { required: true, message: "Please select at least one tag" },
            ]}
          >
            <Select
              mode="multiple"
              placeholder="Select tags to apply"
              style={{ width: "100%" }}
              maxTagCount={5}
            >
              {tags.map((tag) => (
                <Option key={tag.id} value={tag.name}>
                  <Space>
                    <Tag color={tag.color || "#1890ff"}>{tag.name}</Tag>
                    <Text type="secondary">({tag.usage_count})</Text>
                  </Space>
                </Option>
              ))}
            </Select>
          </Form.Item>
        );

      case "reprocess":
        return (
          <Form.Item name="processingOptions" label="Processing Options">
            <Select
              mode="multiple"
              placeholder="Select processing options (optional)"
              style={{ width: "100%" }}
            >
              <Option value="extract_metadata">Extract Metadata</Option>
              <Option value="detect_language">Detect Language</Option>
              <Option value="generate_keywords">Generate Keywords</Option>
              <Option value="improve_chunking">Improve Chunking</Option>
            </Select>
          </Form.Item>
        );

      case "download":
        return (
          <Form.Item
            name="downloadFormat"
            label="Download Format"
            initialValue="original"
          >
            <Select style={{ width: "100%" }}>
              <Option value="original">Original Files</Option>
              <Option value="pdf">Convert to PDF</Option>
              <Option value="text">Extract Text Only</Option>
              <Option value="zip">ZIP Archive</Option>
            </Select>
          </Form.Item>
        );

      default:
        return null;
    }
  };

  const renderDocumentList = () => (
    <div style={{ maxHeight: 200, overflowY: "auto", marginBottom: 16 }}>
      <List
        size="small"
        dataSource={selectedDocuments}
        renderItem={(doc) => (
          <List.Item>
            <List.Item.Meta
              title={doc.title}
              description={
                <Space size="small">
                  <Tag>{doc.document_type || "Unknown"}</Tag>
                  <Text type="secondary">{doc.file_name}</Text>
                  {doc.author && <Text type="secondary">by {doc.author}</Text>}
                </Space>
              }
            />
          </List.Item>
        )}
      />
    </div>
  );

  return (
    <Modal
      title={
        <Space>
          {getActionIcon()}
          <span>{getActionTitle()}</span>
        </Space>
      }
      open={visible}
      onCancel={onCancel}
      footer={null}
      width={600}
    >
      <div style={{ marginBottom: 16 }}>
        <Text type="secondary">{getActionDescription()}</Text>
      </div>

      {actionType === "delete" && (
        <Alert
          message="Warning"
          description="This action will permanently delete the selected documents and cannot be undone."
          type="warning"
          showIcon
          icon={<ExclamationCircleOutlined />}
          style={{ marginBottom: 16 }}
        />
      )}

      <div style={{ marginBottom: 16 }}>
        <Title level={5}>Selected Documents ({selectedDocuments.length})</Title>
        {renderDocumentList()}
      </div>

      <Form form={form} layout="vertical" onFinish={handleAction}>
        <Form.Item
          name="actionType"
          label="Action Type"
          initialValue={actionType}
        >
          <Select onChange={setActionType} style={{ width: "100%" }}>
            <Option value="tag">Apply Tags</Option>
            <Option value="reprocess">Reprocess Documents</Option>
            <Option value="download">Download Documents</Option>
            <Option value="delete">Delete Documents</Option>
          </Select>
        </Form.Item>

        {renderActionForm()}

        {loading && (
          <div style={{ marginBottom: 16 }}>
            <Progress percent={progress} status="active" />
            <Text type="secondary">Processing...</Text>
          </div>
        )}

        <Form.Item>
          <Space>
            <Button
              type={getActionButtonType()}
              danger={getActionButtonDanger()}
              icon={getActionIcon()}
              loading={loading}
              htmlType="submit"
            >
              {getActionButtonText()}
            </Button>
            <Button onClick={onCancel} disabled={loading}>
              Cancel
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default BulkActions;
