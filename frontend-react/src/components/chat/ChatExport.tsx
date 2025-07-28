import React, { useState } from "react";
import {
  Modal,
  Form,
  Select,
  Button,
  Space,
  Typography,
  Alert,
  Spin,
  Checkbox,
  Divider,
} from "antd";
import {
  DownloadOutlined,
  FileTextOutlined,
  FilePdfOutlined,
  FileExcelOutlined,
  FileMarkdownOutlined,
  SettingOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useThemeStore } from "../../store/themeStore";
import ModernButton from "../ModernButton";
import type { ChatMessage } from "../../services/chat";

const { Title, Text } = Typography;
const { Option } = Select;

export interface ChatExportOptions {
  format: "json" | "pdf" | "markdown" | "txt" | "csv";
  includeMetadata: boolean;
  includeTimestamps: boolean;
  includeUserInfo: boolean;
  dateRange?: {
    start: string;
    end: string;
  };
  messageFilter?: "all" | "user" | "assistant";
}

interface ChatExportProps {
  visible: boolean;
  onClose: () => void;
  messages: ChatMessage[];
  conversationTitle?: string;
  onExport: (options: ChatExportOptions) => Promise<void>;
}

const ChatExport: React.FC<ChatExportProps> = ({
  visible,
  onClose,
  messages,
  conversationTitle,
  onExport,
}) => {
  const { t } = useTranslation();
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const [form] = Form.useForm();
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const exportFormats = [
    {
      value: "json",
      label: "JSON",
      icon: <FileTextOutlined />,
      description: t("chat.export.json_description"),
    },
    {
      value: "pdf",
      label: "PDF",
      icon: <FilePdfOutlined />,
      description: t("chat.export.pdf_description"),
    },
    {
      value: "markdown",
      label: "Markdown",
      icon: <FileMarkdownOutlined />,
      description: t("chat.export.markdown_description"),
    },
    {
      value: "txt",
      label: "Text",
      icon: <FileTextOutlined />,
      description: t("chat.export.txt_description"),
    },
    {
      value: "csv",
      label: "CSV",
      icon: <FileExcelOutlined />,
      description: t("chat.export.csv_description"),
    },
  ];

  const handleExport = async () => {
    try {
      setExporting(true);
      setError(null);

      const values = await form.validateFields();
      await onExport(values);
      
      onClose();
    } catch (err) {
      console.error("Export error:", err);
      setError(t("chat.export.error"));
    } finally {
      setExporting(false);
    }
  };

  const handleClose = () => {
    form.resetFields();
    setError(null);
    onClose();
  };

  const getFormatIcon = (format: string) => {
    const formatInfo = exportFormats.find(f => f.value === format);
    return formatInfo?.icon || <FileTextOutlined />;
  };

  return (
    <Modal
      title={
        <Space>
          <DownloadOutlined />
          <Title level={4} style={{ margin: 0 }}>
            {t("chat.export.title")}
          </Title>
        </Space>
      }
      open={visible}
      onCancel={handleClose}
      footer={null}
      width={600}
      destroyOnClose
    >
      {conversationTitle && (
        <div style={{ marginBottom: 16 }}>
          <Text strong>{t("chat.export.conversation")}:</Text>
          <Text style={{ marginLeft: 8 }}>{conversationTitle}</Text>
        </div>
      )}

      <div style={{ marginBottom: 16 }}>
        <Text type="secondary">
          {t("chat.export.messages_count", { count: messages.length })}
        </Text>
      </div>

      {error && (
        <Alert
          message={error}
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      <Form
        form={form}
        layout="vertical"
        initialValues={{
          format: "markdown",
          includeMetadata: true,
          includeTimestamps: true,
          includeUserInfo: true,
          messageFilter: "all",
        }}
      >
        <Form.Item
          name="format"
          label={t("chat.export.format")}
          rules={[{ required: true, message: t("chat.export.format_required") }]}
        >
          <Select
            placeholder={t("chat.export.select_format")}
            size="large"
            onChange={() => setError(null)}
          >
            {exportFormats.map((format) => (
              <Option key={format.value} value={format.value}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{ color: colors.colorPrimary }}>{format.icon}</span>
                  <div>
                    <div style={{ fontWeight: 500 }}>{format.label}</div>
                    <div style={{ fontSize: "12px", color: colors.colorTextSecondary }}>
                      {format.description}
                    </div>
                  </div>
                </div>
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Divider />

        <Form.Item
          name="messageFilter"
          label={t("chat.export.message_filter")}
        >
          <Select size="large">
            <Option value="all">{t("chat.export.filter_all")}</Option>
            <Option value="user">{t("chat.export.filter_user")}</Option>
            <Option value="assistant">{t("chat.export.filter_assistant")}</Option>
          </Select>
        </Form.Item>

        <Form.Item
          name="includeMetadata"
          valuePropName="checked"
        >
          <Checkbox>{t("chat.export.include_metadata")}</Checkbox>
        </Form.Item>

        <Form.Item
          name="includeTimestamps"
          valuePropName="checked"
        >
          <Checkbox>{t("chat.export.include_timestamps")}</Checkbox>
        </Form.Item>

        <Form.Item
          name="includeUserInfo"
          valuePropName="checked"
        >
          <Checkbox>{t("chat.export.include_user_info")}</Checkbox>
        </Form.Item>
      </Form>

      <div style={{ 
        display: "flex", 
        justifyContent: "flex-end", 
        gap: 12, 
        marginTop: 24 
      }}>
        <ModernButton
          variant="outlined"
          onClick={handleClose}
          disabled={exporting}
        >
          {t("common.cancel")}
        </ModernButton>
        <ModernButton
          variant="primary"
          icon={<DownloadOutlined />}
          onClick={handleExport}
          loading={exporting}
        >
          {exporting ? t("chat.export.exporting") : t("chat.export.export")}
        </ModernButton>
      </div>
    </Modal>
  );
};

export default ChatExport;