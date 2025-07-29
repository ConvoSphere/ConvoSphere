import React, { useState, useEffect, useCallback } from "react";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import { Button, Space, Typography, Modal, Select, Form, InputNumber, Switch, Alert, Input } from "antd";
import {
  PlusOutlined,
  SettingOutlined,
  SaveOutlined,
  ReloadOutlined,
  DragOutlined,
  GridOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "../../store/authStore";
import { useThemeStore } from "../../store/themeStore";
import ModernButton from "../ModernButton";
import ModernCard from "../ModernCard";
import WidgetBase, { type WidgetConfig } from "../widgets/WidgetBase";
import StatsWidget from "../widgets/StatsWidget";
import ActivityWidget from "../widgets/ActivityWidget";
import DraggableWidget from "./DraggableWidget";
import DroppableGrid from "./DroppableGrid";

const { Title, Text } = Typography;
const { Option } = Select;

interface DraggableDashboardProps {
  className?: string;
}

interface WidgetTemplate {
  type: string;
  name: string;
  description: string;
  icon: string;
  defaultSize: "small" | "medium" | "large" | "full";
  defaultSettings: Record<string, any>;
}

interface GridPosition {
  x: number;
  y: number;
  width: number;
  height: number;
}

const DraggableDashboard: React.FC<DraggableDashboardProps> = ({ className }) => {
  const { t } = useTranslation();
  const { token } = useAuthStore();
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const [widgets, setWidgets] = useState<WidgetConfig[]>([]);
  const [showAddWidget, setShowAddWidget] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [selectedWidget, setSelectedWidget] = useState<WidgetConfig | null>(null);
  const [loading, setLoading] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [gridLayout, setGridLayout] = useState<GridPosition[]>([]);

  // Widget templates
  const widgetTemplates: WidgetTemplate[] = [
    {
      type: "stats",
      name: t("widgets.stats_widget"),
      description: t("widgets.stats_widget_description"),
      icon: "📊",
      defaultSize: "medium",
      defaultSettings: {
        showConversations: true,
        showMessages: true,
        showDocuments: true,
        showAssistants: true,
        showTools: true,
        showUsers: true,
        showPerformance: true,
        refreshInterval: 30,
      },
    },
    {
      type: "activity",
      name: t("widgets.activity_widget"),
      description: t("widgets.activity_widget_description"),
      icon: "📝",
      defaultSize: "large",
      defaultSettings: {
        maxItems: 10,
        showUserInfo: true,
        showTimestamps: true,
        filterTypes: [],
        refreshInterval: 60,
      },
    },
  ];

  useEffect(() => {
    loadDashboard();
  }, [token]);

  const loadDashboard = async () => {
    if (!token) return;

    try {
      setLoading(true);
      const savedWidgets = localStorage.getItem("dashboard-widgets");
      const savedLayout = localStorage.getItem("dashboard-layout");
      
      if (savedWidgets) {
        setWidgets(JSON.parse(savedWidgets));
      } else {
        // Default widgets
        const defaultWidgets = [
          {
            id: "default-stats",
            type: "stats",
            title: t("widgets.system_stats"),
            description: t("widgets.system_stats_description"),
            size: "medium",
            position: { x: 0, y: 0 },
            settings: widgetTemplates[0].defaultSettings,
            isVisible: true,
            isCollapsed: false,
          },
          {
            id: "default-activity",
            type: "activity",
            title: t("widgets.recent_activity"),
            description: t("widgets.recent_activity_description"),
            size: "large",
            position: { x: 1, y: 0 },
            settings: widgetTemplates[1].defaultSettings,
            isVisible: true,
            isCollapsed: false,
          },
        ];
        setWidgets(defaultWidgets);
      }

      if (savedLayout) {
        setGridLayout(JSON.parse(savedLayout));
      }
    } catch (error) {
      console.error("Error loading dashboard:", error);
    } finally {
      setLoading(false);
    }
  };

  const saveDashboard = async () => {
    try {
      localStorage.setItem("dashboard-widgets", JSON.stringify(widgets));
      localStorage.setItem("dashboard-layout", JSON.stringify(gridLayout));
    } catch (error) {
      console.error("Error saving dashboard:", error);
    }
  };

  const addWidget = (template: WidgetTemplate) => {
    const newWidget: WidgetConfig = {
      id: `widget-${Date.now()}`,
      type: template.type,
      title: template.name,
      description: template.description,
      size: template.defaultSize,
      position: { x: widgets.length % 2, y: Math.floor(widgets.length / 2) },
      settings: template.defaultSettings,
      isVisible: true,
      isCollapsed: false,
    };

    setWidgets([...widgets, newWidget]);
    setShowAddWidget(false);
  };

  const updateWidget = (widgetId: string, updates: Partial<WidgetConfig>) => {
    setWidgets(prevWidgets =>
      prevWidgets.map(widget =>
        widget.id === widgetId ? { ...widget, ...updates } : widget
      )
    );
  };

  const removeWidget = (widgetId: string) => {
    setWidgets(prevWidgets => prevWidgets.filter(widget => widget.id !== widgetId));
    setGridLayout(prevLayout => prevLayout.filter(pos => pos.x !== widgetId));
  };

  const handleWidgetMove = useCallback((widgetId: string, newPosition: { x: number; y: number }) => {
    setWidgets(prevWidgets =>
      prevWidgets.map(widget =>
        widget.id === widgetId ? { ...widget, position: newPosition } : widget
      )
    );
  }, []);

  const handleWidgetResize = useCallback((widgetId: string, newSize: { width: number; height: number }) => {
    setGridLayout(prevLayout => {
      const existing = prevLayout.find(pos => pos.x === widgetId);
      if (existing) {
        return prevLayout.map(pos => 
          pos.x === widgetId ? { ...pos, width: newSize.width, height: newSize.height } : pos
        );
      } else {
        return [...prevLayout, { x: widgetId, y: 0, width: newSize.width, height: newSize.height }];
      }
    });
  }, []);

  const renderWidget = (widget: WidgetConfig) => {
    const commonProps = {
      config: widget,
      onConfigChange: (config: WidgetConfig) => updateWidget(widget.id, config),
      onRemove: removeWidget,
      onRefresh: () => console.log("Refresh widget:", widget.id),
    };

    switch (widget.type) {
      case "stats":
        return <StatsWidget {...commonProps} />;
      case "activity":
        return <ActivityWidget {...commonProps} />;
      default:
        return (
          <WidgetBase {...commonProps}>
            <div style={{ textAlign: "center", padding: "20px" }}>
              <Text type="secondary">{t("widgets.unknown_widget_type")}</Text>
            </div>
          </WidgetBase>
        );
    }
  };

  const renderAddWidgetModal = () => (
    <Modal
      title={
        <Space>
          <PlusOutlined />
          <Title level={4} style={{ margin: 0 }}>
            {t("widgets.add_widget")}
          </Title>
        </Space>
      }
      open={showAddWidget}
      onCancel={() => setShowAddWidget(false)}
      footer={null}
      width={600}
    >
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: 16 }}>
        {widgetTemplates.map((template) => (
          <ModernCard
            key={template.type}
            variant="interactive"
            size="md"
            style={{ cursor: "pointer" }}
            onClick={() => addWidget(template)}
            header={
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ fontSize: "20px" }}>{template.icon}</span>
                <Title level={5} style={{ margin: 0 }}>
                  {template.name}
                </Title>
              </div>
            }
          >
            <Text type="secondary">{template.description}</Text>
          </ModernCard>
        ))}
      </div>
    </Modal>
  );

  const renderSettingsModal = () => (
    <Modal
      title={
        <Space>
          <SettingOutlined />
          <Title level={4} style={{ margin: 0 }}>
            {t("widgets.widget_settings")}
          </Title>
        </Space>
      }
      open={showSettings && !!selectedWidget}
      onCancel={() => {
        setShowSettings(false);
        setSelectedWidget(null);
      }}
      footer={[
        <ModernButton
          key="cancel"
          variant="outlined"
          onClick={() => {
            setShowSettings(false);
            setSelectedWidget(null);
          }}
        >
          {t("common.cancel")}
        </ModernButton>,
        <ModernButton
          key="save"
          variant="primary"
          icon={<SaveOutlined />}
          onClick={() => {
            setShowSettings(false);
            setSelectedWidget(null);
          }}
        >
          {t("common.save")}
        </ModernButton>,
      ]}
      width={500}
    >
      {selectedWidget && (
        <div>
          <Form layout="vertical">
            <Form.Item label={t("widgets.title")}>
              <Input
                value={selectedWidget.title}
                onChange={(e) =>
                  setSelectedWidget({ ...selectedWidget, title: e.target.value })
                }
              />
            </Form.Item>
            <Form.Item label={t("widgets.description")}>
              <Input.TextArea
                value={selectedWidget.description}
                onChange={(e) =>
                  setSelectedWidget({ ...selectedWidget, description: e.target.value })
                }
                rows={2}
              />
            </Form.Item>
            <Form.Item label={t("widgets.size")}>
              <Select
                value={selectedWidget.size}
                onChange={(value) =>
                  setSelectedWidget({ ...selectedWidget, size: value })
                }
              >
                <Option value="small">{t("widgets.size_small")}</Option>
                <Option value="medium">{t("widgets.size_medium")}</Option>
                <Option value="large">{t("widgets.size_large")}</Option>
                <Option value="full">{t("widgets.size_full")}</Option>
              </Select>
            </Form.Item>
            <Form.Item label={t("widgets.refresh_interval")}>
              <InputNumber
                value={selectedWidget.settings.refreshInterval}
                onChange={(value) =>
                  setSelectedWidget({
                    ...selectedWidget,
                    settings: { ...selectedWidget.settings, refreshInterval: value || 0 },
                  })
                }
                min={0}
                max={3600}
                addonAfter={t("widgets.seconds")}
              />
            </Form.Item>
          </Form>
        </div>
      )}
    </Modal>
  );

  return (
    <DndProvider backend={HTML5Backend}>
      <div className={`draggable-dashboard ${className || ""}`}>
        {/* Dashboard Header */}
        <ModernCard
          variant="outlined"
          size="md"
          style={{ marginBottom: 24 }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div>
              <Title level={3} style={{ margin: 0 }}>
                {t("dashboard.title")}
              </Title>
              <Text type="secondary">{t("dashboard.subtitle")}</Text>
            </div>
            <Space>
              <ModernButton
                variant={editMode ? "primary" : "outlined"}
                icon={<DragOutlined />}
                onClick={() => setEditMode(!editMode)}
              >
                {editMode ? t("dashboard.exit_edit_mode") : t("dashboard.edit_mode")}
              </ModernButton>
              <ModernButton
                variant="outlined"
                icon={<ReloadOutlined />}
                onClick={loadDashboard}
                loading={loading}
              >
                {t("dashboard.refresh")}
              </ModernButton>
              <ModernButton
                variant="outlined"
                icon={<SettingOutlined />}
                onClick={() => setShowSettings(true)}
              >
                {t("dashboard.settings")}
              </ModernButton>
              <ModernButton
                variant="primary"
                icon={<PlusOutlined />}
                onClick={() => setShowAddWidget(true)}
              >
                {t("widgets.add_widget")}
              </ModernButton>
            </Space>
          </div>
        </ModernCard>

        {/* Edit Mode Alert */}
        {editMode && (
          <Alert
            message={t("dashboard.edit_mode_active")}
            description={t("dashboard.edit_mode_description")}
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
            closable
          />
        )}

        {/* Draggable Widget Grid */}
        <DroppableGrid
          widgets={widgets}
          onWidgetMove={handleWidgetMove}
          onWidgetResize={handleWidgetResize}
          editMode={editMode}
          renderWidget={renderWidget}
        />

        {/* Empty State */}
        {widgets.length === 0 && !loading && (
          <ModernCard
            variant="outlined"
            size="lg"
            style={{ textAlign: "center", padding: "60px" }}
          >
            <div style={{ marginBottom: 24 }}>
              <Title level={4} style={{ color: colors.colorTextSecondary }}>
                {t("dashboard.no_widgets")}
              </Title>
              <Text type="secondary">{t("dashboard.no_widgets_description")}</Text>
            </div>
            <ModernButton
              variant="primary"
              icon={<PlusOutlined />}
              onClick={() => setShowAddWidget(true)}
            >
              {t("widgets.add_first_widget")}
            </ModernButton>
          </ModernCard>
        )}

        {renderAddWidgetModal()}
        {renderSettingsModal()}
      </div>
    </DndProvider>
  );
};

export default DraggableDashboard;