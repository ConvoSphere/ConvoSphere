import React, { useState, useEffect } from "react";
import {
  Modal,
  Form,
  Input,
  Select,
  DatePicker,
  Space,
  Button,
  Alert,
  Typography,
  Divider,
  Card,
  Row,
  Col,
  Tag,
  message,
  Spin,
} from "antd";
import {
  EditOutlined,
  SaveOutlined,
  CloseOutlined,
  FileTextOutlined,
  TagOutlined,
  UserOutlined,
  CalendarOutlined,
  InfoCircleOutlined,
} from "@ant-design/icons";
import type { Document, Tag } from "../../services/knowledge";
import { formatDate } from "../../utils/formatters";

const { TextArea } = Input;
const { Option } = Select;
const { Text, Title } = Typography;

interface BulkEditModalProps {
  visible: boolean;
  documents: Document[];
  tags: Tag[];
  onClose: () => void;
  onSave: (updates: BulkEditUpdates) => Promise<void>;
  loading?: boolean;
}

interface BulkEditUpdates {
  title?: string;
  description?: string;
  author?: string;
  source?: string;
  year?: number;
  language?: string;
  keywords?: string[];
  tags?: string[];
  // Special values for bulk operations
  titleMode: "keep" | "replace" | "append";
  descriptionMode: "keep" | "replace" | "append";
  tagsMode: "keep" | "replace" | "add" | "remove";
  keywordsMode: "keep" | "replace" | "add" | "remove";
}

