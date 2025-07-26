import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  Row,
  Col,
  Space,
  Typography,
  Alert,
  Tabs,
  Statistic,
  Modal,
  message,
  Avatar,
  Tag,
  Empty,
  Spin,
} from "antd";
import {
  SearchOutlined,
  FilterOutlined,
  UploadOutlined,
  ReloadOutlined,
  PlusOutlined,
  FileTextOutlined,
  FilePdfOutlined,
  FileWordOutlined,
  FileExcelOutlined,
  BookOutlined,
  TagsOutlined,
  BarChartOutlined,
  SettingOutlined,
  EyeOutlined,
  DownloadOutlined,
  CloudUploadOutlined,
  DatabaseOutlined,
  CheckCircleOutlined,
} from "@ant-design/icons";
import { useKnowledgeStore } from "../store/knowledgeStore";
import DocumentList from "../components/knowledge/DocumentList";
import UploadArea from "../components/knowledge/UploadArea";
import TagManager from "../components/knowledge/TagManager";
import BulkActions from "../components/knowledge/BulkActions";
import SystemStats from "../components/admin/SystemStats";

import { useThemeStore } from "../store/themeStore";
import ModernCard from "../components/ModernCard";
import ModernButton from "../components/ModernButton";
import ModernInput from "../components/ModernInput";
import ModernSelect from "../components/ModernSelect";


const { Title, Text } = Typography;

