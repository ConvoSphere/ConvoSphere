import React, { useState, useEffect } from "react";
import {
  Modal,
  Spin,
  Alert,
  Tabs,
  Typography,
  Space,
  Button,
  Tag,
  Divider,
  Card,
  Row,
  Col,
  Statistic,
} from "antd";
import {
  FileTextOutlined,
  FilePdfOutlined,
  FileWordOutlined,
  FileExcelOutlined,
  FileImageOutlined,
  DownloadOutlined,
  EyeOutlined,
  InfoCircleOutlined,
  TagOutlined,
  CalendarOutlined,
  UserOutlined,
  FileOutlined,
} from "@ant-design/icons";
import type { Document, DocumentChunk } from "../../services/knowledge";
import { formatFileSize, formatDate } from "../../utils/formatters";
import { FileValidator } from "../../utils/fileValidation";

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;

interface DocumentPreviewProps {
  document: Document | null;
  visible: boolean;
  onClose: () => void;
  onDownload?: (documentId: string) => void;
  onEdit?: (document: Document) => void;
  onReprocess?: (documentId: string) => void;
}

interface PreviewContent {
  type: "text" | "image" | "pdf" | "table" | "error";
  content?: string;
  url?: string;
  error?: string;
}

const DocumentPreview: React.FC<DocumentPreviewProps> = ({
  document,
  visible,
  onClose,
  onDownload,
  onEdit,
  onReprocess,
}) => {
  const [previewContent, setPreviewContent] = useState<PreviewContent | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("preview");

  useEffect(() => {
    if (document && visible) {
      loadPreviewContent();
    }
  }, [document, visible]);

  const loadPreviewContent = async () => {
    if (!document) return;

    setLoading(true);
    try {
      const content = await generatePreviewContent(document);
      setPreviewContent(content);
    } catch (error) {
      setPreviewContent({
        type: "error",
        error: "Failed to load preview content",
      });
    } finally {
      setLoading(false);
    }
  };

  const generatePreviewContent = async (doc: Document): Promise<PreviewContent> => {
    // Determine content type based on file type
    const fileType = doc.file_type.toLowerCase();
    
    if (FileValidator.isImage({ type: doc.mime_type || "" } as File)) {
      return {
        type: "image",
        url: `/api/v1/knowledge/documents/${doc.id}/download`,
      };
    } else if (fileType === "pdf") {
      return {
        type: "pdf",
        url: `/api/v1/knowledge/documents/${doc.id}/download`,
      };
    } else if (FileValidator.isDocument({ type: doc.mime_type || "" } as File)) {
      // For text-based documents, we could fetch the content
      return {
        type: "text",
        content: "Document content preview not available for this file type.",
      };
    } else if (FileValidator.isSpreadsheet({ type: doc.mime_type || "" } as File)) {
      return {
        type: "table",
        content: "Spreadsheet preview not available. Please download to view.",
      };
    } else {
      return {
        type: "text",
        content: "Preview not available for this file type.",
      };
    }
  };

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
      case "jpg":
      case "jpeg":
      case "png":
      case "gif":
        return <FileImageOutlined style={{ color: "#722ed1" }} />;
      default:
        return <FileTextOutlined style={{ color: "#8c8c8c" }} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "PROCESSED":
        return "success";
      case "PROCESSING":
        return "processing";
      case "ERROR":
        return "error";
      case "UPLOADED":
        return "default";
      default:
        return "default";
    }
  };

  const renderPreviewContent = () => {
    if (loading) {
      return (
        <div style={{ textAlign: "center", padding: "40px" }}>
          <Spin size="large" />
          <div style={{ marginTop: "16px" }}>Loading preview...</div>
        </div>
      );
    }

    if (!previewContent) {
      return (
        <Alert
          message="No preview available"
          description="This document type does not support preview."
          type="info"
          showIcon
        />
      );
    }

    switch (previewContent.type) {
      case "image":
        return (
          <div style={{ textAlign: "center" }}>
            <img
              src={previewContent.url}
              alt={document?.title}
              style={{ maxWidth: "100%", maxHeight: "500px" }}
            />
          </div>
        );

      case "pdf":
        return (
          <iframe
            src={previewContent.url}
            style={{ width: "100%", height: "600px", border: "none" }}
            title={document?.title}
          />
        );

      case "text":
        return (
          <Card>
            <Paragraph style={{ whiteSpace: "pre-wrap" }}>
              {previewContent.content}
            </Paragraph>
          </Card>
        );

      case "table":
        return (
          <Alert
            message="Spreadsheet Preview"
            description={previewContent.content}
            type="info"
            showIcon
          />
        );

      case "error":
        return (
          <Alert
            message="Preview Error"
            description={previewContent.error}
            type="error"
            showIcon
          />
        );

      default:
        return (
          <Alert
            message="Unsupported Format"
            description="Preview is not available for this file type."
            type="warning"
            showIcon
          />
        );
    }
  };

  const renderDocumentInfo = () => {
    if (!document) return null;

    return (
      <Card>
        <Row gutter={[16, 16]}>
          <Col span={12}>
            <Statistic
              title="File Size"
              value={formatFileSize(document.file_size)}
              prefix={<FileOutlined />}
            />
          </Col>
          <Col span={12}>
            <Statistic
              title="Word Count"
              value={document.word_count || 0}
              prefix={<FileTextOutlined />}
            />
          </Col>
          <Col span={12}>
            <Statistic
              title="Page Count"
              value={document.page_count || 0}
              prefix={<FileTextOutlined />}
            />
          </Col>
          <Col span={12}>
            <Statistic
              title="Character Count"
              value={document.character_count || 0}
              prefix={<FileTextOutlined />}
            />
          </Col>
        </Row>

        <Divider />

        <Space direction="vertical" style={{ width: "100%" }}>
          <div>
            <Text strong>Author:</Text>{" "}
            <Text>{document.author || "Unknown"}</Text>
          </div>
          <div>
            <Text strong>Source:</Text>{" "}
            <Text>{document.source || "Not specified"}</Text>
          </div>
          <div>
            <Text strong>Language:</Text>{" "}
            <Text>{document.language || "Not detected"}</Text>
          </div>
          <div>
            <Text strong>Year:</Text>{" "}
            <Text>{document.year || "Not specified"}</Text>
          </div>
          <div>
            <Text strong>Version:</Text>{" "}
            <Text>{document.version || "Not specified"}</Text>
          </div>
          <div>
            <Text strong>Processing Engine:</Text>{" "}
            <Text>{document.processing_engine || "Default"}</Text>
          </div>
        </Space>

        {document.keywords && document.keywords.length > 0 && (
          <>
            <Divider />
            <div>
              <Text strong>Keywords:</Text>
              <div style={{ marginTop: "8px" }}>
                {document.keywords.map((keyword, index) => (
                  <Tag key={index} style={{ marginBottom: "4px" }}>
                    {keyword}
                  </Tag>
                ))}
              </div>
            </div>
          </>
        )}
      </Card>
    );
  };

  const renderMetadata = () => {
    if (!document) return null;

    return (
      <Card>
        <Space direction="vertical" style={{ width: "100%" }}>
          <div>
            <Text strong>File Name:</Text>{" "}
            <Text code>{document.file_name}</Text>
          </div>
          <div>
            <Text strong>File Type:</Text>{" "}
            <Text code>{document.file_type.toUpperCase()}</Text>
          </div>
          <div>
            <Text strong>MIME Type:</Text>{" "}
            <Text code>{document.mime_type || "Not detected"}</Text>
          </div>
          <div>
            <Text strong>Document Type:</Text>{" "}
            <Text code>{document.document_type || "Unknown"}</Text>
          </div>
          <div>
            <Text strong>Status:</Text>{" "}
            <Tag color={getStatusColor(document.status)}>
              {document.status}
            </Tag>
          </div>
          <div>
            <Text strong>Created:</Text>{" "}
            <Text>{formatDate(document.created_at)}</Text>
          </div>
          <div>
            <Text strong>Updated:</Text>{" "}
            <Text>{formatDate(document.updated_at)}</Text>
          </div>
          {document.processed_at && (
            <div>
              <Text strong>Processed:</Text>{" "}
              <Text>{formatDate(document.processed_at)}</Text>
            </div>
          )}
          {document.error_message && (
            <div>
              <Text strong>Error:</Text>{" "}
              <Text type="danger">{document.error_message}</Text>
            </div>
          )}
        </Space>
      </Card>
    );
  };

  if (!document) return null;

  return (
    <Modal
      title={
        <Space>
          {getFileIcon(document.file_type)}
          <span>{document.title}</span>
        </Space>
      }
      open={visible}
      onCancel={onClose}
      width={1000}
      footer={[
        <Button key="close" onClick={onClose}>
          Close
        </Button>,
        onDownload && (
          <Button
            key="download"
            type="primary"
            icon={<DownloadOutlined />}
            onClick={() => onDownload(document.id)}
          >
            Download
          </Button>
        ),
        onEdit && (
          <Button
            key="edit"
            icon={<FileTextOutlined />}
            onClick={() => onEdit(document)}
          >
            Edit
          </Button>
        ),
        onReprocess && (
          <Button
            key="reprocess"
            icon={<FileTextOutlined />}
            onClick={() => onReprocess(document.id)}
          >
            Reprocess
          </Button>
        ),
      ].filter(Boolean)}
    >
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane
          tab={
            <span>
              <EyeOutlined />
              Preview
            </span>
          }
          key="preview"
        >
          {renderPreviewContent()}
        </TabPane>
        <TabPane
          tab={
            <span>
              <InfoCircleOutlined />
              Information
            </span>
          }
          key="info"
        >
          {renderDocumentInfo()}
        </TabPane>
        <TabPane
          tab={
            <span>
              <TagOutlined />
              Metadata
            </span>
          }
          key="metadata"
        >
          {renderMetadata()}
        </TabPane>
      </Tabs>
    </Modal>
  );
};

export default DocumentPreview;