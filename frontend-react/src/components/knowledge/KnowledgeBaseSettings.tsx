import React, { useState, useEffect } from "react";
import {
  Typography,
  Space,
  Row,
  Col,
  message,
  Spin,
  Alert,
  Divider,
} from "antd";
import {
  SettingOutlined,
  SaveOutlined,
  ReloadOutlined,
  InfoCircleOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "../../store/authStore";
import { useThemeStore } from "../../store/themeStore";
import ModernCard from "../ModernCard";
import ModernButton from "../ModernButton";
import ModernInput from "../ModernInput";
import ModernSelect from "../ModernSelect";
import ModernForm, { ModernFormItem } from "../ModernForm";
import { Form } from "antd";
import { config } from "../../config";

const { Title, Text, Paragraph } = Typography;

interface KnowledgeBaseSettings {
  chunkSize: number;
  chunkOverlap: number;
  embeddingModel: string;
  indexType: "vector" | "hybrid";
  metadataExtraction: boolean;
  autoTagging: boolean;
  searchAlgorithm: "semantic" | "keyword" | "hybrid";
  maxFileSize: number;
  supportedFileTypes: string[];
  processingTimeout: number;
  batchSize: number;
  enableCache: boolean;
  cacheExpiry: number;
}

interface EmbeddingModel {
  id: string;
  name: string;
  provider: string;
  dimensions: number;
  maxTokens: number;
  costPerToken: number;
}

const KnowledgeBaseSettings: React.FC = () => {
  const { t } = useTranslation();
  const token = useAuthStore((s) => s.token);
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [settings, setSettings] = useState<KnowledgeBaseSettings>({
    chunkSize: 500,
    chunkOverlap: 50,
    embeddingModel: "text-embedding-ada-002",
    indexType: "hybrid",
    metadataExtraction: true,
    autoTagging: true,
    searchAlgorithm: "hybrid",
    maxFileSize: 10 * 1024 * 1024, // 10MB
    supportedFileTypes: [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "text/plain",
      "text/markdown",
    ],
    processingTimeout: 300,
    batchSize: 10,
    enableCache: true,
    cacheExpiry: 3600,
  });

  const [availableEmbeddingModels, setAvailableEmbeddingModels] = useState<EmbeddingModel[]>([
    {
      id: "text-embedding-ada-002",
      name: "OpenAI Ada-002",
      provider: "OpenAI",
      dimensions: 1536,
      maxTokens: 8191,
      costPerToken: 0.0001,
    },
    {
      id: "text-embedding-3-small",
      name: "OpenAI Text Embedding 3 Small",
      provider: "OpenAI",
      dimensions: 1536,
      maxTokens: 8191,
      costPerToken: 0.00002,
    },
    {
      id: "text-embedding-3-large",
      name: "OpenAI Text Embedding 3 Large",
      provider: "OpenAI",
      dimensions: 3072,
      maxTokens: 8191,
      costPerToken: 0.00013,
    },
    {
      id: "all-MiniLM-L6-v2",
      name: "Sentence Transformers MiniLM",
      provider: "HuggingFace",
      dimensions: 384,
      maxTokens: 256,
      costPerToken: 0,
    },
  ]);

  const [form] = Form.useForm();

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${config.apiUrl}/api/v1/knowledge/settings`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSettings(data);
        form.setFieldsValue(data);
      } else {
        // Use default settings if API is not available
        console.log("Using default KnowledgeBase settings");
      }
    } catch (err) {
      console.error("Error loading KnowledgeBase settings:", err);
      // Use default settings on error
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (values: KnowledgeBaseSettings) => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      const response = await fetch(`${config.apiUrl}/api/v1/knowledge/settings`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(values),
      });

      if (response.ok) {
        setSettings(values);
        setSuccess(t("knowledge.settings.saved_successfully"));
        message.success(t("knowledge.settings.saved_successfully"));
      } else {
        throw new Error("Failed to save settings");
      }
    } catch (err) {
      const errorMessage = t("knowledge.settings.save_failed");
      setError(errorMessage);
      message.error(errorMessage);
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    form.resetFields();
    setError(null);
    setSuccess(null);
  };

  const formatFileSize = (bytes: number) => {
    const sizes = ["B", "KB", "MB", "GB"];
    if (bytes === 0) return "0 B";
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${Math.round(bytes / Math.pow(1024, i) * 100) / 100} ${sizes[i]}`;
  };

  const getEmbeddingModelInfo = (modelId: string) => {
    return availableEmbeddingModels.find(model => model.id === modelId);
  };

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: "40px" }}>
        <Spin size="large" />
        <div style={{ marginTop: "16px" }}>
          {t("knowledge.settings.loading")}
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: "800px", margin: "0 auto" }}>
      <ModernCard variant="elevated" size="lg">
        <div style={{ textAlign: "center", marginBottom: "32px" }}>
          <Title level={2} style={{ marginBottom: "8px" }}>
            <SettingOutlined style={{ marginRight: "12px", color: colors.colorPrimary }} />
            {t("knowledge.settings.title")}
          </Title>
          <Text type="secondary">
            {t("knowledge.settings.description")}
          </Text>
        </div>

        {error && (
          <Alert
            message={error}
            type="error"
            showIcon
            style={{ marginBottom: "24px" }}
            closable
            onClose={() => setError(null)}
          />
        )}

        {success && (
          <Alert
            message={success}
            type="success"
            showIcon
            style={{ marginBottom: "24px" }}
            closable
            onClose={() => setSuccess(null)}
          />
        )}

        <ModernForm
          form={form}
          layout="vertical"
          onFinish={handleSave}
          initialValues={settings}
        >
          {/* Document Processing Settings */}
          <ModernCard variant="outlined" size="md" style={{ marginBottom: "24px" }}>
            <Title level={4} style={{ marginBottom: "16px" }}>
              {t("knowledge.settings.document_processing")}
            </Title>
            
            <Row gutter={16}>
              <Col span={12}>
                <ModernFormItem
                  name="chunkSize"
                  label={t("knowledge.settings.chunk_size")}
                  rules={[
                    { required: true, message: t("knowledge.settings.chunk_size_required") },
                    { type: "number", min: 100, max: 2000, message: t("knowledge.settings.chunk_size_range") }
                  ]}
                >
                  <ModernInput
                    type="number"
                    min={100}
                    max={2000}
                    suffix={t("knowledge.settings.characters")}
                  />
                </ModernFormItem>
              </Col>
              <Col span={12}>
                <ModernFormItem
                  name="chunkOverlap"
                  label={t("knowledge.settings.chunk_overlap")}
                  rules={[
                    { required: true, message: t("knowledge.settings.chunk_overlap_required") },
                    { type: "number", min: 0, max: 500, message: t("knowledge.settings.chunk_overlap_range") }
                  ]}
                >
                  <ModernInput
                    type="number"
                    min={0}
                    max={500}
                    suffix={t("knowledge.settings.characters")}
                  />
                </ModernFormItem>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={12}>
                <ModernFormItem
                  name="maxFileSize"
                  label={t("knowledge.settings.max_file_size")}
                  rules={[
                    { required: true, message: t("knowledge.settings.max_file_size_required") },
                    { type: "number", min: 1024 * 1024, max: 100 * 1024 * 1024, message: t("knowledge.settings.max_file_size_range") }
                  ]}
                >
                  <ModernInput
                    type="number"
                    min={1024 * 1024}
                    max={100 * 1024 * 1024}
                    suffix="bytes"
                  />
                </ModernFormItem>
                <Text type="secondary" style={{ fontSize: "12px" }}>
                  {t("knowledge.settings.current_size")}: {formatFileSize(settings.maxFileSize)}
                </Text>
              </Col>
              <Col span={12}>
                <ModernFormItem
                  name="processingTimeout"
                  label={t("knowledge.settings.processing_timeout")}
                  rules={[
                    { required: true, message: t("knowledge.settings.processing_timeout_required") },
                    { type: "number", min: 60, max: 3600, message: t("knowledge.settings.processing_timeout_range") }
                  ]}
                >
                  <ModernInput
                    type="number"
                    min={60}
                    max={3600}
                    suffix={t("knowledge.settings.seconds")}
                  />
                </ModernFormItem>
              </Col>
            </Row>
          </ModernCard>

          {/* Embedding and Indexing Settings */}
          <ModernCard variant="outlined" size="md" style={{ marginBottom: "24px" }}>
            <Title level={4} style={{ marginBottom: "16px" }}>
              {t("knowledge.settings.embedding_indexing")}
            </Title>
            
            <Row gutter={16}>
              <Col span={12}>
                <ModernFormItem
                  name="embeddingModel"
                  label={t("knowledge.settings.embedding_model")}
                  rules={[
                    { required: true, message: t("knowledge.settings.embedding_model_required") }
                  ]}
                >
                  <ModernSelect
                    placeholder={t("knowledge.settings.select_embedding_model")}
                    showSearch
                    filterOption={(input, option) =>
                      option?.children?.toLowerCase().includes(input.toLowerCase())
                    }
                  >
                    {availableEmbeddingModels.map(model => (
                      <ModernSelect.Option key={model.id} value={model.id}>
                        <div>
                          <div style={{ fontWeight: 500 }}>{model.name}</div>
                          <div style={{ fontSize: "12px", color: colors.colorTextSecondary }}>
                            {model.provider} • {model.dimensions}D • {model.maxTokens} tokens
                          </div>
                        </div>
                      </ModernSelect.Option>
                    ))}
                  </ModernSelect>
                </ModernFormItem>
                
                {settings.embeddingModel && (
                  <div style={{ marginTop: "8px", padding: "12px", backgroundColor: colors.colorBgElevated, borderRadius: "8px" }}>
                    <Text strong>{t("knowledge.settings.model_info")}:</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: "12px" }}>
                      {getEmbeddingModelInfo(settings.embeddingModel)?.name} • 
                      {getEmbeddingModelInfo(settings.embeddingModel)?.dimensions} dimensions • 
                      {getEmbeddingModelInfo(settings.embeddingModel)?.maxTokens} max tokens
                    </Text>
                  </div>
                )}
              </Col>
              <Col span={12}>
                <ModernFormItem
                  name="indexType"
                  label={t("knowledge.settings.index_type")}
                  rules={[
                    { required: true, message: t("knowledge.settings.index_type_required") }
                  ]}
                >
                  <ModernSelect placeholder={t("knowledge.settings.select_index_type")}>
                    <ModernSelect.Option value="vector">
                      {t("knowledge.settings.vector_index")}
                    </ModernSelect.Option>
                    <ModernSelect.Option value="hybrid">
                      {t("knowledge.settings.hybrid_index")}
                    </ModernSelect.Option>
                  </ModernSelect>
                </ModernFormItem>
                
                <ModernFormItem
                  name="searchAlgorithm"
                  label={t("knowledge.settings.search_algorithm")}
                  rules={[
                    { required: true, message: t("knowledge.settings.search_algorithm_required") }
                  ]}
                >
                  <ModernSelect placeholder={t("knowledge.settings.select_search_algorithm")}>
                    <ModernSelect.Option value="semantic">
                      {t("knowledge.settings.semantic_search")}
                    </ModernSelect.Option>
                    <ModernSelect.Option value="keyword">
                      {t("knowledge.settings.keyword_search")}
                    </ModernSelect.Option>
                    <ModernSelect.Option value="hybrid">
                      {t("knowledge.settings.hybrid_search")}
                    </ModernSelect.Option>
                  </ModernSelect>
                </ModernFormItem>
              </Col>
            </Row>
          </ModernCard>

          {/* Processing Options */}
          <ModernCard variant="outlined" size="md" style={{ marginBottom: "24px" }}>
            <Title level={4} style={{ marginBottom: "16px" }}>
              {t("knowledge.settings.processing_options")}
            </Title>
            
            <Row gutter={16}>
              <Col span={12}>
                <ModernFormItem
                  name="metadataExtraction"
                  valuePropName="checked"
                  label={t("knowledge.settings.metadata_extraction")}
                >
                  <ModernSelect>
                    <ModernSelect.Option value={true}>
                      {t("common.enabled")}
                    </ModernSelect.Option>
                    <ModernSelect.Option value={false}>
                      {t("common.disabled")}
                    </ModernSelect.Option>
                  </ModernSelect>
                </ModernFormItem>
                
                <ModernFormItem
                  name="autoTagging"
                  valuePropName="checked"
                  label={t("knowledge.settings.auto_tagging")}
                >
                  <ModernSelect>
                    <ModernSelect.Option value={true}>
                      {t("common.enabled")}
                    </ModernSelect.Option>
                    <ModernSelect.Option value={false}>
                      {t("common.disabled")}
                    </ModernSelect.Option>
                  </ModernSelect>
                </ModernFormItem>
              </Col>
              <Col span={12}>
                <ModernFormItem
                  name="batchSize"
                  label={t("knowledge.settings.batch_size")}
                  rules={[
                    { required: true, message: t("knowledge.settings.batch_size_required") },
                    { type: "number", min: 1, max: 100, message: t("knowledge.settings.batch_size_range") }
                  ]}
                >
                  <ModernInput
                    type="number"
                    min={1}
                    max={100}
                    suffix={t("knowledge.settings.documents")}
                  />
                </ModernFormItem>
                
                <ModernFormItem
                  name="enableCache"
                  valuePropName="checked"
                  label={t("knowledge.settings.enable_cache")}
                >
                  <ModernSelect>
                    <ModernSelect.Option value={true}>
                      {t("common.enabled")}
                    </ModernSelect.Option>
                    <ModernSelect.Option value={false}>
                      {t("common.disabled")}
                    </ModernSelect.Option>
                  </ModernSelect>
                </ModernFormItem>
              </Col>
            </Row>
          </ModernCard>

          {/* Actions */}
          <div style={{ display: "flex", gap: "12px", justifyContent: "center", marginTop: "32px" }}>
            <ModernButton
              type="primary"
              icon={<SaveOutlined />}
              loading={saving}
              htmlType="submit"
              size="lg"
            >
              {t("knowledge.settings.save_settings")}
            </ModernButton>
            
            <ModernButton
              icon={<ReloadOutlined />}
              onClick={handleReset}
              size="lg"
            >
              {t("knowledge.settings.reset")}
            </ModernButton>
          </div>
        </ModernForm>
      </ModernCard>
    </div>
  );
};

export default KnowledgeBaseSettings;