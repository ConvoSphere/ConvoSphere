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
export const LazyDashboard = lazy(() => import("../pages/Dashboard"));
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

// Page-specific Lazy Components - Direct exports without additional Suspense wrapper
export const LazyHomePage: React.FC = () => <LazyHome />;
export const LazyDashboardPage: React.FC = () => <LazyDashboard />;
export const LazyOverviewPage: React.FC = () => <LazyOverview />;
export const LazyChatPage: React.FC = () => <LazyChat />;
export const LazyAssistantsPage: React.FC = () => <LazyAssistants />;
export const LazyKnowledgeBasePage: React.FC = () => <LazyKnowledgeBase />;
export const LazyToolsPage: React.FC = () => <LazyTools />;
export const LazySettingsPage: React.FC = () => <LazySettings />;
export const LazyAdminPage: React.FC = () => <LazyAdmin />;
export const LazyLoginPage: React.FC = () => <LazyLogin />;
export const LazyRegisterPage: React.FC = () => <LazyRegister />;
export const LazyProfilePage: React.FC = () => <LazyProfile />;
export const LazyConversationsPage: React.FC = () => <LazyConversations />;
export const LazyMcpToolsPage: React.FC = () => <LazyMcpTools />;
export const LazySystemStatusPage: React.FC = () => <LazySystemStatus />;
