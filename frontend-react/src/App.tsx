import React from 'react';
import { ConfigProvider, theme as antdTheme } from 'antd';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import i18n from './i18n';
import { useThemeStore } from './store/themeStore';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import {
  LazyChatPage,
  LazyDashboardPage,
  LazyAssistantsPage,
  LazyKnowledgeBasePage,
  LazyToolsPage,
  LazySettingsPage,
  LazyAdminPage,
  LazyLoginPage,
  LazyRegisterPage,
  LazyProfilePage,
  LazyConversationsPage,
  LazyMcpToolsPage,
  LazySystemStatusPage,
} from './components/LazyComponents';

const App: React.FC = () => {
  const { mode, getCurrentTheme } = useThemeStore();
  const currentTheme = getCurrentTheme();

  return (
    <I18nextProvider i18n={i18n}>
      <ConfigProvider
        theme={{
          algorithm: mode === 'dark' ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm,
          token: currentTheme.token,
        }}
      >
        <Router>
          <Routes>
            <Route path="/login" element={<LazyLoginPage />} />
            <Route path="/register" element={<LazyRegisterPage />} />
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Routes>
                      <Route path="/" element={<LazyChatPage />} />
                      <Route path="/dashboard" element={<LazyDashboardPage />} />
                      <Route path="/assistants" element={<LazyAssistantsPage />} />
                      <Route path="/knowledge-base" element={<LazyKnowledgeBasePage />} />
                      <Route path="/tools" element={<LazyToolsPage />} />
                      <Route path="/settings" element={<LazySettingsPage />} />
                      <Route path="/admin" element={<LazyAdminPage />} />
                      <Route path="/profile" element={<LazyProfilePage />} />
                      <Route path="/conversations" element={<LazyConversationsPage />} />
                      <Route path="/mcp-tools" element={<LazyMcpToolsPage />} />
                      <Route path="/admin/system-status" element={<LazySystemStatusPage />} />
                    </Routes>
                  </Layout>
                </ProtectedRoute>
              }
            />
          </Routes>
        </Router>
      </ConfigProvider>
    </I18nextProvider>
  );
};

export default App; 