const BulkEditModal: React.FC<BulkEditModalProps> = ({
  visible,
  documents,
  tags,
  onClose,
  onSave,
  loading = false,
}) => {
  const [form] = Form.useForm();
  const [saving, setSaving] = useState(false);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [selectedKeywords, setSelectedKeywords] = useState<string[]>([]);

  useEffect(() => {
    if (visible && documents.length > 0) {
      // Initialize form with common values from selected documents
      initializeForm();
    }
  }, [visible, documents]);

  const initializeForm = () => {
    if (documents.length === 0) return;

    // Find common values across documents
    const commonValues = findCommonValues();

    form.setFieldsValue({
      title: commonValues.title,
      description: commonValues.description,
      author: commonValues.author,
      source: commonValues.source,
      year: commonValues.year ? new Date(commonValues.year, 0, 1) : undefined,
      language: commonValues.language,
      titleMode: "keep",
      descriptionMode: "keep",
      tagsMode: "keep",
      keywordsMode: "keep",
    });

    setSelectedTags(commonValues.tags || []);
    setSelectedKeywords(commonValues.keywords || []);
  };

  const findCommonValues = () => {
    if (documents.length === 0) return {};

    const firstDoc = documents[0];
    const common = {
      title: firstDoc.title,
      description: firstDoc.description,
      author: firstDoc.author,
      source: firstDoc.source,
      year: firstDoc.year,
      language: firstDoc.language,
      tags: firstDoc.tag_names || [],
      keywords: firstDoc.keywords || [],
    };

    // Check if all documents have the same values
    for (const doc of documents.slice(1)) {
      if (doc.title !== common.title) common.title = undefined;
      if (doc.description !== common.description)
        common.description = undefined;
      if (doc.author !== common.author) common.author = undefined;
      if (doc.source !== common.source) common.source = undefined;
      if (doc.year !== common.year) common.year = undefined;
      if (doc.language !== common.language) common.language = undefined;

      // For arrays, find intersection
      if (common.tags) {
        const docTags = doc.tag_names || [];
        common.tags = common.tags.filter((tag) => docTags.includes(tag));
      }

      if (common.keywords) {
        const docKeywords = doc.keywords || [];
        common.keywords = common.keywords.filter((keyword) =>
          docKeywords.includes(keyword),
        );
      }
    }

    return common;
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      const values = await form.validateFields();

      const updates: BulkEditUpdates = {
        ...values,
        tags: selectedTags,
        keywords: selectedKeywords,
        year: values.year ? values.year.getFullYear() : undefined,
      };

      await onSave(updates);
      message.success(`Successfully updated ${documents.length} documents`);
      onClose();
    } catch (error) {
      console.error("Bulk edit error:", error);
      message.error("Failed to update documents");
    } finally {
      setSaving(false);
    }
  };

  const getFileTypeIcon = (fileType: string) => {
    switch (fileType.toLowerCase()) {
      case "pdf":
        return <FileTextOutlined style={{ color: "#ff4d4f" }} />;
      case "doc":
      case "docx":
        return <FileTextOutlined style={{ color: "#1890ff" }} />;
      case "xls":
      case "xlsx":
        return <FileTextOutlined style={{ color: "#52c41a" }} />;
      default:
        return <FileTextOutlined style={{ color: "#8c8c8c" }} />;
    }
  };

  const renderDocumentList = () => (
    <Card size="small" title={`Selected Documents (${documents.length})`}>
      <div style={{ maxHeight: "200px", overflowY: "auto" }}>
        {documents.map((doc, index) => (
          <div
            key={doc.id}
            style={{
              display: "flex",
              alignItems: "center",
              padding: "8px 0",
              borderBottom:
                index < documents.length - 1 ? "1px solid #f0f0f0" : "none",
            }}
          >
            {getFileTypeIcon(doc.file_type)}
            <div style={{ marginLeft: "8px", flex: 1 }}>
              <Text strong>{doc.title}</Text>
              <br />
              <Text type="secondary" style={{ fontSize: "12px" }}>
                {doc.file_name} • {formatDate(doc.created_at)}
              </Text>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );

  const renderModeSelector = (fieldName: string, label: string) => (
    <Form.Item
      name={`${fieldName}Mode`}
      label={`${label} Mode`}
      style={{ marginBottom: "8px" }}
    >
      <Select size="small">
        <Option value="keep">Keep existing values</Option>
        <Option value="replace">Replace with new value</Option>
        {fieldName === "title" || fieldName === "description" ? (
          <Option value="append">Append to existing value</Option>
        ) : (
          <>
            <Option value="add">Add to existing values</Option>
            <Option value="remove">Remove from existing values</Option>
          </>
        )}
      </Select>
    </Form.Item>
  );

  return (
    <Modal
      title={
        <Space>
          <EditOutlined />
          <span>Bulk Edit Documents</span>
        </Space>
      }
      open={visible}
      onCancel={onClose}
      width={800}
      footer={[
        <Button key="cancel" onClick={onClose} disabled={saving}>
          Cancel
        </Button>,
        <Button
          key="save"
          type="primary"
          icon={<SaveOutlined />}
          onClick={handleSave}
          loading={saving}
        >
          Save Changes
        </Button>,
      ]}
    >
      <Spin spinning={loading}>
        <Space direction="vertical" style={{ width: "100%" }} size="large">
          {renderDocumentList()}

          <Alert
            message="Bulk Edit Information"
            description="You can update multiple documents at once. Use the mode selectors to control how the changes are applied."
            type="info"
            showIcon
            icon={<InfoCircleOutlined />}
          />

          <Form form={form} layout="vertical">
            <Row gutter={16}>
              <Col span={12}>
                {renderModeSelector("title", "Title")}
                <Form.Item name="title" label="Title">
                  <Input placeholder="Document title" />
                </Form.Item>
              </Col>
              <Col span={12}>
                {renderModeSelector("description", "Description")}
                <Form.Item name="description" label="Description">
                  <TextArea rows={3} placeholder="Document description" />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="author" label="Author">
                  <Input placeholder="Document author" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="source" label="Source">
                  <Input placeholder="Document source" />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="year" label="Year">
                  <DatePicker
                    picker="year"
                    placeholder="Select year"
                    style={{ width: "100%" }}
                  />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="language" label="Language">
                  <Select placeholder="Select language" allowClear>
                    <Option value="en">English</Option>
                    <Option value="de">German</Option>
                    <Option value="fr">French</Option>
                    <Option value="es">Spanish</Option>
                    <Option value="it">Italian</Option>
                    <Option value="pt">Portuguese</Option>
                    <Option value="ru">Russian</Option>
                    <Option value="zh">Chinese</Option>
                    <Option value="ja">Japanese</Option>
                    <Option value="ko">Korean</Option>
                  </Select>
                </Form.Item>
              </Col>
            </Row>

            <Divider />

            <Row gutter={16}>
              <Col span={12}>
                {renderModeSelector("tags", "Tags")}
                <Form.Item label="Tags">
                  <Select
                    mode="tags"
                    placeholder="Select or create tags"
                    value={selectedTags}
                    onChange={setSelectedTags}
                    style={{ width: "100%" }}
                  >
                    {tags.map((tag) => (
                      <Option key={tag.id} value={tag.name}>
                        <Space>
                          <TagOutlined />
                          {tag.name}
                        </Space>
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
              <Col span={12}>
                {renderModeSelector("keywords", "Keywords")}
                <Form.Item label="Keywords">
                  <Select
                    mode="tags"
                    placeholder="Enter keywords"
                    value={selectedKeywords}
                    onChange={setSelectedKeywords}
                    style={{ width: "100%" }}
                  />
                </Form.Item>
              </Col>
            </Row>
          </Form>

          <Alert
            message="Preview of Changes"
            description={
              <div>
                <Text>This will affect {documents.length} document(s):</Text>
                <ul style={{ margin: "8px 0 0 0", paddingLeft: "20px" }}>
                  {documents.slice(0, 3).map((doc) => (
                    <li key={doc.id}>
                      <Text code>{doc.title}</Text>
                    </li>
                  ))}
                  {documents.length > 3 && (
                    <li>
                      <Text type="secondary">
                        ... and {documents.length - 3} more
                      </Text>
                    </li>
                  )}
                </ul>
              </div>
            }
            type="warning"
            showIcon
          />
        </Space>
      </Spin>
    </Modal>
  );
};

export default BulkEditModal;
