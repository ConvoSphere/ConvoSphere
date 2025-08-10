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
import { detectLanguage, saveLanguagePreference } from "./utils/languageDetection";
import ProtectedLayoutRoute from "./components/ProtectedLayoutRoute";
import { protectedRoutes } from "./routes/routesConfig";

// Import modern UI styles
import "./styles/animations.css";
import "./styles/chat.css";

// Import auth components directly to ensure they are loaded
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";

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
  LazyConversationIntelligencePage,
  LazyDomainGroupsPage,
  LazyExportBackupPage,
  LazyAIModelsPage,
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
      <div style={{ textAlign: "center", maxWidth: "500px" }}>
        <h1 style={{ color: "#e74c3c", marginBottom: "16px" }}>
          {t("common.error_something_wrong")}
        </h1>
        <p style={{ marginBottom: "16px", color: simpleTheme.token.colorTextSecondary }}>
          {t("common.error_unexpected")}
        </p>
        <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
          <Button type="primary" onClick={resetErrorBoundary}>
            {t("common.try_again")}
          </Button>
          <Button onClick={() => window.location.reload()}>
            {t("common.refresh_page")}
          </Button>
        </div>
        {import.meta.env.DEV && (
          <details style={{ marginTop: "16px", textAlign: "left" }}>
            <summary style={{ cursor: "pointer", color: simpleTheme.token.colorTextSecondary }}>
              {t("common.error_details")}
            </summary>
            <pre
              style={{
                background: "#f5f5f5",
                padding: "12px",
                borderRadius: "4px",
                fontSize: "12px",
                overflow: "auto",
                marginTop: "8px",
              }}
            >
              {error.message}
            </pre>
          </details>
        )}
      </div>
    </div>
  );
};

const App: React.FC = () => {
  const { mode } = useThemeStore();
  const { initializeAuth, user } = useAuthStore();
  const [isInitialized, setIsInitialized] = useState(false);
  const [showPerformanceMonitor, setShowPerformanceMonitor] = useState(false);

  // Initialize language detection and authentication on app start
  useEffect(() => {
    const initApp = async () => {
      try {
        // Initialize language detection
        const detectedLanguage = detectLanguage();
        if (detectedLanguage !== i18n.language) {
          await i18n.changeLanguage(detectedLanguage);
          saveLanguagePreference(detectedLanguage);
        }
      
        // Ensure document language attribute stays in sync
        document.documentElement.lang = i18n.language;

        // Initialize authentication
        await initializeAuth();
      } catch (error) {
        if (import.meta.env.DEV) {
          console.error("Failed to initialize application:", error);
        }
      } finally {
        setIsInitialized(true);
      }
    };

    initApp();
  }, [initializeAuth]);

  // Sync user language preference with i18n
  useEffect(() => {
    if (user?.language && user.language !== i18n.language) {
      i18n.changeLanguage(user.language);
      saveLanguagePreference(user.language);
      document.documentElement.lang = user.language;
    }
  }, [user?.language]);

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
        if (import.meta.env.DEV) {
          console.error("App Error:", error, errorInfo);
        }
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
          <Router basename={import.meta.env.BASE_URL}>
            <ErrorBoundary
              onError={(error, errorInfo) => {
                if (import.meta.env.DEV) {
                  console.error("Router Error:", error, errorInfo);
                }
                performanceMonitor.logError("Router Error", {
                  error: error.message,
                  errorInfo,
                });
              }}
            >
              <Routes>
                {/* auth routes */}
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
                  path="/forgot-password"
                  element={
                    <ErrorBoundary>
                      <Suspense fallback={<LoadingSpinner />}>
                        <ForgotPassword />
                      </Suspense>
                    </ErrorBoundary>
                  }
                />
                <Route
                  path="/reset-password"
                  element={
                    <ErrorBoundary>
                      <Suspense fallback={<LoadingSpinner />}>
                        <ResetPassword />
                      </Suspense>
                    </ErrorBoundary>
                  }
                />
                {protectedRoutes.map(({ path, element }) => (
                  <Route key={path} path={path} element={element} />
                ))}
              </Routes>
            </ErrorBoundary>
          </Router>
          </ConfigProvider>
        </AccessibilityProvider>
      </I18nextProvider>

      {/* Performance Monitor (development only) */}
      {process.env.NODE_ENV === "development" && showPerformanceMonitor && (
        <PerformanceMonitor />
      )}

      {/* Performance Monitor Toggle (development only) */}
      {process.env.NODE_ENV === "development" && (
        <div
          style={{
            position: "fixed",
            bottom: "20px",
            right: "20px",
            zIndex: 9999,
          }}
        >
          <Button
            type="primary"
            icon={<DashboardOutlined />}
            onClick={() => setShowPerformanceMonitor(!showPerformanceMonitor)}
            size="small"
          >
            {showPerformanceMonitor ? "Hide" : "Show"} Monitor
          </Button>
        </div>
      )}
    </ErrorBoundary>
  );
};

export default App;
