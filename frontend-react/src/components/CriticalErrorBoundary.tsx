import React, { Component } from "react";
import type { ErrorInfo, ReactNode } from "react";
import { Button, Result, Card, Typography, Space, Alert } from "antd";
import { ReloadOutlined, HomeOutlined, BugOutlined, ExclamationCircleOutlined } from "@ant-design/icons";
import { useThemeStore } from "../store/themeStore";
import { useAuthStore } from "../store/authStore";

const { Text, Paragraph } = Typography;

interface Props {
  children: ReactNode;
  componentName: string;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  resetKey?: string | number;
  critical?: boolean;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string;
  retryCount: number;
}

class CriticalErrorBoundaryClass extends Component<Props & { colors: any }, State> {
  constructor(props: Props & { colors: any }) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: "",
      retryCount: 0,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error,
      errorId: `critical-error-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ errorInfo });

    // Log error to console in development
    if (process.env.NODE_ENV === "development") {
      console.error(`CriticalErrorBoundary caught an error in ${this.props.componentName}:`, error, errorInfo);
    }

    // Call custom error handler
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Send error to monitoring service
    this.logErrorToService(error, errorInfo);

    // For critical errors, log out user if authentication related
    if (this.props.critical && this.isAuthRelatedError(error)) {
      this.handleAuthError();
    }
  }

  componentDidUpdate(prevProps: Props & { colors: any }) {
    // Reset error state when resetKey changes
    if (prevProps.resetKey !== this.props.resetKey && this.state.hasError) {
      this.setState({
        hasError: false,
        error: null,
        errorInfo: null,
        errorId: "",
        retryCount: 0,
      });
    }
  }

  isAuthRelatedError = (error: Error): boolean => {
    const authErrorPatterns = [
      "unauthorized",
      "authentication",
      "token",
      "401",
      "403",
      "jwt",
      "auth",
    ];
    
    const errorMessage = error.message.toLowerCase();
    return authErrorPatterns.some(pattern => errorMessage.includes(pattern));
  };

  handleAuthError = () => {
    // Clear authentication state
    const { logout } = useAuthStore.getState();
    logout();
    
    // Redirect to login
    setTimeout(() => {
      window.location.href = "/login";
    }, 1000);
  };

  logErrorToService = (error: Error, errorInfo: ErrorInfo) => {
    const errorData = {
      errorId: this.state.errorId,
      componentName: this.props.componentName,
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      critical: this.props.critical,
      retryCount: this.state.retryCount,
    };

    // Store error in localStorage for debugging
    try {
      const existingErrors = JSON.parse(
        localStorage.getItem("critical-app-errors") || "[]",
      );
      existingErrors.push(errorData);
      localStorage.setItem(
        "critical-app-errors",
        JSON.stringify(existingErrors.slice(-20)), // Keep last 20 critical errors
      );
    } catch (e) {
      console.warn("Could not save critical error to localStorage:", e);
    }

    // In production, send to error monitoring service
    if (process.env.NODE_ENV === "production") {
      // Example: Sentry.captureException(error, { 
      //   tags: { component: this.props.componentName, critical: this.props.critical },
      //   extra: errorData 
      // });
    }
  };

  handleReset = () => {
    const newRetryCount = this.state.retryCount + 1;
    
    // Limit retry attempts for critical components
    if (this.props.critical && newRetryCount > 3) {
      this.handleAuthError();
      return;
    }

    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: "",
      retryCount: newRetryCount,
    });
  };

  handleGoHome = () => {
    window.location.href = "/";
  };

  handleReportBug = () => {
    const { error, errorInfo, errorId } = this.state;
    const errorReport = {
      errorId,
      componentName: this.props.componentName,
      message: error?.message,
      stack: error?.stack,
      componentStack: errorInfo?.componentStack,
      url: window.location.href,
      userAgent: navigator.userAgent,
      critical: this.props.critical,
      retryCount: this.state.retryCount,
    };

    // Copy to clipboard
    navigator.clipboard
      .writeText(JSON.stringify(errorReport, null, 2))
      .then(() => alert("Critical error report copied to clipboard"))
      .catch(() => alert("Could not copy error report"));
  };

  render() {
    const { colors, componentName, critical } = this.props;

    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Critical error UI
      if (critical) {
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
                maxWidth: "700px",
                width: "100%",
                backgroundColor: colors.colorBgContainer,
                border: `2px solid ${colors.colorError}`,
                boxShadow: colors.boxShadow,
              }}
            >
              <Result
                status="error"
                icon={<ExclamationCircleOutlined style={{ color: colors.colorError, fontSize: "48px" }} />}
                title="Critical System Error"
                subTitle={`A critical error occurred in ${componentName}. The system may be unstable.`}
                extra={
                  <Space direction="vertical" size="large" style={{ width: "100%" }}>
                    <Alert
                      message="Critical Error"
                      description="This is a critical system error that may affect the application's stability. Please report this issue immediately."
                      type="error"
                      showIcon
                      style={{ marginBottom: "16px" }}
                    />
                    
                    <Space>
                      <Button
                        type="primary"
                        danger
                        icon={<ReloadOutlined />}
                        onClick={this.handleReset}
                        disabled={this.state.retryCount >= 3}
                      >
                        {this.state.retryCount >= 3 ? "Max Retries Reached" : "Try Again"}
                      </Button>
                      <Button
                        icon={<HomeOutlined />}
                        onClick={this.handleGoHome}
                      >
                        Go Home
                      </Button>
                      <Button
                        icon={<BugOutlined />}
                        onClick={this.handleReportBug}
                      >
                        Report Critical Bug
                      </Button>
                    </Space>

                    {process.env.NODE_ENV === "development" && this.state.error && (
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
                          maxHeight: "300px",
                        }}
                      >
                        <Text strong style={{ color: colors.colorError }}>
                          Critical Error ID: {this.state.errorId}
                        </Text>
                        <br />
                        <Text strong style={{ color: colors.colorTextSecondary }}>
                          Component: {componentName}
                        </Text>
                        <br />
                        <Text strong style={{ color: colors.colorTextSecondary }}>
                          Retry Count: {this.state.retryCount}/3
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
                          <summary style={{ cursor: "pointer", color: colors.colorTextSecondary }}>
                            Stack Trace
                          </summary>
                          <pre style={{ margin: "8px 0", color: colors.colorTextSecondary, whiteSpace: "pre-wrap" }}>
                            {this.state.error.stack}
                          </pre>
                        </details>
                        {this.state.errorInfo && (
                          <details>
                            <summary style={{ cursor: "pointer", color: colors.colorTextSecondary }}>
                              Component Stack
                            </summary>
                            <pre style={{ margin: "8px 0", color: colors.colorTextSecondary, whiteSpace: "pre-wrap" }}>
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

      // Regular error UI (same as default ErrorBoundary)
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
              title={`Error in ${componentName}`}
              subTitle="Something went wrong in this component. Please try again."
              extra={
                <Space direction="vertical" size="middle" style={{ width: "100%" }}>
                  <Space>
                    <Button
                      type="primary"
                      icon={<ReloadOutlined />}
                      onClick={this.handleReset}
                    >
                      Try Again
                    </Button>
                    <Button
                      icon={<HomeOutlined />}
                      onClick={this.handleGoHome}
                    >
                      Go Home
                    </Button>
                    <Button
                      icon={<BugOutlined />}
                      onClick={this.handleReportBug}
                    >
                      Report Bug
                    </Button>
                  </Space>

                  {process.env.NODE_ENV === "development" && this.state.error && (
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
                      <br />
                      <Text strong style={{ color: colors.colorTextSecondary }}>
                        Component: {componentName}
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
                        <summary style={{ cursor: "pointer", color: colors.colorTextSecondary }}>
                          Stack Trace
                        </summary>
                        <pre style={{ margin: "8px 0", color: colors.colorTextSecondary, whiteSpace: "pre-wrap" }}>
                          {this.state.error.stack}
                        </pre>
                      </details>
                      {this.state.errorInfo && (
                        <details>
                          <summary style={{ cursor: "pointer", color: colors.colorTextSecondary }}>
                            Component Stack
                          </summary>
                          <pre style={{ margin: "8px 0", color: colors.colorTextSecondary, whiteSpace: "pre-wrap" }}>
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
const CriticalErrorBoundary: React.FC<Props> = (props) => {
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  return <CriticalErrorBoundaryClass {...props} colors={colors} />;
};

export default CriticalErrorBoundary;