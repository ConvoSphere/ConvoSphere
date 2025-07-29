import React, { Suspense, useState, useEffect } from "react";
import { ConfigProvider, theme as antdTheme, Spin, Button } from "antd";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { I18nextProvider, useTranslation } from "react-i18next";
import { DashboardOutlined } from "@ant-design/icons";
import i18n from "./i18n";
import { useThemeStore } from "./store/themeStore";
import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";
import ErrorBoundary from "./components/ErrorBoundary";
import CriticalErrorBoundary from "./components/CriticalErrorBoundary";
import PerformanceMonitor from "./components/PerformanceMonitor";
import performanceMonitor from "./utils/performance";
import { AccessibilityProvider } from "./components/AccessibilityProvider";
import { useAuthStore } from "./store/authStore";

// Import modern UI styles
import "./styles/animations.css";
import "./styles/chat.css";

// Import auth components directly to ensure they are loaded
import Login from "./pages/Login";
import Register from "./pages/Register";

import {
  LazyHomePage,
  LazyDashboardPage,
  LazyOverviewPage,
  LazyChatPage,
  LazyAssistantsPage,
  LazyKnowledgeBasePage,
  LazyToolsPage,
  LazySettingsPage,
  LazyAdminPage,
  LazyProfilePage,
  LazyConversationsPage,
  LazyMcpToolsPage,
  LazySystemStatusPage,
} from "./components/LazyComponents";

// Simple theme configuration to avoid complex theme store issues
const simpleTheme = {
  token: {
    colorPrimary: "#23224A",
    colorBgBase: "#F7F9FB",
    colorBgContainer: "#FFFFFF",
    colorText: "#23224A",
    colorTextSecondary: "#7A869A",
    colorBorder: "#E5E7EB",
  },
};

// Loading component with theme-aware styling
const LoadingSpinner: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        backgroundColor: simpleTheme.token.colorBgBase,
      }}
    >
      <div style={{ textAlign: "center" }}>
        <Spin size="large" style={{ color: simpleTheme.token.colorPrimary }} />
        <div
          style={{
            marginTop: "16px",
            color: simpleTheme.token.colorTextSecondary,
            fontSize: "14px",
          }}
        >
          {t("common.loading_app")}
        </div>
      </div>
    </div>
  );
};

// Error fallback component
const ErrorFallback: React.FC<{
  error: Error;
  resetErrorBoundary: () => void;
}> = ({ error, resetErrorBoundary }) => {
  const { t } = useTranslation();

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        backgroundColor: simpleTheme.token.colorBgBase,
        padding: "20px",
      }}
    >
      <div
        style={{
          maxWidth: "500px",
          textAlign: "center",
          backgroundColor: simpleTheme.token.colorBgContainer,
          padding: "32px",
          borderRadius: "12px",
          border: `1px solid ${simpleTheme.token.colorBorder}`,
          boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)",
        }}
      >
        <h2 style={{ color: simpleTheme.token.colorText, marginBottom: "16px" }}>
          {t("common.error_occurred")}
        </h2>
        <p style={{ color: simpleTheme.token.colorTextSecondary, marginBottom: "24px" }}>
          {error.message || t("common.unknown_error")}
        </p>
        <Button
          type="primary"
          onClick={resetErrorBoundary}
          style={{ backgroundColor: simpleTheme.token.colorPrimary }}
        >
          {t("common.try_again")}
        </Button>
      </div>
    </div>
  );
};

