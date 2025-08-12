import React, { useState, useRef, useEffect } from "react";
import {
  Input,
  Button,
  Space,
  Upload,
  Tooltip,
  Popconfirm,
  message,
} from "antd";
import {
  SendOutlined,
  PaperClipOutlined,
  StopOutlined,
  ClearOutlined,
  SettingOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { ChatFormData } from "../types/chat.types";

const { TextArea } = Input;

interface ChatInputProps {
  onSend: (formData: ChatFormData) => void;
  onStop?: () => void;
  onClear?: () => void;
  onSettings?: () => void;
  isLoading?: boolean;
  isStreaming?: boolean;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
  allowAttachments?: boolean;
  maxAttachments?: number;
}

const ChatInput: React.FC<ChatInputProps> = ({
  onSend,
  onStop,
  onClear,
  onSettings,
  isLoading = false,
  isStreaming = false,
  disabled = false,
  placeholder,
  maxLength = 4000,
  allowAttachments = true,
  maxAttachments = 5,
}) => {
  const { t } = useTranslation();
  const [inputValue, setInputValue] = useState("");
  const [attachments, setAttachments] = useState<File[]>([]);
  const textAreaRef = useRef<any>(null);

  const handleSend = () => {
    if (!inputValue.trim() && attachments.length === 0) return;

    const formData: ChatFormData = {
      message: inputValue.trim(),
      attachments: attachments.length > 0 ? attachments : undefined,
    };

    onSend(formData);
    setInputValue("");
    setAttachments([]);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClear = () => {
    setInputValue("");
    setAttachments([]);
    if (onClear) {
      onClear();
    }
  };

  const handleStop = () => {
    if (onStop) {
      onStop();
    }
  };

  const handleFileUpload = (file: File) => {
    if (attachments.length >= maxAttachments) {
      message.error(t("chat.max_attachments_reached", { max: maxAttachments }));
      return false;
    }

    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      message.error(t("chat.file_too_large", { maxSize: "10MB" }));
      return false;
    }

    setAttachments((prev) => [...prev, file]);
    return false; // Prevent default upload behavior
  };

  const removeAttachment = (index: number) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const getSendButtonIcon = () => {
    if (isStreaming) {
      return <StopOutlined />;
    }
    return <SendOutlined />;
  };

  const getSendButtonText = () => {
    if (isStreaming) {
      return t("chat.stop");
    }
    return t("chat.send");
  };

  const isSendDisabled = () => {
    return (
      disabled || isLoading || (!inputValue.trim() && attachments.length === 0)
    );
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textAreaRef.current) {
      textAreaRef.current.focus();
    }
  }, []);

  return (
    <div
      style={{
        padding: 16,
        borderTop: "1px solid #f0f0f0",
        backgroundColor: "#fff",
      }}
    >
      {/* Attachments */}
      {attachments.length > 0 && (
        <div style={{ marginBottom: 12 }}>
          <Space wrap>
            {attachments.map((file, index) => (
              <div
                key={index}
                style={{
                  padding: "4px 8px",
                  backgroundColor: "#f5f5f5",
                  borderRadius: 4,
                  fontSize: 12,
                  display: "flex",
                  alignItems: "center",
                  gap: 4,
                }}
              >
                <span>{file.name}</span>
                <span style={{ color: "#999" }}>
                  ({formatFileSize(file.size)})
                </span>
                <Button
                  type="text"
                  size="small"
                  danger
                  onClick={() => removeAttachment(index)}
                  style={{ padding: 0, height: "auto" }}
                >
                  ×
                </Button>
              </div>
            ))}
          </Space>
        </div>
      )}

      {/* Input Area */}
      <div style={{ display: "flex", gap: 8, alignItems: "flex-end" }}>
        <div style={{ flex: 1 }}>
          <TextArea
            ref={textAreaRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={placeholder || t("chat.type_message")}
            autoSize={{ minRows: 1, maxRows: 6 }}
            maxLength={maxLength}
            disabled={disabled || isLoading}
            style={{ resize: "none" }}
          />
          <div style={{ fontSize: 12, color: "#999", marginTop: 4 }}>
            {inputValue.length}/{maxLength}
          </div>
        </div>

        <Space direction="vertical" size="small">
          {/* Send/Stop Button */}
          <Button
            type="primary"
            icon={getSendButtonIcon()}
            onClick={isStreaming ? handleStop : handleSend}
            disabled={isSendDisabled()}
            loading={isLoading && !isStreaming}
            style={{ height: 40, width: 40 }}
          />

          {/* Action Buttons */}
          <Space size="small">
            {allowAttachments && (
              <Upload
                beforeUpload={handleFileUpload}
                showUploadList={false}
                disabled={disabled || isLoading}
              >
                <Tooltip title={t("chat.attach_file")}>
                  <Button
                    type="text"
                    icon={<PaperClipOutlined />}
                    disabled={disabled || isLoading}
                    style={{ height: 32, width: 32 }}
                  />
                </Tooltip>
              </Upload>
            )}

            {onSettings && (
              <Tooltip title={t("chat.settings")}>
                <Button
                  type="text"
                  icon={<SettingOutlined />}
                  onClick={onSettings}
                  disabled={disabled || isLoading}
                  style={{ height: 32, width: 32 }}
                />
              </Tooltip>
            )}

            {onClear && (
              <Popconfirm
                title={t("chat.clear_confirm")}
                onConfirm={handleClear}
                okText={t("common.yes")}
                cancelText={t("common.no")}
              >
                <Tooltip title={t("chat.clear")}>
                  <Button
                    type="text"
                    icon={<ClearOutlined />}
                    disabled={disabled || isLoading}
                    style={{ height: 32, width: 32 }}
                  />
                </Tooltip>
              </Popconfirm>
            )}
          </Space>
        </Space>
      </div>

      {/* Keyboard Shortcuts Info */}
      <div style={{ fontSize: 12, color: "#999", marginTop: 8 }}>
        {t("chat.shortcuts_info")}
      </div>
    </div>
  );
};

export default ChatInput;
