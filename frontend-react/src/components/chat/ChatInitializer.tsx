import React, { useState, useEffect } from "react";
import {
  Form,
  Input,
  Select,
  Button,
  Alert,
  Spin,
  Space,
  Typography,
} from "antd";
import {
  MessageOutlined,
  RobotOutlined,
  SendOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../../store/authStore";
import { useThemeStore } from "../../store/themeStore";
import ModernCard from "../ModernCard";
import ModernButton from "../ModernButton";
import { config } from "../../config";

const { TextArea } = Input;
const { Option } = Select;
const { Title, Text } = Typography;

interface Assistant {
  id: string;
  name: string;
  description: string;
  personality: string;
  isActive: boolean;
}

interface ChatInitializerProps {
  variant?: "card" | "inline" | "minimal";
  showTitle?: boolean;
  onSuccess?: (conversationId: string) => void;
  className?: string;
}

const ChatInitializer: React.FC<ChatInitializerProps> = ({
  variant = "card",
  showTitle = true,
  onSuccess,
  className,
}) => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const token = useAuthStore((s) => s.token);
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const [form] = Form.useForm();
  const [assistants, setAssistants] = useState<Assistant[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load available assistants
  useEffect(() => {
    const loadAssistants = async () => {
      if (!token) return;

      try {
        setLoading(true);
        const response = await fetch(`${config.apiUrl}/v1/assistants`, {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });

        if (response.ok) {
          const data = await response.json();
          setAssistants(data.filter((assistant: Assistant) => assistant.isActive));
        } else {
          throw new Error("Failed to load assistants");
        }
      } catch (err) {
        console.error("Error loading assistants:", err);
        setError(t("home.error_loading_assistants"));
      } finally {
        setLoading(false);
      }
    };

    loadAssistants();
  }, [token, t]);

  const handleStartChat = async (values: {
    initialMessage: string;
    assistantId: string;
  }) => {
    if (!token) return;

    try {
      setSubmitting(true);
      setError(null);

      // Create new conversation
      const conversationResponse = await fetch(
        `${config.apiUrl}/v1/chat/conversations`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            assistant_id: values.assistantId,
            title: values.initialMessage.substring(0, 50) + "...",
          }),
        }
      );

      if (!conversationResponse.ok) {
        throw new Error("Failed to create conversation");
      }

      const conversation = await conversationResponse.json();

      // Send initial message
      const messageResponse = await fetch(
        `${config.apiUrl}/v1/chat/conversations/${conversation.id}/messages`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            content: values.initialMessage,
            role: "user",
          }),
        }
      );

      if (!messageResponse.ok) {
        throw new Error("Failed to send initial message");
      }

      // Call onSuccess callback if provided
      if (onSuccess) {
        onSuccess(conversation.id);
      } else {
        // Navigate to chat with conversation ID
        navigate(`/chat?conversation=${conversation.id}`);
      }
    } catch (err) {
      console.error("Error starting chat:", err);
      setError(t("home.error_starting_chat"));
    } finally {
      setSubmitting(false);
    }
  };

  const handleQuickStart = (assistantId: string) => {
    form.setFieldsValue({ assistantId });
    form.submit();
  };

  const renderForm = () => (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleStartChat}
      initialValues={{
        assistantId: assistants.length > 0 ? assistants[0].id : undefined,
      }}
    >
      <Form.Item
        name="assistantId"
        label={variant === "minimal" ? undefined : t("home.select_assistant")}
        rules={[{ required: true, message: t("home.assistant_required") }]}
      >
        <Select
          placeholder={t("home.assistant_placeholder")}
          loading={loading}
          size={variant === "minimal" ? "middle" : "large"}
        >
          {assistants.map((assistant) => (
            <Option key={assistant.id} value={assistant.id}>
              <Space>
                <RobotOutlined />
                <div>
                  <div style={{ fontWeight: 500 }}>{assistant.name}</div>
                  {variant !== "minimal" && (
                    <div style={{ fontSize: "12px", color: colors.colorTextSecondary }}>
                      {assistant.description}
                    </div>
                  )}
                </div>
              </Space>
            </Option>
          ))}
        </Select>
      </Form.Item>

      <Form.Item
        name="initialMessage"
        label={variant === "minimal" ? undefined : t("home.initial_message")}
        rules={[{ required: true, message: t("home.message_required") }]}
      >
        <TextArea
          placeholder={t("home.message_placeholder")}
          rows={variant === "minimal" ? 2 : 4}
          maxLength={1000}
          showCount={variant !== "minimal"}
          size={variant === "minimal" ? "middle" : "large"}
        />
      </Form.Item>

      <Form.Item>
        <ModernButton
          type="primary"
          htmlType="submit"
          size={variant === "minimal" ? "middle" : "large"}
          loading={submitting}
          icon={<SendOutlined />}
          style={{ width: variant === "minimal" ? "auto" : "100%" }}
        >
          {t("home.start_chat_button")}
        </ModernButton>
      </Form.Item>
    </Form>
  );

  if (loading) {
    return (
      <div style={{ 
        display: "flex", 
        justifyContent: "center", 
        alignItems: "center", 
        padding: variant === "minimal" ? "16px" : "40px" 
      }}>
        <Spin size={variant === "minimal" ? "default" : "large"} />
      </div>
    );
  }

  if (variant === "minimal") {
    return (
      <div className={className}>
        {error && (
          <Alert
            message={error}
            type="error"
            showIcon
            closable
            onClose={() => setError(null)}
            style={{ marginBottom: 16 }}
          />
        )}
        {renderForm()}
      </div>
    );
  }

  if (variant === "inline") {
    return (
      <div className={className}>
        {error && (
          <Alert
            message={error}
            type="error"
            showIcon
            closable
            onClose={() => setError(null)}
            style={{ marginBottom: 16 }}
          />
        )}
        {showTitle && (
          <Title level={4} style={{ marginBottom: 16 }}>
            <MessageOutlined style={{ marginRight: 8 }} />
            {t("home.start_chat")}
          </Title>
        )}
        {renderForm()}
      </div>
    );
  }

  // Default card variant
  return (
    <ModernCard
      variant="elevated"
      size="lg"
      header={
        showTitle ? (
          <Title level={3} style={{ margin: 0 }}>
            <MessageOutlined style={{ marginRight: 8 }} />
            {t("home.start_chat")}
          </Title>
        ) : undefined
      }
      className={className}
    >
      {error && (
        <Alert
          message={error}
          type="error"
          showIcon
          closable
          onClose={() => setError(null)}
          style={{ marginBottom: 24 }}
        />
      )}
      {renderForm()}
    </ModernCard>
  );
};

export default ChatInitializer;