const App: React.FC = () => {
  const { mode } = useThemeStore();
  const { initializeAuth } = useAuthStore();
  const [isInitialized, setIsInitialized] = useState(false);
  const [showPerformanceMonitor, setShowPerformanceMonitor] = useState(false);

  // Initialize authentication on app start
  useEffect(() => {
    const initApp = async () => {
      try {
        await initializeAuth();
      } catch (error) {
        console.error("Failed to initialize authentication:", error);
      } finally {
        setIsInitialized(true);
      }
    };

    initApp();
  }, [initializeAuth]);

  // Initialize performance monitoring - MUST be before conditional return
  useEffect(() => {
    performanceMonitor.init();

    // Mark app initialization
    performanceMonitor.mark("app-init-start");

    return () => {
      performanceMonitor.mark("app-init-end");
      performanceMonitor.measure(
        "App Initialization",
        "app-init-start",
        "app-init-end",
      );
    };
  }, []);

  // Show loading spinner while initializing
  if (!isInitialized) {
    return (
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
          backgroundColor: simpleTheme.token.colorBgBase,
        }}
      >
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <ErrorBoundary
      fallback={
        <ErrorFallback
          error={new Error("App failed to load")}
          resetErrorBoundary={() => window.location.reload()}
        />
      }
      onError={(error, errorInfo) => {
        console.error("App Error:", error, errorInfo);
        // Send to error reporting service
        performanceMonitor.logError("App Error", {
          error: error.message,
          errorInfo,
        });
      }}
    >
      <I18nextProvider i18n={i18n}>
        <AccessibilityProvider>
          <ConfigProvider
            theme={{
              algorithm:
                mode === "dark"
                  ? antdTheme.darkAlgorithm
                  : antdTheme.defaultAlgorithm,
              token: simpleTheme.token,
            }}
          >
          <Router>
            <ErrorBoundary
              onError={(error, errorInfo) => {
                console.error("Router Error:", error, errorInfo);
                performanceMonitor.logError("Router Error", {
                  error: error.message,
                  errorInfo,
                });
              }}
            >
              <Routes>
                <Route
                  path="/login"
                  element={
                    <ErrorBoundary>
                      <Suspense fallback={<LoadingSpinner />}>
                        <Login />
                      </Suspense>
                    </ErrorBoundary>
                  }
                />
                <Route
                  path="/register"
                  element={
                    <ErrorBoundary>
                      <Suspense fallback={<LoadingSpinner />}>
                        <Register />
                      </Suspense>
                    </ErrorBoundary>
                  }
                />
                <Route
                  path="/*"
                  element={
                    <CriticalErrorBoundary componentName="App" critical={true}>
                      <ProtectedRoute>
                        <Layout>
                          <ErrorBoundary>
                            <Suspense fallback={<LoadingSpinner />}>
                              <Routes>
                                                          <Route path="/" element={<LazyHomePage />} />
                          <Route
                            path="/dashboard"
                            element={<LazyDashboardPage />}
                          />
                          <Route
                            path="/overview"
                            element={<LazyOverviewPage />}
                          />
                                <Route
                                  path="/chat"
                                  element={<LazyChatPage />}
                                />
                                <Route
                                  path="/assistants"
                                  element={<LazyAssistantsPage />}
                                />
                                <Route
                                  path="/knowledge-base"
                                  element={<LazyKnowledgeBasePage />}
                                />
                                <Route
                                  path="/tools"
                                  element={<LazyToolsPage />}
                                />
                                <Route
                                  path="/settings"
                                  element={<LazySettingsPage />}
                                />
                                <Route
                                  path="/admin"
                                  element={<LazyAdminPage />}
                                />
                                <Route
                                  path="/profile"
                                  element={<LazyProfilePage />}
                                />
                                <Route
                                  path="/conversations"
                                  element={<LazyConversationsPage />}
                                />
                                <Route
                                  path="/mcp-tools"
                                  element={<LazyMcpToolsPage />}
                                />
                                <Route
                                  path="/admin/system-status"
                                  element={<LazySystemStatusPage />}
                                />
                              </Routes>
                            </Suspense>
                          </ErrorBoundary>
                        </Layout>
                      </ProtectedRoute>
                    </CriticalErrorBoundary>
                  }
                />
              </Routes>
            </ErrorBoundary>
          </Router>

          {/* Performance Monitor Toggle (Development Only) */}
          {process.env.NODE_ENV === "development" && (
            <Button
              type="primary"
              icon={<DashboardOutlined />}
              size="small"
              onClick={() => setShowPerformanceMonitor(!showPerformanceMonitor)}
              style={{
                position: "fixed",
                bottom: "20px",
                right: "20px",
                zIndex: 1001,
                borderRadius: "50%",
                width: "48px",
                height: "48px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)",
              }}
            />
          )}

          {/* Performance Monitor */}
          <PerformanceMonitor
            visible={showPerformanceMonitor}
            onClose={() => setShowPerformanceMonitor(false)}
          />
        </ConfigProvider>
        </AccessibilityProvider>
      </I18nextProvider>
    </ErrorBoundary>
  );
};

export default App;
