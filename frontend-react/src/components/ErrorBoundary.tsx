import React, { Component } from "react";
import type { ErrorInfo, ReactNode } from "react";
import { Result, Card, Typography, Space } from "antd";
import ModernButton from "./ModernButton";
import { ReloadOutlined, HomeOutlined, BugOutlined } from "@ant-design/icons";
import { useThemeStore } from "../store/themeStore";

const { Text, Paragraph } = Typography;

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  resetKey?: string | number;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string;
}

class ErrorBoundaryClass extends Component<Props & { colors: any }, State> {
  constructor(props: Props & { colors: any }) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: "",
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error,
      errorId: `error-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ errorInfo });

    // Log error to console in development
    if (process.env.NODE_ENV === "development") {
      console.error("ErrorBoundary caught an error:", error, errorInfo);
    }

    // Call custom error handler
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Send error to monitoring service (e.g., Sentry)
    this.logErrorToService(error, errorInfo);
  }

  componentDidUpdate(prevProps: Props & { colors: any }) {
    // Reset error state when resetKey changes
    if (prevProps.resetKey !== this.props.resetKey && this.state.hasError) {
      this.setState({
        hasError: false,
        error: null,
        errorInfo: null,
        errorId: "",
      });
    }
  }

  logErrorToService = (error: Error, errorInfo: ErrorInfo) => {
    // In a real app, you would send this to your error monitoring service
    // Example: Sentry.captureException(error, { extra: errorInfo });

    const errorData = {
      errorId: this.state.errorId,
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
    };

    // Store error in localStorage for debugging
    try {
      const existingErrors = JSON.parse(
        localStorage.getItem("app-errors") || "[]",
      );
      existingErrors.push(errorData);
      localStorage.setItem(
        "app-errors",
        JSON.stringify(existingErrors.slice(-10)),
      ); // Keep last 10 errors
    } catch (e) {
      console.warn("Could not save error to localStorage:", e);
    }
  };

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: "",
    });
  };

  handleGoHome = () => {
    window.location.href = "/";
  };

  handleReportBug = () => {
    const { error, errorInfo, errorId } = this.state;
    const errorReport = {
      errorId,
      message: error?.message,
      stack: error?.stack,
      componentStack: errorInfo?.componentStack,
      url: window.location.href,
      userAgent: navigator.userAgent,
    };

    // In a real app, you would send this to your bug reporting system
    console.log("Bug Report:", errorReport);

    // For now, just copy to clipboard
    navigator.clipboard
      .writeText(JSON.stringify(errorReport, null, 2))
      .then(() => alert("Error report copied to clipboard"))
      .catch(() => alert("Could not copy error report"));
  };

  render() {
    const { colors } = this.props;

    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <div
          style={{
            minHeight: "100vh",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            backgroundColor: colors.colorBgBase,
            padding: "20px",
          }}
        >
          <Card
            style={{
              maxWidth: "600px",
              width: "100%",
              backgroundColor: colors.colorBgContainer,
              border: `1px solid ${colors.colorBorder}`,
              boxShadow: colors.boxShadow,
            }}
          >
            <Result
              status="error"
              icon={<BugOutlined style={{ color: colors.colorError }} />}
              title="Something went wrong"
              subTitle="We're sorry, but something unexpected happened. Please try again."
              extra={
                <Space
                  direction="vertical"
                  size="middle"
                  style={{ width: "100%" }}
                >
                  <Space>
                    <ModernButton
                      variant="primary"
                      icon={<ReloadOutlined />}
                      onClick={this.handleReset}
                    >
                      Try Again
                    </ModernButton>
                    <ModernButton
                      variant="secondary"
                      icon={<HomeOutlined />}
                      onClick={this.handleGoHome}
                    >
                      Go Home
                    </ModernButton>
                    <ModernButton
                      variant="secondary"
                      icon={<BugOutlined />}
                      onClick={this.handleReportBug}
                    >
                      Report Bug
                    </ModernButton>
                  </Space>

                  {process.env.NODE_ENV === "development" &&
                    this.state.error && (
                      <div
                        style={{
                          marginTop: "20px",
                          padding: "16px",
                          backgroundColor: colors.colorBgElevated,
                          border: `1px solid ${colors.colorBorder}`,
                          borderRadius: "8px",
                          fontSize: "12px",
                          fontFamily: "monospace",
                          overflow: "auto",
                          maxHeight: "200px",
                        }}
                      >
                        <Text strong style={{ color: colors.colorError }}>
                          Error ID: {this.state.errorId}
                        </Text>
                        <Paragraph
                          style={{
                            margin: "8px 0",
                            color: colors.colorTextSecondary,
                          }}
                        >
                          {this.state.error.message}
                        </Paragraph>
                        <details>
                          <summary
                            style={{
                              cursor: "pointer",
                              color: colors.colorTextSecondary,
                            }}
                          >
                            Stack Trace
                          </summary>
                          <pre
                            style={{
                              margin: "8px 0",
                              color: colors.colorTextSecondary,
                              whiteSpace: "pre-wrap",
                            }}
                          >
                            {this.state.error.stack}
                          </pre>
                        </details>
                        {this.state.errorInfo && (
                          <details>
                            <summary
                              style={{
                                cursor: "pointer",
                                color: colors.colorTextSecondary,
                              }}
                            >
                              Component Stack
                            </summary>
                            <pre
                              style={{
                                margin: "8px 0",
                                color: colors.colorTextSecondary,
                                whiteSpace: "pre-wrap",
                              }}
                            >
                              {this.state.errorInfo.componentStack}
                            </pre>
                          </details>
                        )}
                      </div>
                    )}
                </Space>
              }
            />
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

// Wrapper component to provide theme colors
const ErrorBoundary: React.FC<Props> = (props) => {
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  return <ErrorBoundaryClass {...props} colors={colors} />;
};

export default ErrorBoundary;
