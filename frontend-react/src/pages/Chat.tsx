// @ts-nocheck
import React, { useState, useEffect, useRef } from "react";
import {
  Spin,
  Alert,
  message,
  Row,
  Col,
  Typography,
  Badge,
  Tooltip,
} from "antd";
import {
  SendOutlined,
  UserOutlined,
  RobotOutlined,
  BookOutlined,
  SearchOutlined,
  LoadingOutlined,
  DownloadOutlined,
  MoreOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useLocation } from "react-router-dom";
import { chatWebSocket } from "../services/chat";
import type { ChatMessage, KnowledgeContext } from "../services/chat";
import { useAuthStore } from "../store/authStore";
import { useThemeStore } from "../store/themeStore";
import { useKnowledgeStore } from "../store/knowledgeStore";
import KnowledgeContextComponent from "../components/chat/KnowledgeContext";
import type { Document } from "../services/knowledge";
import type { InputRef } from "antd";
import { config } from "../config";
import ModernCard from "../components/ModernCard";
import ModernButton from "../components/ModernButton";
import ModernInput from "../components/ModernInput";
import ChatExport from "../components/chat/ChatExport";
import { exportService } from "../services/export";

const { Title, Text } = Typography;

const Chat: React.FC = () => {
  const { t } = useTranslation();
  const location = useLocation();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const [showKnowledgeDrawer, setShowKnowledgeDrawer] = useState(false);
  const [knowledgeContextEnabled, setKnowledgeContextEnabled] = useState(false);
  const [selectedDocuments, setSelectedDocuments] = useState<Document[]>([]);
  const [searchResults, setSearchResults] = useState<Document[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [typingTimeout, setTypingTimeout] = useState<NodeJS.Timeout | null>(
    null,
  );
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [streamingMessage, setStreamingMessage] = useState<string>("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [conversationTitle, setConversationTitle] = useState<string>("");

  const token = useAuthStore((s) => s.token);
  const { getCurrentColors } = useThemeStore();
  const { searchDocuments } = useKnowledgeStore() as any;
  const colors = (getCurrentColors() as any) ?? {};
  const listRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<InputRef>(null);

  // Get conversation ID from URL params or create/get conversation
  useEffect(() => {
    if (!token) return;

    const createOrGetConversation = async () => {
      try {
        // Check if conversation ID is provided in URL params
        const urlParams = new URLSearchParams(location.search);
        const conversationParam = urlParams.get('conversation');
        
        if (conversationParam) {
          setConversationId(conversationParam);
          return;
        }

        // Try to get existing conversations first
        const response = await fetch(`${config.apiUrl}${config.apiEndpoints.chat}/conversations`, {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });

        if (response.ok) {
          const conversations = await response.json();
          if (conversations.length > 0) {
            // Use the most recent conversation
            setConversationId(conversations[0].id);
            return;
          }
        }

        // Get default assistant ID first
        const assistantIdResponse = await fetch(
          `${config.apiUrl}${config.apiEndpoints.assistants}/default/id`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          },
        );

        if (!assistantIdResponse.ok) {
          throw new Error("Failed to get default assistant ID");
        }

        const { assistant_id } = await assistantIdResponse.json();

        // Get the full assistant details
        const assistantResponse = await fetch(
          `${config.apiUrl}${config.apiEndpoints.assistants}/${assistant_id}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          },
        );

        if (!assistantResponse.ok) {
          throw new Error("Failed to get default assistant");
        }

        const defaultAssistant = await assistantResponse.json();

        // Create new conversation if none exists
        const createResponse = await fetch(
          `${config.apiUrl}${config.apiEndpoints.chat}/conversations`,
          {
            method: "POST",
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              title: "New Chat",
              assistant_id: defaultAssistant.id,
            }),
          },
        );

        if (createResponse.ok) {
          const conversation = await createResponse.json();
          setConversationId(conversation.id);
        }
      } catch (error) {
        console.error("Error creating/getting conversation:", error);
        setError(t("chat.error"));
      }
    };

    createOrGetConversation();
  }, [token]);

  useEffect(() => {
    if (!token || !conversationId) return;
    setLoading(true);
    setError(null);
    try {
      chatWebSocket.connect(
        token,
        conversationId,
        handleMessage,
        handleKnowledgeUpdate,
        handleProcessingJobUpdate,
        handleStreamChunk,
        handleStreamComplete,
      );
    } catch {
      setError(t("chat.error"));
      setLoading(false);
    }
    return () => chatWebSocket.disconnect();
  }, [token, conversationId]);

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages]);

  const handleMessage = (msg: ChatMessage) => {
    setMessages((prev) => [
      ...prev,
      { ...msg, timestamp: msg.timestamp || new Date() },
    ]);
    setLoading(false);
    setIsTyping(false);
  };

  const handleKnowledgeUpdate = (
    documents: Document[],
    searchQuery: string,
  ) => {
    setSearchResults(documents);
    // Add a system message about knowledge search
    const searchMessage: ChatMessage = {
      sender: "System",
      text: `Found ${documents.length} relevant documents for "${searchQuery}"`,
      messageType: "system",
      timestamp: new Date(),
      documents,
    };
    setMessages((prev) => [...prev, searchMessage]);
  };

  const handleProcessingJobUpdate = (
    jobId: string,
    status: string,
    progress: number,
  ) => {
    // Update processing job status in knowledge store
    // This could be used to show upload progress or processing status
    console.log(`Job ${jobId}: ${status} (${progress}%)`);
  };

  const handleStreamChunk = (content: string, conversationId: string) => {
    // Handle streaming content chunks
    setStreamingMessage((prev) => prev + content);
    setIsStreaming(true);
  };

  const handleStreamComplete = (msg: ChatMessage) => {
    // Handle completed streaming message
    setMessages((prev) => [
      ...prev,
      { ...msg, timestamp: msg.timestamp || new Date() },
    ]);
    setStreamingMessage("");
    setIsStreaming(false);
    setIsTyping(false);
    setLoading(false);
  };

  const handleSend = () => {
    if (input.trim()) {
      setSending(true);
      try {
        // Create knowledge context if enabled
        const knowledgeContext: KnowledgeContext | undefined =
          knowledgeContextEnabled
            ? {
                enabled: true,
                documentIds: selectedDocuments.map((doc) => doc.id),
                searchQuery: input,
                maxChunks: 5,
                filters: {
                  tags: selectedDocuments.flatMap(
                    (doc) => doc.tags?.map((tag) => tag.name) || [],
                  ),
                  documentTypes: [
                    ...new Set(
                      selectedDocuments
                        .map((doc) => doc.document_type)
                        .filter(Boolean) as string[],
                    ),
                  ],
                },
              }
            : undefined;

        // Send message via WebSocket
        chatWebSocket.sendMessage(input, knowledgeContext);

        // Add user message to local state
        setMessages((prev) => [
          ...prev,
          {
            sender: "You",
            text: input,
            timestamp: new Date(),
          },
        ]);

        setInput("");
        setSelectedDocuments([]); // Clear selected documents after sending
        message.success("Message sent");
        setTimeout(() => inputRef.current?.focus(), 100);
      } catch {
        message.error("Failed to send message");
      } finally {
        setSending(false);
      }
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setInput(value);

    // Send typing indicator
    if (typingTimeout) {
      clearTimeout(typingTimeout);
    }

    setIsTyping(true);
    chatWebSocket.sendTypingIndicator(true);

    const timeout = setTimeout(() => {
      setIsTyping(false);
      chatWebSocket.sendTypingIndicator(false);
    }, 1000);

    setTypingTimeout(timeout);
  };

  const handleKnowledgeSearch = async (query: string) => {
    try {
      const results = await searchDocuments(query);
      setSearchResults(results.documents || []);

      // Send knowledge search via WebSocket for real-time updates
      chatWebSocket.sendKnowledgeSearch(query);

      return results.documents || [];
    } catch (error) {
      console.error("Knowledge search failed:", error);
      message.error("Search failed");
      return [];
    }
  };

  const handleDocumentSelect = (document: Document) => {
    setSelectedDocuments((prev) => {
      const exists = prev.find((doc) => doc.id === document.id);
      if (exists) {
        return prev.filter((doc) => doc.id !== document.id);
      } else {
        return [...prev, document];
      }
    });
  };

  const handleToggleKnowledgeContext = (enabled: boolean) => {
    setKnowledgeContextEnabled(enabled);
    if (!enabled) {
      setSelectedDocuments([]);
      setSearchResults([]);
    }
  };

  const handleExport = async (options: any) => {
    try {
      await exportService.exportChat(messages, options, conversationTitle);
      message.success(t("chat.export.success"));
    } catch (error) {
      console.error("Export error:", error);
      message.error(t("chat.export.error"));
    }
  };

  const formatTime = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const renderMessage = (msg: ChatMessage, index: number) => {
    const isUser = msg.sender === "You";
    const isSystem = msg.messageType === "system";
    const isError = msg.messageType === "error";

    const messageStyle: React.CSSProperties = {
      display: "flex",
      flexDirection: isUser ? "row-reverse" : "row",
      alignItems: "flex-start",
      gap: "16px",
      marginBottom: "20px",
      maxWidth: "85%",
      marginLeft: isUser ? "auto" : "0",
      marginRight: isUser ? "0" : "auto",
      animation: "fadeInUp 0.3s ease-out",
    };

    const bubbleStyle: React.CSSProperties = {
      background: isError
        ? "#ff4d4f"
        : isSystem
          ? "#f0f0f0"
          : isUser
            ? colors.colorChatUserBubble
            : colors.colorChatAIBubble,
      color: isError
        ? "#fff"
        : isSystem
          ? "#666"
          : isUser
            ? colors.colorChatUserText
            : colors.colorChatAIText,
      padding: "16px 20px",
      borderRadius: "20px",
      boxShadow: colors.boxShadow,
      position: "relative",
      wordWrap: "break-word",
      maxWidth: "100%",
      border: isSystem ? "1px dashed #d9d9d9" : "none",
      transition: "all 0.3s ease",
    };

    const avatarStyle: React.CSSProperties = {
      backgroundColor: isError
        ? "#ff4d4f"
        : isSystem
          ? "#d9d9d9"
          : isUser
            ? colors.colorPrimary
            : colors.colorSecondary,
      flexShrink: 0,
      width: "40px",
      height: "40px",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      borderRadius: "50%",
      boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
    };

    return (
      <div key={index} style={messageStyle} className="message-item">
        <div style={avatarStyle}>
          {isUser ? (
            <UserOutlined style={{ color: "#fff" }} />
          ) : isSystem ? (
            <SearchOutlined style={{ color: "#666" }} />
          ) : (
            <RobotOutlined style={{ color: "#fff" }} />
          )}
        </div>
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "8px",
            flex: 1,
          }}
        >
          <div style={bubbleStyle} className="message-bubble">
            {msg.text}
            {isStreaming && index === messages.length - 1 && (
              <span
                style={{
                  display: "inline-block",
                  width: "8px",
                  height: "16px",
                  backgroundColor: colors.colorPrimary,
                  animation: "blink 1s infinite",
                  marginLeft: "4px",
                }}
              />
            )}
            {msg.metadata && (
              <div
                style={{
                  fontSize: "11px",
                  marginTop: "12px",
                  opacity: 0.7,
                  borderTop: "1px solid rgba(0,0,0,0.1)",
                  paddingTop: "8px",
                }}
              >
                {msg.metadata.contextChunks &&
                  `Context: ${msg.metadata.contextChunks} chunks`}
                {msg.metadata.confidence &&
                  ` | Confidence: ${(msg.metadata.confidence * 100).toFixed(1)}%`}
                {msg.metadata.processingTime &&
                  ` | Time: ${msg.metadata.processingTime}ms`}
              </div>
            )}
          </div>

          {msg.documents && msg.documents.length > 0 && (
            <ModernCard
              variant="outlined"
              size="sm"
              style={{
                maxWidth: "400px",
                marginTop: "8px",
              }}
            >
              <div
                style={{
                  fontSize: "12px",
                  color: colors.colorSecondary,
                }}
              >
                <Text
                  type="secondary"
                  style={{ fontSize: "12px", fontWeight: "bold" }}
                >
                  {t("common.sources")} ({msg.documents.length}):
                </Text>
                <div style={{ marginTop: "8px" }}>
                  {msg.documents.slice(0, 3).map((doc, idx) => (
                    <div
                      key={idx}
                      style={{
                        fontSize: "11px",
                        marginBottom: "4px",
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        padding: "4px 8px",
                        background: "rgba(0,0,0,0.05)",
                        borderRadius: "6px",
                      }}
                    >
                      • {doc.title}
                    </div>
                  ))}
                  {msg.documents.length > 3 && (
                    <div
                      style={{
                        fontSize: "11px",
                        color: colors.colorSecondary,
                        textAlign: "center",
                        marginTop: "4px",
                      }}
                    >
                      +{msg.documents.length - 3} more
                    </div>
                  )}
                </div>
              </div>
            </ModernCard>
          )}

          <div
            style={{
              fontSize: "11px",
              color: colors.colorSecondary,
              marginLeft: isUser ? "auto" : "0",
              marginRight: isUser ? "0" : "auto",
              opacity: 0.8,
            }}
          >
            {msg.timestamp && formatTime(msg.timestamp)}
          </div>
        </div>
      </div>
    );
  };

  return (
    <Row style={{ height: "100vh" }}>
      <Col span={showKnowledgeDrawer ? 18 : 24} style={{ height: "100%" }}>
        <ModernCard
          variant="default"
          size="xl"
          header={
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
              }}
            >
              <div
                style={{ display: "flex", alignItems: "center", gap: "12px" }}
              >
                <Title
                  level={4}
                  style={{ margin: 0, color: colors.colorTextBase }}
                >
                  {t("chat.title")}
                </Title>
                {!chatWebSocket.isConnected() && (
                  <Badge status="error" text={t("errors.network")} />
                )}
                {isTyping && (
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                    }}
                  >
                    <LoadingOutlined
                      style={{ fontSize: "14px", color: colors.colorPrimary }}
                    />
                    <span
                      style={{ fontSize: "14px", color: colors.colorSecondary }}
                    >
                      {t("chat.typing")}
                    </span>
                  </div>
                )}
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                {messages.length > 0 && (
                  <Tooltip title={t("chat.export.title")}>
                    <ModernButton
                      variant="outlined"
                      size="md"
                      icon={<DownloadOutlined />}
                      onClick={() => setShowExportModal(true)}
                    >
                      {t("chat.export.export")}
                    </ModernButton>
                  </Tooltip>
                )}
                <Tooltip
                  title={
                    knowledgeContextEnabled
                      ? t("knowledge.processing")
                      : t("knowledge.title")
                  }
                >
                  <ModernButton
                    variant={knowledgeContextEnabled ? "primary" : "secondary"}
                    size="md"
                    icon={<BookOutlined />}
                    onClick={() => setShowKnowledgeDrawer(!showKnowledgeDrawer)}
                  >
                    {t("knowledge.title")}
                    {selectedDocuments.length > 0 && (
                      <Badge
                        count={selectedDocuments.length}
                        style={{ marginLeft: "8px" }}
                      />
                    )}
                  </ModernButton>
                </Tooltip>
              </div>
            </div>
          }
          style={{ height: "100%", display: "flex", flexDirection: "column" }}
        >
          {error && (
            <Alert
              message={t("errors.network")}
              description={error}
              type="error"
              showIcon
              closable
              style={{ marginBottom: 16, borderRadius: "12px" }}
            />
          )}

          <div
            ref={listRef}
            style={{
              flex: 1,
              overflowY: "auto",
              padding: "24px",
              marginBottom: "20px",
              border: "1px solid var(--colorBorder)",
              borderRadius: "16px",
              background: colors.colorBackground,
              minHeight: "400px",
            }}
            className="chat-messages-container"
          >
            {loading ? (
              <div style={{ textAlign: "center", padding: "60px" }}>
                <Spin size="large" />
                <div
                  style={{
                    marginTop: 20,
                    fontSize: "16px",
                    color: colors.colorSecondary,
                  }}
                >
                  {t("chat.loading")}
                </div>
              </div>
            ) : messages.length === 0 ? (
              <div
                style={{
                  textAlign: "center",
                  padding: "60px",
                  color: colors.colorSecondary,
                }}
              >
                <RobotOutlined
                  style={{
                    fontSize: "64px",
                    marginBottom: 24,
                    color: colors.colorPrimary,
                  }}
                />
                <Title
                  level={3}
                  style={{ color: colors.colorTextBase, marginBottom: 16 }}
                >
                  {t("chat.title")}
                </Title>
                <Text type="secondary" style={{ fontSize: "16px" }}>
                  {t("chat.empty")}
                </Text>
                {knowledgeContextEnabled && (
                  <div style={{ marginTop: "20px" }}>
                    <Text type="secondary" style={{ fontSize: "14px" }}>
                      {t("knowledge.processing")}
                    </Text>
                  </div>
                )}
              </div>
            ) : (
              <div className="stagger-children">
                {messages.map(renderMessage)}
                {isStreaming && streamingMessage && (
                  <div
                    style={{
                      display: "flex",
                      flexDirection: "row",
                      alignItems: "flex-start",
                      gap: "16px",
                      marginBottom: "20px",
                      maxWidth: "85%",
                      marginLeft: "0",
                      marginRight: "auto",
                      animation: "fadeInUp 0.3s ease-out",
                    }}
                  >
                    <div
                      style={{
                        backgroundColor: colors.colorChatAIBubble,
                        color: colors.colorChatAIText,
                        padding: "16px 20px",
                        borderRadius: "20px",
                        boxShadow: colors.boxShadow,
                        position: "relative",
                        wordWrap: "break-word",
                        maxWidth: "100%",
                        transition: "all 0.3s ease",
                      }}
                    >
                      <div
                        style={{
                          backgroundColor: colors.colorPrimary,
                          flexShrink: 0,
                          width: "40px",
                          height: "40px",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          borderRadius: "50%",
                          boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                        }}
                      >
                        <RobotOutlined style={{ color: "#fff" }} />
                      </div>
                      <div
                        style={{
                          display: "flex",
                          flexDirection: "column",
                          gap: "8px",
                          flex: 1,
                        }}
                      >
                        <div className="message-bubble">
                          {streamingMessage}
                          <span
                            style={{
                              display: "inline-block",
                              width: "8px",
                              height: "16px",
                              backgroundColor: colors.colorPrimary,
                              animation: "blink 1s infinite",
                              marginLeft: "4px",
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          <div style={{ display: "flex", gap: "12px", alignItems: "flex-end" }}>
            <div style={{ flex: 1 }}>
              <ModernInput
                variant="filled"
                size="lg"
                value={input}
                onChange={handleInputChange}
                onPressEnter={handleSend}
                placeholder={
                  knowledgeContextEnabled
                    ? t("chat.placeholder") + " (" + t("knowledge.title") + ")"
                    : t("chat.placeholder")
                }
                disabled={sending}
                clearable
                onClear={() => setInput("")}
              />
            </div>
            <ModernButton
              variant="primary"
              size="lg"
              icon={<SendOutlined />}
              onClick={handleSend}
              loading={sending}
              disabled={!input.trim()}
              style={{ minWidth: "120px" }}
            >
              {t("chat.send")}
            </ModernButton>
          </div>
        </ModernCard>
      </Col>

      {showKnowledgeDrawer && (
        <Col span={6} style={{ height: "100%" }}>
          <ModernCard
            variant="outlined"
            size="lg"
            header={
              <Title level={5} style={{ margin: 0 }}>
                {t("knowledge.title")}
              </Title>
            }
            style={{ height: "100%", overflowY: "auto" }}
          >
            <KnowledgeContextComponent
              onDocumentSelect={handleDocumentSelect}
              onSearch={handleKnowledgeSearch}
              selectedDocuments={selectedDocuments}
              searchResults={searchResults}
              onToggleContext={handleToggleKnowledgeContext}
              contextEnabled={knowledgeContextEnabled}
            />
          </ModernCard>
        </Col>
      )}

      <ChatExport
        visible={showExportModal}
        onClose={() => setShowExportModal(false)}
        messages={messages}
        conversationTitle={conversationTitle}
        onExport={handleExport}
      />
    </Row>
  );
};

export default Chat;
