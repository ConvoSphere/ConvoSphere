import React, { Suspense, lazy } from "react";
import { Spin, Result } from "antd";
import ModernButton from "./ModernButton";
import { LoadingOutlined } from "@ant-design/icons";

// Enhanced loading component with better UX
const EnhancedLoadingSpinner: React.FC<{ message?: string }> = ({
  message = "Loading...",
}) => (
  <div
    style={{
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
      height: "200px",
      gap: "16px",
    }}
  >
    <Spin
      indicator={<LoadingOutlined style={{ fontSize: 24 }} spin />}
      size="large"
    />
    <div style={{ color: "#666", fontSize: "14px" }}>{message}</div>
  </div>
);

// Enhanced error boundary component
const EnhancedErrorBoundary: React.FC<{
  children: React.ReactNode;
  fallback?: React.ReactNode;
}> = ({ children, fallback }) => {
  const [hasError, setHasError] = React.useState(false);
  const [error, setError] = React.useState<Error | null>(null);

  React.useEffect(() => {
    const handleError = (error: Error) => {
      console.error("Lazy component error:", error);
      setError(error);
      setHasError(true);
    };

    window.addEventListener("error", handleError);
    return () => window.removeEventListener("error", handleError);
  }, []);

  if (hasError) {
    return (
      fallback || (
        <Result
          status="error"
          title="Component failed to load"
          subTitle={error?.message || "An unexpected error occurred"}
          extra={[
            <ModernButton
              variant="primary"
              key="retry"
              onClick={() => window.location.reload()}
            >
              Retry
            </ModernButton>,
          ]}
        />
      )
    );
  }

  return <>{children}</>;
};

// Wrapper for lazy components with enhanced error handling
const createLazyComponent = (
  importFunc: () => Promise<{ default: React.ComponentType<any> }>,
  loadingMessage?: string,
) => {
  const LazyComponent = lazy(importFunc);

  return React.forwardRef<any, any>((props, ref) => (
    <EnhancedErrorBoundary>
      <Suspense fallback={<EnhancedLoadingSpinner message={loadingMessage} />}>
        <LazyComponent {...props} ref={ref} />
      </Suspense>
    </EnhancedErrorBoundary>
  ));
};

// Lazy-loaded components with optimized chunk splitting
export const LazyHomePage = createLazyComponent(
  () => import("../pages/Home"),
  "Loading home page...",
);

export const LazyDashboardPage = createLazyComponent(
  () => import("../pages/Dashboard"),
  "Loading dashboard...",
);

export const LazyOverviewPage = createLazyComponent(
  () => import("../pages/Overview"),
  "Loading overview...",
);

export const LazyChatPage = createLazyComponent(
  () => import("../pages/Chat"),
  "Loading chat...",
);

export const LazyAssistantsPage = createLazyComponent(
  () => import("../pages/Assistants"),
  "Loading assistants...",
);

export const LazyAIModelsPage = createLazyComponent(
  () => import("../pages/AIModels"),
  "Loading AI models...",
);

export const LazyKnowledgeBasePage = createLazyComponent(
  () => import("../pages/KnowledgeBase"),
  "Loading knowledge base...",
);

export const LazyToolsPage = createLazyComponent(
  () => import("../pages/Tools"),
  "Loading tools...",
);

export const LazySettingsPage = createLazyComponent(
  () => import("../pages/Settings"),
  "Loading settings...",
);

export const LazyAdminPage = createLazyComponent(
  () => import("../pages/Admin"),
  "Loading admin panel...",
);

export const LazyProfilePage = createLazyComponent(
  () => import("../pages/Profile"),
  "Loading profile...",
);

export const LazyConversationsPage = createLazyComponent(
  () => import("../pages/Conversations"),
  "Loading conversations...",
);

export const LazyMcpToolsPage = createLazyComponent(
  () => import("../pages/McpTools"),
  "Loading MCP tools...",
);

export const LazySystemStatusPage = createLazyComponent(
  () => import("../pages/SystemStatus"),
  "Loading system status...",
);

export const LazyConversationIntelligencePage = createLazyComponent(
  () => import("../pages/ConversationIntelligence"),
  "Loading conversation intelligence...",
);

export const LazyDomainGroupsPage = createLazyComponent(
  () => import("../pages/DomainGroups"),
  "Loading domain groups...",
);

export const LazyExportBackupPage = createLazyComponent(
  () => import("../pages/ExportBackup"),
  "Loading export/backup...",
);

// Preload critical components for better UX
export const preloadCriticalComponents = () => {
  // Preload dashboard and chat as they are most commonly used
  const preloadDashboard = () => import("../pages/Dashboard");
  const preloadChat = () => import("../pages/Chat");

  // Preload after a short delay to not block initial load
  setTimeout(() => {
    preloadDashboard();
    preloadChat();
  }, 2000);
};

// Export the enhanced loading component for use elsewhere
export { EnhancedLoadingSpinner, EnhancedErrorBoundary };
