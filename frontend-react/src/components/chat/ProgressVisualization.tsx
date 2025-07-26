import React, { useState, useEffect } from "react";
import { Progress, Card, Space, Typography, Tag, Spin } from "antd";
import {
  LoadingOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ClockCircleOutlined,
  ToolOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";

const { Text, Title } = Typography;

interface ProgressStep {
  id: string;
  name: string;
  status: "pending" | "processing" | "completed" | "failed";
  progress: number;
  startTime?: string;
  endTime?: string;
  error?: string;
  details?: string;
}

interface ProgressVisualizationProps {
  steps: ProgressStep[];
  currentStep?: string;
  overallProgress: number;
  status: "idle" | "processing" | "completed" | "failed";
  mode: "chat" | "agent" | "auto";
  onStepClick?: (stepId: string) => void;
  className?: string;
}

const ProgressVisualization: React.FC<ProgressVisualizationProps> = ({
  steps,
  currentStep,
  overallProgress,
  status,
  mode,
  onStepClick,
  className = "",
}) => {
  const { t } = useTranslation();
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "success";
      case "processing":
        return "processing";
      case "failed":
        return "error";
      default:
        return "default";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircleOutlined />;
      case "processing":
        return <LoadingOutlined />;
      case "failed":
        return <ExclamationCircleOutlined />;
      default:
        return <ClockCircleOutlined />;
    }
  };

  const getModeColor = (mode: string) => {
    switch (mode) {
      case "chat":
        return "blue";
      case "agent":
        return "green";
      case "auto":
        return "purple";
      default:
        return "default";
    }
  };

  const getModeIcon = (mode: string) => {
    switch (mode) {
      case "chat":
        return "💬";
      case "agent":
        return "🤖";
      case "auto":
        return "⚡";
      default:
        return "💬";
    }
  };

  const formatDuration = (startTime?: string, endTime?: string) => {
    if (!startTime) return "";

    const start = new Date(startTime);
    const end = endTime ? new Date(endTime) : currentTime;
    const duration = Math.round((end.getTime() - start.getTime()) / 1000);

    if (duration < 60) return `${duration}s`;
    if (duration < 3600)
      return `${Math.floor(duration / 60)}m ${duration % 60}s`;
    return `${Math.floor(duration / 3600)}h ${Math.floor((duration % 3600) / 60)}m`;
  };

  const isStepActive = (step: ProgressStep) => {
    return step.id === currentStep || step.status === "processing";
  };

  return (
    <div className={`progress-visualization ${className}`}>
      {/* Header */}
      <div className="progress-header">
        <Space align="center">
          <span className="mode-icon">{getModeIcon(mode)}</span>
          <Title level={5} style={{ margin: 0 }}>
            {t("chat.progress.title")}
          </Title>
          <Tag color={getModeColor(mode)}>{mode.toUpperCase()} MODE</Tag>
          <Tag color={getStatusColor(status)}>{status.toUpperCase()}</Tag>
        </Space>
      </div>

      {/* Overall Progress */}
      <Card size="small" className="overall-progress-card">
        <div className="overall-progress">
          <Space direction="vertical" size="small" style={{ width: "100%" }}>
            <div className="progress-header-row">
              <Text strong>{t("chat.progress.overall")}</Text>
              <Text type="secondary">{Math.round(overallProgress)}%</Text>
            </div>

            <Progress
              percent={overallProgress}
              status={
                status === "failed"
                  ? "exception"
                  : status === "completed"
                    ? "success"
                    : "active"
              }
              strokeColor={getModeColor(mode)}
              showInfo={false}
            />

            <div className="progress-stats">
              <Space>
                <Text type="secondary">
                  {steps.filter((s) => s.status === "completed").length} /{" "}
                  {steps.length} {t("chat.progress.completed")}
                </Text>
                {currentStep && (
                  <Text type="secondary">
                    {t("chat.progress.current")}:{" "}
                    {steps.find((s) => s.id === currentStep)?.name}
                  </Text>
                )}
              </Space>
            </div>
          </Space>
        </div>
      </Card>

      {/* Individual Steps */}
      <div className="progress-steps">
        {steps.map((step, index) => (
          <Card
            key={step.id}
            size="small"
            className={`progress-step-card ${isStepActive(step) ? "active" : ""}`}
            onClick={() => onStepClick?.(step.id)}
            style={{ cursor: onStepClick ? "pointer" : "default" }}
          >
            <div className="progress-step">
              <div className="step-header">
                <Space>
                  {getStatusIcon(step.status)}
                  <Text strong>{step.name}</Text>
                  <Tag color={getStatusColor(step.status)}>
                    {step.status.toUpperCase()}
                  </Tag>
                </Space>
              </div>

              <div className="step-progress">
                <Progress
                  percent={step.progress}
                  size="small"
                  status={
                    step.status === "failed"
                      ? "exception"
                      : step.status === "completed"
                        ? "success"
                        : "active"
                  }
                  showInfo={false}
                />
              </div>

              <div className="step-details">
                <Space>
                  {step.startTime && (
                    <Text type="secondary" style={{ fontSize: "12px" }}>
                      {formatDuration(step.startTime, step.endTime)}
                    </Text>
                  )}

                  {step.status === "processing" && <Spin size="small" />}

                  {step.error && (
                    <Text type="danger" style={{ fontSize: "12px" }}>
                      {step.error}
                    </Text>
                  )}
                </Space>
              </div>

              {step.details && (
                <div className="step-details-text">
                  <Text type="secondary" style={{ fontSize: "12px" }}>
                    {step.details}
                  </Text>
                </div>
              )}
            </div>
          </Card>
        ))}
      </div>

      {/* Tool Usage Indicator */}
      {mode === "agent" && (
        <div className="tool-usage-indicator">
          <Space>
            <ToolOutlined />
            <Text type="secondary">{t("chat.progress.toolUsage")}</Text>
            <Tag color="green">
              {steps.filter((s) => s.status === "completed").length}{" "}
              {t("chat.progress.toolsUsed")}
            </Tag>
          </Space>
        </div>
      )}
    </div>
  );
};

export default ProgressVisualization;
