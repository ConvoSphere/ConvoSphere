import React from "react";
import { Row, Col, Typography } from "antd";
import { LineChartOutlined } from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
} from "recharts";
import ModernCard from "../../components/ModernCard";
import ModernSelect from "../../components/ModernSelect";
import { Select } from "antd";

const { Title, Text } = Typography;

interface PerformanceData {
  timestamp: string;
  responseTime: number;
  throughput: number;
  errorRate: number;
}

interface PerformanceMetricsProps {
  performanceData: PerformanceData[];
  timeRange: string;
  onTimeRangeChange: (range: string) => void;
  loading?: boolean;
}

const PerformanceMetrics: React.FC<PerformanceMetricsProps> = ({
  performanceData,
  timeRange,
  onTimeRangeChange,
  loading = false,
}) => {
  const { t } = useTranslation();

  return (
    <ModernCard>
      <Row gutter={[16, 16]} style={{ marginBottom: "16px" }}>
        <Col xs={24} sm={12} md={6}>
          <ModernSelect
            value={timeRange}
            onChange={onTimeRangeChange}
            style={{ width: "100%" }}
          >
            <Select.Option value="1h">
              {t("monitoring.last_hour")}
            </Select.Option>
            <Select.Option value="6h">
              {t("monitoring.last_6_hours")}
            </Select.Option>
            <Select.Option value="24h">
              {t("monitoring.last_24_hours")}
            </Select.Option>
            <Select.Option value="7d">
              {t("monitoring.last_7_days")}
            </Select.Option>
          </ModernSelect>
        </Col>
      </Row>

      {performanceData.length > 0 ? (
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={performanceData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="timestamp"
              tickFormatter={(value) => new Date(value).toLocaleTimeString()}
            />
            <YAxis />
            <RechartsTooltip
              labelFormatter={(value) => new Date(value).toLocaleString()}
            />
            <Line
              type="monotone"
              dataKey="responseTime"
              stroke="#1890ff"
              name={t("monitoring.response_time")}
            />
            <Line
              type="monotone"
              dataKey="throughput"
              stroke="#52c41a"
              name={t("monitoring.throughput")}
            />
            <Line
              type="monotone"
              dataKey="errorRate"
              stroke="#ff4d4f"
              name={t("monitoring.error_rate")}
            />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <div style={{ textAlign: "center", padding: "40px" }}>
          <Text type="secondary">{t("monitoring.no_performance_data")}</Text>
        </div>
      )}
    </ModernCard>
  );
};

export default PerformanceMetrics;
