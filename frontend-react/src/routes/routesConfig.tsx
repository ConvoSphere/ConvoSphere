import React from "react";
import ProtectedLayoutRoute from "../components/ProtectedLayoutRoute";
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
} from "../components/LazyComponents";

export type AppRoute = {
  path: string;
  element: React.ReactNode;
};

export const protectedRoutes: AppRoute[] = [
  { path: "/", element: (<ProtectedLayoutRoute><LazyHomePage /></ProtectedLayoutRoute>) },
  { path: "/dashboard", element: (<ProtectedLayoutRoute><LazyDashboardPage /></ProtectedLayoutRoute>) },
  { path: "/overview", element: (<ProtectedLayoutRoute><LazyOverviewPage /></ProtectedLayoutRoute>) },
  { path: "/chat", element: (<ProtectedLayoutRoute><LazyChatPage /></ProtectedLayoutRoute>) },
  { path: "/assistants", element: (<ProtectedLayoutRoute><LazyAssistantsPage /></ProtectedLayoutRoute>) },
  { path: "/ai-models", element: (<ProtectedLayoutRoute><LazyAIModelsPage /></ProtectedLayoutRoute>) },
  { path: "/knowledge-base", element: (<ProtectedLayoutRoute><LazyKnowledgeBasePage /></ProtectedLayoutRoute>) },
  { path: "/tools", element: (<ProtectedLayoutRoute><LazyToolsPage /></ProtectedLayoutRoute>) },
  { path: "/settings", element: (<ProtectedLayoutRoute><LazySettingsPage /></ProtectedLayoutRoute>) },
  { path: "/admin", element: (<ProtectedLayoutRoute><LazyAdminPage /></ProtectedLayoutRoute>) },
  { path: "/profile", element: (<ProtectedLayoutRoute><LazyProfilePage /></ProtectedLayoutRoute>) },
  { path: "/conversations", element: (<ProtectedLayoutRoute><LazyConversationsPage /></ProtectedLayoutRoute>) },
  { path: "/mcp-tools", element: (<ProtectedLayoutRoute><LazyMcpToolsPage /></ProtectedLayoutRoute>) },
  { path: "/system-status", element: (<ProtectedLayoutRoute><LazySystemStatusPage /></ProtectedLayoutRoute>) },
  { path: "/conversation-intelligence", element: (<ProtectedLayoutRoute><LazyConversationIntelligencePage /></ProtectedLayoutRoute>) },
  { path: "/domain-groups", element: (<ProtectedLayoutRoute><LazyDomainGroupsPage /></ProtectedLayoutRoute>) },
  { path: "/export-backup", element: (<ProtectedLayoutRoute><LazyExportBackupPage /></ProtectedLayoutRoute>) },
];