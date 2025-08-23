import React from "react";
import {
  Row,
  Col,
  Typography,
  Space,
  Tag,
  Badge,
  Avatar,
  Spin,
  Empty,
} from "antd";
import {
  ToolOutlined,
  ApiOutlined,
  CalculatorOutlined,
  FileTextOutlined,
  CodeOutlined,
  PlayCircleOutlined,
  SettingOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  StarOutlined,
  PlusOutlined,
  SearchOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import ModernCard from "../../components/ModernCard";
import ModernButton from "../../components/ModernButton";
import ModernInput from "../../components/ModernInput";
import { useThemeStore } from "../../store/themeStore";
import type { Tool } from "./types/tools.types";

const { Title, Text, Paragraph } = Typography;

interface ToolListProps {
  tools: Tool[];
  loading: boolean;
  searchQuery: string;
  activeTab: string;
  onSearchChange: (query: string) => void;
  onTabChange: (tab: string) => void;
  onToolClick: (tool: Tool) => void;
  onToggleActive: (tool: Tool) => void;
  onAddTool: () => void;
  isAdmin?: boolean;
}

const ToolList: React.FC<ToolListProps> = ({
  tools,
  loading,
  searchQuery,
  activeTab,
  onSearchChange,
  onTabChange,
  onToolClick,
  onToggleActive,
  onAddTool,
  isAdmin,
}) => {
  const { t } = useTranslation();
  const { colors } = useThemeStore();

  const categories = [
    {
      value: "utility",
      label: t("tools.categories.utility", "Utility"),
      icon: <ToolOutlined />,
    },
    {
      value: "api",
      label: t("tools.categories.api", "API"),
      icon: <ApiOutlined />,
    },
    {
      value: "calculation",
      label: t("tools.categories.calculation", "Calculation"),
      icon: <CalculatorOutlined />,
    },
    {
      value: "file",
      label: t("tools.categories.file", "File"),
      icon: <FileTextOutlined />,
    },
    {
      value: "code",
      label: t("tools.categories.code", "Code"),
      icon: <CodeOutlined />,
    },
  ];

  const getCategoryIcon = (category: string) => {
    const cat = categories.find((c) => c.value === category);
    return cat ? cat.icon : <ToolOutlined />;
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "utility":
        return colors.colorPrimary;
      case "api":
        return colors.colorSecondary;
      case "calculation":
        return colors.colorAccent;
      case "file":
        return "#FF6B6B";
      case "code":
        return "#4ECDC4";
      default:
        return colors.colorPrimary;
    }
  };

  const filteredTools = tools.filter((tool) => {
    const matchesSearch =
      tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tool.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = activeTab === "all" || tool.category === activeTab;
    return matchesSearch && matchesCategory;
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      {/* Search and Filters */}
      <ModernCard variant="elevated" size="md">
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} md={12}>
            <ModernInput
              placeholder={t(
                "tools.search_placeholder",
                "Tools durchsuchen...",
              )}
              prefix={
                <SearchOutlined style={{ color: colors.colorTextSecondary }} />
              }
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              allowClear
            />
          </Col>

          <Col xs={24} md={12}>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <ModernButton
                variant={activeTab === "all" ? "primary" : "outlined"}
                size="sm"
                onClick={() => onTabChange("all")}
              >
                {t("tools.categories.all", "Alle")}
              </ModernButton>
              {categories.map((category) => (
                <ModernButton
                  key={category.value}
                  variant={
                    activeTab === category.value ? "primary" : "outlined"
                  }
                  size="sm"
                  icon={category.icon}
                  onClick={() => onTabChange(category.value)}
                >
                  {category.label}
                </ModernButton>
              ))}
            </div>
          </Col>
        </Row>
      </ModernCard>

      {/* Tools Grid */}
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
              {t("tools.available_tools", "Verfügbare Tools")}
            </Title>
            <ModernButton
              variant="primary"
              size="md"
              icon={<PlusOutlined />}
              onClick={onAddTool}
            >
              {t("tools.add", "Hinzufügen")}
            </ModernButton>
          </div>
        }
      >
        {loading ? (
          <div style={{ textAlign: "center", padding: "48px" }}>
            <Spin size="large" />
          </div>
        ) : filteredTools.length === 0 ? (
          <Empty
            description={t("tools.no_tools", "Keine Tools gefunden")}
            style={{ padding: "48px 0" }}
          />
        ) : (
          <div className="modern-card-grid" style={{ gap: 16 }}>
            {filteredTools.map((tool) => (
              <ModernCard
                key={tool.id}
                variant="interactive"
                size="md"
                hoverable
                style={{ cursor: "pointer" }}
                onClick={() => onToolClick(tool)}
              >
                <div
                  style={{ display: "flex", alignItems: "flex-start", gap: 16 }}
                >
                  <Avatar
                    size={48}
                    icon={getCategoryIcon(tool.category)}
                    style={{
                      backgroundColor: getCategoryColor(tool.category),
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
                      <Title level={5} style={{ margin: 0, fontSize: "16px" }}>
                        {tool.name}
                      </Title>
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: 8,
                        }}
                      >
                        <Tag
                          color={tool.isActive ? "green" : "orange"}
                          size="small"
                        >
                          {tool.isActive
                            ? t("tools.active", "Aktiv")
                            : t("tools.inactive", "Inaktiv")}
                        </Tag>
                        <Badge count={tool.usageCount} size="small" />
                      </div>
                    </div>

                    <Paragraph
                      ellipsis={{ rows: 2 }}
                      style={{
                        margin: 0,
                        color: colors.colorTextSecondary,
                        fontSize: "14px",
                      }}
                    >
                      {tool.description}
                    </Paragraph>

                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 16,
                        marginTop: 12,
                      }}
                    >
                      <Text type="secondary" style={{ fontSize: "12px" }}>
                        <ClockCircleOutlined style={{ marginRight: 4 }} />
                        {tool.executionTime.toFixed(2)}s
                      </Text>
                      <Text type="secondary" style={{ fontSize: "12px" }}>
                        <CheckCircleOutlined style={{ marginRight: 4 }} />
                        {tool.successRate}%
                      </Text>
                      <Text type="secondary" style={{ fontSize: "12px" }}>
                        <StarOutlined style={{ marginRight: 4 }} />v
                        {tool.version}
                      </Text>
                    </div>

                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 8,
                        marginTop: 12,
                      }}
                    >
                      {tool.tags.slice(0, 3).map((tag, index) => (
                        <Tag
                          key={index}
                          size="small"
                          style={{ fontSize: "10px" }}
                        >
                          {tag}
                        </Tag>
                      ))}
                      {tool.tags.length > 3 && (
                        <Tag size="small" style={{ fontSize: "10px" }}>
                          +{tool.tags.length - 3}
                        </Tag>
                      )}
                    </div>
                  </div>

                  <div
                    style={{ display: "flex", flexDirection: "column", gap: 8 }}
                  >
                    <ModernButton
                      variant="primary"
                      size="sm"
                      icon={<PlayCircleOutlined />}
                      disabled={tool.canUse === false}
                      onClick={(e) => {
                        e.stopPropagation();
                        onToolClick(tool);
                      }}
                    />
                    {isAdmin && (
                      <ModernButton
                        variant="secondary"
                        size="sm"
                        icon={<SettingOutlined />}
                        onClick={(e) => {
                          e.stopPropagation();
                          onToggleActive(tool);
                        }}
                      />
                    )}
                  </div>
                </div>
              </ModernCard>
            ))}
          </div>
        )}
      </ModernCard>
    </div>
  );
};

export default ToolList;
