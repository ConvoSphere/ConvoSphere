import React, { Suspense, lazy } from "react";
import { Spin } from "antd";
import { useThemeStore } from "../store/themeStore";

// Loading Component mit Theme-Aware Styling
const LoadingSpinner: React.FC<{ size?: "small" | "default" | "large" }> = ({
  size = "default",
}) => {
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();

  const spinnerStyle: React.CSSProperties = {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    padding: "40px",
    color: colors.colorTextSecondary,
  };

  return (
    <div style={spinnerStyle}>
      <Spin size={size} />
    </div>
  );
};

// Lazy-Loaded Page Components
export const LazyHome = lazy(() => import("../pages/Home"));
export const LazyOverview = lazy(() => import("../pages/Overview"));
export const LazyChat = lazy(() => import("../pages/Chat"));
export const LazyAssistants = lazy(() => import("../pages/Assistants"));
export const LazyKnowledgeBase = lazy(() => import("../pages/KnowledgeBase"));
export const LazyTools = lazy(() => import("../pages/Tools"));
export const LazySettings = lazy(() => import("../pages/Settings"));
export const LazyAdmin = lazy(() => import("../pages/Admin"));
export const LazyLogin = lazy(() => import("../pages/Login"));
export const LazyRegister = lazy(() => import("../pages/Register"));
export const LazyProfile = lazy(() => import("../pages/Profile"));
export const LazyConversations = lazy(() => import("../pages/Conversations"));
export const LazyMcpTools = lazy(() => import("../pages/McpTools"));
export const LazySystemStatus = lazy(() => import("../pages/SystemStatus"));

// Lazy-Loaded Feature Components
export const LazyVirtualizedChat = lazy(() => import("./VirtualizedChat"));
// IconSystem is not a component; use Icon from './icons' where needed

// Lazy Component Wrapper
interface LazyComponentProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export const LazyComponent: React.FC<LazyComponentProps> = ({
  children,
  fallback = <LoadingSpinner size="large" />,
}) => {
  return <Suspense fallback={fallback}>{children}</Suspense>;
};

// Page-specific Lazy Components
export const LazyHomePage: React.FC = () => (
  <LazyComponent>
    <LazyHome />
  </LazyComponent>
);

export const LazyOverviewPage: React.FC = () => (
  <LazyComponent>
    <LazyOverview />
  </LazyComponent>
);

export const LazyChatPage: React.FC = () => (
  <LazyComponent>
    <LazyChat />
  </LazyComponent>
);

export const LazyAssistantsPage: React.FC = () => (
  <LazyComponent>
    <LazyAssistants />
  </LazyComponent>
);

export const LazyKnowledgeBasePage: React.FC = () => (
  <LazyComponent>
    <LazyKnowledgeBase />
  </LazyComponent>
);

export const LazyToolsPage: React.FC = () => (
  <LazyComponent>
    <LazyTools />
  </LazyComponent>
);

export const LazySettingsPage: React.FC = () => (
  <LazyComponent>
    <LazySettings />
  </LazyComponent>
);

export const LazyAdminPage: React.FC = () => (
  <LazyComponent>
    <LazyAdmin />
  </LazyComponent>
);

export const LazyLoginPage: React.FC = () => (
  <LazyComponent>
    <LazyLogin />
  </LazyComponent>
);

export const LazyRegisterPage: React.FC = () => (
  <LazyComponent>
    <LazyRegister />
  </LazyComponent>
);

export const LazyProfilePage: React.FC = () => (
  <LazyComponent>
    <LazyProfile />
  </LazyComponent>
);

export const LazyConversationsPage: React.FC = () => (
  <LazyComponent>
    <LazyConversations />
  </LazyComponent>
);

export const LazyMcpToolsPage: React.FC = () => (
  <LazyComponent>
    <LazyMcpTools />
  </LazyComponent>
);

export const LazySystemStatusPage: React.FC = () => (
  <LazyComponent>
    <LazySystemStatus />
  </LazyComponent>
);
