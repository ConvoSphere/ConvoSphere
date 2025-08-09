import React from 'react';
import { Typography, Space, Statistic, Divider, Badge } from 'antd';
import {
  ToolOutlined,
  ThunderboltOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  PlusOutlined,
  UploadOutlined,
  DownloadOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import ModernCard from '../../components/ModernCard';
import ModernButton from '../../components/ModernButton';
import { useThemeStore } from '../../store/themeStore';
import type { Tool } from './types/tools.types';

const { Title, Text } = Typography;

interface ToolStatsProps {
  tools: Tool[];
  totalExecutions: number;
  successRate: string;
  onAddTool: () => void;
  onImportTools: () => void;
  onExportTools: () => void;
  onRefresh: () => void;
  onCategoryClick: (category: string) => void;
}

const ToolStats: React.FC<ToolStatsProps> = ({
  tools,
  totalExecutions,
  successRate,
  onAddTool,
  onImportTools,
  onExportTools,
  onRefresh,
  onCategoryClick,
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
      icon: <ThunderboltOutlined />,
    },
    {
      value: "calculation",
      label: t("tools.categories.calculation", "Calculation"),
      icon: <PlayCircleOutlined />,
    },
    {
      value: "file",
      label: t("tools.categories.file", "File"),
      icon: <UploadOutlined />,
    },
    {
      value: "code",
      label: t("tools.categories.code", "Code"),
      icon: <ToolOutlined />,
    },
  ];

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

  const stats = {
    total: tools.length,
    active: tools.filter((t) => t.isActive).length,
    totalExecutions,
    successRate,
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      {/* Statistics */}
      <ModernCard variant="interactive" size="md">
        <Title level={4} style={{ marginBottom: 24 }}>
          {t("tools.statistics", "Statistiken")}
        </Title>

        <Space direction="vertical" size="large" style={{ width: "100%" }}>
          <Statistic
            title={t("tools.stats.total_tools", "Gesamt Tools")}
            value={stats.total}
            prefix={<ToolOutlined style={{ color: colors.colorPrimary }} />}
            valueStyle={{
              color: colors.colorPrimary,
              fontSize: "1.5rem",
            }}
          />

          <Divider style={{ margin: "16px 0" }} />

          <Statistic
            title={t("tools.stats.active_tools", "Aktive Tools")}
            value={stats.active}
            prefix={<ThunderboltOutlined style={{ color: colors.colorSecondary }} />}
            valueStyle={{
              color: colors.colorSecondary,
              fontSize: "1.2rem",
            }}
          />

          <Statistic
            title={t("tools.stats.total_executions", "Ausführungen")}
            value={stats.totalExecutions}
            prefix={<PlayCircleOutlined style={{ color: colors.colorAccent }} />}
            valueStyle={{
              color: colors.colorAccent,
              fontSize: "1.2rem",
            }}
          />

          <Statistic
            title={t("tools.stats.success_rate", "Erfolgsrate")}
            value={stats.successRate}
            suffix="%"
            prefix={<CheckCircleOutlined style={{ color: "#52C41A" }} />}
            valueStyle={{ color: "#52C41A", fontSize: "1.2rem" }}
          />
        </Space>
      </ModernCard>

      {/* Quick Actions */}
      <ModernCard variant="outlined" size="md">
        <Title level={4} style={{ marginBottom: 16 }}>
          {t("tools.quick_actions", "Schnellaktionen")}
        </Title>

        <Space direction="vertical" size="small" style={{ width: "100%" }}>
          <ModernButton
            variant="primary"
            size="md"
            icon={<PlusOutlined />}
            onClick={onAddTool}
            style={{ width: "100%", justifyContent: "flex-start" }}
          >
            {t("tools.add_new_tool", "Neues Tool hinzufügen")}
          </ModernButton>

          <ModernButton
            variant="secondary"
            size="md"
            icon={<UploadOutlined />}
            onClick={onImportTools}
            style={{ width: "100%", justifyContent: "flex-start" }}
          >
            {t("tools.import_tools", "Tools importieren")}
          </ModernButton>

          <ModernButton
            variant="secondary"
            size="md"
            icon={<DownloadOutlined />}
            onClick={onExportTools}
            style={{ width: "100%", justifyContent: "flex-start" }}
          >
            {t("tools.export_tools", "Tools exportieren")}
          </ModernButton>

          <ModernButton
            variant="secondary"
            size="md"
            icon={<ReloadOutlined />}
            onClick={onRefresh}
            style={{ width: "100%", justifyContent: "flex-start" }}
          >
            {t("tools.refresh", "Aktualisieren")}
          </ModernButton>
        </Space>
      </ModernCard>

      {/* Category Overview */}
      <ModernCard variant="outlined" size="md">
        <Title level={4} style={{ marginBottom: 16 }}>
          {t("tools.categories", "Kategorien")}
        </Title>

        <Space direction="vertical" size="small" style={{ width: "100%" }}>
          {categories.map((category) => {
            const count = tools.filter((t) => t.category === category.value).length;
            return (
              <div
                key={category.value}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "12px",
                  backgroundColor: colors.colorBgContainer,
                  borderRadius: "8px",
                  cursor: "pointer",
                }}
                onClick={() => onCategoryClick(category.value)}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{ color: getCategoryColor(category.value) }}>
                    {category.icon}
                  </span>
                  <Text>{category.label}</Text>
                </div>
                <Badge count={count} size="small" />
              </div>
            );
          })}
        </Space>
      </ModernCard>
    </div>
  );
};

export default ToolStats;