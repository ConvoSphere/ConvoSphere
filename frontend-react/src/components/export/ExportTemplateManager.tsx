import React, { useState, useEffect } from "react";
import {
  Modal,
  Form,
  Input,
  Button,
  Space,
  Typography,
  Card,
  Row,
  Col,
  Select,
  Switch,
  ColorPicker,
  Divider,
  message,
  Popconfirm,
  Empty,
  Tag,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SaveOutlined,
  EyeOutlined,
  CopyOutlined,
  PaletteOutlined,
  CodeOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useThemeStore } from "../../store/themeStore";
import ModernButton from "../ModernButton";
import ModernCard from "../ModernCard";

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { TextArea } = Input;

export interface ExportTemplate {
  id: string;
  name: string;
  description: string;
  format: "html" | "pdf" | "excel" | "powerpoint";
  category: "business" | "creative" | "minimal" | "custom";
  template: string;
  variables: TemplateVariable[];
  isDefault: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface TemplateVariable {
  name: string;
  type: "string" | "number" | "boolean" | "color" | "select";
  defaultValue: any;
  description: string;
  options?: string[]; // For select type
}

interface ExportTemplateManagerProps {
  visible: boolean;
  onClose: () => void;
  onTemplateSelect?: (template: ExportTemplate) => void;
}

const ExportTemplateManager: React.FC<ExportTemplateManagerProps> = ({
  visible,
  onClose,
  onTemplateSelect,
}) => {
  const { t } = useTranslation();
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const [form] = Form.useForm();
  const [templates, setTemplates] = useState<ExportTemplate[]>([]);
  const [editingTemplate, setEditingTemplate] = useState<ExportTemplate | null>(null);
  const [previewMode, setPreviewMode] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>("all");

  // Load templates from localStorage
  useEffect(() => {
    const savedTemplates = localStorage.getItem("exportTemplates");
    if (savedTemplates) {
      setTemplates(JSON.parse(savedTemplates));
    } else {
      // Initialize with default templates
      const defaultTemplates = getDefaultTemplates();
      setTemplates(defaultTemplates);
      localStorage.setItem("exportTemplates", JSON.stringify(defaultTemplates));
    }
  }, []);

  const getDefaultTemplates = (): ExportTemplate[] => [
    {
      id: "business-report",
      name: "Business Report",
      description: "Professional business report template with corporate styling",
      format: "html",
      category: "business",
      template: `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>{{title}}</title>
  <style>
    body { 
      font-family: 'Arial', sans-serif; 
      margin: 0; 
      padding: 20px; 
      background-color: #f5f5f5;
    }
    .container {
      max-width: 800px;
      margin: 0 auto;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      overflow: hidden;
    }
    .header {
      background: {{primaryColor}};
      color: white;
      padding: 30px;
      text-align: center;
    }
    .content {
      padding: 30px;
    }
    .message {
      margin-bottom: 20px;
      padding: 15px;
      border-radius: 6px;
      border-left: 4px solid {{accentColor}};
    }
    .user { background-color: #e3f2fd; }
    .assistant { background-color: #f3e5f5; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>{{title}}</h1>
      <p>Generated on {{date}}</p>
    </div>
    <div class="content">
      {{#each messages}}
        <div class="message {{role}}">
          <strong>{{role}}</strong>
          <p>{{content}}</p>
        </div>
      {{/each}}
    </div>
  </div>
</body>
</html>`,
      variables: [
        {
          name: "primaryColor",
          type: "color",
          defaultValue: "#1976d2",
          description: "Primary color for header",
        },
        {
          name: "accentColor",
          type: "color",
          defaultValue: "#ff9800",
          description: "Accent color for borders",
        },
      ],
      isDefault: true,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    {
      id: "creative-presentation",
      name: "Creative Presentation",
      description: "Modern and creative template with gradients and animations",
      format: "html",
      category: "creative",
      template: `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>{{title}}</title>
  <style>
    body { 
      font-family: 'Segoe UI', sans-serif; 
      margin: 0; 
      padding: 0;
      background: linear-gradient(135deg, {{gradientStart}} 0%, {{gradientEnd}} 100%);
      min-height: 100vh;
    }
    .container {
      max-width: 900px;
      margin: 0 auto;
      padding: 40px 20px;
    }
    .header {
      text-align: center;
      color: white;
      margin-bottom: 40px;
    }
    .message {
      background: rgba(255,255,255,0.9);
      margin-bottom: 20px;
      padding: 20px;
      border-radius: 15px;
      backdrop-filter: blur(10px);
      box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .user { border-left: 5px solid {{userColor}}; }
    .assistant { border-left: 5px solid {{assistantColor}}; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>{{title}}</h1>
      <p>{{date}}</p>
    </div>
    {{#each messages}}
      <div class="message {{role}}">
        <h3>{{role}}</h3>
        <p>{{content}}</p>
      </div>
    {{/each}}
  </div>
</body>
</html>`,
      variables: [
        {
          name: "gradientStart",
          type: "color",
          defaultValue: "#667eea",
          description: "Gradient start color",
        },
        {
          name: "gradientEnd",
          type: "color",
          defaultValue: "#764ba2",
          description: "Gradient end color",
        },
        {
          name: "userColor",
          type: "color",
          defaultValue: "#2196f3",
          description: "User message color",
        },
        {
          name: "assistantColor",
          type: "color",
          defaultValue: "#9c27b0",
          description: "Assistant message color",
        },
      ],
      isDefault: true,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
  ];

  const handleSaveTemplate = async () => {
    try {
      const values = await form.validateFields();
      
      const template: ExportTemplate = {
        id: editingTemplate?.id || `template-${Date.now()}`,
        name: values.name,
        description: values.description,
        format: values.format,
        category: values.category,
        template: values.template,
        variables: values.variables || [],
        isDefault: false,
        createdAt: editingTemplate?.createdAt || new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      const updatedTemplates = editingTemplate
        ? templates.map(t => t.id === editingTemplate.id ? template : t)
        : [...templates, template];

      setTemplates(updatedTemplates);
      localStorage.setItem("exportTemplates", JSON.stringify(updatedTemplates));
      
      message.success(t("export.template.saved", "Template gespeichert"));
      setEditingTemplate(null);
      form.resetFields();
    } catch (error) {
      console.error("Save template error:", error);
      message.error(t("export.template.save_error", "Fehler beim Speichern"));
    }
  };

  const handleDeleteTemplate = (templateId: string) => {
    const updatedTemplates = templates.filter(t => t.id !== templateId);
    setTemplates(updatedTemplates);
    localStorage.setItem("exportTemplates", JSON.stringify(updatedTemplates));
    message.success(t("export.template.deleted", "Template gelöscht"));
  };

  const handleDuplicateTemplate = (template: ExportTemplate) => {
    const duplicatedTemplate: ExportTemplate = {
      ...template,
      id: `template-${Date.now()}`,
      name: `${template.name} (Kopie)`,
      isDefault: false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    const updatedTemplates = [...templates, duplicatedTemplate];
    setTemplates(updatedTemplates);
    localStorage.setItem("exportTemplates", JSON.stringify(updatedTemplates));
    message.success(t("export.template.duplicated", "Template dupliziert"));
  };

  const filteredTemplates = templates.filter(template => 
    selectedCategory === "all" || template.category === selectedCategory
  );

  const categories = [
    { value: "all", label: "Alle", color: "#1890ff" },
    { value: "business", label: "Business", color: "#52c41a" },
    { value: "creative", label: "Creative", color: "#722ed1" },
    { value: "minimal", label: "Minimal", color: "#8c8c8c" },
    { value: "custom", label: "Custom", color: "#fa8c16" },
  ];

  const renderTemplateCard = (template: ExportTemplate) => (
    <ModernCard
      key={template.id}
      variant="interactive"
      size="md"
      style={{ marginBottom: 16 }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
            <Title level={5} style={{ margin: 0 }}>{template.name}</Title>
            {template.isDefault && (
              <Tag color="blue">Standard</Tag>
            )}
            <Tag color={categories.find(c => c.value === template.category)?.color}>
              {categories.find(c => c.value === template.category)?.label}
            </Tag>
          </div>
          <Paragraph style={{ color: colors.colorTextSecondary, marginBottom: 12 }}>
            {template.description}
          </Paragraph>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <Tag icon={<CodeOutlined />}>{template.format.toUpperCase()}</Tag>
            <Tag>{template.variables.length} Variablen</Tag>
          </div>
        </div>
        
        <div style={{ display: "flex", gap: 8 }}>
          <ModernButton
            variant="ghost"
            size="sm"
            icon={<EyeOutlined />}
            onClick={() => setPreviewMode(true)}
          />
          <ModernButton
            variant="ghost"
            size="sm"
            icon={<CopyOutlined />}
            onClick={() => handleDuplicateTemplate(template)}
          />
          <ModernButton
            variant="ghost"
            size="sm"
            icon={<EditOutlined />}
            onClick={() => {
              setEditingTemplate(template);
              form.setFieldsValue(template);
            }}
          />
          {!template.isDefault && (
            <Popconfirm
              title={t("export.template.delete_confirm", "Template wirklich löschen?")}
              onConfirm={() => handleDeleteTemplate(template.id)}
              okText={t("common.yes", "Ja")}
              cancelText={t("common.no", "Nein")}
            >
              <ModernButton
                variant="ghost"
                size="sm"
                icon={<DeleteOutlined />}
                style={{ color: colors.colorError }}
              />
            </Popconfirm>
          )}
        </div>
      </div>
    </ModernCard>
  );

  return (
    <Modal
      title={
        <Space>
          <PaletteOutlined />
          <Title level={4} style={{ margin: 0 }}>
            {t("export.template.manager", "Export Templates")}
          </Title>
        </Space>
      }
      open={visible}
      onCancel={onClose}
      footer={null}
      width={1000}
      destroyOnClose
    >
      <div style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <div style={{ display: "flex", gap: 8 }}>
            {categories.map(category => (
              <ModernButton
                key={category.value}
                variant={selectedCategory === category.value ? "primary" : "ghost"}
                size="sm"
                onClick={() => setSelectedCategory(category.value)}
              >
                {category.label}
              </ModernButton>
            ))}
          </div>
          
          <ModernButton
            variant="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              setEditingTemplate(null);
              form.resetFields();
            }}
          >
            {t("export.template.create", "Neues Template")}
          </ModernButton>
        </div>

        {filteredTemplates.length === 0 ? (
          <Empty
            description={t("export.template.no_templates", "Keine Templates gefunden")}
            style={{ margin: "40px 0" }}
          />
        ) : (
          <div style={{ maxHeight: "400px", overflowY: "auto" }}>
            {filteredTemplates.map(renderTemplateCard)}
          </div>
        )}
      </div>

      {/* Template Editor Modal */}
      <Modal
        title={
          <Space>
            <EditOutlined />
            <Title level={4} style={{ margin: 0 }}>
              {editingTemplate ? t("export.template.edit", "Template bearbeiten") : t("export.template.create", "Neues Template")}
            </Title>
          </Space>
        }
        open={!!editingTemplate || form.getFieldValue("name")}
        onCancel={() => {
          setEditingTemplate(null);
          form.resetFields();
        }}
        footer={null}
        width={800}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            format: "html",
            category: "custom",
            variables: [],
          }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="name"
                label={t("export.template.name", "Name")}
                rules={[{ required: true, message: t("export.template.name_required", "Name ist erforderlich") }]}
              >
                <Input placeholder={t("export.template.name_placeholder", "Template Name")} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="format"
                label={t("export.template.format", "Format")}
                rules={[{ required: true }]}
              >
                <Select>
                  <Option value="html">HTML</Option>
                  <Option value="pdf">PDF</Option>
                  <Option value="excel">Excel</Option>
                  <Option value="powerpoint">PowerPoint</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="description"
            label={t("export.template.description", "Beschreibung")}
          >
            <TextArea
              rows={2}
              placeholder={t("export.template.description_placeholder", "Template Beschreibung")}
            />
          </Form.Item>

          <Form.Item
            name="category"
            label={t("export.template.category", "Kategorie")}
          >
            <Select>
              <Option value="business">Business</Option>
              <Option value="creative">Creative</Option>
              <Option value="minimal">Minimal</Option>
              <Option value="custom">Custom</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="template"
            label={t("export.template.template", "Template Code")}
            rules={[{ required: true, message: t("export.template.template_required", "Template Code ist erforderlich") }]}
          >
            <TextArea
              rows={12}
              placeholder={t("export.template.template_placeholder", "Template Code hier eingeben...")}
              style={{ fontFamily: "monospace" }}
            />
          </Form.Item>

          <div style={{ display: "flex", justifyContent: "flex-end", gap: 12 }}>
            <ModernButton
              variant="ghost"
              onClick={() => {
                setEditingTemplate(null);
                form.resetFields();
              }}
            >
              {t("common.cancel", "Abbrechen")}
            </ModernButton>
            <ModernButton
              variant="primary"
              icon={<SaveOutlined />}
              onClick={handleSaveTemplate}
            >
              {t("common.save", "Speichern")}
            </ModernButton>
          </div>
        </Form>
      </Modal>
    </Modal>
  );
};

export default ExportTemplateManager;