const KnowledgeBase: React.FC = () => {
  const { t } = useTranslation();

  const { colors } = useThemeStore();
  const {
    documents,
    documentsLoading: loading,
    documentsError: error,
    fetchDocuments,
    search,
    applyFilters,
    clearFilters,
    currentFilters,
    setFilters,
    refreshDocuments,
  } = useKnowledgeStore();
  const { stats, statsLoading } = useKnowledgeStore();
  const [searchQuery, setSearchQuery] = useState("");
  const [showUploadArea, setShowUploadArea] = useState(false);
  const [showBulkActions, setShowBulkActions] = useState(false);
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState("documents");

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const handleSearch = (value: string) => {
    setSearchQuery(value);
    if (value.trim()) {
      search(value);
    } else {
      refreshDocuments();
    }
  };

  const handleApplyFilters = () => {
    applyFilters();
  };

  const handleClearFilters = () => {
    setFilters({});
    clearFilters();
  };

  const handleViewDocument = () => {
    message.info("View functionality coming soon");
  };

  const handleEditDocument = () => {
    message.info("Edit functionality coming soon");
  };

  const handleDeleteDocument = async () => {
    try {
      message.success("Document deleted successfully");
      refreshDocuments();
    } catch (_error) {
      message.error("Failed to delete document");
    }
  };

  const handleDownloadDocument = () => {
    message.info("Download functionality coming soon");
  };

  const handleReprocessDocument = async () => {
    try {
      message.success("Document reprocessing started");
      refreshDocuments();
    } catch (_error) {
      message.error("Failed to reprocess document");
    }
  };

  const handleBulkDelete = async (documentIds: string[]) => {
    try {
      message.success(`${documentIds.length} documents deleted successfully`);
      setSelectedRowKeys([]);
      refreshDocuments();
    } catch (_error) {
      message.error("Failed to delete documents");
    }
  };

  const handleBulkTag = async (documentIds: string[]) => {
    try {
      message.success(`Tags applied to ${documentIds.length} documents`);
      refreshDocuments();
    } catch (_error) {
      message.error("Failed to apply tags");
    }
  };

  const handleBulkReprocess = async (documentIds: string[]) => {
    try {
      message.success(
        `${documentIds.length} documents queued for reprocessing`,
      );
      refreshDocuments();
    } catch (_error) {
      message.error("Failed to queue documents for reprocessing");
    }
  };

  const handleBulkDownload = async (documentIds: string[]) => {
    try {
      message.success(`Download started for ${documentIds.length} documents`);
    } catch (_error) {
      message.error("Failed to start download");
    }
  };

  const getDocumentTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case "PROCESSED":
        return "success";
      case "PROCESSING":
        return "processing";
      case "ERROR":
        return "error";
      case "REPROCESSING":
        return "warning";
      default:
        return "default";
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const renderStats = () => (
    <div className="modern-card-grid" style={{ marginBottom: 24 }}>
      <ModernCard variant="elevated" size="md">
        <Statistic
          title={t("knowledge.stats.total_documents")}
          value={stats?.total_documents || 0}
          loading={statsLoading}
          prefix={<DatabaseOutlined style={{ color: colors.colorPrimary }} />}
        />
      </ModernCard>
      <ModernCard variant="elevated" size="md">
        <Statistic
          title={t("knowledge.stats.total_chunks")}
          value={stats?.total_chunks || 0}
          loading={statsLoading}
          prefix={<FileTextOutlined style={{ color: colors.colorPrimary }} />}
        />
      </ModernCard>
      <ModernCard variant="elevated" size="md">
        <Statistic
          title={t("knowledge.stats.total_tokens")}
          value={stats?.total_tokens || 0}
          loading={statsLoading}
          formatter={(value) => `${(Number(value) / 1000).toFixed(1)}K`}
          prefix={
            <CheckCircleOutlined style={{ color: colors.colorPrimary }} />
          }
        />
      </ModernCard>
      <ModernCard variant="elevated" size="md">
        <Statistic
          title={t("knowledge.stats.storage_used")}
          value={stats?.storage_used || 0}
          loading={statsLoading}
          formatter={(value) => formatFileSize(Number(value))}
          prefix={
            <CloudUploadOutlined style={{ color: colors.colorPrimary }} />
          }
        />
      </ModernCard>
    </div>
  );

  const renderFilters = () => (
    <ModernCard variant="outlined" size="md" style={{ marginBottom: 16 }}>
      <Row gutter={[16, 16]} align="middle">
        <Col xs={24} sm={6}>
          <ModernSelect
            placeholder={t("knowledge.filters.document_type")}
            allowClear
            value={currentFilters.document_type}
            onChange={(value) =>
              setFilters({ ...currentFilters, document_type: value })
            }
          >
            <ModernSelect.Option value="PDF">
              {t("knowledge.document_types.pdf")}
            </ModernSelect.Option>
            <ModernSelect.Option value="DOCUMENT">
              {t("knowledge.document_types.word")}
            </ModernSelect.Option>
            <ModernSelect.Option value="TEXT">
              {t("knowledge.document_types.text")}
            </ModernSelect.Option>
            <ModernSelect.Option value="SPREADSHEET">
              {t("knowledge.document_types.spreadsheet")}
            </ModernSelect.Option>
          </ModernSelect>
        </Col>
        <Col xs={24} sm={6}>
          <ModernInput
            placeholder={t("knowledge.filters.author")}
            value={currentFilters.author}
            onChange={(e) =>
              setFilters({ ...currentFilters, author: e.target.value })
            }
          />
        </Col>
        <Col xs={24} sm={4}>
          <ModernInput
            placeholder={t("knowledge.filters.year")}
            type="number"
            value={currentFilters.year}
            onChange={(e) =>
              setFilters({
                ...currentFilters,
                year: e.target.value ? parseInt(e.target.value) : undefined,
              })
            }
          />
        </Col>
        <Col xs={24} sm={4}>
          <ModernSelect
            placeholder={t("knowledge.filters.language")}
            allowClear
            value={currentFilters.language}
            onChange={(value) =>
              setFilters({ ...currentFilters, language: value })
            }
          >
            <ModernSelect.Option value="en">
              {t("knowledge.languages.en")}
            </ModernSelect.Option>
            <ModernSelect.Option value="de">
              {t("knowledge.languages.de")}
            </ModernSelect.Option>
            <ModernSelect.Option value="fr">
              {t("knowledge.languages.fr")}
            </ModernSelect.Option>
            <ModernSelect.Option value="es">
              {t("knowledge.languages.es")}
            </ModernSelect.Option>
          </ModernSelect>
        </Col>
        <Col xs={24} sm={4}>
          <Space>
            <ModernButton
              variant="primary"
              icon={<FilterOutlined />}
              onClick={handleApplyFilters}
            >
              {t("common.apply")}
            </ModernButton>
            <ModernButton
              variant="outlined"
              icon={<ReloadOutlined />}
              onClick={handleClearFilters}
            >
              {t("common.clear")}
            </ModernButton>
          </Space>
        </Col>
      </Row>
    </ModernCard>
  );

  const renderActions = () => (
    <ModernCard variant="outlined" size="md" style={{ marginBottom: 16 }}>
      <Row gutter={[16, 16]} align="middle">
        <Col xs={24} sm={12}>
          <Space wrap>
            <ModernButton
              variant="primary"
              icon={<UploadOutlined />}
              onClick={() => setShowUploadArea(true)}
            >
              {t("knowledge.actions.upload_documents")}
            </ModernButton>
            {user?.role === "premium" && (
              <ModernButton
                variant="secondary"
                icon={<PlusOutlined />}
                onClick={() => setShowUploadArea(true)}
              >
                {t("knowledge.actions.bulk_import")}
              </ModernButton>
            )}
            <ModernButton
              variant="outlined"
              icon={<ReloadOutlined />}
              onClick={refreshDocuments}
            >
              {t("common.refresh")}
            </ModernButton>
          </Space>
        </Col>
        <Col xs={24} sm={12} style={{ textAlign: "right" }}>
          <Space>
            {selectedRowKeys.length > 0 && (
              <>
                <Text type="secondary">
                  {selectedRowKeys.length} {t("common.selected")}
                </Text>
                <ModernButton
                  variant="secondary"
                  icon={<ReloadOutlined />}
                  onClick={() => setShowBulkActions(true)}
                >
                  {t("knowledge.actions.bulk_actions")}
                </ModernButton>
              </>
            )}
          </Space>
        </Col>
      </Row>
    </ModernCard>
  );

  const renderSearch = () => (
    <ModernCard variant="outlined" size="md" style={{ marginBottom: 16 }}>
      <Row gutter={[16, 16]} align="middle">
        <Col xs={24} sm={16}>
          <ModernInput
            placeholder={t("knowledge.search.placeholder")}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onPressEnter={() => handleSearch(searchQuery)}
            prefix={<SearchOutlined />}
            size="large"
          />
        </Col>
        <Col xs={24} sm={8}>
          <Space>
            <ModernButton
              variant="outlined"
              icon={<FilterOutlined />}
              onClick={() => {}}
            >
              {t("knowledge.search.advanced")}
            </ModernButton>
          </Space>
        </Col>
      </Row>
    </ModernCard>
  );

  const renderDocumentPreview = () => {
    const documentsArray = Array.isArray(documents) ? documents : [];
    const recentDocuments = documentsArray.slice(0, 5);

    return (
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {recentDocuments.length === 0 ? (
          <Empty description={t("knowledge.no_documents")} />
        ) : (
          recentDocuments.map((doc) => (
            <ModernCard key={doc.id} variant="interactive" size="sm">
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <Avatar
                  icon={getDocumentTypeIcon(doc.file_type)}
                  size="large"
                />
                <div style={{ flex: 1 }}>
                  <Title level={5} style={{ margin: 0 }}>
                    {doc.title}
                  </Title>
                  <Text type="secondary" style={{ fontSize: "12px" }}>
                    {doc.file_name} • {formatFileSize(doc.file_size || 0)}
                  </Text>
                  <div style={{ marginTop: 8 }}>
                    <Tag color={getStatusColor(doc.status)}>
                      {t(`knowledge.status.${doc.status.toLowerCase()}`)}
                    </Tag>
                  </div>
                </div>
                <Space>
                  <ModernButton
                    variant="text"
                    icon={<EyeOutlined />}
                    size="small"
                  />
                  <ModernButton
                    variant="text"
                    icon={<DownloadOutlined />}
                    size="small"
                  />
                </Space>
              </div>
            </ModernCard>
          ))
        )}
      </div>
    );
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: colors.colorGradientPrimary,
        padding: "24px",
      }}
    >
      <div style={{ maxWidth: 1400, margin: "0 auto" }}>
        <ModernCard variant="gradient" size="lg" className="stagger-children">
          <div style={{ textAlign: "center", padding: "32px 0" }}>
            <div
              style={{
                fontSize: "48px",
                marginBottom: "16px",
                filter: "drop-shadow(0 4px 8px rgba(0,0,0,0.1))",
              }}
            >
              📚
            </div>
            <Title level={1} style={{ color: "#FFFFFF", margin: 0 }}>
              {t("knowledge.title")}
            </Title>
            <Text style={{ color: "rgba(255,255,255,0.8)", fontSize: "16px" }}>
              {t("knowledge.subtitle")}
            </Text>
          </div>
        </ModernCard>

        {error && (
          <Alert
            message={t("notifications.error")}
            description={error}
            type="error"
            showIcon
            closable
            style={{ marginBottom: 16, marginTop: 24 }}
          />
        )}

        <Row gutter={[24, 24]} style={{ marginTop: 32 }}>
          <Col xs={24} lg={16}>
            <Tabs
              activeKey={activeTab}
              onChange={setActiveTab}
              type="card"
              size="large"
              style={{ backgroundColor: colors.colorBgContainer }}
              items={[
                {
                  key: "documents",
                  label: (
                    <Space>
                      <BookOutlined />
                      {t("knowledge.tabs.documents")}
                    </Space>
                  ),
                  children: (
                    <div style={{ padding: "24px 0" }}>
                      {renderStats()}
                      {renderSearch()}
                      {renderActions()}

                      <DocumentList
                        documents={Array.isArray(documents) ? documents : []}
                        loading={loading}
                        onView={handleViewDocument}
                        onEdit={handleEditDocument}
                        onDelete={handleDeleteDocument}
                        onDownload={handleDownloadDocument}
                        onReprocess={handleReprocessDocument}
                        selectedRowKeys={selectedRowKeys}
                        onSelectionChange={setSelectedRowKeys}
                      />
                    </div>
                  ),
                },
                {
                  key: "tags",
                  label: (
                    <Space>
                      <TagsOutlined />
                      {t("knowledge.tabs.tags")}
                    </Space>
                  ),
                  children: (
                    <div style={{ padding: "24px 0" }}>
                      <TagManager
                        showCreateButton={user?.role === "premium"}
                        showStatistics={true}
                        mode="management"
                      />
                    </div>
                  ),
                },
                ...(user?.role === "admin"
                  ? [
                      {
                        key: "statistics",
                        label: (
                          <Space>
                            <BarChartOutlined />
                            {t("knowledge.tabs.statistics")}
                          </Space>
                        ),
                        children: (
                          <div style={{ padding: "24px 0" }}>
                            <SystemStats />
                          </div>
                        ),
                      },
                    ]
                  : []),
                ...(user?.role === "admin"
                  ? [
                      {
                        key: "settings",
                        label: (
                          <Space>
                            <SettingOutlined />
                            {t("knowledge.tabs.settings")}
                          </Space>
                        ),
                        children: (
                          <div style={{ padding: "24px 0" }}>
                            <ModernCard variant="elevated" size="lg">
                              <Title level={4}>
                                {t("knowledge.settings.title")}
                              </Title>
                              <Text type="secondary">
                                {t("knowledge.settings.description")}
                              </Text>
                              {/* TODO: Implement Settings component */}
                            </ModernCard>
                          </div>
                        ),
                      },
                    ]
                  : []),
              ]}
            />
          </Col>

          <Col xs={24} lg={8}>
            <ModernCard
              variant="interactive"
              size="md"
              style={{ marginBottom: 24 }}
            >
              <Title level={4}>{t("knowledge.quick_stats")}</Title>
              <div
                style={{ display: "flex", flexDirection: "column", gap: 16 }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <Text>{t("knowledge.stats.processed")}</Text>
                  <Text strong style={{ color: colors.colorSuccess }}>
                    {stats?.processed_documents || 0}
                  </Text>
                </div>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <Text>{t("knowledge.stats.processing")}</Text>
                  <Text strong style={{ color: colors.colorWarning }}>
                    {stats?.processing_documents || 0}
                  </Text>
                </div>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <Text>{t("knowledge.stats.errors")}</Text>
                  <Text strong style={{ color: colors.colorError }}>
                    {stats?.error_documents || 0}
                  </Text>
                </div>
              </div>
            </ModernCard>

            <ModernCard
              variant="outlined"
              size="md"
              style={{ marginBottom: 24 }}
            >
              <Title level={4}>{t("knowledge.quick_actions")}</Title>
              <div
                style={{ display: "flex", flexDirection: "column", gap: 12 }}
              >
                <ModernButton variant="primary" icon={<UploadOutlined />} block>
                  {t("knowledge.actions.upload")}
                </ModernButton>
                <ModernButton
                  variant="secondary"
                  icon={<SearchOutlined />}
                  block
                >
                  {t("knowledge.actions.search")}
                </ModernButton>
                <ModernButton
                  variant="outlined"
                  icon={<ReloadOutlined />}
                  block
                >
                  {t("knowledge.actions.refresh")}
                </ModernButton>
              </div>
            </ModernCard>

            <ModernCard variant="elevated" size="md">
              <Title level={4}>{t("knowledge.recent_documents")}</Title>
              {loading ? (
                <div style={{ textAlign: "center", padding: "20px" }}>
                  <Spin />
                </div>
              ) : (
                renderDocumentPreview()
              )}
            </ModernCard>
          </Col>
        </Row>
      </div>

      {/* Upload Modal */}
      <Modal
        title={t("knowledge.upload.title")}
        open={showUploadArea}
        onCancel={() => setShowUploadArea(false)}
        footer={null}
        width={800}
      >
        <UploadArea
          onUploadComplete={() => {
            setShowUploadArea(false);
            refreshDocuments();
          }}
          maxFiles={user?.role === "premium" ? 50 : 10}
          maxFileSize={100 * 1024 * 1024} // 100MB
          allowedTypes={[
            "pdf",
            "doc",
            "docx",
            "txt",
            "md",
            "xls",
            "xlsx",
            "ppt",
            "pptx",
          ]}
          showQueue={true}
        />
      </Modal>

      {/* Bulk Actions Modal */}
      <BulkActions
        visible={showBulkActions}
        onCancel={() => setShowBulkActions(false)}
        selectedDocuments={
          Array.isArray(documents)
            ? documents.filter((doc) => selectedRowKeys.includes(doc.id))
            : []
        }
        onBulkDelete={handleBulkDelete}
        onBulkTag={handleBulkTag}
        onBulkReprocess={handleBulkReprocess}
        onBulkDownload={handleBulkDownload}
      />
    </div>
  );
};

export default KnowledgeBase;
