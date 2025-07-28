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
  Tabs,
  Card,
  Row,
  Col,
  Switch,
  InputNumber,
  Radio,
  Collapse,
} from "antd";
import {
  DownloadOutlined,
  FileTextOutlined,
  FilePdfOutlined,
  FileExcelOutlined,
  FileMarkdownOutlined,
  FilePowerpointOutlined,
  FileHtmlOutlined,
  SettingOutlined,
  BarChartOutlined,
  LayoutOutlined,
  PaletteOutlined,
  PrinterOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useThemeStore } from "../../store/themeStore";
import ModernButton from "../ModernButton";
import type { ChatMessage } from "../../services/chat";
import type { ExtendedChatExportOptions } from "../../services/export";

const { Title, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;
const { Panel } = Collapse;

interface ChatExportProps {
  visible: boolean;
  onClose: () => void;
  messages: ChatMessage[];
  conversationTitle?: string;
  onExport: (options: ExtendedChatExportOptions) => Promise<void>;
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
  const [selectedFormat, setSelectedFormat] = useState<string>("markdown");

  const exportFormats = [
    {
      value: "json",
      label: "JSON",
      icon: <FileTextOutlined />,
      description: t("chat.export.json_description", "Strukturierte Daten für Entwickler"),
      color: "#1890ff",
    },
    {
      value: "pdf",
      label: "PDF",
      icon: <FilePdfOutlined />,
      description: t("chat.export.pdf_description", "Professionelles Dokument für Druck"),
      color: "#ff4d4f",
    },
    {
      value: "excel",
      label: "Excel",
      icon: <FileExcelOutlined />,
      description: t("chat.export.excel_description", "Tabellarische Daten mit Charts"),
      color: "#52c41a",
    },
    {
      value: "powerpoint",
      label: "PowerPoint",
      icon: <FilePowerpointOutlined />,
      description: t("chat.export.powerpoint_description", "Präsentation mit Themes"),
      color: "#fa8c16",
    },
    {
      value: "html",
      label: "HTML",
      icon: <FileHtmlOutlined />,
      description: t("chat.export.html_description", "Web-Dokument mit Templates"),
      color: "#722ed1",
    },
    {
      value: "markdown",
      label: "Markdown",
      icon: <FileMarkdownOutlined />,
      description: t("chat.export.markdown_description", "Formatiert für Dokumentation"),
      color: "#13c2c2",
    },
    {
      value: "txt",
      label: "Text",
      icon: <FileTextOutlined />,
      description: t("chat.export.txt_description", "Einfacher Text-Export"),
      color: "#8c8c8c",
    },
    {
      value: "csv",
      label: "CSV",
      icon: <FileExcelOutlined />,
      description: t("chat.export.csv_description", "Tabellarische Daten"),
      color: "#52c41a",
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

  const renderFormatCard = (format: any) => (
    <Card
      key={format.value}
      hoverable
      style={{
        cursor: "pointer",
        border: selectedFormat === format.value ? `2px solid ${format.color}` : "1px solid #d9d9d9",
        borderRadius: "12px",
        transition: "all 0.3s ease",
      }}
      onClick={() => {
        setSelectedFormat(format.value);
        form.setFieldsValue({ format: format.value });
        setError(null);
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <div style={{ 
          color: format.color, 
          fontSize: "24px",
          display: "flex",
          alignItems: "center"
        }}>
          {format.icon}
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 600, fontSize: "16px", marginBottom: 4 }}>
            {format.label}
          </div>
          <div style={{ fontSize: "12px", color: colors.colorTextSecondary }}>
            {format.description}
          </div>
        </div>
      </div>
    </Card>
  );

  const renderExcelOptions = () => (
    <Panel header={<><BarChartOutlined /> Excel Optionen</>} key="excel">
      <Row gutter={16}>
        <Col span={12}>
          <Form.Item
            name={["excelOptions", "multipleSheets"]}
            valuePropName="checked"
          >
            <Switch checkedChildren="Aktiv" unCheckedChildren="Inaktiv" />
          </Form.Item>
          <Text>Mehrere Arbeitsblätter</Text>
        </Col>
        <Col span={12}>
          <Form.Item
            name={["excelOptions", "includeCharts"]}
            valuePropName="checked"
          >
            <Switch checkedChildren="Aktiv" unCheckedChildren="Inaktiv" />
          </Form.Item>
          <Text>Charts einbeziehen</Text>
        </Col>
      </Row>
      <Row gutter={16}>
        <Col span={12}>
          <Form.Item
            name={["excelOptions", "autoFilter"]}
            valuePropName="checked"
          >
            <Switch checkedChildren="Aktiv" unCheckedChildren="Inaktiv" />
          </Form.Item>
          <Text>Auto-Filter</Text>
        </Col>
        <Col span={12}>
          <Form.Item
            name={["excelOptions", "freezeHeader"]}
            valuePropName="checked"
          >
            <Switch checkedChildren="Aktiv" unCheckedChildren="Inaktiv" />
          </Form.Item>
          <Text>Header einfrieren</Text>
        </Col>
      </Row>
    </Panel>
  );

  const renderPowerPointOptions = () => (
    <Panel header={<><LayoutOutlined /> PowerPoint Optionen</>} key="powerpoint">
      <Form.Item
        name={["powerpointOptions", "slideLayout"]}
        label="Slide Layout"
      >
        <Select size="large">
          <Option value="title-content">Titel & Inhalt</Option>
          <Option value="two-column">Zwei Spalten</Option>
          <Option value="timeline">Timeline</Option>
          <Option value="summary">Zusammenfassung</Option>
        </Select>
      </Form.Item>
      
      <Form.Item
        name={["powerpointOptions", "theme"]}
        label="Theme"
      >
        <Select size="large">
          <Option value="default">Standard</Option>
          <Option value="modern">Modern</Option>
          <Option value="corporate">Corporate</Option>
          <Option value="creative">Creative</Option>
        </Select>
      </Form.Item>
      
      <Form.Item
        name={["powerpointOptions", "includeCharts"]}
        valuePropName="checked"
      >
        <Switch checkedChildren="Aktiv" unCheckedChildren="Inaktiv" />
      </Form.Item>
      <Text>Charts einbeziehen</Text>
    </Panel>
  );

  const renderPDFOptions = () => (
    <Panel header={<><PrinterOutlined /> PDF Optionen</>} key="pdf">
      <Row gutter={16}>
        <Col span={12}>
          <Form.Item
            name={["pdfOptions", "pageSize"]}
            label="Seitengröße"
          >
            <Select size="large">
              <Option value="A4">A4</Option>
              <Option value="Letter">Letter</Option>
              <Option value="Legal">Legal</Option>
              <Option value="A3">A3</Option>
            </Select>
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item
            name={["pdfOptions", "orientation"]}
            label="Ausrichtung"
          >
            <Radio.Group>
              <Radio.Button value="portrait">Hochformat</Radio.Button>
              <Radio.Button value="landscape">Querformat</Radio.Button>
            </Radio.Group>
          </Form.Item>
        </Col>
      </Row>
      
      <Row gutter={16}>
        <Col span={8}>
          <Form.Item
            name={["pdfOptions", "header"]}
            valuePropName="checked"
          >
            <Switch checkedChildren="Aktiv" unCheckedChildren="Inaktiv" />
          </Form.Item>
          <Text>Header</Text>
        </Col>
        <Col span={8}>
          <Form.Item
            name={["pdfOptions", "footer"]}
            valuePropName="checked"
          >
            <Switch checkedChildren="Aktiv" unCheckedChildren="Inaktiv" />
          </Form.Item>
          <Text>Footer</Text>
        </Col>
        <Col span={8}>
          <Form.Item
            name={["pdfOptions", "pageNumbers"]}
            valuePropName="checked"
          >
            <Switch checkedChildren="Aktiv" unCheckedChildren="Inaktiv" />
          </Form.Item>
          <Text>Seitennummern</Text>
        </Col>
      </Row>
      
      <Text strong style={{ display: "block", marginBottom: 8 }}>Ränder (mm)</Text>
      <Row gutter={8}>
        <Col span={6}>
          <Form.Item name={["pdfOptions", "margins", "top"]} label="Oben">
            <InputNumber min={0} max={50} defaultValue={20} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={["pdfOptions", "margins", "right"]} label="Rechts">
            <InputNumber min={0} max={50} defaultValue={20} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={["pdfOptions", "margins", "bottom"]} label="Unten">
            <InputNumber min={0} max={50} defaultValue={20} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name={["pdfOptions", "margins", "left"]} label="Links">
            <InputNumber min={0} max={50} defaultValue={20} />
          </Form.Item>
        </Col>
      </Row>
    </Panel>
  );

  const renderHTMLOptions = () => (
    <Panel header={<><PaletteOutlined /> HTML Template</>} key="html">
      <Form.Item
        name="template"
        label="Template"
      >
        <Select size="large">
          <Option value="default">Standard</Option>
          <Option value="professional">Professional</Option>
          <Option value="minimal">Minimal</Option>
          <Option value="detailed">Detailliert</Option>
          <Option value="custom">Custom</Option>
        </Select>
      </Form.Item>
    </Panel>
  );

  return (
    <Modal
      title={
        <Space>
          <DownloadOutlined />
          <Title level={4} style={{ margin: 0 }}>
            {t("chat.export.title", "Chat Export")}
          </Title>
        </Space>
      }
      open={visible}
      onCancel={handleClose}
      footer={null}
      width={800}
      destroyOnClose
    >
      {conversationTitle && (
        <div style={{ marginBottom: 16 }}>
          <Text strong>{t("chat.export.conversation", "Konversation")}:</Text>
          <Text style={{ marginLeft: 8 }}>{conversationTitle}</Text>
        </div>
      )}

      <div style={{ marginBottom: 16 }}>
        <Text type="secondary">
          {t("chat.export.messages_count", { count: messages.length }, `${messages.length} Nachrichten`)}
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
          template: "default",
          excelOptions: {
            multipleSheets: true,
            includeCharts: false,
            autoFilter: true,
            freezeHeader: true,
          },
          powerpointOptions: {
            slideLayout: "title-content",
            theme: "default",
            includeCharts: false,
          },
          pdfOptions: {
            pageSize: "A4",
            orientation: "portrait",
            header: true,
            footer: true,
            pageNumbers: true,
            margins: { top: 20, right: 20, bottom: 20, left: 20 },
          },
        }}
      >
        <Tabs defaultActiveKey="format" style={{ marginBottom: 24 }}>
          <TabPane tab="Export Format" key="format">
            <Form.Item
              name="format"
              rules={[{ required: true, message: t("chat.export.format_required", "Bitte wählen Sie ein Format") }]}
            >
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12 }}>
                {exportFormats.map(renderFormatCard)}
              </div>
            </Form.Item>
          </TabPane>
          
          <TabPane tab="Erweiterte Optionen" key="advanced">
            <Collapse defaultActiveKey={[]} ghost>
              {selectedFormat === "excel" && renderExcelOptions()}
              {selectedFormat === "powerpoint" && renderPowerPointOptions()}
              {selectedFormat === "pdf" && renderPDFOptions()}
              {selectedFormat === "html" && renderHTMLOptions()}
            </Collapse>
          </TabPane>
          
          <TabPane tab="Inhalt" key="content">
            <Form.Item
              name="messageFilter"
              label={t("chat.export.message_filter", "Nachrichten Filter")}
            >
              <Select size="large">
                <Option value="all">{t("chat.export.filter_all", "Alle Nachrichten")}</Option>
                <Option value="user">{t("chat.export.filter_user", "Nur User Nachrichten")}</Option>
                <Option value="assistant">{t("chat.export.filter_assistant", "Nur Assistant Nachrichten")}</Option>
              </Select>
            </Form.Item>

            <Form.Item
              name="includeMetadata"
              valuePropName="checked"
            >
              <Checkbox>{t("chat.export.include_metadata", "Metadaten einbeziehen")}</Checkbox>
            </Form.Item>

            <Form.Item
              name="includeTimestamps"
              valuePropName="checked"
            >
              <Checkbox>{t("chat.export.include_timestamps", "Zeitstempel einbeziehen")}</Checkbox>
            </Form.Item>

            <Form.Item
              name="includeUserInfo"
              valuePropName="checked"
            >
              <Checkbox>{t("chat.export.include_user_info", "Benutzer-Info einbeziehen")}</Checkbox>
            </Form.Item>
          </TabPane>
        </Tabs>
      </Form>

      <div style={{ 
        display: "flex", 
        justifyContent: "flex-end", 
        gap: 12, 
        marginTop: 24 
      }}>
        <ModernButton
          variant="ghost"
          onClick={handleClose}
          disabled={exporting}
        >
          {t("common.cancel", "Abbrechen")}
        </ModernButton>
        <ModernButton
          variant="primary"
          icon={<DownloadOutlined />}
          onClick={handleExport}
          loading={exporting}
        >
          {exporting ? t("chat.export.exporting", "Exportiere...") : t("chat.export.export", "Exportieren")}
        </ModernButton>
      </div>
    </Modal>
  );
};

export default ChatExport;