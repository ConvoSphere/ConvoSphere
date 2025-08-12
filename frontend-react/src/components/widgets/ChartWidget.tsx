import React, { useState, useEffect, useRef } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
} from "chart.js";
import { Line, Bar, Doughnut, Radar } from "react-chartjs-2";
import { Select, Space, Typography } from "antd";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "../../store/authStore";
import { useThemeStore } from "../../store/themeStore";
import WidgetBase, { type WidgetConfig, type WidgetProps } from "./WidgetBase";
import { statisticsService } from "../../services/statistics";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
);

const { Title: AntTitle, Text } = Typography;
const { Option } = Select;

interface ChartWidgetProps extends Omit<WidgetProps, "children"> {
  config: WidgetConfig & {
    settings: {
      chartType: "line" | "bar" | "doughnut" | "radar";
      dataSource: "conversations" | "messages" | "users" | "performance";
      timeRange: "24h" | "7d" | "30d" | "90d";
      showLegend: boolean;
      showGrid: boolean;
      refreshInterval: number;
    };
  };
}

const ChartWidget: React.FC<ChartWidgetProps> = ({
  config,
  onConfigChange,
  onRemove,
  onRefresh,
  loading = false,
  error = null,
}) => {
  const { t } = useTranslation();
  const { token } = useAuthStore();
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const [chartData, setChartData] = useState<any>(null);
  const [localLoading, setLocalLoading] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  useEffect(() => {
    if (token) {
      loadChartData();
    }
  }, [token, config.settings.dataSource, config.settings.timeRange]);

  useEffect(() => {
    if (
      config.settings.refreshInterval &&
      config.settings.refreshInterval > 0
    ) {
      const interval = setInterval(
        loadChartData,
        config.settings.refreshInterval * 1000,
      );
      return () => clearInterval(interval);
    }
  }, [config.settings.refreshInterval]);

  const loadChartData = async () => {
    if (!token) return;

    try {
      setLocalLoading(true);
      setLocalError(null);

      // Simulate API call for chart data
      await new Promise((resolve) => setTimeout(resolve, 1000));

      const data = generateChartData();
      setChartData(data);
    } catch (error) {
      console.error("Error loading chart data:", error);
      setLocalError(t("widgets.error_loading_chart_data"));
    } finally {
      setLocalLoading(false);
    }
  };

  const generateChartData = () => {
    const labels = generateLabels();
    const datasets = generateDatasets(labels);

    return {
      labels,
      datasets,
    };
  };

  const generateLabels = () => {
    const { timeRange } = config.settings;
    const now = new Date();
    const labels = [];

    switch (timeRange) {
      case "24h":
        for (let i = 23; i >= 0; i--) {
          const time = new Date(now.getTime() - i * 60 * 60 * 1000);
          labels.push(
            time.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          );
        }
        break;
      case "7d":
        for (let i = 6; i >= 0; i--) {
          const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
          labels.push(date.toLocaleDateString([], { weekday: "short" }));
        }
        break;
      case "30d":
        for (let i = 29; i >= 0; i--) {
          const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
          labels.push(date.getDate().toString());
        }
        break;
      case "90d":
        for (let i = 89; i >= 0; i -= 3) {
          const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
          labels.push(
            date.toLocaleDateString([], { month: "short", day: "numeric" }),
          );
        }
        break;
    }

    return labels;
  };

  const generateDatasets = (labels: string[]) => {
    const { dataSource } = config.settings;
    const baseValue = getBaseValue(dataSource);
    const variance = getVariance(dataSource);

    const data = labels.map(() =>
      Math.max(0, baseValue + (Math.random() - 0.5) * variance),
    );

    return [
      {
        label: t(`widgets.chart.${dataSource}`),
        data,
        borderColor: colors.colorPrimary,
        backgroundColor: `${colors.colorPrimary}20`,
        tension: 0.4,
        fill: config.settings.chartType === "line",
      },
    ];
  };

  const getBaseValue = (dataSource: string) => {
    switch (dataSource) {
      case "conversations":
        return 50;
      case "messages":
        return 200;
      case "users":
        return 25;
      case "performance":
        return 85;
      default:
        return 100;
    }
  };

  const getVariance = (dataSource: string) => {
    switch (dataSource) {
      case "conversations":
        return 30;
      case "messages":
        return 100;
      case "users":
        return 10;
      case "performance":
        return 15;
      default:
        return 50;
    }
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: config.settings.showLegend,
        position: "top" as const,
      },
      title: {
        display: false,
      },
    },
    scales:
      config.settings.chartType !== "doughnut" &&
      config.settings.chartType !== "radar"
        ? {
            x: {
              display: true,
              grid: {
                display: config.settings.showGrid,
                color: colors.colorBorder,
              },
              ticks: {
                color: colors.colorTextSecondary,
              },
            },
            y: {
              display: true,
              grid: {
                display: config.settings.showGrid,
                color: colors.colorBorder,
              },
              ticks: {
                color: colors.colorTextSecondary,
              },
            },
          }
        : undefined,
  };

  const handleChartTypeChange = (chartType: string) => {
    onConfigChange({
      ...config,
      settings: {
        ...config.settings,
        chartType: chartType as any,
      },
    });
  };

  const handleDataSourceChange = (dataSource: string) => {
    onConfigChange({
      ...config,
      settings: {
        ...config.settings,
        dataSource: dataSource as any,
      },
    });
  };

  const handleTimeRangeChange = (timeRange: string) => {
    onConfigChange({
      ...config,
      settings: {
        ...config.settings,
        timeRange: timeRange as any,
      },
    });
  };

  const renderChart = () => {
    if (!chartData) return null;

    const chartProps = {
      data: chartData,
      options: chartOptions,
    };

    switch (config.settings.chartType) {
      case "line":
        return <Line {...chartProps} />;
      case "bar":
        return <Bar {...chartProps} />;
      case "doughnut":
        return <Doughnut {...chartProps} />;
      case "radar":
        return <Radar {...chartProps} />;
      default:
        return <Line {...chartProps} />;
    }
  };

  const renderControls = () => (
    <div style={{ marginBottom: 16 }}>
      <Space wrap>
        <Select
          value={config.settings.chartType}
          onChange={handleChartTypeChange}
          style={{ width: 120 }}
          size="small"
        >
          <Option value="line">{t("widgets.chart.line")}</Option>
          <Option value="bar">{t("widgets.chart.bar")}</Option>
          <Option value="doughnut">{t("widgets.chart.doughnut")}</Option>
          <Option value="radar">{t("widgets.chart.radar")}</Option>
        </Select>

        <Select
          value={config.settings.dataSource}
          onChange={handleDataSourceChange}
          style={{ width: 140 }}
          size="small"
        >
          <Option value="conversations">
            {t("widgets.chart.conversations")}
          </Option>
          <Option value="messages">{t("widgets.chart.messages")}</Option>
          <Option value="users">{t("widgets.chart.users")}</Option>
          <Option value="performance">{t("widgets.chart.performance")}</Option>
        </Select>

        <Select
          value={config.settings.timeRange}
          onChange={handleTimeRangeChange}
          style={{ width: 100 }}
          size="small"
        >
          <Option value="24h">{t("widgets.chart.24h")}</Option>
          <Option value="7d">{t("widgets.chart.7d")}</Option>
          <Option value="30d">{t("widgets.chart.30d")}</Option>
          <Option value="90d">{t("widgets.chart.90d")}</Option>
        </Select>
      </Space>
    </div>
  );

  const renderContent = () => {
    if (localError) {
      return (
        <div style={{ textAlign: "center", padding: "20px" }}>
          <Text type="danger">{localError}</Text>
        </div>
      );
    }

    return (
      <div>
        {renderControls()}
        <div style={{ height: "300px", position: "relative" }}>
          {renderChart()}
        </div>
      </div>
    );
  };

  return (
    <WidgetBase
      config={config}
      onConfigChange={onConfigChange}
      onRemove={onRemove}
      onRefresh={loadChartData}
      loading={loading || localLoading}
      error={error || localError}
    >
      {renderContent()}
    </WidgetBase>
  );
};

export default ChartWidget;
