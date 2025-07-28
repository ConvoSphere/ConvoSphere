import React, { useState, useEffect } from "react";
import {
  Modal,
  Tabs,
  Card,
  Space,
  Typography,
  Tag,
  Button,
  Input,
  Spin,
  Alert,
  Divider,
  Tooltip,
  Badge,
} from "antd";
import {
  SearchOutlined,
  PlusOutlined,
  StarOutlined,
  EyeOutlined,
  CopyOutlined,
  SettingOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "../../store/authStore";
import { useThemeStore } from "../../store/themeStore";
import ModernCard from "../ModernCard";
import ModernButton from "../ModernButton";
import {
  assistantTemplateService,
  type AssistantTemplate,
  type TemplateCategory,
} from "../../services/assistantTemplates";

const { Title, Text, Paragraph } = Typography;
const { Search } = Input;
const { TabPane } = Tabs;

interface TemplateSelectorProps {
  visible: boolean;
  onClose: () => void;
  onSelect: (template: AssistantTemplate) => void;
  onCustomize?: (template: AssistantTemplate) => void;
}

const TemplateSelector: React.FC<TemplateSelectorProps> = ({
  visible,
  onClose,
  onSelect,
  onCustomize,
}) => {
  const { t } = useTranslation();
  const { token } = useAuthStore();
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const [templates, setTemplates] = useState<AssistantTemplate[]>([]);
  const [categories, setCategories] = useState<TemplateCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (visible && token) {
      loadTemplates();
    }
  }, [visible, token]);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      setError(null);

      const [templatesData, categoriesData] = await Promise.all([
        assistantTemplateService.getTemplates(token!),
        Promise.resolve(assistantTemplateService.getCategories()),
      ]);

      setTemplates(templatesData);
      setCategories(categoriesData);
    } catch (error) {
      console.error("Error loading templates:", error);
      setError(t("assistants.error_loading_templates"));
    } finally {
      setLoading(false);
    }
  };

  const filteredTemplates = templates.filter((template) => {
    const matchesSearch = searchQuery === "" || 
      template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesCategory = selectedCategory === "all" || template.category === selectedCategory;

    return matchesSearch && matchesCategory;
  });

  const handleTemplateSelect = (template: AssistantTemplate) => {
    onSelect(template);
    onClose();
  };

  const handleTemplateCustomize = (template: AssistantTemplate) => {
    if (onCustomize) {
      onCustomize(template);
    }
  };

  const renderTemplateCard = (template: AssistantTemplate) => {
    const category = categories.find(c => c.id === template.category);
    
    return (
      <ModernCard
        key={template.id}
        variant="interactive"
        size="md"
        style={{ 
          cursor: "pointer",
          transition: "all 0.3s ease",
          border: `1px solid ${colors.colorBorder}`,
        }}
        onClick={() => handleTemplateSelect(template)}
        header={
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: "20px" }}>{category?.icon}</span>
            <Title level={5} style={{ margin: 0, flex: 1 }}>
              {template.name}
            </Title>
            <Tag color={category?.color} style={{ margin: 0 }}>
              {category?.name}
            </Tag>
          </div>
        }
      >
        <div style={{ marginBottom: 12 }}>
          <Text type="secondary">{template.description}</Text>
        </div>

        <div style={{ marginBottom: 12 }}>
          <Text strong style={{ fontSize: "12px" }}>
            {t("assistants.personality")}:
          </Text>
          <Paragraph 
            style={{ 
              fontSize: "12px", 
              marginBottom: 8,
              color: colors.colorTextSecondary 
            }}
            ellipsis={{ rows: 2 }}
          >
            {template.personality}
          </Paragraph>
        </div>

        <div style={{ marginBottom: 12 }}>
          <Text strong style={{ fontSize: "12px" }}>
            {t("assistants.tools")}:
          </Text>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 4, marginTop: 4 }}>
            {template.tools.slice(0, 3).map((tool, index) => (
              <Tag key={index} size="small" style={{ fontSize: "10px" }}>
                {tool}
              </Tag>
            ))}
            {template.tools.length > 3 && (
              <Tag size="small" style={{ fontSize: "10px" }}>
                +{template.tools.length - 3}
              </Tag>
            )}
          </div>
        </div>

        <div style={{ marginBottom: 12 }}>
          <Text strong style={{ fontSize: "12px" }}>
            {t("assistants.examples")}:
          </Text>
          <div style={{ marginTop: 4 }}>
            {template.examples.slice(0, 1).map((example, index) => (
              <div key={index} style={{ fontSize: "11px", color: colors.colorTextSecondary }}>
                <Text strong>Q:</Text> {example.user.substring(0, 50)}...
              </div>
            ))}
          </div>
        </div>

        <Divider style={{ margin: "8px 0" }} />

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", gap: 4 }}>
            {template.tags.slice(0, 2).map((tag, index) => (
              <Tag key={index} size="small" style={{ fontSize: "10px" }}>
                {tag}
              </Tag>
            ))}
          </div>
          
          <Space>
            <Tooltip title={t("assistants.preview_template")}>
              <Button
                type="text"
                size="small"
                icon={<EyeOutlined />}
                onClick={(e) => {
                  e.stopPropagation();
                  // TODO: Implement preview
                }}
              />
            </Tooltip>
            {onCustomize && (
              <Tooltip title={t("assistants.customize_template")}>
                <Button
                  type="text"
                  size="small"
                  icon={<SettingOutlined />}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleTemplateCustomize(template);
                  }}
                />
              </Tooltip>
            )}
          </Space>
        </div>
      </ModernCard>
    );
  };

  const renderCategoryTab = (category: TemplateCategory) => {
    const categoryTemplates = filteredTemplates.filter(t => t.category === category.id);
    
    return (
      <TabPane
        tab={
          <span>
            <span style={{ marginRight: 8 }}>{category.icon}</span>
            {category.name}
            <Badge 
              count={categoryTemplates.length} 
              style={{ marginLeft: 8 }}
              size="small"
            />
          </span>
        }
        key={category.id}
      >
        <div style={{ padding: "16px 0" }}>
          {categoryTemplates.length === 0 ? (
            <div style={{ textAlign: "center", padding: "40px" }}>
              <Text type="secondary">
                {t("assistants.no_templates_in_category")}
              </Text>
            </div>
          ) : (
            <div style={{ 
              display: "grid", 
              gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
              gap: 16 
            }}>
              {categoryTemplates.map(renderTemplateCard)}
            </div>
          )}
        </div>
      </TabPane>
    );
  };

  return (
    <Modal
      title={
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <StarOutlined style={{ color: colors.colorPrimary }} />
          <Title level={4} style={{ margin: 0 }}>
            {t("assistants.select_template")}
          </Title>
        </div>
      }
      open={visible}
      onCancel={onClose}
      footer={null}
      width={1000}
      destroyOnClose
    >
      {error && (
        <Alert
          message={error}
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      <div style={{ marginBottom: 16 }}>
        <Search
          placeholder={t("assistants.search_templates")}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{ marginBottom: 16 }}
          allowClear
        />
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: "60px" }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>
            <Text type="secondary">{t("assistants.loading_templates")}</Text>
          </div>
        </div>
      ) : (
        <Tabs
          activeKey={selectedCategory}
          onChange={setSelectedCategory}
          type="card"
          style={{ marginTop: 16 }}
        >
          <TabPane
            tab={
              <span>
                📋 {t("assistants.all_templates")}
                <Badge 
                  count={filteredTemplates.length} 
                  style={{ marginLeft: 8 }}
                  size="small"
                />
              </span>
            }
            key="all"
          >
            <div style={{ padding: "16px 0" }}>
              {filteredTemplates.length === 0 ? (
                <div style={{ textAlign: "center", padding: "40px" }}>
                  <Text type="secondary">
                    {t("assistants.no_templates_found")}
                  </Text>
                </div>
              ) : (
                <div style={{ 
                  display: "grid", 
                  gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
                  gap: 16 
                }}>
                  {filteredTemplates.map(renderTemplateCard)}
                </div>
              )}
            </div>
          </TabPane>
          
          {categories.map(renderCategoryTab)}
        </Tabs>
      )}

      <div style={{ 
        display: "flex", 
        justifyContent: "flex-end", 
        gap: 12, 
        marginTop: 24,
        paddingTop: 16,
        borderTop: `1px solid ${colors.colorBorder}`
      }}>
        <ModernButton
          variant="outlined"
          onClick={onClose}
        >
          {t("common.cancel")}
        </ModernButton>
        <ModernButton
          variant="primary"
          icon={<PlusOutlined />}
          onClick={() => {
            // TODO: Implement custom template creation
            onClose();
          }}
        >
          {t("assistants.create_custom_template")}
        </ModernButton>
      </div>
    </Modal>
  );
};

export default TemplateSelector;