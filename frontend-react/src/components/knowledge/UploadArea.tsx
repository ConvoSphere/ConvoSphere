import React, { useState, useCallback } from "react";
import {
  Upload,
  Button,
  Progress,
  List,
  Card,
  Space,
  Typography,
  Alert,
  Tag,
  Tooltip,
} from "antd";
import {
  InboxOutlined,
  FileTextOutlined,
  FilePdfOutlined,
  FileWordOutlined,
  FileExcelOutlined,
  FileImageOutlined,
  FileZipOutlined,
  CloseOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  LoadingOutlined,
} from "@ant-design/icons";
import { useKnowledgeStore } from "../../store/knowledgeStore";
import { formatFileSize } from "../../utils/formatters";
import { 
  createFileValidator, 
  showValidationErrors, 
  showValidationWarnings,
  type FileValidationConfig 
} from "../../utils/fileValidation";
import { useQueryClient } from "@tanstack/react-query";

const { Dragger } = Upload;
const { Text, Title } = Typography;

interface UploadAreaProps {
  onUploadComplete?: () => void;
  maxFiles?: number;
  maxFileSize?: number; // in bytes
  allowedTypes?: string[];
  showQueue?: boolean;
  validationConfig?: Partial<FileValidationConfig>;
}

const UploadArea: React.FC<UploadAreaProps> = ({
  onUploadComplete,
  maxFiles = 10,
  maxFileSize = 100 * 1024 * 1024, // 100MB
  allowedTypes = [
    "pdf",
    "doc",
    "docx",
    "txt",
    "md",
    "xls",
    "xlsx",
    "ppt",
    "pptx",
  ],
  showQueue = true,
  validationConfig,
}) => {
  const { uploadQueue, addToUploadQueue, removeFromUploadQueue, uploadFiles } =
    useKnowledgeStore();
  const [dragOver, setDragOver] = useState(false);
  const queryClient = useQueryClient();
  
  // Create file validator with custom config
  const fileValidator = createFileValidator({
    maxFileSize,
    allowedTypes,
    maxFiles,
    ...validationConfig,
  });

  const getFileIcon = (fileType: string) => {
    const ext = fileType.split(".").pop()?.toLowerCase() || "";
    switch (ext) {
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
      case "zip":
      case "rar":
      case "7z":
        return <FileZipOutlined style={{ color: "#fa8c16" }} />;
      default:
        return <FileTextOutlined style={{ color: "#8c8c8c" }} />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircleOutlined style={{ color: "#52c41a" }} />;
      case "error":
        return <ExclamationCircleOutlined style={{ color: "#ff4d4f" }} />;
      case "uploading":
        return <LoadingOutlined style={{ color: "#1890ff" }} />;
      default:
        return null;
    }
  };

  const handleFileSelect = useCallback(
    (files: File[]) => {
      const { validFiles, invalidFiles, warnings } = fileValidator.validateFiles(files);

      if (invalidFiles.length > 0) {
        showValidationErrors(invalidFiles);
      }

      if (warnings.length > 0) {
        showValidationWarnings(warnings);
      }

      if (validFiles.length > 0) {
        addToUploadQueue(validFiles);
        uploadFiles(validFiles).then(async () => {
          onUploadComplete?.();
          await queryClient.invalidateQueries({ queryKey: ["knowledge-documents"] });
        });
      }
    },
    [fileValidator, addToUploadQueue, uploadFiles, onUploadComplete, queryClient],
  );

  const uploadProps = {
    name: "file",
    multiple: true,
    beforeUpload: (file: File) => {
      handleFileSelect([file]);
      return false; // Prevent default upload
    },
    showUploadList: false,
    accept: allowedTypes.map((type) => `.${type}`).join(","),
  };

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);

      const files = Array.from(e.dataTransfer.files);
      handleFileSelect(files);
    },
    [handleFileSelect],
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  }, []);

  const handleRemoveFromQueue = (id: string) => {
    removeFromUploadQueue(id);
  };

  const pendingFiles = uploadQueue.filter((item) => item.status === "pending");
  const uploadingFiles = uploadQueue.filter(
    (item) => item.status === "uploading",
  );
  const completedFiles = uploadQueue.filter(
    (item) => item.status === "completed",
  );
  const errorFiles = uploadQueue.filter((item) => item.status === "error");

  return (
    <Space direction="vertical" style={{ width: "100%" }} size="large">
      <Card>
        <Dragger
          {...uploadProps}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          style={{
            border: dragOver ? "2px dashed #1890ff" : "2px dashed #d9d9d9",
            backgroundColor: dragOver ? "#f0f8ff" : "#fafafa",
            transition: "all 0.3s",
          }}
        >
          <p className="ant-upload-drag-icon">
            <InboxOutlined
              style={{
                fontSize: "48px",
                color: dragOver ? "#1890ff" : "#8c8c8c",
              }}
            />
          </p>
          <p className="ant-upload-text">
            <Title level={4} style={{ margin: 0 }}>
              Click or drag files to upload
            </Title>
          </p>
          <p className="ant-upload-hint">
            <Text type="secondary">
              Support for {allowedTypes.join(", ").toUpperCase()} files up to{" "}
              {formatFileSize(maxFileSize)}
            </Text>
          </p>
        </Dragger>
      </Card>

      {showQueue && uploadQueue.length > 0 && (
        <Card title="Upload Queue" size="small">
          <Space direction="vertical" style={{ width: "100%" }} size="small">
            {/* Pending files */}
            {pendingFiles.length > 0 && (
              <div>
                <Text strong>Pending ({pendingFiles.length})</Text>
                <List
                  size="small"
                  dataSource={pendingFiles}
                  renderItem={(item) => (
                    <List.Item
                      actions={[
                        <Button
                          type="text"
                          size="small"
                          icon={<CloseOutlined />}
                          onClick={() => handleRemoveFromQueue(item.id)}
                        />,
                      ]}
                    >
                      <List.Item.Meta
                        avatar={getFileIcon(item.file.name)}
                        title={item.file.name}
                        description={`${formatFileSize(item.file.size)} - Waiting to upload`}
                      />
                    </List.Item>
                  )}
                />
              </div>
            )}

            {/* Uploading files */}
            {uploadingFiles.length > 0 && (
              <div>
                <Text strong>Uploading ({uploadingFiles.length})</Text>
                <List
                  size="small"
                  dataSource={uploadingFiles}
                  renderItem={(item) => (
                    <List.Item>
                      <List.Item.Meta
                        avatar={getFileIcon(item.file.name)}
                        title={item.file.name}
                        description={
                          <Space direction="vertical" style={{ width: "100%" }}>
                            <Text type="secondary">
                              {formatFileSize(item.file.size)} - Uploading...
                            </Text>
                            <Progress
                              percent={item.progress}
                              size="small"
                              status="active"
                              showInfo={false}
                            />
                          </Space>
                        }
                      />
                    </List.Item>
                  )}
                />
              </div>
            )}

            {/* Completed files */}
            {completedFiles.length > 0 && (
              <div>
                <Text strong type="success">
                  Completed ({completedFiles.length})
                </Text>
                <List
                  size="small"
                  dataSource={completedFiles}
                  renderItem={(item) => (
                    <List.Item
                      actions={[
                        <Tag color="success" icon={<CheckCircleOutlined />}>
                          Success
                        </Tag>,
                      ]}
                    >
                      <List.Item.Meta
                        avatar={getFileIcon(item.file.name)}
                        title={
                          <Tooltip
                            title={item.document?.title || item.file.name}
                          >
                            {item.document?.title || item.file.name}
                          </Tooltip>
                        }
                        description={`${formatFileSize(item.file.size)} - Uploaded successfully`}
                      />
                    </List.Item>
                  )}
                />
              </div>
            )}

            {/* Error files */}
            {errorFiles.length > 0 && (
              <div>
                <Text strong type="danger">
                  Failed ({errorFiles.length})
                </Text>
                <List
                  size="small"
                  dataSource={errorFiles}
                  renderItem={(item) => (
                    <List.Item
                      actions={[
                        <Button
                          type="text"
                          size="small"
                          icon={<CloseOutlined />}
                          onClick={() => handleRemoveFromQueue(item.id)}
                        />,
                      ]}
                    >
                      <List.Item.Meta
                        avatar={getFileIcon(item.file.name)}
                        title={item.file.name}
                        description={
                          <Space direction="vertical" style={{ width: "100%" }}>
                            <Text type="danger">
                              {item.error || "Upload failed"}
                            </Text>
                            <Button
                              size="small"
                              type="link"
                              onClick={() => {
                                handleRemoveFromQueue(item.id);
                                handleFileSelect([item.file]);
                              }}
                            >
                              Retry
                            </Button>
                          </Space>
                        }
                      />
                    </List.Item>
                  )}
                />
              </div>
            )}
          </Space>
        </Card>
      )}

      {/* Summary */}
      {uploadQueue.length > 0 && (
        <Alert
          message={`Upload Summary: ${completedFiles.length} completed, ${uploadingFiles.length} uploading, ${errorFiles.length} failed`}
          type={errorFiles.length > 0 ? "warning" : "success"}
          showIcon
          closable
          onClose={() => {
            // Clear completed and error files from queue
            uploadQueue.forEach((item) => {
              if (item.status === "completed" || item.status === "error") {
                handleRemoveFromQueue(item.id);
              }
            });
          }}
        />
      )}
    </Space>
  );
};

export default UploadArea;
