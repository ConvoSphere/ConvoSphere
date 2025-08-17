import React, { useState, useEffect, useCallback } from "react";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import {
  Space,
  Typography,
  Modal,
  Select,
  Form,
  InputNumber,
  Switch,
  Alert,
  Input,
} from "antd";
import ModernButton from "../ModernButton";
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
import ModernCard from "../ModernCard";
import WidgetBase, { type WidgetConfig } from "../widgets/WidgetBase";
import { WIDGET_REGISTRY, type WidgetType } from "../widgets/registry";
import DraggableWidget from "./DraggableWidget";
import DroppableGrid from "./DroppableGrid";
import { dashboardService, type GridPosition as PersistedGridPosition } from "../../services/dashboard";

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
  id: string; // widget id
  x: number;
  y: number;
  width: number;
  height: number;
}

const DraggableDashboard: React.FC<DraggableDashboardProps> = ({
  className,
}) => {
  const { t } = useTranslation();
  const { token } = useAuthStore();
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const [widgets, setWidgets] = useState<WidgetConfig[]>([]);
  const [showAddWidget, setShowAddWidget] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [selectedWidget, setSelectedWidget] = useState<WidgetConfig | null>(
    null,
  );
  const [loading, setLoading] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [gridLayout, setGridLayout] = useState<GridPosition[]>([]);

  // Widget templates
  const widgetTemplates: WidgetTemplate[] = (Object.values(WIDGET_REGISTRY) as any).map((meta: any) => ({
    type: meta.type,
    name: t(meta.i18nTitleKey),
    description: t(meta.i18nDescriptionKey),
    icon: meta.icon,
    defaultSize: meta.defaultSize,
    defaultSettings: meta.defaultSettings,
  }));

  useEffect(() => {
    loadDashboard();
  }, [token]);

  const loadDashboard = async () => {
    if (!token) return;

    try {
      setLoading(true);
      // Try server first
      try {
        const serverState = await dashboardService.getMyDashboard();
        setWidgets(serverState.widgets || []);
        setGridLayout((serverState.layout || []) as any);
      } catch (e) {
        const savedWidgets = localStorage.getItem("dashboard-widgets");
        const savedLayout = localStorage.getItem("dashboard-layout");
        if (savedWidgets) {
          setWidgets(JSON.parse(savedWidgets));
        } else {
          const defaultWidgets = [
            {
              id: "default-stats",
              type: "stats",
              title: t("widgets.system_stats"),
              description: t("widgets.system_stats_description"),
              size: WIDGET_REGISTRY.stats.defaultSize,
              position: { x: 0, y: 0 },
              settings: WIDGET_REGISTRY.stats.defaultSettings,
              isVisible: true,
              isCollapsed: false,
            },
            {
              id: "default-activity",
              type: "activity",
              title: t("widgets.recent_activity"),
              description: t("widgets.recent_activity_description"),
              size: WIDGET_REGISTRY.activity.defaultSize,
              position: { x: 1, y: 0 },
              settings: WIDGET_REGISTRY.activity.defaultSettings,
              isVisible: true,
              isCollapsed: false,
            },
            {
              id: "default-system-metrics",
              type: "systemMetrics",
              title: t("monitoring.system_metrics"),
              description: t("monitoring.system_metrics_description"),
              size: WIDGET_REGISTRY.systemMetrics.defaultSize,
              position: { x: 0, y: 1 },
              settings: WIDGET_REGISTRY.systemMetrics.defaultSettings,
              isVisible: true,
              isCollapsed: false,
            },
          ];
          setWidgets(defaultWidgets);
        }
        if (savedLayout) {
          setGridLayout(JSON.parse(savedLayout));
        } else {
          // initialize layout from widgets if none present
          setGridLayout(
            (savedWidgets ? JSON.parse(savedWidgets) : []).map((w: any, idx: number) => ({
              id: w.id,
              x: (idx % 12) + 1,
              y: Math.floor(idx / 12) * 6 + 1,
              width: 6,
              height: 6,
            })),
          );
        }
      }
    } catch (error) {
      console.error("Error loading dashboard:", error);
    } finally {
      setLoading(false);
    }
  };

  const saveDashboard = async () => {
    try {
      const state = { widgets, layout: gridLayout as PersistedGridPosition[] };
      await dashboardService.saveMyDashboard(state);
      localStorage.setItem("dashboard-widgets", JSON.stringify(widgets));
      localStorage.setItem("dashboard-layout", JSON.stringify(gridLayout));
    } catch (error) {
      console.error("Error saving dashboard:", error);
    }
  }; // TODO: replace with server-side persistence via dashboardService

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
    setGridLayout((prev) => [
      ...prev,
      { id: newWidget.id, x: newWidget.position.x, y: newWidget.position.y, width: 1, height: 1 },
    ]);
    setShowAddWidget(false);
    // persist
    setTimeout(saveDashboard, 0);
  };

  const updateWidget = (widgetId: string, updates: Partial<WidgetConfig>) => {
    setWidgets((prevWidgets) =>
      prevWidgets.map((widget) =>
        widget.id === widgetId ? { ...widget, ...updates } : widget,
      ),
    );
    // persist
    setTimeout(saveDashboard, 0);
  };

  const removeWidget = (widgetId: string) => {
    setWidgets((prevWidgets) =>
      prevWidgets.filter((widget) => widget.id !== widgetId),
    );
    setGridLayout((prevLayout) =>
      prevLayout.filter((pos) => pos.id !== widgetId),
    );
    // persist
    setTimeout(saveDashboard, 0);
  };

  const handleWidgetMove = useCallback(
    (widgetId: string, newPosition: { x: number; y: number }) => {
      setWidgets((prevWidgets) =>
        prevWidgets.map((widget) =>
          widget.id === widgetId
            ? { ...widget, position: newPosition }
            : widget,
        ),
      );
      // persist
      setTimeout(saveDashboard, 0);
    },
    [],
  );

  const handleWidgetResize = useCallback(
    (widgetId: string, newSize: { width: number; height: number }) => {
      setGridLayout((prevLayout) => {
        const existing = prevLayout.find((pos) => pos.id === widgetId);
        if (existing) {
          return prevLayout.map((pos) =>
            pos.id === widgetId
              ? { ...pos, width: newSize.width, height: newSize.height }
              : pos,
          );
        } else {
          return [
            ...prevLayout,
            { id: widgetId, x: 0, y: 0, width: newSize.width, height: newSize.height },
          ];
        }
      });
      // persist
      setTimeout(saveDashboard, 0);
    },
    [],
  );

  const openWidgetSettings = (widget: WidgetConfig) => {
    setSelectedWidget(widget);
    setShowSettings(true);
  };

  const renderWidget = (widget: WidgetConfig) => {
    const commonProps = {
      config: widget,
      onConfigChange: (config: WidgetConfig) => updateWidget(widget.id, config),
      onRemove: removeWidget,
      onRefresh: () => console.log("Refresh widget:", widget.id),
    };

    const meta = WIDGET_REGISTRY[widget.type as WidgetType];
    if (meta) {
      const Component = meta.component as any;
      return <Component {...commonProps} />;
    }

    return (
      <WidgetBase {...commonProps}>
        <div style={{ textAlign: "center", padding: "20px" }}>
          <Text type="secondary">{t("widgets.unknown_widget_type")}</Text>
        </div>
      </WidgetBase>
    );
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
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
          gap: 16,
        }}
      >
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
            if (selectedWidget) {
              updateWidget(selectedWidget.id, selectedWidget);
              setTimeout(saveDashboard, 0);
            }
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
                  setSelectedWidget({
                    ...selectedWidget,
                    title: e.target.value,
                  })
                }
              />
            </Form.Item>
            <Form.Item label={t("widgets.description")}>
              <Input.TextArea
                value={selectedWidget.description}
                onChange={(e) =>
                  setSelectedWidget({
                    ...selectedWidget,
                    description: e.target.value,
                  })
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
                    settings: {
                      ...selectedWidget.settings,
                      refreshInterval: value || 0,
                    },
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
        <ModernCard variant="outlined" size="md" style={{ marginBottom: 24 }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
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
                {editMode
                  ? t("dashboard.exit_edit_mode")
                  : t("dashboard.edit_mode")}
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
          layout={gridLayout}
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
              <Text type="secondary">
                {t("dashboard.no_widgets_description")}
              </Text>
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
