import React, { useState, useEffect } from "react";
import {
  Modal,
  Space,
  Typography,
  Button,
  Spin,
  Alert,
  Tabs,
  Tag,
  Divider,
  Descriptions,
} from "antd";
import {
  FileTextOutlined,
  FilePdfOutlined,
  FileImageOutlined,
  FileCodeOutlined,
  DownloadOutlined,
  EyeOutlined,
  CloseOutlined,
  LoadingOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { Document } from "../../services/knowledge";
import { LoadingState } from "../LoadingStates";

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;

interface DocumentPreviewProps {
  document: Document | null;
  visible: boolean;
  onClose: () => void;
  onDownload?: (documentId: string) => void;
}

interface FileTypeConfig {
  icon: React.ReactNode;
  color: string;
  previewComponent: React.ComponentType<{ document: Document }>;
  supported: boolean;
}

const DocumentPreview: React.FC<DocumentPreviewProps> = ({
  document,
  visible,
  onClose,
  onDownload,
}) => {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState("preview");
  const [loading, setLoading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string | null>(null);

  useEffect(() => {
    if (document && visible) {
      loadDocumentPreview();
    }
  }, [document, visible]);

  const loadDocumentPreview = async () => {
    if (!document) return;

    setLoading(true);
    try {
      // In a real implementation, you would fetch the document content
      // For now, we'll simulate loading
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Simulate different content based on file type
      const fileType = getFileType(document.filename);
      if (fileType === "pdf") {
        setPreviewUrl(`/api/documents/${document.id}/preview`);
      } else if (fileType === "text" || fileType === "code") {
        setFileContent("This is a sample document content...\n\nLorem ipsum dolor sit amet...");
      }
    } catch (error) {
      console.error("Failed to load document preview:", error);
    } finally {
      setLoading(false);
    }
  };

  const getFileType = (filename: string): string => {
    const extension = filename.split('.').pop()?.toLowerCase();
    
    if (['pdf'].includes(extension || '')) return 'pdf';
    if (['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp'].includes(extension || '')) return 'image';
    if (['txt', 'md', 'rtf'].includes(extension || '')) return 'text';
    if (['js', 'ts', 'jsx', 'tsx', 'py', 'java', 'cpp', 'c', 'html', 'css', 'json', 'xml'].includes(extension || '')) return 'code';
    
    return 'unknown';
  };

  const getFileTypeConfig = (filename: string): FileTypeConfig => {
    const fileType = getFileType(filename);
    
    const configs: Record<string, FileTypeConfig> = {
      pdf: {
        icon: <FilePdfOutlined />,
        color: "#ff4d4f",
        previewComponent: PDFPreview,
        supported: true,
      },
      image: {
        icon: <FileImageOutlined />,
        color: "#52c41a",
        previewComponent: ImagePreview,
        supported: true,
      },
      text: {
        icon: <FileTextOutlined />,
        color: "#1890ff",
        previewComponent: TextPreview,
        supported: true,
      },
      code: {
        icon: <FileCodeOutlined />,
        color: "#722ed1",
        previewComponent: CodePreview,
        supported: true,
      },
      unknown: {
        icon: <FileTextOutlined />,
        color: "#8c8c8c",
        previewComponent: UnsupportedPreview,
        supported: false,
      },
    };

    return configs[fileType] || configs.unknown;
  };

  const handleDownload = () => {
    if (document && onDownload) {
      onDownload(document.id);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString();
  };

  if (!document) return null;

  const fileConfig = getFileTypeConfig(document.filename);

  return (
    <Modal
      title={
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ color: fileConfig.color }}>{fileConfig.icon}</span>
          <Title level={4} style={{ margin: 0 }}>
            {document.title || document.filename}
          </Title>
        </div>
      }
      open={visible}
      onCancel={onClose}
      width="80%"
      style={{ top: 20 }}
      footer={
        <Space>
          <Button icon={<CloseOutlined />} onClick={onClose}>
            {t("common.close", "Schließen")}
          </Button>
          {onDownload && (
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              onClick={handleDownload}
            >
              {t("documents.download", "Herunterladen")}
            </Button>
          )}
        </Space>
      }
    >
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane
          tab={
            <Space>
              <EyeOutlined />
              {t("documents.preview", "Vorschau")}
            </Space>
          }
          key="preview"
        >
          <LoadingState loading={loading} error={null}>
            <div style={{ minHeight: "400px" }}>
              {fileConfig.supported ? (
                React.createElement(fileConfig.previewComponent, { document })
              ) : (
                <UnsupportedPreview document={document} />
              )}
            </div>
          </LoadingState>
        </TabPane>

        <TabPane
          tab={t("documents.details", "Details")}
          key="details"
        >
          <Descriptions bordered column={2}>
            <Descriptions.Item label={t("documents.filename", "Dateiname")}>
              {document.filename}
            </Descriptions.Item>
            <Descriptions.Item label={t("documents.title", "Titel")}>
              {document.title || "-"}
            </Descriptions.Item>
            <Descriptions.Item label={t("documents.description", "Beschreibung")}>
              {document.description || "-"}
            </Descriptions.Item>
            <Descriptions.Item label={t("documents.file_type", "Dateityp")}>
              <Tag color={fileConfig.color}>
                {getFileType(document.filename).toUpperCase()}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label={t("documents.file_size", "Dateigröße")}>
              {formatFileSize(document.file_size || 0)}
            </Descriptions.Item>
            <Descriptions.Item label={t("documents.upload_date", "Upload-Datum")}>
              {formatDate(document.created_at)}
            </Descriptions.Item>
            <Descriptions.Item label={t("documents.tags", "Tags")}>
              {document.tags && document.tags.length > 0 ? (
                <Space>
                  {document.tags.map((tag, index) => (
                    <Tag key={index} color="blue">
                      {tag}
                    </Tag>
                  ))}
                </Space>
              ) : (
                "-"
              )}
            </Descriptions.Item>
            <Descriptions.Item label={t("documents.status", "Status")}>
              <Tag color={document.status === "processed" ? "green" : "orange"}>
                {t(`documents.status.${document.status}`, document.status)}
              </Tag>
            </Descriptions.Item>
          </Descriptions>
        </TabPane>
      </Tabs>
    </Modal>
  );
};

// Preview Components
const PDFPreview: React.FC<{ document: Document }> = ({ document }) => {
  return (
    <div style={{ width: "100%", height: "600px" }}>
      <iframe
        src={`/api/documents/${document.id}/preview`}
        width="100%"
        height="100%"
        style={{ border: "none" }}
        title={document.title || document.filename}
      />
    </div>
  );
};

const ImagePreview: React.FC<{ document: Document }> = ({ document }) => {
  return (
    <div style={{ textAlign: "center" }}>
      <img
        src={`/api/documents/${document.id}/preview`}
        alt={document.title || document.filename}
        style={{ maxWidth: "100%", maxHeight: "600px", objectFit: "contain" }}
      />
    </div>
  );
};

const TextPreview: React.FC<{ document: Document }> = ({ document }) => {
  const [content, setContent] = useState<string>("");

  useEffect(() => {
    // In a real implementation, fetch the text content
    setContent("This is a sample text document content...\n\nLorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.");
  }, [document]);

  return (
    <div style={{ padding: "16px", backgroundColor: "#fafafa", borderRadius: "8px" }}>
      <pre style={{ 
        whiteSpace: "pre-wrap", 
        fontFamily: "monospace", 
        fontSize: "14px",
        lineHeight: "1.5",
        margin: 0
      }}>
        {content}
      </pre>
    </div>
  );
};

const CodePreview: React.FC<{ document: Document }> = ({ document }) => {
  const [content, setContent] = useState<string>("");

  useEffect(() => {
    // In a real implementation, fetch the code content with syntax highlighting
    setContent(`function example() {
  console.log("Hello, World!");
  return "This is a sample code file";
}

// Sample code content
const data = {
  name: "Document",
  type: "code",
  language: "javascript"
};`);
  }, [document]);

  return (
    <div style={{ padding: "16px", backgroundColor: "#1e1e1e", borderRadius: "8px" }}>
      <pre style={{ 
        whiteSpace: "pre-wrap", 
        fontFamily: "Consolas, Monaco, 'Courier New', monospace", 
        fontSize: "14px",
        lineHeight: "1.5",
        margin: 0,
        color: "#d4d4d4"
      }}>
        {content}
      </pre>
    </div>
  );
};

const UnsupportedPreview: React.FC<{ document: Document }> = ({ document }) => {
  const { t } = useTranslation();
  
  return (
    <div style={{ textAlign: "center", padding: "48px" }}>
      <FileTextOutlined style={{ fontSize: "64px", color: "#8c8c8c", marginBottom: "16px" }} />
      <Title level={4} style={{ color: "#8c8c8c" }}>
        {t("documents.preview_not_supported", "Vorschau nicht unterstützt")}
      </Title>
      <Paragraph type="secondary">
        {t("documents.preview_not_supported_desc", "Für diesen Dateityp ist keine Vorschau verfügbar. Sie können die Datei herunterladen, um sie zu öffnen.")}
      </Paragraph>
      <Tag color="orange">
        {document.filename.split('.').pop()?.toUpperCase() || "UNKNOWN"}
      </Tag>
    </div>
  );
};

export default DocumentPreview;