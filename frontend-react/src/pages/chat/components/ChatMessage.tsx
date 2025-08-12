import React from "react";
import {
  Avatar,
  Card,
  Space,
  Typography,
  Tag,
  Tooltip,
  Button,
  Popconfirm,
  Spin,
} from "antd";
import {
  UserOutlined,
  RobotOutlined,
  CopyOutlined,
  DeleteOutlined,
  ReloadOutlined,
  ExclamationCircleOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { ChatMessage as ChatMessageType } from "../types/chat.types";
// import ReactMarkdown from 'react-markdown';
// import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
// import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';

const { Text, Paragraph } = Typography;

interface ChatMessageProps {
  message: ChatMessageType;
  onCopy?: (content: string) => void;
  onDelete?: (id: string) => void;
  onRetry?: (id: string) => void;
  showMetadata?: boolean;
}

const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  onCopy,
  onDelete,
  onRetry,
  showMetadata = false,
}) => {
  const { t } = useTranslation();

  const isUser = message.role === "user";
  const isAssistant = message.role === "assistant";
  const isSystem = message.role === "system";

  const getAvatar = () => {
    if (isUser) {
      return (
        <Avatar
          icon={<UserOutlined />}
          style={{ backgroundColor: "#1890ff" }}
        />
      );
    } else if (isAssistant) {
      return (
        <Avatar
          icon={<RobotOutlined />}
          style={{ backgroundColor: "#52c41a" }}
        />
      );
    } else {
      return (
        <Avatar
          icon={<UserOutlined />}
          style={{ backgroundColor: "#722ed1" }}
        />
      );
    }
  };

  const getMessageStyle = () => {
    if (isUser) {
      return {
        backgroundColor: "#f0f8ff",
        borderLeft: "4px solid #1890ff",
      };
    } else if (isAssistant) {
      return {
        backgroundColor: "#f6ffed",
        borderLeft: "4px solid #52c41a",
      };
    } else {
      return {
        backgroundColor: "#f9f0ff",
        borderLeft: "4px solid #722ed1",
      };
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const formatCost = (cost?: number) => {
    if (!cost) return "N/A";
    return `$${cost.toFixed(4)}`;
  };

  const formatTokens = (tokens?: number) => {
    if (!tokens) return "N/A";
    return tokens.toLocaleString();
  };

  const handleCopy = () => {
    if (onCopy) {
      onCopy(message.content);
    } else {
      navigator.clipboard.writeText(message.content);
    }
  };

  const handleDelete = () => {
    if (onDelete) {
      onDelete(message.id);
    }
  };

  const handleRetry = () => {
    if (onRetry) {
      onRetry(message.id);
    }
  };

  const renderContent = () => {
    if (message.status === "sending") {
      return (
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Spin size="small" />
          <Text type="secondary">{t("chat.sending_message")}</Text>
        </div>
      );
    }

    if (message.status === "error") {
      return (
        <div style={{ color: "#ff4d4f" }}>
          <ExclamationCircleOutlined style={{ marginRight: 8 }} />
          {message.error || t("chat.message_error")}
        </div>
      );
    }

    return (
      <div className="chat-message-content">
        <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
          {message.content}
        </pre>
      </div>
    );
  };

  const renderMetadata = () => {
    if (!showMetadata || !message.metadata) return null;

    const { model, tokens, cost, tools_used, sources } = message.metadata;

    return (
      <div
        style={{ marginTop: 8, paddingTop: 8, borderTop: "1px solid #f0f0f0" }}
      >
        <Space size="small" wrap>
          {model && (
            <Tag size="small" color="blue">
              {model}
            </Tag>
          )}
          {tokens && (
            <Tag size="small" color="green">
              {formatTokens(tokens)} tokens
            </Tag>
          )}
          {cost && (
            <Tag size="small" color="orange">
              {formatCost(cost)}
            </Tag>
          )}
          {tools_used && tools_used.length > 0 && (
            <Tag size="small" color="purple">
              {tools_used.length} tools
            </Tag>
          )}
          {sources && sources.length > 0 && (
            <Tag size="small" color="cyan">
              {sources.length} sources
            </Tag>
          )}
        </Space>
      </div>
    );
  };

  const renderActions = () => {
    if (isSystem) return null;

    return (
      <div style={{ marginTop: 8, display: "flex", gap: 4 }}>
        <Tooltip title={t("chat.copy_message")}>
          <Button
            type="text"
            size="small"
            icon={<CopyOutlined />}
            onClick={handleCopy}
          />
        </Tooltip>

        {onDelete && (
          <Popconfirm
            title={t("chat.delete_message_confirm")}
            onConfirm={handleDelete}
            okText={t("common.yes")}
            cancelText={t("common.no")}
          >
            <Tooltip title={t("chat.delete_message")}>
              <Button
                type="text"
                size="small"
                danger
                icon={<DeleteOutlined />}
              />
            </Tooltip>
          </Popconfirm>
        )}

        {message.status === "error" && onRetry && (
          <Tooltip title={t("chat.retry_message")}>
            <Button
              type="text"
              size="small"
              icon={<ReloadOutlined />}
              onClick={handleRetry}
            />
          </Tooltip>
        )}
      </div>
    );
  };

  return (
    <div style={{ marginBottom: 16 }}>
      <Card size="small" style={getMessageStyle()} bodyStyle={{ padding: 12 }}>
        <div style={{ display: "flex", gap: 12 }}>
          {getAvatar()}

          <div style={{ flex: 1, minWidth: 0 }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "flex-start",
                marginBottom: 8,
              }}
            >
              <Space>
                <Text strong>
                  {isUser
                    ? t("chat.you")
                    : isAssistant
                      ? t("chat.assistant")
                      : t("chat.system")}
                </Text>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {formatTimestamp(message.timestamp)}
                </Text>
              </Space>
            </div>

            {renderContent()}
            {renderMetadata()}
            {renderActions()}
          </div>
        </div>
      </Card>
    </div>
  );
};

export default ChatMessage;
