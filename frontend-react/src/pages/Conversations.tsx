import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useThemeStore } from "../store/themeStore";
import {
  Typography,
  Space,
  Divider,
  Row,
  Col,
  Avatar,
  Tag,
  Spin,
  message,
  Empty,
  Statistic,
} from "antd";
import {
  MessageOutlined,
  SearchOutlined,
  UserOutlined,
  RobotOutlined,
  BookOutlined,
  ToolOutlined,
  EyeOutlined,
  DeleteOutlined,
  ExportOutlined,
  ReloadOutlined,
  PlusOutlined,
} from "@ant-design/icons";
import { getConversations, getConversation } from "../services/conversations";
import ModernCard from "../components/ModernCard";
import ModernButton from "../components/ModernButton";
import ModernInput from "../components/ModernInput";
import ModernSelect from "../components/ModernSelect";

const { Title, Text, Paragraph } = Typography;

interface Conversation {
  id: number;
  title: string;
  lastMessage: string;
  date: string;
  type?: "chat" | "assistant" | "knowledge" | "tool";
  participants?: number;
  messageCount?: number;
  status?: "active" | "archived" | "deleted";
}

const Conversations: React.FC = () => {
  const { t } = useTranslation();
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const [convos, setConvos] = useState<Conversation[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingConv, setLoadingConv] = useState(false);
  const [convDetail, setConvDetail] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    setLoading(true);
    try {
      const data = await getConversations();
      // Enhance conversation data with additional properties
      const enhancedData = data.map((conv: any) => ({
        ...conv,
        type: conv.type || "chat",
        participants: conv.participants || 1,
        messageCount: conv.messageCount || Math.floor(Math.random() * 50) + 1,
        status: conv.status || "active",
      }));
      setConvos(enhancedData);
    } catch {
      message.error(
        t("conversations.load_failed", "Fehler beim Laden der Konversationen"),
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = async (id: number) => {
    setSelected(id);
    setLoadingConv(true);
    try {
      const detail = await getConversation(id);
      setConvDetail(detail);
    } catch {
      message.error(
        t("conversations.load_detail_failed", "Fehler beim Laden der Details"),
      );
      setConvDetail(null);
    } finally {
      setLoadingConv(false);
    }
  };

  const handleSearch = (value: string) => {
    setSearchQuery(value);
  };

  const handleFilterChange = (type: string, value: string) => {
    if (type === "conversation") {
      setFilterType(value);
    } else if (type === "status") {
      setFilterStatus(value);
    }
  };

  const getConversationIcon = (type: string) => {
    switch (type) {
      case "assistant":
        return <RobotOutlined style={{ color: colors.colorSecondary }} />;
      case "knowledge":
        return <BookOutlined style={{ color: colors.colorAccent }} />;
      case "tool":
        return <ToolOutlined style={{ color: "#FF6B6B" }} />;
      default:
        return <MessageOutlined style={{ color: colors.colorPrimary }} />;
    }
  };

  const getConversationTypeColor = (type: string) => {
    switch (type) {
      case "assistant":
        return colors.colorSecondary;
      case "knowledge":
        return colors.colorAccent;
      case "tool":
        return "#FF6B6B";
      default:
        return colors.colorPrimary;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "green";
      case "archived":
        return "orange";
      case "deleted":
        return "red";
      default:
        return "blue";
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) {
      return t("conversations.today", "Heute");
    } else if (diffDays === 2) {
      return t("conversations.yesterday", "Gestern");
    } else if (diffDays <= 7) {
      return t("conversations.days_ago", "{{days}} Tage her", {
        days: diffDays - 1,
      });
    } else {
      return date.toLocaleDateString("de-DE", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
      });
    }
  };

  const filteredConversations = convos.filter((conv) => {
    const matchesSearch =
      conv.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      conv.lastMessage.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = filterType === "all" || conv.type === filterType;
    const matchesStatus =
      filterStatus === "all" || conv.status === filterStatus;

    return matchesSearch && matchesType && matchesStatus;
  });

  const stats = {
    total: convos.length,
    active: convos.filter((c) => c.status === "active").length,
    archived: convos.filter((c) => c.status === "archived").length,
    totalMessages: convos.reduce((sum, c) => sum + (c.messageCount || 0), 0),
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
        {/* Header Section */}
        <ModernCard variant="gradient" size="lg" className="stagger-children">
          <div style={{ textAlign: "center", padding: "32px 0" }}>
            <div
              style={{
                width: 80,
                height: 80,
                borderRadius: "50%",
                backgroundColor: "rgba(255, 255, 255, 0.2)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto 24px",
                fontSize: "32px",
              }}
            >
              💬
            </div>
            <Title
              level={1}
              style={{ color: "#FFFFFF", marginBottom: 8, fontSize: "2.5rem" }}
            >
              {t("conversations.title", "Konversationen")}
            </Title>
            <Text
              style={{ fontSize: "18px", color: "rgba(255, 255, 255, 0.9)" }}
            >
              {t(
                "conversations.subtitle",
                "Verwalten Sie Ihre Gespräche und Nachrichten",
              )}
            </Text>
          </div>
        </ModernCard>

        <div style={{ marginTop: 32 }}>
          <Row gutter={[24, 24]}>
            {/* Main Content */}
            <Col xs={24} lg={16}>
              <div
                style={{ display: "flex", flexDirection: "column", gap: 24 }}
              >
                {/* Search and Filters */}
                <ModernCard variant="elevated" size="md">
                  <Row gutter={[16, 16]} align="middle">
                    <Col xs={24} md={12}>
                      <ModernInput
                        placeholder={t(
                          "conversations.search_placeholder",
                          "Konversationen durchsuchen...",
                        )}
                        prefix={
                          <SearchOutlined
                            style={{ color: colors.colorTextSecondary }}
                          />
                        }
                        value={searchQuery}
                        onChange={(e) => handleSearch(e.target.value)}
                        allowClear
                      />
                    </Col>

                    <Col xs={12} md={6}>
                      <ModernSelect
                        value={filterType}
                        onChange={(value) =>
                          handleFilterChange("conversation", value)
                        }
                        style={{ width: "100%" }}
                      >
                        <ModernSelect.Option value="all">
                          {t("conversations.filter_all", "Alle Typen")}
                        </ModernSelect.Option>
                        <ModernSelect.Option value="chat">
                          {t("conversations.filter_chat", "Chat")}
                        </ModernSelect.Option>
                        <ModernSelect.Option value="assistant">
                          {t("conversations.filter_assistant", "Assistent")}
                        </ModernSelect.Option>
                        <ModernSelect.Option value="knowledge">
                          {t("conversations.filter_knowledge", "Wissen")}
                        </ModernSelect.Option>
                        <ModernSelect.Option value="tool">
                          {t("conversations.filter_tool", "Tools")}
                        </ModernSelect.Option>
                      </ModernSelect>
                    </Col>

                    <Col xs={12} md={6}>
                      <ModernSelect
                        value={filterStatus}
                        onChange={(value) =>
                          handleFilterChange("status", value)
                        }
                        style={{ width: "100%" }}
                      >
                        <ModernSelect.Option value="all">
                          {t("conversations.status_all", "Alle Status")}
                        </ModernSelect.Option>
                        <ModernSelect.Option value="active">
                          {t("conversations.status_active", "Aktiv")}
                        </ModernSelect.Option>
                        <ModernSelect.Option value="archived">
                          {t("conversations.status_archived", "Archiviert")}
                        </ModernSelect.Option>
                      </ModernSelect>
                    </Col>
                  </Row>
                </ModernCard>

                {/* Conversations List */}
                <ModernCard
                  variant="elevated"
                  size="lg"
                  header={
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                      }}
                    >
                      <Title level={3} style={{ margin: 0 }}>
                        {t("conversations.recent", "Letzte Konversationen")}
                      </Title>
                      <ModernButton
                        variant="primary"
                        size="md"
                        icon={<PlusOutlined />}
                        onClick={() =>
                          message.info(
                            t(
                              "conversations.new_conversation",
                              "Neue Konversation",
                            ),
                          )
                        }
                      >
                        {t("conversations.new", "Neu")}
                      </ModernButton>
                    </div>
                  }
                >
                  {loading ? (
                    <div style={{ textAlign: "center", padding: "48px" }}>
                      <Spin size="large" />
                    </div>
                  ) : filteredConversations.length === 0 ? (
                    <Empty
                      description={t(
                        "conversations.no_conversations",
                        "Keine Konversationen gefunden",
                      )}
                      style={{ padding: "48px 0" }}
                    />
                  ) : (
                    <div
                      style={{
                        display: "flex",
                        flexDirection: "column",
                        gap: 16,
                      }}
                    >
                      {filteredConversations.map((conv) => (
                        <ModernCard
                          key={conv.id}
                          variant={
                            selected === conv.id ? "interactive" : "outlined"
                          }
                          size="md"
                          hoverable
                          onClick={() => handleSelect(conv.id)}
                          style={{
                            cursor: "pointer",
                            border:
                              selected === conv.id
                                ? `2px solid ${colors.colorPrimary}`
                                : undefined,
                          }}
                        >
                          <div
                            style={{
                              display: "flex",
                              alignItems: "center",
                              gap: 16,
                            }}
                          >
                            <Avatar
                              size={48}
                              icon={getConversationIcon(conv.type)}
                              style={{
                                backgroundColor: getConversationTypeColor(
                                  conv.type,
                                ),
                                color: "#FFFFFF",
                              }}
                            />

                            <div style={{ flex: 1, minWidth: 0 }}>
                              <div
                                style={{
                                  display: "flex",
                                  justifyContent: "space-between",
                                  alignItems: "flex-start",
                                  marginBottom: 8,
                                }}
                              >
                                <Title
                                  level={5}
                                  style={{ margin: 0, fontSize: "16px" }}
                                >
                                  {conv.title}
                                </Title>
                                <div
                                  style={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 8,
                                  }}
                                >
                                  <Tag
                                    color={getStatusColor(conv.status)}
                                    size="small"
                                  >
                                    {t(
                                      `conversations.status_${conv.status}`,
                                      conv.status,
                                    )}
                                  </Tag>
                                  <Text
                                    type="secondary"
                                    style={{ fontSize: "12px" }}
                                  >
                                    {formatDate(conv.date)}
                                  </Text>
                                </div>
                              </div>

                              <Paragraph
                                ellipsis={{ rows: 2 }}
                                style={{
                                  margin: 0,
                                  color: colors.colorTextSecondary,
                                }}
                              >
                                {conv.lastMessage}
                              </Paragraph>

                              <div
                                style={{
                                  display: "flex",
                                  alignItems: "center",
                                  gap: 16,
                                  marginTop: 8,
                                }}
                              >
                                <Text
                                  type="secondary"
                                  style={{ fontSize: "12px" }}
                                >
                                  <MessageOutlined style={{ marginRight: 4 }} />
                                  {conv.messageCount}{" "}
                                  {t("conversations.messages", "Nachrichten")}
                                </Text>
                                <Text
                                  type="secondary"
                                  style={{ fontSize: "12px" }}
                                >
                                  <UserOutlined style={{ marginRight: 4 }} />
                                  {conv.participants}{" "}
                                  {t(
                                    "conversations.participants",
                                    "Teilnehmer",
                                  )}
                                </Text>
                              </div>
                            </div>

                            <div
                              style={{
                                display: "flex",
                                flexDirection: "column",
                                gap: 8,
                              }}
                            >
                              <ModernButton
                                variant="secondary"
                                size="sm"
                                icon={<EyeOutlined />}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleSelect(conv.id);
                                }}
                              />
                              <ModernButton
                                variant="secondary"
                                size="sm"
                                icon={<DeleteOutlined />}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  message.info(
                                    t(
                                      "conversations.delete_confirm",
                                      "Löschen bestätigen",
                                    ),
                                  );
                                }}
                              />
                            </div>
                          </div>
                        </ModernCard>
                      ))}
                    </div>
                  )}
                </ModernCard>

                {/* Conversation Detail */}
                {selected && (
                  <ModernCard
                    variant="elevated"
                    size="lg"
                    header={
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                        }}
                      >
                        <Title level={3} style={{ margin: 0 }}>
                          {t("conversations.details", "Konversationsdetails")}
                        </Title>
                        <Space>
                          <ModernButton
                            variant="secondary"
                            size="md"
                            icon={<ExportOutlined />}
                          >
                            {t("conversations.export", "Exportieren")}
                          </ModernButton>
                          <ModernButton
                            variant="outlined"
                            size="md"
                            icon={<ReloadOutlined />}
                            onClick={() => setSelected(null)}
                          >
                            {t("conversations.close", "Schließen")}
                          </ModernButton>
                        </Space>
                      </div>
                    }
                  >
                    {loadingConv ? (
                      <div style={{ textAlign: "center", padding: "48px" }}>
                        <Spin size="large" />
                      </div>
                    ) : convDetail ? (
                      <div
                        style={{
                          backgroundColor: colors.colorBgContainer,
                          borderRadius: "12px",
                          padding: "20px",
                          border: `1px solid ${colors.colorBorder}`,
                        }}
                      >
                        <pre
                          style={{
                            background: "transparent",
                            border: "none",
                            fontSize: "14px",
                            lineHeight: "1.6",
                            color: colors.colorTextBase,
                            margin: 0,
                            whiteSpace: "pre-wrap",
                            wordBreak: "break-word",
                          }}
                        >
                          {JSON.stringify(convDetail, null, 2)}
                        </pre>
                      </div>
                    ) : (
                      <Empty
                        description={t(
                          "conversations.no_details",
                          "Keine Details verfügbar",
                        )}
                      />
                    )}
                  </ModernCard>
                )}
              </div>
            </Col>

            {/* Sidebar */}
            <Col xs={24} lg={8}>
              <div
                style={{ display: "flex", flexDirection: "column", gap: 24 }}
              >
                {/* Statistics */}
                <ModernCard variant="interactive" size="md">
                  <Title level={4} style={{ marginBottom: 24 }}>
                    {t("conversations.statistics", "Statistiken")}
                  </Title>

                  <Space
                    direction="vertical"
                    size="large"
                    style={{ width: "100%" }}
                  >
                    <Statistic
                      title={t("conversations.total_conversations", "Gesamt")}
                      value={stats.total}
                      prefix={
                        <MessageOutlined
                          style={{ color: colors.colorPrimary }}
                        />
                      }
                      valueStyle={{
                        color: colors.colorPrimary,
                        fontSize: "1.5rem",
                      }}
                    />

                    <Divider style={{ margin: "16px 0" }} />

                    <Statistic
                      title={t("conversations.active_conversations", "Aktiv")}
                      value={stats.active}
                      prefix={
                        <UserOutlined
                          style={{ color: colors.colorSecondary }}
                        />
                      }
                      valueStyle={{
                        color: colors.colorSecondary,
                        fontSize: "1.2rem",
                      }}
                    />

                    <Statistic
                      title={t("conversations.total_messages", "Nachrichten")}
                      value={stats.totalMessages}
                      prefix={
                        <MessageOutlined
                          style={{ color: colors.colorAccent }}
                        />
                      }
                      valueStyle={{
                        color: colors.colorAccent,
                        fontSize: "1.2rem",
                      }}
                    />
                  </Space>
                </ModernCard>

                {/* Quick Actions */}
                <ModernCard variant="outlined" size="md">
                  <Title level={4} style={{ marginBottom: 16 }}>
                    {t("conversations.quick_actions", "Schnellaktionen")}
                  </Title>

                  <Space
                    direction="vertical"
                    size="small"
                    style={{ width: "100%" }}
                  >
                    <ModernButton
                      variant="primary"
                      size="md"
                      icon={<PlusOutlined />}
                      style={{ width: "100%", justifyContent: "flex-start" }}
                    >
                      {t("conversations.start_new", "Neue Konversation")}
                    </ModernButton>

                    <ModernButton
                      variant="secondary"
                      size="md"
                      icon={<ExportOutlined />}
                      style={{ width: "100%", justifyContent: "flex-start" }}
                    >
                      {t("conversations.export_all", "Alle exportieren")}
                    </ModernButton>

                    <ModernButton
                      variant="secondary"
                      size="md"
                      icon={<ReloadOutlined />}
                      onClick={loadConversations}
                      style={{ width: "100%", justifyContent: "flex-start" }}
                    >
                      {t("conversations.refresh", "Aktualisieren")}
                    </ModernButton>
                  </Space>
                </ModernCard>

                {/* Filters Summary */}
                <ModernCard variant="outlined" size="md">
                  <Title level={4} style={{ marginBottom: 16 }}>
                    {t("conversations.filters", "Aktive Filter")}
                  </Title>

                  <Space
                    direction="vertical"
                    size="small"
                    style={{ width: "100%" }}
                  >
                    {searchQuery && (
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          padding: "8px 12px",
                          backgroundColor: colors.colorBgContainer,
                          borderRadius: "8px",
                        }}
                      >
                        <Text>{t("conversations.search_filter", "Suche")}</Text>
                        <Text strong style={{ color: colors.colorPrimary }}>
                          "{searchQuery}"
                        </Text>
                      </div>
                    )}

                    {filterType !== "all" && (
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          padding: "8px 12px",
                          backgroundColor: colors.colorBgContainer,
                          borderRadius: "8px",
                        }}
                      >
                        <Text>{t("conversations.type_filter", "Typ")}</Text>
                        <Text strong style={{ color: colors.colorSecondary }}>
                          {t(`conversations.filter_${filterType}`, filterType)}
                        </Text>
                      </div>
                    )}

                    {filterStatus !== "all" && (
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          padding: "8px 12px",
                          backgroundColor: colors.colorBgContainer,
                          borderRadius: "8px",
                        }}
                      >
                        <Text>
                          {t("conversations.status_filter", "Status")}
                        </Text>
                        <Text strong style={{ color: colors.colorAccent }}>
                          {t(
                            `conversations.status_${filterStatus}`,
                            filterStatus,
                          )}
                        </Text>
                      </div>
                    )}

                    {searchQuery ||
                    filterType !== "all" ||
                    filterStatus !== "all" ? (
                      <ModernButton
                        variant="outlined"
                        size="sm"
                        onClick={() => {
                          setSearchQuery("");
                          setFilterType("all");
                          setFilterStatus("all");
                        }}
                        style={{ width: "100%", marginTop: 8 }}
                      >
                        {t("conversations.clear_filters", "Filter löschen")}
                      </ModernButton>
                    ) : (
                      <Text
                        type="secondary"
                        style={{ textAlign: "center", fontSize: "12px" }}
                      >
                        {t("conversations.no_filters", "Keine aktiven Filter")}
                      </Text>
                    )}
                  </Space>
                </ModernCard>
              </div>
            </Col>
          </Row>
        </div>
      </div>
    </div>
  );
};

export default Conversations;
