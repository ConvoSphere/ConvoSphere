import React, { useRef, useEffect } from "react";
import { Layout, Spin, Empty, Alert } from "antd";
import { useTranslation } from "react-i18next";
import { ChatMessage as ChatMessageType } from "../types/chat.types";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import ChatToolbar from "./ChatToolbar";
import { useChat } from "../hooks/useChat";

const { Content } = Layout;

interface ChatContainerProps {
  threadId?: string;
  assistantId?: string;
  onThreadChange?: (threadId: string) => void;
  showToolbar?: boolean;
  showMetadata?: boolean;
  allowAttachments?: boolean;
  maxMessages?: number;
}

const ChatContainer: React.FC<ChatContainerProps> = ({
  threadId,
  assistantId,
  onThreadChange,
  showToolbar = true,
  showMetadata = false,
  allowAttachments = true,
  maxMessages = 100,
}) => {
  const { t } = useTranslation();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    messages,
    thread,
    assistant,
    isLoading,
    isStreaming,
    error,
    settings,
    addMessage,
    updateMessage,
    removeMessage,
    clearMessages,
    sendMessage,
    sendMessageStreaming,
    stopStreaming,
    updateSettings,
    loadThread,
    saveThread,
    exportChat,
  } = useChat();

  // Load thread on mount if threadId is provided
  useEffect(() => {
    if (threadId) {
      loadThread(threadId);
    }
  }, [threadId, loadThread]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (formData: any) => {
    if (isStreaming) {
      await sendMessageStreaming(formData);
    } else {
      await sendMessage(formData);
    }
  };

  const handleStopStreaming = () => {
    stopStreaming();
  };

  const handleClearMessages = () => {
    clearMessages();
  };

  const handleSaveThread = () => {
    saveThread();
  };

  const handleExportChat = (options: any) => {
    exportChat(options.format);
  };

  const handleSettingsChange = (newSettings: any) => {
    updateSettings(newSettings);
  };

  const handleCopyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  const handleDeleteMessage = (id: string) => {
    removeMessage(id);
  };

  const handleRetryMessage = (id: string) => {
    // Find the message and retry
    const messageIndex = messages.findIndex((m) => m.id === id);
    if (messageIndex > 0) {
      const previousMessage = messages[messageIndex - 1];
      if (previousMessage.role === "user") {
        sendMessage({ message: previousMessage.content });
      }
    }
  };

  const renderMessages = () => {
    if (isLoading && messages.length === 0) {
      return (
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            height: "50vh",
          }}
        >
          <Spin size="large" />
        </div>
      );
    }

    if (messages.length === 0) {
      return (
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            height: "50vh",
          }}
        >
          <Empty
            description={t("chat.no_messages")}
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        </div>
      );
    }

    // Limit messages to prevent performance issues
    const displayMessages = messages.slice(-maxMessages);

    return (
      <div style={{ padding: "16px 0" }}>
        {displayMessages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message}
            onCopy={handleCopyMessage}
            onDelete={handleDeleteMessage}
            onRetry={handleRetryMessage}
            showMetadata={showMetadata}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>
    );
  };

  const renderError = () => {
    if (!error) return null;

    return (
      <Alert
        message={t("chat.error")}
        description={error.message}
        type="error"
        showIcon
        closable
        style={{ margin: 16 }}
      />
    );
  };

  const renderWelcomeMessage = () => {
    if (messages.length > 0 || isLoading) return null;

    return (
      <div
        style={{
          textAlign: "center",
          padding: "40px 20px",
          color: "#666",
          maxWidth: 600,
          margin: "0 auto",
        }}
      >
        <h2>{t("chat.welcome_title")}</h2>
        <p>{t("chat.welcome_message")}</p>
        {assistant && (
          <div
            style={{
              marginTop: 20,
              padding: 16,
              backgroundColor: "#f5f5f5",
              borderRadius: 8,
            }}
          >
            <h4>{assistant.name}</h4>
            <p>{assistant.description}</p>
          </div>
        )}
      </div>
    );
  };

  return (
    <Layout
      style={{ height: "100vh", display: "flex", flexDirection: "column" }}
    >
      {/* Toolbar */}
      {showToolbar && (
        <ChatToolbar
          onSave={handleSaveThread}
          onExport={handleExportChat}
          onClear={handleClearMessages}
          onSettings={handleSettingsChange}
          settings={settings}
          hasMessages={messages.length > 0}
          isLoading={isLoading}
          disabled={isStreaming}
        />
      )}

      {/* Error Display */}
      {renderError()}

      {/* Messages Content */}
      <Content
        style={{
          flex: 1,
          overflow: "auto",
          backgroundColor: "#fff",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {renderWelcomeMessage()}
        {renderMessages()}
      </Content>

      {/* Input */}
      <ChatInput
        onSend={handleSendMessage}
        onStop={handleStopStreaming}
        onClear={handleClearMessages}
        onSettings={() => handleSettingsChange(settings)}
        isLoading={isLoading}
        isStreaming={isStreaming}
        disabled={false}
        allowAttachments={allowAttachments}
        placeholder={t("chat.type_message_placeholder")}
      />
    </Layout>
  );
};

export default ChatContainer;
