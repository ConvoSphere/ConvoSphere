import React, { useEffect, useState } from "react";
import {
  Typography,
  Space,
  Row,
  Col,
  Card,
  Button,
  DatePicker,
  Select,
  Input,
  Tabs,
  message,
  Spin,
  Alert,
  Tooltip,
} from "antd";
import {
  BarChartOutlined,
  DownloadOutlined,
  ReloadOutlined,
  FilterOutlined,
  EyeOutlined,
  SettingOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { RangePickerProps } from "antd/es/date-picker";
import dayjs from "dayjs";
import { useConversationIntelligenceStore } from "../store/conversationIntelligenceStore";
import { useAuthStore } from "../store/authStore";
import ConversationAnalytics from "../components/intelligence/ConversationAnalytics";
import SentimentAnalysis from "../components/intelligence/SentimentAnalysis";
import TopicClustering from "../components/intelligence/TopicClustering";
import UserBehaviorAnalysis from "../components/intelligence/UserBehaviorAnalysis";
import ModernCard from "../components/ModernCard";
import ModernButton from "../components/ModernButton";
import ModernInput from "../components/ModernInput";
import ModernSelect from "../components/ModernSelect";
import type { AnalyticsFilters } from "../services/conversationIntelligence";

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;
const { TabPane } = Tabs;

const ConversationIntelligence: React.FC = () => {
  const { t } = useTranslation();
  const user = useAuthStore((s) => s.user);

  const {
    analytics,
    sentimentAnalysis,
    topicClusters,
    userBehavior,
    loading,
    error,
    filters,
    fetchAnalytics,
    fetchSentimentAnalysis,
    fetchTopicClustering,
    fetchUserBehaviorAnalysis,
    exportAnalytics,
    setFilters,
    clearError,
  } = useConversationIntelligenceStore();

  // Local state
  const [selectedConversationId, setSelectedConversationId] =
    useState<string>("");
  const [activeTab, setActiveTab] = useState("overview");
  const [localFilters, setLocalFilters] = useState<AnalyticsFilters>({});

  // Date range picker props
  const rangePickerProps: RangePickerProps = {
    ranges: {
      [t("intelligence.today")]: [dayjs(), dayjs()],
      [t("intelligence.last_7_days")]: [dayjs().subtract(7, "day"), dayjs()],
      [t("intelligence.last_30_days")]: [dayjs().subtract(30, "day"), dayjs()],
      [t("intelligence.last_90_days")]: [dayjs().subtract(90, "day"), dayjs()],
    },
    showTime: false,
    format: "YYYY-MM-DD",
  };

  // Load initial data
  useEffect(() => {
    loadData();
  }, []);

  // Load data with current filters
  const loadData = async () => {
    try {
      await Promise.all([
        fetchAnalytics(localFilters),
        fetchTopicClustering(localFilters),
        fetchUserBehaviorAnalysis(localFilters),
      ]);
    } catch (error) {
      console.error("Failed to load conversation intelligence data:", error);
    }
  };

  // Handle filter changes
  const handleFilterChange = (key: keyof AnalyticsFilters, value: any) => {
    const newFilters = { ...localFilters, [key]: value };
    setLocalFilters(newFilters);
  };

  // Apply filters
  const handleApplyFilters = async () => {
    setFilters(localFilters);
    await loadData();
    message.success(t("intelligence.filters_applied"));
  };

  // Clear filters
  const handleClearFilters = () => {
    const clearedFilters: AnalyticsFilters = {};
    setLocalFilters(clearedFilters);
    setFilters(clearedFilters);
    loadData();
    message.info(t("intelligence.filters_cleared"));
  };

  // Export data
  const handleExport = async (format: "csv" | "json" = "csv") => {
    try {
      await exportAnalytics(localFilters, format);
      message.success(t("intelligence.export_success"));
    } catch (error) {
      message.error(t("intelligence.export_error"));
    }
  };

  // Load sentiment analysis for specific conversation
  const handleLoadSentimentAnalysis = async (conversationId: string) => {
    if (!conversationId.trim()) {
      message.warning(t("intelligence.enter_conversation_id"));
      return;
    }

    try {
      await fetchSentimentAnalysis(conversationId);
      setActiveTab("sentiment");
      message.success(t("intelligence.sentiment_loaded"));
    } catch (error) {
      message.error(t("intelligence.sentiment_load_error"));
    }
  };

  // Refresh data
  const handleRefresh = () => {
    loadData();
    message.info(t("intelligence.data_refreshed"));
  };

  return (
    <div style={{ padding: "24px" }}>
      {/* Header */}
      <Row
        justify="space-between"
        align="middle"
        style={{ marginBottom: "24px" }}
      >
        <Col>
          <Title level={2} style={{ margin: 0 }}>
            <BarChartOutlined style={{ marginRight: "8px" }} />
            {t("intelligence.conversation_intelligence")}
          </Title>
          <Text type="secondary">
            {t("intelligence.analytics_description")}
          </Text>
        </Col>
        <Col>
          <Space>
            <Tooltip title={t("intelligence.refresh_data")}>
              <ModernButton
                icon={<ReloadOutlined />}
                onClick={handleRefresh}
                loading={loading}
              >
                {t("intelligence.refresh")}
              </ModernButton>
            </Tooltip>
            <Tooltip title={t("intelligence.export_data")}>
              <ModernButton
                icon={<DownloadOutlined />}
                onClick={() => handleExport("csv")}
              >
                {t("intelligence.export")}
              </ModernButton>
            </Tooltip>
          </Space>
        </Col>
      </Row>

      {/* Error Alert */}
      {error && (
        <Alert
          message={t("intelligence.error")}
          description={error}
          type="error"
          showIcon
          closable
          onClose={clearError}
          style={{ marginBottom: "16px" }}
        />
      )}

      {/* Filters */}
      <ModernCard
        title={t("intelligence.filters")}
        style={{ marginBottom: "24px" }}
      >
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={12} md={6}>
            <Text strong>{t("intelligence.date_range")}:</Text>
            <RangePicker
              {...rangePickerProps}
              value={
                localFilters.dateRange
                  ? [
                      dayjs(localFilters.dateRange.start),
                      dayjs(localFilters.dateRange.end),
                    ]
                  : undefined
              }
              onChange={(dates) => {
                if (dates) {
                  handleFilterChange("dateRange", {
                    start: dates[0]?.format("YYYY-MM-DD"),
                    end: dates[1]?.format("YYYY-MM-DD"),
                  });
                } else {
                  handleFilterChange("dateRange", undefined);
                }
              }}
              style={{ width: "100%", marginTop: "4px" }}
            />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Text strong>{t("intelligence.tags")}:</Text>
            <ModernInput
              placeholder={t("intelligence.enter_tags")}
              value={localFilters.tags?.join(", ") || ""}
              onChange={(e) => {
                const tags = e.target.value
                  .split(",")
                  .map((tag) => tag.trim())
                  .filter(Boolean);
                handleFilterChange("tags", tags.length > 0 ? tags : undefined);
              }}
              style={{ marginTop: "4px" }}
            />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Text strong>{t("intelligence.assistants")}:</Text>
            <ModernSelect
              mode="multiple"
              placeholder={t("intelligence.select_assistants")}
              value={localFilters.assistantIds}
              onChange={(value) => handleFilterChange("assistantIds", value)}
              style={{ width: "100%", marginTop: "4px" }}
            >
              <Option value="assistant1">Assistant 1</Option>
              <Option value="assistant2">Assistant 2</Option>
              <Option value="assistant3">Assistant 3</Option>
            </ModernSelect>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Space style={{ marginTop: "24px" }}>
              <ModernButton
                type="primary"
                icon={<FilterOutlined />}
                onClick={handleApplyFilters}
                loading={loading}
              >
                {t("intelligence.apply")}
              </ModernButton>
              <ModernButton onClick={handleClearFilters}>
                {t("intelligence.clear")}
              </ModernButton>
            </Space>
          </Col>
        </Row>
      </ModernCard>

      {/* Sentiment Analysis Input */}
      <ModernCard
        title={t("intelligence.sentiment_analysis")}
        style={{ marginBottom: "24px" }}
      >
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={16}>
            <ModernInput
              placeholder={t("intelligence.enter_conversation_id")}
              value={selectedConversationId}
              onChange={(e) => setSelectedConversationId(e.target.value)}
              onPressEnter={() =>
                handleLoadSentimentAnalysis(selectedConversationId)
              }
            />
          </Col>
          <Col xs={24} sm={8}>
            <ModernButton
              type="primary"
              icon={<EyeOutlined />}
              onClick={() =>
                handleLoadSentimentAnalysis(selectedConversationId)
              }
              loading={loading}
            >
              {t("intelligence.analyze_sentiment")}
            </ModernButton>
          </Col>
        </Row>
      </ModernCard>

      {/* Main Content Tabs */}
      <Tabs activeKey={activeTab} onChange={setActiveTab} type="card">
        <TabPane
          tab={
            <span>
              <BarChartOutlined />
              {t("intelligence.overview")}
            </span>
          }
          key="overview"
        >
          <Spin spinning={loading}>
            <ConversationAnalytics data={analytics} loading={loading} />
          </Spin>
        </TabPane>

        <TabPane
          tab={
            <span>
              <BarChartOutlined />
              {t("intelligence.sentiment_analysis")}
            </span>
          }
          key="sentiment"
        >
          <Spin spinning={loading}>
            <SentimentAnalysis data={sentimentAnalysis} loading={loading} />
          </Spin>
        </TabPane>

        <TabPane
          tab={
            <span>
              <BarChartOutlined />
              {t("intelligence.topic_clustering")}
            </span>
          }
          key="topics"
        >
          <Spin spinning={loading}>
            <TopicClustering data={topicClusters} loading={loading} />
          </Spin>
        </TabPane>

        <TabPane
          tab={
            <span>
              <BarChartOutlined />
              {t("intelligence.user_behavior")}
            </span>
          }
          key="behavior"
        >
          <Spin spinning={loading}>
            <UserBehaviorAnalysis data={userBehavior} loading={loading} />
          </Spin>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default ConversationIntelligence;
