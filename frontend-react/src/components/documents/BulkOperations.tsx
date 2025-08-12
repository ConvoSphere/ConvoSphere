import React, { useState } from "react";
import {
  Card,
  Space,
  Typography,
  Button,
  Modal,
  Checkbox,
  Select,
  Input,
  Tag,
  Progress,
  Alert,
  List,
  Divider,
  Tooltip,
  Popconfirm,
} from "antd";
import {
  DeleteOutlined,
  DownloadOutlined,
  TagOutlined,
  EditOutlined,
  CheckOutlined,
  CloseOutlined,
  ExclamationCircleOutlined,
  FileTextOutlined,
  FolderOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { Document } from "../../services/knowledge";
import ModernCard from "../ModernCard";
import ModernButton from "../ModernButton";
import ModernSelect from "../ModernSelect";
import ModernInput from "../ModernInput";

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

interface BulkOperationsProps {
  documents: Document[];
  selectedDocuments: string[];
  onSelectionChange: (selectedIds: string[]) => void;
  onBulkDelete: (documentIds: string[]) => Promise<void>;
  onBulkDownload: (documentIds: string[]) => Promise<void>;
  onBulkTag: (documentIds: string[], tags: string[]) => Promise<void>;
  onBulkMove: (documentIds: string[], folder: string) => Promise<void>;
  loading?: boolean;
}

interface BulkOperation {
  type: "delete" | "download" | "tag" | "move";
  status: "pending" | "processing" | "completed" | "failed";
  progress: number;
  total: number;
  completed: number;
  failed: number;
  errors: string[];
}

const BulkOperations: React.FC<BulkOperationsProps> = ({
  documents,
  selectedDocuments,
  onSelectionChange,
  onBulkDelete,
  onBulkDownload,
  onBulkTag,
  onBulkMove,
  loading = false,
}) => {
  const { t } = useTranslation();
  const [currentOperation, setCurrentOperation] =
    useState<BulkOperation | null>(null);
  const [showTagModal, setShowTagModal] = useState(false);
  const [showMoveModal, setShowMoveModal] = useState(false);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [newTag, setNewTag] = useState("");
  const [selectedFolder, setSelectedFolder] = useState("");
  const [availableTags, setAvailableTags] = useState<string[]>([
    "important",
    "draft",
    "final",
    "review",
    "archived",
  ]);

  const selectedDocs = documents.filter((doc) =>
    selectedDocuments.includes(doc.id),
  );

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      onSelectionChange(documents.map((doc) => doc.id));
    } else {
      onSelectionChange([]);
    }
  };

  const handleSelectDocument = (documentId: string, checked: boolean) => {
    if (checked) {
      onSelectionChange([...selectedDocuments, documentId]);
    } else {
      onSelectionChange(selectedDocuments.filter((id) => id !== documentId));
    }
  };

  const handleBulkDelete = async () => {
    if (selectedDocuments.length === 0) return;

    Modal.confirm({
      title: t("bulk.delete_confirm_title", "Dokumente löschen"),
      content: (
        <div>
          <Paragraph>
            {t(
              "bulk.delete_confirm_message",
              "Sind Sie sicher, dass Sie {{count}} Dokumente löschen möchten?",
              {
                count: selectedDocuments.length,
              },
            )}
          </Paragraph>
          <Alert
            message={t(
              "bulk.delete_warning",
              "Diese Aktion kann nicht rückgängig gemacht werden",
            )}
            type="warning"
            showIcon
          />
        </div>
      ),
      okText: t("bulk.delete", "Löschen"),
      cancelText: t("common.cancel", "Abbrechen"),
      okType: "danger",
      onOk: async () => {
        await executeBulkOperation("delete", onBulkDelete);
      },
    });
  };

  const handleBulkDownload = async () => {
    if (selectedDocuments.length === 0) return;
    await executeBulkOperation("download", onBulkDownload);
  };

  const handleBulkTag = () => {
    if (selectedDocuments.length === 0) return;
    setShowTagModal(true);
  };

  const handleBulkMove = () => {
    if (selectedDocuments.length === 0) return;
    setShowMoveModal(true);
  };

  const executeBulkOperation = async (
    type: BulkOperation["type"],
    operation: (ids: string[], ...args: any[]) => Promise<void>,
    ...args: any[]
  ) => {
    const operationData: BulkOperation = {
      type,
      status: "processing",
      progress: 0,
      total: selectedDocuments.length,
      completed: 0,
      failed: 0,
      errors: [],
    };

    setCurrentOperation(operationData);

    try {
      await operation(selectedDocuments, ...args);

      setCurrentOperation({
        ...operationData,
        status: "completed",
        progress: 100,
        completed: selectedDocuments.length,
      });

      // Clear selection after successful operation
      onSelectionChange([]);

      // Hide operation status after 3 seconds
      setTimeout(() => setCurrentOperation(null), 3000);
    } catch (error) {
      setCurrentOperation({
        ...operationData,
        status: "failed",
        errors: [error instanceof Error ? error.message : "Unknown error"],
      });
    }
  };

  const handleTagSubmit = async () => {
    if (selectedTags.length === 0) return;

    await executeBulkOperation("tag", onBulkTag, selectedTags);
    setShowTagModal(false);
    setSelectedTags([]);
  };

  const handleMoveSubmit = async () => {
    if (!selectedFolder) return;

    await executeBulkOperation("move", onBulkMove, selectedFolder);
    setShowMoveModal(false);
    setSelectedFolder("");
  };

  const addNewTag = () => {
    if (newTag.trim() && !availableTags.includes(newTag.trim())) {
      setAvailableTags((prev) => [...prev, newTag.trim()]);
      setSelectedTags((prev) => [...prev, newTag.trim()]);
      setNewTag("");
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const getTotalSize = (): number => {
    return selectedDocs.reduce((total, doc) => total + (doc.file_size || 0), 0);
  };

  const getOperationIcon = (type: string) => {
    switch (type) {
      case "delete":
        return <DeleteOutlined />;
      case "download":
        return <DownloadOutlined />;
      case "tag":
        return <TagOutlined />;
      case "move":
        return <FolderOutlined />;
      default:
        return <FileTextOutlined />;
    }
  };

  const getOperationColor = (type: string) => {
    switch (type) {
      case "delete":
        return "#ff4d4f";
      case "download":
        return "#52c41a";
      case "tag":
        return "#1890ff";
      case "move":
        return "#722ed1";
      default:
        return "#8c8c8c";
    }
  };

  return (
    <div>
      {/* Selection Summary */}
      {selectedDocuments.length > 0 && (
        <ModernCard variant="elevated" size="md" style={{ marginBottom: 16 }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <div>
              <Title level={5} style={{ margin: 0 }}>
                {t("bulk.selected_count", "{{count}} Dokumente ausgewählt", {
                  count: selectedDocuments.length,
                })}
              </Title>
              <Text type="secondary">
                {t("bulk.total_size", "Gesamtgröße: {{size}}", {
                  size: formatFileSize(getTotalSize()),
                })}
              </Text>
            </div>
            <Space>
              <ModernButton
                variant="outlined"
                icon={<CloseOutlined />}
                onClick={() => onSelectionChange([])}
              >
                {t("bulk.clear_selection", "Auswahl aufheben")}
              </ModernButton>
            </Space>
          </div>
        </ModernCard>
      )}

      {/* Bulk Operations */}
      {selectedDocuments.length > 0 && (
        <ModernCard variant="elevated" size="md" style={{ marginBottom: 16 }}>
          <Title level={5} style={{ marginBottom: 16 }}>
            {t("bulk.operations", "Massenoperationen")}
          </Title>

          <Space wrap>
            <ModernButton
              variant="outlined"
              icon={<DownloadOutlined />}
              onClick={handleBulkDownload}
              disabled={loading}
            >
              {t("bulk.download", "Herunterladen")}
            </ModernButton>

            <ModernButton
              variant="outlined"
              icon={<TagOutlined />}
              onClick={handleBulkTag}
              disabled={loading}
            >
              {t("bulk.add_tags", "Tags hinzufügen")}
            </ModernButton>

            <ModernButton
              variant="outlined"
              icon={<FolderOutlined />}
              onClick={handleBulkMove}
              disabled={loading}
            >
              {t("bulk.move", "Verschieben")}
            </ModernButton>

            <Popconfirm
              title={t("bulk.delete_confirm", "Dokumente löschen?")}
              onConfirm={handleBulkDelete}
              okText={t("bulk.delete", "Löschen")}
              cancelText={t("common.cancel", "Abbrechen")}
            >
              <ModernButton
                variant="outlined"
                icon={<DeleteOutlined />}
                danger
                disabled={loading}
              >
                {t("bulk.delete", "Löschen")}
              </ModernButton>
            </Popconfirm>
          </Space>
        </ModernCard>
      )}

      {/* Operation Progress */}
      {currentOperation && (
        <ModernCard variant="elevated" size="md" style={{ marginBottom: 16 }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              marginBottom: 12,
            }}
          >
            <span style={{ color: getOperationColor(currentOperation.type) }}>
              {getOperationIcon(currentOperation.type)}
            </span>
            <Title level={5} style={{ margin: 0 }}>
              {t(
                `bulk.operation.${currentOperation.type}`,
                currentOperation.type,
              )}
            </Title>
            <Tag
              color={
                currentOperation.status === "completed"
                  ? "green"
                  : currentOperation.status === "failed"
                    ? "red"
                    : "blue"
              }
            >
              {t(
                `bulk.status.${currentOperation.status}`,
                currentOperation.status,
              )}
            </Tag>
          </div>

          <Progress
            percent={currentOperation.progress}
            status={
              currentOperation.status === "failed" ? "exception" : undefined
            }
            format={() =>
              `${currentOperation.completed}/${currentOperation.total}`
            }
          />

          {currentOperation.errors.length > 0 && (
            <Alert
              message={t("bulk.errors_occurred", "Fehler aufgetreten")}
              description={
                <ul style={{ margin: 0, paddingLeft: 16 }}>
                  {currentOperation.errors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              }
              type="error"
              showIcon
              style={{ marginTop: 12 }}
            />
          )}
        </ModernCard>
      )}

      {/* Document List */}
      <ModernCard variant="elevated" size="lg">
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: 16,
          }}
        >
          <Title level={4} style={{ margin: 0 }}>
            {t("documents.title", "Dokumente")}
          </Title>
          <Checkbox
            checked={
              selectedDocuments.length === documents.length &&
              documents.length > 0
            }
            indeterminate={
              selectedDocuments.length > 0 &&
              selectedDocuments.length < documents.length
            }
            onChange={(e) => handleSelectAll(e.target.checked)}
          >
            {t("bulk.select_all", "Alle auswählen")}
          </Checkbox>
        </div>

        <List
          dataSource={documents}
          renderItem={(document) => (
            <List.Item
              style={{
                padding: "12px 0",
                borderBottom: "1px solid #f0f0f0",
                display: "flex",
                alignItems: "center",
                gap: 12,
              }}
            >
              <Checkbox
                checked={selectedDocuments.includes(document.id)}
                onChange={(e) =>
                  handleSelectDocument(document.id, e.target.checked)
                }
              />

              <div style={{ flex: 1 }}>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    marginBottom: 4,
                  }}
                >
                  <FileTextOutlined style={{ color: "#1890ff" }} />
                  <Text strong>{document.title || document.filename}</Text>
                  <Tag
                    color={document.status === "processed" ? "green" : "orange"}
                  >
                    {t(`documents.status.${document.status}`, document.status)}
                  </Tag>
                </div>

                <Text type="secondary" style={{ fontSize: "12px" }}>
                  {document.filename} •{" "}
                  {formatFileSize(document.file_size || 0)} •{" "}
                  {new Date(document.created_at).toLocaleDateString()}
                </Text>

                {document.tags && document.tags.length > 0 && (
                  <div style={{ marginTop: 4 }}>
                    {document.tags.map((tag, index) => (
                      <Tag key={index} size="small">
                        {tag}
                      </Tag>
                    ))}
                  </div>
                )}
              </div>
            </List.Item>
          )}
        />
      </ModernCard>

      {/* Tag Modal */}
      <Modal
        title={t("bulk.add_tags", "Tags hinzufügen")}
        open={showTagModal}
        onCancel={() => setShowTagModal(false)}
        onOk={handleTagSubmit}
        okText={t("bulk.apply", "Anwenden")}
        cancelText={t("common.cancel", "Abbrechen")}
      >
        <div style={{ marginBottom: 16 }}>
          <Text strong>{t("bulk.select_tags", "Tags auswählen")}</Text>
          <ModernSelect
            mode="multiple"
            placeholder={t("bulk.select_tags_placeholder", "Tags auswählen")}
            value={selectedTags}
            onChange={setSelectedTags}
            style={{ width: "100%", marginTop: 8 }}
          >
            {availableTags.map((tag) => (
              <Option key={tag} value={tag}>
                {tag}
              </Option>
            ))}
          </ModernSelect>
        </div>

        <div>
          <Text strong>{t("bulk.add_new_tag", "Neuen Tag hinzufügen")}</Text>
          <Space.Compact style={{ width: "100%", marginTop: 8 }}>
            <ModernInput
              placeholder={t("bulk.new_tag_placeholder", "Neuer Tag")}
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              onPressEnter={addNewTag}
            />
            <ModernButton
              variant="outlined"
              onClick={addNewTag}
              disabled={!newTag.trim()}
            >
              {t("bulk.add", "Hinzufügen")}
            </ModernButton>
          </Space.Compact>
        </div>
      </Modal>

      {/* Move Modal */}
      <Modal
        title={t("bulk.move_documents", "Dokumente verschieben")}
        open={showMoveModal}
        onCancel={() => setShowMoveModal(false)}
        onOk={handleMoveSubmit}
        okText={t("bulk.move", "Verschieben")}
        cancelText={t("common.cancel", "Abbrechen")}
      >
        <div>
          <Text strong>{t("bulk.select_folder", "Ordner auswählen")}</Text>
          <ModernSelect
            placeholder={t(
              "bulk.select_folder_placeholder",
              "Ordner auswählen",
            )}
            value={selectedFolder}
            onChange={setSelectedFolder}
            style={{ width: "100%", marginTop: 8 }}
          >
            <Option value="documents">Documents</Option>
            <Option value="archived">Archived</Option>
            <Option value="drafts">Drafts</Option>
            <Option value="shared">Shared</Option>
          </ModernSelect>
        </div>
      </Modal>
    </div>
  );
};

export default BulkOperations;
